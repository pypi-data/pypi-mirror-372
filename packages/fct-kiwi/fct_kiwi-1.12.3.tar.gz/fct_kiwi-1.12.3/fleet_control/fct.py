#!/usr/bin/env python3
# =============================================================================
"""Balena Vars

Author:
    Juan Pablo Castillo - juan.castillo@kiwibot.com
"""
# =============================================================================
import click
import json, yaml
import logging
import datetime
import importlib.metadata
import fleet_control.logging_config
from fleet_control.utils.python_utils import (
    ColorFormatter,
    load_json,
    converter,
    select_option,
    COLORS,
    convert_values_to_strings,
)
from fleet_control.resources.commands import (
    change,
    clone,
    purge,
    get,
    delete,
    move,
    schedule_change,
    schedule_update,
    initialize,
    rename,
    pin,
)
from fleet_control.utils.utils import BOT_ID_REGEX, balena_sdk, get_device_by_id, get_fleet, parse_targets_variables

# =============================================================================
# Get package version from metadata
try:
    __version__ = importlib.metadata.version("fct-kiwi")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

logger = logging.getLogger(__name__)


@click.group()
@click.option(
    "--log-format",
    default=None,
    help="Specify the log format for the console handler (e.g., 'message').",
)
@click.option(
    "--silent",
    is_flag=True,
    help="Disable all logging output.",
)
@click.option(
    "--minimal-logs",
    is_flag=True,
    help="Only INFO output.",
)
@click.option(
    "--log-level",
    default="INFO",
    help="Set the logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).",
)
def cli(log_format, silent, minimal_logs, log_level):
    """Balena device configuration management tool."""
    handler = fleet_control.logging_config.console_handler

    if silent:
        logger.setLevel(logging.CRITICAL)  # Suppress all logs below CRITICAL
        handler.setLevel(logging.CRITICAL)
        logger.handlers.clear()  # Remove all handlers
    elif minimal_logs:
        logger.setLevel(logging.INFO)
        handler.setLevel(logging.INFO)
        handler.setFormatter(ColorFormatter(fmt="{message}"))
    else:
        # Set the logging level based on the provided log_level option
        log_level = log_level.upper()
        if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            logger.setLevel(getattr(logging, log_level))
            handler.setLevel(getattr(logging, log_level))
            logger.debug("Debugging mode enabled.")
        else:
            logger.warning(f"Invalid log level: {log_level}. Defaulting to INFO.")
            logger.setLevel(logging.INFO)
            handler.setLevel(logging.INFO)

        if log_format:
            handler.setFormatter(ColorFormatter(fmt=log_format))


@cli.group()
def schedule(name="schedule"):
    """Creates a GCP Task to send an HTTP POST request at an specified date"""
    pass


@cli.command(name="change")
@click.argument("variables", type=str, required=False)
@click.argument("targets", type=str, nargs=-1)
@click.option("--file", type=click.Path(exists=True, readable=True), help="Path to a file containing variables.")
@click.option("--force", is_flag=True, help="Don't check if the variable is already set.")
def _change(variables, targets: tuple, file, force: bool):
    """
    Change or create specified variable(s) to TARGET(s).

    \b
    VARIABLES: Separated by spaces in the form "var1=value1=service1 var2=value2=service2"
    TARGETS: One or more target bots (format: 4X000) and/or fleets

    \b
    Example: fct change 'VAR_NAME=0=*' 4X002 4X003
    Example with fleets: fct change 'VAR_NAME=0=*' FLEET_NAME Test4_x 4X003
    Example with file: fct change --file variables.txt '' 4X002 4X003
    """

    if file:
        variables = load_json(file)

    if not variables:
        logger.error("No variables provided.")
        exit(1)
    targets_set = list(targets)
    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id) and not click.confirm(
            click.style(f"Targets include a fleet {target_id} are you sure?", fg="yellow")
        ):
            targets_set.remove(target_id)
            continue

    change(variables, set(targets_set), force)


@cli.command(name="clone")
@click.option(
    "--exclude",
    type=str,
    help='Variables to exclude, must be in the format "var1 var2"',
)
@click.argument("source", type=str)
@click.argument("targets", type=str, nargs=-1)
def _clone(source: str, targets: tuple, exclude: str):
    """
    Clone configuration from SOURCE to TARGET(s).

    \b
    SOURCE: Either a device ID (format: 4X000) or a fleet name.
    TARGETS: One or more target device IDs (format: 4X000) or fleets.

    \b
    Example: fct clone 4X001 4X002 4X003
    Example with fleet: fct clone FLEET_NAME 4X002
    Example with fleet: fct clone FLEET_NAME ANOTHER_FLEET_NAME
    """
    targets_set = list(targets)
    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id) and not click.confirm(
            click.style(f"Targets include a fleet {target_id} are you sure?", fg="yellow")
        ):
            targets_set.remove(target_id)
            continue
    clone(source, set(targets_set), exclude)


