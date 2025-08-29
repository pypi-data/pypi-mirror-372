import logging
import sys

logger = logging.getLogger("logger")

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
YELLOW = "\033[33m"
BLUE = "\033[34m"


# Custom formatter with color coding
class ColoredFormatter(logging.Formatter):
    """Formatter that applies colors based on log level."""

    COLORS = {
        logging.DEBUG: RESET,
        logging.INFO: BOLD,
        logging.WARNING: YELLOW,
        logging.ERROR: RED + BOLD,
        logging.CRITICAL: RED + BOLD + "!!! ",
    }

    def format(self, record):
        color = self.COLORS.get(record.levelno, RESET)
        message = super().format(record)
        return f"{color}{message}{RESET}"


def setup_logger(verbose=False):
    """
    Set up the global logger

    Args:
      verbose (bool): True if verbose, False otherwise
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(log_level)

    handler = logging.StreamHandler()
    handler.setLevel(log_level)

    formatter = ColoredFormatter("%(message)s")

    # INFO, DEBUG → stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.addFilter(lambda record: record.levelno < logging.WARNING)
    stdout_handler.setFormatter(formatter)

    # WARNING, ERROR, CRITICAL → stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)
    stderr_handler.setFormatter(formatter)

    # Clear existing handlers & add the new ones
    logger.handlers.clear()
    logger.addHandler(stdout_handler)
    logger.addHandler(stderr_handler)
