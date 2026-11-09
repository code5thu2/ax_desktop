from unittest.mock import MagicMock
import pytest
from PIL import Image
from edge_ie_agent.agent import VisualAgent
from edge_ie_agent.subagents.orchestrator import OrchestratorDecision
from edge_ie_agent.subagents.vision_subagent import VisionInspectionResult
from edge_ie_agent.config import Config

def test_multi_agent_subagent_dispatch_and_finish():
    mock_orchestrator = MagicMock()
    step1 = OrchestratorDecision(
        thought="Cần tìm vị trí nút Báo cáo",
        action="invoke_vision_subagent",
        instruction="Tìm vị trí menu Báo cáo"
    )
    step2 = OrchestratorDecision(
        thought="Vision subagent đã tìm thấy menu Báo cáo tại [250, 150]",
        action="click",
        point=[250, 150]
    )
    step3 = OrchestratorDecision(
        thought="Đã xong",
        action="finish",
        message="Đã mở menu Báo cáo thành công"
    )
    mock_orchestrator.decide_next_step.side_effect = [step1, step2, step3]

    mock_vision = MagicMock()
    mock_vision.inspect.return_value = VisionInspectionResult(
        found=True,
        description="Thấy menu Báo cáo",
        point=[250, 150],
        is_menu_expanded=False
    )

    mock_wm = MagicMock()
    mock_wm.find_edge_window.return_value = 1001
    mock_wm.get_window_bounds.return_value = (0, 0, 1000, 1000)
    mock_wm.capture_window.return_value = (Image.new("RGB", (100, 100)), (0, 0, 1000, 1000))
    mock_wm.wait_until_stable.return_value = True

    mock_controller = MagicMock()

    cfg = Config(api_key="mock", max_steps=5)
    agent = VisualAgent(
        config=cfg,
        orchestrator=mock_orchestrator,
        vision_subagent=mock_vision,
        controller=mock_controller,
        window_module=mock_wm
    )

    result = agent.run("Mở menu Báo cáo")
    assert result == "Đã mở menu Báo cáo thành công"
    assert mock_vision.inspect.called
    assert mock_controller.click.called
    assert mock_wm.wait_until_stable.called

def test_human_in_the_loop_rejection():
    mock_orchestrator = MagicMock()
    # Sensitive action: Click submit
    sensitive_step = OrchestratorDecision(
        thought="Chuẩn bị nộp tờ khai",
        action="click",
        point=[800, 900],
        is_sensitive=True,
        sensitive_reason="Bấm nút Nộp tờ khai thuế"
    )
    # Next step: Finish after user rejection
    finish_step = OrchestratorDecision(
        thought="Người dùng từ chối, dừng lại",
        action="finish",
        message="Đã dừng theo yêu cầu của người dùng"
    )
    mock_orchestrator.decide_next_step.side_effect = [sensitive_step, finish_step]

    mock_wm = MagicMock()
    mock_wm.find_edge_window.return_value = 1001
    mock_wm.get_window_bounds.return_value = (0, 0, 1000, 1000)

    mock_controller = MagicMock()
    # User rejects confirmation
    mock_confirm = MagicMock(return_value=False)

    cfg = Config(api_key="mock", max_steps=5)
    agent = VisualAgent(
        config=cfg,
        orchestrator=mock_orchestrator,
        vision_subagent=MagicMock(),
        controller=mock_controller,
        window_module=mock_wm,
        confirm_callback=mock_confirm
    )

    result = agent.run("Nộp tờ khai")
    assert result == "Đã dừng theo yêu cầu của người dùng"
    assert mock_confirm.called
    # Controller should NOT have clicked because user rejected
    assert mock_controller.click.call_count == 0

def test_multi_agent_timeout():
    mock_orchestrator = MagicMock()
    mock_orchestrator.decide_next_step.return_value = OrchestratorDecision(
        thought="Waiting", action="wait", seconds=0.01
    )
    mock_wm = MagicMock()
    mock_wm.find_edge_window.return_value = 1001
    mock_wm.get_window_bounds.return_value = (0, 0, 1000, 1000)

    cfg = Config(api_key="mock", max_steps=2)
    agent = VisualAgent(
        config=cfg,
        orchestrator=mock_orchestrator,
        vision_subagent=MagicMock(),
        controller=MagicMock(),
        window_module=mock_wm
    )

    with pytest.raises(TimeoutError):
        agent.run("Vòng lặp quá số bước")
