#!/usr/bin/env python3
# =============================================================================
"""Balena Vars Utils

Author:
    Juan Pablo Castillo - juan.castillo@kiwibot.com
"""
# =============================================================================

import balena
import os
import re
import balena.types.models
import json
import google.auth.credentials
import gspread
import os
import uuid
import json
import base64
import datetime
import google.auth
import re
import click
import requests
import fleet_control.logging_config # Ensure logging is configured
import logging
from google.cloud import tasks_v2
from google.protobuf import duration_pb2, timestamp_pb2
from fleet_control.utils.python_utils import handle_request_error, COLORS, load_json
from dotenv import dotenv_values
from pathlib import Path
from balena.exceptions import DeviceNotFound, RequestError
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

# ===================================================================================
def load_env_values():
    """Load .env values into a dict, if a file exists."""
    custom_env_path = os.getenv("FCT_ENV_PATH")
    env_path = Path(custom_env_path) if custom_env_path else Path.cwd() / ".env"

    if env_path.exists():
        env_vars = dotenv_values(dotenv_path=env_path)
        logger.info(f"{COLORS['OK_GREEN']} Environment variables loaded from: {env_path} {COLORS['RESET']}")
        return env_vars
    else:
        # logger.info(f"[env] No .env file found at {env_path}. Using defaults and environment variables.")
        return {}


env_file_values: dict = load_env_values()


def get_config(key, default: str | None = None) -> str:
    """
    Get config value with priority:
    1. .env file
    2. default
    3. os.environ
    """
    if key in env_file_values:
        return env_file_values[key]
    elif default is not None:
        return default
    else:
        variable = os.getenv(key)
        if variable is None:
            raise EnvironmentError(
                f"{key} not set. Please export the variable into your environment or add it to a .env file"
            )
        else:
            return variable


CREDENTIAL_SCOPES = ["https://www.googleapis.com/auth/cloud-platform",
                     "https://www.googleapis.com/auth/sqlservice.login",
                     "https://www.googleapis.com/auth/userinfo.email",
                     "openid",
                     "https://www.googleapis.com/auth/spreadsheets",
                     "https://www.googleapis.com/auth/drive"]
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
SPREADSHEET_NAME = get_config("SPREADSHEET_NAME", "SD Logs")
# ORGANIZATION_HANDLE = get_config("ORGANIZATION_HANDLE","")
TAGS_BY_VERSION_FILE = get_config("TAGS_BY_VERSION_FILE", "tags_by_version.json")
BALENA_API_TOKEN = get_config("BALENA_API_KEY")
BOT_ID_REGEX = re.compile("[0-9][A-Z][0-9]{3}$")
VARIABLES_REGEX = re.compile("^[a-zA-Z0-9_]+=.*(=[a-zA-Z0-9_*]+)?$")


# Optional variables:
def try_get_config(key) -> str | None:
    try:
        return get_config(key)
    except EnvironmentError as e:
        if key != "SERVICE_ACCOUNT_EMAIL" and key != "GOOGLE_APPLICATION_CREDENTIALS":
            logger.warning(f"Environment variable not set: {key}. Some functions will not work.")
        return None


PROJECT_ID = try_get_config("PROJECT_ID")
LOCATION_ID = try_get_config("LOCATION_ID")
QUEUE_ID = try_get_config("QUEUE_ID")
SERVICE_ACCOUNT = try_get_config("GOOGLE_APPLICATION_CREDENTIALS")
SERVICE_ACCOUNT_EMAIL = try_get_config("SERVICE_ACCOUNT_EMAIL")
if SERVICE_ACCOUNT is None and SERVICE_ACCOUNT_EMAIL is None:
    logger.warning("Environment variables: SERVICE_ACCOUNT and SERVICE_ACCOUNT_EMAIL not set. Some functions will not work.")


# Initialize the Balena SDK
balena_sdk = balena.Balena()
balena_sdk.auth.login_with_token(BALENA_API_TOKEN)


# ===================================================================================


def get_service_id(
    target: balena.types.models.TypeDevice | balena.types.models.TypeApplication | int, service_name: str
):
    if isinstance(target, int):
        app_id = target
    elif target.get("device_name"):
        app_id = int(target["belongs_to__application"]["__id"])  # type: ignore
    else:
        app_id = target.get("id")
    services = balena_sdk.models.service.get_all_by_application(app_id)
    service = next((s["id"] for s in services if s.get("service_name") == service_name), 0)
    return service


