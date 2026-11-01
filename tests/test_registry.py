"""
Unit Tests for Central Registry APIs
"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

TEST_DIR = Path(__file__).resolve().parent
PROJECT_DIR = TEST_DIR.parent
sys.path.insert(0, str(PROJECT_DIR))

from app import app

client = TestClient(app)


def test_get_catalog():
    """Verify GET /api/v1/catalog returns catalog items."""
    response = client.get("/api/v1/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "servers" in data
    assert len(data["servers"]) > 0
    
    # Check first item structure
    item = data["servers"][0]
    assert "id" in item
    assert "name" in item
    assert "tools" in item
    assert "download_url" in item


def test_get_catalog_item():
    """Verify GET /api/v1/catalog/{id} returns single server manifest."""
    response = client.get("/api/v1/catalog/excel")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "excel"
    assert data["runtime"] == "python"
    assert len(data["tools"]) > 0


def test_get_catalog_item_not_found():
    """Verify 404 on non-existent server."""
    response = client.get("/api/v1/catalog/non-existent-xyz")
    assert response.status_code == 404


def test_download_bundle():
    """Verify GET /api/v1/catalog/{id}/bundle downloads the zip."""
    response = client.get("/api/v1/catalog/archive/bundle")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert len(response.content) > 1000
