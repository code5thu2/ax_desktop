from unittest.mock import MagicMock
import pytest
from PIL import Image
from edge_ie_agent.agent import VisualAgent
from edge_ie_agent.subagents.orchestrator import OrchestratorDecision
from edge_ie_agent.subagents.vision_subagent import VisionInspectionResult
from edge_ie_agent.config import Config

def test_multi_agent_subagent_dispatch_and_finish():
    # Setup mocks
    mock_orchestrator = MagicMock()
    # Step 1: GLM decides to invoke Vision Subagent
    step1 = OrchestratorDecision(
        thought="Cần tìm vị trí nút Báo cáo",
        action="invoke_vision_subagent",
        instruction="Tìm vị trí menu Báo cáo"
    )
    # Step 2: GLM decides to click on coordinate from subagent
    step2 = OrchestratorDecision(
        thought="Vision subagent đã tìm thấy menu Báo cáo tại [250, 150]",
        action="click",
        point=[250, 150]
    )
    # Step 3: GLM completes
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
