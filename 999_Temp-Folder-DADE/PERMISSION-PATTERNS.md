# Claude Code Permission Patterns

## Essential Wildcard Patterns Added:

### Shell/Command Patterns:
- `Bash(*)` - ALL bash commands including chains (&&, ||, |)
- `Shell(*)` - Any shell operations
- `Cmd(*)` - Windows CMD commands
- `PowerShell(*)` - PowerShell commands
- `Python(*)` - Python with any arguments
- `Node(*)` - Node.js with any arguments
- `Git(*)` - Git with any subcommands
- `Docker(*)` - Docker operations

### Why These Matter:

#### Compound Commands:
```bash
# These all need Bash(*):
echo "test" && ls -la && pwd
cat file.txt | grep "pattern" | sort
$(command substitution) or `backticks`
command > output.txt 2>&1
```

#### Tool Variations:
```bash
# These need python*:
python script.py
python3 script.py
python -m venv
python3.11 script.py
```

#### Git Subcommands:
```bash
# These need Git(*):
git add .
git commit -m "message"
git push origin main
git log --oneline
```

## Complete Coverage List:

### Development Tools:
- All Python versions (python, python3, python3.x)
- Node ecosystem (node, npm, npx, yarn, pnpm)
- Git operations (all subcommands)
- Docker (build, run, compose)
- Compilers (gcc, g++, javac, rustc, go)
- Package managers (pip, gem, cargo, composer)

### Shell Operations:
- File operations (ls, cp, mv, rm, mkdir)
- Text processing (grep, sed, awk, sort)
- Network tools (ping, curl, wget, netstat)
- Process management (ps, kill, tasklist)
- Archives (tar, zip, unzip, 7z)

### Windows Specific:
- PowerShell cmdlets
- CMD commands
- Windows tools (tasklist, taskkill, wmic)
- Package managers (winget, choco, scoop)

### Control Flow:
- Conditionals (if, else, case)
- Loops (for, while, do)
- Functions and returns
- Error handling (try, catch)

## What This Means:

With these patterns, Claude Code should **NEVER** prompt for:
1. Any bash command chain
2. Any Python/Node/Git operation
3. Any file manipulation
4. Any development workflow command
5. Any system administration task

## Still Getting Prompts?

If you still see prompts for certain commands:

1. **Option 1:** Use the prompt option:
   "Yes, and don't ask again for [command] in this project"

2. **Option 2:** Add specific patterns:
   ```json
   "YourTool(*)",
   "your-command*"
   ```

3. **Option 3:** Nuclear option - allow EVERYTHING:
   ```json
   "*"  // Allows literally everything (use with caution!)
   ```

## Examples of What's Now Allowed:

```bash
# Complex bash chains
find . -name "*.py" -exec grep "TODO" {} \; | sort | uniq > todos.txt

# Python with any arguments
python -m pip install --upgrade pip && python script.py --verbose

# Git workflows
git stash && git pull && git stash pop && git status

# Docker operations
docker build -t myapp . && docker run -p 3000:3000 myapp

# PowerShell pipelines
Get-Process | Where-Object {$_.CPU -gt 100} | Stop-Process

# All work without prompts! 🚀
```