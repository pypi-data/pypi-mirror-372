# --------------- Imports ---------------

import logging

from logging.handlers import RotatingFileHandler

# --------------- Logging Configuration ---------------

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        fileHandler = RotatingFileHandler(
        filename="app.log",
        maxBytes=10000,
        backupCount=3,
        encoding='utf-8',
        delay=False
        )
    
        format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileHandler.setFormatter(format)
        logger.addHandler(fileHandler)

    return logger