@cli.command(name="purge")
@click.option(
    "--exclude",
    type=str,
    help='Variables to exclude, must be in the format "var1 var2"',
)
@click.argument("targets", type=str, nargs=-1)
def _purge(targets: tuple, exclude: str):
    """
    Purge all custom variables in TARGET device(s).

    \b
    TARGETS: One or more target device IDs (format: 4X000).

    \b
    Example: fct purge 4X001 4X002 4X003
    """
    purge(set(targets), exclude)


@cli.command(name="get")
@click.argument("variable_name", type=str, required=True)
@click.argument("targets", type=str, nargs=-1)
@click.option("--output", "-o", type=click.Path(writable=True), help="File to save the output.")
@click.option("--custom", "-c", is_flag=True, help="Return all custom vars")
@click.option("--all-vars", "-a", is_flag=True, help="Return all device + fleet vars")
@click.option("--output-yaml", "-y", is_flag=True, help="Output the result in YAML format instead of JSON")
def _get(targets: tuple, variable_name: str, output: str, custom: bool, all_vars: bool, output_yaml: bool):
    """
    Fetch variable value for a device.

    \b
    TARGETS: One or more target device IDs (format: 4X000).

    \b
    Example: fct get VAR_NAME 4X001 4X002 4X003
    Example with file output: fct get --output result.json VAR_NAME 4X001
    Example with custom vars: fct get --output result.json --custom '' 4X001 4X002 4X003
    Example with YAML output: fct get --output-yaml VAR_NAME 4X001 4X002 4X003
    Example with all vars: fct get --all-vars '' 4X001 4X002 4X003
    """

    if variable_name is None and not all_vars and not output and not custom:
        logger.error(f"No variables provided")
        exit(1)
    if output:
        all_vars = True
    result = get(set(targets), variable_name, custom, all_vars)
    if output_yaml:  # Handle YAML output
        yaml_output = yaml.dump(result, sort_keys=True, default_flow_style=False)
        logger.info(yaml_output)
    else:  # Default to JSON output
        logger.info(json.dumps(result, indent=2, sort_keys=True))
    if output:
        with open(output, "w") as f:
            if output_yaml:  # Write YAML to file
                yaml.dump(result, f, sort_keys=True, default_flow_style=False)
            else:  # Write JSON to file
                json.dump(result, f, indent=4, sort_keys=True)
        logger.info(f"Result saved to {output}")


@cli.command(name="delete")
@click.argument("variables", type=str, required=False)
@click.argument("targets", type=str, nargs=-1)
@click.option("--file", type=click.Path(exists=True, readable=True), help="Path to a file containing variables.")
def _delete(variables, targets: tuple, file):
    """
    Delete the overwritten value for the specified variable(s) on the TARGET device(s).

    \b
    VARIABLES: Separated by spaces in the form "var1=value1=service1 var2=value2=service2"
    TARGETS: One or more target device IDs (format: 4X000)

    \b
    Example: fct delete 'VAR_NAME=0=*' 4X002 4X003
    Example with file: fct delete --file variables.txt '' 4X002 4X003
    """

    if file:
        variables = load_json(file)

    if not variables:
        logger.error("No variables provided.")
        exit(1)
    delete(variables, set(targets))


@cli.command(name="move")
@click.option("--keep-vars", "-k", is_flag=True, help="keep custom device vars")
@click.option("--keep-service-vars", "-s", is_flag=True, help="keep custom device and service vars")
@click.option("--clone", "-c", is_flag=True, help="keep custom and previous fleet vars")
@click.option("--semver", "-p", type=str, help="pin to specific release (format: 1.3.11+rev87)")
@click.argument("fleet", type=str)
@click.argument("targets", type=str, nargs=-1)
def _move(fleet: str, targets: tuple, keep_vars: bool, keep_service_vars: bool, clone: bool, semver: str):
    """
    Move target(s) from its fleet to specified FLEET.

    \b
    FLEET: Chosen fleet's name (i.e: Test4_x).
    TARGETS: One or more target device IDs (format: 4X000).

    \b
    Example: fct move FLEET_NAME 4X001 4X002 4X003
    """
    move(fleet, set(targets), keep_vars, keep_service_vars, clone, semver)


