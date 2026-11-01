# AX Desktop: Hợp nhất Skill Marketplace & MCP Protocol Studio — Đặc tả Thiết kế Kiến trúc

> **Ngày lập:** 2026-11-02  
> **Trạng thái:** Proposed / Đang xét duyệt  
> **Phạm vi:** Backend Rust (Tauri v2) + Frontend Vue 3 (PrimeVue 4)  
> **Nguồn đặc tả hành vi:** 26 trang tài liệu ảnh chụp (`docs/image doc/`) & `D:\primevue-auth-showcase`  

---

## 1. Tổng quan & Mục tiêu

### 1.1 Mục tiêu (Goals)
1. **Đổi tên & Định danh Thương hiệu:** Chuyển đổi ứng dụng thành **AX Desktop** (Windows Standalone Desktop App), tích hợp cả 2 năng lực cốt lõi:
   - **Skill Marketplace**: Quản lý vòng đời kỹ năng AI cho **AIPRO Studio** (Duyệt, Cài đặt Toàn cục/Dự án, Bật/Tắt, Gỡ bỏ, Sao chép giữa các project, Đồng bộ cờ `disabledSkills` vào `~/.aipro/config.json`).
   - **MCP Protocol Studio**: Quản lý, kiểm thử và chạy các máy chủ giao thức MCP (Model Context Protocol) với Mock Server biệt lập bên ngoài (`D:\AI_MCP\servers`).
2. **Backend Native Rust (Cargo Workspace)**:
   - Chuẩn hóa theo mô hình Headless-First Multi-Crate Workspace: `shared-types`, `win11-platform`, `mcp-core`, `ax-core`, `apps/desktop`.
   - Thay thế 100% backend Python cũ bằng Rust hiệu năng cao, khởi động < 0.3s, RAM ~40-50MB.
   - Triển khai **Mock API Engine** cho phép kiểm thử offline toàn bộ luồng Auth và Marketplace mà không phụ thuộc server mạng nội bộ.
   - Hỗ trợ cập nhật ứng dụng tự động qua GitHub Releases API công khai (`https://github.com/code5thu2/ax_desktop`).
3. **Frontend Hiện đại (Vue 3 + PrimeVue 4 Aura)**:
   - Tuân thủ triết lý `frontend-design`: Giao diện Obsidian AI Dark cao cấp, điểm nhấn ngọc lục bảo (Emerald `#10A37F`), hiệu ứng Ambient Glow và Glassmorphism.
   - Tích hợp bộ màn hình xác thực chất lượng cao từ `D:\primevue-auth-showcase` (`LoginScreen`, `RegisterScreen`, `OtpScreen`, `ForgotScreen`, `LogoutScreen`).
   - Đầy đủ 3 tab quản lý kỹ năng: `Marketplace`, `Installed`, `Projects` cùng các Modal/Dialog (Scope Selection, Folder Picker, Clone Skill, Confirm Uninstall).
   - Đa ngôn ngữ i18n (`vi`, `en`, `ko`).
4. **Đóng gói phân phối**: Bộ cài NSIS Setup `.exe` (~5 MB) siêu nhẹ của Tauri v2, tự động dọn dẹp sạch `target/debug` ngay sau khi build.

### 1.2 Ngoài phạm vi (Non-Goals)
- Không đụng chạm hay sửa đổi mã nguồn của AIPRO Studio core (chỉ giao tiếp qua filesystem: `~/.aipro/skills/` và `~/.aipro/config.json`).
- Không lưu trữ mã nguồn MCP Server trong repo này (tôn trọng nguyên tắc mock runner thư mục ngoài).

---

## 2. Kiến trúc Tổng thể (Overall Architecture)

