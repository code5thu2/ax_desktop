"""
MCP Protocol Studio Desktop Application
=======================================
Dedicated desktop application for managing AI Model Context Protocol servers and tools.
Provides:
- Independent process execution and taskbar grouping
- Custom isometric 3D protocol cube branding
- Fast, focused direct-to-plugin routing
- Dark theme title bar integration and system tray management
"""

import os
import sys
import time
import threading
import ctypes
import webview
import webview.platforms.winforms as wf

try:
    import clr
    clr.AddReference('System.Windows.Forms')
    clr.AddReference('System.Drawing')
    import System
    import System.Windows.Forms as WinForms
    import System.Drawing as Drawing
except Exception:
    WinForms = None
    Drawing = None

from desktop.config import (
    PLUGIN_APP_NAME,
    PLUGIN_MUTEX_NAME,
    PLUGIN_IPC_PORT_FILE,
    PLUGIN_APP_USER_MODEL_ID,
    PLUGIN_WINDOW_WIDTH,
    PLUGIN_WINDOW_HEIGHT,
    PLUGIN_MIN_WIDTH,
    PLUGIN_MIN_HEIGHT,
    PLUGIN_DARK_BG,
    PLUGIN_DARK_BORDER,
    get_dist_dir,
    get_icon_path,
)
from desktop.server import start_local_server
from desktop.platform.win32_window import (
    ensure_default_desktop,
    check_single_instance,
    start_ipc_server,
    _steal_foreground,
)
from desktop.platform.win32_dwm import apply_title_bar_theme
from desktop.platform.win32_tray import SystemTrayManager
from desktop.core.screens import get_screen_center
from desktop.core.coordinator import AppCoordinator
from desktop.api.plugin_manager_api import PluginManagerApi


def run_plugin_manager():
    """Entry point to launch the MCP Protocol Studio desktop application."""
    ensure_default_desktop()

    # Single-instance check
    if "PYTEST_CURRENT_TEST" not in os.environ:
        check_single_instance(PLUGIN_MUTEX_NAME, PLUGIN_IPC_PORT_FILE, PLUGIN_APP_NAME)

    # Set explicit AppUserModelID for taskbar isolation
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(PLUGIN_APP_USER_MODEL_ID)
    except Exception:
        pass

    dist_dir = get_dist_dir()
    index_html = os.path.join(dist_dir, 'index.html')
    if not os.path.isfile(index_html):
        print(f"Error: Could not find build files at {index_html}")
        print("Please run 'npm run build' first.")
        sys.exit(1)

    # Initialize WinForms app styling
    wf.setup_app()

    # Start local HTTP server
    server, port = start_local_server()
    # Note: query param ?target=plugins avoids WebView2 # crash on initial create_window
    app_url = f'http://127.0.0.1:{port}/?target=plugins'

    is_debug = '--debug' in sys.argv or os.environ.get('MCP_DEBUG') == '1'

    coordinator = AppCoordinator()
    api = PluginManagerApi(coordinator=coordinator, app_name=PLUGIN_APP_NAME)

    # Calculate center position
    main_x, main_y, primary_screen = get_screen_center(PLUGIN_WINDOW_WIDTH, PLUGIN_WINDOW_HEIGHT)

    is_hidden_startup = ('--autostart' in sys.argv or '--hidden' in sys.argv or '--minimized' in sys.argv)

    main_window = webview.create_window(
        title=PLUGIN_APP_NAME,
        url=app_url,
        width=PLUGIN_WINDOW_WIDTH,
        height=PLUGIN_WINDOW_HEIGHT,
        x=main_x,
        y=main_y,
        screen=primary_screen,
        min_size=(PLUGIN_MIN_WIDTH, PLUGIN_MIN_HEIGHT),
        resizable=True,
        hidden=is_hidden_startup,
        background_color=PLUGIN_DARK_BG,
        js_api=api,
    )

    coordinator.set_windows(None, main_window)
    coordinator.notify_main_ready()
    coordinator.transitioned = True

    is_real_exit = False

    def exit_application():
        nonlocal is_real_exit
        is_real_exit = True

        if tray_manager:
            tray_manager.dispose()

        try:
            if os.path.isfile(PLUGIN_IPC_PORT_FILE):
                os.remove(PLUGIN_IPC_PORT_FILE)
        except Exception:
            pass

        try:
            server.shutdown()
        except Exception:
            pass

        try:
            if main_window:
                main_window.destroy()
        except Exception:
            pass

        try:
            if WinForms:
                WinForms.Application.Exit()
        except Exception:
            pass

        threading.Timer(0.3, lambda: os._exit(0)).start()

    # Intercept 'X' window close button -> Close to Tray
    def on_main_closing():
        nonlocal is_real_exit
        if not is_real_exit:
            tray_manager.hide_window()
            return False
        return True

    main_window.events.closing += on_main_closing

    # Icon path
    icon_file = get_icon_path(is_plugin_mode=True)

    # Initialize System Tray Manager
    tray_manager = SystemTrayManager(
        main_window=main_window,
        coordinator=coordinator,
        icon_path=icon_file,
        on_exit_fn=exit_application,
        app_title=PLUGIN_APP_NAME,
        app_reg_name=PLUGIN_APP_NAME,
    )

    def init_tray_thread():
        target = None
        while not target:
            if getattr(main_window, 'native', None):
                target = main_window.native
            else:
                time.sleep(0.05)

        if WinForms:
            target.Invoke(WinForms.MethodInvoker(tray_manager.initialize))
        apply_title_bar_theme(main_window, is_dark=True, bg_hex=PLUGIN_DARK_BG, border_hex=PLUGIN_DARK_BORDER)

    threading.Thread(target=init_tray_thread, daemon=True).start()

    def apply_theme():
        apply_title_bar_theme(main_window, is_dark=True, bg_hex=PLUGIN_DARK_BG, border_hex=PLUGIN_DARK_BORDER)

    main_window.events.shown += apply_theme
    main_window.events.loaded += apply_theme

    # Start IPC server
    start_ipc_server(PLUGIN_IPC_PORT_FILE, tray_manager.show_and_activate)

    # Start pywebview event loop
    webview.start(
        debug=is_debug,
        icon=icon_file if os.path.isfile(icon_file) else None
    )


if __name__ == '__main__':
    run_plugin_manager()
