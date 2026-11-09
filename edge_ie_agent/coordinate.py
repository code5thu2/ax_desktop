"""Coordinate normalization and scaling utility.

Translates normalized [0, 1000] coordinates returned by Qwen Vision
into absolute Windows screen coordinates (pixels).
"""
from typing import Tuple

def clamp_point(point: Tuple[float, float]) -> Tuple[float, float]:
    """Clamps coordinates to the valid [0, 1000] range."""
    x, y = point
    clamped_x = max(0.0, min(1000.0, float(x)))
    clamped_y = max(0.0, min(1000.0, float(y)))
    return (clamped_x, clamped_y)

def normalize_to_screen(
    point: Tuple[float, float],
    window_rect: Tuple[int, int, int, int]
) -> Tuple[int, int]:
    """Converts a normalized (x, y) point [0, 1000] to absolute screen coordinates.
    
    Args:
        point: Tuple (x, y) where 0 <= x, y <= 1000.
        window_rect: Tuple (left, top, width, height) of the captured window.
        
    Returns:
        Tuple (screen_x, screen_y) in screen pixels.
    """
    clamped_x, clamped_y = clamp_point(point)
    left, top, width, height = window_rect
    
    screen_x = int(left + (clamped_x / 1000.0) * width)
    screen_y = int(top + (clamped_y / 1000.0) * height)
    return (screen_x, screen_y)
