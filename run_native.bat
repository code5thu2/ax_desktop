@echo off
title AX Desktop (Tauri v2 Native Rust)
cd /d "%~dp0"

echo ======================================================================
echo Launching AX Desktop (Native Rust 1.90.0 + Tauri v2.12.5)
echo Binary: target\release\desktop.exe
echo ======================================================================

start "" "target\release\desktop.exe"
