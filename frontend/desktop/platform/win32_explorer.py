"""
Windows Explorer & Clipboard Context Provider
==============================================
Provides contextual integration with the Windows Shell:
- Inspects active File Explorer windows or Desktop via COM (Shell.Application) to detect selected files.
- Captures active text selections via transient clipboard interception.
- Reads file contents (plain text, utf-8/cp1252 fallbacks, docx tables/paragraphs).
"""

import os
import time
import uuid
import base64
import mimetypes
import ctypes

try:
    import clr
    clr.AddReference('System.Windows.Forms')
    import System
    from System.Reflection import BindingFlags
    from System.Threading import Thread, ThreadStart, ApartmentState
    import System.Windows.Forms as WinForms
except Exception:
    System = None
    WinForms = None


def read_local_file_content(path: str) -> str:
    """
    Reads file content from the local filesystem to supply context to AI.
    Supports text files (UTF-8 with fallbacks), docx documents, and warns for binary files.
    No artificial size limit is applied.

    Args:
        path (str): Absolute file path.

    Returns:
        str: Extracted textual contents.
    """
    if not path or not os.path.isfile(path):
        return ""
    try:
        lower = path.lower()
        if lower.endswith('.docx'):
            try:
                import docx
                doc = docx.Document(path)
                paragraphs = [p.text for p in doc.paragraphs if p.text]
                for table in doc.tables:
                    for row in table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                        if row_text:
                            paragraphs.append(row_text)
                return "\n".join(paragraphs)
            except Exception as de:
                return f"[Lỗi đọc tệp docx: {de}]"

        # Check if file might be binary
        with open(path, 'rb') as f:
            sample = f.read(1024)
            if b'\x00' in sample:
                mime, _ = mimetypes.guess_type(path)
                size = os.path.getsize(path)
                return f"[Tệp nhị phân {os.path.basename(path)} ({mime or 'application/octet-stream'}, {size} bytes)]"

        # Try plain text reading with multiple encodings
        for enc in ('utf-8', 'utf-8-sig', 'cp1252', 'latin-1'):
            try:
                with open(path, 'r', encoding=enc) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"[Desktop] read_local_file_content error for {path}:", e)
        return f"[Lỗi đọc tệp: {e}]"


def get_clipboard_text() -> str:
    """Reads text content from Windows clipboard using STA thread."""
    if not WinForms:
        return ""
    res = [""]

    def worker():
        try:
            if WinForms.Clipboard.ContainsText():
                res[0] = WinForms.Clipboard.GetText()
        except Exception:
            pass

    t = Thread(ThreadStart(worker))
    t.SetApartmentState(ApartmentState.STA)
    t.Start()
    t.Join()
    return res[0]


def set_clipboard_text(text: str):
    """Sets or clears text content on Windows clipboard using STA thread."""
    if not WinForms:
        return

    def worker():
        try:
            if text:
                WinForms.Clipboard.SetText(text)
            else:
                WinForms.Clipboard.Clear()
        except Exception:
            pass

    t = Thread(ThreadStart(worker))
    t.SetApartmentState(ApartmentState.STA)
    t.Start()
    t.Join()