```
d:\mcp-server-test\
├── Cargo.toml                  # Workspace root (resolver = 2)
├── crates/
│   ├── shared-types/           # DTOs & Models (ts-rs export sang frontend/src/types/generated)
│   ├── win11-platform/         # Windows 11 DWM dark titlebar, Single Instance Mutex, Autostart
│   ├── mcp-core/               # MCP Catalog, JSON-RPC stdio client, external mock runner
│   └── ax-core/                # [MỚI] AX Skill Marketplace Core:
│       ├── auth_manager.rs     # Quản lý JWT token, lưu %APPDATA%\ax-desktop\auth.json
│       ├── storage.rs          # Atomic write JSON (.bak), normalize path, safe zip extract
│       ├── skill_manager.rs    # Install, Uninstall, Toggle, Clone skill, check SKILL.md
│       ├── synchronizer.rs     # Đọc SKILL.md name, sync disabledSkills vào AIPRO Studio config
│       ├── mock_engine.rs      # Giả lập Auth & Marketplace API offline
│       └── updater.rs          # Kiểm tra release & download update qua GitHub API (code5thu2/ax_desktop)
├── apps/
│   └── desktop/                # Tauri v2 Binary Shell ("AX Desktop")
│       ├── tauri.conf.json     # App config, identifier, icons, NSIS bundle
│       ├── src/commands.rs     # Phơi bày toàn bộ Tauri IPC commands (js_api contract)
│       └── src/lib.rs          # Tauri runtime builder & event loop
└── frontend/                   # Vue 3 + PrimeVue 4 + Tailwind CSS
    └── src/
        ├── App.vue             # Auth Gate (chưa login -> AuthScreens; đã login -> AXPortalView)
        ├── features/
        │   ├── auth/           # Màn hình xác thực (kế thừa từ D:\primevue-auth-showcase)
        │   ├── skills/         # AXPortalView (Marketplace, Installed, Projects, Detail, Dialogs)
        │   └── mcp/            # MCP Protocol Studio (Catalog & Tools)
        ├── services/           # nativeBridge.ts (Tauri IPC invoke wrapper)
        ├── stores/             # Pinia: pluginStore.ts, mcpStore.ts
        └── i18n/               # Từ điển vi, en, ko
```

---

## 3. Backend Specification (`crates/ax-core` & IPC Contract)

### 3.1 Cấu hình & Vùng lưu trữ (Storage Layout)
| Đường dẫn | Nội dung | Cơ chế an toàn |
| :--- | :--- | :--- |
| `%APPDATA%\ax-desktop\auth.json` | `{ accessToken, refreshToken, user, updatedAt }` | Atomic replace + `.bak` |
| `%APPDATA%\ax-desktop\installed.json` | Mảng `InstalledPlugin[]` | Atomic replace + `.bak` |
| `%APPDATA%\ax-desktop\settings.json` | `{ theme, recentProjects[], rememberedEmail, rememberAccount }` | Atomic replace + `.bak` |
| `~/.aipro/skills/<id>/` | Thư mục mã nguồn skill toàn cục (Global Scope) | Chống Zip-slip |
| `<project>/.aipro/skills/<id>/` | Thư mục mã nguồn skill của dự án (Project Scope) | Chống Zip-slip |
| `~/.aipro/config.json` | Cấu hình core AIPRO toàn cục | Sync mảng `disabledSkills` |
| `<project>/.aipro/config.json` | Cấu hình core AIPRO dự án | Sync mảng `disabledSkills` |

### 3.2 Mock Engine & Live API Switching
- Biến môi trường: `AX_MOCK_API=true` (hoặc bật tùy chọn trong Settings).
- **Khi ở chế độ Mock**:
  - `login`: Chấp nhận email/password bất kỳ, sinh JWT token giả lập, lưu `auth.json`.
  - `request_otp`: Sinh mã OTP mẫu `123456`.
  - `fetch_skills`: Trả về danh sách 10+ skill mẫu phong phú (AI Coding, Prompt Optimizer, SQL Helper, Web Scraper, Translation...).
  - `get_skill_versions`: Trả về lịch sử v1, v2, v3.
  - `download_zip`: Tự động tạo in-memory ZIP chứa `SKILL.md` hợp lệ với YAML frontmatter đầy đủ.

