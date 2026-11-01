"""
Windows Global Hotkey Listener
==============================
Listens for system-wide shortcuts (Ctrl+Space, Alt+Space, Ctrl+Shift+Space)
using Win32 RegisterHotKey in a background message loop thread.
"""

import threading
import ctypes
from ctypes import wintypes
from desktop.platform.win32_window import ensure_default_desktop


class GlobalHotkeyListener:
    """
    Listens for system-wide hotkeys using Win32 RegisterHotKey in a dedicated background thread.
    """
    def __init__(self, callback, hotkey_id: int = 9001):
        self.callback = callback
        self.hotkey_id = hotkey_id
        self.thread = None
        self.running = False
        self.thread_id = None

    def start(self):
        """Starts the hotkey message loop in a background daemon thread."""
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def run(self):
        """Runs synchronously in the current thread."""
        self._run()

    def _run(self):
        ensure_default_desktop()
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        self.thread_id = kernel32.GetCurrentThreadId()

        MOD_ALT = 0x0001
        MOD_CONTROL = 0x0002
        MOD_SHIFT = 0x0004
        MOD_NOREPEAT = 0x4000
        VK_SPACE = 0x20
        WM_HOTKEY = 0x0312

        # 1. Register Ctrl + Space with MOD_NOREPEAT to prevent repeat triggers
        res1 = user32.RegisterHotKey(None, self.hotkey_id, MOD_CONTROL | MOD_NOREPEAT, VK_SPACE)
        if not res1:
            res1 = user32.RegisterHotKey(None, self.hotkey_id, MOD_CONTROL, VK_SPACE)

        if not res1:
            print(f"[Spotlight] Failed to register Ctrl+Space global hotkey (code: {kernel32.GetLastError()})", flush=True)
        else:
            print(f"[Spotlight] Successfully registered Ctrl+Space global hotkey (id: {self.hotkey_id})", flush=True)

        # 2. Register Ctrl + Shift + Space as alternative fallback (in case IME/Unikey/EVKey steals Ctrl+Space)
        alt_id = self.hotkey_id + 1
        res2 = user32.RegisterHotKey(None, alt_id, MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT, VK_SPACE)
        if not res2:
            res2 = user32.RegisterHotKey(None, alt_id, MOD_CONTROL | MOD_SHIFT, VK_SPACE)
        if res2:
            print(f"[Spotlight] Successfully registered secondary Ctrl+Shift+Space global hotkey (id: {alt_id})", flush=True)

        # 3. Register Alt + Space (Raycast/Spotlight/PowerToys standard, immune to UniKey hooks)
        alt_space_id = self.hotkey_id + 2
        res3 = user32.RegisterHotKey(None, alt_space_id, MOD_ALT | MOD_NOREPEAT, VK_SPACE)
        if not res3:
            res3 = user32.RegisterHotKey(None, alt_space_id, MOD_ALT, VK_SPACE)
        if res3:
            print(f"[Spotlight] Successfully registered Alt+Space global hotkey (id: {alt_space_id})", flush=True)

        msg = wintypes.MSG()
        while self.running and user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY and (msg.wParam in (self.hotkey_id, alt_id, alt_space_id)):
                print(f"[Spotlight] Hotkey triggered (id: {msg.wParam})! Executing callback...", flush=True)
                try:
                    self.callback()
                except Exception as e:
                    print("[Spotlight] Error in hotkey callback:", e, flush=True)
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if res1:
            user32.UnregisterHotKey(None, self.hotkey_id)
        if res2:
            user32.UnregisterHotKey(None, alt_id)
        if res3:
            user32.UnregisterHotKey(None, alt_space_id)

    def stop(self):
        """Stops the hotkey message loop and terminates thread."""
        self.running = False
        if self.thread_id:
            WM_QUIT = 0x0012
            try:
                ctypes.windll.user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
            except Exception:
                pass