@schedule.command(name="change")
@click.option("--file", type=click.Path(exists=True), help="File with the targets and variables to change.")
@click.option(
    "--date",
    default=(datetime.datetime.now() + datetime.timedelta(days=1))
    .replace(hour=3, minute=0, second=0, microsecond=0)
    .strftime("%Y-%m-%d %H:%M:%S"),
    help="The date string to convert (e.g., '2024-11-25 15:30:00') [default: Next day at 3am]",
    show_default=False,
)
@click.option(
    "--format", "date_format", default="%Y-%m-%d %H:%M:%S", help="The format of the date string", show_default=True
)
@click.option(
    "--tz",
    # type=click.Choice(pytz.common_timezones),
    default="America/Bogota",
    help="The timezone for the schedule date",
    show_default=True,
)
@click.argument("variables", required=False)
@click.argument("targets", nargs=-1, required=False)
def _schedule_change(file: str, date: str, date_format: str, tz: str, variables: str, targets: tuple):
    """
    POST request with variables to change in some targets to a Google Pub/Sub topic at a specified time.

    \b
    VARIABLES: must be in the format 'variable1=value=service'. Optional if using --file flag.
    TARGETS: to apply the changes to separated by spaces. Optional if using --file flag.

    \b
    Example: fct schedule change --date '2025-02-25 12:06:00' 'VAR_NAME=0=main' 4X001 4X002
    Example: fct schedule change --file vars.json --date '2025-02-25 12:06:00'
    """

    # Helper function to process JSON file or command-line variables/targets
    def process_input_data(json_file, variables_str, targets):
        if json_file:
            logger.info(f"Using JSON file: {json_file}")
            dictionary: dict[str, dict | str] = convert_values_to_strings(load_json(json_file))  # type: ignore
            return dictionary
        elif variables_str and targets:
            return parse_targets_variables(targets, variables_str)
        else:
            logger.error("Both variables and targets are required when no JSON file is provided.")
            exit(1)

    # Process input data (from JSON file or command-line arguments)
    message_data = process_input_data(file, variables, targets)

    schedule_change(message_data, date, date_format, tz)


@schedule.command(name="update")
@click.option("--file", type=click.Path(exists=True), help="File with the targets and selected release")
@click.option(
    "--date",
    default=(datetime.datetime.now() + datetime.timedelta(days=1))
    .replace(hour=3, minute=0, second=0, microsecond=0)
    .strftime("%Y-%m-%d %H:%M:%S"),
    help="The date string to convert (e.g., '2024-11-25 15:30:00') [default: Next day at 3am]",
    show_default=False,
)
@click.option(
    "--format", "date_format", default="%Y-%m-%d %H:%M:%S", help="The format of the date string", show_default=True
)
@click.option(
    "--tz",
    # type=click.Choice(pytz.common_timezones),
    default="America/Bogota",
    help="The timezone for the schedule date",
    show_default=True,
)
@click.argument("fleet", required=False)
@click.argument("release", required=False)
@click.argument("targets", nargs=-1, required=False)
def _schedule_update(file: str, date: str, date_format: str, tz: str, targets: tuple, fleet: str, release: str):
    """
    POST request with targets to pin to a specific release.

    \b
    FLEET: fleet from which the targets and the release belong to. Optional if using --file flag.
    RELEASE: semantic version of the target release (i.e: 1.3.12+rev12). Optional if using --file flag.
    TARGETS: to pin to the release separated by spaces. Optional if using --file flag.

    \b
    Example: fct schedule update FLEET_NAME 1.3.19+rev43 4X001 4X002
    Example: fct schedule update --date '2025-02-25 12:06:00' FLEET_NAME 1.3.19+rev43 4X001
    Example: fct schedule update --file file.json --date '2025-02-25 12:06:00'
    """

    # Helper function to process JSON file or command-line variables/targets
    def process_input_data(json_file, targets, fleet, release):
        if json_file:
            logger.info(f"Using JSON file: {json_file}")
            dictionary: dict[str, list | str] = convert_values_to_strings(load_json(json_file))  # type: ignore
            return dictionary
        elif targets and fleet and release:
            json_structure: dict[str, list | str] = {"targets": [], "fleet": fleet, "release": release}
            for target_id in targets:
                if not BOT_ID_REGEX.match(target_id):
                    logger.info(f"Skipping invalid target ID format: {target_id}")
                    continue
                json_structure["targets"].append(target_id)  # type: ignore
            return json_structure
        else:
            logger.error("Targets, fleet, and release are required when no JSON file is provided.")
            exit(1)

    message_data = process_input_data(file, targets, fleet, release)

    schedule_update(message_data, date, date_format, tz)


