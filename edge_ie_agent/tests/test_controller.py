from unittest.mock import patch, MagicMock
from edge_ie_agent.controller import Controller

def test_paste_text_uses_clipboard():
    controller = Controller()
    with patch("pyperclip.copy") as mock_copy, \
         patch("pyautogui.hotkey") as mock_hotkey, \
         patch("pyautogui.press") as mock_press:
        controller.paste_text("Mã số thuế 0101234567", press_enter=True)
        mock_copy.assert_called_once_with("Mã số thuế 0101234567")
        mock_hotkey.assert_any_call("ctrl", "v")
        mock_press.assert_called_once_with("enter")

def test_click_and_double_click():
    controller = Controller()
    with patch("pyautogui.click") as mock_click, \
         patch("pyautogui.doubleClick") as mock_dbl_click:
        controller.click(150, 250)
        mock_click.assert_called_once_with(150, 250)
        
        controller.double_click(150, 250)
        mock_dbl_click.assert_called_once_with(150, 250)

def test_hover():
    controller = Controller()
    with patch("pyautogui.moveTo") as mock_move, \
         patch("time.sleep") as mock_sleep:
        controller.hover(300, 400, duration=0.8)
        mock_move.assert_called_once_with(300, 400)
        mock_sleep.assert_called_with(0.8)

def test_scroll_at():
    controller = Controller()
    with patch("pyautogui.moveTo") as mock_move, \
         patch("pyautogui.scroll") as mock_scroll:
        controller.scroll_at(200, 300, direction="down", amount=5)
        mock_move.assert_called_once_with(200, 300)
        # down scroll in pyautogui is negative
        mock_scroll.assert_called_once_with(-500)
        
        mock_scroll.reset_mock()
        controller.scroll_at(200, 300, direction="up", amount=2)
        mock_scroll.assert_called_once_with(200)
