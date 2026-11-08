# Cẩm Nang Toàn Diện: Lập Trình & Đóng Gói Rust + Tauri v2 Trên Máy Không Có Mạng (Air-Gapped / Offline Development)

> **Mục tiêu:** Cung cấp hướng dẫn từng bước (Step-by-Step Playbook) để chuẩn bị môi trường, mang mã nguồn và toàn bộ công cụ sang một máy tính **hoàn toàn không có Internet** (Air-gapped / Secure Environment), đảm bảo quá trình code, chạy test, sửa lỗi, và build ra bộ cài đặt Windows Setup `.exe` (NSIS) diễn ra 100% offline và không bị chặn bởi bất kỳ phụ thuộc mạng nào.

---

## 1. Bản Đồ Các Rào Cản Khi Code Rust & Tauri Offline

Khi làm việc trên máy không có mạng, một dự án Rust + Tauri thông thường sẽ bị gãy ở **5 điểm then chốt**:

| Hạng mục | Rào cản khi không có mạng | Giải pháp kỹ thuật chuẩn |
| :--- | :--- | :--- |
| **1. Rust Crates** | `cargo build` đòi kết nối tới `crates.io` để tải package | Dùng `cargo vendor` đóng gói toàn bộ source crates vào local repo + cấu hình `.cargo/config.toml` |
| **2. Frontend NPM** | `npm install` hoặc build script cần tải packages từ `npmjs.org` | Pre-bundle `node_modules` hoặc tạo offline cache/tarballs |
| **3. Tauri NSIS Assets** | `cargo tauri build` ngầm tải bộ NSIS và plugins từ GitHub về `%LOCALAPPDATA%\tauri` | Tải trước bộ bundle NSIS đặt vào đúng thư mục cache hệ thống |
| **4. WebView2 Runtime** | Bộ cài mặc định (`downloadBootstrapper`) tải WebView2 online khi cài đặt | Cấu hình `embedBootstrapper` hoặc `offlineInstaller` trong `tauri.conf.json` |
| **5. Tài liệu & Language Server** | Không thể tra cứu Google, StackOverflow, crates.io docs | Kích hoạt `rustup doc` (HTML offline), tải offline docsets (Zeal/Dash) |

---

## 2. Giai Đoạn 1: Chuẩn Bị Trên Máy Có Mạng (The Online Phase)

Thực hiện các bước sau trên máy có kết nối Internet trước khi copy sang USB/ổ cứng mang đi.

### 2.1 Cài Đặt Trọn Vẹn Offline Toolchain & Docs
Tải mã nguồn thư viện chuẩn (để `rust-analyzer` gợi ý code không cần mạng) và tài liệu HTML:

```powershell
# 1. Tải source code Rust std và tài liệu HTML offline
rustup component add rust-src rust-docs

# 2. Kiểm tra tài liệu offline (sẽ mở browser cục bộ từ máy tính, không cần internet)
rustup doc --std
```

### 2.2 Đóng Gói Toàn Bộ Crates Bằng `cargo vendor`
Lệnh `cargo vendor` sẽ copy mã nguồn của tất cả thư viện trong `Cargo.lock` vào một thư mục local `vendor/`:

```powershell
# Chạy tại thư mục root của Cargo Workspace
cargo vendor ./vendor
```

Sau khi chạy xong, Cargo sẽ in ra cấu hình nguồn thay thế. Hãy tạo file **`.cargo/config.toml`** ngay tại root của project với nội dung:

```toml
# .cargo/config.toml
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"

# Bật cờ offline mặc định
[net]
offline = true
```

> [!TIP]
> Với cấu hình này, bất kỳ lệnh nào như `cargo check`, `cargo test`, `cargo build` sẽ chỉ tìm kiếm thư viện trong thư mục `vendor/` mà không bao giờ cố kết nối ra ngoài internet.

---

### 2.3 Đóng Gói Frontend `node_modules`
Cách an toàn và nhanh nhất cho máy offline là chuẩn bị sẵn toàn bộ `node_modules` đã được resolve và test build thành công:

```powershell
cd frontend
# 1. Cài đặt chuẩn theo package-lock.json
npm ci

# 2. Test thử build trước để đảm bảo không thiếu file binary (như esbuild, rollup...)
npm run build
cd ..
```

*Lưu ý khi copy:* Do thư mục `node_modules` chứa hàng nghìn file nhỏ, hãy nén thành file zip (ví dụ: `frontend_node_modules.zip`) trước khi copy vào USB để tốc độ truyền tải nhanh gấp 20 lần.

---

### 2.4 Cache Trước Các Binary Của Tauri v2 (Cực Kỳ Quan Trọng!)
Khi chạy lệnh `cargo tauri build` lần đầu, Tauri sẽ tự động kết nối GitHub Releases để tải các thành phần phục vụ đóng gói NSIS (Nullsoft Scriptable Install System). Trên máy không có mạng, lệnh này **chắc chắn sẽ fail**.

**Giải pháp:** Chạy build release thử 1 lần trên máy có mạng để Tauri tải toàn bộ dependencies vào cache:

```powershell
cargo tauri build
```

