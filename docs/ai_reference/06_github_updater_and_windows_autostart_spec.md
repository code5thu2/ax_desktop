# Đặc Tả Kỹ Thuật Cho AI: GitHub Updater & Windows Autostart (Offline AI Spec)

> **MỤC ĐÍCH DÀNH CHO AI:** Tập tin này đặc tả chuẩn xác 2 tính năng thường được yêu cầu trong Desktop Apps:
> 1. Kiểm tra cập nhật qua GitHub Releases API không cần backend server.
> 2. Đăng ký khởi động cùng Windows qua Registry HKCU và kỹ thuật khởi động ẩn xuống System Tray.

---

## 1. GitHub Releases Auto-Updater Specification

### 1.1 Nguyên Tắc Thiết Kế Cho AI
* **Không dùng plugin nếu không có mạng:** AI phải biết tự viết hàm Rust bằng `reqwest` và `serde` thay vì phụ thuộc `tauri-plugin-updater`.
* **Bắt buộc có User-Agent:** `reqwest::Client::builder().user_agent("MyApp").build()`. Không có header này GitHub sẽ trả về lỗi `403`.
* **So sánh SemVer phân đoạn số:** Cấm dùng `rel.tag_name > current_version` (so sánh chuỗi sẽ sai vì `"1.2.0" > "1.10.0"`). Phải split `.` và parse `u64` để so sánh từng phần tử.
* **Quy trình Silent Update:**
  1. Tải file binary vào `%TEMP%` (dùng `std::env::temp_dir()`).
  2. Dùng `std::process::Command::new(installer_path).spawn()`.
  3. Gọi `std::process::exit(0)` để nhường tài nguyên cho bộ cài ghi đè file.

---

## 2. Windows Autostart Specification

### 2.1 Nguyên Tắc Thiết Kế Cho AI
* **Không ghi vào HKLM:** Ghi vào `HKEY_LOCAL_MACHINE` sẽ gây lỗi `Permission Denied` nếu người dùng không chạy quyền Admin. Phải ghi vào `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`.
* **Đính kèm cờ `--autostart`:** `format!("\"{}\" --autostart", exe_path)`.
* **Khởi động ẩn (Start Minimized to Tray):**
  Trong `setup()` của Tauri, nếu `std::env::args().any(|a| a == "--autostart")`, AI phải gọi `window.hide()` để ứng dụng không bật cửa sổ to lên màn hình khi Windows vừa khởi động.
