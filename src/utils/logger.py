import logging
import sys

import urllib3
from colorlog import ColoredFormatter
from rich.logging import RichHandler

urllib3.disable_warnings(DeprecationWarning)
LOGGER = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s %(process)d %(name)s | %(message)s "
V_LEVELS = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
level = V_LEVELS.get(logging.INFO, logging.DEBUG)
logging.basicConfig(
    level=level, format=LOG_FORMAT, datefmt="[%X]", handlers=[RichHandler(rich_tracebacks=True)]
)

_STDERR_HANDLER = logging.StreamHandler(sys.stderr)
_LOGGER_FORMAT = (
    '%(asctime)s:'
    '%(log_color)s%(name)s[%(process)d]%(reset)s:'
    '%(log_color)s%(threadName)s| '
    '%(log_color)s%(levelname)-3s%(reset)s |'
    '%(log_color)s%(message)s%(reset)s'
)
_LOG_FORMATTER = ColoredFormatter(_LOGGER_FORMAT)
_STDERR_HANDLER.setFormatter(_LOG_FORMATTER)
LOGGER.addHandler(_STDERR_HANDLER)
LOGGER.setLevel('DEBUG')
