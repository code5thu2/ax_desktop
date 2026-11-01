@echo off
title MCP Protocol Studio
cd /d "%~dp0"

set "PYTHON_EXE=C:\Program Files\Python313\python.exe"
if not exist "%PYTHON_EXE%" (
    where python >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_EXE=python"
    ) else (
        set "PYTHON_EXE=D:\AI_MCP\.venv\Scripts\python.exe"
    )
)

"%PYTHON_EXE%" plugin_desktop.py %*
if errorlevel 1 pause
