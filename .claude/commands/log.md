# Unified Logging - Quick Append or Comprehensive Dump

## Two Modes: Quick or Full

### MODE 1: QUICK APPEND (Default - for single file operations)

After ANY file operation, quickly log it:

```bash
# Get current time
TIMESTAMP=$(date '+%I:%M:%S %p')

# Find today's log
TODAY=$(date +%Y-%m-%d)
DAILY_LOG="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\$TODAY.md"

# Ensure log exists
mkdir -p "C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs"
if [ ! -f "$DAILY_LOG" ]; then
    echo "# Daily Log - $TODAY" > "$DAILY_LOG"
    echo "" >> "$DAILY_LOG"
fi

# Append entry for the file operation just completed
cat >> "$DAILY_LOG" << EOF

#### File Operation ($TIMESTAMP)
**Action:** [CREATED/MODIFIED/DELETED/RENAMED]
**File:** \`$FILEPATH\`
**Size:** $(stat -c%s "$FILEPATH" 2>/dev/null || echo "N/A") bytes
**Lines:** $(wc -l < "$FILEPATH" 2>/dev/null || echo "N/A")

**Changes Made:**
[Describe what was changed/added/removed]

**Status:** ✅ Complete
---
EOF

# Verify entry was added
tail -15 "$DAILY_LOG"
```

---

### MODE 2: COMPREHENSIVE SESSION DUMP (for retroactive logging)

When you need to document everything done in current session:

```bash
# Initialize comprehensive logging
TODAY=$(date +%Y-%m-%d)
SESSION_TIME=$(date +%H%M%S)
DAILY_LOG="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\$TODAY.md"
TECH_LOG="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\technical_$TODAY_$SESSION_TIME.log"

# Create both logs
mkdir -p "C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs"

# Technical verification log
echo "=== COMPREHENSIVE SESSION LOG: $(date '+%Y-%m-%d %H:%M:%S.%N') ===" | tee -a "$TECH_LOG"
echo "Session ID: $$" | tee -a "$TECH_LOG"
echo "Working directory: $(pwd)" | tee -a "$TECH_LOG"
echo "User: $(whoami)" | tee -a "$TECH_LOG"
echo "Terminal: $(tty)" | tee -a "$TECH_LOG"

# Document ALL files modified in session
echo "=== FILES MODIFIED IN SESSION ===" | tee -a "$TECH_LOG"
find . -type f -mmin -120 -ls 2>/dev/null | tee -a "$TECH_LOG"

# For each file, create detailed log entry
for file in $(find . -type f -mmin -120 2>/dev/null | head -20); do
    echo "--- Documenting: $file ---" | tee -a "$TECH_LOG"
    ls -la "$file" | tee -a "$TECH_LOG"
    wc -l "$file" 2>/dev/null | tee -a "$TECH_LOG"
    md5sum "$file" 2>/dev/null | tee -a "$TECH_LOG"
    
    # Also append to daily markdown log
    cat >> "$DAILY_LOG" << EOF

#### Retroactive Log: $file
**Time:** $(date '+%I:%M:%S %p')
**File:** \`$file\`
**Size:** $(stat -c%s "$file" 2>/dev/null) bytes
**MD5:** $(md5sum "$file" 2>/dev/null | cut -d' ' -f1)
**Status:** 📝 Retroactively logged
EOF
done

# List all commands executed (if available)
echo "=== COMMAND HISTORY ===" | tee -a "$TECH_LOG"
history | tail -50 | tee -a "$TECH_LOG"

# Show process tree
echo "=== PROCESS VERIFICATION ===" | tee -a "$TECH_LOG"
ps aux | grep $$ | tee -a "$TECH_LOG"

# Final summary in markdown
cat >> "$DAILY_LOG" << EOF

---
### Comprehensive Session Dump
**Time:** $(date '+%I:%M:%S %p')
**Files Logged:** $(find . -type f -mmin -120 2>/dev/null | wc -l)
**Technical Log:** $TECH_LOG
**Session Verified:** ✅
---
EOF

echo "Comprehensive logging complete!"
echo "Markdown log: $DAILY_LOG"
echo "Technical log: $TECH_LOG"
```

---

## USAGE PATTERNS

### For Single File Operations:
```bash
# After creating/modifying a file, immediately run:
/unified-log quick [filepath] [action] [description]
```

### For Session Documentation:
```bash
# When approaching context limits or ending session:
/unified-log full
```

### For Verification:
```bash
# To check if all operations were logged:
/audit
```

---

## KEY FEATURES

1. **Dual Mode:** Quick append OR comprehensive dump
2. **Consistent Location:** All logs in `99-claude-daily-logs`
3. **Both Formats:** Markdown for humans, technical for verification
4. **Retroactive Capability:** Can document past operations
5. **Verification Built-in:** MD5 hashes, timestamps, file sizes
6. **Session Tracking:** Process IDs, command history

---

## REPLACES
- **Log.md** (comprehensive logging functionality)
- **log-file.md** (quick append functionality)

Use this single command for ALL logging needs!