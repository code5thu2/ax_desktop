# Bảng Tra Cứu Chống Hallucination: Tauri v1 vs Tauri v2 (Dành Cho AI Offline)

> **MỤC ĐÍCH DÀNH CHO AI:** Tập tin này chứa các quy tắc bắt buộc để AI không viết nhầm code **Tauri v1 (đã lỗi thời)** sang dự án **Tauri v2**. Dữ liệu huấn luyện của các mô hình LLM thường chứa rất nhiều code v1, dẫn đến việc sinh ra mã nguồn không biên dịch được. Khi code trên máy offline, AI **BẮT BUỘC TUÂN THỦ** các quy tắc dưới đây.

---

## 1. Bảng Đối Chiếu Breaking Changes Giữa Tauri v1 & Tauri v2

| Thành phần | ❌ Tauri v1 (ĐÃ BỎ - CẤM DÙNG) | ✅ Tauri v2 (BẮT BUỘC DÙNG) |
| :--- | :--- | :--- |
| **Frontend IPC Package** | `import { invoke } from '@tauri-apps/api/tauri'` | `import { invoke } from '@tauri-apps/api/core'` |
| **System Tray** | `tauri::SystemTray::new()` | `tauri::tray::TrayIconBuilder::new()` |
| **Tray Menu** | `tauri::SystemTrayMenu::new()` | `tauri::menu::Menu::with_items(app, &[...])` |
| **Tray Menu Item** | `tauri::CustomMenuItem::new("id", "label")` | `tauri::menu::MenuItem::with_id(app, "id", "label", true, None)` |
| **Tray Event** | `SystemTrayEvent::LeftClick` | `TrayIconEvent::Click { button: MouseButton::Left, .. }` |
| **Broadcast Event** | `app.emit_all("event", payload)` | `app.emit("event", payload)` |
| **Window Event** | `window.emit_all("event", payload)` | `window.emit("event", payload)` |
| **Window Object** | `tauri::Window` cho mọi thứ | Phân tách `WebviewWindow` (có UI) và `Window` (chỉ frame) |
| **Lấy Cửa Sổ** | `app.get_window("main")` | `app.get_webview_window("main")` |
| **Config `allowlist`** | `"tauri": { "allowlist": { "all": true } }` | ĐÃ BỎ HOÀN TOÀN. Dùng hệ thống **Capabilities / Permissions** |
| **Tauri Core Crates** | `tauri::api::*` (dialog, path, fs...) | Chuyển thành các plugin riêng hoặc tự viết hàm Rust thuần |

---

## 2. Quy Tắc Code Mẫu: System Tray Trong Tauri v2

### ❌ KHÔNG ĐƯỢC VIẾT (Tauri v1 cũ):
```rust
// CẤM: Không tồn tại trong Tauri v2!
let tray_menu = SystemTrayMenu::new().add_item(CustomMenuItem::new("quit", "Quit"));
let system_tray = SystemTray::new().with_menu(tray_menu);
tauri::Builder::default().system_tray(system_tray)...
```

### ✅ BẮT BUỘC VIẾT (Tauri v2 chuẩn):
```rust
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent};
use tauri::Manager;

// Trong hàm setup(app):
let item_show = MenuItem::with_id(app, "show", "Mở ứng dụng", true, None::<&str>)?;
let item_quit = MenuItem::with_id(app, "quit", "Thoát", true, None::<&str>)?;
let tray_menu = Menu::with_items(app, &[&item_show, &item_quit])?;

let _tray = TrayIconBuilder::new()
    .icon(app.default_window_icon().unwrap().clone())
    .menu(&tray_menu)
    .show_menu_on_left_click(false)
    .on_menu_event(|app, event| match event.id.as_ref() {
        "show" => {
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.show();
                let _ = w.set_focus();
            }
        }
        "quit" => app.exit(0),
        _ => {}
    })
    .on_tray_icon_event(|tray, event| {
        if let TrayIconEvent::Click { button: MouseButton::Left, button_state: MouseButtonState::Up, .. } = event {
            let app = tray.app_handle();
            if let Some(w) = app.get_webview_window("main") {
                let _ = w.show();
                let _ = w.set_focus();
            }
        }
    })
    .build(app)?;
```

---

## 3. Quy Tắc Code Mẫu: Window Event & Close-to-Tray

### ❌ KHÔNG ĐƯỢC VIẾT:
```rust
// CẤM: on_window_event không nhận Closure trực tiếp làm crash ownership
window.on_window_event(|event| match event { ... });
```

### ✅ BẮT BUỘC VIẾT:
```rust
// Clone window handle trước khi đưa vào on_window_event
if let Some(window) = app.get_webview_window("main") {
    let win_clone = window.clone();
    window.on_window_event(move |event| {
        if let tauri::WindowEvent::CloseRequested { api, .. } = event {
            api.prevent_close(); // Chặn đóng hoàn toàn
            let _ = win_clone.hide(); // Ẩn xuống system tray
        }
    });
}
```

---

## 4. Quy Tắc Code Mẫu: Frontend IPC Trong Tauri v2

### ❌ KHÔNG ĐƯỢC VIẾT:
```typescript
// CẤM: Gói @tauri-apps/api/tauri không còn tồn tại trong Tauri v2
import { invoke } from '@tauri-apps/api/tauri'
```

### ✅ BẮT BUỘC VIẾT:
```typescript
// Chuẩn Tauri v2:
import { invoke } from '@tauri-apps/api/core'
import { listen, emit } from '@tauri-apps/api/event'
```

---

## 5. Quy Tắc Cấu Trúc File Cấu Hình `tauri.conf.json`

Trong Tauri v2, khối `"tauri"` gốc đã được đổi thành `"app"` và loại bỏ `"allowlist"`:

```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-config-schema/schema.json",
  "productName": "MyApp",
  "version": "1.0.0",
  "identifier": "com.company.myapp",
  "build": {
    "devUrl": "http://localhost:5173",
    "frontendDist": "../frontend/dist"
  },
  "app": {
    "windows": [
      {
        "title": "MyApp",
        "width": 1200,
        "height": 800,
        "center": true
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": ["nsis"]
  }
}
```
