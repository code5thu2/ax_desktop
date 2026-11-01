"""
Splash Screen JavaScript Bridge API
====================================
API exposed to the standalone Splash window (public/splash.html).
Allows HTML/JS animation to query Vue application readiness and signal completion.
"""


class SplashApi:
    """API exposed to the standalone Splash window (public/splash.html)"""
    def __init__(self, coordinator):
        # Must start with underscore to avoid pywebview reflection traversal
        self._coordinator = coordinator

    def is_main_ready(self) -> bool:
        """
        Queries coordinator to determine whether the main Vue window is ready to display.

        Returns:
            bool: True if ready.
        """
        if self._coordinator:
            return self._coordinator.is_main_ready()
        return True

    def on_splash_done(self):
        """
        Notifies coordinator that the splash progress animation has completed.
        """
        if self._coordinator:
            self._coordinator.on_splash_done()