Kiểm tra thư mục cache đã được sinh ra:
* **Windows:** `C:\Users\<Tên_User>\AppData\Local\tauri\`
  * Trong thư mục này sẽ có thư mục `NSIS` chứa `nsis-3.x.x` và các plugin (`nsis_tauri_utils.dll`, v.v.).
* Hãy **copy toàn bộ thư mục `%LOCALAPPDATA%\tauri\` này vào USB** để mang sang máy offline!

---

### 2.5 Cấu Hình WebView2 Cho Máy Offline
Trong file `apps/desktop/tauri.conf.json`, hãy kiểm tra cấu hình `webviewInstallMode`:

```json
{
  "bundle": {
    "windows": {
      "webviewInstallMode": {
        "type": "embedBootstrapper"
      }
    }
  }
}
```

* **`downloadBootstrapper` (Mặc định - KHÔNG DÙNG CHO MÁY OFFLINE):** Bộ cài sẽ tải installer qua mạng.
* **`embedBootstrapper` (Khuyên dùng):** Nhúng sẵn file cài đặt bootstrapper vào file exe; nếu máy Windows 10/11 đã có sẵn WebView2 (hầu hết Windows hiện đại đều có sẵn), app sẽ chạy ngay mà không cần cài thêm.
* **`offlineInstaller`:** Nhúng trọn vẹn bộ runtime đầy đủ ~150MB nếu triển khai cho máy tính chuyên dụng cách ly hoàn toàn chưa từng cài Edge/WebView2.

---

### 2.6 Script Đóng Gói Tự Động Toàn Bộ Dự Án Sang USB
Tạo script `bundle_for_airgap.bat` trên máy có mạng:

```bat
:: bundle_for_airgap.bat
@echo off
echo ========================================================
echo   CHUAN BI GOI PHAT TRIEN OFFLINE / AIR-GAPPED
echo ========================================================

echo [1/4] Vendoring Cargo Crates...
call cargo vendor ./vendor
if not exist .cargo mkdir .cargo
(
  echo [source.crates-io]
  echo replace-with = "vendored-sources"
  echo.
  echo [source.vendored-sources]
  echo directory = "vendor"
  echo.
  echo [net]
  echo offline = true
) > .cargo\config.toml

echo [2/4] Testing Offline Rust Build...
call cargo test --offline
if %errorlevel% neq 0 (
  echo Error: Cargo offline test failed!
  exit /b 1
)

echo [3/4] Packaging Tauri Local Cache...
set TAURI_CACHE_DIR=%LOCALAPPDATA%\tauri
if exist "%TAURI_CACHE_DIR%" (
  tar -czvf tauri_cache.tar.gz -C "%LOCALAPPDATA%" tauri
  echo Tauri cache bundled successfully.
) else (
  echo Warning: %TAURI_CACHE_DIR% not found. Run 'cargo tauri build' online once!
)

echo [4/4] Bundling Frontend node_modules...
cd frontend
tar -czvf ..\frontend_modules.tar.gz node_modules
cd ..

echo ========================================================
echo   HOAN TAT! CAC FILE CAN COPY VAO USB:
echo   - Toan bo ma nguon workspace (da gom thu muc ./vendor va .cargo/)
echo   - File tauri_cache.tar.gz
echo   - File frontend_modules.tar.gz
echo   - Installer Rustup (rustup-init.exe) va VS Build Tools (offline layout)
echo ========================================================
pause
```

---

## 3. Giai Đoạn 2: Thiết Lập Trên Máy Không Có Mạng (The Offline Setup)

Sau khi chuyển dữ liệu qua USB sang máy tính biệt lập:

### 3.1 Khôi Phục Tauri Cache
Giải nén file `tauri_cache.tar.gz` vào đúng thư mục AppData cục bộ của người dùng trên máy offline:

```powershell
# Chạy trong PowerShell trên máy offline:
$target = "$env:LOCALAPPDATA"
tar -xzvf tauri_cache.tar.gz -C "$target"

