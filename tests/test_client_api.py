"""
Test Client Installation APIs (Cách 1)
"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from app import app
from services.packager import package_single_server

client = TestClient(app)


def test_client_install_api():
    """Test POST /api/v1/client/install/{server_id} and uninstall."""
    package_single_server("archive")

    # Install
    res = client.post("/api/v1/client/install/archive", json={"env": {"TEST_VAR": "abc"}})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["status"] == "ready"
    assert data["server_id"] == "archive"
    assert "venv_python" in data
    assert data["configured_env"]["TEST_VAR"] == "abc"

    # List
    list_res = client.get("/api/v1/client/installed")
    assert list_res.status_code == 200
    inst_list = list_res.json()["installed"]
    assert any(x["server_id"] == "archive" for x in inst_list)

    # Update config
    cfg_res = client.post("/api/v1/client/config/archive", json={"env": {"TEST_VAR": "new_val", "ANOTHER_KEY": "123"}})
    assert cfg_res.status_code == 200, cfg_res.text
    assert cfg_res.json()["status"] == "updated"
    assert cfg_res.json()["configured_env"]["TEST_VAR"] == "new_val"

    # Uninstall
    uninst_res = client.post("/api/v1/client/uninstall/archive")
    assert uninst_res.status_code == 200
    assert uninst_res.json()["status"] == "uninstalled"
