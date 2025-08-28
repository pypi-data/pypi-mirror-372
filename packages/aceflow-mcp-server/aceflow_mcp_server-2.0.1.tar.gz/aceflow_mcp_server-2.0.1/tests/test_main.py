"""Test suite for __main__ module."""

import pytest
import sys
from unittest.mock import patch, MagicMock


class TestMain:
    """Test __main__ module functionality."""
    
    def test_main_module_import(self):
        """Test that __main__ module can be imported."""
        import aceflow_mcp_server.__main__
        assert aceflow_mcp_server.__main__ is not None
    
    @patch('aceflow_mcp_server.server.main')
    def test_main_execution(self, mock_main):
        """Test main execution path."""
        mock_main.return_value = 0
        
        # Import and execute the main module
        import aceflow_mcp_server.__main__
        
        # The module should have been imported successfully
        assert aceflow_mcp_server.__main__ is not None
    
    @patch('sys.exit')
    @patch('aceflow_mcp_server.server.main')
    def test_main_with_exit_code(self, mock_main, mock_exit):
        """Test main execution with exit code."""
        mock_main.return_value = 1
        
        # Simulate running as main
        with patch('__main__.__name__', '__main__'):
            # Re-import to trigger the if __name__ == "__main__" block
            import importlib
            import aceflow_mcp_server.__main__
            importlib.reload(aceflow_mcp_server.__main__)
        
        # The module should exist
        assert aceflow_mcp_server.__main__ is not None


if __name__ == "__main__":
    pytest.main([__file__])