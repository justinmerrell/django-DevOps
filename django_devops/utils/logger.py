""" A clean logging formatter utility """

import sys

# ANSI escape codes for different colors
COLOR_MAP = {
    'DEBUG': '\033[92m',   # Green
    'INFO': '\033[94m',    # Blue
    'WARNING': '\033[93m', # Yellow
    'ERROR': '\033[91m',   # Red
    'CRITICAL': '\033[95m' # Magenta
}

RESET_CODE = '\033[0m'

def log(message: str, level: str = "INFO") -> None:
    """
    Print a log message to stdout with colored level labels.

    Args:
        message (str): The message to display.
        level (str): Log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
                     Defaults to INFO.
    """
    level = level.upper()
    color = COLOR_MAP.get(level, '')  # Default to no color if level is unknown
    label = f"[{level}]"
    formatted_label = f"{color}{label}{RESET_CODE}" if color else label
    print(f"{formatted_label} {message}", file=sys.stdout)
