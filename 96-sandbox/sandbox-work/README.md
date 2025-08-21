# Sandbox Work Directory

This folder is used when running Claude Code in "Safe Mode" sandbox.

## Purpose:
- Receives output from sandbox when main project is read-only
- Allows you to review Claude's work before merging into main project
- Acts as a staging area for experimental changes

## Usage:
1. Run `claude-sandbox-safe.wsb` (safe mode)
2. Claude can read from main project but only write here
3. Review changes in this folder
4. Copy approved changes to main project

## Cleanup:
This folder can be safely deleted anytime to clean up test files.