@cli.command(name="initialize")
@click.argument("fleet", type=str)
@click.argument("target", type=str)
def _initialize(fleet: str, target: str):
    """
    Initialize TARGET with previous device tags, remove old device, delete default config variables, and move to specified FLEET.

    \b
    FLEET: Chosen fleet's name (i.e: Test4_x).
    TARGET: Target device ID (format: 4X000).

    \b
    Example: fct initialize FLEET_NAME 4X001
    """
    fleet_id = get_fleet(fleet)["id"]
    bots = balena_sdk.models.device.get_all_by_application(fleet_id)
    sorted_bots = sorted(bots, key=lambda d: d["created_at"], reverse=True)
    new_bot = sorted_bots[0]
    del bots, sorted_bots

    bot_to_delete = get_device_by_id(target)

    if bot_to_delete and click.confirm(
        f'Do you want to delete the old device {bot_to_delete.get("device_name")} and initialize {new_bot.get("device_name")}? ',
        default=True,
    ):
        initialize(bot_to_delete, fleet)


@cli.command(name="rename")
@click.argument("target", type=str)
@click.argument("new_id", type=str)
@click.option("--version", "-v", type=str, help="Overwrite tags with tags from configuration file for version")
def _rename(target: str, new_id: str, version: str):
    """
    Rename TARGET with new ID. Optional new tags for corresponding version read from configuration file.

    \b
    TARGET: Target device ID (format: 4X000).
    NEW_ID: New device ID (format: 4X000).

    \b
    Example: fct rename 4A001 4B222
    Example: fct rename --version 4.3F 4A001 4B222
    """

    # Validate input formats
    if not BOT_ID_REGEX.match(target):
        logger.error(f"Invalid target ID format: {target}")
        exit(1)

    bot_to_rename = get_device_by_id(target)
    if (
        click.confirm(
            f"Do you want to rename the device {target} to {new_id}?",
            default=True,
        )
        and bot_to_rename
    ):
        rename(bot_to_rename, new_id, version=version)


@cli.command(name="converter")
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
def _converter(input_file, output_file):
    """
    Convert a shell env var file to a JSON config file.
    All variables starting with NODE_ go to 'env_vars'.
    All others go to 'service_vars' > 'main'.
    """
    converter(input_file, output_file)
    logger.info(f"Converted {input_file} to {output_file}")


@cli.command(name="pin")
@click.option("--all", "-a", is_flag=True, help="pin all targets in the fleet")
@click.option(
    "--exclude",
    type=str,
    help='Devices to exclude, must be in the format "id1 id2 id3" (e.g., "4X001 4X002")',
)
@click.option("--semver", "-p", type=str, help="pin to specific release (format: 1.3.11+rev87)")
@click.argument("fleet", type=str)
@click.argument("targets", nargs=-1)
def _pin(fleet: str, semver: str, targets: tuple, all: bool, exclude: str):
    """
    Pin TARGET(s) to specified FLEET release SEMVER.
    If no targets specified, pin fleet.
    If `all` is True, pin all devices in the fleet.

    \b
    FLEET: Chosen fleet's name (i.e: Test4_x).
    SEMVER: Semantic version of the target release (i.e: 1.3.12+rev12).
    TARGETS: One or more target device IDs (format: 4X000).

    \b
    Example: fct pin FLEET_NAME 4X001 4X002 4X003
    Example with fleet: fct pin FLEET_NAME --semver 1.3.12+rev12
    Example with all devices: fct pin FLEET_NAME --all
    Example with exclude: fct pin FLEET_NAME --all --exclude "4X001 4X002"
    """
    exclude_set = set()
    if exclude:
        exclude_set = set(exclude.split())

    targets_set = list(targets)

    if not targets_set and not all:
        logger.warning("No targets provided. Use --all to pin all devices in the fleet.")
        if semver:
            click.confirm(
                click.style(f"Are you sure you want to pin the fleet {fleet} to {semver}?", fg="yellow"),
                abort=True,
            )
        else:
            click.confirm(
                click.style(f"Are you sure you want to pin the fleet {fleet} to the latest release?", fg="yellow"),
                abort=True,
            )

    elif all:
        click.confirm(
            click.style(f"Are you sure you want to pin all devices in the fleet {fleet}?", fg="yellow"),
            abort=True,
        )

    else:
        for target_id in targets:
            if not BOT_ID_REGEX.match(target_id):
                targets_set.remove(target_id)
                logger.info(f"Skipping invalid target ID format: {target_id}")
                continue

    pin(fleet, semver, set(targets_set), all=all, exclude=exclude_set)

@cli.command(name="version")
def _version():
    """
    Get the version of the package.
    """
    print(f"fleet_control version: {__version__}")


if __name__ == "__main__":
    cli()
