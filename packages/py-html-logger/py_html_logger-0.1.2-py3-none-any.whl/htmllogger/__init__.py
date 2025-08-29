from .core import Logger

# Create a singleton instance
_logger = Logger()

# Export the main functions


def log(message, color="white", tag="log"):
    _logger.log(message, color, tag)


def info(message, color="white", tag="info"):
    _logger.info(message, color, tag)


def debug(message, color="white", tag="debug"):
    _logger.debug(message, color, tag)


def warning(message, color="gold", tag="warning"):
    _logger.warning(message, color, tag)


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
