"""
Unit Tests for Pure HTTP MCP Gateway Router
"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from app import app

client = TestClient(app)


def test_mcp_initialize():
    """Verify POST /mcp initialize method."""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"}
        }
    }
    response = client.post("/mcp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data
    assert data["result"]["serverInfo"]["name"] == "in-house-mcp-gateway"


def test_mcp_tools_list():
    """Verify POST /mcp tools/list returns namespaced tools."""
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    response = client.post("/mcp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 2
    assert "tools" in data["result"]
    tool_names = [t["name"] for t in data["result"]["tools"]]
    
    # Check that tools from archive are registered with prefix
    assert any("archive__" in n or "archive" in n for n in tool_names)


def test_mcp_tools_call():
    """Verify executing archive__server_info returns JSON result in standard MCP format."""
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "archive__server_info",
            "arguments": {}
        }
    }
    response = client.post("/mcp", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 3
    assert "result" in data
    assert "content" in data["result"]
    assert len(data["result"]["content"]) > 0
    text_content = data["result"]["content"][0]["text"]
    assert "readonly" in text_content or "ok" in text_content


def test_mcp_rest_shortcuts():
    """Verify REST endpoints GET /mcp/tools and POST /mcp/tools/:name."""
    # 1. GET /mcp/tools
    res_list = client.get("/mcp/tools")
    assert res_list.status_code == 200
    tools = res_list.json()
    assert isinstance(tools, list)
    assert len(tools) > 0
    
    # 2. POST /mcp/tools/:name
    res_call = client.post("/mcp/tools/archive__server_info", json={})
    assert res_call.status_code == 200
    result = res_call.json()
    assert "result" in result or "ok" in result