### 3.3 Danh sách IPC Commands (`js_api` Contract 3.7)
1. **Auth Commands**:
   - `login(credentials: LoginRequest)` -> `Result<AuthResponse, String>`
   - `request_register_otp(email: String)` -> `Result<(), String>`
   - `verify_register_otp(email: String, otp: String)` -> `Result<(), String>`
   - `register(payload: RegisterRequest)` -> `Result<(), String>`
   - `request_forgot_otp(email: String)` -> `Result<(), String>`
   - `verify_forgot_otp(email: String, otp: String)` -> `Result<(), String>`
   - `reset_password(payload: ResetPasswordRequest)` -> `Result<(), String>`
   - `logout()` -> `Result<(), String>`
2. **Skill Marketplace Commands**:
   - `get_status()` -> `PortalStatus`
   - `fetch_skills(query: SkillQuery)` -> `SkillListResponse`
   - `get_skill_detail(id: u64)` -> `Result<PluginDetail, String>`
   - `get_skill_versions(id: u64)` -> `Result<Vec<SkillVersionItem>, String>`
   - `install_skill(req: InstallSkillRequest)` -> `Result<InstallResult, String>`
   - `uninstall_skill(req: UninstallSkillRequest)` -> `Result<(), String>`
   - `toggle_skill(req: ToggleSkillRequest)` -> `Result<(), String>`
   - `clone_skill(req: CloneSkillRequest)` -> `Result<(), String>`
3. **Hệ thống & Tiện ích**:
   - `open_studio()` -> Mở `AIPRO_Studio.exe` qua Registry `HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall`
   - `select_folder()` -> Mở hộp thoại chọn thư mục gốc của Windows
   - `check_for_update()` -> Gọi GitHub Releases API (`https://api.github.com/repos/code5thu2/ax_desktop/releases`)
   - `download_update()` -> Tải file installer
4. **MCP Commands hiện có**:
   - `get_catalog()`, `execute_tool()`

---

## 4. Frontend Specification (Vue 3 + PrimeVue 4)

### 4.1 Triết lý Thiết kế & Tối ưu Hiệu năng (frontend-design & Zero-Jank)
- **Design Personality**: *Obsidian AI Workspace* — Nền tối chiều sâu (`#121212`, `#1E1E1E`, `#252526`), viền phân cách tinh tế (`#333333`), điểm nhấn Ngọc lục bảo thương hiệu (`#10A37F` / Emerald Aura).
- **Nguyên tắc "Mượt mà số 1 - Zero Lag"**:
  1. **Triệt tiêu animation ngốn CPU/GPU chạy ngầm**:
     - Bỏ hoàn toàn các animation vòng lặp vô tận chạy nền (như `ambientGlow 7s ease-in-out infinite` liên tục kích hoạt Chromium layout repaint).
     - Thay thế bằng **Radial Gradient tĩnh (Static Ambient Glow)**: Vẫn giữ hiệu ứng ánh sáng tỏa sang trọng nhưng **0% CPU** khi đứng yên.
     - Giảm tải / loại bỏ `backdrop-filter: blur(24px)` trên các vùng diện tích lớn vì WebView2 tốn nhiều tài nguyên khi render blur. Dùng màu nền bán trong suốt tĩnh kết hợp viền mờ cao cấp (`bg-slate-900/90 border border-white/10`).
  2. **Chỉ animate các thuộc tính GPU-accelerated**:
     - Tuyệt đối không animate `width`, `height`, `margin`, `padding`, `top`, `left`, `box-shadow`.
     - Chỉ cho phép chuyển động trên **`opacity`** và **`transform`** (`translateY`, `scale`) với thời lượng ngắn (`150ms - 200ms`, `cubic-bezier(0.16, 1, 0.3, 1)`).
  3. **Tối ưu Danh sách & Tìm kiếm (Render Performance)**:
     - Debounce 300ms khi người dùng gõ phím tìm kiếm để tránh kích hoạt tính toán và re-render liên tục.
     - Lọc danh sách cục bộ tức thì trong bộ nhớ (Client-side fast filter) mang lại cảm giác phản hồi 0-latency.
  4. **Typography**: Phông chữ chính `Plus Jakarta Sans`, phông số liệu/code `JetBrains Mono` (đã nhúng local woff2, hỗ trợ 100% môi trường air-gapped không cần CDN).
