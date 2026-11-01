@echo off
title MCP Protocol Studio Desktop
cd /d "%~dp0frontend"
call run_plugin_manager.bat %*
