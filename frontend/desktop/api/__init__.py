"""
JavaScript - Python Bridge APIs
===============================
Exposed APIs for Splash, Main Studio, Spotlight AI, and Plugin Manager windows.
"""

from desktop.api.splash_api import SplashApi
from desktop.api.desktop_api import DesktopApi
from desktop.api.spotlight_api import SpotlightApi
from desktop.api.plugin_manager_api import PluginManagerApi

__all__ = [
    'SplashApi',
    'DesktopApi',
    'SpotlightApi',
    'PluginManagerApi',
]
