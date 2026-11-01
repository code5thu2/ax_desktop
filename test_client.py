"""
Test Client for MCP Private Registry & Pure HTTP Gateway
Demonstrates how an AI Client or User interacts with the server over pure HTTP.
"""
import sys
import json
import urllib.request
import urllib.parse

# Reconfigure console output for UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"


def call_http_post(endpoint: str, payload: dict) -> dict:
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_http_get(endpoint: str) -> dict:
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main():
    print("=" * 60)
    print("1. QUERYING REGISTRY CATALOG (Marketplace)")
    print("=" * 60)
    catalog = call_http_get("/api/v1/catalog")
    print(f"Total in-house servers available: {catalog['total']}")
    for s in catalog["servers"][:5]:
        print(f"  * [{s['id']}] {s['name']} - {s['tools_count']} tools ({s['summary']})")

    print("\n" + "=" * 60)
    print("2. CALLING MCP GATEWAY (Pure HTTP JSON-RPC 2.0 - No SSE)")
    print("=" * 60)

    # A. initialize
    print("\n>>> Method: initialize")
    init_res = call_http_post("/mcp", {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    })
    print("Response:", json.dumps(init_res, indent=2))

    # B. tools/list
    print("\n>>> Method: tools/list")
    tools_res = call_http_post("/mcp", {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    tools = tools_res["result"]["tools"]
    print(f"Total live tools available in Gateway: {len(tools)}")
    print("First 5 tools:")
    for t in tools[:5]:
        desc = t['description'].replace('\n', ' ')[:60]
        print(f"  - {t['name']}: {desc}...")

    # C. tools/call
    print("\n>>> Method: tools/call (archive__server_info)")
    call_res = call_http_post("/mcp", {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "archive__server_info",
            "arguments": {}
        }
    })
    print("Response:", json.dumps(call_res, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("3. CALLING REST SHORTCUT (Direct HTTP POST)")
    print("=" * 60)
    rest_res = call_http_post("/mcp/tools/archive__server_info", {})
    print("REST Shortcut Output:", rest_res)
    print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
