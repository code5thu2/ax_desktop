"""
Application Lifecycle Coordinator
=================================
Coordinates synchronization and transitions between the standalone Splash window
and the main Vue application window. Ensures zero flickering, proper DWM theme
application, and seamless activation.
"""

import time
import threading
import ctypes
from desktop.platform.win32_dwm import apply_title_bar_theme
from desktop.platform.win32_window import _steal_foreground

try:
    import clr
    clr.AddReference('System.Windows.Forms')
    import System.Windows.Forms as WinForms
except Exception:
    WinForms = None


class AppCoordinator:
    """
    Coordinates lifecycle between standalone Splash window and the real Main App.
    Guarantees that the splash window only disappears when:
    1. Splash simulation has finished.
    2. The main application (Vue 3, Pinia, Router) has ACTUALLY mounted and signaled ready.
    """
    def __init__(self):
        self.main_ready = False
        self.main_ready_event = threading.Event()
        self.transitioned = False
        self.is_dark = True
        # Use leading underscore to prevent pywebview recursive inspection crash
        self._splash_window = None
        self._main_window = None
        self._spotlight_window = None

    def set_windows(self, splash, main_win, spotlight_win=None):
        """
        Stores window references for the coordinator to manage visibility transitions.

        Args:
            splash: PyWebView splash window instance.
            main_win: PyWebView main application window instance.
            spotlight_win: PyWebView spotlight window instance (optional).
        """
        self._splash_window = splash
        self._main_window = main_win
        self._spotlight_window = spotlight_win

    def notify_main_ready(self):
        """
        Signals that the Vue 3 application has completed mounting, router resolution,
        and is ready for user interaction.
        """
        self.main_ready = True
        self.main_ready_event.set()

    def is_main_ready(self) -> bool:
        """
        Checks whether the main Vue 3 application window has signaled readiness.

        Returns:
            bool: True if main window is mounted and ready.
        """
        return self.main_ready

    def on_splash_done(self):
        """
        Called when the splash progress animation has completed 100%.
        Waits for the main app to finish initialization before executing the transition.
        """
        def _worker():
            if not self.transitioned:
                if not self.main_ready:
                    # Wait up to 5s for main Vue app to finish if splash completed first
                    self.main_ready_event.wait(timeout=5.0)
                self.transition_to_main()

        threading.Thread(target=_worker, daemon=True).start()

    def transition_to_main(self):
        """
        Reveals the main application window with customized Windows 11 DWM title bar styling,
        and disposes of the splash window.
        """
        if not self.transitioned:
            self.transitioned = True
            try:
                # 1. Reveal main application window
                if self._main_window:
                    # Wait up to 5 seconds for the native WinForms form to be initialized by the GUI thread
                    native_form = None
                    for _ in range(50):
                        native_form = getattr(self._main_window, 'native', None)
                        if native_form is not None:
                            break
                        time.sleep(0.1)

                    if WinForms and native_form and isinstance(native_form, WinForms.Form):
                        def _show():
                            if native_form.WindowState == WinForms.FormWindowState.Minimized:
                                native_form.WindowState = WinForms.FormWindowState.Normal
                            native_form.Show()
                            native_form.Activate()
                            native_form.BringToFront()

                        if native_form.InvokeRequired:
                            native_form.Invoke(WinForms.MethodInvoker(_show))
                        else:
                            _show()

                        if hasattr(native_form, 'Handle'):
                            hwnd = int(native_form.Handle.ToInt64())
                            ctypes.windll.user32.ShowWindow(hwnd, 9)
                            _steal_foreground(hwnd)

                        # Set shown event to prevent pywebview deadlock on subsequent window operations
                        if hasattr(self._main_window, 'events') and hasattr(self._main_window.events, 'shown'):
                            self._main_window.events.shown.set()
                    else:
                        if hasattr(self._main_window, 'events') and hasattr(self._main_window.events, 'shown'):
                            self._main_window.events.shown.set()
                        self._main_window.show()

                    apply_title_bar_theme(self._main_window, is_dark=self.is_dark)
            except Exception as e:
                print("[Desktop Coordinator] transition_to_main error:", e, flush=True)

            time.sleep(0.22)

            try:
                # 2. Hide standalone splash window (do NOT destroy master window to preserve WebView2 runtime)
                if self._splash_window:
                    self._splash_window.hide()
            except Exception:
                pass
