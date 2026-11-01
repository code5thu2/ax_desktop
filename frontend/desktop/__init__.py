"""
MCP Protocol Studio Desktop Application Package
===============================================
Enterprise-grade modular desktop framework for MCP Protocol Studio.
Exports all platform, core, api, and application runners for convenient top-level access.
"""

from desktop.config import (
    PLUGIN_APP_NAME,
    PLUGIN_MUTEX_NAME,
    PLUGIN_IPC_PORT_FILE,
    PLUGIN_APP_USER_MODEL_ID,
    get_resource_path,
    get_dist_dir,
    get_icon_path,
)
from desktop.server import (
    SPAHTTPRequestHandler,
    ThreadedTCPServer,
    start_local_server,
)
from desktop.platform.win32_window import (
    ensure_default_desktop,
    check_single_instance,
    start_ipc_server,
    _steal_foreground,
)
from desktop.platform.win32_dwm import (
    hex_to_colorref,
    apply_title_bar_theme,
    apply_dark_title_bar,
)
from desktop.platform.win32_tray import (
    SystemTrayManager,
    is_autostart_enabled,
    set_autostart,
)
from desktop.platform.win32_hotkey import GlobalHotkeyListener
from desktop.platform.win32_explorer import (
    get_selected_explorer_files,
    get_selected_text_snippet,
    read_local_file_content,
    get_clipboard_text,
    set_clipboard_text,
)
from desktop.core.screens import (
    get_screen_center,
    get_spotlight_position,
)
from desktop.core.coordinator import AppCoordinator
from desktop.api.splash_api import SplashApi
from desktop.api.desktop_api import DesktopApi
from desktop.api.plugin_manager_api import PluginManagerApi
from desktop.apps.plugin_manager_app import run_plugin_manager

__all__ = [
    'STUDIO_APP_NAME',
    'STUDIO_MUTEX_NAME',
    'STUDIO_IPC_PORT_FILE',
    'STUDIO_APP_USER_MODEL_ID',
    'PLUGIN_APP_NAME',
    'PLUGIN_MUTEX_NAME',
    'PLUGIN_IPC_PORT_FILE',
    'PLUGIN_APP_USER_MODEL_ID',
    'SPOTLIGHT_WIDTH',
    'SPOTLIGHT_COLLAPSED_HEIGHT',
    'SPOTLIGHT_MAX_HEIGHT',
    'get_resource_path',
    'get_dist_dir',
    'get_icon_path',
    'SPAHTTPRequestHandler',
    'ThreadedTCPServer',
    'start_local_server',
    'ensure_default_desktop',
    'check_single_instance',
    'start_ipc_server',
    '_steal_foreground',
    'hex_to_colorref',
    'apply_title_bar_theme',
    'apply_dark_title_bar',
    'SystemTrayManager',
    'is_autostart_enabled',
    'set_autostart',
    'GlobalHotkeyListener',
    'get_selected_explorer_files',
    'get_selected_text_snippet',
    'read_local_file_content',
    'get_clipboard_text',
    'set_clipboard_text',
    'get_screen_center',
    'get_spotlight_position',
    'AppCoordinator',
    'SplashApi',
    'DesktopApi',
    'SpotlightApi',
    'PluginManagerApi',
    'run_studio',
    'run_plugin_manager',
]
