"""Multi-Agent ReAct Coordinator (Claude Code Subagent Pattern).
Combines GLM (Main Orchestrator) and Qwen (Vision Subagent).
"""
import time
from typing import Optional, List
from PIL import Image

from edge_ie_agent.config import Config, load_config
from edge_ie_agent.coordinate import normalize_to_screen
from edge_ie_agent.controller import Controller
from edge_ie_agent.subagents.orchestrator import OrchestratorAgent, OrchestratorDecision
from edge_ie_agent.subagents.vision_subagent import VisionSubagent, VisionInspectionResult
from edge_ie_agent import window_manager

class VisualAgent:
    """Claude Code Style Multi-Agent System:
    - GLM 5.2: Main Orchestrator (Fast Text Planner)
    - Qwen 33.8: Vision Subagent (Screen Perception & Grounding)
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        orchestrator: Optional[OrchestratorAgent] = None,
        vision_subagent: Optional[VisionSubagent] = None,
        controller: Optional[Controller] = None,
        window_module=None
    ):
        self.config = config or load_config()
        self.orchestrator = orchestrator or OrchestratorAgent(self.config)
        self.vision_subagent = vision_subagent or VisionSubagent(self.config)
        self.controller = controller or Controller()
        self.wm = window_module or window_manager

    def run(self, task: str) -> str:
        """Runs the multi-agent task loop."""
        print(f"\n==================================================")
        print(f"[*] Bắt đầu nhiệm vụ: '{task}'")
        print(f"[*] Nhạc trưởng (Main Agent): {self.config.glm_model}")
        print(f"[*] Trinh sát (Vision Subagent): {self.config.qwen_model}")
        print(f"==================================================\n")

        hwnd = self.wm.find_edge_window(self.config.edge_keyword)
        print(f"[Main] Đã kết nối cửa sổ Edge (HWND: {hwnd})")

        conversation_log: List[str] = []

        for step in range(1, self.config.max_steps + 1):
            print(f"\n--- [Bước {step}/{self.config.max_steps}] ---")
            
            # 1. Main Agent (GLM) plans and decides
            decision: OrchestratorDecision = self.orchestrator.decide_next_step(
                task=task,
                conversation_log=conversation_log
            )

            print(f"[GLM Nhạc trưởng] Suy nghĩ: {decision.thought}")
            print(f"[GLM Nhạc trưởng] Quyết định: {decision.action.upper()}")

            # 2. Finish action
            if decision.action == "finish":
                msg = decision.message or "Nhiệm vụ đã hoàn thành."
                print(f"\n🎉 [Hoàn thành]: {msg}")
                return msg

            # 3. Subagent Dispatch: Call Qwen Vision
            if decision.action == "invoke_vision_subagent":
                instruction = decision.instruction or "Soi màn hình và tìm tọa độ phần tử cần thao tác."
                print(f"  ↪ [DISPATCH SUBAGENT] Triệu hồi Qwen Vision Subagent: '{instruction}'")
                
                # Capture window
                screenshot, bounds = self.wm.capture_window(hwnd)
                
                # Run subagent in isolated context
                v_res: VisionInspectionResult = self.vision_subagent.inspect(
                    image=screenshot,
                    instruction=instruction
                )
                
                subagent_report = (
                    f"Kết quả từ Vision Subagent: "
                    f"Mô tả: '{v_res.description}', "
                    f"Tọa độ tìm thấy: {v_res.point}, "
                    f"Menu con đang mở: {v_res.is_menu_expanded}"
                )
                if v_res.read_text:
                    subagent_report += f", Chữ đọc được: '{v_res.read_text}'"

                print(f"  ↩ [SUBAGENT REPORT] {subagent_report}")
                conversation_log.append(f"Bước {step}: {subagent_report}")
                time.sleep(0.3)
                continue

            # 4. Action Execution via Controller
            bounds = self.wm.get_window_bounds(hwnd)
            action_desc = self._execute_action(decision, bounds)
            conversation_log.append(f"Bước {step}: {action_desc}")
            time.sleep(0.5)

        raise TimeoutError(f"Đã đạt tới giới hạn {self.config.max_steps} bước mà chưa xong.")

    def _execute_action(self, decision: OrchestratorDecision, bounds: tuple) -> str:
        if decision.action in ("click", "double_click"):
            point = decision.point or [500, 500]
            sx, sy = normalize_to_screen(point, bounds)
            if decision.action == "double_click":
                self.controller.double_click(sx, sy)
                return f"Đã nhấp đúp tại tọa độ {point}"
            else:
                self.controller.click(sx, sy)
                return f"Đã click tại tọa độ {point}"

        elif decision.action == "hover":
            point = decision.point or [500, 500]
            sx, sy = normalize_to_screen(point, bounds)
            self.controller.hover(sx, sy, duration=0.6)
            return f"Đã hover chuột tại tọa độ {point} (mở menu con)"

        elif decision.action == "type":
            text = decision.text or ""
            self.controller.paste_text(text, press_enter=decision.press_enter)
            return f"Đã điền văn bản '{text}' qua Clipboard"

        elif decision.action == "scroll":
            point = decision.point or [500, 500]
            sx, sy = normalize_to_screen(point, bounds)
            self.controller.scroll_at(sx, sy, direction=decision.direction, amount=decision.amount)
            return f"Đã cuộn {decision.direction} tại {point}"

        elif decision.action == "wait":
            time.sleep(decision.seconds)
            return f"Đã chờ {decision.seconds} giây"

        return f"Đã thực hiện {decision.action}"