def get_selected_explorer_files(max_files: int = 5) -> list:
    """
    Retrieves selected files from the active Windows File Explorer or Desktop window
    using .NET CLR COM Interop (Shell.Application).
    Returns a list of dicts conforming to the frontend Attachment interface:
    [{ id, name, path, size, type, base64?, url? }]
    """
    if not System:
        return []
    try:
        user32 = ctypes.windll.user32
        h_def = user32.OpenDesktopW('Default', 0, False, 0x10000000)
        if h_def:
            user32.SetThreadDesktop(h_def)

        fg_hwnd = user32.GetForegroundWindow()
        if not fg_hwnd:
            return []

        fg_root = user32.GetAncestor(fg_hwnd, 2)
        shell_hwnd = user32.GetShellWindow()
        desktop_hwnd = user32.GetDesktopWindow()

        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(fg_hwnd, buf, 256)
        cls_fg = buf.value
        user32.GetClassNameW(fg_root, buf, 256)
        cls_root = buf.value

        is_desktop = (
            fg_hwnd in (shell_hwnd, desktop_hwnd) or
            fg_root in (shell_hwnd, desktop_hwnd) or
            cls_fg in ('Progman', 'WorkerW') or
            cls_root in ('Progman', 'WorkerW')
        )
        is_explorer = (
            cls_fg in ('CabinetWClass', 'ExploreWClass') or
            cls_root in ('CabinetWClass', 'ExploreWClass')
        )

        # If foreground is neither File Explorer nor Desktop, don't grab files
        if not is_desktop and not is_explorer:
            return []

        t = System.Type.GetTypeFromProgID('Shell.Application')
        shell = System.Activator.CreateInstance(t)
        windows = t.InvokeMember('Windows', BindingFlags.InvokeMethod, None, shell, None)
        count = windows.GetType().InvokeMember('Count', BindingFlags.GetProperty, None, windows, None)

        def extract_paths_from_doc(doc):
            paths = []
            if not doc:
                return paths
            try:
                sel = doc.GetType().InvokeMember('SelectedItems', BindingFlags.InvokeMethod, None, doc, None)
                sel_count = sel.GetType().InvokeMember('Count', BindingFlags.GetProperty, None, sel, None)
                for j in range(min(sel_count, max_files)):
                    item = sel.GetType().InvokeMember('Item', BindingFlags.InvokeMethod, None, sel, System.Array[System.Object]([System.Int32(j)]))
                    p = item.GetType().InvokeMember('Path', BindingFlags.GetProperty, None, item, None)
                    if p and os.path.exists(p):
                        paths.append(str(p))
            except Exception:
                pass
            return paths

        selected_paths = []
        if is_desktop:
            try:
                args = System.Array[System.Object]([System.Int32(0), System.Int32(0), System.Int32(8), System.Int32(0), System.Int32(1)])
                dt = windows.GetType().InvokeMember('FindWindowSW', BindingFlags.InvokeMethod, None, windows, args)
                if dt:
                    doc = dt.GetType().InvokeMember('Document', BindingFlags.GetProperty, None, dt, None)
                    selected_paths = extract_paths_from_doc(doc)
            except Exception:
                pass

        if is_explorer and not selected_paths:
            # 1. Try matching the exact foreground Explorer HWND or root
            for i in range(count):
                try:
                    w = windows.GetType().InvokeMember('Item', BindingFlags.InvokeMethod, None, windows, System.Array[System.Object]([System.Int32(i)]))
                    w_hwnd = int(w.GetType().InvokeMember('HWND', BindingFlags.GetProperty, None, w, None))
                    if w_hwnd == fg_hwnd or w_hwnd == fg_root:
                        doc = w.GetType().InvokeMember('Document', BindingFlags.GetProperty, None, w, None)
                        selected_paths = extract_paths_from_doc(doc)
                        if selected_paths:
                            break
                except Exception:
                    continue

            # 2. If matching HWND had no selected items or didn't match, check other Explorer windows
            if not selected_paths:
                for i in range(count):
                    try:
                        w = windows.GetType().InvokeMember('Item', BindingFlags.InvokeMethod, None, windows, System.Array[System.Object]([System.Int32(i)]))
                        doc = w.GetType().InvokeMember('Document', BindingFlags.GetProperty, None, w, None)
                        paths = extract_paths_from_doc(doc)
                        if paths:
                            selected_paths = paths
                            break
                    except Exception:
                        continue

        results = []
        for p in selected_paths[:max_files]:
            try:
                name = os.path.basename(p)
                size = os.path.getsize(p) if os.path.isfile(p) else 0
                mime, _ = mimetypes.guess_type(p)
                file_obj = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'path': p,
                    'size': size,
                    'type': mime or 'application/octet-stream'
                }
                if mime and mime.startswith('image/') and size < 20 * 1024 * 1024:
                    try:
                        with open(p, 'rb') as img_f:
                            b64 = base64.b64encode(img_f.read()).decode('ascii')
                            data_url = f'data:{mime};base64,{b64}'
                            file_obj['base64'] = data_url
                            file_obj['url'] = data_url
                    except Exception:
                        pass
                results.append(file_obj)
            except Exception:
                pass
        return results
    except Exception as e:
        print('[Desktop] get_selected_explorer_files error:', e)
        return []


def get_selected_text_snippet() -> str:
    """
    Attempts to capture highlighted text from the active application window
    by simulating a copy action (Ctrl+C), reading clipboard, and immediately
    restoring the user's prior clipboard content.
    Returns the copied text or empty string if nothing was selected.
    """
    user32 = ctypes.windll.user32
    fg_hwnd = user32.GetForegroundWindow()
    if not fg_hwnd:
        return ""

    # Don't grab from Spotlight itself or Windows Desktop
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(fg_hwnd, buf, 256)
    title = buf.value
    user32.GetClassNameW(fg_hwnd, buf, 256)
    cls = buf.value
    if "Spotlight" in title or cls in ('Progman', 'WorkerW'):
        return ""

    try:
        # 1. Backup old clipboard text
        old_text = get_clipboard_text()

        # 2. Clear clipboard so we know if a copy occurred
        set_clipboard_text("")

        # 3. Simulate Ctrl + C
        VK_CONTROL = 0x11
        VK_C = 0x43
        KEYEVENTF_KEYUP = 0x0002

        user32.keybd_event(VK_CONTROL, 0, 0, 0)
        user32.keybd_event(VK_C, 0, 0, 0)
        user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

        # Wait a short duration (60ms) for the target app to process WM_COPY
        time.sleep(0.06)

        # 4. Check if new text appeared on clipboard
        new_text = get_clipboard_text()

        # 5. Restore user's previous clipboard immediately
        if old_text:
            set_clipboard_text(old_text)

        if new_text and new_text.strip():
            return new_text.strip()
        return ""
    except Exception as e:
        print("[Desktop] get_selected_text_snippet error:", e)
        return ""
