"""
Test Data Packager Pipeline
"""
import sys
import json
import zipfile
from pathlib import Path

# Add project root to sys.path
TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

import config
from services.packager import package_all_servers, package_single_server


def test_package_archive_server():
    """Verify that archive_mcp can be packaged into a valid zip with manifest."""
    bundle_path, manifest = package_single_server("archive")
    
    assert bundle_path.exists(), f"Bundle {bundle_path} must exist"
    assert bundle_path.suffix == ".zip"
    assert manifest["id"] == "archive"
    assert manifest["runtime"] == "python"
    assert "tools" in manifest
    assert len(manifest["tools"]) > 0
    
    # Check contents of zip
    with zipfile.ZipFile(bundle_path, "r") as z:
        names = z.namelist()
        assert "manifest.json" in names, "manifest.json must be in zip root"
        # Check that server files or entrypoint are included
        assert any(n.endswith("server.py") for n in names)
        # Check that common package is included
        assert any("common" in n for n in names)


def test_package_all_servers():
    """Verify that all configured servers are packaged and catalog.json is updated."""
    results = package_all_servers()
    assert len(results) >= 3, "Should package at least 3 servers"
    
    # Verify catalog.json
    assert config.CATALOG_FILE.exists()
    with open(config.CATALOG_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)
    
    assert "servers" in catalog
    server_ids = [s["id"] for s in catalog["servers"]]
    assert "archive" in server_ids
    assert "excel" in server_ids
