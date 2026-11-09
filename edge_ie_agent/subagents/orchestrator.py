"""GLM Main Orchestrator Agent: Fast Planner & Task Dispatcher (Claude Code Style).
Controls the high-level workflow, maintains subtasks, and invokes specialized Subagents.
"""
import re
import json
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from openai import OpenAI
from edge_ie_agent.config import Config

ORCHESTRATOR_SYSTEM_PROMPT = """Bạn là Agent Nhạc trưởng (Main Orchestrator) theo phong cách Claude Code, chuyên tự động hóa thao tác trên Microsoft Edge IE Mode.
Bạn có tốc độ suy luận cực nhanh, chịu trách nhiệm quản lý mục tiêu tổng thể và phân chia công việc thành các bước nhỏ.

BẠN CÓ CÁC CÔNG CỤ VÀ SUBAGENT SAU:
1. "invoke_vision_subagent": Triệu hồi Subagent Trinh sát (Qwen Vision) để soi ảnh màn hình tìm tọa độ hoặc kiểm tra trạng thái giao diện.
   Format: {"thought": "...", "action": "invoke_vision_subagent", "instruction": "Cần tìm vị trí của menu hoặc nút gì..."}

2. "click": Bấm chuột vào tọa độ chuẩn hóa [x, y] (lấy từ kết quả của Vision Subagent).
   Format: {"thought": "...", "action": "click", "point": [x, y]}

3. "hover": Rê chuột vào mục cha để làm bung menu con (onmouseover).
   Format: {"thought": "...", "action": "hover", "point": [x, y]}

4. "type": Điền văn bản tiếng Việt qua Clipboard an toàn.
   Format: {"thought": "...", "action": "type", "text": "...", "press_enter": false}

5. "scroll": Cuộn chuột tại vị trí chỉ định.
   Format: {"thought": "...", "action": "scroll", "point": [x, y], "direction": "down|up", "amount": 3}

6. "wait": Đợi trang tải.
   Format: {"thought": "...", "action": "wait", "seconds": 2}

7. "finish": Báo cáo hoàn thành nhiệm vụ.
   Format: {"thought": "...", "action": "finish", "message": "Tóm tắt kết quả..."}

QUY TẮC AN TOÀN (HUMAN-IN-THE-LOOP):
- Nếu một hành động có tính chất NHẠY CẢM hoặc KHÔNG THỂ ĐẢO NGƯỢC (ví dụ: bấm nút "Nộp tờ khai", "Ký số", "Xóa dữ liệu", "Hủy bỏ", "Thanh toán", "Submit"):
  BẮT BUỘC phải thêm:
  "is_sensitive": true,
  "sensitive_reason": "Giải thích ngắn gọn lý do tại sao bước này cần con người xác nhận trước khi bấm"
- Với các hành động duyệt web bình thường (mở menu, xem trang, gõ ô tìm kiếm, tra cứu thông tin):
  "is_sensitive": false

CHIẾN LƯỢC ĐIỀU PHỐI (CLAUDE CODE SUBAGENT PATTERN):
- Khi cần bấm vào một nút/menu mới: Hãy gọi "invoke_vision_subagent" trước để lấy tọa độ chính xác.
- Khi Vision Subagent trả về tọa độ [x, y]: Bước tiếp theo bạn ra lệnh "click" hoặc "hover" vào tọa độ đó.
- Nếu là menu đa cấp: Sau khi "hover", hãy gọi lại "invoke_vision_subagent" để xác nhận menu con đã mở ra và lấy tọa độ menu con.
- Sau khi điền xong và bấm tra cứu: Gọi "invoke_vision_subagent" để đọc kết quả trên màn hình và hoàn thành ("finish").

LUÔN TRẢ VỀ DUY NHẤT 1 JSON HỢP LỆ.
"""

@dataclass
class OrchestratorDecision:
    thought: str
    action: str
    instruction: Optional[str] = None
    point: Optional[List[float]] = None
    text: Optional[str] = None
    press_enter: bool = False
    direction: str = "down"
    amount: int = 3
    seconds: float = 2.0
    message: Optional[str] = None
    is_sensitive: bool = False
    sensitive_reason: Optional[str] = None

class OrchestratorAgent:
    """Main Orchestrator powered by GLM (Fast Text Planner)."""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def decide_next_step(self, task: str, conversation_log: List[str]) -> OrchestratorDecision:
        """Asks GLM to reason and choose the next action or subagent dispatch."""
        log_text = "\n".join(conversation_log) if conversation_log else "Bắt đầu nhiệm vụ mới."

        user_prompt = f"""MỤC TIÊU CỦA NGƯỜI DÙNG:
{task}

NHẬT KÝ ĐIỀU PHỐI VÀ KẾT QUẢ TỪ SUBAGENTS:
{log_text}

Dựa trên tình hình hiện tại, hãy đưa ra quyết định tiếp theo dạng JSON."""

        response = self.client.chat.completions.create(
            model=self.config.glm_model,
            messages=[
                {"role": "system", "content": ORCHESTRATOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=600
        )

        content = response.choices[0].message.content or ""
        return self._parse_decision(content)

    def _parse_decision(self, raw_text: str) -> OrchestratorDecision:
        text = raw_text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        else:
            brace_match = re.search(r"\{[\s\S]*\}", text)
            if brace_match:
                text = brace_match.group(0)

        data = json.loads(text)
        return OrchestratorDecision(
            thought=str(data.get("thought", "")),
            action=str(data.get("action", "")).strip().lower(),
            instruction=data.get("instruction"),
            point=data.get("point"),
            text=data.get("text"),
            press_enter=bool(data.get("press_enter", False)),
            direction=str(data.get("direction", "down")),
            amount=int(data.get("amount", 3)),
            seconds=float(data.get("seconds", 2.0)),
            message=data.get("message"),
            is_sensitive=bool(data.get("is_sensitive", False)),
            sensitive_reason=data.get("sensitive_reason")
        )
