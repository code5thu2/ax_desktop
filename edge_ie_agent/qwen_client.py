"""Qwen Vision client communicating via OpenAI-compatible endpoint (AIPRO)."""
import re
import json
import base64
import io
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from PIL import Image
from openai import OpenAI
from edge_ie_agent.config import Config

VALID_ACTIONS = {"click", "double_click", "hover", "type", "scroll", "wait", "finish"}

class InvalidActionError(Exception):
    """Raised when the LLM returns an invalid action type or malformed payload."""
    pass

@dataclass
class ActionPayload:
    thought: str
    action: str
    point: Optional[List[float]] = None
    text: Optional[str] = None
    press_enter: bool = False
    direction: str = "down"
    amount: int = 3
    seconds: float = 2.0
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionPayload":
        action = str(data.get("action", "")).strip().lower()
        if action not in VALID_ACTIONS:
            raise InvalidActionError(f"Hành động không hợp lệ: '{action}'. Phải là một trong {VALID_ACTIONS}")
            
        thought = str(data.get("thought", "")).strip()
        point = data.get("point")
        text = data.get("text")
        press_enter = bool(data.get("press_enter", False))
        direction = str(data.get("direction", "down")).strip().lower()
        amount = int(data.get("amount", 3))
        seconds = float(data.get("seconds", 2.0))
        message = data.get("message")

        return cls(
            thought=thought,
            action=action,
            point=point,
            text=text,
            press_enter=press_enter,
            direction=direction,
            amount=amount,
            seconds=seconds,
            message=message
        )

def clean_json_response(raw_text: str) -> Dict[str, Any]:
    """Extracts and parses a JSON object from raw model output."""
    text = raw_text.strip()
    
    # 1. Try stripping markdown fences ```json ... ```
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if fence_match:
        text = fence_match.group(1).strip()
        
    # 2. Try direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # 3. Fallback: Search for the first outer {...} object
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            pass
            
    raise ValueError(f"Không thể trích xuất JSON hợp lệ từ phản hồi của model:\n{raw_text}")

SYSTEM_PROMPT = """Bạn là một AI Agent chuyên điều khiển giao diện web cổ điển chạy trên Microsoft Edge ở chế độ IE Mode.
Bạn sẽ nhận được ảnh chụp màn hình hiện tại của cửa sổ Edge, cùng với nhiệm vụ của người dùng và lịch sử các bước đã thực hiện.

QUY TẮC TỌA ĐỘ:
- Hệ tọa độ chuẩn hóa từ 0 đến 1000 cho cả chiều X (ngang) và Y (dọc).
- [0, 0] là góc trên cùng bên trái của cửa sổ.
- [1000, 1000] là góc dưới cùng bên phải.
- [500, 500] là tâm cửa sổ.

CÁC HÀNH ĐỘNG HỖ TRỢ:
1. {"thought": "...", "action": "click", "point": [x, y]}
   -> Bấm chuột trái vào nút, liên kết hoặc ô nhập liệu.
2. {"thought": "...", "action": "double_click", "point": [x, y]}
   -> Nhấp đúp chuột.
3. {"thought": "...", "action": "hover", "point": [x, y]}
   -> RÊ CHUỘT vào danh mục cha (đặc biệt quan trọng với menu đa cấp onmouseover để làm xổ menu con ra).
4. {"thought": "...", "action": "type", "text": "nội dung", "press_enter": false}
   -> Điền văn bản vào ô đang chọn (sẽ tự động dán qua Clipboard, hỗ trợ tiếng Việt có dấu chuẩn xác).
5. {"thought": "...", "action": "scroll", "point": [x, y], "direction": "down|up", "amount": 3}
   -> Cuộn chuột tại vị trí chỉ định (rất hữu ích khi cuộn riêng cột menu bên trái).
6. {"thought": "...", "action": "wait", "seconds": 2}
   -> Chờ trang tải hoặc chờ popup mở.
7. {"thought": "...", "action": "finish", "message": "kết quả nhiệm vụ"}
   -> Báo cáo hoàn thành nhiệm vụ và tóm tắt kết quả tìm được.

LƯU Ý QUAN TRỌNG:
- Trả về DUY NHẤT một chuỗi JSON hợp lệ, không giải thích dài dòng bên ngoài JSON.
"""

class QwenClient:
    """Client for Qwen Vision model on AIPRO endpoint."""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def encode_image(self, image: Image.Image) -> str:
        """Encodes PIL Image to a Base64 JPEG string."""
        buffered = io.BytesIO()
        rgb_image = image.convert("RGB")
        rgb_image.save(buffered, format="JPEG", quality=90)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def predict_action(
        self,
        image: Image.Image,
        task: str,
        step_history: List[str]
    ) -> ActionPayload:
        """Sends screenshot and task context to Qwen Vision and returns the next action."""
        b64_img = self.encode_image(image)
        
        history_text = "\n".join([f"- Bước {i+1}: {step}" for i, step in enumerate(step_history)])
        if not history_text:
            history_text = "Chưa có bước nào trước đó."

        user_prompt = f"""MỤC TIÊU CỦA NGƯỜI DÙNG:
{task}

LỊCH SỬ CÁC BƯỚC ĐÃ LÀM:
{history_text}

Hãy quan sát ảnh chụp màn hình đính kèm, xác định trạng thái hiện tại và đưa ra hành động tiếp theo dạng JSON."""

        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_img}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            max_tokens=800
        )

        content = response.choices[0].message.content or ""
        parsed_dict = clean_json_response(content)
        return ActionPayload.from_dict(parsed_dict)
