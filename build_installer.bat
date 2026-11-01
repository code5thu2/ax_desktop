@echo off
setlocal enabledelayedexpansion
title Build Installer - AX Desktop
cd /d "%~dp0"

echo ======================================================================
echo  1/3. Compiling Frontend (Vue 3 + PrimeVue 4)
echo ======================================================================
cd frontend
call npm run build
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend build failed!
    cd /d "%~dp0"
    pause
    exit /b %ERRORLEVEL%
)
cd /d "%~dp0"

echo.
echo ======================================================================
echo  2/3. Packaging Native Installer via Tauri Bundle (NSIS Setup .exe)
echo ======================================================================
call npx --prefix frontend tauri build
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Tauri installer bundling failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo  3/3. Post-Build Auto Cleanup (Reclaiming Disk Space)
echo ======================================================================
if exist "target\debug" (
    echo [CLEANUP] Found target\debug cache. Removing to reclaim disk space...
    rd /s /q "target\debug"
    echo [CLEANUP] target\debug removed successfully!
) else (
    echo [CLEANUP] target\debug already clean.
)

echo.
echo ======================================================================
echo  INSTALLER BUILD SUCCESS!
echo ======================================================================
if exist "target\release\bundle\nsis" (
    echo Setup Executable generated at:
    dir /b /s "target\release\bundle\nsis\*.exe"
)
echo ======================================================================
pause
