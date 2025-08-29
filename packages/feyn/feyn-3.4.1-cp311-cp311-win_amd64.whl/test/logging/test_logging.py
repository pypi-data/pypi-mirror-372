import unittest
from unittest.mock import MagicMock, patch, Mock

import logging

from feyn._logging import _configure_notebook_logger, _init_logger, JupyterLogger

class CustomLogger(logging.Logger):
    ...

@patch('feyn._logging._logging.detect_notebook')
@patch('logging.setLoggerClass')
@patch('logging.getLoggerClass')
@patch('logging.getLogger')
class TestLogging(unittest.TestCase):

    def setUp(self):
        self.mockLogger = MagicMock(logging.Logger)
        self.mock_detect_notebook = MagicMock()

        self.customMockLogger = MagicMock(CustomLogger)
    
    def test_default_handler_and_level_if_no_conf_exists(self, mock_getLogger: Mock, mock_getLoggerClass: Mock, mock_setLoggerClass: Mock, mock_detect_notebook: Mock):
        # Not configured root logger
        self.mockLogger.hasHandlers = Mock(return_value = False)
        self.mockLogger.level = logging.NOTSET

        mock_getLogger.return_value = self.mockLogger

        _init_logger('log_test')

        self.mockLogger.hasHandlers.assert_called()

        self.mockLogger.addHandler.assert_called() # Default handler added
        self.mockLogger.setLevel.assert_called_with(logging.INFO) # Default level set


    def test_no_handler_if_conf_already_exists(self, mock_getLogger: Mock, mock_getLoggerClass: Mock, mock_setLoggerClass: Mock, mock_detect_notebook: Mock):
        # configured root logger
        self.mockLogger.hasHandlers = Mock(return_value = True)
        mock_getLogger.return_value = self.mockLogger

        _init_logger('log_test')

        self.mockLogger.hasHandlers.assert_called()

        self.mockLogger.addHandler.assert_not_called() # Handlers should not be added
        self.mockLogger.setLevel.assert_not_called() # Level should not be se
    
    def test_log_level_preserved_if_conf_already_exists(self, mock_getLogger: Mock, mock_getLoggerClass: Mock, mock_setLoggerClass: Mock, mock_detect_notebook: Mock):
        # Not configured root logger
        self.mockLogger.hasHandlers = Mock(return_value = False)
        self.mockLogger.level = logging.WARNING
        mock_getLogger.return_value = self.mockLogger

        _init_logger('log_test')

        self.mockLogger.hasHandlers.assert_called()

        self.mockLogger.addHandler.assert_called()
        self.mockLogger.setLevel.assert_not_called() # Level should not be reset if already set

    
    def test_jupyter_logger_gets_configured_if_no_conf_exists(self, mock_getLogger: Mock, mock_getLoggerClass: Mock, mock_setLoggerClass: Mock, mock_detect_notebook: Mock):
        # Not configured root logger
        self.mockLogger.hasHandlers = Mock(return_value = False)
        mock_getLogger.return_value = self.mockLogger

        mock_getLoggerClass.return_value = logging.Logger

        mock_detect_notebook.return_value = True

        _configure_notebook_logger()

        self.mockLogger.hasHandlers.assert_called()

        mock_getLoggerClass.assert_called()
        mock_getLogger.assert_called_with() # Root logger should have been tested
        mock_setLoggerClass.assert_called_with(JupyterLogger) # Jupyter Logger should have been set
    
    def test_jupyter_logger_does_not_get_configured_if_conf_exists(self, mock_getLogger: Mock, mock_getLoggerClass: Mock, mock_setLoggerClass: Mock, mock_detect_notebook: Mock):
        self.mockLogger.hasHandlers = Mock(return_value = True)
        mock_getLoggerClass.return_value = logging.Logger
        
        # Already configured root logger
        self.mockLogger.hasHandlers.returnValue = True
        mock_getLogger.return_value = self.mockLogger

        _configure_notebook_logger()
        
        self.mockLogger.hasHandlers.assert_called()

        mock_getLogger.assert_called_with() # Root logger should have been tested
        mock_setLoggerClass.assert_not_called() # Jupyter logger should not be set
    
    def test_jupyter_logger_does_not_get_configured_if_custom_logger_registered(self, mock_getLogger: Mock, mock_getLoggerClass: Mock, mock_setLoggerClass: Mock, mock_detect_notebook: Mock):
        mock_detect_notebook.return_value = True

        # Not configured root logger
        self.mockLogger.hasHandlers = Mock(return_value = False)
        mock_getLogger.return_value = self.mockLogger

        # Custom logger registered
        mock_getLoggerClass.return_value = self.customMockLogger
        
        _configure_notebook_logger()

        mock_getLoggerClass.assert_called()
        mock_setLoggerClass.assert_not_called() # Jupyter logger should not be set