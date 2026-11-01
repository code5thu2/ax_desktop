"""
Git / GitHub Repository Importer Service
Enables developers to submit a Git/GitHub URL to automatically clone/download,
analyze AST, extract tools, generate packages, and publish to the registry.
"""
import io
import json
import os
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config
from services.auto_detector import analyze_python_ast, extract_tools_from_ast, merge_env_requirements


def parse_git_url(repo_url: str) -> Tuple[str, str, str]:
    """
    Parses a Git repository URL into (provider, owner, repo_name).
    Example: 'https://github.com/company/erp-connector.git' -> ('github', 'company', 'erp-connector')
    """
    cleaned = repo_url.strip().rstrip("/")
    if cleaned.endswith(".git"):
        cleaned = cleaned[:-4]

    parsed = urllib.parse.urlparse(cleaned)
    domain = parsed.netloc.lower()
    path_parts = [p for p in parsed.path.split("/") if p]

    if not path_parts or len(path_parts) < 2:
        raise ValueError(f"Invalid Git URL format: {repo_url}. Expected format: https://domain/owner/repo")

    provider = "generic"
    if "github" in domain:
        provider = "github"
    elif "gitlab" in domain:
        provider = "gitlab"

    owner = path_parts[-2]
    repo_name = path_parts[-1]

    return provider, owner, repo_name


