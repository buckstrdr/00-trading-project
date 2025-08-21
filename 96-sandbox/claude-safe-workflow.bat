@echo off
title Safe Claude YOLO Workflow
echo ========================================
echo SAFE CLAUDE YOLO MODE WORKFLOW
echo ========================================
echo.
echo This script manages the complete safe workflow
echo.

cd /d "C:\Users\salte\ClaudeProjects\github-repos\00-trading-project"

:menu
echo Choose your action:
echo.
echo === BEFORE CLAUDE ===
echo 1. Create safety checkpoint (git commit)
echo 2. Create work branch (even safer)
echo.
echo === RUN CLAUDE ===
echo 3. Launch Claude YOLO in Sandbox
echo 4. Launch Claude YOLO (no sandbox)
echo.
echo === AFTER CLAUDE ===
echo 5. Review changes (git diff)
echo 6. Keep all changes (commit)
echo 7. Discard ALL changes (restore)
echo 8. Cherry-pick changes (selective)
echo.
echo 0. Exit
echo.
set /p choice="Enter your choice: "

if "%choice%"=="1" goto checkpoint
if "%choice%"=="2" goto workbranch
if "%choice%"=="3" goto sandbox
if "%choice%"=="4" goto yolo
if "%choice%"=="5" goto review
if "%choice%"=="6" goto keep
if "%choice%"=="7" goto discard
if "%choice%"=="8" goto cherry
if "%choice%"=="0" exit

:checkpoint
echo.
echo Creating safety checkpoint...
git add .
git commit -m "Safety checkpoint - %date% %time%"
echo ✓ Checkpoint created! Safe to run Claude.
echo.
pause
goto menu

:workbranch
echo.
git checkout -b claude-session-%random%
echo ✓ Created work branch. Original code safe on main branch.
echo.
pause
goto menu

:sandbox
echo.
echo Launching Claude YOLO in Windows Sandbox...
start 96-sandbox\claude-sandbox-work.wsb
echo ✓ Sandbox launched
echo.
pause
goto menu

:yolo
echo.
echo Launching Claude YOLO mode directly...
start ..\claude-code-yolo.bat
echo ✓ Claude YOLO launched
echo.
pause
goto menu

:review
echo.
echo === FILES CHANGED ===
git status --short
echo.
echo === DETAILED CHANGES ===
git diff --stat
echo.
echo To see full diff, run: git diff
pause
goto menu

:keep
echo.
git add .
set /p msg="Commit message: "
git commit -m "%msg%"
echo ✓ Changes committed!
echo.
pause
goto menu

:discard
echo.
echo ⚠️ WARNING: This will DELETE all changes!
set /p confirm="Type DISCARD to confirm: "
if "%confirm%"=="DISCARD" (
    git reset --hard HEAD
    git clean -fd
    echo ✓ All changes discarded. Restored to last commit.
) else (
    echo Cancelled.
)
echo.
pause
goto menu

:cherry
echo.
echo === Modified Files ===
git status --short
echo.
echo Commands:
echo   git checkout -- [filename]  = Discard changes to file
echo   git add [filename]          = Keep changes to file
echo   git diff [filename]         = See changes in file
echo.
cmd /k "echo Cherry-pick mode. Use git commands above. Type 'exit' when done."
goto menu