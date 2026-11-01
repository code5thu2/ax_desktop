"""
Windows Native Window & Session Management
==========================================
Session desktop attachment, single-instance mutex enforcement,
IPC wake-up sockets, and Win32 foreground stealing.
"""

import os
import sys
import socket
import threading
import ctypes
from ctypes import wintypes
from desktop.config import ERROR_ALREADY_EXISTS


def ensure_default_desktop():
    """
    Ensures this process and all its threads attach to the interactive 'Default' desktop
    (where the user is actually logged in and looking at the screen).
    """
    try:
        user32 = ctypes.windll.user32
        GENERIC_ALL = 0x10000000
        h_def = user32.OpenDesktopW('Default', 0, False, GENERIC_ALL)
        if h_def:
            user32.SetThreadDesktop(h_def)
    except Exception:
        pass


def check_single_instance(mutex_name: str, ipc_port_file: str, window_title: str):
    """
    Ensure only one instance runs per user session.
    If another instance is already active, signal it to wake up and exit immediately.

    Args:
        mutex_name (str): Named mutex identifier.
        ipc_port_file (str): Path to temporary IPC port record file.
        window_title (str): Window caption to bring forward as fallback.

    Returns:
        ctypes.wintypes.HANDLE: Mutex handle to maintain active ownership.
    """
    ensure_default_desktop()

    kernel32 = ctypes.windll.kernel32
    mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        # Second instance detected: send wake-up signal to existing instance
        try:
            if os.path.isfile(ipc_port_file):
                with open(ipc_port_file, 'r', encoding='utf-8') as f:
                    port = int(f.read().strip())
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                s.connect(('127.0.0.1', port))
                s.sendall(b"SHOW\n")
                s.close()
        except Exception:
            pass

        # Fallback: force foreground via Win32 FindWindow
        try:
            hwnd = ctypes.windll.user32.FindWindowW(None, window_title)
            if hwnd:
                ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                ctypes.windll.user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

        sys.exit(0)

    return mutex


def start_ipc_server(ipc_port_file: str, on_show_callback):
    """
    Starts a background TCP socket listener on localhost. When a secondary application
    instance launches and connects, this server triggers the wake-up callback to bring the main window forward.

    Args:
        ipc_port_file (str): File where the bound ephemeral port is written.
        on_show_callback (callable): Function invoked when a wake-up command is received.

    Returns:
        socket.socket or None: The bound listening socket object.
    """
    try:
        ipc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ipc_server.bind(('127.0.0.1', 0))
        port = ipc_server.getsockname()[1]
        with open(ipc_port_file, 'w', encoding='utf-8') as f:
            f.write(str(port))

        def listener():
            ipc_server.listen(5)
            while True:
                try:
                    conn, _ = ipc_server.accept()
                    data = conn.recv(1024)
                    if b"SHOW" in data:
                        on_show_callback()
                    conn.close()
                except Exception:
                    break

        thread = threading.Thread(target=listener, daemon=True)
        thread.start()
        return ipc_server
    except Exception as e:
        print("[Desktop IPC] Server startup failed:", e)
        return None


def _steal_foreground(hwnd):
    """
    Forces the specified window handle (HWND) into the foreground,
    bypassing Windows foreground-lock restrictions using AttachThreadInput,
    SetForegroundWindow, BringWindowToTop, and SPI_SETFOREGROUNDLOCKTIMEOUT.
    """
    if not hwnd:
        return
    try:
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32

        SPI_SETFOREGROUNDLOCKTIMEOUT = 0x2001
        SPIF_SENDCHANGE = 0x0002
        SW_RESTORE = 9

        # Zero out foreground lock timeout to permit foreground stealing
        user32.SystemParametersInfoW(SPI_SETFOREGROUNDLOCKTIMEOUT, 0, ctypes.c_void_p(0), SPIF_SENDCHANGE)

        fg_hwnd = user32.GetForegroundWindow()
        cur_thread = kernel32.GetCurrentThreadId()
        fg_thread = user32.GetWindowThreadProcessId(fg_hwnd, None) if fg_hwnd else 0

        attached = False
        if fg_thread and fg_thread != cur_thread:
            attached = bool(user32.AttachThreadInput(cur_thread, fg_thread, True))

        try:
            user32.ShowWindow(hwnd, SW_RESTORE)
            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
        finally:
            if attached:
                user32.AttachThreadInput(cur_thread, fg_thread, False)
    except Exception as e:
        print("[Desktop] _steal_foreground error:", e)
