"""
Debug script to see what the Node.js strategy process is actually outputting
"""

import subprocess
import time
import json
from pathlib import Path

def debug_strategy_runner():
    print("=== DEBUGGING NODE.JS STRATEGY PROCESS OUTPUT ===")
    
    # Configuration
    config = {
        'botId': 'debug_bot',
        'symbol': 'MCL',
        'historicalBarsBack': 30,
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
    print(f"Strategy runner: {runner_path}")
    print(f"Strategy: {strategy_path}")
    print(f"Config: {config}")
    
    try:
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        print(f"\nProcess started (PID: {process.pid})")
        print("Watching output for 15 seconds...")
        print("-" * 80)
        
        # Monitor output for 15 seconds
        start_time = time.time()
        
        while time.time() - start_time < 15 and process.poll() is None:
            # Check stdout
            if process.stdout:
                try:
                    stdout_line = process.stdout.readline()
                    if stdout_line:
                        print(f"STDOUT: {stdout_line.strip()}")
                        
                        # Look for ready signal
                        if 'ready: true' in stdout_line.lower():
                            print(">>> READY SIGNAL DETECTED! <<<")
                            
                except Exception as e:
                    print(f"Error reading stdout: {e}")
            
            # Check stderr
            if process.stderr:
                try:
                    stderr_line = process.stderr.readline()
                    if stderr_line:
                        print(f"STDERR: {stderr_line.strip()}")
                        
                        # Look for ready signal in stderr too
                        if 'ready: true' in stderr_line.lower():
                            print(">>> READY SIGNAL DETECTED IN STDERR! <<<")
                            
                except Exception as e:
                    print(f"Error reading stderr: {e}")
            
            time.sleep(0.1)
        
        print("-" * 80)
        
        # Check if process is still running
        if process.poll() is None:
            print("Process is still running - terminating...")
            process.terminate()
            process.wait(timeout=5)
        else:
            print(f"Process exited with code: {process.returncode}")
            
            # Get any remaining output
            try:
                stdout, stderr = process.communicate(timeout=1)
                if stdout:
                    print(f"Final STDOUT:\n{stdout}")
                if stderr:
                    print(f"Final STDERR:\n{stderr}")
            except Exception as e:
                print(f"Error getting final output: {e}")
        
        print("\n=== DEBUG COMPLETE ===")
        
    except Exception as e:
        print(f"Error running debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_strategy_runner()