# Tauri v2 Modular Workspace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển đổi kiến trúc dự án sang mô hình Headless-First Cargo Workspace với Tauri v2 (core v2.12.5), tách biệt hoàn toàn mã nguồn của các MCP server ra ngoài dự án, chuẩn hóa tầng backend Rust theo các crate chuyên biệt (`shared-types`, `win11-platform`, `mcp-core`, `apps/desktop`).

**Architecture:** Sử dụng kiến trúc Cargo Workspace đa Crate (theo chuẩn GitButler / Spacedrive). Lõi MCP Protocol và tầng Win32 Native chạy độc lập không phụ thuộc vào Tauri, dữ liệu được đồng bộ type sang TypeScript tự động qua `ts-rs`. Các server MCP hiện có được cấu hình nằm ở thư mục bên ngoài (`D:\AI_MCP\servers`) để làm mock test qua Stdio/HTTP.

**Tech Stack:** Rust 1.90.0, Tauri v2.12.5, `ts-rs`, `windows-sys` / `windows-rs`, `serde`, `tokio`, Vue 3, PrimeVue 4, Vite, `uv.exe`.

## Global Constraints

- Lõi Rust crate dùng `tauri = "2.12.5"`.
- Trình biên dịch sử dụng toolchain `1.90.0-x86_64-pc-windows-msvc`.
- Toàn bộ mã nguồn của các MCP Server (`excel`, `postgres`, `zalo`...) không được lưu trong repository này; chỉ giao tiếp qua mock runner trỏ ra thư mục ngoài (`MCP_SERVERS_DIR`).
- Mã nguồn giao diện Vue 3 + PrimeVue trong `frontend/` được giữ nguyên vẹn, chỉ bổ sung adapter IPC giao tiếp với Tauri Command.

## Review Focus

1. **Khởi động không bị phụ thuộc Python**: App Desktop mở lên tức thì không cần cài Python hay nạp runtime .NET CLR.
2. **Type Safety Rust <-> TypeScript**: Mọi thay đổi về Struct trong Rust tự động đồng bộ sang file `frontend/src/types/generated/mcp.ts`.
3. **Cô lập Subprocess an toàn**: Khi gọi test tool MCP server bên ngoài, tiến trình con không bị treo hoặc rò rỉ RAM (zombie process).
4. **Single Instance & System Tray**: Đảm bảo chỉ 1 phiên bản chạy duy nhất, đóng cửa sổ thu nhỏ xuống khay hệ thống mượt mà.
5. **Mock Test Runner độc lập**: Có thể chạy `cargo test` để test toàn bộ logic catalog và protocol mà không cần mở giao diện Webview.

---

### Task 1: Root Cargo Workspace & Crate `crates/shared-types`

**Files:**
- Create: `Cargo.toml` (Root workspace)
- Create: `crates/shared-types/Cargo.toml`
- Create: `crates/shared-types/src/lib.rs`
- Create: `crates/shared-types/tests/test_types.rs`

**Interfaces:**
- Produces: `shared_types::models::{PluginItem, ToolInfo, CatalogResponse, ClientInstallStatus, ToolExecuteRequest}`
- Produces: `ts-rs` export macro target: `../../frontend/src/types/generated/mcp.ts`

- [ ] **Step 1: Viết test kiểm tra serialization và export type của shared-types**

```rust
// crates/shared-types/tests/test_types.rs
use shared_types::models::{PluginItem, ToolInfo};

#[test]
fn test_plugin_item_serialization() {
    let item = PluginItem {
        id: "excel-mcp".to_string(),
        name: "Excel MCP Server".to_string(),
        version: "1.0.0".to_string(),
        enabled: true,
        installed: true,
        tools: vec![ToolInfo {
            name: "read_sheet".to_string(),
            description: "Read excel sheet".to_string(),
        }],
    };
    let json = serde_json::to_string(&item).expect("Failed to serialize");
    assert!(json.contains("excel-mcp"));
}
```

- [ ] **Step 2: Tạo `Cargo.toml` root workspace và crate `crates/shared-types/Cargo.toml`**

Root `Cargo.toml` định nghĩa workspace members:
```toml
[workspace]
members = [
    "crates/shared-types",
    "crates/win11-platform",
    "crates/mcp-core",
    "apps/desktop"
]
resolver = "2"

[workspace.dependencies]
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tokio = { version = "1.0", features = ["full"] }
thiserror = "1.0"
ts-rs = { version = "10.0", features = ["serde-compat"] }
```

