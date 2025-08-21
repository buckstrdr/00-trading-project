# Claude Hooks Configuration

## Overview
Hooks are shell commands that execute automatically in response to Claude events. They can be configured in your settings to run before/after certain actions.

## Available Hook Types

### 1. **user-prompt-submit-hook**
- Triggers: After user submits a prompt
- Use case: Log user inputs, validate requests
- Example: `echo "[$(date)] User: $1" >> .claude_logs/user_prompts.log`

### 2. **assistant-response-complete-hook**
- Triggers: After Claude completes a response
- Use case: Log completions, trigger notifications
- Example: `echo "Claude completed response" | notify-send`

### 3. **tool-use-hook**
- Triggers: Before/after tool execution
- Use case: Validate tool calls, log operations
- Example: `echo "Tool: $TOOL_NAME" >> .claude_logs/tools.log`

### 4. **file-operation-hook**
- Triggers: On file create/modify/delete
- Use case: Track file changes, backup files
- Example: `git add -A && git commit -m "Auto-save: $1"`

### 5. **error-hook**
- Triggers: When errors occur
- Use case: Log errors, send alerts
- Example: `echo "ERROR: $1" >> .claude_logs/errors.log`

## Configuration

Hooks are configured in your Claude settings JSON:

```json
{
  "hooks": {
    "user-prompt-submit-hook": "path/to/script.sh",
    "assistant-response-complete-hook": "echo 'Response complete'",
    "tool-use-hook": ".claude/hooks/log-tool.sh"
  }
}
```

## Creating Hook Scripts

### Example: Log All File Operations
Create `.claude/hooks/log-files.sh`:
```bash
#!/bin/bash
LOGFILE=".claude_logs/file_operations.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1 $2" >> "$LOGFILE"
```

### Example: Auto-commit on File Changes
Create `.claude/hooks/auto-commit.sh`:
```bash
#!/bin/bash
if [[ $1 == "MODIFIED" ]] || [[ $1 == "CREATED" ]]; then
    git add "$2"
    git commit -m "Auto-save: $2" --no-verify
fi
```

### Example: Validate Commands
Create `.claude/hooks/validate-command.sh`:
```bash
#!/bin/bash
# Block dangerous commands
if [[ $1 =~ (rm -rf|format C:|del /s) ]]; then
    echo "BLOCKED: Dangerous command detected"
    exit 1
fi
```

## Best Practices

1. **Keep hooks fast** - They run synchronously
2. **Log to .claude_logs/** - Centralized logging
3. **Use absolute paths** - Avoid path issues
4. **Handle errors gracefully** - Don't break Claude's flow
5. **Test hooks separately** - Ensure they work before configuring

## Current Hooks Status

No hooks currently configured in this project.

To add hooks:
1. Create hook scripts in this directory
2. Update settings.local.json with hook configurations
3. Test with simple echo commands first

## Common Hook Patterns

### Session Tracking
```bash
echo "Session: $SESSION_ID | Time: $(date)" >> .claude_logs/sessions.log
```

### Command Auditing
```bash
echo "$USER | $(date) | $COMMAND" >> .claude_logs/audit.log
```

### Error Collection
```bash
[[ $EXIT_CODE -ne 0 ]] && echo "Failed: $COMMAND" >> .claude_logs/failures.log
```

### Notification
```bash
terminal-notifier -message "Claude: $1" -title "Task Complete"
```

## Testing Hooks

Test a hook manually:
```bash
# Test user prompt hook
.claude/hooks/my-hook.sh "Test prompt"

# Test with environment variables
TOOL_NAME="Bash" .claude/hooks/log-tool.sh
```