- **UX States đầy đủ**:
  - Skeleton loaders nhẹ nhàng khi đang tải danh sách skill.
  - Empty states trực quan khi tìm kiếm không ra kết quả hoặc danh sách project rỗng.
  - Toast thông báo chuẩn ở góc dưới bên phải (`bottom-right`).

### 4.2 Cấu trúc Giao diện
1. **Auth Gate (`App.vue`)**:
   - Trạng thái `loggedIn` quyết định render `AuthScreens` hay `AXPortalView`.
   - Có tùy chọn *"Dùng chế độ Khách / Offline Mock"* để dev có thể vào thẳng app mà không cần login.
2. **Auth Screens (`features/auth/`)**:
   - Kế thừa trực tiếp từ `D:\primevue-auth-showcase`: `LoginScreen.vue`, `RegisterScreen.vue`, `OtpScreen.vue` (với PrimeVue InputOtp), `ForgotScreen.vue`, `LogoutScreen.vue`.
3. **AX Portal View (`features/skills/AXPortalView.vue`)**:
   - **Header**: Logo AX Desktop + Badge "Skill Marketplace" | Language Switcher | Theme Toggle | Nút "Mở AIPRO Studio" | Settings Dropdown.
   - **Mode Switcher**: Nút chuyển đổi giữa `🌐 Skill Marketplace` và `⚡ MCP Protocol Studio`.
   - **Skill Marketplace Shell**:
     - *Tab Bar*: `Marketplace`, `Installed (kèm badge số lượng)`, `Projects`.
     - *Left Panel*: Thanh tìm kiếm, bộ lọc danh mục, danh sách skill (Infinite scroll / Pagination).
     - *Right Panel*: Panel chi tiết skill (Overview tab, What's New tab, Scope card: Toàn cục vs Dự án, nút Bật/Tắt, nút Cài đặt, nút Gỡ bỏ).
   - **Dialogs**:
     - `ScopeModal.vue`: Chọn cài đặt Toàn cục (`~/.aipro/skills/`) hay Vào Dự án cụ thể.
     - `FolderPickerModal.vue`: Nhập hoặc duyệt thư mục dự án với danh sách gợi ý gần đây.
     - `CloneSkillModal.vue`: Sao chép kỹ năng từ dự án này sang dự án khác.
     - `ConfirmDialog`: Xác nhận gỡ cài đặt, cảnh báo xóa file.

---

## 5. Quy trình Đóng gói & Dọn dẹp

1. **Frontend Build**:
   - `npm run build` chạy `vue-tsc` và `vite build`, xuất toàn bộ bundle vào `frontend/dist`.
2. **Tauri NSIS Installer**:
   - Tauri bundling tạo ra `target/release/bundle/nsis/AX-Desktop_1.0.0_x64-setup.exe` (~5 MB).
3. **Automated Cache Cleanup**:
   - Tự động xóa sạch `target/debug` sau khi biên dịch xong, thu hồi ngay > 3.4 GB ổ cứng.

---

## 6. Kế hoạch Kiểm thử & Nghiệm thu

1. **Backend Tests**:
   - Test `storage.rs`: Đọc/ghi atomic JSON, phục hồi khi file hỏng qua `.bak`.
   - Test `installer.rs`: Chống lỗ hổng Zip-slip khi giải nén archive.
   - Test `synchronizer.rs`: Parse YAML frontmatter `name` trong `SKILL.md` và đồng bộ `disabledSkills`.
   - Test `mock_engine.rs`: Kiểm thử toàn bộ API endpoints giả lập.
2. **Frontend Tests**:
   - Vitest component tests cho `AuthScreens.vue`, `AXPortalView.vue`, `pluginStore.ts`.
3. **End-to-End Test**:
   - Chạy `run_native.bat` ➔ Đăng nhập qua Mock Auth ➔ Duyệt kho Skill ➔ Cài đặt 1 skill vào Toàn cục ➔ Kiểm tra file sinh ra tại `~/.aipro/skills/<id>/SKILL.md` ➔ Bật/Tắt skill ➔ Kiểm tra `disabledSkills` trong `~/.aipro/config.json`.
