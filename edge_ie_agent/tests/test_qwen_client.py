import io
import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
from edge_ie_agent.config import Config
from edge_ie_agent.qwen_client import (
    clean_json_response,
    ActionPayload,
    QwenClient,
    InvalidActionError,
)

def test_clean_json_with_markdown_fences():
    raw = '```json\n{"thought": "Click login", "action": "click", "point": [450, 300]}\n```'
    parsed = clean_json_response(raw)
    assert parsed["action"] == "click"
    assert parsed["point"] == [450, 300]
    assert parsed["thought"] == "Click login"

def test_clean_json_embedded_in_text():
    raw = 'Tôi sẽ chọn nút này:\n{"thought": "Hover menu", "action": "hover", "point": [100, 200]}\nChúc bạn thành công.'
    parsed = clean_json_response(raw)
    assert parsed["action"] == "hover"
    assert parsed["point"] == [100, 200]

def test_action_payload_validation():
    # Valid payload
    payload = ActionPayload.from_dict({
        "thought": "Type tax code",
        "action": "type",
        "text": "0101234567",
        "press_enter": True
    })
    assert payload.action == "type"
    assert payload.text == "0101234567"
    assert payload.press_enter is True

    # Invalid action raises error
    with pytest.raises(InvalidActionError):
        ActionPayload.from_dict({"thought": "Bad", "action": "fly_to_moon"})

def test_qwen_client_predict_action():
    config = Config(api_key="mock-key", base_url="https://mock.api/v1", model_name="qwen-vl-mock")
    client = QwenClient(config=config)
    
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = '```json\n{"thought": "Click Tra cuu", "action": "click", "point": [300, 400]}\n```'
    mock_response.choices = [mock_choice]
    
    img = Image.new("RGB", (100, 100), color="white")
    
    with patch.object(client.client.chat.completions, "create", return_value=mock_response):
        payload = client.predict_action(
            image=img,
            task="Tra cứu thông tin",
            step_history=["Đã mở trang"]
        )
        assert payload.action == "click"
        assert payload.point == [300, 400]
