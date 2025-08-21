@echo off
title Sandbox Test - Prove Files Are Saved
echo ========================================
echo SANDBOX PERSISTENCE TEST
echo ========================================
echo.
echo This will prove your files are saved even after sandbox closes.
echo.
pause

echo.
echo Step 1: Creating test file in your project...
echo Test created at %date% %time% > test-sandbox-proof.txt
echo.
echo Created: test-sandbox-proof.txt
type test-sandbox-proof.txt
echo.

echo Step 2: Launching sandbox (create another file inside)...
echo.
echo When sandbox opens:
echo   1. Navigate to C:\Project
echo   2. Create a file: echo "Created inside sandbox" > inside-sandbox.txt
echo   3. Close the sandbox
echo.
pause

start claude-sandbox-work.wsb

echo.
echo Step 3: Waiting for you to close sandbox...
echo.
pause

echo.
echo Step 4: Checking if files exist...
echo.
if exist "inside-sandbox.txt" (
    echo SUCCESS! File created in sandbox exists here:
    type inside-sandbox.txt
) else (
    echo File not found - did you create it in C:\Project inside sandbox?
)
echo.
echo This proves: Sandbox is temporary, but your file changes are permanent!
echo.
pause