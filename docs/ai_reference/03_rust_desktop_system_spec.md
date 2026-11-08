# Đặc Tả Kỹ Thuật Rust Desktop: Async, Storage & Win32 (Dành Cho AI Offline)

> **MỤC ĐÍCH DÀNH CHO AI:** Tài liệu này cung cấp các pattern và đặc tả kỹ thuật chuẩn của **Rust**, **Tokio** và **Windows System Calls** để AI tự sinh mã nguồn xử lý logic nền, lưu trữ dữ liệu an toàn và tương tác hệ điều hành trên máy offline.

---

## 1. Xử Lý Lỗi (Error Handling Pattern) Cho Tauri IPC

Mọi lỗi nội bộ của các Crates nghiệp vụ phải được định nghĩa rõ ràng bằng `thiserror`, và được chuyển đổi thành chuỗi thân thiện hoặc struct trước khi trả về Frontend qua IPC:

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Lỗi I/O tập tin: {0}")]
    Io(#[from] std::io::Error),

    #[error("Lỗi phân tích JSON: {0}")]
    Serialization(#[from] serde_json::Error),

    #[error("Lỗi mạng: {0}")]
    Network(#[from] reqwest::Error),

    #[error("Lỗi nghiệp vụ: {0}")]
    Business(String),
}

// Chuyển đổi lỗi sang Result trả về cho Tauri Command
impl From<AppError> for String {
    fn from(err: AppError) -> Self {
        err.to_string()
    }
}
```

---

## 2. Tokio Async Trong Môi Trường Tauri

Tauri v2 tích hợp sẵn Tokio runtime (`tauri::async_runtime`). AI cần tuân thủ 2 quy tắc vàng:

### Quy Tắc 1: Không Gọi Tác Vụ Blocking Trong `async fn`
Nếu tác vụ là đọc/ghi file lớn, mã hóa nặng hoặc gọi Win32 API đồng bộ, **PHẢI** bọc trong `tokio::task::spawn_blocking`:

```rust
#[tauri::command]
pub async fn compute_heavy_hash(file_path: String) -> Result<String, String> {
    // Chuyển sang Thread Pool riêng của Tokio, không block Async Executor
    let hash = tokio::task::spawn_blocking(move || {
        // Thực hiện tác vụ I/O nặng hoặc tính toán CPU-bound
        std::fs::read_to_string(file_path).map(|content| format!("hash_{}", content.len()))
    })
    .await
    .map_err(|e| e.to_string())?
    .map_err(|e| e.to_string())?;

    Ok(hash)
}
```

---

## 3. Lưu Trữ Dữ Liệu An Toàn Tuyệt Đối (Atomic Storage)

Trên môi trường desktop, file cấu hình và cơ sở dữ liệu JSON cục bộ **BẮT BUỘC** phải được ghi bằng kỹ thuật Atomic Write kết hợp Retry loop để không bị file-lock trên Windows:

```rust
use serde::Serialize;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};

pub fn write_json_atomic<T: Serialize>(path: &Path, value: &T) -> Result<(), std::io::Error> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent)?;
    }

    // 1. Sao lưu .bak trước khi ghi
    let bak_path = PathBuf::from(format!("{}.bak", path.to_string_lossy()));
    if path.exists() {
        let _ = fs::copy(path, &bak_path);
    }

    // 2. Ghi ra file .tmp và flush cứng xuống đĩa
    let tmp_path = PathBuf::from(format!("{}.tmp", path.to_string_lossy()));
    {
        let mut file = File::create(&tmp_path)?;
        let json_data = serde_json::to_string_pretty(value)?;
        file.write_all(json_data.as_bytes())?;
        file.sync_all()?;
    }

    // 3. Rename nguyên tử với cơ chế thử lại (Backoff retry loop)
    let mut last_err = None;
    for _ in 0..5 {
        match fs::rename(&tmp_path, path) {
            Ok(_) => {
                last_err = None;
                break;
            }
            Err(e) => {
                last_err = Some(e);
                std::thread::sleep(std::time::Duration::from_millis(50));
            }
        }
    }

    if let Some(e) = last_err {
        let _ = fs::copy(&tmp_path, path);
        let _ = fs::remove_file(&tmp_path);
        return Err(e);
    }

    Ok(())
}
```

---

## 4. Tương Tác Win32 API Chuẩn Xác (Không Dùng Thư Viện Cũ)

Khi tương tác với Windows Registry hoặc Named Mutex, AI phải sử dụng đúng các API tiêu chuẩn sau:

### 4.1 Win32 Named Mutex (Single Instance)
* API: `CreateMutexW` từ `windows_sys::Win32::System::Threading`
* Kiểm tra `GetLastError() == 183` (`ERROR_ALREADY_EXISTS`)
* Luôn `impl Drop` để gọi `ReleaseMutex` và `CloseHandle`.

### 4.2 Windows Registry Autostart
* Khóa: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
* Sử dụng `std::env::current_exe()` để lấy đường dẫn thực thi của chính app.
* Không ghi vào `HKEY_LOCAL_MACHINE` để tránh bị chặn bởi UAC.
