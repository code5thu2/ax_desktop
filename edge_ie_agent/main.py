"""CLI Entry Point for Edge IE Mode Multi-Agent System (GLM + Qwen)."""
import os
import sys
from edge_ie_agent.config import load_config
from edge_ie_agent.agent import VisualAgent
from edge_ie_agent.window_manager import WindowNotFoundError

def print_banner():
    banner = """
====================================================================
   CLAUDE CODE STYLE MULTI-AGENT FOR EDGE IE MODE (GLM + QWEN)
====================================================================
* Nhạc trưởng (Main Agent):  GLM 5.2 (Lập kế hoạch & phân rã nhiệm vụ)
* Trinh sát (Vision Subagent): Qwen 33.8 (Soi tọa độ & menu đa cấp)
* Isolated Context: Giữ context chính luôn sạch, chạy cực nhanh!
* An toàn: Di chuột ra 1 trong 4 góc màn hình để dừng khẩn cấp.
====================================================================
"""
    print(banner)

def main():
    print_banner()
    config = load_config()

    if not config.api_key:
        print("[LỖI] Chưa cấu hình AIPRO_API_KEY trong file .env!")
        print("Vui lòng tạo file .env trong thư mục edge_ie_agent/ theo mẫu .env.example.")
        sys.exit(1)

    print(f"[*] API Base URL:        {config.base_url}")
    print(f"[*] Main Agent Model:    {config.glm_model}")
    print(f"[*] Subagent Model:      {config.qwen_model}")
    print(f"[*] Cửa sổ Edge:         Chứa từ khóa '{config.edge_keyword}'")
    print(f"[*] Max Steps:           {config.max_steps}\n")

    agent = VisualAgent(config=config)

    while True:
        try:
            task = input("\n👉 Nhập nhiệm vụ cần thực hiện (hoặc 'exit' để thoát): ").strip()
            if not task:
                continue
            if task.lower() in ("exit", "quit", "q"):
                print("Tạm biệt!")
                break

            result = agent.run(task)
            print(f"\n🎉 KẾT QUẢ CUỐI CÙNG: {result}\n")

        except WindowNotFoundError as e:
            print(f"\n[!] Cảnh báo: {e}")
        except TimeoutError as e:
            print(f"\n[!] Quá thời gian: {e}")
        except KeyboardInterrupt:
            print("\n[!] Đã dừng bởi người dùng (Ctrl+C).")
            break
        except Exception as e:
            print(f"\n[!] Có lỗi xảy ra trong quá trình thực thi: {e}")

if __name__ == "__main__":
    main()
