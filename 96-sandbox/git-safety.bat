@echo off
title Git Safety for Claude YOLO Mode
echo ========================================
echo Git Safety Setup for Claude YOLO Mode
echo ========================================
echo.

cd /d "C:\Users\salte\ClaudeProjects\github-repos\00-trading-project"

echo Current git status:
git status --short
echo.

echo Choose safety level:
echo.
echo 1. Create backup commit (on current branch)
echo 2. Create temporary branch for Claude's work
echo 3. Just show me what's changed (git diff)
echo 4. RESTORE - Discard all changes since last commit
echo 5. Selective restore (choose files)
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto backup
if "%choice%"=="2" goto branch
if "%choice%"=="3" goto diff
if "%choice%"=="4" goto restore
if "%choice%"=="5" goto selective

:backup
echo.
echo Creating backup commit...
git add .
git commit -m "Backup before Claude YOLO session - %date% %time%"
echo.
echo Backup created! Safe to run Claude YOLO mode.
echo To restore: git reset --hard HEAD~1
pause
exit

:branch
echo.
set /p branchname="Enter branch name (or press Enter for 'claude-work'): "
if "%branchname%"=="" set branchname=claude-work
echo Creating and switching to branch: %branchname%
git checkout -b %branchname%
echo.
echo Now on safe branch: %branchname%
echo Original code is safe on previous branch
echo To restore: git checkout main
pause
exit

:diff
echo.
echo === CHANGES SINCE LAST COMMIT ===
git diff
echo.
echo === UNTRACKED FILES ===
git status --short | findstr "^??"
pause
exit

:restore
echo.
echo WARNING: This will DELETE all changes since last commit!
echo.
set /p confirm="Type YES to confirm: "
if "%confirm%"=="YES" (
    git reset --hard HEAD
    git clean -fd
    echo All changes discarded. Restored to last commit.
) else (
    echo Cancelled. No changes made.
)
pause
exit

:selective
echo.
echo === Modified files ===
git status --short
echo.
echo Enter filename to restore (or 'exit' to quit):
set /p filename="File: "
if "%filename%"=="exit" exit
git checkout -- %filename%
echo Restored: %filename%
goto selective