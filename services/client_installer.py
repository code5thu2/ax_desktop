"""
Client Runtime Installer & Subprocess Manager (Cách 1: Portable Mode with uv)
Handles 1-Click extraction, isolated virtualenv creation via uv.exe,
offline/online wheel dependency installation, and clean uninstallation.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

import config


class ClientInstaller:
    """Manages local MCP installation into isolated environments using uv."""

    def __init__(self, install_base_dir: Optional[Path] = None):
        self.base_dir = install_base_dir or config.CLIENT_INSTALL_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def get_server_dir(self, server_id: str) -> Path:
        return self.base_dir / server_id

    def is_installed(self, server_id: str) -> bool:
        server_dir = self.get_server_dir(server_id)
        python_exe = server_dir / ".venv" / "Scripts" / "python.exe"
        manifest_file = server_dir / "manifest.json"
        return server_dir.exists() and python_exe.exists() and manifest_file.exists()

    def install(
        self,
        server_id: str,
        configured_env: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        1-Click Install an MCP bundle using uv portable engine.
        Extracts package zip, provisions .venv in < 100ms, and installs dependencies.
        """
        start_time = time.time()
        bundle_path = config.PACKAGES_DIR / f"{server_id}.zip"

        if not bundle_path.exists():
            raise FileNotFoundError(f"Package bundle for '{server_id}' not found in registry at {bundle_path}")

        server_dir = self.get_server_dir(server_id)

        # Clean existing directory if present for clean reinstall
        if server_dir.exists():
            shutil.rmtree(server_dir, ignore_errors=True)
        server_dir.mkdir(parents=True, exist_ok=True)

        # 1. Extract package bundle
        with zipfile.ZipFile(bundle_path, "r") as zf:
            zf.extractall(server_dir)

        # 2. Save configured environment variables
        env_dict = configured_env or {}
        env_file = server_dir / ".env"
        with open(env_file, "w", encoding="utf-8") as f:
            for k, v in env_dict.items():
                f.write(f"{k}={v}\n")

        # 3. Create isolated virtualenv with uv
        uv_bin = str(config.UV_BIN_PATH)
        venv_path = server_dir / ".venv"
        python_base = str(config.SOURCE_VENV_PYTHON if config.SOURCE_VENV_PYTHON.exists() else sys.executable)

        venv_cmd = [
            uv_bin,
            "venv",
            str(venv_path),
            "--python",
            python_base
        ]
        res = subprocess.run(
            venv_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=15
        )
        if res.returncode != 0:
            raise RuntimeError(f"uv venv creation failed: {res.stderr or res.stdout}")

        venv_python = venv_path / "Scripts" / "python.exe"
        if not venv_python.exists():
            # Fallback for unix-style virtualenv
            venv_python = venv_path / "bin" / "python"

        # 4. Install dependencies via uv pip
        req_file = server_dir / "requirements.txt"
        wheels_dir = server_dir / "wheels"
        has_deps = False

        if req_file.exists():
            with open(req_file, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                has_deps = len(lines) > 0

        if has_deps:
            # Check for bundled offline wheels (Cách 1 Offline Distribution)
            if wheels_dir.exists() and any(wheels_dir.glob("*.whl")):
                pip_cmd = [
                    uv_bin,
                    "pip",
                    "install",
                    "--no-index",
                    "--find-links",
                    str(wheels_dir),
                    "-r",
                    str(req_file),
                    "--python",
                    str(venv_python)
                ]
            else:
                pip_cmd = [
                    uv_bin,
                    "pip",
                    "install",
                    "-r",
                    str(req_file),
                    "--python",
                    str(venv_python)
                ]

            pip_res = subprocess.run(
                pip_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=45
            )
            if pip_res.returncode != 0:
                raise RuntimeError(f"uv dependency installation failed: {pip_res.stderr or pip_res.stdout}")

        # 5. Read manifest
        manifest_file = server_dir / "manifest.json"
        manifest: Dict[str, Any] = {}
        if manifest_file.exists():
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)

        duration = time.time() - start_time

        # 6. Save installation metadata
        meta = {
            "server_id": server_id,
            "name": manifest.get("name", server_id),
            "version": manifest.get("version", "1.0.0"),
            "install_path": str(server_dir),
            "venv_python": str(venv_python),
            "duration_seconds": round(duration, 2),
            "tools_count": len(manifest.get("tools", [])),
            "configured_env": env_dict,
            "engine": "uv (Portable Mode - Cách 1)",
            "installed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "status": "ready"
        }

        with open(server_dir / "install_meta.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return meta

    def update_config(self, server_id: str, configured_env: Dict[str, str]) -> Dict[str, Any]:
        """Update environment variables and configuration for an installed MCP."""
        server_dir = self.get_server_dir(server_id)
        if not server_dir.exists():
            raise FileNotFoundError(f"MCP server '{server_id}' is not installed")

        # 1. Update .env file
        env_file = server_dir / ".env"
        with open(env_file, "w", encoding="utf-8") as f:
            for k, v in configured_env.items():
                f.write(f"{k}={v}\n")

        # 2. Update install_meta.json
        meta_file = server_dir / "install_meta.json"
        meta: Dict[str, Any] = {}
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                pass

        meta["configured_env"] = configured_env
        meta["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        return {
            "status": "updated",
            "server_id": server_id,
            "configured_env": configured_env,
            "updated_at": meta["updated_at"]
        }

    def uninstall(self, server_id: str) -> Dict[str, Any]:
        """Uninstall an MCP server by removing its isolated directory."""
        server_dir = self.get_server_dir(server_id)
        if not server_dir.exists():
            return {"server_id": server_id, "status": "not_installed"}

        shutil.rmtree(server_dir, ignore_errors=True)
        if server_dir.exists():
            time.sleep(0.15)
            shutil.rmtree(server_dir, ignore_errors=True)

        return {"server_id": server_id, "status": "uninstalled"}

    def list_installed(self) -> List[Dict[str, Any]]:
        """List all installed MCP servers and their current status."""
        installed = []
        if not self.base_dir.exists():
            return installed

        for d in self.base_dir.iterdir():
            if d.is_dir() and not d.name.startswith("."):
                meta_file = d / "install_meta.json"
                manifest_file = d / "manifest.json"
                if meta_file.exists():
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                            installed.append(meta)
                    except Exception:
                        pass
                elif manifest_file.exists():
                    try:
                        with open(manifest_file, "r", encoding="utf-8") as f:
                            manifest = json.load(f)
                            installed.append({
                                "server_id": d.name,
                                "name": manifest.get("name", d.name),
                                "version": manifest.get("version", "1.0.0"),
                                "install_path": str(d),
                                "status": "ready"
                            })
                    except Exception:
                        pass
        return installed

    def get_installed(self, server_id: str) -> Optional[Dict[str, Any]]:
        """Get install details for a single server."""
        server_dir = self.get_server_dir(server_id)
        meta_file = server_dir / "install_meta.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None


client_installer = ClientInstaller()
