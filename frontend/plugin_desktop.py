"""
MCP Protocol Studio Desktop Launcher
====================================
Launches the desktop application shell for MCP Protocol Studio.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desktop.apps.plugin_manager_app import run_plugin_manager

if __name__ == '__main__':
    run_plugin_manager()
