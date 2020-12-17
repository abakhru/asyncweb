import logging

import urllib3
from rich.logging import RichHandler

urllib3.disable_warnings(DeprecationWarning)
LOGGER = logging.getLogger('fastapi')
LOG_FORMAT = "%(asctime)s %(process)d %(name)s | %(message)s "
logging.basicConfig(handlers=[RichHandler(rich_tracebacks=True, show_time=True)],
                    format=LOG_FORMAT)
LOGGER.setLevel('DEBUG')
