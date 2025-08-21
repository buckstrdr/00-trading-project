# Claude Commands Reference

## Overview
This folder contains consolidated Claude commands for project management, code quality, and session tracking. Commands were consolidated from 39 files down to 19 essential commands (51% reduction).

## Quick Command Reference

### Session Management
- **/md** - Full session initialization with anti-simulation verification and dual logging
- **/session** - Lightweight session start (reads previous work)
- **/session-end** - End session with summary and next priorities
- **/anti-pretend** - Force real execution proof (10 verification categories)

### Logging & Display
- **/log** - Unified logging command
  - Default: Quick append to daily log
  - `--comprehensive`: Full session dump with verification
- **/display** - View logs and session information
  - Default: Today's markdown log
  - `--prev`: Previous session summary
  - `--tech`: Technical verification log
  - `--stats`: Statistics only
  - `--all`: Everything
  - `--last N`: Last N lines

### Git Operations
- **/git** - Unified git command with arguments
  - `--status`: Show git status
  - `--all`: Stage all changes
  - `--message "msg"`: Commit with message
  - `--push`: Push to remote
  - `--amend`: Amend last commit
  - `--eod`: End of day commit and push
- **/git-push** - Smart git push with branch detection

### Code Quality
- **/format** - Auto-format code using project formatter
- **/fix-imports** - Fix broken imports after moving files
- **/remove-comments** - Remove obvious/redundant comments
- **/test** - Run tests and analyze failures
- **/review** - Code review for security/bugs/performance

### Search & Analysis
- **/find-todos** - Find all TODOs, FIXMEs, HACKs
- **/audit** - Find unlogged file operations
- **/deepfix** - Deep analysis and fix of complex issues

### Cleanup
- **/cleanup** - Remove Claude temporary files (claude_*)
- **/cleanup-types** - Clean up type definition issues
- **/undo** - Revert recent changes

## Directory Structure
```
.claude/
├── commands/          # Active command files
│   └── ARCHIVED/      # Deprecated commands (24 files)
├── .claude_logs/      # Technical verification logs
├── hooks/             # Custom hooks
├── settings.local.json
└── README.md          # This file
```

## Log Locations
- **Markdown logs**: `99-claude-daily-logs/YYYY-MM-DD.md`
- **Technical logs**: `.claude/.claude_logs/session_*.log`

## Command Consolidation History

### Original Structure (39 files)
Had duplicate commands across 4 folders with overlapping functionality.

### Consolidation Results
- **Session starters**: 6 → 2 (md.md, session.md)
- **Git commands**: 3 → 1 unified (git.md)
- **Logging**: 2 → 1 unified (log.md)
- **Display**: 3 → 1 unified (display.md)
- **Cleanup**: 3 → 1 (cleanup.md)
- **Archived**: 24 files (agent-based and redundant commands)

### Archived Commands
The following commands were archived because they:
- Use agents (no longer used)
- Are redundant with consolidated commands
- Have been replaced by better alternatives

**Archived files:**
- Agent-based: smartcommit, endday, quickwin, morning, initialize
- Redundant: verify-status, Log, log-file, show99, showlog, check-work
- Git: commit, git-quick, eod-commit
- Context: auto-log-context, monitor, context-cache, cc
- Cleanup: safeclean, trading-clean
- Other: session-start, smart-usage, predeploy

## Usage Tips

1. **Start sessions with /md** for full verification and logging
2. **Use /log frequently** to track file operations
3. **Run /anti-pretend** if verification is questioned
4. **Use /display --tech** to review technical logs
5. **Run /cleanup** before commits to remove Claude files

## Important Files

- **CLAUDE.md** - Mandatory verification protocols (in project root)
- **99-claude-daily-logs/** - Daily session logs (in project root)
- **.claude_logs/** - Technical verification logs

## Hooks
Custom hooks can be placed in the `hooks/` directory for automated workflows.