# Unified Git Command - Flexible Git Operations

## Usage: /git [options]

### OPTIONS:
- `--all` or `-a` : Stage all files (including untracked)
- `--push` or `-p` : Push to remote after commit
- `--eod` : End of day mode (stage all + timestamp commit + push)
- `--message "text"` or `-m "text"` : Provide commit message
- `--amend` : Amend previous commit
- `--status` or `-s` : Just show status (no commit)

### DEFAULT BEHAVIOR (no arguments):
Analyzes changes and creates smart commit message

---

## IMPLEMENTATION:

```bash
# Parse arguments
STAGE_ALL=false
DO_PUSH=false
EOD_MODE=false
CUSTOM_MESSAGE=""
AMEND=false
STATUS_ONLY=false

for arg in "$@"; do
    case $arg in
        --all|-a)
            STAGE_ALL=true
            ;;
        --push|-p)
            DO_PUSH=true
            ;;
        --eod)
            EOD_MODE=true
            STAGE_ALL=true
            DO_PUSH=true
            ;;
        --message|-m)
            shift
            CUSTOM_MESSAGE="$1"
            ;;
        --amend)
            AMEND=true
            ;;
        --status|-s)
            STATUS_ONLY=true
            ;;
    esac
    shift
done

# Status only mode
if [ "$STATUS_ONLY" = true ]; then
    git status
    git diff --stat
    exit 0
fi

# Check for changes
if ! git diff --cached --quiet || ! git diff --quiet; then
    echo "Changes detected:"
    git status --short
else
    echo "No changes to commit"
    exit 0
fi

# Stage files if requested
if [ "$STAGE_ALL" = true ]; then
    echo "Staging all files..."
    git add -A
elif git diff --cached --quiet; then
    echo "No files staged. Staging modified files..."
    git add -u
fi

# Show what will be committed
echo "Files to be committed:"
git diff --cached --name-status

# Determine commit message
if [ "$EOD_MODE" = true ]; then
    # End of day mode - timestamp commit
    COMMIT_MESSAGE="End of day commit - $(date +%Y-%m-%d)"
    echo "Using EOD timestamp message: $COMMIT_MESSAGE"
    
elif [ -n "$CUSTOM_MESSAGE" ]; then
    # Custom message provided
    COMMIT_MESSAGE="$CUSTOM_MESSAGE"
    echo "Using provided message: $COMMIT_MESSAGE"
    
else
    # Smart commit analysis (default)
    echo "Analyzing changes for smart commit message..."
    
    # Analyze the changes
    MODIFIED_COUNT=$(git diff --cached --name-status | grep "^M" | wc -l)
    ADDED_COUNT=$(git diff --cached --name-status | grep "^A" | wc -l)
    DELETED_COUNT=$(git diff --cached --name-status | grep "^D" | wc -l)
    
    # Get the main affected component
    MAIN_COMPONENT=$(git diff --cached --name-only | head -5 | xargs -I {} dirname {} | sort | uniq -c | sort -rn | head -1 | awk '{print $2}')
    
    # Determine change type
    if [ $ADDED_COUNT -gt $MODIFIED_COUNT ]; then
        CHANGE_TYPE="feat"
        ACTION="add"
    elif [ $DELETED_COUNT -gt 0 ]; then
        CHANGE_TYPE="refactor"
        ACTION="remove"
    elif git diff --cached | grep -q "fix\|bug\|error"; then
        CHANGE_TYPE="fix"
        ACTION="fix"
    else
        CHANGE_TYPE="refactor"
        ACTION="update"
    fi
    
    # Build smart message
    if [ -n "$MAIN_COMPONENT" ] && [ "$MAIN_COMPONENT" != "." ]; then
        COMMIT_MESSAGE="$CHANGE_TYPE($MAIN_COMPONENT): $ACTION"
    else
        COMMIT_MESSAGE="$CHANGE_TYPE: $ACTION"
    fi
    
    # Add file summary
    if [ $MODIFIED_COUNT -gt 0 ]; then
        COMMIT_MESSAGE="$COMMIT_MESSAGE modified files"
    fi
    if [ $ADDED_COUNT -gt 0 ]; then
        if [ $MODIFIED_COUNT -gt 0 ]; then
            COMMIT_MESSAGE="$COMMIT_MESSAGE and"
        fi
        COMMIT_MESSAGE="$COMMIT_MESSAGE new files"
    fi
    
    echo "Generated message: $COMMIT_MESSAGE"
fi

# Perform the commit
if [ "$AMEND" = true ]; then
    echo "Amending previous commit..."
    git commit --amend -m "$COMMIT_MESSAGE"
else
    git commit -m "$COMMIT_MESSAGE"
fi

COMMIT_RESULT=$?

if [ $COMMIT_RESULT -eq 0 ]; then
    echo "✅ Commit successful!"
    
    # Show commit info
    git log -1 --oneline
    
    # Push if requested
    if [ "$DO_PUSH" = true ]; then
        echo "Pushing to remote..."
        CURRENT_BRANCH=$(git branch --show-current)
        git push origin "$CURRENT_BRANCH"
        
        if [ $? -eq 0 ]; then
            echo "✅ Pushed to origin/$CURRENT_BRANCH"
        else
            echo "❌ Push failed. You may need to set upstream or resolve conflicts."
        fi
    fi
else
    echo "❌ Commit failed!"
fi
```

---

## EXAMPLES:

### Basic smart commit:
```bash
/git
# Analyzes changes and creates intelligent commit message
```

### Quick commit all with message:
```bash
/git --all -m "Quick fixes"
# Stages everything and commits with your message
```

### End of day backup:
```bash
/git --eod
# Stages all, commits with timestamp, pushes to GitHub
```

### Commit and push:
```bash
/git --push
# Smart commit then push to remote
```

### Just check status:
```bash
/git --status
# Shows git status and diff stats without committing
```

### Combine options:
```bash
/git --all --push -m "Feature complete"
# Stage all, commit with message, and push
```

---

## REPLACES:
- commit.md (smart commit functionality)
- git-quick.md (quick operations)
- eod-commit.md (end of day functionality)

## WORKS WITH:
- git-push.md (for standalone push operations)
- undo.md (for reverting changes)