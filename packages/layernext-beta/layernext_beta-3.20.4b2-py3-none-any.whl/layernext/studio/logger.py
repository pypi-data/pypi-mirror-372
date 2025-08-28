import logging
import logging.handlers
import sys


def get_debug_logger(name):

    _logger = logging.getLogger(name)
    _logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger
