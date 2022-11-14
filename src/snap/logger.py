"""Set up logging to stderr and or file."""
import logging
import os
from logging.handlers import RotatingFileHandler

import coloredlogs

from snap.config import LOG_DIR, LOGFILE, LOGFILE_SIZE, LOGLEVEL

log = logging.getLogger(__name__)


def log_init(debug: bool):
    azurelog = logging.getLogger("azure.cosmosdb.table")
    azurelog.setLevel(logging.WARNING)

    level = logging.DEBUG if debug else logging.INFO
    log.setLevel(logging.DEBUG)
    log_format = "%(levelname)-5.5s: %(message)s"

    # format = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
    # c_handler = logging.StreamHandler()
    # c_handler.setFormatter(format)
    # c_handler.setLevel(level)
    # log.addHandler(c_handler)
    coloredlogs.DEFAULT_LEVEL_STYLES.update({
        'debug': {
            'color': 'white',
            'faint': True
        },
        'info': {
            'color': 'white'
        },
        'error': {
            'bold': True,
            'color': 'red'
        }
    })
    coloredlogs.DEFAULT_FIELD_STYLES = {"loglevel": {"bold": True}}
    # coloredlogs.DEFAULT_LEVEL_STYLES = style
    coloredlogs.install(level=level, fmt=log_format, datefmt="%Y-%m-%d %H:%M:%S")

    if LOGFILE and LOGFILE_SIZE:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
        filename = f"{LOG_DIR}/{LOGFILE}"
        f_handler = RotatingFileHandler(filename, mode="w", maxBytes=LOGFILE_SIZE, backupCount=1)
        loglevel = getattr(logging, LOGLEVEL.upper())
        f_handler.setLevel(loglevel)
        format = logging.Formatter("%(asctime)s %(levelname)-5.5s: %(message)s",
                                   datefmt="%Y-%m-%d %H:%M:%S")
        f_handler.setFormatter(format)
        log.addHandler(f_handler)
