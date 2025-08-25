"""
Debug Enhanced Bridge to see exactly where Node.js process fails
"""

import subprocess
import json
import time
import threading
from pathlib import Path

def debug_enhanced_bridge():
    """Debug the exact point where Node.js process fails in Enhanced Bridge"""
    
    print("=== DEBUGGING ENHANCED BRIDGE NODE.JS PROCESS ===")
    
    # Same configuration as Enhanced Bridge
    config = {
        'botId': 'debug_enhanced',
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
    print(f"Working directory: {Path.cwd()}")
    
    try:
        # Start process with EXACT same configuration as Enhanced Bridge
        import os
        env = {**os.environ, 'NODE_NO_WARNINGS': '1', 'FORCE_TTY': '1'}
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge streams like Enhanced Bridge
            text=True,
            bufsize=0,  # Unbuffered like Enhanced Bridge
            universal_newlines=True,
            encoding='utf-8',  # Handle emoji characters
            errors='replace',  # Replace problematic characters instead of crashing
            env=env
        )
        
        print(f"Process started (PID: {process.pid})")
        print(f"Reading stdout with same configuration as Enhanced Bridge...")
        print("-" * 60)
        
        # Read output exactly like Enhanced Bridge does
        start_time = time.time()
        ready_detected = False
        line_count = 0
        
        while time.time() - start_time < 10 and process.poll() is None:
            try:
                line = process.stdout.readline()
                if line:
                    # PHASE 2A FIX: Handle Unicode properly like Enhanced Bridge
                    if isinstance(line, bytes):
                        line = line.decode('utf-8', errors='replace')
                    line = line.strip()
                    if line:
                        line_count += 1
                        # Filter emojis and Unicode variation selectors for display
                        safe_line = ''.join(c for c in line if ord(c) < 127 or c.isalnum())
                        print(f"[{line_count:02d}] {safe_line}")
                        
                        # Check for ready signal using original line (same logic as Enhanced Bridge)
                        if 'ready: true' in line.lower():
                            print(f">>> READY SIGNAL DETECTED! <<<")
                            ready_detected = True
                            
            except UnicodeDecodeError as e:
                print(f"Unicode decode error, skipping line: {e}")
                continue
            except Exception as e:
                print(f"Error reading line: {e}")
                break
        
        print("-" * 60)
        print(f"Process status: {process.poll()}")
        print(f"Lines captured: {line_count}")
        print(f"Ready signal detected: {ready_detected}")
        print(f"Test duration: {time.time() - start_time:.1f} seconds")
        
        # Terminate process
        if process.poll() is None:
            print("Terminating process...")
            process.terminate()
            process.wait(timeout=5)
        
        # Get any remaining output
        try:
            stdout, stderr = process.communicate(timeout=2)
            if stdout:
                print(f"Remaining output:\n{stdout}")
        except:
            pass
        
        return ready_detected
        
    except Exception as e:
        print(f"Debug failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_enhanced_bridge()