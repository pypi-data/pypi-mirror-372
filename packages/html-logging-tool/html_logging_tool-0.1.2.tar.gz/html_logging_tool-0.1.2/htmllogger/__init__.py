from .core import Logger

# Create a singleton instance
_logger = Logger()

# Export the main functions


def log(message, color="white"):
    _logger.log(message, color)


def error(message):
    _logger.error(message)


def report_exception(exc, timeout=None):
    _logger.report_exception(exc, timeout)


def config(**kwargs):
    from . import config as cfg
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)


def flush():
    _logger.flush()
