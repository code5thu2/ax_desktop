"""
Main Application JavaScript Bridge API
=======================================
API exposed to the primary application window (window.pywebview.api).
Provides file reading, readiness handshake, dynamic DWM theming, and app metadata.
"""

from desktop.platform.win32_explorer import read_local_file_content
from desktop.platform.win32_dwm import apply_title_bar_theme


class DesktopApi:
    """API exposed to the main application window (src/main.ts)"""
    def __init__(self, coordinator, app_name: str = "MCP Protocol Studio"):
        # Attributes MUST have leading underscore to prevent pywebview reflection recursion
        self._coordinator = coordinator
        self._app_name = app_name

    def read_file_content(self, path: str) -> str:
        """
        Reads local file content into text for AI analysis.
        Supports plain text, docx, and standard text formats.
        """
        return read_local_file_content(path)

    def notify_main_ready(self):
        """
        Invoked from JavaScript once Vue, Pinia, and Vue Router are mounted and rendered.
        """
        if self._coordinator:
            self._coordinator.notify_main_ready()

    def set_theme(self, is_dark: bool) -> bool:
        """
        Dynamically synchronizes Windows 11 DWM title bar and native frame colors with app theme.

        Args:
            is_dark (bool): True for dark mode styling, False for light mode.

        Returns:
            bool: True on success.
        """
        if self._coordinator:
            self._coordinator.is_dark = bool(is_dark)
            if self._coordinator._main_window:
                apply_title_bar_theme(self._coordinator._main_window, is_dark=bool(is_dark))
        return True

    def get_app_info(self) -> dict:
        """
        Retrieves desktop application metadata and execution environment details.

        Returns:
            dict: Application metadata dictionary.
        """
        return {
            'name': self._app_name,
            'version': '1.0.0',
            'platform': 'Windows Native Desktop',
        }

    def is_autostart_enabled(self) -> bool:
        """Checks if Windows startup registry entry exists."""
        try:
            from desktop.platform.win32_tray import is_autostart_enabled
            from desktop.config import APP_REG_NAME
            return is_autostart_enabled(self._app_name or APP_REG_NAME)
        except Exception as e:
            print("[Desktop API] is_autostart_enabled error:", e)
            return False

    def set_autostart(self, enable: bool) -> bool:
        """Enables or disables Windows logon autostart entry in registry."""
        try:
            from desktop.platform.win32_tray import set_autostart
            from desktop.config import APP_REG_NAME
            return set_autostart(bool(enable), app_name=self._app_name or APP_REG_NAME)
        except Exception as e:
            print("[Desktop API] set_autostart error:", e)
            return False
