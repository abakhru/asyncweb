import logging

import urllib3
from rich.logging import RichHandler

urllib3.disable_warnings(DeprecationWarning)
LOGGER = logging.getLogger(__name__)
LOG_FORMAT = "%(asctime)s %(process)d %(name)s | %(message)s "
logging.basicConfig(handlers=[RichHandler(rich_tracebacks=True, show_time=True)])
LOGGER.setLevel('DEBUG')
