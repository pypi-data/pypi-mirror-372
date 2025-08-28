#!/usr/bin/env python3
# =============================================================================
"""
Code Information:
    This script contains some python utils.

    Maintainer:
    Juan Pablo Castillo - juan.castillo@kiwibot.com
        Kiwi Campus / Service Desk Team
"""
# =============================================================================

import logging
import os
import datetime
import inspect
import pytz
import re
from functools import wraps
from sys import stderr
from balena.exceptions import DeviceNotFound, RequestError
import json


logger = logging.getLogger(__name__)


# =============================================================================
# ANSI escape sequences for colors
COLORS = {
    "DEBUG": "\033[94m",  # Blue
    "INFO": "\033[0m",  # Green
    "WARNING": "\033[93m",  # Yellow
    "ERROR": "\033[91m",  # Red
    "CRITICAL": "\033[95m",  # Magenta
    "RESET": "\033[0m",  # Reset
    "OK_BLUE": "\033[34m",
    "OK_GREEN": "\033[32m",
    "OK_PURPLE": "\033[35m",
}
BOT_ID_REGEX = re.compile("[0-9][A-Z][0-9]{3}$")


class ColorFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt="%Y-%m-%d %H:%M:%S", style="{"):
        if fmt is None:
            fmt = "[{asctime}][{levelname}][{name}] {message}"
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)  # type: ignore

    def format(self, record):
        # Save original message first
        original_msg = super().format(record)

        level_color = COLORS.get(record.levelname, COLORS["RESET"])
        reset = COLORS["RESET"]

        # Wrap the whole final message with color if needed
        return f"{level_color}{original_msg}{reset}"


class BalenaAPIError(Exception):
    """Custom exception for Balena API errors."""

    def __init__(self, status_code, message="Balena API request failed"):
        self.status_code = status_code
        super().__init__(f"{message} (status code: {status_code})")


def select_option(
    msg: str,
    options: list[str] = ["Yes", "No"],
    msg_type: str = "INFO",
    verbose: bool = True,
    case_insensitive: bool = False,
) -> str:
    """!
    Function
    @param msg `string` message to print
    @param options `list` options to choose
    @param msg_type string` message type
    @param case_insensitive `bool` create case insensitive options
    """

    use_verbose = True if int(os.getenv(key="USE_VERBOSE", default=0)) == 1 else False

    opts = [i.lower() for i in options] if case_insensitive else options

    org = os.path.splitext(os.path.basename(inspect.stack()[1][1]))[0].upper()
    _str = "[{}][{}] {} ({}): ".format(msg_type, org, msg, "/".join(options))
    if verbose or use_verbose:
        log_msg = COLORS[msg_type] + "[{:%Y-%m-%d %H:%M:%S}]".format(datetime.datetime.now()) + _str + COLORS["RESET"]
    else:
        log_msg = COLORS[msg_type] + _str + COLORS["RESET"]

    opt = ""
    while opt not in opts:
        opt = input(log_msg)
        if case_insensitive:
            opt = opt.lower()
    return options[opts.index(opt)]


def handle_request_error(raise_exception=True):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RequestError as e:
                msg = f"Balena status code: {e.status_code}. Please try again in a few minutes."
                logger.error(msg)
                logger.exception(f"{func.__name__} failed with status {e.status_code}: {e}")
                if raise_exception:
                    raise BalenaAPIError(e.status_code) from e

        return wrapper

    return decorator


def load_json(filename):
    with open(filename, "r") as f:
        data = f.read()
    return json.loads(data)


def confirm_schedule(message_data: dict[str, dict], date_object, tz) -> str:
    # if message_data["purge"]:
    #     logger.warning("Variables will be purged")

    if message_data.get("variables"):
        logger.info(f"{COLORS['OK_PURPLE']} Variables to change: {COLORS['RESET']}")
        for var, value in message_data["variables"]["env_vars"].items():
            logger.info(f"{var} = {value}")
        for var, value in message_data["variables"]["service_vars"]["main"].items():
            logger.info(f"{var} = {value}")
    else:
        logger.info(f"{COLORS['OK_PURPLE']}{message_data['fleet']}: {message_data['release']}{COLORS['RESET']}")

    logger.info(f"{COLORS['OK_PURPLE']}Devices/Fleets to apply changes: {COLORS['RESET']}")
    for target in message_data["targets"]:
        logger.info(f"{'Fleet' if not BOT_ID_REGEX.match(target) else 'Device'}: {target}")

    logger.info(
        f"{COLORS['OK_PURPLE']}Time selected: {datetime.datetime.strftime(date_object,'%Y-%m-%d %H:%M:%S GMT%Z')}{COLORS['RESET']}",
    )
    if date_object < datetime.datetime.now(pytz.timezone(tz)):
        logger.warning("Time selected is earlier than current time, task will run immediately!")

    opt = select_option(
        "Do you want to continue?",
        ["Yes", "Y", "No", "N"],
        msg_type="OK_BLUE",
        case_insensitive=True,
    )
    return opt

def format_time(date_string, date_format: str, timezone: str = "America/Bogota"):
    """Creates datetime objects for the datetime input"""

    start = datetime.datetime.strptime(date_string, date_format)
    try:
        tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        logger.error(f"Unknown Time Zone: {timezone}")
        exit(1)
    date_object = tz.localize(start)

    return date_object


def convert_values_to_strings(data):
    """Recursively converts all values in a dictionary or list to strings."""
    if isinstance(data, dict):
        return {k: convert_values_to_strings(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_values_to_strings(item) for item in data]
    else:
        return str(data)


def converter(input_file, output_file):
    """
    Convert a shell env var file to a JSON config file.
    - All variables starting with NODE_ go to 'env_vars'
    - All others go to 'service_vars' > 'main'
    """
    env_vars = {}
    service_vars = {}

    with open(input_file, "r") as f:
        for line in f:
            match = re.match(r'export\s+([A-Z0-9_]+)=(.*)', line)
            if match:
                var, val = match.groups()
                val = val.strip()
                # Remove inline comments (anything after #)
                if '#' in val:
                    val = val.split('#', 1)[0].strip()
                # Remove one pair of surrounding quotes if present
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                if var.startswith("NODE_"):
                    env_vars[var] = val
                else:
                    service_vars[var] = val

    output = {
        "env_vars": env_vars,
        "service_vars": {
            "main": service_vars
        }
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)

def read_file_to_list(file_path):
    """Reads a text file and returns its contents as a list of lines, ignoring comments."""
    with open(file_path, "r") as file:
        lines = file.readlines()
    # Remove newline characters and ignore lines starting with '#'
    return [line.strip() for line in lines if not line.strip().startswith("#")]
