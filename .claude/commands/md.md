# UNIFIED SESSION PROTOCOL - Anti-Simulation with Complete File Audit Trail

## THIS COMMAND COMBINES VERIFICATION PROTOCOLS WITH COMPREHENSIVE FILE LOGGING

### STEP 1: READ AND ENFORCE CLAUDE.MD
**MANDATORY** - Read @CLAUDE.md located at C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\CLAUDE.md
This establishes anti-pretending protocols that MUST be followed.

### STEP 1.5: LOAD RELEVANT DOCUMENTATION
**IMPORTANT** - Use @read-docs command to load relevant documentation from 97-Local-documentation folder
```bash
# Load documentation for the task at hand
# Usage: @read-docs <topic>
# Examples: @read-docs fastapi, @read-docs pandas, @read-docs tsx-api

# Available documentation topics:
# - javascript, nodejs, express, socketio, redis, winston
# - jest, playwright, python, fastapi, pandas, numpy
# - scikit-learn, streamlit, pybroker, tsx-api/topstepx/projectx
```
This ensures all code follows documented patterns and best practices.

### STEP 2: INITIALIZE SESSION WITH DUAL LOGGING

```bash
# Create both log types for complete audit trail
export TODAY=$(date +%Y-%m-%d)
export SESSION_TIME=$(date +%H%M%S)
export SESSION_ID=$$

# 1. Daily markdown log for file tracking (human-readable)
export DAILY_LOG="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\$TODAY.md"
mkdir -p "C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs"

# 2. Technical verification log (proof of execution)
export VERIFY_LOG="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\verify_$TODAY_$SESSION_TIME.log"

# Start session with verification
echo "=== SESSION START: $(date '+%Y-%m-%d %H:%M:%S.%N') ===" | tee -a "$VERIFY_LOG"
echo "Working directory: $(pwd)" | tee -a "$VERIFY_LOG"
echo "User: $(whoami)" | tee -a "$VERIFY_LOG"
echo "Session ID: $SESSION_ID" | tee -a "$VERIFY_LOG"
echo "Random verification: $RANDOM" | tee -a "$VERIFY_LOG"
echo "System verification: $(uname -a)" | tee -a "$VERIFY_LOG"
ls -la | tee -a "$VERIFY_LOG"

# Start script recording for undeniable proof
script -f "$VERIFY_LOG.script"
```

### STEP 3: CHECK PREVIOUS WORK (Session Continuity)

```bash
# Read yesterday's log to understand context
if [ -f "$DAILY_LOG" ]; then
    echo "Continuing today's log..."
    echo -e "\n---\n## New Session Started: $(date '+%I:%M %p')" >> "$DAILY_LOG"
else
    # Check yesterday's log
    YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
    YESTERDAY_LOG="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\$YESTERDAY.md"
    
    if [ -f "$YESTERDAY_LOG" ]; then
        echo "Found yesterday's log. Reading for context..."
        # Extract "Next Session Priority" section
        grep -A 10 "Next Session Priority" "$YESTERDAY_LOG"
    fi
    
    # Create today's log
    cat > "$DAILY_LOG" << EOF
# Daily Log - $TODAY

## Session Started: $(date '+%I:%M %p')
**Session ID:** $SESSION_ID
**Verification Code:** $RANDOM-$(date +%s%N)

### Previous Session Summary:
[Retrieved from yesterday's log if available]

### Today's Priority:
[Based on previous "Next Session Priority"]

---
EOF
fi
```

### STEP 4: MANDATORY FILE OPERATION LOGGING PROTOCOL

**EVERY file operation MUST follow this pattern:**

