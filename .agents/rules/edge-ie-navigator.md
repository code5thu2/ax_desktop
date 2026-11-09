# Edge IE Mode Navigator Rule

Khi người dùng yêu cầu thao tác, tra cứu, click, hoặc tự động hóa trên Microsoft Edge ở chế độ IE Mode:
1. Hãy kích hoạt Subagent hoặc làm theo quy trình trong `.claude/agents/edge-ie-navigator.md`.
2. Sử dụng công cụ `edge_tools.py`:
   - Chụp ảnh: `python edge_tools.py capture --output edge_screenshot.png`
   - Đọc ảnh bằng mắt của model hiện tại.
   - Click: `python edge_tools.py click --x <X> --y <Y>`
   - Hover (cho menu con): `python edge_tools.py hover --x <X> --y <Y>`
   - Type (tiếng Việt an toàn qua Clipboard): `python edge_tools.py type --text "<TEXT>" [--enter]`
   - Scroll: `python edge_tools.py scroll --x <X> --y <Y> --direction down|up`
