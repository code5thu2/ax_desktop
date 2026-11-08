# Sổ Tay Tra Cứu Toàn Diện: Lập Trình Rust & Tauri v2 (Offline Handbook)

> **Mục đích sử dụng:** Sổ tay tra cứu tại chỗ dành cho lập trình viên làm việc trên máy tính **hoàn toàn không có Internet**. Bao gồm đầy đủ cấu trúc cú pháp, API signatures, mẫu code giải quyết vấn đề thực tế (copy-paste dùng ngay) cho **Tauri v2**, **Rust Core**, **Tokio Async**, **Serde JSON** và **Win32 Platform**.

---

## Mục Lục Tra Cứu Nhanh

1. [Tauri v2 Backend API: Commands, State & Window](#1-tauri-v2-backend-api)
2. [Tauri v2 System Tray & Event Bus](#2-tauri-v2-system-tray--event-bus)
3. [Rust Core & Tokio Async Cho Desktop App](#3-rust-core--tokio-async)
4. [Serde & JSON Xử Lý Dữ Liệu](#4-serde--json-xử-lý-dữ-liệu)
5. [Tương Tác Hệ Điều Hành Windows Cấp Thấp](#5-tương-tác-hệ-điều-hành-windows-cấp-thấp)
6. [Frontend TypeScript IPC Cheatsheet](#6-frontend-typescript-ipc-cheatsheet)
7. [Tra Cứu Cấu Hình `tauri.conf.json`](#7-tra-cứu-cấu-hình-tauriconfjson)

---

## 1. Tauri v2 Backend API

### 1.1 Khởi Tạo App & Tiêm Phụ Thuộc (Dependency Injection / State)

Tauri v2 quản lý trạng thái chia sẻ (AppState) thông qua hàm `app.manage()`. State được bảo vệ đa luồng bằng `std::sync::Mutex` hoặc `tokio::sync::RwLock`.

```rust
use tauri::Manager;
use std::sync::Mutex;

// 1. Định nghĩa cấu trúc AppState
pub struct AppState {
    pub db_path: String,
    pub counter: Mutex<i32>,
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // 2. Khởi tạo và đưa vào AppState
            let state = AppState {
                db_path: "storage/data.json".to_string(),
                counter: Mutex::new(0),
            };
            app.manage(state);

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_counter,
            increment_counter
        ])
        .run(tauri::generate_context!())
        .expect("Lỗi chạy Tauri app");
}
```

---

### 1.2 Định Nghĩa IPC Commands (`#[tauri::command]`)

Các hàm command phơi bày cho frontend gọi thông qua IPC.

#### A. Command Đồng Bộ & Đọc/Ghi State
```rust
use tauri::State;

// Trả về dữ liệu thành công
#[tauri::command]
pub fn get_counter(state: State<'_, AppState>) -> Result<i32, String> {
    let count = state.counter.lock().map_err(|e| e.to_string())?;
    Ok(*count)
}

// Nhận tham số từ frontend và cập nhật state
#[tauri::command]
pub fn increment_counter(amount: i32, state: State<'_, AppState>) -> Result<i32, String> {
    let mut count = state.counter.lock().map_err(|e| e.to_string())?;
    *count += amount;
    Ok(*count)
}
```

#### B. Command Bất Đồng Bộ (Async Command & Non-Blocking)
Khi cần gọi HTTP request, đọc file nặng hoặc tác vụ tốn thời gian, **bắt buộc** dùng `async fn` để không làm đơ giao diện UI:

```rust
#[tauri::command]
pub async fn fetch_remote_data(url: String) -> Result<String, String> {
    // Chạy bất đồng bộ, không lock Main UI Thread
    let response = reqwest::get(&url)
        .await
        .map_err(|e| format!("Network error: {}", e))?
        .text()
        .await
        .map_err(|e| format!("Read error: {}", e))?;

    Ok(response)
}
```

---

### 1.3 Điều Khiển Cửa Sổ (Window Lifecycle)

Lấy tham chiếu tới cửa sổ (`WebviewWindow`) từ `AppHandle` hoặc trực tiếp từ Command:

```rust
use tauri::{AppHandle, Manager, WebviewWindow};

#[tauri::command]
pub fn toggle_window_visibility(app: AppHandle) -> Result<(), String> {
    if let Some(window) = app.get_webview_window("main") {
        if window.is_visible().unwrap_or(false) {
            window.hide().map_err(|e| e.to_string())?;
        } else {
            window.show().map_err(|e| e.to_string())?;
            window.unminimize().map_err(|e| e.to_string())?;
            window.set_focus().map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

// Các thao tác cửa sổ thông dụng:
// window.maximize()?;        // Phóng to hết cỡ
// window.unmaximize()?;      // Khôi phục kích thước
// window.minimize()?;        // Thu nhỏ xuống taskbar
// window.set_fullscreen(true)?; // Toàn màn hình
// window.center()?;          // Căn giữa màn hình
```

---

## 2. Tauri v2 System Tray & Event Bus

### 2.1 Tạo Khay Hệ Thống (System Tray) & Menu Chuẩn Tauri v2

```rust
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::Manager;

pub fn setup_tray(app: &mut tauri::App) -> Result<(), Box<dyn std::error::Error>> {
    // 1. Tạo menu items
    let item_show = MenuItem::with_id(app, "show", "Mở ứng dụng", true, None::<&str>)?;
    let item_hide = MenuItem::with_id(app, "hide", "Ẩn ứng dụng", true, None::<&str>)?;
    let item_quit = MenuItem::with_id(app, "quit", "Thoát hoàn toàn", true, None::<&str>)?;

    // 2. Gom vào Menu
    let tray_menu = Menu::with_items(app, &[&item_show, &item_hide, &item_quit])?;

    // 3. Khởi tạo Tray Icon
    if let Some(icon) = app.default_window_icon() {
        TrayIconBuilder::new()
            .icon(icon.clone())
            .menu(&tray_menu)
            .show_menu_on_left_click(false) // Chuột phải mở menu, chuột trái xử lý riêng
            .on_menu_event(|app, event| match event.id.as_ref() {
                "show" => {
                    if let Some(w) = app.get_webview_window("main") {
                        let _ = w.show();
                        let _ = w.unminimize();
                        let _ = w.set_focus();
                    }
                }
                "hide" => {
                    if let Some(w) = app.get_webview_window("main") {
                        let _ = w.hide();
                    }
                }
                "quit" => {
                    app.exit(0);
                }
                _ => {}
            })
            .on_tray_icon_event(|tray, event| {
                // Nhấp chuột trái vào tray icon -> Bật mở cửa sổ
                if let TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. } = event {
                    let app = tray.app_handle();
                    if let Some(w) = app.get_webview_window("main") {
                        let _ = w.show();
                        let _ = w.unminimize();
                        let _ = w.set_focus();
                    }
                }
            })
            .build(app)?;
    }
    Ok(())
}
```

---

### 2.2 Event Bus Hai Chiều (Rust $\leftrightarrow$ Frontend)

Dùng khi backend muốn chủ động đẩy thông báo xuống UI (ví dụ: tiến trình tải file, trạng thái kết nối).

#### Backend Bắn Sự Kiện (Emit)
```rust
use tauri::{AppHandle, Emitter};
use serde::Serialize;

#[derive(Clone, Serialize)]
struct DownloadProgress {
    percentage: u32,
    speed: String,
}

// Bắn sự kiện tới toàn bộ app
pub fn notify_progress(app: &AppHandle, percent: u32) {
    let payload = DownloadProgress {
        percentage: percent,
        speed: "1.2 MB/s".into(),
    };
    let _ = app.emit("download-progress", payload);
}
```

#### Frontend Lắng Nghe Sự Kiện (Listen)
```typescript
import { listen } from '@tauri-apps/api/event'

interface DownloadProgress {
  percentage: number
  speed: string
}

// Bắt đầu lắng nghe
const unlisten = await listen<DownloadProgress>('download-progress', (event) => {
  console.log(`Tiến độ: ${event.payload.percentage}% - Tốc độ: ${event.payload.speed}`)
})

// Khi component unmount:
// unlisten()
```

---

## 3. Rust Core & Tokio Async

### 3.1 Tokio Async Cheatsheet: Chạy Tác Vụ Ngầm

```rust
use tokio::time::{sleep, Duration};

// 1. Tạo tác vụ chạy song song trong background (spawn)
pub fn start_background_worker() {
    tokio::spawn(async move {
        loop {
            // Ngủ không làm đơ thread
            sleep(Duration::from_secs(10)).await;
            println!("Đang quét dữ liệu định kỳ...");
        }
    });
}

// 2. Thực hiện với Timeout (Tránh bị treo vĩnh viễn)
pub async fn run_with_timeout() -> Result<String, String> {
    let task = async {
        sleep(Duration::from_secs(2)).await;
        "Hoàn tất"
    };

    match tokio::time::timeout(Duration::from_secs(5), task).await {
        Ok(res) => Ok(res.to_string()),
        Err(_) => Err("Hết thời gian chờ (Timeout 5s)!".into()),
    }
}
```

---

### 3.2 Giao Tiếp Giữa Các Luồng Bằng Kênh (MPSC Channel)

```rust
use tokio::sync::mpsc;

#[derive(Debug)]
pub enum WorkerJob {
    ProcessItem(String),
    Shutdown,
}

pub fn create_job_queue() -> mpsc::Sender<WorkerJob> {
    let (tx, mut rx) = mpsc::channel::<WorkerJob>(32);

    tokio::spawn(async move {
        while let Some(job) = rx.recv().await {
            match job {
                WorkerJob::ProcessItem(data) => println!("Đang xử lý: {}", data),
                WorkerJob::Shutdown => break,
            }
        }
    });

    tx // Trả về Sender để nơi khác gửi lệnh vào
}
```

---

## 4. Serde & JSON Xử Lý Dữ Liệu

### 4.1 Định Nghĩa Struct Linh Hoạt

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")] // Chuyển field_name thành fieldName
pub struct AppConfig {
    pub server_url: String,

    #[serde(default = "default_port")] // Giá trị mặc định nếu JSON thiếu trường
    pub port: u16,

    #[serde(skip_serializing_if = "Option::is_none")] // Không xuất ra JSON nếu là None
    pub auth_token: Option<String>,

    #[serde(rename = "type")] // Đổi tên trường bị trùng keyword của Rust
    pub item_type: String,
}

fn default_port() -> u16 {
    8080
}
```

### 4.2 Thao Tác Parse & Tạo Chuỗi JSON Nhanh

```rust
use serde_json::{json, Value};

// 1. Parse từ chuỗi
pub fn parse_data(raw_str: &str) -> Result<AppConfig, serde_json::Error> {
    let config: AppConfig = serde_json::from_str(raw_str)?;
    Ok(config)
}

// 2. Chuyển struct thành chuỗi định dạng đẹp
pub fn to_pretty(config: &AppConfig) -> Result<String, serde_json::Error> {
    serde_json::to_string_pretty(config)
}

// 3. Tạo JSON động dạng Ad-hoc
pub fn build_dynamic_json() -> Value {
    json!({
        "status": "success",
        "code": 200,
        "records": [
            { "id": 1, "name": "Item A" },
            { "id": 2, "name": "Item B" }
        ],
        "meta": { "total": 2 }
    })
}
```

---

## 5. Tương Tác Hệ Điều Hành Windows Cấp Thấp

Các đoạn mã sau sử dụng Windows API trực tiếp mà không cần phụ thuộc crate nặng.

### 5.1 Single Instance (Chống Mở 2 App Bằng Win32 Mutex)

```rust
#[cfg(target_os = "windows")]
pub struct SingleInstanceGuard {
    handle: windows_sys::Win32::Foundation::HANDLE,
}

#[cfg(target_os = "windows")]
impl SingleInstanceGuard {
    pub fn acquire(mutex_name: &str) -> Result<Self, &'static str> {
        use std::ffi::OsStr;
        use std::os::windows::ffi::OsStrExt;
        use windows_sys::Win32::Foundation::GetLastError;
        use windows_sys::Win32::System::Threading::CreateMutexW;

        let wide: Vec<u16> = OsStr::new(mutex_name).encode_wide().chain(Some(0)).collect();
        unsafe {
            let handle = CreateMutexW(std::ptr::null(), 1, wide.as_ptr());
            if handle == 0 || GetLastError() == 183 { // ERROR_ALREADY_EXISTS = 183
                return Err("Ứng dụng đã đang chạy trong một phiên khác.");
            }
            Ok(Self { handle })
        }
    }
}

#[cfg(target_os = "windows")]
impl Drop for SingleInstanceGuard {
    fn drop(&mut self) {
        unsafe {
            windows_sys::Win32::System::Threading::ReleaseMutex(self.handle);
            windows_sys::Win32::Foundation::CloseHandle(self.handle);
        }
    }
}
```

---

### 5.2 Khởi Động Cùng Windows (Ghi Registry Không Cần Quyền Admin)

```rust
#[cfg(target_os = "windows")]
use winreg::enums::*;
#[cfg(target_os = "windows")]
use winreg::RegKey;

pub fn set_autostart(app_name: &str, enable: bool) -> Result<(), std::io::Error> {
    #[cfg(target_os = "windows")]
    {
        let hkcu = RegKey::predef(HKEY_CURRENT_USER);
        let path = r"Software\Microsoft\Windows\CurrentVersion\Run";
        let (key, _) = hkcu.create_subkey(path)?;

        if enable {
            let exe_path = std::env::current_exe()?;
            key.set_value(app_name, &exe_path.to_string_lossy().as_ref())?;
        } else {
            let _ = key.delete_value(app_name);
        }
    }
    Ok(())
}

pub fn is_autostart_enabled(app_name: &str) -> bool {
    #[cfg(target_os = "windows")]
    {
        let hkcu = RegKey::predef(HKEY_CURRENT_USER);
        if let Ok(key) = hkcu.open_subkey(r"Software\Microsoft\Windows\CurrentVersion\Run") {
            return key.get_value::<String, _>(app_name).is_ok();
        }
    }
    false
}
```

---

### 5.3 Thanh Tiêu Đề Tối DWM (Windows 11 Dark Titlebar)

```rust
#[cfg(target_os = "windows")]
pub fn set_dark_titlebar(hwnd: isize, dark: bool) -> Result<(), ()> {
    use std::ffi::c_void;
    use windows_sys::Win32::Graphics::Dwm::DwmSetWindowAttribute;

    const DWMWA_USE_IMMERSIVE_DARK_MODE: u32 = 20; // Win11 build 22000+
    let value: i32 = if dark { 1 } else { 0 };

    unsafe {
        let hr = DwmSetWindowAttribute(
            hwnd as _,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            &value as *const _ as *const c_void,
            std::mem::size_of::<i32>() as u32,
        );
        if hr == 0 { Ok(()) } else { Err(()) }
    }
}
```

---

## 6. Frontend TypeScript IPC Cheatsheet

### 6.1 Gọi Command Với Tham Số & Bắt Lỗi
```typescript
import { invoke } from '@tauri-apps/api/core'

interface UserDTO {
  id: string
  name: string
  email: string
}

async function loadUser(userId: string): Promise<UserDTO | null> {
  try {
    const user = await invoke<UserDTO>('get_user_by_id', {
      userId: userId // Tên tham số khớp với tham số trong fn Rust
    })
    return user
  } catch (error) {
    console.error('IPC Command Error:', error)
    return null
  }
}
```

---

## 7. Tra Cứu Cấu Hình `tauri.conf.json`

Mẫu cấu hình tối ưu sẵn cho ứng dụng Desktop hiện đại:

```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-config-schema/schema.json",
  "productName": "MyDesktopApp",
  "version": "1.0.0",
  "identifier": "com.company.desktopapp",
  "build": {
    "beforeDevCommand": "npm run dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../frontend/dist"
  },
  "app": {
    "windows": [
      {
        "title": "My Desktop App",
        "width": 1200,
        "height": 780,
        "minWidth": 900,
        "minHeight": 600,
        "center": true,
        "resizable": true,
        "decorations": true,
        "transparent": false
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": ["nsis"],
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/icon.ico"
    ],
    "windows": {
      "webviewInstallMode": {
        "type": "embedBootstrapper"
      },
      "nsis": {
        "installMode": "currentUser",
        "languages": ["English"]
      }
    }
  }
}
```
