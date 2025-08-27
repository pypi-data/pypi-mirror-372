import time
import inspect
import socket
import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, Union
from collections import defaultdict
from loguru import logger as _loguru_logger

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ProgressRateLimiter:
    """Rate limiter for PROGRESS messages - 1 per second per call site"""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.last_times: Dict[str, float] = defaultdict(float)
    
    def should_log(self, call_site: str) -> bool:
        """Check if enough time has passed since last log from this call site"""
        current_time = time.time()
        last_time = self.last_times[call_site]
        
        if current_time - last_time >= self.interval:
            self.last_times[call_site] = current_time
            return True
        return False


class UDPSink:
    """Custom UDP sink for remote monitoring"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 9999):
        self.host = host
        self.port = port
        self.sock = None
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Set socket to non-blocking to prevent hangs
            self.sock.setblocking(False)
        except Exception:
            pass  # Silent fail
    
    def write(self, message):
        """Send log message via UDP"""
        if not self.sock:
            return
            
        try:
            # Loguru passes formatted strings to the write method
            if isinstance(message, str):
                # Remove trailing newline if present
                msg = message.rstrip('\n')
                # Encode with error handling for special characters
                # 'replace' will substitute problematic characters with ?
                data = msg.encode('utf-8', errors='replace')
                self.sock.sendto(data, (self.host, self.port))
        except (socket.error, BlockingIOError):
            # Ignore network errors silently to not disrupt logging
            pass
        except Exception:
            # Ignore any other errors silently
            pass
    
    def close(self):
        """Close the UDP socket"""
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


# TracecolorEnhanced class removed - now tracecolor is the Loguru wrapper


class tracecolor:
    """
    Enhanced logger with colorized output and TRACE/PROGRESS levels.
    Powered by Loguru backend for superior performance and features.
    
    Features:
    - Custom TRACE logging level (5, lower than DEBUG)
    - Custom PROGRESS logging level (15, between DEBUG and INFO)
    - Colorized output for different log levels
    - Rate-limiting for PROGRESS messages (once per second per call site)
    - UDP remote monitoring support
    - File logging with rotation and compression
    - External configuration support (JSON/YAML)
    
    Usage:
    ```python
    from tracecolor import tracecolor
    
    logger = tracecolor(__name__)
    logger.trace("Detailed trace message")
    logger.debug("Debug information")
    logger.progress("Progress update (rate-limited)")
    logger.info("General information")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error")
    ```
    """
    TRACE_LEVEL = 5  # TRACE below DEBUG (10)
    PROGRESS_LEVEL = 15  # PROGRESS between DEBUG (10) and INFO (20)
    PROGRESS_INTERVAL: float = 1  # Default interval in seconds for progress messages (0 or less disables rate-limiting for testing)

    def __init__(self, 
                 name: str,
                 enable_console: bool = True,
                 enable_file: bool = False,
                 enable_udp: bool = False,
                 log_dir: Optional[Union[str, Path]] = None,
                 udp_host: str = "127.0.0.1",
                 udp_port: int = 9999,
                 log_level: str = "TRACE",
                 config_file: Optional[str] = None):
        
        self.name = name
        self.progress_limiter = ProgressRateLimiter()
        self.udp_sink = None
        self._logger_id = id(self)  # Unique ID for this logger instance
        
        # Initialize Loguru backend (always available now)
        self._init_loguru_backend(enable_console, enable_file, enable_udp, 
                                log_dir, udp_host, udp_port, log_level, config_file)
    
    def _init_loguru_backend(self, enable_console, enable_file, enable_udp, 
                           log_dir, udp_host, udp_port, log_level, config_file):
        """Initialize with Loguru backend (preferred)"""
        # Auto-detect config file if not provided
        if not config_file:
            config_file = self._find_config_file()
        
        # Load external configuration if found or provided
        if config_file:
            config = self._load_config(config_file)
            enable_console = config.get("enable_console", enable_console)
            enable_file = config.get("enable_file", enable_file)
            enable_udp = config.get("use_udp", config.get("enable_udp", enable_udp))
            log_dir = config.get("log_dir", log_dir)
            udp_host = config.get("udp_host", udp_host)
            udp_port = config.get("udp_port", udp_port)
            log_level = config.get("log_level", log_level)
        
        # Create a new logger instance to avoid conflicts
        self.logger = _loguru_logger.bind(name=self.name, logger_id=self._logger_id)
        
        # Remove default loguru handler for this instance
        _loguru_logger.remove()
        
        # Add custom PROGRESS level to match tracecolor exactly
        try:
            _loguru_logger.level("PROGRESS", no=15, color="<blue>")
        except (TypeError, ValueError):
            pass  # Level already exists
        
        # Console handler with tracecolor format (backward compatible)
        if enable_console:
            console_format = (
                "<dim>{level.name[0]}</dim> "  # Single char prefix
                "|<dim>{time:YYYY-MM-DD HH:mm:ss.SSS}</dim>| "  # Timestamp with milliseconds
                "<level>{message}</level>"  # Colored message
            )
            
            _loguru_logger.add(
                sink=sys.stderr,
                format=console_format,
                level=log_level,
                colorize=True,
                filter=self._console_filter
            )
        
        # File handler (enhanced feature)
        if enable_file and log_dir:
            log_path = Path(log_dir)
            log_path.mkdir(exist_ok=True, parents=True)
            
            file_format = (
                "{level.name[0]} |{time:YYYY-MM-DD HH:mm:ss.SSS}| "
                "[{name}:{function}:{line}] {message}"
            )
            
            _loguru_logger.add(
                sink=str(log_path / f"{self.name}.log"),
                format=file_format,
                level=log_level,
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                filter=lambda record: record["extra"].get("logger_id") == self._logger_id
            )
        
        # UDP handler for remote monitoring (enhanced feature)  
        if enable_udp:
            try:
                self.udp_sink = UDPSink(udp_host, udp_port)
                
                # UDP format matches tracecolor console format
                udp_format = (
                    "{level.name[0]} "  # Single char prefix
                    "|{time:YYYY-MM-DD HH:mm:ss.SSS}| "  # Timestamp with milliseconds
                    "[{extra[name]}:{function}:{line}] "  # Logger name and location
                    "{message}"  # Message
                )
                
                _loguru_logger.add(
                    sink=self.udp_sink,
                    level=log_level,
                    format=udp_format,
                    filter=lambda record: record["extra"].get("logger_id") == self._logger_id
                )
            except Exception:
                # Silently fail if UDP setup fails - don't disrupt logging
                pass
        
        # Bind the logger to this instance with unique ID
        self.logger = _loguru_logger.bind(name=self.name, logger_id=self._logger_id)
    
    def _find_config_file(self) -> Optional[str]:
        """Auto-detect standard config files in current directory"""
        # Standard config file names in order of preference
        standard_names = [
            ".tracecolor",      # Hidden TOML config (first priority)
            "tracecolor.toml",  # TOML config
            "tracecolor.yml",   # YAML config
            "tracecolor.yaml",  # YAML alternate
            "tracecolor.json"   # JSON config
        ]
        
        for name in standard_names:
            if Path(name).exists():
                return name
        
        return None
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from TOML, YAML or JSON file with auto-detection"""
        config_path = Path(config_file)
        if not config_path.exists():
            return {}
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Auto-detect format for .tracecolor file
                if config_file == '.tracecolor':
                    return self._auto_detect_and_parse(content)
                    
                # Use file extension for other files
                elif config_file.endswith('.toml'):
                    return self._parse_toml(content)
                elif config_file.endswith(('.yaml', '.yml')):
                    return self._parse_yaml(content)
                else:
                    return self._parse_json(content)
        except Exception:
            return {}
    
    def _auto_detect_and_parse(self, content: str) -> Dict[str, Any]:
        """Auto-detect format and parse configuration"""
        content_stripped = content.strip()
        
        # Try JSON first (starts with { or [)
        if content_stripped.startswith(('{', '[')):
            try:
                return self._parse_json(content)
            except:
                pass
        
        # Try YAML (contains : but not in TOML section format)
        if ':' in content and not content_stripped.startswith('['):
            try:
                return self._parse_yaml(content)
            except:
                pass
        
        # Try TOML (contains [section] or key = value)
        if '[' in content or '=' in content:
            try:
                return self._parse_toml(content)
            except:
                pass
        
        # Default to TOML for .tracecolor
        return self._parse_toml(content)
    
    def _parse_toml(self, content: str) -> Dict[str, Any]:
        """Parse TOML configuration"""
        try:
            import tomllib  # Python 3.11+
        except ImportError:
            try:
                import tomli as tomllib  # Fallback for older Python
            except ImportError:
                # Parse simple TOML manually as fallback
                return self._parse_simple_toml(content)
        
        config_data = tomllib.loads(content)
        return self._toml_to_flat_config(config_data)
    
    def _parse_yaml(self, content: str) -> Dict[str, Any]:
        """Parse YAML configuration"""
        if not YAML_AVAILABLE:
            raise ImportError("PyYAML required for YAML config files")
        config_data = yaml.safe_load(content)
        # Support both flat config and nested 'logging' wrapper
        return config_data.get('logging', config_data) if isinstance(config_data, dict) else {}
    
    def _parse_json(self, content: str) -> Dict[str, Any]:
        """Parse JSON configuration"""
        config_data = json.loads(content)
        # Support both flat config and nested 'logging' wrapper
        return config_data.get('logging', config_data) if isinstance(config_data, dict) else {}
    
    def _toml_to_flat_config(self, toml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert TOML structure to flat config format"""
        config = {}
        
        # Map TOML sections to flat config
        if 'udp' in toml_data:
            config['use_udp'] = toml_data['udp'].get('enabled', False)
            config['udp_host'] = toml_data['udp'].get('host', '127.0.0.1')
            config['udp_port'] = toml_data['udp'].get('port', 9999)
        
        if 'console' in toml_data:
            config['enable_console'] = toml_data['console'].get('enabled', True)
            if 'level' in toml_data['console']:
                config['log_level'] = toml_data['console']['level']
        
        if 'file' in toml_data:
            config['enable_file'] = toml_data['file'].get('enabled', False)
            if 'dir' in toml_data['file']:
                config['log_dir'] = toml_data['file']['dir']
        
        # Also support top-level log_level
        if 'log_level' in toml_data:
            config['log_level'] = toml_data['log_level']
            
        return config
    
    def _parse_simple_toml(self, content: str) -> Dict[str, Any]:
        """Simple TOML parser for basic config (fallback when tomllib not available)"""
        config = {}
        current_section = None
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # Section header
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                continue
            
            # Key-value pair
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Parse value type
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.isdigit():
                    value = int(value)
                elif value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                
                # Store in appropriate section
                if current_section:
                    if current_section == 'udp':
                        if key == 'enabled':
                            config['use_udp'] = value
                        elif key == 'host':
                            config['udp_host'] = value
                        elif key == 'port':
                            config['udp_port'] = value
                    elif current_section == 'console':
                        if key == 'enabled':
                            config['enable_console'] = value
                        elif key == 'level':
                            config['log_level'] = value
                    elif current_section == 'file':
                        if key == 'enabled':
                            config['enable_file'] = value
                        elif key == 'dir':
                            config['log_dir'] = value
        
        return config
    
    def _console_filter(self, record):
        """Filter for console output (Loguru backend)"""
        # Only process records from this logger instance
        if record["extra"].get("logger_id") != self._logger_id:
            return False
        
        # Rate limiting is now handled at source in progress() method
        return True  # Allow all messages from this logger instance

    def trace(self, message, *args, **kwargs):
        """Log a message with severity 'TRACE'."""
        self.logger.trace(message, *args, **kwargs)

    def progress(self, message, *args, **kwargs):
        """Log a message with severity 'PROGRESS' (for progress updates, rate-limited per call site)."""
        # Apply rate limiting at source, before sending to any sink
        frame = inspect.currentframe().f_back
        call_site = f"{frame.f_code.co_filename}:{frame.f_code.co_name}:{frame.f_lineno}"
        
        if not self.progress_limiter.should_log(call_site):
            return  # Skip this message entirely
        
        # If allowed, send to all sinks
        self.logger.log("PROGRESS", message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        """Log a message with severity 'DEBUG'."""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        """Log a message with severity 'INFO'."""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        """Log a message with severity 'WARNING'."""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        """Log a message with severity 'ERROR'."""
        self.logger.error(message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        """Log a message with severity 'CRITICAL'."""
        self.logger.critical(message, *args, **kwargs)
    
    def exception(self, message, *args, **kwargs):
        """Log exception with traceback"""
        self.logger.exception(message, *args, **kwargs)

# Factory functions for enhanced features

def create_enhanced_logger(name: str, 
                          enable_console: bool = True,
                          enable_file: bool = False,
                          enable_udp: bool = False,
                          log_dir: Optional[Union[str, Path]] = None,
                          udp_host: str = "127.0.0.1", 
                          udp_port: int = 9999,
                          log_level: str = "TRACE",
                          config_file: Optional[str] = None) -> 'tracecolor':
    """
    Create enhanced tracecolor logger with additional features enabled
    
    This is a convenience function that enables enhanced features by default.
    The main tracecolor class supports all these features natively.
    
    Usage:
        # Basic enhanced usage (Loguru backend + enhanced features)
        logger = create_enhanced_logger(__name__)
        
        # With UDP monitoring and file logging
        logger = create_enhanced_logger(__name__, enable_udp=True, enable_file=True, log_dir="logs")
        
        # With external configuration
        logger = create_enhanced_logger(__name__, config_file="logging.json")
    
    Args:
        name: Logger name (typically __name__)
        enable_console: Enable console output (default: True)
        enable_file: Enable file logging (default: False)
        enable_udp: Enable UDP remote monitoring (default: False)
        log_dir: Directory for log files
        udp_host: UDP host for remote monitoring
        udp_port: UDP port for remote monitoring
        log_level: Minimum log level (default: "TRACE")
        config_file: External configuration file (JSON/YAML)
        
    Returns:
        tracecolor instance with enhanced features enabled
    """
    return tracecolor(
        name=name,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_udp=enable_udp,
        log_dir=log_dir,
        udp_host=udp_host,
        udp_port=udp_port,
        log_level=log_level,
        config_file=config_file
    )

