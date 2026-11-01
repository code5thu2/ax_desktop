"""
MCP Protocol Studio - Desktop Configuration & Resource Resolution
=================================================================
Centralized configuration, geometry constants, AppUserModelID,
registry keys, and dynamic resource path resolution.
"""

import os
import sys
import tempfile

PLUGIN_APP_NAME = "MCP Protocol Studio"
PLUGIN_MUTEX_NAME = "Local\\MCP_PROTOCOL_STUDIO_SINGLE_INSTANCE_MUTEX"
PLUGIN_IPC_PORT_FILE = os.path.join(tempfile.gettempdir(), 'mcp_studio_ipc.port')
PLUGIN_APP_USER_MODEL_ID = 'com.mcp.protocol.studio.desktop.1.0'

REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_REG_NAME = "MCP Protocol Studio"

ERROR_ALREADY_EXISTS = 183

PLUGIN_WINDOW_WIDTH = 1240
PLUGIN_WINDOW_HEIGHT = 800
PLUGIN_MIN_WIDTH = 960
PLUGIN_MIN_HEIGHT = 600

PLUGIN_DARK_BG = "#1E1E1E"
PLUGIN_DARK_BORDER = "#2D3039"

DARK_TITLE_BG = "#090A0F"
DARK_TITLE_TEXT = "#F1F5F9"
DARK_TITLE_BORDER = "#1E2028"

LIGHT_TITLE_BG = "#F8FAFC"
LIGHT_TITLE_TEXT = "#0F172A"
LIGHT_TITLE_BORDER = "#CBD5E1"


def get_resource_path(filename: str) -> str:
    """
    Resolves the absolute path to a bundled or external resource file.
    Supports development mode, PyInstaller --onefile (_MEIPASS), and PyInstaller --onedir.
    """
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', None)
        if base_dir and os.path.exists(os.path.join(base_dir, filename)):
            return os.path.join(base_dir, filename)

        exe_dir = os.path.dirname(sys.executable)
        internal_path = os.path.join(exe_dir, '_internal', filename)
        if os.path.exists(internal_path):
            return internal_path

        return os.path.join(exe_dir, filename)
    else:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(package_dir)
        root_candidate = os.path.join(project_root, filename)
        if os.path.exists(root_candidate):
            return root_candidate
        return os.path.join(package_dir, filename)


def get_dist_dir() -> str:
    """
    Resolves absolute path to the compiled Vue 3 distribution folder (dist).
    """
    return get_resource_path('dist')


def get_icon_path(is_plugin_mode: bool = True) -> str:
    """
    Finds the highest quality available application icon file (.ico) for taskbar and tray.
    """
    for candidate in ['app_skill_mcp_isocube.ico', 'app_skill_mcp.ico', 'app.ico']:
        p = get_resource_path(candidate)
        if os.path.isfile(p):
            return p

    dist_ico = os.path.join(get_dist_dir(), 'favicon.ico')
    if os.path.isfile(dist_ico):
        return dist_ico

    return get_resource_path('app.ico')
