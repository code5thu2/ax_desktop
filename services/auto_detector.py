"""
Auto-Detector & Upload Pipeline Service
Parses AST for imports and environment variables, performs dry-run validation,
and packages custom uploads into storage/packages/<id>.zip.
"""
import ast
import io
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import config

# Python Standard Library Modules to exclude from external dependencies
STDLIB_MODULES = {
    "abc", "argparse", "array", "ast", "asyncio", "base64", "binascii", "builtins",
    "bz2", "calendar", "cmath", "collections", "colorsys", "compileall", "concurrent",
    "configparser", "contextlib", "contextvars", "copy", "copyreg", "crypt", "csv",
    "ctypes", "curses", "dataclasses", "datetime", "dbm", "decimal", "difflib",
    "dis", "doctest", "email", "encodings", "ensurepip", "enum", "errno", "faulthandler",
    "fcntl", "filecmp", "fileinput", "fnmatch", "fractions", "ftplib", "functools",
    "gc", "getopt", "getpass", "gettext", "glob", "graphlib", "gzip", "hashlib",
    "heapq", "hmac", "html", "http", "imaplib", "imghdr", "importlib", "inspect",
    "io", "ipaddress", "itertools", "json", "keyword", "linecache", "locale",
    "logging", "lzma", "mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap",
    "modulefinder", "multiprocessing", "netrc", "nis", "nntplib", "numbers", "operator",
    "optparse", "os", "ossaudiodev", "pathlib", "pdb", "pickle", "pickletools",
    "pipes", "pkgutil", "platform", "plistlib", "poplib", "posix", "posixpath",
    "pprint", "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc",
    "queue", "quopri", "random", "re", "readline", "reprlib", "resource", "rlcompleter",
    "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex", "shutil",
    "signal", "site", "smtpd", "smtplib", "sndhdr", "socket", "socketserver",
    "spwd", "sqlite3", "ssl", "stat", "statistics", "string", "stringprep", "struct",
    "subprocess", "sunau", "symtable", "sys", "sysconfig", "syslog", "tarfile",
    "telnetlib", "tempfile", "termios", "test", "textwrap", "threading", "time",
    "timeit", "tkinter", "token", "tokenize", "trace", "traceback", "tracemalloc",
    "tty", "turtle", "turtledemo", "types", "typing", "unicodedata", "unittest",
    "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref", "webbrowser",
    "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc", "zipapp", "zipfile",
    "zipimport", "zlib", "zoneinfo"
}


