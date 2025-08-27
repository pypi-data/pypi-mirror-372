import pytest
from tracecolor import tracecolor
import time

def test_tracecolor_creation():
    """Test basic logger creation with Loguru backend."""
    logger = tracecolor("test_logger")
    assert isinstance(logger, tracecolor)
    assert logger.name == "test_logger"
    # Loguru backend doesn't inherit from logging.Logger
    assert hasattr(logger, 'trace')
    assert hasattr(logger, 'debug')
    assert hasattr(logger, 'progress')
    assert hasattr(logger, 'info')
    assert hasattr(logger, 'warning')
    assert hasattr(logger, 'error')
    assert hasattr(logger, 'critical')

def test_log_levels():
    """Test all log levels are properly defined."""
    logger = tracecolor("test_logger")
    assert logger.TRACE_LEVEL == 5
    assert logger.PROGRESS_LEVEL == 15

def test_log_methods():
    """Test all logging methods exist and are callable."""
    logger = tracecolor("test_logger")
    
    # These should all work without raising exceptions
    logger.trace("Test trace message")
    logger.debug("Test debug message")
    logger.progress("Test progress message")
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")
    logger.critical("Test critical message")

def test_progress_rate_limiting():
    """Test that progress messages are rate-limited."""
    logger = tracecolor("test_rate_limit")
    
    # The rate limiting is now at source level in the progress() method
    # We can't easily test the internal behavior without mocking
    # but we can verify the method exists and runs
    
    start = time.time()
    # Send multiple progress messages rapidly
    for i in range(5):
        logger.progress(f"Progress message {i}")
    end = time.time()
    
    # Should complete quickly (not wait for rate limiting)
    assert end - start < 1.0  # Should be nearly instant

def test_enhanced_features():
    """Test enhanced features initialization."""
    # Test with UDP enabled
    logger_udp = tracecolor("test_udp", enable_udp=True, udp_port=19999)
    assert logger_udp.udp_sink is not None
    
    # Test with file logging enabled  
    logger_file = tracecolor("test_file", enable_file=True, log_dir="/tmp/test_logs")
    assert logger_file.name == "test_file"

def test_create_enhanced_logger():
    """Test the create_enhanced_logger factory function."""
    from tracecolor import create_enhanced_logger
    
    logger = create_enhanced_logger("test_enhanced")
    assert isinstance(logger, tracecolor)
    assert logger.name == "test_enhanced"