```bash
# BEFORE any file operation
echo "[$(date '+%H:%M:%S.%N')] PREPARING FILE OPERATION" | tee -a "$VERIFY_LOG"
echo "Intent: [What you're about to do]" | tee -a "$VERIFY_LOG"
echo "Target: [File path]" | tee -a "$VERIFY_LOG"

# EXECUTE the operation (with proof)
[actual command] 2>&1 | tee -a "$VERIFY_LOG"
EXIT_CODE=$?

# VERIFY the operation
if [ $EXIT_CODE -eq 0 ]; then
    # For file creation/modification
    if [ -f "[filepath]" ]; then
        ls -la "[filepath]" | tee -a "$VERIFY_LOG"
        wc -l "[filepath]" | tee -a "$VERIFY_LOG"
        head -5 "[filepath]" | tee -a "$VERIFY_LOG"
        md5sum "[filepath]" | tee -a "$VERIFY_LOG"
    fi
fi

# LOG TO DAILY MARKDOWN (Comprehensive audit trail)
cat >> "$DAILY_LOG" << EOF

#### File Operation ($(date '+%I:%M:%S %p'))
**Action:** [CREATED/MODIFIED/DELETED/RENAMED]
**File:** \`$FILEPATH\`
**Purpose:** [Why this file was created/modified]
**Verification:** 
- Size: $(stat -c%s "$FILEPATH" 2>/dev/null || echo "N/A") bytes
- Lines: $(wc -l < "$FILEPATH" 2>/dev/null || echo "N/A")
- MD5: $(md5sum "$FILEPATH" | cut -d' ' -f1)
- Exit Code: $EXIT_CODE

**Changes Made:**
- [Specific changes with line numbers]
- [Before/after for modifications]

**Code Snippet:**
\`\`\`[language]
$(head -20 "$FILEPATH" 2>/dev/null || echo "[File content not available]")
\`\`\`

**Status:** $([ $EXIT_CODE -eq 0 ] && echo "✅ Complete" || echo "❌ Failed")
**Proof of Execution:** 
- Timestamp: $(date '+%Y-%m-%d %H:%M:%S.%N')
- Random: $RANDOM
- Session: $SESSION_ID

EOF
```

### STEP 5: CONTINUOUS VERIFICATION (Anti-Simulation)

**Execute these periodically to prove real execution:**

```bash
# Verification checkpoint (run every 10 operations)
echo "=== VERIFICATION CHECKPOINT: $(date '+%H:%M:%S.%N') ===" | tee -a "$VERIFY_LOG"
echo "Random proof: $RANDOM $RANDOM $RANDOM" | tee -a "$VERIFY_LOG"
echo "Process check: $$" | tee -a "$VERIFY_LOG"
ps aux | grep $$ | tee -a "$VERIFY_LOG"
echo "Recent files:" | tee -a "$VERIFY_LOG"
find . -type f -mmin -10 -ls | head -10 | tee -a "$VERIFY_LOG"

# Add to daily log
echo "✓ Verification checkpoint passed at $(date '+%I:%M:%S %p')" >> "$DAILY_LOG"
```

### STEP 6: ERROR HANDLING WITH FULL LOGGING

```bash
# When any error occurs
if [ $? -ne 0 ]; then
    ERROR_TIME=$(date '+%H:%M:%S.%N')
    echo "[ERROR] Command failed at $ERROR_TIME" | tee -a "$VERIFY_LOG"
    
    # Log to daily markdown
    cat >> "$DAILY_LOG" << EOF

#### ⚠️ ERROR DETECTED ($ERROR_TIME)
**Command:** \`$LAST_COMMAND\`
**Exit Code:** $?
**Error Output:**
\`\`\`
$ERROR_OUTPUT
\`\`\`
**Impact:** [What this affects]
**Resolution Attempted:** [How you're fixing it]

EOF
fi
```

### STEP 7: TASK COMPLETION VERIFICATION

**Before claiming ANY task is complete:**

