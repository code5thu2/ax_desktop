# AX Desktop Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chuyển đổi và hợp nhất ứng dụng thành **AX Desktop** (Rust Tauri v2 + Vue 3 PrimeVue 4), tích hợp toàn bộ tính năng **Skill Marketplace** của AIPRO Studio và **MCP Protocol Studio**, hỗ trợ Mock API offline, cập nhật qua GitHub `code5thu2/ax_desktop`, giao diện Zero-Jank mượt mà, và đóng gói bộ cài NSIS tự dọn dẹp cache.

**Architecture:** Sử dụng mô hình Headless-First Multi-Crate Workspace: tạo mới `crates/ax-core` (Storage, Safe Zip Extraction, Skill lifecycle, AIPRO sync, Mock API engine, GitHub updater), mở rộng `crates/shared-types` (tự export TypeScript types), kết nối qua `apps/desktop` Tauri IPC commands, và dựng giao diện Vue 3 theo chuẩn `frontend-design` sử dụng các màn Auth từ `D:\primevue-auth-showcase`.

**Tech Stack:** Rust 1.90.0, Tauri 2.12.5, Tokio, Serde, ts-rs 10.1, Vue 3, PrimeVue 4 Aura, Tailwind CSS, TypeScript.

**Spec:** [`docs/superpowers/specs/2026-11-02-ax-desktop-integrated-design.md`](file:///d:/mcp-server-test/docs/superpowers/specs/2026-11-02-ax-desktop-integrated-design.md)

## Global Constraints

- Backend hoàn toàn bằng Rust 1.90.0, zero file Python trong repository.
- File cài đặt tạo ra là Native NSIS Setup `.exe` (~5 MB), tự động dọn dẹp `target/debug` ngay sau khi đóng gói.
- Đảm bảo Zero-Jank: 0% CPU khi ứng dụng đứng yên (không dùng animation vòng lặp vô tận, thay thế bằng static radial gradient).
- Mock API engine hỗ trợ offline 100%, đồng thời sẵn sàng chuyển đổi sang Live API (`http://ax-portal.gafc.vn/api/v1`).
- GitHub Updater trỏ tới `https://github.com/code5thu2/ax_desktop`.

## Review Focus

1. **Zip-slip Vulnerability:** Khi giải nén file zip từ server, nếu tên file chứa `../` hoặc đường dẫn tuyệt đối thì phải bị chặn và báo lỗi `BAD_ZIP`.
2. **Atomic Storage Protection:** Ghi các file `auth.json`, `installed.json`, `settings.json` phải qua `.tmp` và backup `.bak` để không bao giờ bị corrupt khi mất điện/tắt ngang.
3. **AIPRO Studio Config Sync:** Khi bật/tắt/gỡ skill, cờ `disabledSkills` trong `~/.aipro/config.json` hoặc `<project>/.aipro/config.json` phải được cập nhật chuẩn xác theo `name` trong `SKILL.md`.
4. **Offline Mock Autonomy:** Khi không có mạng, người dùng và dev vẫn đăng nhập được (OTP `123456`), duyệt kho kỹ năng mẫu và cài đặt bình thường.
5. **Path Normalization:** Mọi so sánh và lưu trữ đường dẫn `projectPath` phải chuẩn hóa sang forward slash `/` và không có trailing slash.

---

### Task 1: Data Models & DTOs in `crates/shared-types`

**Files:**
- Modify: `crates/shared-types/src/models.rs`
- Modify: `crates/shared-types/src/lib.rs`
- Test: `crates/shared-types/tests/models_test.rs`

**Interfaces:**
- Produces: `AuthUser`, `AuthTokens`, `AuthResponse`, `InstalledPlugin`, `SkillItem`, `SkillDetail`, `SkillVersionItem`, `PortalStatus`, `Settings`, `GithubRelease`

- [ ] **Step 1: Write the failing tests for AX Desktop models and TypeScript export**
- [ ] **Step 2: Run tests to verify they fail** (`cargo test -p shared-types`)
- [ ] **Step 3: Implement data structures with `Serialize`, `Deserialize`, and `TS` traits**
- [ ] **Step 4: Run tests to verify all tests pass and TypeScript files are exported to `frontend/src/types/generated/`**
- [ ] **Step 5: Commit** (`git commit -m "feat(types): add ax-desktop auth, skill, and portal models with ts-rs bindings"`)

---

### Task 2: Core Storage & Helpers in `crates/ax-core`

**Files:**
- Create: `crates/ax-core/Cargo.toml`
- Create: `crates/ax-core/src/lib.rs`
- Create: `crates/ax-core/src/storage.rs`
- Modify: `Cargo.toml` (thêm `crates/ax-core` vào workspace members)
- Test: `crates/ax-core/tests/storage_test.rs`

**Interfaces:**
- Produces: `write_json_atomic<T>()`, `read_json_safe<T>()`, `normalize_path(path)`, `extract_zip_safe(bytes, dest_dir)`

- [ ] **Step 1: Write failing tests for atomic JSON write, backup recovery, path normalization, and zip-slip rejection**
- [ ] **Step 2: Run tests to verify failure** (`cargo test -p ax-core`)
- [ ] **Step 3: Implement `storage.rs` with atomic temp writing, `.bak` fallback, and path sanitization**
- [ ] **Step 4: Run tests to verify all tests pass** (`cargo test -p ax-core`)
- [ ] **Step 5: Commit** (`git commit -m "feat(ax-core): implement atomic storage and zip-slip safe extraction"`)

---

### Task 3: Skill Server Client & Mock Engine in `crates/ax-core`

**Files:**
- Create: `crates/ax-core/src/client.rs`
- Create: `crates/ax-core/src/mock_engine.rs`
- Modify: `crates/ax-core/src/lib.rs`
- Test: `crates/ax-core/tests/mock_engine_test.rs`

**Interfaces:**
- Produces: `AxClient::new(api_base, mock_mode)`, `mock_login()`, `mock_fetch_skills()`, `mock_download_skill_zip()`

- [ ] **Step 1: Write failing tests for mock login, OTP verification, skill listing, and dynamic ZIP generation**
- [ ] **Step 2: Run tests to verify failure**
- [ ] **Step 3: Implement `client.rs` and `mock_engine.rs` with token rotation and realistic mock data**
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Commit** (`git commit -m "feat(ax-core): implement ax client and comprehensive offline mock engine"`)

---

### Task 4: Skill Lifecycle & AIPRO Core Synchronizer in `crates/ax-core`

**Files:**
- Create: `crates/ax-core/src/skill_manager.rs`
- Create: `crates/ax-core/src/synchronizer.rs`
- Modify: `crates/ax-core/src/lib.rs`
- Test: `crates/ax-core/tests/skill_manager_test.rs`

**Interfaces:**
- Produces: `install_skill()`, `uninstall_skill()`, `toggle_skill()`, `clone_skill()`, `sync_disabled_skills()`

- [ ] **Step 1: Write failing tests for install into global/project, toggle state update, clone skill, and `disabledSkills` sync**
- [ ] **Step 2: Run tests to verify failure**
- [ ] **Step 3: Implement `skill_manager.rs` and `synchronizer.rs` (YAML frontmatter parsing of `SKILL.md`)**
- [ ] **Step 4: Run tests to verify all tests pass**
- [ ] **Step 5: Commit** (`git commit -m "feat(ax-core): implement skill lifecycle management and aipro config synchronizer"`)

---

### Task 5: GitHub Release Updater & Studio Launcher

**Files:**
- Create: `crates/ax-core/src/updater.rs`
- Modify: `crates/win11-platform/src/lib.rs`
- Create: `crates/win11-platform/src/studio_launcher.rs`
- Test: `crates/ax-core/tests/updater_test.rs`

**Interfaces:**
- Produces: `check_github_update(repo, current_version)`, `find_and_launch_aipro_studio()`

- [ ] **Step 1: Write failing tests for version comparison (`_version_gt`) and GitHub release JSON parsing**
- [ ] **Step 2: Run tests to verify failure**
- [ ] **Step 3: Implement GitHub Releases checker (`code5thu2/ax_desktop`) and Windows Registry studio launcher**
- [ ] **Step 4: Run tests to verify they pass**
- [ ] **Step 5: Commit** (`git commit -m "feat(ax-core): add github updater for code5thu2/ax_desktop and studio launcher"`)

---

### Task 6: Tauri Desktop Shell Integration in `apps/desktop`

**Files:**
- Modify: `apps/desktop/Cargo.toml` (thêm dependency `ax-core`)
- Modify: `apps/desktop/tauri.conf.json` (`productName: "AX Desktop"`)
- Modify: `apps/desktop/src/commands.rs` (đăng ký đầy đủ `js_api` contract IPC commands)
- Modify: `apps/desktop/src/lib.rs`
- Test: `cargo test -p desktop`

**Interfaces:**
- Produces: Tauri IPC commands: `login`, `get_status`, `fetch_skills`, `get_skill_detail`, `install_skill`, `uninstall_skill`, `toggle_skill`, `clone_skill`, `open_studio`, `select_folder`, `check_for_update`, `download_update`

- [ ] **Step 1: Write tests for commands dispatching and error mapping**
- [ ] **Step 2: Implement Tauri IPC handlers in `commands.rs` connecting to `ax-core`**
- [ ] **Step 3: Register commands in `tauri::Builder` in `apps/desktop/src/lib.rs`**
- [ ] **Step 4: Verify workspace builds cleanly** (`cargo build -p desktop`)
- [ ] **Step 5: Commit** (`git commit -m "feat(desktop): expose all ax-desktop js_api ipc commands in tauri shell"`)

---

### Task 7: Frontend Auth Screens Integration (Zero-Jank)

**Files:**
- Create: `frontend/src/features/auth/AuthScreens.vue`
- Create: `frontend/src/features/auth/LoginScreen.vue`
- Create: `frontend/src/features/auth/RegisterScreen.vue`
- Create: `frontend/src/features/auth/OtpScreen.vue`
- Create: `frontend/src/features/auth/ForgotScreen.vue`
- Create: `frontend/src/features/auth/LogoutScreen.vue`
- Create: `frontend/src/i18n/index.ts` (tích hợp từ điển vi / en / ko)
- Modify: `frontend/src/App.vue` (Auth Gate)

**Interfaces:**
- Consumes: `nativeBridge.ts` (gọi `login`, `request_register_otp`, `verify_register_otp`, `logout`)
- Produces: Màn hình xác thực mượt mà không có animation giật lag, hỗ trợ nút "Dùng chế độ Khách / Offline Mock"

- [ ] **Step 1: Sao chép và tinh chỉnh các component Auth từ `D:\primevue-auth-showcase`**
- [ ] **Step 2: Tối ưu Zero-Jank: Xóa bỏ mọi `ambientGlow` animation vô tận, thay bằng static radial gradient, bỏ `backdrop-filter: blur(24px)` nặng nề**
- [ ] **Step 3: Kết nối Auth screens vào `nativeBridge.ts` và tích hợp vào Auth Gate trong `App.vue`**
- [ ] **Step 4: Chạy typecheck và test** (`npm run typecheck` trong `frontend/`)
- [ ] **Step 5: Commit** (`git commit -m "feat(frontend): integrate zero-jank primevue auth screens with i18n"`)

---

### Task 8: Frontend AXPortalView & Navigation (Skill Marketplace + MCP Studio)

**Files:**
- Create: `frontend/src/features/skills/AXPortalView.vue`
- Create: `frontend/src/features/skills/components/SkillList.vue`
- Create: `frontend/src/features/skills/components/SkillDetailPanel.vue`
- Create: `frontend/src/features/skills/components/ProjectListPanel.vue`
- Create: `frontend/src/features/skills/components/ScopeModal.vue`
- Create: `frontend/src/features/skills/components/FolderPickerModal.vue`
- Create: `frontend/src/features/skills/components/CloneSkillModal.vue`
- Create: `frontend/src/features/skills/components/UpdateDialog.vue`
- Modify: `frontend/src/features/plugins/stores/pluginStore.ts`
- Modify: `frontend/src/services/nativeBridge.ts`

**Interfaces:**
- Consumes: Tauri IPC commands cho Marketplace & Projects
- Produces: Giao diện AXPortalView hoàn chỉnh với 3 tab: `Marketplace`, `Installed`, `Projects`, thanh Mode Switcher chuyển `Skill Marketplace` ⟷ `MCP Studio`, PrimeVue Toast và Dialogs

- [ ] **Step 1: Viết test cho `pluginStore.ts` với đầy đủ actions (loadStatus, fetchSkills, install, toggle, clone)**
- [ ] **Step 2: Triển khai `pluginStore.ts` và `nativeBridge.ts` ánh xạ 100% IPC commands**
- [ ] **Step 3: Xây dựng các components giao diện `AXPortalView`, Header, Left list, Right detail, Dialogs**
- [ ] **Step 4: Kiểm tra lint và typecheck** (`npm run typecheck` && `npm run build`)
- [ ] **Step 5: Commit** (`git commit -m "feat(frontend): implement ax-portal view with 3 tabs, modals, and mcp switcher"`)

---

### Task 9: End-to-End Verification & Installer Build with Auto Cleanup

**Files:**
- Modify: `build_release.bat`
- Modify: `build_installer.bat`
- Test: Toàn bộ quy trình từ mock auth tới install skill và đóng gói

- [ ] **Step 1: Chạy `cargo test --workspace` kiểm tra 100% tests pass**
- [ ] **Step 2: Chạy `npm run test` trong frontend kiểm tra unit tests**
- [ ] **Step 3: Chạy `build_release.bat` kiểm tra binary `desktop.exe` hoạt động, `target/debug` tự động được dọn dẹp**
- [ ] **Step 4: Chạy `build_installer.bat` kiểm tra tạo thành công `AX-Desktop-Setup.exe` (~5 MB)**
- [ ] **Step 5: Commit hoàn tất** (`git commit -m "chore(release): complete ax-desktop unified release with automated cleanup"`)
