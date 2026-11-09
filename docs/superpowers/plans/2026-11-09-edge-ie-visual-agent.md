# Edge IE Mode Visual Automation Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a modular Python Visual AI Agent that automates legacy websites running inside Microsoft Edge IE Mode using Qwen Vision (via AIPRO OpenAI-compatible API) and PyAutoGUI.

**Architecture:** The agent operates in a ReAct loop: it detects and focuses the Edge window, captures a high-resolution screenshot of the browser region, normalizes coordinates to a 0–1000 scale, queries Qwen Vision for structured JSON actions (`click`, `hover`, `scroll`, `type` via clipboard, `wait`, `finish`), and executes them safely via OS mouse/keyboard automation.

**Tech Stack:** Python 3.10+, `openai` (AIPRO client), `pyautogui` (mouse/keyboard automation), `pywin32` (Windows window management), `pillow` (image capture/processing), `pyperclip` (clipboard text injection), `pytest` (unit testing).

**Spec:** [docs/superpowers/specs/2026-11-09-edge-ie-visual-agent-design.md](file:///D:/mcp-server-test/docs/superpowers/specs/2026-11-09-edge-ie-visual-agent-design.md)

## Global Constraints

- Platform: Windows 10/11 only.
- Model provider: AIPRO OpenAI-compatible endpoint (`/v1/chat/completions`).
- Browser target: Microsoft Edge running legacy websites in IE Mode.
- Coordinate system: Normalized `[0, 1000]` relative to the captured window bounding box.
- Text input: Clipboard paste (`Ctrl+V`) via `pyperclip` to avoid Unikey / Vietnamese IME corruption.
- Mouse fail-safe: `pyautogui.FAILSAFE = True` enabled at all times.

## Review Focus

1. **Window not found or minimized:** If Edge is minimized or no window title matches `Edge`, `window_manager` must raise an actionable error instead of crashing.
2. **Normalized coordinates out of bounds:** If Qwen outputs `point` outside `[0, 1000]` (e.g. negative or > 1000), `coordinate.py` must clamp safely to `[0, 1000]`.
3. **Invalid or malformed JSON from Qwen:** If the model returns markdown fences or conversational text alongside JSON, `qwen_client` must extract and validate the JSON object cleanly.
4. **ActiveX/Security modal blocking input:** The ReAct loop must re-capture and feed the screen state so Qwen can identify and click the OK/Dismiss button.
5. **Infinite loop / unresponsive page:** The agent must enforce `max_steps` and report a timeout error rather than looping indefinitely.

---

### Task 1: Project Setup, Configuration, and Coordinate Normalization

**Files:**
- Create: `edge_ie_agent/requirements.txt`
- Create: `edge_ie_agent/.env.example`
- Create: `edge_ie_agent/config.py`
- Create: `edge_ie_agent/coordinate.py`
- Test: `edge_ie_agent/tests/test_coordinate.py`
- Test: `edge_ie_agent/tests/test_config.py`

**Interfaces:**
- Consumes: None
- Produces:
  - `Config`: Dataclass with `api_key: str`, `base_url: str`, `model_name: str`, `edge_keyword: str`, `max_steps: int`
  - `load_config(env_path: Optional[str] = None) -> Config`
  - `normalize_to_screen(point: tuple[float, float], window_rect: tuple[int, int, int, int]) -> tuple[int, int]`
  - `clamp_point(point: tuple[float, float]) -> tuple[float, float]`

- [ ] **Step 1: Write the failing tests for coordinate normalization and config**

```python
# edge_ie_agent/tests/test_coordinate.py
import pytest
from edge_ie_agent.coordinate import normalize_to_screen, clamp_point

def test_normalize_center():
    # Window rect: (left=100, top=100, width=1000, height=800)
    rect = (100, 100, 1000, 800)
    screen_x, screen_y = normalize_to_screen((500, 500), rect)
    assert screen_x == 600
    assert screen_y == 500

def test_clamp_point():
    assert clamp_point((-50, 1200)) == (0.0, 1000.0)
    assert clamp_point((500, 500)) == (500.0, 500.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest edge_ie_agent/tests/test_coordinate.py -v`  
Expected: FAIL with ModuleNotFoundError or import error.

- [ ] **Step 3: Implement `requirements.txt`, `.env.example`, `config.py`, and `coordinate.py`**

Create `edge_ie_agent/requirements.txt`:
```text
openai>=1.30.0
pyautogui>=0.9.54
pywin32>=306
pillow>=10.0.0
pyperclip>=1.8.2
python-dotenv>=1.0.0
pytest>=8.0.0
```

Implement `edge_ie_agent/coordinate.py` with `clamp_point(point: tuple[float, float]) -> tuple[float, float]` and `normalize_to_screen(point: tuple[float, float], window_rect: tuple[int, int, int, int]) -> tuple[int, int]`.

Implement `edge_ie_agent/config.py` loading environment variables with defaults.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest edge_ie_agent/tests/ -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add edge_ie_agent/
git commit -m "feat(edge_agent): add config and coordinate normalization engine"
```

---

### Task 2: Window Management and Screenshot Capture

**Files:**
- Create: `edge_ie_agent/window_manager.py`
- Test: `edge_ie_agent/tests/test_window_manager.py`

**Interfaces:**
- Consumes: None
- Produces:
  - `find_edge_window(title_keyword: str = "Edge") -> int (hwnd)`
  - `get_window_bounds(hwnd: int) -> tuple[int, int, int, int]` (returns `left, top, width, height`)
  - `focus_window(hwnd: int) -> None`
  - `capture_window(hwnd: int) -> tuple[PIL.Image.Image, tuple[int, int, int, int]]`

- [ ] **Step 1: Write unit tests for window bounds calculations and mocks**

```python
# edge_ie_agent/tests/test_window_manager.py
from unittest.mock import patch, MagicMock
import pytest
from edge_ie_agent.window_manager import get_window_bounds

def test_get_window_bounds():
    with patch("win32gui.GetWindowRect") as mock_rect:
        mock_rect.return_value = (50, 50, 850, 650)
        bounds = get_window_bounds(12345)
        assert bounds == (50, 50, 800, 600)  # left, top, width, height
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest edge_ie_agent/tests/test_window_manager.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `window_manager.py` using `pywin32` and `PIL.ImageGrab`**

Implement:
- `find_edge_window`: Iterates via `win32gui.EnumWindows`, finds visible window matching `title_keyword`, restores if minimized.
- `get_window_bounds`: Returns `(left, top, right - left, bottom - top)`.
- `focus_window`: Brings window to foreground with `win32gui.SetForegroundWindow`.
- `capture_window`: Uses `PIL.ImageGrab.grab(bbox=(left, top, right, bottom))` and returns `(image, bounds)`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest edge_ie_agent/tests/test_window_manager.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add edge_ie_agent/window_manager.py edge_ie_agent/tests/test_window_manager.py
git commit -m "feat(edge_agent): implement window manager and screenshot capture"
```

---

### Task 3: Input Automation Controller (Mouse, Hover, Scroll, Paste)

**Files:**
- Create: `edge_ie_agent/controller.py`
- Test: `edge_ie_agent/tests/test_controller.py`

**Interfaces:**
- Consumes: `coordinate.normalize_to_screen`
- Produces:
  - `Controller`:
    - `click(screen_x: int, screen_y: int) -> None`
    - `double_click(screen_x: int, screen_y: int) -> None`
    - `hover(screen_x: int, screen_y: int, duration: float = 0.5) -> None`
    - `scroll_at(screen_x: int, screen_y: int, direction: str, amount: int = 3) -> None`
    - `paste_text(text: str, press_enter: bool = False) -> None`

- [ ] **Step 1: Write unit tests for Controller dispatch**

```python
# edge_ie_agent/tests/test_controller.py
from unittest.mock import patch, MagicMock
from edge_ie_agent.controller import Controller

def test_paste_text_uses_clipboard():
    controller = Controller()
    with patch("pyperclip.copy") as mock_copy, \
         patch("pyautogui.hotkey") as mock_hotkey:
        controller.paste_text("Mã số thuế 0101234567", press_enter=True)
        mock_copy.assert_called_once_with("Mã số thuế 0101234567")
        mock_hotkey.assert_any_call("ctrl", "v")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest edge_ie_agent/tests/test_controller.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `controller.py`**

Implement `Controller` class:
- Sets `pyautogui.FAILSAFE = True` and reasonable `pyautogui.PAUSE = 0.2`.
- `click`, `double_click`, `hover` (moves to position, waits 0.5s for hover submenu to expand).
- `scroll_at` (moves cursor to `(screen_x, screen_y)`, then triggers `pyautogui.scroll(clicks)`).
- `paste_text` (copies string to clipboard via `pyperclip.copy`, hotkeys `ctrl+v`, optionally presses `enter`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest edge_ie_agent/tests/test_controller.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add edge_ie_agent/controller.py edge_ie_agent/tests/test_controller.py
git commit -m "feat(edge_agent): implement mouse and keyboard automation controller"
```

---

### Task 4: Qwen Vision Client with JSON Extraction & Schema Validation

**Files:**
- Create: `edge_ie_agent/qwen_client.py`
- Test: `edge_ie_agent/tests/test_qwen_client.py`

**Interfaces:**
- Consumes: `config.Config`
- Produces:
  - `ActionPayload`: Dataclass for action definition (`thought`, `action`, `point`, `text`, `press_enter`, `direction`, `amount`, `seconds`, `message`)
  - `QwenClient`:
    - `encode_image(image: PIL.Image.Image) -> str` (base64 string)
    - `clean_json_response(raw_text: str) -> dict`
    - `predict_action(image: PIL.Image.Image, task: str, step_history: list[str]) -> ActionPayload`

- [ ] **Step 1: Write failing test for JSON cleaning and response parsing**

```python
# edge_ie_agent/tests/test_qwen_client.py
from edge_ie_agent.qwen_client import clean_json_response, ActionPayload

def test_clean_json_with_markdown_fences():
    raw = '```json\n{"thought": "Click login", "action": "click", "point": [450, 300]}\n```'
    parsed = clean_json_response(raw)
    assert parsed["action"] == "click"
    assert parsed["point"] == [450, 300]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest edge_ie_agent/tests/test_qwen_client.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `qwen_client.py`**

Implement:
- `clean_json_response`: Regex/parser to strip markdown code blocks and extract valid JSON.
- `encode_image`: Converts `PIL.Image` into base64 JPEG format.
- `QwenClient.predict_action`: Constructs system prompt instructing Qwen Vision to return coordinates `[0, 1000]`, calls `openai.ChatCompletion.create` (pointing to AIPRO `base_url`), and validates return schema into `ActionPayload`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest edge_ie_agent/tests/test_qwen_client.py -v`  
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add edge_ie_agent/qwen_client.py edge_ie_agent/tests/test_qwen_client.py
git commit -m "feat(edge_agent): implement Qwen Vision API client with schema parsing"
```

---

### Task 5: ReAct Loop Orchestrator & CLI Entry Point

**Files:**
- Create: `edge_ie_agent/agent.py`
- Create: `edge_ie_agent/main.py`
- Test: `edge_ie_agent/tests/test_agent.py`

**Interfaces:**
- Consumes: `config`, `window_manager`, `coordinate`, `controller`, `qwen_client`
- Produces:
  - `VisualAgent`:
    - `run(task: str) -> str`
  - `main()` CLI runner

- [ ] **Step 1: Write test for VisualAgent loop execution with mocks**

```python
# edge_ie_agent/tests/test_agent.py
from unittest.mock import MagicMock
from edge_ie_agent.agent import VisualAgent
from edge_ie_agent.qwen_client import ActionPayload

def test_agent_completes_on_finish():
    mock_client = MagicMock()
    mock_client.predict_action.return_value = ActionPayload(
        thought="Done", action="finish", message="Found result"
    )
    mock_wm = MagicMock()
    mock_wm.find_edge_window.return_value = 123
    mock_wm.capture_window.return_value = (MagicMock(), (0, 0, 1000, 800))
    
    agent = VisualAgent(client=mock_client, window_mgr=mock_wm, controller=MagicMock())
    result = agent.run("Find information")
    assert result == "Found result"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest edge_ie_agent/tests/test_agent.py -v`  
Expected: FAIL

- [ ] **Step 3: Implement `agent.py` and `main.py`**

Implement:
- `agent.py`:
  - Activates Edge window.
  - Loops up to `config.max_steps`.
  - Captures screenshot, queries Qwen Vision.
  - Translates normalized coordinates via `coordinate.py` and executes via `controller.py`.
  - Records step history to feed back into subsequent turns.
  - Handles `finish` action or `max_steps` timeout.
- `main.py`:
  - CLI banner, loads `.env`, prompts user for task query, runs `VisualAgent.run()`.

- [ ] **Step 4: Run full test suite to verify everything passes**

Run: `pytest edge_ie_agent/tests/ -v`  
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add edge_ie_agent/agent.py edge_ie_agent/main.py edge_ie_agent/tests/test_agent.py
git commit -m "feat(edge_agent): implement ReAct agent loop and CLI entry point"
```
