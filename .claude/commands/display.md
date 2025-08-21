# Unified Display - View Logs and Session Information

## Usage: /display [options]

### OPTIONS:
- (default) : Show today's markdown log
- `--prev` or `-p` : Show previous session summary
- `--tech` or `-t` : Show technical verification log
- `--stats` or `-s` : Show statistics only
- `--all` or `-a` : Show everything
- `--last N` : Show last N lines (for long logs)

---

## IMPLEMENTATION:

```bash
# Parse arguments
MODE="today"
LINE_LIMIT=""

for arg in "$@"; do
    case $arg in
        --prev|-p)
            MODE="previous"
            ;;
        --tech|-t)
            MODE="technical"
            ;;
        --stats|-s)
            MODE="stats"
            ;;
        --all|-a)
            MODE="all"
            ;;
        --last)
            shift
            LINE_LIMIT="$1"
            ;;
    esac
    shift
done

# Set up paths
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d)
DAILY_LOG_DIR="C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\99-claude-daily-logs"
TECH_LOG_DIR=".claude_logs"
TODAY_LOG="$DAILY_LOG_DIR\\$TODAY.md"
YESTERDAY_LOG="$DAILY_LOG_DIR\\$YESTERDAY.md"

# Function to display with optional line limit
show_file() {
    local file="$1"
    if [ -f "$file" ]; then
        if [ -n "$LINE_LIMIT" ]; then
            echo "=== Last $LINE_LIMIT lines of $(basename $file) ==="
            tail -n "$LINE_LIMIT" "$file"
        else
            echo "=== Full contents of $(basename $file) ==="
            cat "$file"
        fi
        return 0
    else
        echo "File not found: $file"
        return 1
    fi
}

# Execute based on mode
case $MODE in
    "today")
        echo "📋 TODAY'S SESSION LOG ($TODAY)"
        echo "================================"
        if show_file "$TODAY_LOG"; then
            # Show quick stats
            echo ""
            echo "📊 Quick Stats:"
            echo "- File operations: $(grep -c "**File:**" "$TODAY_LOG" 2>/dev/null || echo "0")"
            echo "- Tasks completed: $(grep -c "✅" "$TODAY_LOG" 2>/dev/null || echo "0")"
            echo "- Issues encountered: $(grep -c "⚠️\|❌" "$TODAY_LOG" 2>/dev/null || echo "0")"
        else
            echo "No log for today. Checking yesterday..."
            show_file "$YESTERDAY_LOG"
        fi
        ;;
        
    "previous")
        echo "📜 PREVIOUS SESSION SUMMARY"
        echo "==========================="
        # First try yesterday
        if [ -f "$YESTERDAY_LOG" ]; then
            echo "From: $YESTERDAY"
            # Extract key sections
            grep -A 10 "Next Session Priority" "$YESTERDAY_LOG" 2>/dev/null
            echo ""
            echo "Last 5 completed tasks:"
            grep "✅" "$YESTERDAY_LOG" 2>/dev/null | tail -5
        elif [ -f "$TODAY_LOG" ]; then
            echo "Showing earlier from today:"
            head -50 "$TODAY_LOG"
        else
            echo "No recent logs found"
        fi
        ;;
        
    "technical")
        echo "🔧 TECHNICAL VERIFICATION LOG"
        echo "============================="
        if [ -d "$TECH_LOG_DIR" ]; then
            # Find most recent technical log
            LATEST_TECH=$(ls -t "$TECH_LOG_DIR"/session_*.log 2>/dev/null | head -1)
            if [ -n "$LATEST_TECH" ]; then
                echo "Latest technical log: $(basename $LATEST_TECH)"
                echo "Size: $(wc -l < "$LATEST_TECH") lines"
                echo ""
                
                if [ -n "$LINE_LIMIT" ]; then
                    tail -n "$LINE_LIMIT" "$LATEST_TECH"
                else
                    tail -50 "$LATEST_TECH"
                fi
                
                echo ""
                echo "🔍 Technical Stats:"
                echo "- Commands executed: $(grep -c "EXECUTING:" "$LATEST_TECH" 2>/dev/null || echo "0")"
                echo "- Errors detected: $(grep -c "ERROR" "$LATEST_TECH" 2>/dev/null || echo "0")"
                echo "- Verifications: $(grep -c "VERIFY:" "$LATEST_TECH" 2>/dev/null || echo "0")"
            else
                echo "No technical logs found in $TECH_LOG_DIR"
            fi
        else
            echo "Technical log directory not found: $TECH_LOG_DIR"
            echo "Run /md to initialize technical logging"
        fi
        ;;
        
    "stats")
        echo "📈 SESSION STATISTICS"
        echo "===================="
        echo ""
        echo "Today's Activity ($TODAY):"
        if [ -f "$TODAY_LOG" ]; then
            echo "- File operations: $(grep -c "**File:**" "$TODAY_LOG" 2>/dev/null || echo "0")"
            echo "- Tasks completed: $(grep -c "✅" "$TODAY_LOG" 2>/dev/null || echo "0")"
            echo "- Issues/warnings: $(grep -c "⚠️\|❌" "$TODAY_LOG" 2>/dev/null || echo "0")"
            echo "- Log size: $(wc -l < "$TODAY_LOG") lines"
        else
            echo "- No log for today"
        fi
        
        echo ""
        echo "Recent Files Modified (last 60 min):"
        find . -type f -mmin -60 2>/dev/null | head -10
        
        echo ""
        echo "Current Session:"
        echo "- Time: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "- Directory: $(pwd)"
        echo "- Session PID: $$"
        
        if [ -d "$TECH_LOG_DIR" ]; then
            TECH_COUNT=$(ls "$TECH_LOG_DIR"/session_*.log 2>/dev/null | wc -l)
            echo "- Technical logs available: $TECH_COUNT"
        fi
        ;;
        
    "all")
        echo "📚 COMPLETE LOG DISPLAY"
        echo "======================"
        echo ""
        echo "=== TODAY'S MARKDOWN LOG ==="
        show_file "$TODAY_LOG"
        echo ""
        echo "=== TECHNICAL LOG ==="
        if [ -d "$TECH_LOG_DIR" ]; then
            LATEST_TECH=$(ls -t "$TECH_LOG_DIR"/session_*.log 2>/dev/null | head -1)
            if [ -n "$LATEST_TECH" ]; then
                tail -100 "$LATEST_TECH"
            fi
        fi
        echo ""
        echo "=== STATISTICS ==="
        /display --stats
        ;;
esac

# Final tip
echo ""
echo "💡 Tip: Use '/display --last 20' to limit output"
```

---

## EXAMPLES:

### View today's work:
```bash
/display
# Shows full markdown log for today
```

### Check what was done yesterday:
```bash
/display --prev
# Shows previous session summary and priorities
```

### View technical verification log:
```bash
/display --tech
# Shows bash commands, errors, verifications from .claude_logs
```

### Quick statistics:
```bash
/display --stats
# Just the numbers - files, tasks, errors
```

### Last 30 lines of today:
```bash
/display --last 30
# Limits output for long logs
```

### Everything:
```bash
/display --all
# Shows both markdown and technical logs plus stats
```

---

## LOG LOCATIONS:
- **Markdown logs:** `99-claude-daily-logs\YYYY-MM-DD.md`
- **Technical logs:** `.claude_logs\session_*.log`

## REPLACES:
- show99.md (today's log functionality)
- showlog.md (technical log functionality)  
- check-work.md (previous session functionality)