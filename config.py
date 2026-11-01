"""
Configuration for MCP Registry & Gateway Server
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Server Network Settings
SERVER_HOST = os.getenv("SERVER_HOST", "127.0.0.1")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))

# Storage Locations
STORAGE_DIR = BASE_DIR / "storage"
PACKAGES_DIR = STORAGE_DIR / "packages"
CATALOG_FILE = STORAGE_DIR / "catalog.json"
TEMP_DIR = BASE_DIR / "temp"

# External Data Source (User's In-House MCPs)
SOURCE_MCP_DIR = Path("D:/AI_MCP/servers")
SOURCE_CONFIG_FILE = Path("D:/AI_MCP/mcp.config.json")
SOURCE_VENV_PYTHON = Path("D:/AI_MCP/.venv/Scripts/python.exe")

# Client Runtime & Installation Storage (Cách 1: Portable uv Sandbox)
CLIENT_INSTALL_DIR = STORAGE_DIR / "installed_clients"
CLIENT_INSTALL_DIR.mkdir(parents=True, exist_ok=True)

UV_BIN_PATH = BASE_DIR / "bin" / "uv.exe"
if not UV_BIN_PATH.exists():
    venv_uv = Path("D:/AI_MCP/.venv/Scripts/uv.exe")
    if venv_uv.exists():
        UV_BIN_PATH = venv_uv

# Ensure required directories exist
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
TEMP_DIR.mkdir(parents=True, exist_ok=True)

