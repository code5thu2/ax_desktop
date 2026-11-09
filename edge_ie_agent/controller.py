"""Mouse and keyboard controller for Windows automation."""
import time
import pyautogui
import pyperclip

# Enable fail-safe: Moving mouse cursor to any corner of the screen aborts execution
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.2

class Controller:
    """Provides safe mouse and keyboard automation primitives."""
    
    def __init__(self, pause: float = 0.2):
        self.pause = pause
        pyautogui.PAUSE = pause

    def click(self, screen_x: int, screen_y: int) -> None:
        """Clicks at the specified screen coordinate."""
        pyautogui.click(screen_x, screen_y)

    def double_click(self, screen_x: int, screen_y: int) -> None:
        """Double clicks at the specified screen coordinate."""
        pyautogui.doubleClick(screen_x, screen_y)

    def hover(self, screen_x: int, screen_y: int, duration: float = 0.5) -> None:
        """Moves cursor to coordinate and hovers to trigger onmouseover dropdowns."""
        pyautogui.moveTo(screen_x, screen_y)
        time.sleep(duration)

    def scroll_at(self, screen_x: int, screen_y: int, direction: str = "down", amount: int = 3) -> None:
        """Moves cursor to target coordinate and scrolls vertically.
        
        Args:
            screen_x: X coordinate on screen.
            screen_y: Y coordinate on screen.
            direction: 'up' or 'down'.
            amount: Number of scroll units (each unit is 100 scroll clicks).
        """
        pyautogui.moveTo(screen_x, screen_y)
        clicks = amount * 100
        if direction.lower() == "down":
            clicks = -clicks
        pyautogui.scroll(clicks)

    def paste_text(self, text: str, press_enter: bool = False) -> None:
        """Inserts text safely via Windows Clipboard and Ctrl+V to prevent IME/Unikey conflicts."""
        pyperclip.copy(text)
        time.sleep(0.05)
        pyautogui.hotkey("ctrl", "v")
        if press_enter:
            time.sleep(0.1)
            pyautogui.press("enter")
