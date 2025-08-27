#!/usr/bin/env python3
"""
Test script for tracecolor UDP logging functionality.

Run this script in one terminal, and run the monitor in another:
    Terminal 1: python monitor.py
    Terminal 2: python test_udp.py
"""

import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tracecolor import tracecolor, create_enhanced_logger


def test_basic_udp():
    """Test basic UDP logging functionality"""
    print("Testing basic UDP logging...")
    
    # Create logger with UDP enabled
    logger = tracecolor(
        __name__,
        enable_console=True,
        enable_udp=True,
        udp_host="127.0.0.1",
        udp_port=9999,
        log_level="TRACE"
    )
    
    # Test all log levels
    logger.trace("This is a TRACE message")
    time.sleep(0.1)
    
    logger.debug("This is a DEBUG message")
    time.sleep(0.1)
    
    logger.progress("This is a PROGRESS message")
    time.sleep(0.1)
    
    logger.info("This is an INFO message")
    time.sleep(0.1)
    
    logger.warning("This is a WARNING message")
    time.sleep(0.1)
    
    logger.error("This is an ERROR message")
    time.sleep(0.1)
    
    logger.critical("This is a CRITICAL message")
    time.sleep(0.1)
    
    print("Basic UDP logging test complete!")


def test_progress_rate_limiting():
    """Test progress rate limiting with UDP"""
    print("\nTesting progress rate limiting...")
    
    logger = create_enhanced_logger(
        "rate_test",
        enable_udp=True,
        udp_host="127.0.0.1",
        udp_port=9999
    )
    
    # This should only send one message per second
    for i in range(10):
        logger.progress(f"Progress update {i}")
        time.sleep(0.1)  # 100ms between attempts
    
    print("Rate limiting test complete!")


def test_multiple_loggers():
    """Test multiple loggers with UDP"""
    print("\nTesting multiple loggers...")
    
    logger1 = tracecolor(
        "app.module1",
        enable_udp=True,
        udp_host="127.0.0.1",
        udp_port=9999
    )
    
    logger2 = tracecolor(
        "app.module2",
        enable_udp=True,
        udp_host="127.0.0.1",
        udp_port=9999
    )
    
    logger1.info("Message from module1")
    logger2.info("Message from module2")
    logger1.error("Error from module1")
    logger2.warning("Warning from module2")
    
    print("Multiple loggers test complete!")


def test_long_messages():
    """Test long messages over UDP"""
    print("\nTesting long messages...")
    
    logger = tracecolor(
        "long_msg_test",
        enable_udp=True,
        udp_host="127.0.0.1",
        udp_port=9999
    )
    
    long_message = "This is a very long message that contains " * 20
    logger.info(long_message)
    
    print("Long message test complete!")


def main():
    """Run all UDP logging tests"""
    print("=" * 60)
    print("TRACECOLOR UDP LOGGING TEST SUITE")
    print("=" * 60)
    print("\nMake sure the monitor is running in another terminal:")
    print("  python monitor.py")
    print("\nStarting tests in 3 seconds...")
    time.sleep(3)
    
    try:
        test_basic_udp()
        test_progress_rate_limiting()
        test_multiple_loggers()
        test_long_messages()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETE!")
        print("Check the monitor terminal for UDP messages")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())