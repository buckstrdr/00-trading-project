# 96-sandbox - Claude Code Safe Execution Environment

This folder contains all tools for running Claude Code in YOLO mode safely.

## Quick Start

### Windows Sandbox (Easiest):
```batch
# From this folder:
launch-container.bat
# Choose option 1
```

### Docker:
```batch
# From this folder:
docker-compose build
docker-compose run --rm claude-yolo
```

### Safe Workflow:
```batch
# Complete workflow with Git safety:
claude-safe-workflow.bat
```

## Files in This Folder:

### Windows Sandbox Configurations:
- `claude-sandbox-work.wsb` - Full read/write access to project
- `claude-sandbox-safe.wsb` - Read-only project, separate output folder
- `claude-sandbox.wsb` - Original configuration

### Docker Setup:
- `Dockerfile` - Container definition
- `docker-compose.yml` - Docker orchestration

### Workflow Scripts:
- `launch-container.bat` - Main launcher with menu
- `claude-safe-workflow.bat` - Complete Git + Sandbox workflow
- `git-safety.bat` - Git backup and restore utilities

### Documentation:
- `SANDBOX-SETUP.md` - How to enable Windows Sandbox
- `SANDBOX-EXPLAINED.md` - How sandbox preserves your code
- `GIT-SAFETY-GUIDE.md` - Git safety strategies
- `test-sandbox-persistence.bat` - Proof that files are saved

## How It Works:

1. **Git Checkpoint** - Create restore point
2. **Launch Sandbox** - Isolated environment
3. **Run Claude YOLO** - No permission prompts
4. **Review Changes** - Git diff
5. **Keep or Discard** - Your choice!

## Key Points:

- Your code changes ARE saved (sandbox only deletes environment)
- Git provides unlimited undo
- Sandbox protects your system
- YOLO mode gives maximum speed

## To Run From Main Project Folder:

```batch
# From 00-trading-project folder:
96-sandbox\launch-container.bat
96-sandbox\claude-safe-workflow.bat
```