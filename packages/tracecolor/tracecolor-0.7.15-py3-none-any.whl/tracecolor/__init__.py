"""
Tracecolor - Enhanced logging with TRACE/PROGRESS levels and UDP monitoring

Features:
- Custom TRACE (5) and PROGRESS (15) log levels
- Colorized console output with Loguru backend
- Rate-limited progress messages
- UDP remote monitoring
- File logging with rotation
- TOML/YAML/JSON configuration support with automatic detection

Usage:
    from tracecolor import tracecolor
    
    logger = tracecolor(__name__)
    logger.trace("Detailed trace")
    logger.progress("Progress update")
    logger.info("Information")
"""

from .tracecolor import tracecolor, create_enhanced_logger

__version__ = "0.7.15"
__author__ = "Marco Del Pin"
__all__ = ['tracecolor', 'create_enhanced_logger']

# Backward compatibility - existing code using tracecolor() continues to work
# Enhanced features now built into tracecolor class with Loguru backend
# create_enhanced_logger() is a convenience function for explicit enhanced features