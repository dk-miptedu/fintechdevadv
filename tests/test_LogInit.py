import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.append(src_dir)

import unittest
import logging
from unittest.mock import patch
import log_handler.LogInit  # Assuming LogInit is the file name where logging is configured

class TestLogInit(unittest.TestCase):

    @patch('logging.getLogger')
    @patch('logging.basicConfig')
    def test_logging_setup(self, mock_basicConfig, mock_getLogger):
        # Reload the LogInit module to ensure logging setup runs
        import importlib
        importlib.reload(log_handler.LogInit)

        # Check that logging.basicConfig was called with the expected parameters
        mock_basicConfig.assert_called_once_with(
            level=logging.DEBUG, 
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Check that getLogger was called and a logger was created
        mock_getLogger.assert_called_once_with(log_handler.LogInit.__name__)

if __name__ == "__main__":
    unittest.main(verbosity=2)