def get_fleet(fleet: str | int) -> balena.types.models.TypeApplication:
    """Get device information by ID with 'kiwibot' prefix."""
    # global ORGANIZATION_HANDLE
    if isinstance(fleet, str):
        res = balena_sdk.models.application.get_by_name(fleet)
        # ORGANIZATION_HANDLE = (res["slug"].split("/")[0] + "/") if res and not ORGANIZATION_HANDLE else ""
    elif isinstance(fleet, int):
        res = balena_sdk.models.application.get(fleet)
        # ORGANIZATION_HANDLE = (res["slug"].split("/")[0] + "/") if res and not ORGANIZATION_HANDLE else ""
    if not res:
        logger.info(f"Device {fleet} not found.")
    return res


def get_device_by_id(device_id: str) -> balena.types.models.TypeDevice | None:
    """Get device information by ID with 'kiwibot' prefix."""
    try:
        device = balena_sdk.models.device.get_by_name(f"kiwibot{device_id}")
    except DeviceNotFound:
        logger.warning(f"Device {device_id} not found.")
        return None
    return device[0]


def get_fleet_variables(
    fleet: balena.types.models.TypeApplication | int,
) -> dict[str, dict[str, str] | dict[int, dict[str, str]]]:
    """Fetch variables for a fleet."""
    service = 0
    if isinstance(fleet, int):
        fleet_env_vars = balena_sdk.models.application.env_var.get_all_by_application(fleet)
        fleet_service_vars = balena_sdk.models.service.var.get_all_by_application(fleet)
        service = get_service_id(fleet, "main")
    elif isinstance(fleet, dict):
        fleet_env_vars = balena_sdk.models.application.env_var.get_all_by_application(fleet["id"])
        fleet_service_vars = balena_sdk.models.service.var.get_all_by_application(fleet["id"])
        service = get_service_id(fleet, "main")

    env_vars = {var["name"]: var["value"] for var in fleet_env_vars}
    service_vars = {var["name"]: var["value"] for var in fleet_service_vars}

    return {"env_vars": env_vars, "service_vars": {service: service_vars}}


def get_device_variables(
    device_info: balena.types.models.TypeDevice, custom_only: bool = False, fleet_vars=None
) -> dict[str, dict]:
    """Fetch both environment and service variables for a device."""
    device_id = device_info["id"]
    app_id = int(device_info["belongs_to__application"]["__id"])  # type: ignore

    # Get device-specific variables
    device_env_vars = balena_sdk.models.device.env_var.get_all_by_device(device_id)
    device_service_vars = balena_sdk.models.device.service_var.get_all_by_device(device_id)
    service = get_service_id(device_info, "main")

    variables = {"env_vars": {}, "service_vars": {service: {}}}
    if not custom_only:
        if not fleet_vars:
            # Get fleet-level variables
            variables = get_fleet_variables(app_id)
        else:
            variables = fleet_vars

    # Combine fleet and device variables
    variables["env_vars"].update({var["name"]: var["value"] for var in device_env_vars})  # type: ignore
    variables["service_vars"][service].update({var["name"]: var["value"] for var in device_service_vars})  # type: ignore

    return variables


