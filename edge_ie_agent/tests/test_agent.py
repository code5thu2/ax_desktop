import time
from unittest.mock import MagicMock, patch
import pytest
from PIL import Image
from edge_ie_agent.agent import VisualAgent
from edge_ie_agent.qwen_client import ActionPayload
from edge_ie_agent.config import Config

def test_agent_completes_on_finish():
    mock_client = MagicMock()
    mock_client.predict_action.return_value = ActionPayload(
        thought="Đã thấy kết quả tra cứu",
        action="finish",
        message="Mã số thuế hợp lệ, trạng thái đang hoạt động."
    )
    
    mock_wm_module = MagicMock()
    mock_wm_module.find_edge_window.return_value = 12345
    mock_img = Image.new("RGB", (800, 600), color="white")
    mock_wm_module.capture_window.return_value = (mock_img, (100, 100, 800, 600))
    
    mock_controller = MagicMock()
    
    cfg = Config(api_key="mock", max_steps=5)
    agent = VisualAgent(
        config=cfg,
        client=mock_client,
        controller=mock_controller,
        window_module=mock_wm_module
    )
    
    result = agent.run("Kiểm tra mã số thuế")
    assert result == "Mã số thuế hợp lệ, trạng thái đang hoạt động."
    assert mock_wm_module.find_edge_window.called
    assert mock_client.predict_action.called

def test_agent_executes_actions_in_loop():
    mock_client = MagicMock()
    # Step 1: Click
    action1 = ActionPayload(thought="Click nút", action="click", point=[500, 500])
    # Step 2: Hover
    action2 = ActionPayload(thought="Hover menu", action="hover", point=[200, 300])
    # Step 3: Type
    action3 = ActionPayload(thought="Type search", action="type", text="test query", press_enter=True)
    # Step 4: Finish
    action4 = ActionPayload(thought="Done", action="finish", message="Hoàn thành tất cả")
    
    mock_client.predict_action.side_effect = [action1, action2, action3, action4]
    
    mock_wm_module = MagicMock()
    mock_wm_module.find_edge_window.return_value = 12345
    mock_img = Image.new("RGB", (800, 600), color="white")
    mock_wm_module.capture_window.return_value = (mock_img, (0, 0, 1000, 1000))
    
    mock_controller = MagicMock()
    
    cfg = Config(api_key="mock", max_steps=10)
    agent = VisualAgent(
        config=cfg,
        client=mock_client,
        controller=mock_controller,
        window_module=mock_wm_module
    )
    
    result = agent.run("Thao tác menu và tìm kiếm")
    assert result == "Hoàn thành tất cả"
    assert mock_controller.click.call_count == 1
    assert mock_controller.hover.call_count == 1
    assert mock_controller.paste_text.call_count == 1

def test_agent_stops_at_max_steps():
    mock_client = MagicMock()
    # Continuous wait action without finish
    mock_client.predict_action.return_value = ActionPayload(
        thought="Still waiting", action="wait", seconds=0.1
    )
    
    mock_wm_module = MagicMock()
    mock_wm_module.find_edge_window.return_value = 12345
    mock_img = Image.new("RGB", (800, 600), color="white")
    mock_wm_module.capture_window.return_value = (mock_img, (0, 0, 1000, 1000))
    
    mock_controller = MagicMock()
    
    cfg = Config(api_key="mock", max_steps=3)
    agent = VisualAgent(
        config=cfg,
        client=mock_client,
        controller=mock_controller,
        window_module=mock_wm_module
    )
    
    with pytest.raises(TimeoutError):
        agent.run("Nhiệm vụ lặp vô tận")
