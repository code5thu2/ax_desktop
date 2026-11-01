"""
Unit Tests for Git / GitHub Repository Import Pipeline
"""
import sys
import tempfile
import zipfile
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from app import app
from services.git_importer import parse_git_url, process_git_directory

client = TestClient(app)


def test_parse_git_url():
    """Verify Git URL parser extracts owner, repo, and clean name."""
    url1 = "https://github.com/company/erp-connector.git"
    provider1, owner1, repo1 = parse_git_url(url1)
    assert provider1 == "github"
    assert owner1 == "company"
    assert repo1 == "erp-connector"

    url2 = "https://gitlab.com/internal-team/data-sync"
    provider2, owner2, repo2 = parse_git_url(url2)
    assert provider2 == "gitlab"
    assert owner2 == "internal-team"
    assert repo2 == "data-sync"


def test_process_git_directory_with_code():
    """Verify processing a downloaded git folder creates a valid MCP package."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        # Create mock repo contents
        server_code = """
import os
import requests
from mcp.server import MCPServer

mcp = MCPServer("git_imported_mcp")

@mcp.tool()
def sync_data(target: str) -> dict:
    \"\"\"Syncs data with external target.\"\"\"
    api_url = os.getenv("REMOTE_API_URL", "http://api.local")
    return {"status": "synced", "target": target}
"""
        (tmp_path / "server.py").write_text(server_code, encoding="utf-8")
        (tmp_path / "requirements.txt").write_text("requests>=2.31.0\n", encoding="utf-8")

        result = process_git_directory(
            repo_dir=tmp_path,
            repo_name="git-sync-mcp",
            name="Git Sync MCP Tool",
            description="Imported from Git test"
        )

        assert result["success"] is True
        assert result["id"] == "git-sync-mcp"
        assert "REMOTE_API_URL" in result["detected_env_vars"]
        assert "requests" in result["detected_dependencies"]
        assert result["tools_count"] >= 1
        assert "sync_data" in [t["name"] for t in result["tools"]]


def test_import_git_endpoint_validation():
    """Verify POST /api/v1/mcp/import-git validates empty or invalid URL."""
    # 1. Invalid empty URL
    res_empty = client.post("/api/v1/mcp/import-git", json={"repo_url": ""})
    assert res_empty.status_code == 400

    # 2. Invalid non-git URL
    res_invalid = client.post("/api/v1/mcp/import-git", json={"repo_url": "ftp://not-supported"})
    assert res_invalid.status_code == 400
