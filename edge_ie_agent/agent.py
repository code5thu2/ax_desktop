"""ReAct Loop Orchestrator for Visual Agent."""
import time
from typing import Optional, List
from PIL import Image

from edge_ie_agent.config import Config, load_config
from edge_ie_agent.coordinate import normalize_to_screen
from edge_ie_agent.controller import Controller
from edge_ie_agent.qwen_client import QwenClient, ActionPayload
from edge_ie_agent import window_manager

class VisualAgent:
    """Autonomous Visual Agent controlling Edge IE Mode."""

    def __init__(
        self,
        config: Optional[Config] = None,
        client: Optional[QwenClient] = None,
        controller: Optional[Controller] = None,
        window_module=None
    ):
        self.config = config or load_config()
        self.client = client or QwenClient(self.config)
        self.controller = controller or Controller()
        self.wm = window_module or window_manager

    def run(self, task: str) -> str:
        """Executes the visual agent loop for the given task.
        
        Args:
            task: Natural language goal (e.g. "Tra cứu mã số thuế 0101234567").
            
        Returns:
            Completion summary message.
            
        Raises:
            TimeoutError: If max_steps is reached without completing.
            WindowNotFoundError: If the Edge window is not found.
        """
        print(f"\n[Agent] Bắt đầu nhiệm vụ: '{task}'")
        hwnd = self.wm.find_edge_window(self.config.edge_keyword)
        print(f"[Agent] Đã tìm thấy cửa sổ Edge (HWND: {hwnd})")

        step_history: List[str] = []

        for step in range(1, self.config.max_steps + 1):
            print(f"\n--- [Bước {step}/{self.config.max_steps}] ---")
            
            # 1. Capture current visual state
            screenshot, bounds = self.wm.capture_window(hwnd)
            print(f"[Agent] Đã chụp màn hình cửa sổ (Vùng: {bounds})")

            # 2. Ask Qwen Vision for reasoning and next action
            print("[Agent] Đang gửi ảnh lên Qwen Vision để suy luận...")
            payload: ActionPayload = self.client.predict_action(
                image=screenshot,
                task=task,
                step_history=step_history
            )

            print(f"[Qwen] Suy luận: {payload.thought}")
            print(f"[Qwen] Hành động: {payload.action.upper()}")

            # 3. Handle Completion
            if payload.action == "finish":
                msg = payload.message or "Nhiệm vụ đã hoàn thành thành công."
                print(f"[Agent] Hoàn thành: {msg}")
                return msg

            # 4. Execute UI Action
            step_desc = self._execute_action(payload, bounds)
            step_history.append(step_desc)

            # Small pause between steps for rendering
            time.sleep(0.5)

        raise TimeoutError(
            f"Agent đã đạt tới giới hạn tối đa {self.config.max_steps} bước mà chưa hoàn thành nhiệm vụ."
        )

    def _execute_action(self, payload: ActionPayload, bounds: tuple) -> str:
        """Executes the given ActionPayload using Controller and returns a step description."""
        left, top, width, height = bounds

        if payload.action in ("click", "double_click"):
            point = payload.point or [500, 500]
            sx, sy = normalize_to_screen(point, bounds)
            if payload.action == "double_click":
                self.controller.double_click(sx, sy)
                return f"Đã nhấp đúp tại tọa độ {point}"
            else:
                self.controller.click(sx, sy)
                return f"Đã bấm chuột tại tọa độ {point}"

        elif payload.action == "hover":
            point = payload.point or [500, 500]
            sx, sy = normalize_to_screen(point, bounds)
            self.controller.hover(sx, sy, duration=0.6)
            return f"Đã rê chuột (hover) tại {point} để mở menu con"

        elif payload.action == "type":
            text = payload.text or ""
            self.controller.paste_text(text, press_enter=payload.press_enter)
            return f"Đã điền văn bản '{text}' (Enter: {payload.press_enter})"

        elif payload.action == "scroll":
            point = payload.point or [500, 500]
            sx, sy = normalize_to_screen(point, bounds)
            self.controller.scroll_at(
                sx, sy,
                direction=payload.direction,
                amount=payload.amount
            )
            return f"Đã cuộn {payload.direction} tại {point} với lượng {payload.amount}"

        elif payload.action == "wait":
            time.sleep(payload.seconds)
            return f"Đã chờ {payload.seconds} giây"

        return f"Đã thực hiện {payload.action}"
