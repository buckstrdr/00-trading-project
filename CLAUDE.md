Claude Code Project Instructions
MANDATORY: Read This First
This file contains MANDATORY verification protocols. You MUST follow these instructions for EVERY action in this project. These are not suggestions - they are requirements.
Core Principles

NEVER simulate or pretend to execute commands - Every command must be actually run
NEVER claim completion without proof - Every task requires verification
NEVER generate fake output - All output must come from real execution
NEVER skip verification steps - Each phase has mandatory checks

Anti-Pretending Verification Protocol
Session Initialization (RUN IMMEDIATELY)
bash# Start every session with these commands:
echo "=== SESSION START: $(date '+%Y-%m-%d %H:%M:%S.%N') ==="
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Session ID: $$"
echo "Random verification: $RANDOM"
ls -la
Continuous Verification Requirements
After EVERY Command:
bashecho "✓ Executed at $(date '+%H:%M:%S.%N') | Exit code: $?"
For EVERY File Operation:
bash# After creating/modifying any file:
ls -la [filename]
wc -l [filename]
head -5 [filename]
tail -5 [filename]
md5sum [filename]
For EVERY Process/Server Start:
bash# Don't just say it's running, PROVE it:
ps aux | grep [process]
lsof -i:[port]
curl -v http://localhost:[port]
netstat -an | grep [port]
Phase Completion Protocol
MANDATORY Phase Verification Checklist
Before declaring ANY phase complete, you MUST complete ALL items:
Phase [X] Verification Checklist
1. CODE VERIFICATION
bash# Show all created/modified files
find . -type f -mmin -30 -ls

# Display full content of main files
cat [main_file]

# Verify no TODOs remain
grep -r "TODO\|FIXME\|XXX" .

# Check syntax (language-specific)
python -m py_compile *.py  # For Python
node --check *.js          # For JavaScript
2. EXECUTION VERIFICATION
bash# Create execution log
script execution_log_phase_[X].txt

# Run the actual code
[execution command]

# Exit logging
exit

# Show the log
cat execution_log_phase_[X].txt

# Verify success
echo "Final exit code: $?"
3. TEST VERIFICATION
bash# Create test execution log
script test_log_phase_[X].txt

# Run ALL tests with verbose output
pytest -v --tb=short  # Python
npm test -- --verbose  # JavaScript
[appropriate test command]

# Exit logging
exit

# Display results
cat test_log_phase_[X].txt

# Summary
echo "Test completion time: $(date)"
4. INTEGRATION VERIFICATION
bash# Test with previous phases
[run integration tests]

# Verify entire application
[run full application]

# Check all services
ps aux | grep -E "(python|node|java)"
Phase Completion Report Template
markdown## Phase [X] Completion Report - $(date)

### Files Created/Modified
[List with timestamps and line counts from ls -la]

### Execution Proof
[PASTE ACTUAL execution_log_phase_X.txt CONTENT]

### Test Results
[PASTE ACTUAL test_log_phase_X.txt CONTENT]

### Integration Status
- Previous features tested: [YES/NO with proof]
- New feature integrated: [YES/NO with proof]
- Full application working: [YES/NO with proof]

### Verification Signature
Session ID: [$$]
Timestamp: [$(date '+%Y-%m-%d %H:%M:%S.%N')]
Random: [$RANDOM]
Proof-of-Work Commands
Use These Commands Frequently (Hard to Fake):
bash# Timestamp proof
date '+%Y-%m-%d %H:%M:%S.%N'

# Random verification
echo $RANDOM
head -c 20 /dev/urandom | base64

# System state
df -h
free -m
uptime

# Process verification
ps aux | head -10
echo $$

# Recent activity
history | tail -20
find . -mmin -5 -type f

# Network state (for servers)
ss -tlnp
netstat -tulpn
Error Handling Requirements
You MUST Show Failures:
bash# If a command fails, SHOW IT:
command_that_might_fail 2>&1 | tee error.log
if [ $? -ne 0 ]; then
    echo "ERROR DETECTED - Showing full output:"
    cat error.log
    echo "Attempting to fix..."
    # [fix attempts]
fi
Forbidden Behaviors
❌ NEVER DO THESE:

NEVER generate output like:
Server running successfully...
All tests passed.
Feature implemented correctly.
Without showing ACTUAL terminal output
NEVER claim without proof:

