# Hướng Dẫn Dành Cho AI Code Assistant Trong Môi Trường Offline (AIR-GAPPED AI INSTRUCTIONS)

> **CHỈ DẪN QUAN TRỌNG DÀNH CHO AI TRÊN MÁY OFFLINE:**  
> Bạn đang hoạt động trong môi trường **không có kết nối Internet**. Bạn không thể tra cứu Google, docs.rs hay StackOverflow. Trước khi viết hoặc sửa đổi bất kỳ đoạn mã Rust, Tauri hoặc Frontend nào, bạn **BẮT BUỘC** phải tham chiếu các tài liệu đặc tả chính thức trong thư mục này.

---

## Danh Mục Tài Liệu Đặc Tả Kỹ Thuật (Official Specs)

1. **[`02_tauri_v2_anti_hallucination_guide.md`](./02_tauri_v2_anti_hallucination_guide.md)** — **[QUAN TRỌNG NHẤT]**
   * Bảng đối chiếu & danh sách cấm các API cũ của **Tauri v1** (`@tauri-apps/api/tauri`, `SystemTray`, `allowlist`, `emit_all`).
   * Cung cấp mẫu code chuẩn Tauri v2 cho Tray, Window Lifecycle, Event Bus và Frontend IPC.

2. **[`01_tauri_v2_core_spec.md`](./01_tauri_v2_core_spec.md)**
   * Đặc tả toàn bộ API cốt lõi của Tauri v2: `tauri::Builder`, `AppState`, `#[tauri::command]`, `WebviewWindow`, `Emitter`, `Listener`.
   * Hướng dẫn chi tiết cách tiêm phụ thuộc (Dependency Injection) và quy chuẩn trả về `Result<T, E>`.

3. **[`03_rust_desktop_system_spec.md`](./03_rust_desktop_system_spec.md)**
   * Quy chuẩn kiến trúc xử lý lỗi với `thiserror`.
   * Tối ưu hóa Tokio Async (tránh block main UI thread với `spawn_blocking`).
   * Cơ chế ghi file Atomic Write chống mất dữ liệu khi crash.
   * Giao tiếp Windows API cấp thấp: Single Instance Mutex và Registry Autostart.

4. **[`04_tauri_v2_capabilities_and_plugins.md`](./04_tauri_v2_capabilities_and_plugins.md)**
   * Hệ thống bảo mật phân quyền Capabilities & Permissions (ACL) mới của Tauri v2.
   * Cách dùng các plugin chính thức (`dialog`, `shell`, `autostart`, `single-instance`, `store`).
   * **Chiến lược Pure Rust Fallback:** Cách tự viết code Rust thay thế khi máy offline thiếu crate plugin.

5. **[`05_complete_project_boilerplate_template.md`](./05_complete_project_boilerplate_template.md)**
   * Bộ khung Turnkey Starter Template hoàn chỉnh: Root `Cargo.toml`, các crate con, `main.rs`, `lib.rs`, `commands.rs`, `tauri.conf.json`, `nativeBridge.ts`.
   * Copy-paste dùng ngay để khởi tạo dự án mới từ số 0 mà không thiếu sót tệp nào.

6. **[`06_github_updater_and_windows_autostart_spec.md`](./06_github_updater_and_windows_autostart_spec.md)**
   * Đặc tả kỹ thuật kiểm tra cập nhật từ GitHub Releases API (so sánh phiên bản số học an toàn, tải và kích hoạt installer).
   * Kỹ thuật khởi động cùng Windows qua Registry HKCU và khởi động ẩn xuống System Tray (`--autostart`).

---

## 3 Quy Tắc Bắt Buộc Dành Cho AI Khi Sinh Mã Nguồn:

1. **KHÔNG BAO GIỜ sinh code Tauri v1:** Mọi import trên Frontend phải là `@tauri-apps/api/core` hoặc `@tauri-apps/api/event`.
2. **KHÔNG BAO GIỜ viết logic nghiệp vụ trực tiếp trong IPC Command:** Chia nhỏ logic vào các crates độc lập (`crates/*`), `apps/desktop` chỉ là lớp điều hướng (dispatcher).
3. **MỌI TÁC VỤ NẶNG PHẢI LÀ ASYNC:** Tuyệt đối không thực hiện I/O nặng trực tiếp trong command đồng bộ làm treo giao diện người dùng.
