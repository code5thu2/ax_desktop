"""
Windows System Tray (NotifyIcon) & Startup Integration
======================================================
Manages Windows System Tray icon, dynamic context menus (Show/Hide, Autostart, Exit),
mouse interaction events, and Windows logon autostart registry entries.
"""

import os
import sys
import winreg
import ctypes
from desktop.config import REG_RUN_KEY, APP_REG_NAME
from desktop.platform.win32_dwm import apply_title_bar_theme
from desktop.platform.win32_window import _steal_foreground

# CLR Windows Forms imports for NotifyIcon
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


def is_autostart_enabled(app_name: str = APP_REG_NAME) -> bool:
    r"""
    Checks Windows registry (HKCU\Software\Microsoft\Windows\CurrentVersion\Run)
    to verify if the application is registered to automatically start on Windows logon.

    Returns:
        bool: True if autostart registry entry exists, False otherwise.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
            val, _ = winreg.QueryValueEx(key, app_name)
            return bool(val)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def set_autostart(enable: bool, app_name: str = APP_REG_NAME, custom_command: str = None) -> bool:
    """
    Enables or disables automatic application startup on Windows logon via the registry.

    Args:
        enable (bool): Whether to add (True) or remove (False) the registry run entry.
        app_name (str): The registry value name. Defaults to APP_REG_NAME.
        custom_command (str, optional): The command line to register.

    Returns:
        bool: True if registry operation succeeded, False otherwise.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                if custom_command:
                    cmd = custom_command
                elif getattr(sys, 'frozen', False):
                    cmd = f'"{sys.executable}" --autostart'
                else:
                    exe = sys.executable
                    if exe.lower().endswith("python.exe"):
                        w_candidate = exe[:-10] + "pythonw.exe"
                        if os.path.isfile(w_candidate):
                            exe = w_candidate
                    script_path = os.path.abspath(sys.argv[0])
                    cmd = f'"{exe}" "{script_path}" --autostart'
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                except FileNotFoundError:
                    pass
            return True
    except Exception as e:
        print("[Desktop Tray] Failed to update autostart setting:", e)
        return False


