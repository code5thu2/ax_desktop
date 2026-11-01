"""
Test Client Runtime Installer (Cách 1: uv Portable Sandbox)
"""
import sys
import shutil
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

import config
from services.client_installer import ClientInstaller
from services.packager import package_single_server


def test_client_installer_archive():
    """Verify 1-click install of archive MCP into isolated test sandbox using uv."""
    # Ensure package exists
    package_single_server("archive")

    # Use a separate test sandbox dir
    sandbox_dir = config.TEMP_DIR / "test_client_sandbox"
    shutil.rmtree(sandbox_dir, ignore_errors=True)
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    installer = ClientInstaller(install_base_dir=sandbox_dir)

    # 1. Install
    result = installer.install("archive", configured_env={"LOG_LEVEL": "DEBUG"})
    assert result["status"] == "ready"
    assert result["server_id"] == "archive"
    assert "venv_python" in result
    assert Path(result["venv_python"]).exists(), f"Virtualenv python must exist at {result['venv_python']}"
    assert result["configured_env"]["LOG_LEVEL"] == "DEBUG"
    assert installer.is_installed("archive")

    # 2. Check installed list
    installed_list = installer.list_installed()
    assert any(item["server_id"] == "archive" for item in installed_list)

    # 3. Uninstall
    uninst_res = installer.uninstall("archive")
    assert uninst_res["status"] == "uninstalled"
    assert not installer.is_installed("archive")

    # Clean up
    shutil.rmtree(sandbox_dir, ignore_errors=True)
