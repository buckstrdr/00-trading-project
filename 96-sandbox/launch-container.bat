@echo off
title Claude Code Container Launcher
echo ========================================
echo Claude Code Safe Container Options
echo ========================================
echo.
echo Choose your isolation method:
echo.
echo 1. Windows Sandbox (Recommended - Easiest)
echo 2. Docker Container
echo 3. Check Windows Sandbox availability
echo 4. Setup instructions
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto sandbox
if "%choice%"=="2" goto docker
if "%choice%"=="3" goto check
if "%choice%"=="4" goto instructions

:sandbox
echo.
echo Launching Windows Sandbox with Claude Code YOLO mode...
echo.
if exist "96-sandbox\claude-sandbox.wsb" (
    start 96-sandbox\claude-sandbox.wsb
    echo Sandbox launched! Claude Code will run in YOLO mode inside.
) else if exist "claude-sandbox.wsb" (
    start claude-sandbox.wsb
    echo Sandbox launched! Claude Code will run in YOLO mode inside.
) else (
    echo ERROR: claude-sandbox.wsb not found!
)
pause
exit

:docker
echo.
echo Starting Docker container with Claude Code YOLO mode...
echo.
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit
)
echo Building Docker image...
docker-compose build
echo.
echo Starting container...
docker-compose run --rm claude-yolo
pause
exit

:check
echo.
echo Checking Windows Sandbox availability...
echo.
powershell -Command "Get-WindowsOptionalFeature -Online -FeatureName 'Containers-DisposableClientVM' | Select State"
echo.
echo If State shows "Disabled", run this as Administrator:
echo powershell Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
echo.
pause
exit

:instructions
echo.
echo === SETUP INSTRUCTIONS ===
echo.
echo OPTION 1: Windows Sandbox (Easiest)
echo -------------------------------------
echo 1. Requires Windows 10/11 Pro or Enterprise
echo 2. Enable from "Turn Windows features on or off"
echo 3. Double-click claude-sandbox.wsb to launch
echo.
echo OPTION 2: Docker
echo -----------------
echo 1. Install Docker Desktop
echo 2. Run: docker-compose build
echo 3. Run: docker-compose run --rm claude-yolo
echo.
echo Both options provide:
echo - Complete isolation from main system
echo - YOLO mode (no permission prompts)
echo - Easy cleanup (just close container)
echo.
pause
exit