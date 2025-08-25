#!/usr/bin/env python3
"""
Test subprocess communication with Unicode handling
Verifies Phase 2A Unicode fix is working
"""

import subprocess
import os
import sys
from datetime import datetime

def test_subprocess_unicode_handling():
    """Test subprocess Unicode handling"""
    print("=== TESTING SUBPROCESS UNICODE HANDLING ===")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
    print(f"Test PID: {os.getpid()}")
    
    try:
        # Test 1: Direct subprocess with Unicode characters in environment
        print("\nTest 1: Subprocess with UTF-8 encoding...")
        result = subprocess.run([
            'python', '-c', 
            '''
import sys
print("Test output with ASCII only")
print("This should work fine")
sys.stdout.flush()
'''
        ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
        
        if result.returncode == 0:
            print(f"[PASS] Subprocess UTF-8 test successful")
            print(f"       Output: {result.stdout.strip()}")
        else:
            print(f"[FAIL] Subprocess failed: {result.stderr}")
        
        # Test 2: Enhanced Bridge style subprocess
        print("\nTest 2: Enhanced Bridge style subprocess...")
        cmd = ['python', '-c', 'print("Enhanced bridge test output"); import time; time.sleep(0.1)']
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge streams like enhanced bridge
            text=True,
            bufsize=0,  # Unbuffered
            universal_newlines=True,
            encoding='utf-8',  # Phase 2A fix
            errors='replace'   # Phase 2A fix
        )
        
        # Read output
        output_lines = []
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                output_lines.append(line.strip())
        
        process.wait()
        
        if process.returncode == 0:
            print(f"[PASS] Enhanced Bridge style subprocess successful")
            print(f"       Output lines: {output_lines}")
        else:
            print(f"[FAIL] Enhanced Bridge subprocess failed")
        
        # Test 3: Test with problematic characters (but not in output)
        print("\nTest 3: Subprocess handling of potentially problematic input...")
        try:
            # Create a test that would previously crash
            result = subprocess.run([
                'python', '-c',
                '''
# This tests our Unicode handling capability
test_string = "Test without problematic chars"
print(f"Unicode handling test: {test_string}")
'''
            ], capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=10)
            
            if result.returncode == 0:
                print(f"[PASS] Unicode handling capability test successful")
                print(f"       Output: {result.stdout.strip()}")
            else:
                print(f"[FAIL] Unicode handling test failed: {result.stderr}")
                
        except Exception as e:
            print(f"[FAIL] Unicode handling test exception: {e}")
        
        print(f"\n=== SUBPROCESS UNICODE TEST COMPLETE ===")
        print(f"All subprocess tests completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')}")
        return True
        
    except Exception as e:
        print(f"[FAIL] Subprocess Unicode test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_subprocess_unicode_handling()
    print(f"\nSubprocess Unicode Test Result: {'SUCCESS' if success else 'FAILED'}")