"""
Catalog Service for Registry
Handles searching, listing, and retrieving MCP packages.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import config


class CatalogService:
    def __init__(self, catalog_path: Path = config.CATALOG_FILE):
        self.catalog_path = catalog_path

    def _load_catalog(self) -> Dict[str, Any]:
        if not self.catalog_path.exists():
            return {"version": "1.0.0", "servers": []}
        try:
            with open(self.catalog_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"version": "1.0.0", "servers": []}

    def list_servers(self, query: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        catalog = self._load_catalog()
        servers = catalog.get("servers", [])

        if query:
            q = query.lower()
            servers = [
                s for s in servers
                if q in s.get("id", "").lower()
                or q in s.get("name", "").lower()
                or q in s.get("summary", "").lower()
                or any(q in t.get("name", "").lower() for t in s.get("tools", []))
            ]

        if category:
            cat = category.lower()
            servers = [s for s in servers if s.get("category", "").lower() == cat]

        return servers

    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        servers = self.list_servers()
        for s in servers:
            if s.get("id") == server_id:
                return s
        return None

    def get_bundle_path(self, server_id: str) -> Optional[Path]:
        bundle_path = config.PACKAGES_DIR / f"{server_id}.zip"
        if bundle_path.exists() and bundle_path.is_file():
            return bundle_path
        return None


# Global instance
catalog_service = CatalogService()