def get_custom_set_vars_fleet(fleet_name: str) -> dict[str, dict[str, str | int]]:
    """Fetch all custom set variables in all devices of the selected fleet

    Args:
        fleet_name (str): fleet name

    Returns:
        dict[str, dict[str, str | int]]: dictionary with variables, see default structure
    """

    @handle_request_error()
    def get_service_install_vars(fleet_name: str):

        # Define the endpoint and parameters
        url = "https://api.balena-cloud.com/v7/device_service_environment_variable"

        # Raw query string (copy it exactly as used in curl, without encoding $)
        query_string = (
            "?$filter=service_install/any(si:si/device/any(d:d/belongs_to__application/app_name eq '{}'))"
            "&$expand=service_install($expand=installs__service($select=id,service_name))"
        ).format(fleet_name)

        url = f"https://api.balena-cloud.com/v7/device_service_environment_variable{query_string}"

        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {BALENA_API_TOKEN}"}

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json().get("d", {})
        else:
            logger.info(f"Request failed: {response.status_code} - {response.text}")
            raise RequestError(response.text, response.status_code)

    fleet_id = get_fleet(fleet_name)["id"]
    raw_env_vars = balena_sdk.models.device.env_var.get_all_by_application(fleet_id)
    raw_service_vars = get_service_install_vars(fleet_name)

    vars_per_bot = {}

    device_ids = set([item["device"]["__id"] for item in raw_env_vars])  # type: ignore
    device_ids.update(set([item["service_install"][0]["device"]["__id"] for item in raw_service_vars]))

    vars_per_bot = {id: {"env_vars": {}, "service_vars": {"main": {}}} for id in device_ids}
    for i in raw_env_vars:
        bot = i["device"]["__id"]  # type: ignore
        vars_per_bot[bot]["env_vars"].update({i["name"]: i["value"]})

    for i in raw_service_vars:
        bot = i["service_install"][0]["device"]["__id"]
        vars_per_bot[bot]["service_vars"]["main"].update({i["name"]: i["value"]})

    return vars_per_bot


def find_release(fleet_id: int, semver: str | None) -> balena.types.models.ReleaseType:
    if semver:
        releases = balena_sdk.models.release.get_all_by_application(fleet_id)
        version, revision = semver.split("+rev")

        for release in releases:
            if (version == "0.0.0" and release.get("revision") == int(revision)) or release.get("semver") == semver:
                return release  # Return the first matching release
        logger.info("No release found")
        exit(1)
    else:
        release = balena_sdk.models.release.get_latest_by_application(fleet_id)
        if release:
            return release
        else:
            logger.info("No release found")
            exit(1)


def pin_to_release(
    target: balena.types.models.TypeDevice | balena.types.models.TypeApplication,
    release: balena.types.models.ReleaseType,
):
    if target.get("device_name") is None:
        # If the target is an application, pin the application to the release
        logger.debug(
            f"Pinning application {target.get('app_name')} to release {release['semver']}+rev{release['revision']}"
            if release["semver"] == "0.0.0"
            else f"Pinning {target.get('app_name')} to release {release['semver']}"
        )
        balena_sdk.models.application.pin_to_release(target["id"], release["commit"])
        logger.info(
            f"{target.get('app_name')} pinned to release: {release['semver']}+rev{release['revision']}"
            if release["semver"] == "0.0.0"
            else f"{target.get('device_name')} pinned to release: {release['semver']}"
        )
    else:
        # If the target is a device, pin the device to the release
        logger.debug(
            f"Pinning {target.get('device_name')} to release {release['semver']}+rev{release['revision']}"
            if release["semver"] == "0.0.0"
            else f"Pinning {target.get('device_name')} to release {release['semver']}"
        )
        balena_sdk.models.device.pin_to_release(target["id"], release["id"])
        logger.info(
            f"{target.get('device_name')} pinned to release: {release['semver']}+rev{release['revision']}"
            if release["semver"] == "0.0.0"
            else f"{target.get('device_name')} pinned to release: {release['semver']}"
        )


def open_sheet(credentials_file: str | None, sheet_name: str, worksheet_name: str) -> gspread.Worksheet:
    """
    Function to get access to a sheet file
    @param credentials_file (str): API json credentials file path
    @param sheet_key (str): google spreadsheet file key
    @param worksheet_name (str): google worksheet name

    @return gspread.worksheet instance
    """
    if credentials_file is not None and os.path.isfile(credentials_file):
        logger.info("Service account file based credentials used")
        credentials = google.auth.load_credentials_from_file(credentials_file, scopes=SCOPES)[0]
    else:
        logger.info("Application Default Credentials (ADC) used")
        credentials: google.auth.credentials.Credentials = google.auth.default(scopes=CREDENTIAL_SCOPES, quota_project_id=PROJECT_ID)[0] # type: ignore

    client = gspread.authorize(credentials)

    return client.open(sheet_name).worksheet(worksheet_name)


def format_pubsub_message(message_data):
    return {
        "messages": [
            {
                "data": base64.b64encode(json.dumps(message_data).encode("utf-8")).decode("utf-8"),
                "attributes": {"origin": "cloud-tasks"},
            }
        ]
    }


