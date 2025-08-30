"""utility functions for logging"""
import logging

LOGGING_LEVEL = logging.CRITICAL
LOGGING_LEVELS = ('NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')


def get_logger(name):
    """return a custom logger object"""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        fstr = '%(levelname)s:%(name)s:%(message)s'
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fstr))
        logger.addHandler(handler)
    logger.setLevel(LOGGING_LEVEL)
    return logger


def get_logging_level(logging_level):
    """return the logging level from string"""
    return getattr(logging, logging_level)


def disable_logging():
    """disable logging globally"""
    logging.disable(logging.CRITICAL)
