"""
Multi-Monitor & Screen Geometry Calculations
=============================================
Calculates exact screen centering and Spotlight placement coordinates
across primary and multi-monitor setups.
"""

import ctypes
import webview
from desktop.config import SPOTLIGHT_WIDTH, SPOTLIGHT_COLLAPSED_HEIGHT


def get_screen_center(width: int, height: int) -> tuple:
    """
    Compute exact (x, y) coordinates to center a window of (width, height)
    on the user's primary monitor.

    Args:
        width (int): Window width in pixels.
        height (int): Window height in pixels.

    Returns:
        tuple[int, int, object]: (x, y, primary_screen_object)
    """
    primary = None
    try:
        for s in webview.screens:
            if s.x == 0 and s.y == 0:
                primary = s
                break
        if not primary and len(webview.screens) > 0:
            primary = webview.screens[0]
    except Exception:
        primary = None

    if primary:
        x = int(primary.x + (primary.width - width) // 2)
        y = int(primary.y + (primary.height - height) // 2)
        return x, y, primary

    # Fallback using Win32 GetSystemMetrics
    try:
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        return int((sw - width) // 2), int((sh - height) // 2), None
    except Exception:
        return 100, 100, None


def get_spotlight_position(width: int = SPOTLIGHT_WIDTH, height: int = SPOTLIGHT_COLLAPSED_HEIGHT) -> tuple:
    """
    Compute coordinates for Spotlight window:
    Horizontally centered, and Y at ~18% from screen top of the primary monitor.

    Args:
        width (int): Spotlight window width.
        height (int): Spotlight window height.

    Returns:
        tuple[int, int, object]: (x, y, primary_screen_object)
    """
    primary = None
    try:
        for s in webview.screens:
            if s.x == 0 and s.y == 0:
                primary = s
                break
        if not primary and len(webview.screens) > 0:
            primary = webview.screens[0]
    except Exception:
        primary = None

    if primary:
        x = int(primary.x + (primary.width - width) // 2)
        y = int(primary.y + int(primary.height * 0.18))
        return x, y, primary

    try:
        user32 = ctypes.windll.user32
        sw = user32.GetSystemMetrics(0)
        sh = user32.GetSystemMetrics(1)
        return int((sw - width) // 2), int(sh * 0.18), None
    except Exception:
        return 100, 100, None