```bash
# Comprehensive verification
echo "=== TASK VERIFICATION: $(date '+%H:%M:%S.%N') ===" | tee -a "$VERIFY_LOG"

# 1. List all files touched
echo "Files modified in this task:" | tee -a "$VERIFY_LOG"
find . -type f -mmin -30 -ls | tee -a "$VERIFY_LOG"

# 2. Show actual content (not simulated)
for file in $(find . -type f -mmin -30); do
    echo "--- Verifying $file ---" | tee -a "$VERIFY_LOG"
    ls -la "$file" | tee -a "$VERIFY_LOG"
    head -10 "$file" | tee -a "$VERIFY_LOG"
    md5sum "$file" | tee -a "$VERIFY_LOG"
done

# 3. Run tests if applicable
if [ -f "package.json" ] || [ -f "requirements.txt" ]; then
    echo "Running tests for verification:" | tee -a "$VERIFY_LOG"
    npm test 2>&1 | tee -a "$VERIFY_LOG" || pytest -v 2>&1 | tee -a "$VERIFY_LOG"
fi

# 4. Add verification signature to daily log
cat >> "$DAILY_LOG" << EOF

### Task Verification Complete
**Time:** $(date '+%I:%M:%S %p')
**Files Changed:** $(find . -type f -mmin -30 | wc -l)
**Tests Run:** $([ -f "package.json" ] && echo "Yes" || echo "N/A")
**Verification Signature:** $SESSION_ID-$RANDOM-$(date +%s%N)
**All Changes Verified:** ✅

EOF
```

### STEP 8: SESSION END PROTOCOL

```bash
# Calculate session statistics
SESSION_END=$(date '+%Y-%m-%d %H:%M:%S.%N')
FILES_CREATED=$(grep -c "CREATED" "$DAILY_LOG")
FILES_MODIFIED=$(grep -c "MODIFIED" "$DAILY_LOG")
FILES_DELETED=$(grep -c "DELETED" "$DAILY_LOG")
ERRORS_COUNT=$(grep -c "ERROR" "$VERIFY_LOG")

# Final verification
echo "=== SESSION END VERIFICATION ===" | tee -a "$VERIFY_LOG"
echo "End time: $SESSION_END" | tee -a "$VERIFY_LOG"
echo "Total commands executed: $(grep -c "EXECUTING" "$VERIFY_LOG")" | tee -a "$VERIFY_LOG"
echo "Errors encountered: $ERRORS_COUNT" | tee -a "$VERIFY_LOG"
echo "Final random proof: $RANDOM-$RANDOM-$RANDOM" | tee -a "$VERIFY_LOG"

# Update daily log with session summary
cat >> "$DAILY_LOG" << EOF

---
## Session Ended: $(date '+%I:%M %p')

### Session Statistics
**Duration:** [Calculate from start]
**Files Created:** $FILES_CREATED
**Files Modified:** $FILES_MODIFIED  
**Files Deleted:** $FILES_DELETED
**Total Operations:** $((FILES_CREATED + FILES_MODIFIED + FILES_DELETED))
**Errors Encountered:** $ERRORS_COUNT

### Detailed File List
$(grep "**File:**" "$DAILY_LOG" | sort | uniq)

### Completed Today
1. [List main accomplishments]
2. [Include file counts]
3. [Note any issues]

### Next Session Priority
1. [Most important task]
2. [Secondary priority]
3. [Files needing review]

### Verification Summary
- Session ID: $SESSION_ID
- Verification Log: $VERIFY_LOG
- Script Recording: $VERIFY_LOG.script
- All operations verified: ✅
- Anti-simulation checks passed: ✅

### Notes for Next Session
[Any important context or reminders]

EOF

# Stop script recording
exit
```

## CRITICAL ENFORCEMENT RULES

1. **DUAL LOGGING IS MANDATORY**
   - Daily markdown log for human review and audit trail
   - Verification log with timestamps/randoms for proof
   - Both stored in: `C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs\`

2. **EVERY FILE OPERATION REQUIRES**
   - Pre-operation declaration
   - Actual command execution (no simulation)
   - Post-operation verification
   - MD5 hash recording
   - Timestamp with nanoseconds
   - Random verification number

3. **NO OPERATION WITHOUT PROOF**
   - Must show actual terminal output
   - Must include exit codes
   - Must verify file exists/was modified
   - Must show file content (not generate it)

4. **CONTINUOUS VERIFICATION**
   - Random checks every 10 operations
   - Process verification via ps/grep
   - File modification timestamps
   - System state snapshots

5. **COMPREHENSIVE AUDIT TRAIL**
   - Every file touched is logged
   - Every command is recorded
   - Every error is documented
   - Every session has unique ID
   - Everything is timestamped

## REMEMBER
- This protocol ensures ZERO simulation
- Creates legal-grade audit trail
- Maintains perfect session continuity
- Provides undeniable proof of work
- Both logs together = complete picture