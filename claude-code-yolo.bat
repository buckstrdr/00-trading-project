@echo off
title Claude Code CTO Dev Team - %USERNAME% - %DATE%
cd /d "C:\Users\salte\ClaudeProjects\github-repos\00-trading-project"

echo ========================================
echo Claude Code - Trading Project
echo ========================================
echo.
echo Your Custom Commands:
echo   /md            - Start with previous session context + full logging
echo   /git-push      - Auto commit and push to GitHub
echo   /git-quick     - Quick push with custom message
echo   /eod-commit    - End of day commit
echo   /show-log      - View today's work log
echo   /audit         - Audit file changes
echo   /log-file      - Log individual file operations
echo.
echo Starting Claude in %cd%
echo.
echo *** YOLO MODE - NO PERMISSION PROMPTS ***
echo.
claude --dangerously-skip-permissions
pause