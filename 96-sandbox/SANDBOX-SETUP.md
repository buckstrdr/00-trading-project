# Windows Sandbox Setup for Claude Code YOLO Mode

## What is Windows Sandbox?
A lightweight, temporary, isolated desktop environment built into Windows 10/11 Pro and Enterprise.
When closed, everything is deleted - perfect for safe testing!

## Enable Windows Sandbox

### Step 1: Check if you have Windows Pro/Enterprise
```powershell
Get-ComputerInfo | select WindowsProductName, WindowsVersion
```

### Step 2: Enable Windows Sandbox Feature
Run PowerShell as Administrator:
```powershell
Enable-WindowsOptionalFeature -FeatureName "Containers-DisposableClientVM" -All -Online
```
Or via GUI:
1. Open "Turn Windows features on or off"
2. Check "Windows Sandbox"
3. Restart

## Create Sandbox Configuration

Save this as `claude-sandbox.wsb`:
```xml
<Configuration>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\Users\salte\ClaudeProjects\github-repos\00-trading-project</HostFolder>
      <SandboxFolder>C:\Project</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell.exe -ExecutionPolicy Bypass -Command "cd C:\Project; .\claude-code-yolo.bat"</Command>
  </LogonCommand>
  <MemoryInMB>4096</MemoryInMB>
</Configuration>
```

## Usage
1. Double-click `claude-sandbox.wsb`
2. Sandbox opens with your project mapped
3. Claude Code runs in YOLO mode
4. Close sandbox when done - everything is wiped!

## Benefits
- Zero persistence - completely fresh each time
- Full Windows environment
- No Docker overhead
- Built into Windows Pro
- Network isolated by default