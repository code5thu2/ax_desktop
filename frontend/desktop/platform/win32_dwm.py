"""
Windows 11 Desktop Window Manager (DWM) Theming
================================================
Immersive Dark Mode, custom caption background color, title text color,
and window border coloring via DwmSetWindowAttribute.
"""

import ctypes
from desktop.config import (
    DARK_TITLE_BG, DARK_TITLE_TEXT, DARK_TITLE_BORDER,
    LIGHT_TITLE_BG, LIGHT_TITLE_TEXT, LIGHT_TITLE_BORDER
)


def hex_to_colorref(hex_str: str) -> int:
    """Convert hex color (#RRGGBB) to Windows Win32 COLORREF format (0x00BBGGRR)."""
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16)
    g = int(hex_str[2:4], 16)
    b = int(hex_str[4:6], 16)
    return (b << 16) | (g << 8) | r


def apply_title_bar_theme(window, is_dark: bool = True, bg_hex: str = None, text_hex: str = None, border_hex: str = None):
    """
    Apply Windows 11 DWM Custom Title Bar styling to dynamically match app theme.
    - DWMWA_USE_IMMERSIVE_DARK_MODE (20, fallback 19)
    - DWMWA_CAPTION_COLOR (35) -> Sets exact title bar background color
    - DWMWA_TEXT_COLOR (36) -> Sets title bar text/controls color
    - DWMWA_BORDER_COLOR (34) -> Sets window border color
    """
    try:
        native = getattr(window, 'native', None)
        if not native or not hasattr(native, 'Handle'):
            return

        hwnd = int(native.Handle.ToInt64())
        dwmapi = ctypes.windll.dwmapi

        if is_dark:
            dark_val = ctypes.c_int(1)
            bg = bg_hex or DARK_TITLE_BG
            text = text_hex or DARK_TITLE_TEXT
            border = border_hex or DARK_TITLE_BORDER
        else:
            dark_val = ctypes.c_int(0)
            bg = bg_hex or LIGHT_TITLE_BG
            text = text_hex or LIGHT_TITLE_TEXT
            border = border_hex or LIGHT_TITLE_BORDER

        # 1. Toggle Immersive Dark Mode
        res = dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(dark_val), 4)
        if res != 0:
            dwmapi.DwmSetWindowAttribute(hwnd, 19, ctypes.byref(dark_val), 4)

        # 2. Set Exact Title Bar Background Color (DWMWA_CAPTION_COLOR = 35)
        caption_col = ctypes.c_int(hex_to_colorref(bg))
        dwmapi.DwmSetWindowAttribute(hwnd, 35, ctypes.byref(caption_col), 4)

        # 3. Set Title Bar Text Color (DWMWA_TEXT_COLOR = 36)
        text_col = ctypes.c_int(hex_to_colorref(text))
        dwmapi.DwmSetWindowAttribute(hwnd, 36, ctypes.byref(text_col), 4)

        # 4. Set Window Border Color (DWMWA_BORDER_COLOR = 34)
        border_col = ctypes.c_int(hex_to_colorref(border))
        dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(border_col), 4)

    except Exception:
        pass


def apply_dark_title_bar(window, bg_hex: str = "#090A0F", text_hex: str = "#F1F5F9", border_hex: str = "#1E2028"):
    """
    Convenience wrapper to enforce dark mode title bar styling on the specified PyWebView window.
    """
    apply_title_bar_theme(window, is_dark=True, bg_hex=bg_hex, text_hex=text_hex, border_hex=border_hex)
