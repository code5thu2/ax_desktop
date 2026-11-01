"""
Stateless Pure HTTP MCP Gateway Router
Implements JSON-RPC 2.0 (POST /mcp) and REST shortcuts for AI client tool execution.
Strictly pure HTTP request-response; NO Server-Sent Events (SSE).
"""
import asyncio
import inspect
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import config

# Add D:\AI_MCP to sys.path to allow dynamic imports of in-house servers
ai_mcp_path = str(config.SOURCE_MCP_DIR.parent)
if ai_mcp_path not in sys.path:
    sys.path.insert(0, ai_mcp_path)


class GatewayRouter:
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._load_active_servers()

    def _load_active_servers(self):
        """Discovers and mounts MCP servers from D:\\AI_MCP\\servers."""
        server_mapping = {
            "archive": "servers.archive_mcp.server",
            "excel": "servers.excel_mcp.server",
            "docs": "servers.docs_mcp.server",
            "fs": "servers.fs_mcp.server",
            "postgres": "servers.postgres_mcp.server",
            "screenshot": "servers.screenshot_mcp.server",
            "gitlab": "servers.gitlab_mcp.server",
            "jenkins": "servers.jenkins_mcp.server",
            "zalo": "servers.zalo_mcp.server",
        }

        for server_id, module_path in server_mapping.items():
            try:
                mod = __import__(module_path, fromlist=["mcp"])
                mcp_instance = getattr(mod, "mcp", None)
                if mcp_instance and hasattr(mcp_instance, "_tool_manager"):
                    for raw_name, tool_obj in mcp_instance._tool_manager._tools.items():
                        namespaced_name = f"{server_id}__{raw_name}"
                        tool_info = {
                            "server_id": server_id,
                            "raw_name": raw_name,
                            "namespaced_name": namespaced_name,
                            "tool_obj": tool_obj,
                            "description": getattr(tool_obj, "description", "") or "",
                            "parameters": getattr(tool_obj, "parameters", {}) or {
                                "type": "object",
                                "properties": {}
                            }
                        }
                        # Register both namespaced and raw fallback
                        self.tools[namespaced_name] = tool_info
                        if raw_name not in self.tools:
                            self.tools[raw_name] = tool_info
            except Exception as e:
                # Server might require missing dependencies (e.g. postgres db connection)
                # print(f"Gateway Notice: could not auto-load {server_id}: {e}")
                pass

    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns list of tools formatted for MCP tools/list."""
        unique_tools = {}
        for name, info in self.tools.items():
            ns_name = info["namespaced_name"]
            if ns_name not in unique_tools:
                unique_tools[ns_name] = {
                    "name": ns_name,
                    "description": info["description"],
                    "inputSchema": info["parameters"]
                }
        return list(unique_tools.values())

    async def execute_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
        """Executes target tool by name (either namespaced or raw)."""
        tool_info = self.tools.get(tool_name)
        if not tool_info:
            raise KeyError(f"Tool '{tool_name}' not found in registered MCP tools")

        tool_obj = tool_info["tool_obj"]
        args = arguments or {}

        # If tool_obj has fn or run
        func = getattr(tool_obj, "fn", None)
        if not func:
            func = getattr(tool_obj, "run", None)

        if not callable(func):
            raise RuntimeError(f"Tool '{tool_name}' has no callable function")

        if inspect.iscoroutinefunction(func):
            result = await func(**args)
        else:
            result = func(**args)

        return result

    async def handle_jsonrpc(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Main JSON-RPC 2.0 dispatcher for POST /mcp."""
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {}) or {}

        if not method:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32600, "message": "Invalid Request: missing method"}
            }

        # 1. initialize
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True}
                    },
                    "serverInfo": {
                        "name": "in-house-mcp-gateway",
                        "version": "1.0.0"
                    }
                }
            }

        # 2. tools/list
        elif method == "tools/list":
            tools_list = self.list_tools()
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "tools": tools_list
                }
            }

        # 3. tools/call
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            if not tool_name:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": "Missing 'name' in tools/call parameters"}
                }

            try:
                output = await self.execute_tool(tool_name, tool_args)
                # Serialize output to string for MCP content text block
                if isinstance(output, (dict, list)):
                    text_out = json.dumps(output, ensure_ascii=False)
                else:
                    text_out = str(output)

                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": text_out}
                        ]
                    }
                }
            except KeyError as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": str(e)}
                }
            except Exception as e:
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": f"Tool execution failed: {str(e)}"}
                }

        # Unknown method
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method '{method}' not found"}
            }


# Global instance
gateway_router = GatewayRouter()
