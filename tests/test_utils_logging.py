"""
Tests for utils logging module.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import tempfile
import logging

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.logging_utils import (
    setup_logging,
    get_logger,
    log_function_call,
    log_error,
    log_performance
)


class TestSetupLogging:
    """Test logging setup functionality."""
    
    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        logger = setup_logging()
        
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.INFO
    
    def test_setup_logging_with_level(self):
        """Test logging setup with custom level."""
        logger = setup_logging(log_level="DEBUG")
        
        assert isinstance(logger, logging.Logger)
        assert logger.level == logging.DEBUG
    
    def test_setup_logging_with_file(self):
        """Test logging setup with file output."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "test.log"
            
            logger = setup_logging(log_file=str(log_path))
            
            assert isinstance(logger, logging.Logger)
            assert log_path.exists()
    
    def test_setup_logging_creates_directory(self):
        """Test that logging setup creates directory if needed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "subdir" / "test.log"
            
            logger = setup_logging(log_file=str(log_path))
            
            assert isinstance(logger, logging.Logger)
            assert log_path.parent.exists()


class TestGetLogger:
    """Test logger retrieval functionality."""
    
    def test_get_logger_basic(self):
        """Test basic logger retrieval."""
        logger = get_logger("test_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
    
    def test_get_logger_different_names(self):
        """Test that get_logger returns different instances for different names."""
        logger1 = get_logger("logger1")
        logger2 = get_logger("logger2")
        
        assert logger1.name == "logger1"
        assert logger2.name == "logger2"
    
    def test_get_logger_module_name(self):
        """Test getting logger with module name."""
        logger = get_logger(__name__)
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == __name__


class TestLogFunctionCall:
    """Test function call logging."""
    
    @patch('utils.logging_utils.get_logger')
    def test_log_function_call_basic(self, mock_get_logger):
        """Test basic function call logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_function_call("test_function", ("arg1", "arg2"), {"key": "value"})
        
        mock_logger.debug.assert_called_once()
        call_args = mock_logger.debug.call_args[0][0]
        assert "test_function" in call_args
        assert "arg1" in call_args
        assert "key" in call_args
    
    @patch('utils.logging_utils.get_logger')
    def test_log_function_call_empty_args(self, mock_get_logger):
        """Test function call logging with empty arguments."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_function_call("test_function", (), {})
        
        mock_logger.debug.assert_called_once()


class TestLogError:
    """Test error logging functionality."""
    
    @patch('utils.logging_utils.get_logger')
    def test_log_error_basic(self, mock_get_logger):
        """Test basic error logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        error = ValueError("Test error")
        log_error(error)
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "ValueError" in call_args
        assert "Test error" in call_args
    
    @patch('utils.logging_utils.get_logger')
    def test_log_error_with_context(self, mock_get_logger):
        """Test error logging with context."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        error = RuntimeError("Test runtime error")
        log_error(error, "test_function")
        
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args[0][0]
        assert "test_function" in call_args
        assert "RuntimeError" in call_args
        assert "Test runtime error" in call_args
    
    @patch('utils.logging_utils.get_logger')
    def test_log_error_different_exception_types(self, mock_get_logger):
        """Test error logging with different exception types."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        exceptions = [
            ValueError("Value error"),
            TypeError("Type error"),
            IOError("IO error"),
            Exception("Generic exception")
        ]
        
        for error in exceptions:
            log_error(error, "test_context")
            
        assert mock_logger.error.call_count == len(exceptions)


class TestLogPerformance:
    """Test performance logging functionality."""
    
    @patch('utils.logging_utils.get_logger')
    def test_log_performance_basic(self, mock_get_logger):
        """Test basic performance logging."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        log_performance("test_operation", 1.5)
        
        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "test_operation" in call_args
        assert "1.50s" in call_args
    
    @patch('utils.logging_utils.get_logger')
    def test_log_performance_different_durations(self, mock_get_logger):
        """Test performance logging with different durations."""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        operations = [
            ("fast_operation", 0.1),
            ("medium_operation", 1.0),
            ("slow_operation", 10.5)
        ]
        
        for operation, duration in operations:
            log_performance(operation, duration)
        
        assert mock_logger.info.call_count == len(operations)
        
        # Check that all durations are formatted correctly
        calls = mock_logger.info.call_args_list
        assert "0.10s" in calls[0][0][0]
        assert "1.00s" in calls[1][0][0]
        assert "10.50s" in calls[2][0][0]


class TestLoggingUtilsIntegration:
    """Integration tests for logging utilities."""
    
    def test_full_logging_workflow(self):
        """Test full logging workflow integration."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            log_path = Path(tmp_dir) / "integration.log"
            
            # Setup logging
            logger = setup_logging(log_file=str(log_path), log_level="DEBUG")
            
            # Get specific logger
            module_logger = get_logger("test_module")
            
            # Test logging at different levels
            module_logger.debug("Debug message")
            module_logger.info("Info message")
            module_logger.warning("Warning message")
            module_logger.error("Error message")
            
            # Test utility functions
            log_function_call("test_function", ("arg1",), {"key": "value"})
            log_error(ValueError("Test error"), "test_context")
            log_performance("test_operation", 2.5)
            
            # Verify log file was created and contains content
            assert log_path.exists()
            content = log_path.read_text()
            assert len(content) > 0
    
    def test_logging_with_different_levels(self):
        """Test logging with different log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        for level in levels:
            logger = setup_logging(log_level=level)
            assert isinstance(logger, logging.Logger)
            assert logger.level == getattr(logging, level)
    
    def test_error_handling_in_logging(self):
        """Test that logging functions handle errors gracefully."""
        # Test with various error types
        errors = [
            ValueError("Value error"),
            TypeError("Type error"),
            Exception("Generic error")
        ]
        
        for error in errors:
            # Should not raise exceptions
            log_error(error, "test_context")
            log_function_call("test_func", (), {})
            log_performance("test_op", 1.0)
        
        assert True  # All functions completed without exceptions 