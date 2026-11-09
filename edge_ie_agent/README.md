# Edge IE Mode Visual Automation Agent (Qwen Vision)

Ứng dụng AI Agent tự động hóa thao tác người dùng trên các website cổ chạy qua **Microsoft Edge ở chế độ Internet Explorer (IE Mode)**. Sử dụng **Qwen Vision** (qua endpoint AIPRO chuẩn OpenAI API) và **PyAutoGUI**.

---

## 1. Tính năng nổi bật

- 👁️ **Thị giác máy tính (Visual Grounding):** Qwen nhìn thẳng vào ảnh chụp màn hình cửa sổ Edge, bất chấp mọi rào cản code cũ, frameset, hay layout table cổ.
- 🎯 **Chuẩn hóa tọa độ 0–1000:** Định vị bấm nút chính xác tuyệt đối trên mọi độ phân giải màn hình Windows (100%, 125%, 150% scaling).
- 🧭 **Chuyên trị menu dày đặc & đa cấp (Hover):** Hỗ trợ action `hover` giúp di chuột vào menu cha để bung menu con (`onmouseover`) trước khi click.
- 📜 **Cuộn theo vị trí (`scroll_at`):** Di chuyển chuột đến đúng cột menu bên trái để cuộn danh mục mà không làm trôi toàn bộ trang web.
- 🇻🇳 **Gõ tiếng Việt an toàn:** Điền văn bản thông qua Windows Clipboard (`Ctrl+V`), không bao giờ bị lỗi dấu hoặc xung đột với Unikey / EVKey.
- 🛡️ **Fail-Safe an toàn:** Di chuyển chuột ra bất kỳ góc nào của màn hình để ngắt chương trình khẩn cấp.

---

## 2. Cài đặt

1. Đảm bảo bạn đang ở môi trường Python 3.10+:
```bash
pip install -r requirements.txt
```

2. Tạo file cấu hình `.env` từ `.env.example`:
```bash
copy .env.example .env
```

3. Mở file `.env` và điền thông tin API của AIPRO:
```env
AIPRO_API_KEY=your_actual_aipro_api_key
AIPRO_BASE_URL=https://api.aipro.vn/v1
QWEN_MODEL_NAME=qwen-vl-plus
EDGE_WINDOW_KEYWORD=Edge
MAX_STEPS=20
```

---

## 3. Hướng dẫn sử dụng

1. **Chuẩn bị trình duyệt:**
   - Mở **Microsoft Edge**.
   - Truy cập vào trang web cổ của bạn.
   - Bấm nút **Reload in Internet Explorer mode** (Chế độ IE).
   - Đăng nhập sẵn hoặc cắm USB Token ký số sẵn nếu cần.

2. **Chạy Agent:**
```bash
python -m edge_ie_agent.main
```
hoặc:
```bash
python edge_ie_agent/main.py
```

3. **Nhập lệnh:**
   - Ví dụ: `Vào menu Báo cáo thuế, chọn Tra cứu tờ khai, nhập mã số thuế 0101234567 và bấm Tìm kiếm`
   - Agent sẽ tự kích hoạt cửa sổ Edge, quan sát, rê chuột mở menu con, click và điền dữ liệu tự động.

---

## 4. Chạy kiểm thử tự động (Unit Tests)

```bash
python -m pytest edge_ie_agent/tests/ -v
```
Toàn bộ 19 test case đều độc lập và tự động giả lập (mock) các thao tác chuột, cửa sổ và API.