"I've tested this"
"It's working"
"Implementation complete"


NEVER skip to next phase if:

Tests are failing
Errors are present
Verification incomplete


NEVER simulate terminal output

All output must be from real execution
Use script command to capture sessions
Include timestamps and exit codes



Verification Enforcement
Random Verification Checks
At any point, I may ask you to run:
bash# Proof of real execution
echo "VERIFY: $RANDOM at $(date +%s%N)"
history | tail -10
ps aux | grep $$
ls -la --full-time
You must be able to execute these immediately.
Failure Test
I may ask you to deliberately fail:
bashls /nonexistent/path 2>&1
echo "Error code was: $?"
You MUST show the actual error.
Project-Specific Requirements
For Web Development:

Always use curl -v to test endpoints
Show browser screenshots or curl output
Run lighthouse or performance tests

For API Development:

Test every endpoint with curl
Show request and response headers
Verify status codes

For Database Projects:

Show table structures
Count records after operations
Display sample data

Session Termination
Before Ending Any Session:
bashecho "=== SESSION SUMMARY ==="
echo "End time: $(date '+%Y-%m-%d %H:%M:%S')"
echo "Files created/modified:"
find . -type f -mmin -60 -ls
echo "Processes still running:"
ps aux | grep -E "(python|node|java)"
echo "Final directory state:"
ls -la
echo "Command history:"
history | tail -50
echo "=== END OF SESSION ==="
Sequential Thinking Integration
When using sequential-thinking MCP:

Plan verification steps
Execute each step with proof
Verify results before proceeding
Document actual outcomes
Only proceed if verification passes

Code Standards and Cleanliness Requirements
Language-Specific Standards
For ALL Languages (Python, Node.js, PineScript):

NO EMOJIS in code, comments, or commit messages
Use clear, professional variable names
Maintain consistent indentation
Remove all console.log/print statements used for debugging before completion

Python Standards:

Follow PEP 8 naming conventions
Use snake_case for variables and functions
Use UPPER_CASE for constants
Docstrings for all functions and classes

Node.js Standards:

Use camelCase for variables and functions
Use PascalCase for classes and constructors
Use UPPER_CASE for constants
JSDoc comments for all functions

PineScript Standards:

Follow TradingView's style guide
Use camelCase for variables
Clear indicator/strategy descriptions
Comment complex logic

File Naming and Organization
CRITICAL: Distinguish Between Permanent Project Files and Claude's Temporary Work Files

File Categories and Naming Conventions:
1. PERMANENT TEST FILES (Part of the project - DO NOT DELETE):
bash# Official test suite files that stay with the project:
tests/test_*.py           # Python unit tests
tests/*.test.js          # JavaScript test files
tests/*.spec.js          # JavaScript spec files
src/**/__tests__/        # Component test directories

2. CLAUDE'S TEMPORARY FILES (SAFE TO DELETE - All prefixed with 'claude_'):
bash# ALL temporary files created by Claude MUST start with 'claude_':
claude_temp_*.py         # Temporary Python scripts
claude_test_*.js         # Quick test files
claude_debug_*.txt       # Debug output
claude_output_*.json     # Temporary data files
claude_example_*.py      # Example implementations
claude_verify_*.sh       # Verification scripts
claude_check_*.js        # Quick check scripts

