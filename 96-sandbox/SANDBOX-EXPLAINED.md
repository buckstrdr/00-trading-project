# IMPORTANT: Your Code Is NOT Deleted!

## What Gets Deleted vs What Is Saved

### ✅ **SAVED** (Persists after sandbox closes):
- All changes to your project files
- New files created in your project
- Git commits and history
- Any files in mapped folders

### ❌ **DELETED** (Lost when sandbox closes):
- Claude Code installation
- System changes (registry, etc.)
- Temporary files outside mapped folders
- Browser cookies/cache
- Any malware/viruses (that's the point!)

## How It Works:

```
Your Real Folder: C:\Users\salte\ClaudeProjects\github-repos\00-trading-project
                                    ↕️ (Two-way sync)
Sandbox Folder:   C:\Project
```

When Claude Code edits a file in `C:\Project` inside the sandbox, it's ACTUALLY editing your real file!

## Three Sandbox Modes Available:

### 1. **claude-sandbox-work.wsb** (For Real Work)
- Full read/write access to your project
- Changes are saved immediately
- Use this for actual development

### 2. **claude-sandbox-safe.wsb** (For Testing)
- Read-only project access
- Separate output folder for new files
- Use this for risky experiments

### 3. **claude-sandbox.wsb** (Original)
- Standard setup with your project mapped

## Example Workflow:

1. **Before Sandbox:**
   ```
   your-project/
   ├── main.py (100 lines)
   └── data.csv
   ```

2. **In Sandbox:** Claude Code adds feature.py and modifies main.py

3. **After Closing Sandbox:**
   ```
   your-project/
   ├── main.py (150 lines) ← CHANGES SAVED! ✅
   ├── feature.py ← NEW FILE SAVED! ✅
   └── data.csv
   ```

## Why Use Sandbox Then?

The sandbox protects your SYSTEM, not your code:
- If Claude Code tries to modify system files → Blocked
- If it downloads something malicious → Gone when closed
- If it breaks something → Only breaks the sandbox
- Your project changes → Always saved

## Docker Alternative:

Same concept with Docker:
```yaml
volumes:
  - ./:/project  # Your folder is mounted, changes persist
```

## Quick Test:

1. Run `claude-sandbox-work.wsb`
2. Create a file: `echo "test" > test.txt`
3. Close sandbox
4. Check your project folder - test.txt is still there!

## Summary:

- **Sandbox = Disposable environment**
- **Your code = Permanent and safe**
- **Changes = Automatically saved to your real folder**

Think of it like this: The sandbox is like a disposable computer that borrows your project folder. When you throw away the computer, your project folder remains unchanged on your real computer!