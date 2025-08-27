#!/usr/bin/env python3
"""
Cross-platform launcher for tracecolor UDP monitor
Works on both Windows and Linux/Mac
Usage: python run_monitor.py [port] [host]
"""
import sys
import os
import subprocess

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))
monitor_path = os.path.join(script_dir, 'monitor.py')

# Build command
cmd = [sys.executable, monitor_path]

# Add arguments if provided
if len(sys.argv) > 1:
    if sys.argv[1] in ['-h', '--help']:
        cmd.extend(['--help'])
    else:
        cmd.extend(['--port', sys.argv[1]])
        if len(sys.argv) > 2:
            cmd.extend(['--host', sys.argv[2]])

# Run monitor
try:
    subprocess.run(cmd)
except KeyboardInterrupt:
    print("\nMonitor stopped.")