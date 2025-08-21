# File Audit Check

Quick audit to ensure all file operations have been logged.

## Automatic Audit Steps:

1. **List Recent File Operations:**
   - Check git status for uncommitted changes
   - List files modified in current directory in last hour
   - Show any new files created today

2. **Compare Against Log:**
   - Read today's log from `C:\Users\salte\ClaudeProjects\github-repos\99-claude-daily-logs\YYYY-MM-DD.md`
   - Extract all file paths mentioned in log
   - Compare with actual file changes

3. **Report Missing Entries:**
   ```
   ⚠️ UNLOGGED FILES DETECTED:
   - [File path] - Modified but not in log
   - [File path] - Created but not in log
   ```

4. **Generate Missing Log Entries:**
   For each unlogged file, create a log entry template:
   ```markdown
   #### File Operation (NEEDS TIMESTAMP)
   **Action:** [MODIFIED/CREATED]
   **File:** `[Path]`
   **Changes:** [TO BE FILLED]
   **Status:** ⚠️ Retroactive Entry
   ```

5. **Append Missing Entries:**
   Add all missing entries to the log with a note about retroactive logging

Use this periodically to ensure logging compliance!