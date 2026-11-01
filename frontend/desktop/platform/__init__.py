"""
Windows Native Platform Integrations
====================================
Subpackage containing Win32 window management, DWM theming,
global hotkeys, system tray NotifyIcon, and Windows Explorer shell integration.
"""

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

__all__ = [
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
]
