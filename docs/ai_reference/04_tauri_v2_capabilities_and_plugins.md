# Đặc Tả Tauri v2: Capabilities, Permissions & Official Plugins (Dành Cho AI Offline)

> **MỤC ĐÍCH DÀNH CHO AI:** Trong Tauri v2, cơ chế bảo mật đã được thay thế hoàn toàn bằng hệ thống **Capabilities và Permissions (ACL)**. Nếu AI không cấu hình đúng hoặc không biết cách dùng plugin, ứng dụng sẽ bị từ chối quyền thực thi ngầm (`Access Denied / Permission Denied`). Tài liệu này đặc tả cơ chế phân quyền và cách sử dụng các Plugin chính thức của Tauri v2 (kèm giải pháp thay thế bằng Rust thuần khi không có sẵn crate plugin).

---

## 1. Hệ Thống Capabilities & Permissions Trong Tauri v2

Khác với Tauri v1 (dùng `"allowlist"` trong `tauri.conf.json`), Tauri v2 chia nhỏ quyền vào các tệp JSON đặt tại `src-tauri/capabilities/` hoặc nhúng trong cấu hình.

### 1.1 Cấu Trúc File Capability Mặc Định (`src-tauri/capabilities/default.json`)
```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default-capability",
  "description": "Cấp quyền IPC mặc định cho cửa sổ chính",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "core:window:allow-show",
    "core:window:allow-hide",
    "core:window:allow-set-focus",
    "core:window:allow-minimize",
    "core:window:allow-unminimize",
    "core:event:allow-listen",
    "core:event:allow-emit"
  ]
}
```

> [!IMPORTANT]
> **Quy tắc vàng cho AI:** Mặc định `"core:default"` cho phép gọi các command tự viết qua `#[tauri::command]`. Nhưng nếu gọi API điều khiển cửa sổ trực tiếp từ Frontend (`@tauri-apps/api/window`), bạn **PHẢI** khai báo quyền tương ứng trong `permissions` (như `core:window:allow-show`).

---

## 2. Danh Mục Các Plugin Chính Thức Của Tauri v2 & Cách Tích Hợp

| Plugin | Tên Crate Backend | Tên Package Frontend | Quyền Cần Cấp (Capability) |
| :--- | :--- | :--- | :--- |
| **Dialog (File Picker)** | `tauri-plugin-dialog` | `@tauri-apps/plugin-dialog` | `"dialog:default"`, `"dialog:allow-open"` |
| **Shell (Chạy tiến trình)**| `tauri-plugin-shell` | `@tauri-apps/plugin-shell` | `"shell:default"`, `"shell:allow-open"` |
| **Notification** | `tauri-plugin-notification`| `@tauri-apps/plugin-notification` | `"notification:default"` |
| **Clipboard** | `tauri-plugin-clipboard-manager`| `@tauri-apps/plugin-clipboard-manager`| `"clipboard-manager:default"` |
| **Single Instance** | `tauri-plugin-single-instance`| *(Chỉ backend)* | Không cần |
| **Autostart** | `tauri-plugin-autostart` | *(Chỉ backend hoặc frontend)* | `"autostart:default"` |
| **Local Store (KV)** | `tauri-plugin-store` | `@tauri-apps/plugin-store` | `"store:default"` |
| **Updater** | `tauri-plugin-updater` | `@tauri-apps/plugin-updater` | `"updater:default"` |

### 2.1 Mẫu Tích Hợp Plugin Trong `lib.rs` (Tauri v2)
```rust
pub fn run() {
    tauri::Builder::default()
        // Đăng ký các plugin chính thức của Tauri v2:
        .plugin(tauri_plugin_single_instance::init(|app, _args, _cwd| {
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.show();
                let _ = w.set_focus();
            }
        }))
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            Some(vec!["--autostart"]),
        ))
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .run(tauri::generate_context!())
        .expect("Lỗi chạy app");
}
```

---

## 3. Chiến Lược "Pure Rust Fallback" (Cực Kỳ Quan Trọng Khi Offline)

Khi làm việc trên máy không có mạng, nếu dự án **chưa tải sẵn crate plugin** (ví dụ thiếu `tauri-plugin-dialog` hoặc `tauri-plugin-single-instance`), AI **KHÔNG ĐƯỢC ĐẦU HÀNG** mà phải chuyển sang giải pháp **Pure Rust Fallback** sử dụng thư viện chuẩn và Win32 API tích hợp sẵn:

### 3.1 Thay Thế `tauri-plugin-single-instance` Bằng Win32 Mutex
*Không cần bất kỳ crate nào ngoài `windows-sys` (hoặc `winapi`):*
```rust
#[cfg(target_os = "windows")]
pub fn ensure_single_instance(mutex_name: &str) -> Result<windows_sys::Win32::Foundation::HANDLE, &'static str> {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;
    let wide: Vec<u16> = OsStr::new(mutex_name).encode_wide().chain(Some(0)).collect();
    unsafe {
        let handle = windows_sys::Win32::System::Threading::CreateMutexW(std::ptr::null(), 1, wide.as_ptr());
        if handle == 0 || windows_sys::Win32::Foundation::GetLastError() == 183 {
            return Err("Instance already running");
        }
        Ok(handle)
    }
}
```

### 3.2 Thay Thế `tauri-plugin-dialog` Bằng PowerShell/COM Native
*Không cần plugin, không hiện màn hình đen console:*
```rust
use std::os::windows::process::CommandExt;
use std::process::Command;

#[tauri::command]
pub fn native_open_file_dialog() -> Option<String> {
    const CREATE_NO_WINDOW: u32 = 0x08000000;
    let script = "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; \
                  $d = New-Object System.Windows.Forms.OpenFileDialog; \
                  if ($d.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { [Console]::Write($d.FileName) }";

    let output = Command::new("powershell")
        .args(["-NoProfile", "-NonInteractive", "-Command", script])
        .creation_flags(CREATE_NO_WINDOW)
        .output()
        .ok()?;

    let path = String::from_utf8_lossy(&output.stdout).trim().to_string();
    if path.is_empty() { None } else { Some(path) }
}
```

### 3.3 Thay Thế `tauri-plugin-autostart` Bằng Registry
*Ghi trực tiếp Registry `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`:*
```rust
#[cfg(target_os = "windows")]
pub fn toggle_autostart(app_name: &str, enable: bool) -> Result<(), std::io::Error> {
    let hkcu = winreg::RegKey::predef(winreg::enums::HKEY_CURRENT_USER);
    let (key, _) = hkcu.create_subkey(r"Software\Microsoft\Windows\CurrentVersion\Run")?;
    if enable {
        let exe = std::env::current_exe()?;
        key.set_value(app_name, &exe.to_string_lossy().as_ref())?;
    } else {
        let _ = key.delete_value(app_name);
    }
    Ok(())
}
```
