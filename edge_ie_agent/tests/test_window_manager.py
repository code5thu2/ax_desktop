from unittest.mock import patch, MagicMock
import pytest
from PIL import Image
from edge_ie_agent.window_manager import (
    get_window_bounds,
    find_edge_window,
    WindowNotFoundError,
    calculate_image_diff_ratio,
    wait_until_stable
)

def test_get_window_bounds():
    with patch("win32gui.GetWindowRect") as mock_rect:
        mock_rect.return_value = (50, 50, 850, 650)
        bounds = get_window_bounds(12345)
        assert bounds == (50, 50, 800, 600)  # left, top, width, height

def test_find_edge_window_not_found():
    with patch("win32gui.EnumWindows") as mock_enum:
        mock_enum.side_effect = lambda callback, extra: None
        with pytest.raises(WindowNotFoundError):
            find_edge_window("NonExistentKeywordXYZ")

def test_find_edge_window_found():
    def fake_enum(callback, extra):
        callback(101, extra)
        
    with patch("win32gui.EnumWindows", side_effect=fake_enum), \
         patch("win32gui.IsWindowVisible", return_value=True), \
         patch("win32gui.GetWindowText", return_value="Microsoft Edge - Trang chủ"):
        hwnd = find_edge_window("Edge")
        assert hwnd == 101

def test_calculate_image_diff_ratio_identical():
    img1 = Image.new("RGB", (100, 100), color="white")
    img2 = Image.new("RGB", (100, 100), color="white")
    assert calculate_image_diff_ratio(img1, img2) == 0.0

def test_calculate_image_diff_ratio_different():
    img1 = Image.new("RGB", (100, 100), color="white")
    img2 = Image.new("RGB", (100, 100), color="black")
    diff = calculate_image_diff_ratio(img1, img2)
    assert diff == 1.0

def test_wait_until_stable():
    img1 = Image.new("RGB", (100, 100), color="white")
    img2 = Image.new("RGB", (100, 100), color="white")
    
    with patch("edge_ie_agent.window_manager.capture_window") as mock_cap:
        mock_cap.side_effect = [(img1, (0, 0, 100, 100)), (img2, (0, 0, 100, 100))]
        stable = wait_until_stable(101, timeout=1.0, check_interval=0.05)
        assert stable is True
