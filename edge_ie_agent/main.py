"""CLI Entry Point for Edge IE Mode Visual Agent."""
import os
import sys
from edge_ie_agent.config import load_config
from edge_ie_agent.agent import VisualAgent
from edge_ie_agent.window_manager import WindowNotFoundError

def print_banner():
    banner = """
============================================================
      EDGE IE-MODE VISUAL AUTOMATION AGENT (QWEN VISION)
============================================================
* Chuyên tự động hóa web cổ trên Microsoft Edge (IE Mode).
* Hỗ trợ menu đa cấp (Hover), cuộn độc lập, gõ tiếng Việt.
* An toàn: Di chuột ra góc màn hình để dừng khẩn cấp.
============================================================
"""
    print(banner)

def main():
    print_banner()
    config = load_config()

    if not config.api_key:
        print("[LỖI] Chưa cấu hình AIPRO_API_KEY trong môi trường hoặc file .env!")
        print("Vui lòng tạo file .env trong thư mục edge_ie_agent/ theo mẫu .env.example.")
        sys.exit(1)

    print(f"[*] API Base URL: {config.base_url}")
    print(f"[*] Model:        {config.model_name}")
    print(f"[*] Cửa sổ Edge:  Chứa từ khóa '{config.edge_keyword}'")
    print(f"[*] Max Steps:    {config.max_steps}\n")

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
            print(f"\n🎉 KẾT QUẢ: {result}\n")

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
