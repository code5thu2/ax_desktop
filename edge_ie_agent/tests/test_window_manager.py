from unittest.mock import patch, MagicMock
import pytest
from edge_ie_agent.window_manager import get_window_bounds, find_edge_window, WindowNotFoundError

def test_get_window_bounds():
    with patch("win32gui.GetWindowRect") as mock_rect:
        mock_rect.return_value = (50, 50, 850, 650)
        bounds = get_window_bounds(12345)
        assert bounds == (50, 50, 800, 600)  # left, top, width, height

def test_find_edge_window_not_found():
    with patch("win32gui.EnumWindows") as mock_enum:
        # Simulate no windows found matching
        mock_enum.side_effect = lambda callback, extra: None
        with pytest.raises(WindowNotFoundError):
            find_edge_window("NonExistentKeywordXYZ")

def test_find_edge_window_found():
    def fake_enum(callback, extra):
        # callback(hwnd, extra)
        callback(101, extra)
        
    with patch("win32gui.EnumWindows", side_effect=fake_enum), \
         patch("win32gui.IsWindowVisible", return_value=True), \
         patch("win32gui.GetWindowText", return_value="Microsoft Edge - Trang chủ"):
        hwnd = find_edge_window("Edge")
        assert hwnd == 101