def create_http_task(
    project: str,
    location: str,
    queue: str,
    url: str,
    json_payload: dict,
    service_account_client_email: str,
    scheduled_datetime: datetime.datetime | None = None,
    task_id: uuid.UUID | None = None,
    deadline_in_seconds: int | None = None,
) -> tasks_v2.Task:
    """Create an HTTP POST google cloud task with a JSON payload.
    Args:
        project: The project ID where the queue is located.
        location: The location where the queue is located.
        queue: The ID of the queue to add the task to.
        url: The target URL of the task.
        json_payload: The JSON payload to send.
        service_account_client_email: Service account email to authorize request.
        scheduled_datetime: Datetime to schedule the task for.
        task_id: ID to use for the newly created task.
        deadline_in_seconds: The deadline in seconds for task.
    Returns:
        The newly created task.
    """

    # Create a client.
    client = tasks_v2.CloudTasksClient()

    # Build the http_request kwargs
    http_request_kwargs = {
        "http_method": tasks_v2.HttpMethod.POST,
        "url": url,
        "headers": {"Content-type": "application/json"},
        "body": json.dumps(json_payload).encode(),
        "oauth_token": tasks_v2.OAuthToken(service_account_email=service_account_client_email),
    }

    # Construct the task.
    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(**http_request_kwargs),
        name=(client.task_path(project, location, queue, str(task_id)) if task_id is not None else None),
    )

    if scheduled_datetime is not None:
        timestamp = timestamp_pb2.Timestamp()
        timestamp.FromDatetime(scheduled_datetime)
        task.schedule_time = timestamp

    if deadline_in_seconds is not None:
        duration = duration_pb2.Duration()
        duration.FromSeconds(deadline_in_seconds)
        task.dispatch_deadline = duration

    return client.create_task(
        tasks_v2.CreateTaskRequest(
            # The queue to add the task to
            parent=client.queue_path(project, location, queue),
            task=task,
        )
    )


def parse_targets_variables(targets: list[str], variables: str) -> dict:
    """
    Create a JSON structure with the given list of names.

    Args:
        targets list[str]: List of targets to be added to the Target array
        variables (str): List of variables to be added to the variables array
                    should be in the form 'variable1=value=service'

    Returns:
        dict: Formatted JSON with the targets and variables added
    """

    # Create the base structure
    json_structure: dict[str, list | dict] = {"targets": [], "variables": {}}
    env_vars, service_vars = {}, {}

    for variable in variables.split(" "):
        if not VARIABLES_REGEX.match(variable):
            raise ValueError("Variable must be in the format 'variable1=value=service'")
        variable = variable.split("=")
        if len(variable) <= 2 or variable[2] == "*":
            env_vars.update({variable[0]: str(variable[1])})
        else:
            service_vars.update({variable[0]: str(variable[1])})
    var_entry = {"env_vars": env_vars, "service_vars": {"main": service_vars}}

    json_structure["variables"].update(var_entry)  # type: ignore

    for target in targets:
        if not BOT_ID_REGEX.match(target):
            if not click.confirm(click.style(f"Targets include a fleet {target} are you sure?", fg="yellow")):
                logger.info(f"Skipping {target}")
                continue
        json_structure["targets"].append(target)  # type: ignore

    return json_structure


def get_user_email(credentials_file: str | None) -> str:
    """Get user info from credentials."""
    root_logger = logging.getLogger()
    _level = root_logger.level
    root_logger.setLevel(logging.INFO)
    if credentials_file is not None and os.path.isfile(credentials_file):
        credentials = google.auth.load_credentials_from_file(credentials_file, scopes=SCOPES)[0]
        email = load_json(credentials_file).get("client_email", "")
        root_logger.setLevel(_level)
        return email
    else:
        credentials: google.auth.credentials.Credentials = google.auth.default(scopes=CREDENTIAL_SCOPES, quota_project_id=PROJECT_ID)[0] # type: ignore
        credentials.refresh(Request())
        access_token = credentials.token
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get("https://www.googleapis.com/oauth2/v1/userinfo", headers=headers)
        root_logger.setLevel(_level)
        if response.ok:
            return response.json().get("email")
        else:
            logger.warning(f"Error getting user info: {response.status_code} {response.text}")
            return ""
        

# Get the user email from the service account or ADC
AUTHOR = get_user_email(SERVICE_ACCOUNT)