- [ ] **Step 3: Triển khai các Structs trong `crates/shared-types/src/lib.rs`**
Triển khai `PluginItem`, `ToolInfo`, `CatalogResponse`, `ClientInstallStatus` kèm `#[derive(Serialize, Deserialize, TS)]` với cấu hình `#[ts(export, export_to = "../../frontend/src/types/generated/")]`.

- [ ] **Step 4: Chạy test kiểm tra**
Run: `cargo test -p shared-types`
Expected: PASS, sinh file TypeScript binding trong `frontend/src/types/generated/`.

- [ ] **Step 5: Commit**
```bash
git add Cargo.toml crates/shared-types
git commit -m "feat(types): create root cargo workspace and shared-types crate with ts-rs"
```

---

### Task 2: Crate `crates/win11-platform` (Windows 11 Native Integration)

**Files:**
- Create: `crates/win11-platform/Cargo.toml`
- Create: `crates/win11-platform/src/lib.rs`
- Create: `crates/win11-platform/src/dwm.rs`
- Create: `crates/win11-platform/src/single_instance.rs`
- Create: `crates/win11-platform/src/autostart.rs`
- Create: `crates/win11-platform/tests/test_platform.rs`

**Interfaces:**
- Produces: `win11_platform::dwm::apply_dark_titlebar(hwnd: isize, is_dark: bool) -> Result<(), String>`
- Produces: `win11_platform::single_instance::SingleInstanceGuard::acquire(name: &str) -> Result<SingleInstanceGuard, String>`
- Produces: `win11_platform::autostart::set_run_at_startup(app_name: &str, enable: bool) -> Result<(), String>`

- [ ] **Step 1: Viết test cho Single Instance Mutex guard**

```rust
// crates/win11-platform/tests/test_platform.rs
use win11_platform::single_instance::SingleInstanceGuard;

#[test]
fn test_single_instance_mutex() {
    let mutex_name = "MCP_Studio_Test_Mutex_12345";
    let guard1 = SingleInstanceGuard::acquire(mutex_name);
    assert!(guard1.is_ok(), "First acquisition must succeed");
    
    let guard2 = SingleInstanceGuard::acquire(mutex_name);
    assert!(guard2.is_err(), "Second acquisition must fail (already running)");
}
```

- [ ] **Step 2: Tạo `crates/win11-platform/Cargo.toml` với dependencies `windows-sys`**
Cấu hình link tới các API Win32: `Win32_Graphics_Dwm`, `Win32_System_Threading`, `Win32_System_Registry`.

- [ ] **Step 3: Triển khai các module `dwm.rs`, `single_instance.rs`, `autostart.rs`**
Triển khai hàm áp dụng `DWMWA_USE_IMMERSIVE_DARK_MODE`, `CreateMutexW`, và ghi Windows Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`.

- [ ] **Step 4: Chạy test kiểm tra**
Run: `cargo test -p win11-platform`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add crates/win11-platform
git commit -m "feat(platform): implement win11-platform crate with dwm, mutex, and registry autostart"
```

---

### Task 3: Crate `crates/mcp-core` (Catalog & External Mock Engine)

**Files:**
- Create: `crates/mcp-core/Cargo.toml`
- Create: `crates/mcp-core/src/lib.rs`
- Create: `crates/mcp-core/src/catalog.rs`
- Create: `crates/mcp-core/src/client.rs`
- Create: `crates/mcp-core/src/installer.rs`
- Create: `crates/mcp-core/src/mock_runner.rs`
- Create: `crates/mcp-core/tests/test_mcp_core.rs`

**Interfaces:**
- Consumes: `shared_types::models::*`
- Produces: `mcp_core::catalog::CatalogManager::load(path: &Path) -> Result<CatalogManager, Error>`
- Produces: `mcp_core::mock_runner::MockServerScanner::scan_external_dir(dir: &Path) -> Vec<PluginItem>`
- Produces: `mcp_core::client::StdioMcpClient::call_tool(server_path: &Path, tool: &str, args: Value) -> Result<Value, Error>`

- [ ] **Step 1: Viết test cho catalog manager và mock runner**

```rust
// crates/mcp-core/tests/test_mcp_core.rs
use mcp_core::catalog::CatalogManager;
use std::path::PathBuf;

#[test]
fn test_catalog_search() {
    let sample_json = r#"{
        "version": "1.0.0",
        "servers": [
            {"id": "excel", "name": "Excel MCP", "version": "1.0.0", "installed": true, "enabled": true, "tools": []}
        ]
    }"#;
    let cm = CatalogManager::from_str(sample_json).unwrap();
    let results = cm.search("excel");
    assert_eq!(results.len(), 1);
    assert_eq!(results[0].id, "excel");
}
```

