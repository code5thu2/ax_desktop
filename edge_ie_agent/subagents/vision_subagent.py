"""Qwen Vision Subagent: Specialized Screen Navigator and Eye of the Agent.
Operates in an isolated context, taking screenshots and returning visual grounding data to the Main Agent.
"""
import io
import re
import json
import base64
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from PIL import Image
from openai import OpenAI
from edge_ie_agent.config import Config

@dataclass
class VisionInspectionResult:
    found: bool
    description: str
    point: Optional[List[float]] = None
    is_menu_expanded: bool = False
    read_text: Optional[str] = None

VISION_SUBAGENT_PROMPT = """Bạn là Subagent Trinh sát Thị giác (Vision Subagent) chuyên soi màn hình Microsoft Edge (IE Mode).
Bạn nhận ảnh chụp màn hình và câu hỏi/yêu cầu cụ thể từ Agent Nhạc trưởng (Main Orchestrator).

NHIỆM VỤ CỦA BẠN:
1. Quan sát ảnh chụp màn hình hiện tại.
2. Định vị chính xác tọa độ phần tử được yêu cầu theo hệ tọa độ chuẩn hóa [0, 1000]:
   - [0, 0] là góc trên cùng bên trái của ảnh.
   - [1000, 1000] là góc dưới cùng bên phải của ảnh.
   - [500, 500] là tâm ảnh.
3. Kiểm tra trạng thái giao diện: Menu con có đang mở hay không? Có popup cảnh báo không? Kết quả tra cứu có hiện ra không?

QUY ĐỊNH PHẢN HỒI:
Trả về DUY NHẤT một chuỗi JSON hợp lệ theo cấu trúc sau:
{
  "found": true | false,
  "description": "Mô tả ngắn gọn những gì bạn thấy tại vùng mục tiêu",
  "point": [x, y],
  "is_menu_expanded": true | false,
  "read_text": "Chữ đọc được trên màn hình nếu được yêu cầu"
}
"""

class VisionSubagent:
    """Specialized Subagent for Visual Perception using Qwen Vision."""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )

    def encode_image(self, image: Image.Image) -> str:
        buffered = io.BytesIO()
        rgb_image = image.convert("RGB")
        rgb_image.save(buffered, format="JPEG", quality=90)
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def inspect(self, image: Image.Image, instruction: str) -> VisionInspectionResult:
        """Runs the vision inspection in an isolated subagent context."""
        b64_img = self.encode_image(image)
        
        user_content = f"YÊU CẦU SOI MÀN HÌNH TỪ NHẠC TRƯỞNG:\n{instruction}"

        response = self.client.chat.completions.create(
            model=self.config.qwen_model,
            messages=[
                {"role": "system", "content": VISION_SUBAGENT_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_content},
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
            max_tokens=600
        )

        content = response.choices[0].message.content or ""
        return self._parse_result(content)

    def _parse_result(self, raw_text: str) -> VisionInspectionResult:
        text = raw_text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if fence_match:
            text = fence_match.group(1).strip()
        else:
            brace_match = re.search(r"\{[\s\S]*\}", text)
            if brace_match:
                text = brace_match.group(0)

        try:
            data = json.loads(text)
        except Exception:
            data = {"found": False, "description": raw_text[:200], "point": None}

        return VisionInspectionResult(
            found=bool(data.get("found", True)),
            description=str(data.get("description", "")),
            point=data.get("point"),
            is_menu_expanded=bool(data.get("is_menu_expanded", False)),
            read_text=data.get("read_text")
        )
