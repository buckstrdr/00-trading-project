"""
Test subprocess execution directly to isolate the issue
"""

import subprocess
import json
import time
from pathlib import Path

def test_subprocess():
    print("=== TESTING SUBPROCESS EXECUTION ===")
    
    # Configuration
    config = {
        'botId': 'test_subprocess',
        'symbol': 'MCL',
        'historicalBarsBack': 10,
        'redisHost': 'localhost',
        'redisPort': 6379
    }
    
    strategy_path = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
    runner_path = Path(__file__).parent / 'claude_tsx_v5_strategy_runner.js'
    
    cmd = [
        'node',
        str(runner_path),
        str(strategy_path),
        json.dumps(config)
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print(f"Runner exists: {runner_path.exists()}")
    print(f"Strategy exists: {Path(strategy_path).exists()}")
    
    try:
        print("\nStarting process...")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"Process started (PID: {process.pid})")
        
        # Read output for 10 seconds
        start_time = time.time()
        found_ready = False
        
        while time.time() - start_time < 10:
            # Check if process is still running
            if process.poll() is not None:
                print(f"Process exited with code: {process.returncode}")
                break
            
            # Try to read stdout (non-blocking)
            try:
                # Read available stdout
                import select
                import sys
                
                if sys.platform == 'win32':
                    # Windows doesn't support select on pipes, just try readline with short timeout
                    line = process.stdout.readline()
                    if line:
                        line = line.strip()
                        print(f"STDOUT: {line}")
                        
                        if 'ready: true' in line.lower():
                            print(">>> FOUND READY SIGNAL! <<<")
                            found_ready = True
                            break
                
                # Check stderr too
                stderr_line = process.stderr.readline()
                if stderr_line:
                    stderr_line = stderr_line.strip()
                    print(f"STDERR: {stderr_line}")
                    
            except Exception as e:
                print(f"Error reading output: {e}")
            
            time.sleep(0.1)
        
        # Terminate process
        if process.poll() is None:
            print("Terminating process...")
            process.terminate()
            process.wait(timeout=3)
        
        # Get any remaining output
        try:
            stdout, stderr = process.communicate(timeout=2)
            if stdout:
                print(f"Remaining STDOUT:\n{stdout}")
            if stderr:
                print(f"Remaining STDERR:\n{stderr}")
        except Exception as e:
            print(f"Error getting final output: {e}")
        
        print(f"\nResult: Ready signal found = {found_ready}")
        return found_ready
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_subprocess()