"""
Plugin Manager JavaScript Bridge API
====================================
API exposed to the standalone MCP Protocol Studio window.
"""

from desktop.api.desktop_api import DesktopApi


class PluginManagerApi(DesktopApi):
    """API exposed to the standalone Plugin & MCP Manager window."""
    def __init__(self, coordinator=None, app_name: str = "MCP Protocol Studio"):
        super().__init__(coordinator=coordinator, app_name=app_name)
