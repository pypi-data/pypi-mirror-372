from feyn._logging import JupyterLogger
import unittest
from unittest.mock import patch, Mock

from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

class TestJupyterLogger(unittest.TestCase):

    def setUp(self):
        self.jl = JupyterLogger("testlog")
        self.jl._log = Mock()

    
    @patch('feyn._logging._jupyter_logger._display')
    def test_jupyter_logger_display_on_info(self, mock_display: Mock):
        self.jl.isEnabledFor = Mock(return_value=True)

        msg = "Hi"
        self.jl.info(msg)

        mock_display.assert_called_with(msg)
        self.jl._log.assert_not_called()


    @patch('feyn._logging._jupyter_logger._display')
    def test_jupyter_logger_display_on_debug(self, mock_display: Mock):
        self.jl.isEnabledFor = Mock(return_value=True)
        
        msg = "Hi"
        self.jl.debug(msg)

        mock_display.assert_called_with("[DEBUG] - " + msg)
        self.jl._log.assert_not_called()
    
    @patch('feyn._logging._jupyter_logger._display')
    def test_jupyter_logger_logs_everything_else(self, mock_display: Mock):
        msg = "Hi"
        self.jl.warning(msg)
        self.jl._log.assert_called_with(WARNING, msg, ())

        self.jl.error(msg)
        self.jl._log.assert_called_with(ERROR, msg, ())
        
        self.jl.critical(msg)
        self.jl._log.assert_called_with(CRITICAL, msg, ())


    @patch('feyn._logging._jupyter_logger._display')
    def test_jupyter_logger_disable_display(self, mock_display: Mock):
        self.jl.use_display = False

        msg = "Hi"
        self.jl.info(msg)
        self.jl._log.assert_called_with(INFO, msg, ())

        self.jl.debug(msg)
        self.jl._log.assert_called_with(DEBUG, msg, ())