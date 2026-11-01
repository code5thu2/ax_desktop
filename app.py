"""
Main FastAPI Application for MCP Registry & Gateway Server
"""
from pathlib import Path
from fastapi import FastAPI, File, Form, HTTPException, Query, Request, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

import config
from services.catalog_service import catalog_service
from services.auto_detector import process_uploaded_package
from services.gateway_router import gateway_router
from services.git_importer import import_mcp_from_git
from services.client_installer import client_installer

app = FastAPI(
    title="MCP Private Registry & Pure HTTP Gateway",
    version="1.0.0",
    description="In-House MCP Server Registry and Stateless HTTP Gateway"
)

# Enable CORS for Desktop & Web App access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_dist = Path(__file__).parent / "frontend" / "dist"
if frontend_dist.is_dir() and (frontend_dist / "index.html").is_file():
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="frontend_assets")
    if (frontend_dist / "mascots").is_dir():
        app.mount("/mascots", StaticFiles(directory=str(frontend_dist / "mascots")), name="frontend_mascots")
    if (frontend_dist / "fonts").is_dir():
        app.mount("/fonts", StaticFiles(directory=str(frontend_dist / "fonts")), name="frontend_fonts")

    @app.get("/", include_in_schema=False)
    def root_index():
        """Serve compiled MCP Studio UI."""
        return FileResponse(str(frontend_dist / "index.html"))
else:
    @app.get("/", include_in_schema=False)
    def root_redirect():
        """Redirect home to interactive Swagger UI documentation."""
        return RedirectResponse(url="/docs")


# ============================================================================ #
# 1. REGISTRY APIS (For Marketplace & Package Downloads)
# ============================================================================ #

@app.get("/api/v1/catalog")
def get_catalog(
    q: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Retrieve catalog of available in-house MCP servers."""
    servers = catalog_service.list_servers(query=q, category=category)
    return {
        "total": len(servers),
        "servers": servers
    }


@app.get("/api/v1/catalog/{server_id}")
def get_catalog_item(server_id: str):
    """Retrieve manifest details for a specific server."""
    server = catalog_service.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail=f"Server '{server_id}' not found in registry")
    return server


@app.get("/api/v1/catalog/{server_id}/bundle")
def download_bundle(server_id: str):
    """Download the .zip package bundle for a server."""
    bundle_path = catalog_service.get_bundle_path(server_id)
    if not bundle_path:
        raise HTTPException(status_code=404, detail=f"Package bundle for '{server_id}' not found")
    
    return FileResponse(
        path=str(bundle_path),
        filename=f"{server_id}.zip",
        media_type="application/zip"
    )


@app.post("/api/v1/mcp/upload", status_code=201)
async def upload_mcp(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    env_requirements: Optional[str] = Form(None)
):
    """
    Upload a standalone .py script or .zip package.
    Automatically parses AST for imports/dependencies, scans environment variables,
    merges custom user env requirements if provided, and publishes to the registry.
    """
    try:
        custom_env = None
        if env_requirements:
            import json
            try:
                parsed = json.loads(env_requirements)
                if isinstance(parsed, list):
                    custom_env = parsed
            except Exception:
                pass

        content = await file.read()
        result = process_uploaded_package(
            file_bytes=content,
            filename=file.filename or "custom_mcp.py",
            name=name,
            description=description,
            custom_env_requirements=custom_env
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload processing failed: {str(e)}")


class GitImportRequest(BaseModel):
    repo_url: str
    branch: Optional[str] = "main"
    token: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    env_requirements: Optional[List[Dict[str, Any]]] = None


@app.post("/api/v1/mcp/import-git", status_code=201)
def import_git_repository(req: GitImportRequest):
    """
    Import an MCP server directly from a GitHub or GitLab repository link.
    Automatically clones/downloads archive, parses AST for tools and dependencies,
    merges custom user env requirements if provided, and registers package in Marketplace catalog.
    """
    try:
        result = import_mcp_from_git(
            repo_url=req.repo_url,
            branch=req.branch or "main",
            token=req.token,
            name=req.name,
            description=req.description,
            custom_env_requirements=req.env_requirements
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git import failed: {str(e)}")


# ============================================================================ #
# 2. CLIENT RUNTIME & INSTALLATION APIS (Cách 1: Portable uv Engine)
# ============================================================================ #

class ClientInstallRequest(BaseModel):
    env: Optional[Dict[str, str]] = None


@app.post("/api/v1/client/install/{server_id}")
def install_mcp_client(server_id: str, req: Optional[ClientInstallRequest] = None):
    """
    1-Click Client Installation (Cách 1: Portable Mode via uv).
    Unpacks MCP package, sets up isolated .venv, installs dependencies in ~0.5s,
    and configures environment variables.
    """
    try:
        env_dict = req.env if req else None
        res = client_installer.install(server_id, configured_env=env_dict)
        return res
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Client installation failed: {str(e)}")


class ClientConfigUpdateRequest(BaseModel):
    env: Dict[str, str]


@app.post("/api/v1/client/config/{server_id}")
def update_mcp_config(server_id: str, req: ClientConfigUpdateRequest):
    """Update environment variables and configuration for an installed MCP instance."""
    try:
        return client_installer.update_config(server_id, req.env)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update config: {str(e)}")


@app.post("/api/v1/client/uninstall/{server_id}")
def uninstall_mcp_client(server_id: str):
    """Uninstall client MCP instance and purge isolated virtualenv."""
    return client_installer.uninstall(server_id)


@app.get("/api/v1/client/installed")
def list_installed_mcp_clients():
    """List all currently installed MCP instances on this client."""
    return {"installed": client_installer.list_installed()}


# ============================================================================ #
# 3. MCP GATEWAY APIS (Pure HTTP Standard - Strictly No SSE)
# ============================================================================ #

@app.post("/mcp")
async def mcp_jsonrpc_endpoint(request: Request):
    """
    Standard Model Context Protocol JSON-RPC 2.0 Stateless HTTP Endpoint.
    Direct Request-Response: supports initialize, tools/list, and tools/call.
    Zero persistent connection / zero SSE overhead.
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error: Invalid JSON"}}
        )

    response = await gateway_router.handle_jsonrpc(body)
    return JSONResponse(content=response)


@app.get("/mcp/tools")
def get_tools_shortcut():
    """RESTful shortcut: Returns all available registered tools."""
    return gateway_router.list_tools()


@app.api_route("/mcp/tools/{tool_name}", methods=["GET", "POST"])
async def call_tool_shortcut(tool_name: str, request: Request):
    """
    RESTful shortcut: Call an MCP tool directly via HTTP GET or POST.
    Supports browser address bar testing (GET) or JSON body payload (POST).
    """
    arguments: Dict[str, Any] = {}
    
    if request.method == "POST":
        try:
            arguments = await request.json()
        except Exception:
            arguments = {}
    elif request.method == "GET":
        arguments = dict(request.query_params)

    try:
        result = await gateway_router.execute_tool(tool_name, arguments)
        return {"ok": True, "tool": tool_name, "result": result}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")