- [ ] **Step 2: Triển khai CatalogManager và MockServerScanner trong `crates/mcp-core`**
Đọc `catalog.json`, tìm kiếm theo từ khóa / category. Quét thư mục ngoài (`MCP_SERVERS_DIR` hoặc fallback `D:\AI_MCP\servers`) để tìm các file `server.py` hoặc `manifest.json` nhằm phục vụ mock API test.

- [ ] **Step 3: Triển khai Stdio Subprocess Client an toàn**
Dùng `tokio::process::Command` để spawn `python.exe` với timeout và Windows Job Objects đảm bảo tự đóng tiến trình khi huỷ task.

- [ ] **Step 4: Chạy test kiểm tra**
Run: `cargo test -p mcp-core`
Expected: PASS.

- [ ] **Step 5: Commit**
```bash
git add crates/mcp-core
git commit -m "feat(mcp): implement mcp-core crate with catalog search and external mock runner"
```

---

### Task 4: Crate `apps/desktop` (Tauri v2 Shell & IPC Handlers)

**Files:**
- Create: `apps/desktop/Cargo.toml`
- Create: `apps/desktop/tauri.conf.json`
- Create: `apps/desktop/capabilities/default.json`
- Create: `apps/desktop/build.rs`
- Create: `apps/desktop/src/main.rs`
- Create: `apps/desktop/src/lib.rs`
- Create: `apps/desktop/src/commands.rs`

**Interfaces:**
- Consumes: `mcp_core::*`, `win11_platform::*`, `shared_types::*`
- Produces: Tauri executable `mcp-protocol-studio.exe`
- IPC Commands: `get_catalog`, `install_mcp`, `execute_tool`, `set_theme`, `toggle_autostart`

- [ ] **Step 1: Tạo cấu hình `apps/desktop/Cargo.toml` và `tauri.conf.json`**
Khai báo `tauri = "2.12.5"`, cấu hình đọc frontend từ `../../frontend/dist` (dev: `http://localhost:5173`).

- [ ] **Step 2: Tạo các Tauri Commands trong `apps/desktop/src/commands.rs`**
Ánh xạ các lệnh từ Vue 3:
```rust
#[tauri::command]
async fn get_catalog(
    state: tauri::State<'_, AppState>,
    query: Option<String>,
) -> Result<Vec<PluginItem>, String> {
    state.catalog.search(query.as_deref().unwrap_or("")).map_err(|e| e.to_string())
}
```

- [ ] **Step 3: Triển khai `apps/desktop/src/lib.rs` và `main.rs`**
Khởi tạo SingleInstanceGuard, thiết lập System Tray với icon 3D, đăng ký invoke handler và nạp DWM theme khi cửa sổ xuất hiện.

- [ ] **Step 4: Kiểm tra build cú pháp**
Run: `cargo check -p desktop`
Expected: PASS, 0 warnings/errors.

- [ ] **Step 5: Commit**
```bash
git add apps/desktop
git commit -m "feat(desktop): implement tauri v2 desktop shell with tray, dwm, and ipc commands"
```

---

### Task 5: Cấu hình Frontend Adapter & Xác minh Toàn diện

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/src/services/nativeBridge.ts`
- Modify: `frontend/src/features/plugins/stores/pluginStore.ts`

- [ ] **Step 1: Cài đặt `@tauri-apps/api` vào `frontend`**
Cài đặt dependency `@tauri-apps/api` và `@tauri-apps/cli`.

- [ ] **Step 2: Viết `frontend/src/services/nativeBridge.ts`**
Cung cấp adapter thông minh: Nếu đang chạy trong Tauri (`window.__TAURI_INTERNALS__`) -> gọi `invoke()`; nếu đang chạy Web dev mode -> fallback gọi HTTP Gateway `http://127.0.0.1:8000`.

- [ ] **Step 3: Tích hợp adapter vào `pluginStore.ts`**
Cập nhật `fetchCatalogFromServer()`, `installMcpOnClient()`, `executeToolDirectly()` để sử dụng `nativeBridge`.

- [ ] **Step 4: Chạy toàn bộ test kiểm tra trong workspace**
Run: `cargo test --workspace`
Expected: Tất cả các crate `shared-types`, `win11-platform`, `mcp-core` pass 100%.

- [ ] **Step 5: Commit**
```bash
git add frontend/
git commit -m "feat(frontend): integrate nativeBridge adapter supporting both tauri ipc and http fallback"
```
