""" Functions to setup and control feyn's internal logging """
import logging

from feyn._compatibility import detect_notebook
from ._jupyter_logger import JupyterLogger

_default_formatter = logging.Formatter('[%(levelname)s: %(name)s] - %(message)s')

def _configure_notebook_logger():
    if detect_notebook():
        # Less output is desirable in notebook environments, since it's for humans
        _default_formatter = logging.Formatter('[%(levelname)s] - %(message)s')

        # Only extend logging for Jupyter notebooks if no existing configuration exists and no other custom loggers are configured
        if logging.Logger == logging.getLoggerClass() and not logging.getLogger().hasHandlers():
            # Extend the logger for Jupyter environments where we'd like to display print info and debug messages instead
            logging.setLoggerClass(JupyterLogger)


def _init_logger(logger_name: str) -> logging.Logger:
    """ Initialize a logger for a module.
    Adds stream handlers to the logger if:
    1. The root logger is not configured and has no handlers
    2. AND the module logger or its parents don't have any handlers configured.

    If both of these conditions are met, it also sets the default level of the logger to INFO if the logging level is not set for the module.
    
    This means that any submodule loggers initialised after the parent will get no handlers attached, and remain with a NOTSET level, propagating all messages to the parent, which decides what to ignore and what to pass on.
    For more fine-grained control, levels can be set on the submodule level to avoid propagation of messages.

    If configuration already exists, the function just returns the logger.

    Arguments:
        logger_name {str} -- The name of the module to log for

    Returns:
        logging.Logger -- The logger
    """
    root_logger = logging.getLogger()
    logger = logging.getLogger(logger_name)

    # Add a handler only if the root logger is not configured and no handlers exist on this or parent loggers.
    if not root_logger.hasHandlers() and not logger.hasHandlers():
        # Note: Adding a stream handler is the least invasive option of ensuring we can default to log levels below WARNING
        logger.addHandler(_getStreamHandler())

        # Set the log level to INFO if no root configuration exists and the user has not set the level to something else.
        if logger.level == logging.NOTSET:
            logger.setLevel(logging.INFO)
    
    return logger


def _getStreamHandler():
    handler = logging.StreamHandler()
    handler.setFormatter(_default_formatter)
    return handler