""" This module contains functions and variables to control dynasor's logging

* `logger` - the module logger
"""

import logging
import sys


# This is the root logger of dynasor.
logger = logging.getLogger('dynasor')

# Will process all levels of INFO or higher. This sets the default level.
logger.setLevel(logging.INFO)

# If you know what you are doing you may set this to True.
logger.propagate = False

# The dynasor logger will collect events from childs and the default behavior
# is to print it directly to stdout.
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(logging.Formatter(
    r'%(levelname)s %(asctime)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(ch)


def set_logging_level(level: str) -> None:
    """
    Alters the logging verbosity logging is handled.

    Possible values from least to most verbose:
    `CRITICAL`, `ERROR`, `WARNING`, `INFO`, `DEBUG`.

    Parameters
    ----------
    level
        Verbosity level; see `Python logging library
        <https://docs.python.org/3/library/logging.html>`_ for details.
    """
    logger.setLevel(level)
