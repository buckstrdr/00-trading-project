# Archived Commands Summary

## Archive Date: 2024-08-21
## Reason: Command Consolidation Project

These 24 commands were archived during the consolidation from 39 to 19 commands.

## Archived Commands List

### Agent-Based Commands (User no longer uses agents)
1. **smartcommit.md** - Used agents for format/test/review chain
2. **endday.md** - Agent-based end of day routine
3. **quickwin.md** - Quick wins using agents
4. **morning.md** - Morning routine with sub-agents
5. **initialize.md** - Initialization with verification agents
6. **predeploy.md** - Pre-deployment with multiple agents

### Redundant Session Commands (Replaced by md.md and session.md)
7. **session-start.md** - Created .claude-sessions logs
8. **smart-usage.md** - Usage tracking

### Redundant Git Commands (Replaced by unified git.md)
9. **commit.md** - Conventional commits (now: /git --message)
10. **git-quick.md** - Quick git operations (now: /git)
11. **eod-commit.md** - End of day commit (now: /git --eod)

### Redundant Logging Commands (Replaced by unified log.md)
12. **Log.md** - Comprehensive logging (now: /log --comprehensive)
13. **log-file.md** - Quick append (now: /log)

### Redundant Display Commands (Replaced by unified display.md)
14. **show99.md** - Show markdown logs (now: /display)
15. **showlog.md** - Show technical logs (now: /display --tech)
16. **check-work.md** - Previous session (now: /display --prev)

### Context Commands (Not actively used)
17. **auto-log-context.md** - Automatic context logging
18. **monitor.md** - Monitor file changes
19. **context-cache.md** - Cache context
20. **cc.md** - Non-functional shortcut

### Redundant Cleanup Commands (Replaced by cleanup.md)
21. **safeclean.md** - Safe cleanup
22. **trading-clean.md** - Trading-specific cleanup

### Redundant Verification (Merged into anti-pretend.md)
23. **verify-status.md** - Status verification

### Session Management
24. **session-start.md** - Alternative session starter

## Migration Guide

### If you were using...
- **smartcommit** → Use `/git --message "msg"` then `/format` and `/test`
- **endday** → Use `/session-end` then `/git --eod`
- **commit** → Use `/git --message "your message"`
- **show99** → Use `/display`
- **showlog** → Use `/display --tech`
- **check-work** → Use `/display --prev`
- **Log** → Use `/log --comprehensive`
- **log-file** → Use `/log`
- **safeclean** → Use `/cleanup`
- **verify-status** → Use `/anti-pretend`

## Note
These files were permanently removed during consolidation. The functionality has been preserved in the unified commands or was deprecated due to non-use (agents).