import pytest
from edge_ie_agent.coordinate import normalize_to_screen, clamp_point

def test_normalize_center():
    # Window rect: (left=100, top=100, width=1000, height=800)
    rect = (100, 100, 1000, 800)
    screen_x, screen_y = normalize_to_screen((500, 500), rect)
    assert screen_x == 600
    assert screen_y == 500

def test_normalize_corners():
    rect = (200, 150, 800, 600)
    # Top-left (0, 0) -> (200, 150)
    assert normalize_to_screen((0, 0), rect) == (200, 150)
    # Bottom-right (1000, 1000) -> (1000, 750)
    assert normalize_to_screen((1000, 1000), rect) == (1000, 750)

def test_clamp_point():
    assert clamp_point((-50, 1200)) == (0.0, 1000.0)
    assert clamp_point((500, 500)) == (500.0, 500.0)
    assert clamp_point((0, 1000)) == (0.0, 1000.0)
