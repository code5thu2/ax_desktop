"""
Core Application Infrastructure
===============================
Provides application lifecycle coordination, transition handlers,
and multi-monitor screen geometry logic.
"""

from desktop.core.screens import get_screen_center, get_spotlight_position
from desktop.core.coordinator import AppCoordinator

__all__ = [
    'get_screen_center',
    'get_spotlight_position',
    'AppCoordinator',
]
