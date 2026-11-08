# Đặc Tả Kỹ Thuật Chính Thức: Tauri v2 Core API (Dành Cho AI Offline)

> **MỤC ĐÍCH DÀNH CHO AI:** Tài liệu này cung cấp quy chuẩn kỹ thuật (Specification), chữ ký hàm (Signatures) và kiến trúc chính thức của **Tauri v2** để AI phân tích cú pháp và tự động sinh mã nguồn chính xác 100% khi không có kết nối internet.

---

## 1. Khởi Tạo Ứng Dụng (Application Runtime Lifecycle)

### 1.1 Khởi Tạo Builder & Setup Hook
Ứng dụng Tauri v2 bắt đầu bằng `tauri::Builder::default()`. Mọi khởi tạo phụ thuộc và tài nguyên cấp thấp được thực hiện trong hàm closure `.setup()`:

```rust
use tauri::Manager;

pub fn run() {
    tauri::Builder::default()
        // 1. Hook khởi tạo hệ thống
        .setup(|app: &mut tauri::App| {
            // Lấy AppHandle để dispatch tác vụ ngầm
            let handle = app.handle();

            // Đưa AppState vào bộ chứa Dependency Injection của Tauri
            app.manage(MyState::new());

            Ok(())
        })
        // 2. Đăng ký các IPC Commands
        .invoke_handler(tauri::generate_handler![
            my_command_one,
            my_command_two
        ])
        // 3. Chạy runtime loop
        .run(tauri::generate_context!())
        .expect("Lỗi chạy ứng dụng Tauri");
}
```

---

## 2. Quy Chuẩn Thiết Kế IPC Command (`#[tauri::command]`)

### 2.1 Quy Tắc Tham Số & Kiểu Trả Về
1. **Tham số từ Frontend:** Được deserialize tự động từ JSON payload. Tên tham số trong TypeScript phải trùng với tên tham số trong Rust (nếu dùng `camelCase` trên JS, Tauri tự map sang `snake_case` trong Rust).
2. **State Injection:** Dùng `tauri::State<'_, T>`. `T` phải được đăng ký trước bằng `app.manage(T)`.
3. **AppHandle & Window Injection:** Có thể nhận trực tiếp `app: tauri::AppHandle` hoặc `window: tauri::WebviewWindow` làm tham số của command.
4. **Kiểu trả về:** **BẮT BUỘC** trả về `Result<T, E>` trong đó:
   - `T` phải implement `serde::Serialize`.
   - `E` thường là `String` hoặc custom struct implement `serde::Serialize` (để frontend bắt được trong block `catch(err)`).

```rust
use tauri::{AppHandle, State, WebviewWindow};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct CommandOutput {
    pub success: bool,
    pub message: String,
}

#[derive(Deserialize)]
pub struct CommandInput {
    pub task_name: String,
    pub timeout_seconds: u32,
}

#[tauri::command]
pub async fn execute_task(
    input: CommandInput,
    state: State<'_, MyState>,
    app: AppHandle,
    window: WebviewWindow,
) -> Result<CommandOutput, String> {
    // Logic bất đồng bộ
    state.process(&input.task_name).map_err(|e| e.to_string())?;

    Ok(CommandOutput {
        success: true,
        message: format!("Đã hoàn thành task {}", input.task_name),
    })
}
```

---

## 3. Quản Lý Trạng Thái Chia Sẻ (State Management)

AppState trong Tauri được chia sẻ an toàn qua đa luồng (Thread-safe).
* Nếu chỉ đọc (Read-heavy): Dùng `tokio::sync::RwLock` hoặc `std::sync::RwLock`.
* Nếu ghi thường xuyên (Write-heavy / Counter): Dùng `std::sync::Mutex` hoặc `tokio::sync::Mutex`.

```rust
use std::sync::Mutex;
use std::path::PathBuf;

pub struct AppState {
    pub base_dir: PathBuf,
    pub session_token: Mutex<Option<String>>,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            base_dir: PathBuf::from("storage"),
            session_token: Mutex::new(None),
        }
    }
}
```

---

## 4. Thao Tác Cửa Sổ (WebviewWindow API)

Trong Tauri v2, cửa sổ có giao diện web được đại diện bởi kiểu **`tauri::WebviewWindow`**.

### 4.1 Lấy Tham Chiếu Cửa Sổ
```rust
use tauri::{AppHandle, Manager};

// Lấy cửa sổ chính có nhãn là "main"
if let Some(window) = app.get_webview_window("main") {
    // Ẩn/Hiện
    let _ = window.show();
    let _ = window.hide();

    // Focus & Restore
    let _ = window.unminimize();
    let _ = window.set_focus();

    // Vị trí & Kích thước
    let _ = window.center();
    let _ = window.set_size(tauri::Size::Logical(tauri::LogicalSize { width: 1280.0, height: 800.0 }));

    // Lấy HWND nguyên bản trên Windows (Dùng cho Win32 API)
    #[cfg(target_os = "windows")]
    if let Ok(hwnd) = window.hwnd() {
        let raw_hwnd: isize = hwnd.0 as isize;
        // Gọi Windows API...
    }
}
```

---

## 5. Hệ Thống Sự Kiện (Event System)

Tauri v2 sử dụng trait `tauri::Emitter` và `tauri::Listener`.

### 5.1 Backend Phát Sự Kiện (Emit)
```rust
use tauri::Emitter;

// 1. Phát tới toàn bộ các cửa sổ trong ứng dụng
app.emit("global-event", "Dữ liệu dạng chuỗi hoặc struct Serialize")?;

// 2. Chỉ phát tới một cửa sổ cụ thể
if let Some(window) = app.get_webview_window("main") {
    window.emit("window-specific-event", serde_json::json!({ "status": "ready" }))?;
}
```

### 5.2 Backend Lắng Nghe Sự Kiện (Listen)
```rust
use tauri::Listener;

app.listen("frontend-ping", |event| {
    println!("Nhận được payload: {:?}", event.payload());
});
```

---

## 6. Frontend IPC Contract Chuẩn

Tệp TypeScript phía client gọi vào các command đã định nghĩa:

```typescript
import { invoke } from '@tauri-apps/api/core'
import { listen, type UnlistenFn } from '@tauri-apps/api/event'

// 1. Gọi Command có kiểu dữ liệu chặt chẽ
interface TaskResult {
  success: boolean
  message: string
}

export async function runTask(taskName: string): Promise<TaskResult> {
  return await invoke<TaskResult>('execute_task', {
    input: {
      taskName: taskName, // Tự động serialize sang struct CommandInput
      timeoutSeconds: 30
    }
  })
}

// 2. Đăng ký lắng nghe sự kiện kèm hàm hủy (unlisten)
export async function subscribeToProgress(callback: (data: any) => void): Promise<UnlistenFn> {
  return await listen('download-progress', (event) => {
    callback(event.payload)
  })
}
```