def download_git_repository(
    repo_url: str,
    target_dir: Path,
    branch: str = "main",
    token: Optional[str] = None
) -> Path:
    """
    Downloads or clones a Git repository into target_dir.
    Tries fast GitHub zipball API first, falls back to `git clone --depth 1`.
    """
    provider, owner, repo = parse_git_url(repo_url)
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Try fast GitHub zipball download if it is a GitHub repo
    if provider == "github":
        zipball_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{branch}"
        headers = {
            "User-Agent": "MCP-Registry-Importer/1.0",
            "Accept": "application/vnd.github.v3+json"
        }
        auth_token = token or os.getenv("GITHUB_TOKEN")
        if auth_token:
            headers["Authorization"] = f"token {auth_token}"

        req = urllib.request.Request(zipball_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                content = resp.read()
                with zipfile.ZipFile(io.BytesIO(content)) as zf:
                    zf.extractall(target_dir)

                subdirs = [d for d in target_dir.iterdir() if d.is_dir()]
                if len(subdirs) == 1:
                    return subdirs[0]
                return target_dir
        except Exception:
            pass

    # 2. Fallback to git clone --depth 1
    clone_url = repo_url.strip()
    auth_token = token or (os.getenv("GITHUB_TOKEN") if provider == "github" else os.getenv("GITLAB_TOKEN"))
    if auth_token:
        parsed = urllib.parse.urlparse(clone_url)
        if provider == "gitlab":
            netloc = f"oauth2:{auth_token}@{parsed.netloc}"
        else:
            netloc = f"{auth_token}@{parsed.netloc}"
        clone_url = urllib.parse.urlunparse(parsed._replace(netloc=netloc))

    cmd = ["git", "clone", "--depth", "1", "--branch", branch, clone_url, str(target_dir)]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        err = proc.stderr.strip()
        if auth_token:
            err = err.replace(auth_token, "***")
        raise RuntimeError(f"Git clone failed: {err}")

    return target_dir


def process_git_directory(
    repo_dir: Path,
    repo_name: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    custom_env_requirements: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Analyzes code inside a cloned/extracted git directory, builds package zip,
    and updates catalog.json.
    """
    clean_id = re.sub(r"[^a-z0-9\-]", "", repo_name.lower().replace("_", "-"))
    if not clean_id:
        clean_id = f"git-mcp-{int(datetime.now().timestamp())}"

    display_name = name or clean_id.replace("-", " ").title()
    summary = description or f"In-house MCP imported from Git: {display_name}"

    manifest_file = repo_dir / "manifest.json"
    manifest: Dict[str, Any] = {}
    dependencies: List[str] = []
    env_vars: List[str] = []
    tools: List[Dict[str, Any]] = []

    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as f:
                manifest = json.load(f)
                dependencies = manifest.get("dependencies", [])
                env_vars = [e.get("key") for e in manifest.get("envRequirements", [])]
                tools = manifest.get("tools", [])
        except Exception:
            manifest = {}

    if not manifest:
        # Scan for entrypoints: server.py, main.py, app.py
        candidate_files = ["server.py", "main.py", "app.py"]
        found_entry = None
        for cand in candidate_files:
            if (repo_dir / cand).exists():
                found_entry = cand
                break

        if not found_entry:
            py_files = list(repo_dir.rglob("*.py"))
            if py_files:
                found_entry = str(py_files[0].relative_to(repo_dir))
            else:
                found_entry = "server.py"

        entrypoint = found_entry

        # Read requirements.txt if available
        req_file = repo_dir / "requirements.txt"
        if req_file.exists():
            with open(req_file, "r", encoding="utf-8") as f:
                for line in f:
                    cleaned = line.strip()
                    if cleaned and not cleaned.startswith("#"):
                        pkg_name = re.split(r"[>=<~!\s]", cleaned)[0].strip()
                        if pkg_name:
                            dependencies.append(pkg_name)

        # 1. Read and parse .env.example / .env.sample if available
        env_defaults: Dict[str, str] = {}
        for env_file_name in [".env.example", ".env.sample", ".env.template", ".env"]:
            env_file = repo_dir / env_file_name
            if env_file.exists():
                try:
                    for line in env_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("'\"")
                            if k:
                                env_defaults[k] = v
                                if k not in env_vars:
                                    env_vars.append(k)
                except Exception:
                    pass

        # 2. Read and AST analyze all python files in repo
        for py_file in repo_dir.rglob("*.py"):
            rel_parts = py_file.relative_to(repo_dir).parts
            if not any(p in [".git", "__pycache__", ".venv", "venv", ".idea"] for p in rel_parts):
                try:
                    code_text = py_file.read_text(encoding="utf-8", errors="ignore")
                    ast_deps, ast_envs = analyze_python_ast(code_text)
                    for d in ast_deps:
                        if d not in dependencies:
                            dependencies.append(d)
                    for ev in ast_envs:
                        if ev not in env_vars:
                            env_vars.append(ev)
                    if not tools and py_file.name in ["server.py", "main.py", "app.py"]:
                        tools = extract_tools_from_ast(code_text)
                except Exception:
                    pass

        if not tools and (repo_dir / entrypoint).exists():
            try:
                code_text = (repo_dir / entrypoint).read_text(encoding="utf-8", errors="ignore")
                tools = extract_tools_from_ast(code_text)
            except Exception:
                pass

        env_requirements = []
        for v in env_vars:
            is_secret = any(s in v.lower() for s in ["token", "key", "pass", "secret", "auth", "pwd"])
            def_val = env_defaults.get(v, "")
            env_requirements.append({
                "key": v,
                "label": v.replace("_", " ").title(),
                "default": def_val,
                "required": not bool(def_val),
                "type": "password" if is_secret else "text"
            })

        manifest = {
            "id": clean_id,
            "name": display_name,
            "version": "1.0.0",
            "vendor": "Git Import",
            "runtime": "python",
            "entrypoint": entrypoint,
            "icon": "pi pi-github",
            "summary": summary,
            "category": "Git Imports",
            "dependencies": dependencies,
            "envRequirements": env_requirements,
            "tools": tools,
            "tools_count": len(tools),
            "download_url": f"/api/v1/catalog/{clean_id}/bundle"
        }

    # Merge custom env definitions if supplied
    manifest["envRequirements"] = merge_env_requirements(manifest.get("envRequirements", []), custom_env_requirements)

    # Build zip bundle into storage/packages/<id>.zip
    bundle_path = config.PACKAGES_DIR / f"{clean_id}.zip"
    with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))

        for item in repo_dir.rglob("*"):
            if item.is_file():
                rel_parts = item.relative_to(repo_dir).parts
                if not any(p in [".git", "__pycache__", ".venv", "venv", ".idea"] for p in rel_parts):
                    zf.write(item, arcname=str(item.relative_to(repo_dir)))

    # Update storage/catalog.json
    catalog_data = {"version": "1.0.0", "servers": []}
    if config.CATALOG_FILE.exists():
        try:
            with open(config.CATALOG_FILE, "r", encoding="utf-8") as f:
                catalog_data = json.load(f)
        except Exception:
            pass

    servers = [s for s in catalog_data.get("servers", []) if s.get("id") != clean_id]
    servers.insert(0, manifest)
    catalog_data["servers"] = servers
    catalog_data["total"] = len(servers)
    catalog_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(config.CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "id": clean_id,
        "name": display_name,
        "detected_runtime": manifest.get("runtime", "python"),
        "detected_dependencies": dependencies,
        "detected_env_vars": [e["key"] for e in manifest.get("envRequirements", [])] or env_vars,
        "env_requirements": manifest.get("envRequirements", []),
        "tools_count": len(tools),
        "tools": tools,
        "download_url": manifest["download_url"]
    }


def import_mcp_from_git(
    repo_url: str,
    branch: str = "main",
    token: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    custom_env_requirements: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Full workflow: Downloads Git repository, processes code, and publishes to catalog."""
    if not repo_url or not repo_url.strip():
        raise ValueError("Repository URL is required")

    cleaned_url = repo_url.strip()
    if not (cleaned_url.startswith("http://") or cleaned_url.startswith("https://") or cleaned_url.startswith("git@")):
        raise ValueError(f"Invalid Git URL protocol: {cleaned_url}. Must start with http://, https://, or git@")

    _, _, repo_name = parse_git_url(cleaned_url)

    temp_dir = config.TEMP_DIR / f"git_clone_{int(datetime.now().timestamp())}_{repo_name}"
    try:
        actual_dir = download_git_repository(
            repo_url=cleaned_url,
            target_dir=temp_dir,
            branch=branch,
            token=token
        )
        result = process_git_directory(
            repo_dir=actual_dir,
            repo_name=repo_name,
            name=name,
            description=description,
            custom_env_requirements=custom_env_requirements
        )
        return result
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
