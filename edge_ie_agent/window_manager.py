"""Window management and screenshot capture for Microsoft Edge."""
import time
from typing import Tuple, List, Optional
from PIL import Image, ImageGrab
import win32gui
import win32con

class WindowNotFoundError(Exception):
    """Raised when the specified target window is not found."""
    pass

def find_edge_window(title_keyword: str = "Edge") -> int:
    """Finds the first visible window whose title contains title_keyword.
    
    Returns:
        HWND (window handle integer).
        
    Raises:
        WindowNotFoundError: If no matching window is found.
    """
    matches: List[int] = []
    
    def enum_callback(hwnd: int, extra: list) -> bool:
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_keyword.lower() in title.lower():
                matches.append(hwnd)
        return True
        
    win32gui.EnumWindows(enum_callback, matches)
    
    if not matches:
        raise WindowNotFoundError(
            f"Không tìm thấy cửa sổ nào chứa từ khóa '{title_keyword}'. "
            "Vui lòng đảm bảo Microsoft Edge (IE Mode) đang được mở."
        )
    return matches[0]

def get_window_bounds(hwnd: int) -> Tuple[int, int, int, int]:
    """Gets the (left, top, width, height) of the given window."""
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = max(1, right - left)
    height = max(1, bottom - top)
    return (left, top, width, height)

def focus_window(hwnd: int) -> None:
    """Restores (if minimized) and brings the window to the foreground."""
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        time.sleep(0.3)
    try:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    except Exception:
        # Fallback in case of Windows focus lock
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

def capture_window(hwnd: int) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    """Focuses the window and captures its bounding area.
    
    Returns:
        Tuple of (PIL.Image, (left, top, width, height)).
    """
    focus_window(hwnd)
    bounds = get_window_bounds(hwnd)
    left, top, width, height = bounds
    
    bbox = (left, top, left + width, top + height)
    screenshot = ImageGrab.grab(bbox=bbox)
    return screenshot, bounds