class SystemTrayManager:
    """
    Manages Windows System Tray (NotifyIcon) with:
    - Left-click / Double-click: Toggle show/hide the main app window
    - Context Menu:
      * Dynamic "Mở [App Title]" / "Ẩn [App Title]"
      * "Khởi động cùng Windows" (with Checkmark synced to Registry)
      * Optional Spotlight AI trigger item
      * Separator
      * "Thoát" (Clean exit and icon disposal)
    """
    def __init__(self, main_window, coordinator, icon_path: str, on_exit_fn, on_spotlight_fn=None, app_title: str = "MCP Protocol Studio", app_reg_name: str = APP_REG_NAME):
        self.main_window = main_window
        self.coordinator = coordinator
        self.icon_path = icon_path
        self.on_exit_fn = on_exit_fn
        self.on_spotlight_fn = on_spotlight_fn
        self.app_title = app_title
        self.app_reg_name = app_reg_name
        self.notify_icon = None
        self.context_menu = None
        self.item_toggle = None
        self.item_autostart = None
        self.is_initialized = False

    def initialize(self):
        """
        Initializes the Windows Forms NotifyIcon on the GUI thread, configures tray icon,
        and builds the contextual right-click menu strip.
        """
        if self.is_initialized or not WinForms:
            return
        self.is_initialized = True

        self.notify_icon = WinForms.NotifyIcon()
        self.notify_icon.Text = self.app_title

        if self.icon_path and os.path.isfile(self.icon_path):
            try:
                self.notify_icon.Icon = Drawing.Icon(self.icon_path)
            except Exception:
                pass

        self.context_menu = WinForms.ContextMenuStrip()

        # Item 1: Dynamic Show/Hide
        self.item_toggle = WinForms.ToolStripMenuItem(f"Mở {self.app_title}")
        self.item_toggle.Click += lambda s, e: self.toggle_window()

        # Item 2: Khởi động cùng Windows
        self.item_autostart = WinForms.ToolStripMenuItem("Khởi động cùng Windows")
        self.item_autostart.Click += self.on_autostart_clicked

        # Item 3: Separator
        separator = WinForms.ToolStripSeparator()

        # Item 4: Thoát
        item_exit = WinForms.ToolStripMenuItem("Thoát")
        item_exit.Click += lambda s, e: self.on_exit_fn()

        self.context_menu.Items.Add(self.item_toggle)
        self.context_menu.Items.Add(self.item_autostart)
        self.context_menu.Items.Add(separator)
        self.context_menu.Items.Add(item_exit)

        self.context_menu.Opening += self.on_menu_opening
        self.notify_icon.ContextMenuStrip = self.context_menu

        # Left-click toggles Show/Hide, double-click shows and activates
        self.notify_icon.MouseClick += self.on_tray_click
        self.notify_icon.DoubleClick += lambda s, e: self.show_and_activate()

        # On right-click, set foreground window to ensure context menu properly opens and dismisses
        def on_mouse_up(sender, e):
            if e.Button == WinForms.MouseButtons.Right:
                try:
                    native_form = getattr(self.main_window, 'native', None)
                    if native_form and hasattr(native_form, 'Handle'):
                        hwnd = int(native_form.Handle.ToInt64())
                        ctypes.windll.user32.SetForegroundWindow(hwnd)
                except Exception:
                    pass

        self.notify_icon.MouseUp += on_mouse_up
        self.notify_icon.Visible = True

    def on_tray_click(self, sender, e):
        """
        Handles mouse click on tray icon. Left click toggles window visibility.
        """
        if e.Button == WinForms.MouseButtons.Left:
            self.toggle_window()

    def on_menu_opening(self, sender, e):
        """
        Dynamically updates the context menu item text ('Mở' vs 'Ẩn') and autostart checkmark
        immediately before displaying the popup menu.
        """
        try:
            native_form = getattr(self.main_window, 'native', None)
            if native_form and native_form.Visible and native_form.WindowState != WinForms.FormWindowState.Minimized:
                self.item_toggle.Text = f"Ẩn {self.app_title}"
            else:
                self.item_toggle.Text = f"Mở {self.app_title}"
            self.item_autostart.Checked = is_autostart_enabled(self.app_reg_name)
        except Exception:
            pass

    def on_autostart_clicked(self, sender, e):
        """
        Toggles the Windows autostart registry configuration on menu item click.
        """
        current_state = is_autostart_enabled(self.app_reg_name)
        new_state = not current_state
        set_autostart(new_state, app_name=self.app_reg_name)
        self.item_autostart.Checked = is_autostart_enabled(self.app_reg_name)

    def show_and_activate(self):
        """
        Brings the main application window out of tray, restores from minimized state,
        and focuses it as the active foreground window.
        """
        try:
            if self.coordinator and not self.coordinator.transitioned:
                self.coordinator.transition_to_main()

            native_form = getattr(self.main_window, 'native', None)
            if not native_form:
                self.main_window.show()
                return

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
                _steal_foreground(hwnd)

            apply_title_bar_theme(self.main_window, is_dark=getattr(self.coordinator, 'is_dark', True))
        except Exception as e:
            print("[Desktop Tray] show_and_activate error:", e)

    def hide_window(self):
        """
        Hides the main application window into the Windows notification tray area.
        """
        try:
            native_form = getattr(self.main_window, 'native', None)
            if native_form:
                if native_form.InvokeRequired:
                    native_form.Invoke(WinForms.MethodInvoker(native_form.Hide))
                else:
                    native_form.Hide()
            else:
                self.main_window.hide()
        except Exception:
            pass

    def toggle_window(self):
        """
        Toggles window visibility: if currently visible and active, hides to tray; otherwise restores to front.
        """
        try:
            if self.coordinator and not self.coordinator.transitioned:
                self.coordinator.transition_to_main()
                return

            native_form = getattr(self.main_window, 'native', None)
            if not native_form:
                self.main_window.show()
                return

            def _toggle():
                if native_form.Visible and native_form.WindowState != WinForms.FormWindowState.Minimized:
                    native_form.Hide()
                else:
                    if native_form.WindowState == WinForms.FormWindowState.Minimized:
                        native_form.WindowState = WinForms.FormWindowState.Normal
                    native_form.Show()
                    native_form.Activate()
                    native_form.BringToFront()

            if native_form.InvokeRequired:
                native_form.Invoke(WinForms.MethodInvoker(_toggle))
            else:
                _toggle()

            apply_title_bar_theme(self.main_window, is_dark=getattr(self.coordinator, 'is_dark', True))
        except Exception:
            pass

    def dispose(self):
        """
        Safely disposes of NotifyIcon system resources upon application exit.
        """
        try:
            def _dispose():
                if self.notify_icon:
                    self.notify_icon.Visible = False
                    self.notify_icon.Dispose()
            native_form = getattr(self.main_window, 'native', None)
            if native_form and hasattr(native_form, 'InvokeRequired') and native_form.InvokeRequired:
                native_form.Invoke(WinForms.MethodInvoker(_dispose))
            else:
                _dispose()
        except Exception:
            pass