def merge_env_requirements(
    detected: List[Dict[str, Any]],
    custom: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Merge auto-detected env requirements with user-supplied custom env definitions.
    Custom definitions override auto-detected properties (label, type, default, required)
    and can add new environment variables not discovered by AST.
    """
    if not custom:
        return detected

    req_map = {r["key"]: dict(r) for r in detected}
    for item in custom:
        k = item.get("key", "").strip()
        if not k:
            continue
        is_secret = item.get("type") == "password" or any(s in k.lower() for s in ["token", "key", "pass", "secret", "auth", "pwd"])
        req_map[k] = {
            "key": k,
            "label": item.get("label") or k.replace("_", " ").title(),
            "default": item.get("default", ""),
            "required": bool(item.get("required", False)),
            "type": "password" if is_secret else "text"
        }
    return list(req_map.values())


def analyze_python_ast(source_code: str) -> Tuple[List[str], List[str]]:
    """
    Parses Python source code AST to extract:
    1. Third-party dependencies (excluding stdlib)
    2. Environment variable names (os.getenv, os.environ, os.environ.get)
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        raise ValueError(f"SyntaxError at line {e.lineno}: {e.msg}") from e

    dependencies: Set[str] = set()
    env_vars: Set[str] = set()

    for node in ast.walk(tree):
        # 1. Imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                top_pkg = alias.name.split(".")[0]
                if top_pkg not in STDLIB_MODULES:
                    dependencies.add(top_pkg)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                top_pkg = node.module.split(".")[0]
                if top_pkg not in STDLIB_MODULES:
                    dependencies.add(top_pkg)

        # 2. Env vars: os.getenv("VAR") or getenv("VAR")
        if isinstance(node, ast.Call):
            # os.getenv("VAR")
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "getenv"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                env_vars.add(node.args[0].value)
            # os.environ.get("VAR")
            elif (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Attribute)
                and node.func.value.attr == "environ"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                env_vars.add(node.args[0].value)

        # 3. Env vars: os.environ["VAR"]
        elif (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "environ"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        ):
            env_vars.add(node.slice.value)

    return sorted(list(dependencies)), sorted(list(env_vars))


def extract_tools_from_ast(source_code: str) -> List[Dict[str, Any]]:
    """Extract tool definitions and parameters from Python AST."""
    try:
        tree = ast.parse(source_code)
    except Exception:
        return []

    tools: List[Dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            is_tool = False
            for dec in node.decorator_list:
                if (isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "tool") or \
                   (isinstance(dec, ast.Attribute) and dec.attr == "tool"):
                    is_tool = True
                    break
            
            # If no decorator, consider top-level functions not starting with _ as candidates
            if is_tool or (not node.name.startswith("_")):
                doc = ast.get_docstring(node) or ""
                args = [a.arg for a in node.args.args if a.arg != "self"]
                tools.append({
                    "name": node.name,
                    "description": doc.strip() or f"Function {node.name}",
                    "parameters": args
                })

    return tools


def process_uploaded_package(
    file_bytes: bytes,
    filename: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    custom_env_requirements: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """Process an uploaded .zip or .py file, validate, create package and update catalog."""
    ext = Path(filename).suffix.lower()
    base_name = Path(filename).stem.lower().replace(" ", "-").replace("_", "-")
    mcp_id = re.sub(r"[^a-z0-9\-]", "", base_name)
    if not mcp_id:
        mcp_id = f"custom-mcp-{int(datetime.now().timestamp())}"

    display_name = name or mcp_id.replace("-", " ").title()
    summary = description or f"Custom uploaded MCP server: {display_name}"

    dependencies: List[str] = []
    env_vars: List[str] = []
    tools: List[Dict[str, Any]] = []
    source_code = ""
    bundle_path = config.PACKAGES_DIR / f"{mcp_id}.zip"

    if ext == ".py":
        try:
            source_code = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            source_code = file_bytes.decode("latin-1")

        # Check syntax & analyze
        dependencies, env_vars = analyze_python_ast(source_code)
        tools = extract_tools_from_ast(source_code)

        # Format env requirements with secret detection
        env_requirements = []
        for v in env_vars:
            is_secret = any(s in v.lower() for s in ["token", "key", "pass", "secret", "auth", "pwd"])
            env_requirements.append({
                "key": v,
                "label": v.replace("_", " ").title(),
                "default": "",
                "required": True,
                "type": "password" if is_secret else "text"
            })

        env_requirements = merge_env_requirements(env_requirements, custom_env_requirements)

        manifest = {
            "id": mcp_id,
            "name": display_name,
            "version": "1.0.0",
            "vendor": "Custom Upload",
            "runtime": "python",
            "entrypoint": "server.py",
            "icon": "pi pi-code",
            "summary": summary,
            "category": "Custom Uploads",
            "dependencies": dependencies,
            "envRequirements": env_requirements,
            "tools": tools,
            "tools_count": len(tools),
            "download_url": f"/api/v1/catalog/{mcp_id}/bundle"
        }

        with zipfile.ZipFile(bundle_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            zf.writestr("requirements.txt", "\n".join(dependencies))
            zf.writestr("server.py", source_code)

    elif ext == ".zip":
        bundle_path = config.PACKAGES_DIR / f"{mcp_id}.zip"
        with open(bundle_path, "wb") as f:
            f.write(file_bytes)

        # Inspect zip
        with zipfile.ZipFile(bundle_path, "r") as zf:
            names = zf.namelist()
            if "manifest.json" in names:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
                dependencies = manifest.get("dependencies", [])
                env_vars = [e.get("key") for e in manifest.get("envRequirements", [])]
                tools = manifest.get("tools", [])
                manifest["envRequirements"] = merge_env_requirements(manifest.get("envRequirements", []), custom_env_requirements)
            else:
                # 1. Parse .env.example / .env.sample if available
                env_defaults = {}
                for env_name in [".env.example", ".env.sample", ".env.template", ".env"]:
                    match_env = [n for n in names if n.endswith(env_name)]
                    if match_env:
                        try:
                            content = zf.read(match_env[0]).decode("utf-8", errors="ignore")
                            for line in content.splitlines():
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

                # 2. Scan all .py files in zip
                py_files = [n for n in names if n.endswith(".py") and not any(p in n for p in ["__pycache__", ".venv"])]
                for pf in py_files:
                    try:
                        code = zf.read(pf).decode("utf-8", errors="ignore")
                        pf_deps, pf_envs = analyze_python_ast(code)
                        for d in pf_deps:
                            if d not in dependencies:
                                dependencies.append(d)
                        for ev in pf_envs:
                            if ev not in env_vars:
                                env_vars.append(ev)
                        if not tools:
                            tools = extract_tools_from_ast(code)
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

                env_requirements = merge_env_requirements(env_requirements, custom_env_requirements)

                manifest = {
                    "id": mcp_id,
                    "name": display_name,
                    "version": "1.0.0",
                    "vendor": "Custom Upload",
                    "runtime": "python",
                    "entrypoint": py_files[0] if py_files else "server.py",
                    "icon": "pi pi-box",
                    "summary": summary,
                    "category": "Custom Uploads",
                    "dependencies": dependencies,
                    "envRequirements": env_requirements,
                    "tools": tools,
                    "tools_count": len(tools),
                    "download_url": f"/api/v1/catalog/{mcp_id}/bundle"
                }

        # If custom env was supplied for a zip, rewrite the updated manifest inside bundle
        if custom_env_requirements:
            temp_zip = config.PACKAGES_DIR / f"{mcp_id}_tmp.zip"
            with zipfile.ZipFile(bundle_path, "r") as zin:
                with zipfile.ZipFile(temp_zip, "w", zipfile.ZIP_DEFLATED) as zout:
                    for item in zin.infolist():
                        if item.filename != "manifest.json":
                            zout.writestr(item, zin.read(item.filename))
                    zout.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False))
            temp_zip.replace(bundle_path)

    else:
        raise ValueError(f"Unsupported file extension: {ext}. Only .zip and .py are supported.")

    # Update catalog.json
    catalog_data = {"version": "1.0.0", "servers": []}
    if config.CATALOG_FILE.exists():
        try:
            with open(config.CATALOG_FILE, "r", encoding="utf-8") as f:
                catalog_data = json.load(f)
        except Exception:
            pass

    servers = [s for s in catalog_data.get("servers", []) if s.get("id") != mcp_id]
    servers.insert(0, manifest)
    catalog_data["servers"] = servers
    catalog_data["total"] = len(servers)
    catalog_data["updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(config.CATALOG_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog_data, f, indent=2, ensure_ascii=False)

    return {
        "success": True,
        "id": mcp_id,
        "name": display_name,
        "detected_runtime": manifest["runtime"],
        "detected_dependencies": dependencies,
        "detected_env_vars": [e["key"] for e in manifest.get("envRequirements", [])] or env_vars,
        "env_requirements": manifest.get("envRequirements", []),
        "tools_count": len(tools),
        "tools": tools,
        "download_url": manifest["download_url"]
    }
