@echo off
setlocal enabledelayedexpansion
title Build Release - MCP Protocol Studio
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
echo  2/3. Compiling Native Rust Binary (LTO, Opt-level 3, Strip)
echo ======================================================================
cargo build --release -p desktop
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Cargo release build failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ======================================================================
echo  3/3. Post-Build Auto Cleanup (Reclaiming Disk Space)
echo ======================================================================
if exist "target\debug" (
    echo [CLEANUP] Found target\debug cache. Removing to reclaim ~3.4 GB...
    rd /s /q "target\debug"
    echo [CLEANUP] target\debug removed successfully!
) else (
    echo [CLEANUP] target\debug already clean.
)

echo.
echo ======================================================================
echo  BUILD SUCCESS!
echo ======================================================================
if exist "target\release\desktop.exe" (
    for %%I in ("target\release\desktop.exe") do (
        set "BYTES=%%~zI"
        set /a "KB=BYTES/1024"
        set /a "MB=KB/1024"
        echo Executable: target\release\desktop.exe [!MB! MB / !BYTES! bytes]
    )
    echo Launcher:   run_native.bat
)
echo ======================================================================
