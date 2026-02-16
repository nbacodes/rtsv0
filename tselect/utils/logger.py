import logging
import sys

# ANSI COLORS
RESET = "\x1b[0m"
COLORS = {
    "DEBUG": "\x1b[36m",     # Cyan
    "INFO": "\x1b[32m",      # Green
    "WARNING": "\x1b[33m",   # Yellow
    "ERROR": "\x1b[31m",     # Red
    "CRITICAL": "\x1b[41m",  # Red background
}


class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        color = COLORS.get(levelname, "")
        record.levelname = f"{color}{levelname}{RESET}"
        return super().format(record)


def setup_logger():
    logger = logging.getLogger("tselect")

    # Prevent duplicate handlers if imported multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)   # Default level

    handler = logging.StreamHandler(sys.stdout)

    formatter = ColorFormatter(
        "[%(levelname)s] %(message)s"
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
