"""
Unit Tests for Custom Upload & Auto-Detector Pipeline
"""
import io
import sys
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from app import app
from services.auto_detector import analyze_python_ast

client = TestClient(app)


def test_ast_dependency_and_env_analysis():
    """Verify AST parser extracts external dependencies and env vars correctly."""
    sample_code = """
import os
import sys
import math
import requests
from openpyxl import load_workbook

api_key = os.getenv("SECRET_API_KEY", "default")
db_url = os.environ.get("DATABASE_URL")
port = os.environ["APP_PORT"]

def my_func():
    pass
"""
    deps, env_vars = analyze_python_ast(sample_code)
    
    assert "requests" in deps
    assert "openpyxl" in deps
    assert "sys" not in deps, "Standard lib 'sys' must be ignored"
    assert "math" not in deps, "Standard lib 'math' must be ignored"
    assert "os" not in deps, "Standard lib 'os' must be ignored"
    
    assert "SECRET_API_KEY" in env_vars
    assert "DATABASE_URL" in env_vars
    assert "APP_PORT" in env_vars


def test_upload_single_python_file():
    """Verify uploading a single .py file generates package and registers in catalog."""
    script_content = b"""
import os
from mcp.server import MCPServer

mcp = MCPServer("my_custom_tool")

@mcp.tool()
def calculate_tax(amount: float) -> float:
    \"\"\"Calculates tax for target amount.\"\"\"
    tax_rate = float(os.getenv("TAX_RATE", "0.1"))
    return amount * tax_rate
"""
    files = {
        "file": ("custom_tax.py", io.BytesIO(script_content), "text/x-python")
    }
    data = {
        "name": "Custom Tax Calculator",
        "description": "Calculates tax based on configurable rates"
    }
    
    response = client.post("/api/v1/mcp/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert "id" in res_data
    assert "TAX_RATE" in res_data["detected_env_vars"]
    assert res_data["tools_count"] >= 1
    assert "calculate_tax" in [t["name"] for t in res_data["tools"]]


def test_upload_invalid_syntax_rejected():
    """Verify syntax error is caught and rejected with 400 Bad Request."""
    invalid_code = b"""
def broken_syntax(
    print("missing closing paren"
"""
    files = {
        "file": ("broken.py", io.BytesIO(invalid_code), "text/x-python")
    }
    response = client.post("/api/v1/mcp/upload", files=files)
    assert response.status_code == 400
    res_data = response.json()
    assert "SyntaxError" in res_data["detail"] or "syntax" in res_data["detail"].lower()


def test_upload_with_custom_env_requirements():
    """Verify user can supply, edit, or override env requirements during upload."""
    import json
    script_content = b"""
import os
token = os.getenv("GITHUB_TOKEN")
"""
    custom_env = [
        {
            "key": "GITHUB_TOKEN",
            "label": "GitHub Personal Access Token",
            "type": "password",
            "required": True,
            "default": ""
        },
        {
            "key": "MAX_REPOSITORIES",
            "label": "Max Repositories to Sync",
            "type": "text",
            "required": False,
            "default": "50"
        }
    ]
    files = {
        "file": ("git_syncer.py", io.BytesIO(script_content), "text/x-python")
    }
    data = {
        "name": "Git Syncer",
        "env_requirements": json.dumps(custom_env)
    }

    response = client.post("/api/v1/mcp/upload", files=files, data=data)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert "GITHUB_TOKEN" in res_data["detected_env_vars"]
    assert "MAX_REPOSITORIES" in res_data["detected_env_vars"]
    
    # Check catalog item
    cat_res = client.get("/api/v1/catalog")
    assert cat_res.status_code == 200
    servers = cat_res.json()["servers"]
    found = next((s for s in servers if s["id"] == res_data["id"]), None)
    assert found is not None
    env_keys = [e["key"] for e in found["envRequirements"]]
    assert "GITHUB_TOKEN" in env_keys
    assert "MAX_REPOSITORIES" in env_keys
    max_repo_item = next(e for e in found["envRequirements"] if e["key"] == "MAX_REPOSITORIES")
    assert max_repo_item["default"] == "50"
    assert max_repo_item["label"] == "Max Repositories to Sync"

