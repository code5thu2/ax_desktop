"""
Data Packager Utility for In-House MCP Servers
Packages servers from D:\\AI_MCP\\servers into standalone .zip bundles with manifest.json.
"""
import os
import sys
import ast
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import config

ICON_MAP = {
    "archive": "pi pi-box",
    "excel": "pi pi-file-excel",
    "docs": "pi pi-file-word",
    "fs": "pi pi-folder",
    "postgres": "pi pi-database",
    "screenshot": "pi pi-camera",
    "gitlab": "pi pi-code",
    "jenkins": "pi pi-cog",
    "zalo": "pi pi-comments",
}


def extract_tools_from_server_file(server_file: Path) -> List[Dict[str, Any]]:
    """Extract tool names and descriptions from an MCP server.py file using AST."""
    if not server_file.exists():
        return []
    
    with open(server_file, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read())
        except Exception:
            return []

    tools: List[Dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_tool = False
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "tool":
                    is_tool = True
                elif isinstance(dec, ast.Attribute) and dec.attr == "tool":
                    is_tool = True
            if is_tool:
                doc = ast.get_docstring(node) or ""
                # Also collect argument names
                args = [a.arg for a in node.args.args if a.arg != "self"]
                tools.append({
                    "name": node.name,
                    "description": doc.strip(),
                    "parameters": args
                })
    return tools


def package_single_server(server_id: str) -> Tuple[Path, Dict[str, Any]]:
    """Package one in-house server into storage/packages/<id>.zip and return (path, manifest)."""
    # Load mcp.config.json if available
    config_data: Dict[str, Any] = {}
    if config.SOURCE_CONFIG_FILE.exists():
        with open(config.SOURCE_CONFIG_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f).get("servers", {})

    server_conf = config_data.get(server_id, {})
    module_name = server_conf.get("module", f"servers.{server_id}_mcp")
    server_dir_name = module_name.split(".")[-1]
    server_dir = config.SOURCE_MCP_DIR / server_dir_name

    if not server_dir.exists():
        raise FileNotFoundError(f"Source server directory not found: {server_dir}")

    # Extract tools
    server_file = server_dir / "server.py"
    tools = extract_tools_from_server_file(server_file)

    # Format environment requirements
    raw_env = server_conf.get("env", {})
    env_requirements = []
    for k, v in raw_env.items():
        env_requirements.append({
            "key": k,
            "label": k.replace("_", " ").title(),
            "default": str(v),
            "required": False,
            "type": "text"
        })

    deps = server_conf.get("deps", [])

    manifest = {
        "id": server_id,
        "name": f"{server_id.title()} MCP Studio",
        "version": "1.0.0",
        "vendor": "In-House Engineering",
        "runtime": "python",
        "entrypoint": "server.py",
        "icon": ICON_MAP.get(server_id, "pi pi-cog"),
        "summary": server_conf.get("desc", f"In-house {server_id} MCP server"),
        "category": "In-House Tools",
        "dependencies": deps,
        "envRequirements": env_requirements,
        "tools": tools,
        "tools_count": len(tools),
        "download_url": f"/api/v1/catalog/{server_id}/bundle"
    }

    # Build zip file
    bundle_path = config.PACKAGES_DIR / f"{server_id}.zip"
    common_dir = config.SOURCE_MCP_DIR.parent / "common"

    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. Write manifest.json
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        # 2. Write requirements.txt
        zf.writestr("requirements.txt", "\n".join(deps))

        # 3. Write server files
        for item in server_dir.rglob("*"):
            if item.is_file() and "__pycache__" not in item.parts:
                rel_path = item.relative_to(server_dir)
                zf.write(item, arcname=str(rel_path))

        # 4. Include common package if exists
        if common_dir.exists():
            for item in common_dir.rglob("*"):
                if item.is_file() and "__pycache__" not in item.parts:
                    rel_path = item.relative_to(common_dir.parent)
                    zf.write(item, arcname=str(rel_path))

    return bundle_path, manifest


def package_all_servers() -> List[Dict[str, Any]]:
    """Package all servers listed in mcp.config.json or found in SOURCE_MCP_DIR."""
    server_ids = []
    if config.SOURCE_CONFIG_FILE.exists():
        with open(config.SOURCE_CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
            server_ids = list(cfg.get("servers", {}).keys())

    if not server_ids:
        # Fallback by scanning directories
        for d in config.SOURCE_MCP_DIR.iterdir():
            if d.is_dir() and d.name.endswith("_mcp") and not d.name.startswith("_"):
                server_ids.append(d.name.replace("_mcp", ""))

    manifests = []
    for sid in server_ids:
        try:
            _, manifest = package_single_server(sid)
            manifests.append(manifest)
        except Exception as e:
            print(f"Warning: Failed to package {sid}: {e}")

    # Update catalog.json
    catalog_data = {
        "version": "1.0.0",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(manifests),
        "servers": manifests
    }
    with open(config.CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)

    return manifests


if __name__ == "__main__":
    results = package_all_servers()
    print(f"Successfully packaged {len(results)} servers:")
    for r in results:
        print(f" - {r['id']}: {r['tools_count']} tools -> {config.PACKAGES_DIR / (r['id'] + '.zip')}")
