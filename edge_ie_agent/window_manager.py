"""Window management, screenshot capture, and visual stabilization for Microsoft Edge."""
import time
from typing import Tuple, List, Optional
from PIL import Image, ImageGrab, ImageChops
import win32gui
import win32con

class WindowNotFoundError(Exception):
    """Raised when the specified target window is not found."""
    pass

def find_edge_window(title_keyword: str = "Edge") -> int:
    """Finds the first visible window whose title contains title_keyword."""
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
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

def capture_window(hwnd: int) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
    """Focuses the window and captures its bounding area."""
    focus_window(hwnd)
    bounds = get_window_bounds(hwnd)
    left, top, width, height = bounds
    
    bbox = (left, top, left + width, top + height)
    screenshot = ImageGrab.grab(bbox=bbox)
    return screenshot, bounds

def calculate_image_diff_ratio(img1: Image.Image, img2: Image.Image) -> float:
    """Calculates the ratio of differing pixels between two images (0.0 to 1.0)."""
    if img1.size != img2.size or img1.mode != img2.mode:
        return 1.0
    diff = ImageChops.difference(img1, img2)
    bbox = diff.getbbox()
    if not bbox:
        return 0.0
    gray_diff = diff.convert("L")
    hist = gray_diff.histogram()
    total_pixels = img1.size[0] * img1.size[1]
    differing_pixels = total_pixels - hist[0]
    return differing_pixels / float(total_pixels)

def wait_until_stable(
    hwnd: int,
    timeout: float = 6.0,
    check_interval: float = 0.4,
    diff_threshold: float = 0.005
) -> bool:
    """Monitors the window and waits until visual changes stop (page finish loading).
    
    Returns:
        True if the page stabilized before timeout, False if it timed out.
    """
    start_time = time.time()
    try:
        prev_img, _ = capture_window(hwnd)
    except Exception:
        return False

    time.sleep(check_interval)

    while (time.time() - start_time) < timeout:
        try:
            curr_img, _ = capture_window(hwnd)
            ratio = calculate_image_diff_ratio(prev_img, curr_img)
            # If difference is negligible, page has settled
            if ratio <= diff_threshold:
                return True
            prev_img = curr_img
        except Exception:
            break
        time.sleep(check_interval)

    return False