3. DEBUG FILES (Created during Claude's work - SAFE TO DELETE):
bash# Debug and log files from Claude's testing:
claude_log_*.txt         # Log files
claude_trace_*.log       # Trace logs
claude_error_*.txt       # Error captures
claude_session_*.log     # Session logs

4. PRODUCTION CODE (NEVER prefixed with 'claude_'):
bash# Real project files - NO PREFIX:
src/user_auth.py         # Production code
src/database.js          # Production code
src/api_handler.py       # Production code

Example Naming:
✅ CORRECT Claude temporary files:
claude_temp_api_test.py
claude_debug_output.txt
claude_test_connection.js
claude_verify_phase1.sh

✅ CORRECT permanent project files:
tests/test_user_auth.py    # Permanent test
src/user_auth.py           # Production code
config/settings.json       # Production config

❌ WRONG (ambiguous):
temp_test.py              # Is this Claude's or permanent?
debug.txt                 # Who created this?
test_something.js         # Permanent or temporary?
Cleanup Verification Commands:
bash# ESSENTIAL: Show all Claude's temporary files for bulk removal:
echo "=== CLAUDE'S TEMPORARY FILES (Safe to delete) ==="
find . -type f -name "claude_*" -ls
echo "Total Claude files: $(find . -name "claude_*" -type f | wc -l)"

# Show permanent test files (DO NOT DELETE):
echo "=== PERMANENT TEST FILES (Keep these) ==="
find tests/ -type f \( -name "*.test.js" -o -name "test_*.py" -o -name "*.spec.js" \) -ls

# CLEANUP COMMANDS:
# Remove ALL Claude's temporary work (SAFE):
find . -type f -name "claude_*" -exec rm -v {} \;

# Clean specific Claude file types:
find . -type f -name "claude_temp_*" -exec rm -v {} \;   # Remove temp files
find . -type f -name "claude_debug_*" -exec rm -v {} \;  # Remove debug files
find . -type f -name "claude_log_*" -exec rm -v {} \;    # Remove log files

# Verify cleanup:
echo "Remaining Claude files: $(find . -name "claude_*" -type f | wc -l)"
if [ $(find . -name "claude_*" -type f | wc -l) -eq 0 ]; then
    echo "✓ All Claude temporary files removed"
else
    echo "⚠ Some Claude files remain:"
    find . -name "claude_*" -type f
fi
Directory Structure Requirements:
bashproject/
├── src/              # Main source code (NO claude_ prefix)
├── tests/            # Permanent test suite (NO claude_ prefix)
├── temp/             # General temporary files
├── claude_work/      # All Claude's temporary work
├── docs/             # Documentation
└── scripts/          # Utility scripts

# Create structure:
mkdir -p src tests temp claude_work docs scripts

# MANDATORY: Add Claude files to .gitignore:
echo "# Claude's temporary work files" >> .gitignore
echo "claude_*" >> .gitignore
echo "claude_work/" >> .gitignore
echo "*.claude_temp.*" >> .gitignore
echo "*.claude_debug.*" >> .gitignore

MANDATORY Claude File Creation Rules:
When I create ANY file for testing, debugging, or verification:
bash# BEFORE creating any temporary file:
filename="claude_temp_${purpose}_$(date +%s).${ext}"
echo "Creating Claude temporary file: $filename"

# Examples of MANDATORY naming:
# Instead of: test.py
# Use: claude_temp_test_1698765432.py

# Instead of: output.txt  
# Use: claude_debug_output_1698765432.txt

# Instead of: verify.js
# Use: claude_verify_feature_1698765432.js

Claude's Pre-Cleanup Check (Run before delivering to user):
bash# MANDATORY before phase completion:
echo "=== CLAUDE FILE AUDIT ==="
echo "Claude temporary files that need cleanup decision:"
find . -name "claude_*" -type f -exec ls -lh {} \;
echo ""
echo "To remove all Claude files, run:"
echo "find . -type f -name 'claude_*' -exec rm -v {} \;"
echo ""
echo "Production files (keeping):"
find src/ tests/ -type f ! -name "claude_*" | head -20
Code Quality Checks Before Phase Completion:
bash# Check for debugging artifacts in PRODUCTION code only:
grep -r "console\.log\|print\(" src/ --exclude="claude_*" | grep -v "test"

# Check for TODOs in production code:
grep -r "TODO\|FIXME\|HACK\|XXX" src/ tests/ --exclude="claude_*"

# Check for emojis in code files:
grep -rP "[\x{1F300}-\x{1F9FF}]" --include="*.py" --include="*.js" --include="*.pine" --exclude="claude_*" .

# List all Claude temporary files for review:
echo "=== Claude temporary files to be removed: ==="
find . -name "claude_*" -type f -exec echo "  - {}" \;

# Verify production files have no 'claude_' prefix:
echo "=== Checking for misnamed production files: ==="
find src/ tests/ -name "claude_*" -type f
if [ $? -eq 0 ]; then
    echo "WARNING: Found claude_ files in production directories!"
fi

# Summary report:
echo "=== File Summary ==="
echo "Production files: $(find src/ -type f ! -name 'claude_*' | wc -l)"
echo "Permanent tests: $(find tests/ -type f ! -name 'claude_*' | wc -l)"  
echo "Claude temp files: $(find . -name 'claude_*' -type f | wc -l)"

Final Warning
This is a VERIFICATION PROTOCOL, not a suggestion. The user is a beginner who cannot debug issues. You MUST:

Execute real commands
Show real output
Capture real errors
Provide real proof

Every claim requires evidence. Every phase requires verification. Every command requires execution.
Remember: The user is paying for REAL, WORKING, TESTED code - not explanations or simulations.

This claude.md file must be respected throughout the entire project session.

LOCAL DOCUMENTATION REFERENCE - MANDATORY
CRITICAL: Local API and Framework Documentation
The project contains comprehensive local documentation that MUST be referenced for all coding tasks:

Location: ./97-Local-documentation/

Available Documentation (ALWAYS consult these BEFORE coding):
1. 01-javascript/javascript-complete-documentation.md - JavaScript ES6+, async/await, promises
2. 02-nodejs/nodejs-complete-documentation.md - Node.js runtime, modules, streams
3. 03-express/express-complete-documentation.md - Express.js web framework
4. 04-socketio/socketio-complete-documentation.md - Socket.io real-time communication
5. 05-redis/redis-complete-documentation.md - Redis database and caching
6. 06-winston/winston-complete-documentation.md - Winston logging framework
7. 07-jest/jest-complete-documentation.md - Jest testing framework
8. 08-playwright/playwright-complete-documentation.md - Playwright browser automation
9. 09-python/python-complete-documentation.md - Python core language features
10. 10-fastapi/fastapi-complete-documentation.md - FastAPI web framework
11. 11-pandas/pandas-complete-documentation.md - Pandas data manipulation
12. 12-numpy/numpy-complete-documentation.md - NumPy numerical computing
13. 13-scikit-learn/scikit-learn-complete-documentation.md - Scikit-learn machine learning
14. 14-streamlit/streamlit-complete-documentation.md - Streamlit app development
15. 15-pybroker/pybroker-complete-documentation.md - PyBroker algorithmic trading
16. 16-tsx-gateway-api/tsx-gateway-api-comprehensive.md - TSX/TopStepX/ProjectX Gateway API

MANDATORY Usage Rules:
1. BEFORE writing ANY code, check if relevant documentation exists in 97-Local-documentation
2. Use the @read-docs command to load relevant documentation (e.g., @read-docs fastapi)
3. Use the EXACT syntax and patterns shown in the documentation
4. Follow the code examples and best practices from the documentation
5. Reference the documentation when explaining code to the user
6. If documentation exists for a framework/library, NEVER guess - ALWAYS check the docs

Quick Documentation Access:
Use the @read-docs command for instant documentation access:
- @read-docs <topic> - Load specific documentation
- @read-docs all - List all available documentation
Examples: @read-docs pandas, @read-docs tsx-api, @read-docs express

Documentation Verification Commands:
bash# List all available documentation
echo "=== AVAILABLE LOCAL DOCUMENTATION ==="
ls -la ./97-Local-documentation/*/
find ./97-Local-documentation -name "*.md" -type f -exec echo "  - {}" \;

# Check specific documentation exists before coding
DOC_TOPIC="fastapi"  # Change to relevant topic
if [ -d "./97-Local-documentation/*${DOC_TOPIC}*" ]; then
    echo "Documentation found for ${DOC_TOPIC}"
    ls -la ./97-Local-documentation/*${DOC_TOPIC}*/*.md
else
    echo "No local documentation for ${DOC_TOPIC} - check online resources"
fi

# Quick reference lookup
grep -r "specific_function_or_concept" ./97-Local-documentation/ --include="*.md"

When Starting ANY Coding Task:
1. Identify the frameworks/libraries involved
2. Check 97-Local-documentation for relevant docs
3. Read the documentation BEFORE writing code
4. Use examples from the documentation as templates
5. Verify your code matches documentation patterns

Example Usage:
bashecho "Task: Create a FastAPI endpoint"
echo "Step 1: Checking local documentation..."
cat ./97-Local-documentation/10-fastapi/fastapi-complete-documentation.md | grep -A 20 "POST endpoint"
echo "Step 2: Using documentation example as template..."
# Then write code based on the documentation

This local documentation is MORE AUTHORITATIVE than general knowledge. Always prefer local documentation over memory or assumptions.