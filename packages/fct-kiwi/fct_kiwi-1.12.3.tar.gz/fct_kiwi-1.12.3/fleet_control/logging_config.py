import logging
from fleet_control.utils.python_utils import ColorFormatter

# Set up root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Controls what gets emitted

# Console handler with color
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(ColorFormatter())

# Optional: file handler without color
# file_handler = logging.FileHandler("app.log", encoding="utf-8")
# file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(logging.Formatter("{levelname} - {message}", style="{"))

# Remove existing handlers (if re-running in interactive sessions)
if logger.hasHandlers():
    logger.handlers.clear()

# Add new handlers
logger.addHandler(console_handler)
# logger.addHandler(file_handler)
