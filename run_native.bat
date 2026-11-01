@echo off
title MCP Protocol Studio (Tauri v2 Native Rust)
cd /d "%~dp0"

echo ======================================================================
echo Launching MCP Protocol Studio (Native Rust 1.90.0 + Tauri v2.12.5)
echo Binary: target\release\desktop.exe (4.17 MB)
echo ======================================================================

start "" "target\release\desktop.exe"