# Đảm bảo đường dẫn tồn tại:
Test-Path "$env:LOCALAPPDATA\tauri"  # Phải trả về True
```

### 3.2 Khôi Phục Frontend `node_modules`
```powershell
cd frontend
tar -xzvf ..\frontend_modules.tar.gz
cd ..
```

---

## 4. Kỹ Thuật Lập Trình & Tra Cứu Offline (Developer Experience)

### 4.1 Tra Cứu Tài Liệu Không Cần Mạng
1. **Rust Standard Library & The Rust Book:**
   Chạy lệnh sau trong command prompt (sẽ mở trình duyệt xem offline 100%):
   ```cmd
   rustup doc --std
   rustup doc --book
   ```
2. **Tài liệu các thư viện đã tải trong `vendor/`:**
   Bạn có thể tự sinh tài liệu HTML cục bộ cho tất cả các crates trong dự án bằng lệnh:
   ```cmd
   cargo doc --offline --no-deps --open
   ```
   Lệnh này sẽ biên dịch tài liệu của `serde`, `tokio`, `tauri`, v.v. thành trang web HTML ngay trong thư mục `target/doc/` để tra cứu API.

### 4.2 Cấu Hình `rust-analyzer` Mượt Mà Khi Không Có Mạng
Trong VS Code hoặc Cursor (cài sẵn extension `rust-analyzer` bằng file `.vsix`), hãy vào Settings (`settings.json`) và thêm cấu hình:

```json
{
  "rust-analyzer.cargo.extraArgs": [
    "--offline"
  ],
  "rust-analyzer.check.extraArgs": [
    "--offline"
  ],
  "rust-analyzer.check.command": "check",
  "rust-analyzer.procMacro.enable": true
}
```
*Tác dụng:* Ngăn `rust-analyzer` kết nối internet tìm bản cập nhật crates, chuyển toàn bộ việc phân tích kiểu dữ liệu và gợi ý code sang thư mục `vendor/` nội bộ.

---

### 4.3 Áp Dụng Mô Hình Offline Mock Engine (Mô Hình Chuẩn Cho Desktop App)
Khi phát triển ứng dụng gọi REST API hoặc dịch vụ bên ngoài, trong môi trường không có mạng bạn **không thể kết nối tới máy chủ thật**.  
Hãy áp dụng triệt để pattern **Offline Mock Engine** và **Isomorphic Bridge** đã triển khai thành công trong dự án này:

```
[UI Components] 
       │
       ▼
[nativeBridge.ts] 
       │
   (Tauri IPC)
       │
       ▼
[Rust AppState] ──> is_offline_mode == true?
                         ├── YES ──> [MockEngine] (Sinh mock JWT, mock data JSON, OTP cố định 123456)
                         └── NO  ──> [HttpClient] (Gọi live URL thật)
```

**Nguyên tắc thiết kế Mock Engine cho máy offline:**
1. **Mock State In-Memory + File Fallback:** Lưu dữ liệu mẫu vào file `mock_catalog.json` hoặc struct tĩnh trong bộ nhớ.
2. **Full Lifecycle Simulation:** Mô phỏng đầy đủ mã trạng thái HTTP (`200 OK`, `401 Unauthorized`), logic xoay token, và sinh dữ liệu giả lập có cấu trúc thực tế.
3. **Zero Configuration Toggle:** Đọc biến môi trường hoặc cờ config (ví dụ: `APP_OFFLINE=1`) để tự động chuyển sang mock mode khi mất kết nối.

---

## 5. Quy Trình Build & Kiểm Thử Hàng Ngày Hoàn Toàn Offline

Mỗi khi chỉnh sửa code trên máy không có mạng, hãy sử dụng quy trình chuẩn sau:

### 1. Kiểm tra Backend Rust:
```powershell
cargo check --offline
cargo test --offline
```

### 2. Kiểm tra Frontend:
```powershell
cd frontend
npm run typecheck
npm run test
cd ..
```

### 3. Đóng Gói Bộ Cài Đặt NSIS Offline:
Tạo file `run_offline_build.bat`:
```bat
:: run_offline_build.bat
@echo off
set CARGO_NET_OFFLINE=true

echo [1/3] Building Frontend Assets...
cd frontend
call npm run build
if %errorlevel% neq 0 exit /b %errorlevel%
cd ..

echo [2/3] Compiling Tauri Desktop App & NSIS Installer...
call cargo tauri build --offline
if %errorlevel% neq 0 (
  echo Build failed! Kiem tra lai cache tai: %LOCALAPPDATA%\tauri
  exit /b %errorlevel%
)

echo [3/3] Done! Installer generated at:
dir /b target\release\bundle\nsis\*.exe
pause
```

---

## 6. Bảng Tra Cứu Sự Cố Offline Thường Gặp (Troubleshooting)

| Hiện tượng lỗi | Nguyên nhân | Cách khắc phục |
| :--- | :--- | :--- |
| `error: failed to get 'xyz' as a dependency of package...` | Cargo đang cố truy cập crates.io | Kiểm tra xem file `.cargo/config.toml` đã có mục `replace-with = "vendored-sources"` chưa. Chạy lệnh với cờ `--offline`. |
| `error: failed to download nsis binary from github.com` | Máy offline thiếu bộ công cụ NSIS của Tauri | Kiểm tra thư mục `%LOCALAPPDATA%\tauri\NSIS`. Copy lại thư mục này từ máy có mạng sang. |
| `Cannot find module 'esbuild'` khi chạy `npm run build` | `node_modules` copy thiếu các binary platform-specific | Khi đóng gói ở máy có mạng, phải chạy trên cùng hệ điều hành (Windows x64) và chạy thử `npm run build` trước khi nén. |
| `WebView2 installation failed / timeout` khi chạy bộ cài | File installer cố kết nối Microsoft để tải Edge WebView2 | Đổi `webviewInstallMode` trong `tauri.conf.json` sang `embedBootstrapper` hoặc đảm bảo Windows máy đích đã có Edge WebView2 Runtime. |
| `rust-analyzer` báo gạch đỏ toàn bộ thư viện ngoài | Chưa nhận diện thư mục `vendor/` | Mở Command Palette trong VS Code (`Ctrl+Shift+P`) $\to$ gõ `Rust-Analyzer: Restart server`. |
