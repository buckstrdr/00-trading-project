@echo off
echo ========================================
echo Claude Sandbox Tools
echo ========================================
echo.
echo All sandbox tools have been moved to: 96-sandbox\
echo.
echo 1. Launch Container Menu
echo 2. Safe Workflow (Git + Sandbox)
echo 3. Git Safety Tools
echo 4. Open Sandbox Folder
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    start launch-container.bat
) else if "%choice%"=="2" (
    start claude-safe-workflow.bat
) else if "%choice%"=="3" (
    start git-safety.bat
) else if "%choice%"=="4" (
    explorer .
) else (
    echo Invalid choice
    pause
)