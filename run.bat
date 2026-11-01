@echo off
title MCP Protocol Studio (:8000)
cd /d "%~dp0"

echo ======================================================================
echo Starting MCP Protocol Studio (Full-Stack Gateway + UI)
echo Web UI:          http://127.0.0.1:8000/
echo Swagger UI Docs: http://127.0.0.1:8000/docs
echo Catalog API:     http://127.0.0.1:8000/api/v1/catalog
echo MCP Gateway:     http://127.0.0.1:8000/mcp (Pure HTTP POST - No SSE)
echo ======================================================================

"D:\AI_MCP\.venv\Scripts\python.exe" -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause
