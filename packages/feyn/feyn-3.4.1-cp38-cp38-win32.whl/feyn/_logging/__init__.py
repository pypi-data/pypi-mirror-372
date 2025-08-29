"""
Module for controlling the logging behaviour of feyn.
"""
from ._logging import _init_logger, _configure_notebook_logger
from ._jupyter_logger import JupyterLogger

__all__ = [
    '_init_logger',
    '_configure_notebook_logger',
    'JupyterLogger'
]
