#!/usr/bin/env python3
"""
Tracecolor UDP Monitor - Real-time log monitoring over UDP

This module provides a UDP log monitor for real-time viewing of logs
from tracecolor-enhanced applications with UDP logging enabled.

Usage:
    # As module
    python -m tracecolor.monitor
    python -m tracecolor.monitor --host 0.0.0.0 --port 8888
    
    # Direct execution
    python monitor.py
    python monitor.py listen 192.168.1.100 9999
"""

import socket
import json
import argparse
import sys
from typing import Dict


def udp_monitor(host: str = "127.0.0.1", port: int = 9999):
    """
    UDP log monitor with tracecolor-style output
    
    Args:
        host: Host to bind to (default: "127.0.0.1")
        port: Port to bind to (default: 9999)
    """
    print(f"Tracecolor UDP Monitor v0.7.0")
    print(f"Listening on {host}:{port}")
    print("Press Ctrl+C to stop\n")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
    except OSError as e:
        print(f"ERROR: Cannot bind to {host}:{port} - {e}")
        print("Try a different port or check if another process is using this port")
        return
    
    # Level color mapping (same as tracecolor)
    level_colors = {
        'T': '\033[1;30m',     # TRACE - Gray (dim)
        'D': '\033[36m',       # DEBUG - Cyan  
        'P': '\033[34m',       # PROGRESS - Blue
        'I': '\033[32m',       # INFO - Green
        'S': '\033[32m',       # SUCCESS - Green (Loguru level)
        'W': '\033[33m',       # WARNING - Yellow
        'E': '\033[31m',       # ERROR - Red
        'C': '\033[1;31m',     # CRITICAL - Bright Red
    }
    reset = '\033[0m'
    
    message_count = 0
    
    try:
        print("=" * 80)
        
        while True:
            try:
                data, addr = sock.recvfrom(4096)
                message_count += 1
                
                try:
                    msg = data.decode('utf-8')
                    
                    # Try to parse the tracecolor plain text format:
                    # {level[0]} |{time}| [{name}:{function}:{line}] {message}
                    # Example: I |2024-01-15 10:23:45.123| [myapp:main:42] Starting application
                    
                    # The message might be in plain text format from tracecolor
                    if msg and len(msg) > 0:
                        # Get the level character (first character)
                        level_char = msg[0] if msg else '?'
                        
                        # Apply color based on level character
                        color = level_colors.get(level_char, '')
                        
                        # Color only the first character, leave the rest as-is
                        if len(msg) > 1:
                            # Print colored first character + rest of message
                            print(f"{color}{msg[0]}{reset}{msg[1:]}", end='')
                        else:
                            # Just the single character
                            print(f"{color}{msg}{reset}", end='')
                        
                        # If the message doesn't end with newline, add one
                        if not msg.endswith('\n'):
                            print()
                    
                except UnicodeDecodeError:
                    print(f"[{message_count:04d}] Invalid UTF-8 from {addr}: {data[:50]}...")
                except Exception as e:
                    print(f"[{message_count:04d}] Error processing message from {addr}: {e}")
                    
            except socket.timeout:
                continue
            except ConnectionResetError:
                # Windows specific - ignore
                continue
                
    except KeyboardInterrupt:
        print(f"\n\nReceived {message_count} messages")
        print("UDP Monitor stopped")
    except Exception as e:
        print(f"Monitor error: {e}")
    finally:
        sock.close()


def main():
    """Main entry point for the UDP monitor"""
    parser = argparse.ArgumentParser(
        description="Tracecolor UDP Monitor - Real-time log monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m tracecolor.monitor                    # Monitor localhost:9999
  python -m tracecolor.monitor --port 8888        # Monitor localhost:8888  
  python -m tracecolor.monitor --host 0.0.0.0     # Monitor all interfaces:9999
  python -m tracecolor.monitor --host 192.168.1.100 --port 7777  # Remote monitoring
        """
    )
    
    parser.add_argument(
        '--host', 
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=9999,
        help='Port to bind to (default: 9999)'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Tracecolor Monitor v0.7.0'
    )
    
    # Handle legacy command line format for backward compatibility
    if len(sys.argv) > 1 and sys.argv[1] == "listen":
        # Legacy format: python monitor.py listen [host] [port]
        host = sys.argv[2] if len(sys.argv) > 2 else "127.0.0.1"
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 9999
        udp_monitor(host, port)
    else:
        # Standard argparse format
        args = parser.parse_args()
        udp_monitor(args.host, args.port)


if __name__ == "__main__":
    main()