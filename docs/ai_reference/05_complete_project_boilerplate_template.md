# Bộ Khung Khởi Tạo Hoàn Chỉnh: Turnkey Boilerplate Template (Dành Cho AI Offline)

> **MỤC ĐÍCH DÀNH CHO AI:** Khi được yêu cầu tạo một dự án mới hoàn toàn từ đầu (from scratch) trên máy không có mạng, AI chỉ cần sao chép các tệp cấu hình và mã nguồn tối thiểu dưới đây để có ngay một ứng dụng **Headless-First Rust + Tauri v2** hoạt động được ngay lập tức, không lỗi thiếu file hay sai cấu trúc.

---

## 1. Cấu Trúc Thư Mục Chuẩn Bắt Buộc

```text
my-project/
├── Cargo.toml
├── crates/
│   ├── shared-types/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   └── app-core/
│       ├── Cargo.toml
│       └── src/lib.rs
├── apps/
│   └── desktop/
│       ├── Cargo.toml
│       ├── tauri.conf.json
│       └── src/
│           ├── main.rs
│           ├── lib.rs
│           └── commands.rs
└── frontend/
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── App.vue
        └── services/nativeBridge.ts
```

---

## 2. Mã Nguồn Các Tệp Cấu Hình Gốc (Root & Crates)

### Tệp 1: Root `Cargo.toml`
```toml
[workspace]
members = [
    "crates/shared-types",
    "crates/app-core",
    "apps/desktop"
]
resolver = "2"

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
thiserror = "2.0"
ts-rs = { version = "10.1", features = ["serde-compat"] }
tauri = { version = "2.12" }

[profile.dev]
debug = 1

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
panic = "abort"
strip = true
```

### Tệp 2: `crates/shared-types/Cargo.toml`
```toml
[package]
name = "shared-types"
version = "0.1.0"
edition = "2021"

[dependencies]
serde = { workspace = true }
serde_json = { workspace = true }
ts-rs = { workspace = true }
```

### Tệp 3: `crates/shared-types/src/lib.rs`
```rust
use serde::{Deserialize, Serialize};
use ts_rs::TS;

#[derive(Debug, Clone, Serialize, Deserialize, TS)]
#[serde(rename_all = "camelCase")]
#[ts(export, export_to = "../../../frontend/src/types/generated/")]
pub struct AppInfo {
    pub app_name: String,
    pub version: String,
    pub is_online: bool,
}

#[cfg(test)]
mod tests {
    use super::*;
    use ts_rs::TS;

    #[test]
    fn export_bindings() {
        AppInfo::export().expect("Failed to export AppInfo");
    }
}
```

### Tệp 4: `crates/app-core/Cargo.toml`
```toml
[package]
name = "app-core"
version = "0.1.0"
edition = "2021"

[dependencies]
shared-types = { path = "../shared-types" }
serde = { workspace = true }
serde_json = { workspace = true }
thiserror = { workspace = true }
```

### Tệp 5: `crates/app-core/src/lib.rs`
```rust
use shared-types::AppInfo;

pub struct CoreService;

impl CoreService {
    pub fn new() -> Self {
        Self
    }

    pub fn get_info(&self) -> AppInfo {
        AppInfo {
            app_name: "Tauri Desktop Boilerplate".to_string(),
            version: "1.0.0".to_string(),
            is_online: false,
        }
    }
}
```

---

## 3. Mã Nguồn Desktop Shell (`apps/desktop`)

### Tệp 6: `apps/desktop/Cargo.toml`
```toml
[package]
name = "desktop"
version = "0.1.0"
edition = "2021"

[dependencies]
shared-types = { path = "../../crates/shared-types" }
app-core = { path = "../../crates/app-core" }
tauri = { workspace = true, features = ["tray-icon"] }
serde = { workspace = true }
serde_json = { workspace = true }

[build-dependencies]
tauri-build = { version = "2", default-features = false }
```

### Tệp 7: `apps/desktop/src/main.rs`
```rust
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    desktop::run();
}
```

### Tệp 8: `apps/desktop/src/commands.rs`
```rust
use app_core::CoreService;
use shared_types::AppInfo;
use tauri::State;

pub struct AppState {
    pub service: CoreService,
}

impl AppState {
    pub fn new() -> Self {
        Self {
            service: CoreService::new(),
        }
    }
}

#[tauri::command]
pub fn get_app_info(state: State<'_, AppState>) -> Result<AppInfo, String> {
    Ok(state.service.get_info())
}
```

### Tệp 9: `apps/desktop/src/lib.rs`
```rust
pub mod commands;
use commands::AppState;
use tauri::Manager;

pub fn run() {
    tauri::Builder::default()
        .setup(|app| {
            app.manage(AppState::new());
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::get_app_info,
        ])
        .run(tauri::generate_context!())
        .expect("Failed to run app");
}
```

### Tệp 10: `apps/desktop/tauri.conf.json`
```json
{
  "$schema": "https://raw.githubusercontent.com/tauri-apps/tauri/dev/crates/tauri-config-schema/schema.json",
  "productName": "BoilerplateApp",
  "version": "1.0.0",
  "identifier": "com.local.boilerplate",
  "build": {
    "beforeDevCommand": "npm run dev",
    "devUrl": "http://localhost:5173",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../frontend/dist"
  },
  "app": {
    "windows": [
      {
        "title": "Boilerplate App",
        "width": 1024,
        "height": 720,
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

---

## 4. Frontend Isomorphic Bridge (`frontend/`)

### Tệp 11: `frontend/src/services/nativeBridge.ts`
```typescript
import type { AppInfo } from '@/types/generated/AppInfo'

export function isTauri(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}

export const nativeBridge = {
  async getAppInfo(): Promise<AppInfo> {
    if (isTauri()) {
      const { invoke } = await import('@tauri-apps/api/core')
      return await invoke<AppInfo>('get_app_info')
    } else {
      // Fallback khi chạy dev trên trình duyệt web thường
      return {
        appName: 'Mock Web App',
        version: '1.0.0-mock',
        isOnline: true,
      }
    }
  },
}
```
