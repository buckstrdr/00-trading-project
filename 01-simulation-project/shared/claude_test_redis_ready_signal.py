"""
Test Redis Ready Signal Communication
Verify that the Node.js strategy runner Redis ready signal can be received by Python
"""

import redis
import json
import threading
import time
import subprocess
from pathlib import Path

def test_redis_ready_signal():
    """Test Redis ready signal end-to-end"""
    
    print("=== TESTING REDIS READY SIGNAL COMMUNICATION ===")
    
    # Redis client for listening
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Test Redis connectivity first
    try:
        redis_client.ping()
        print("[OK] Redis connection established")
    except Exception as e:
        print(f"[FAIL] Redis connection failed: {e}")
        return False
    
    # Setup ready signal listener
    ready_received = None
    ready_event = threading.Event()
    
    def listen_for_ready():
        nonlocal ready_received
        pubsub = redis_client.pubsub()
        pubsub.subscribe('aggregator:strategy-ready')
        
        print("[OK] Listening for ready signals on: aggregator:strategy-ready")
        
        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    ready_data = json.loads(message['data'])
                    print(f"[OK] Ready signal received: {ready_data}")
                    ready_received = ready_data
                    ready_event.set()
                    break
        except Exception as e:
            print(f"[ERROR] Error in ready listener: {e}")
        finally:
            pubsub.unsubscribe()
            pubsub.close()
    
    # Start listener thread
    listener_thread = threading.Thread(target=listen_for_ready, daemon=True)
    listener_thread.start()
    
    print("[OK] Ready signal listener started")
    
    # Wait a moment for listener to be ready
    time.sleep(1)
    
    # Start Node.js strategy runner
    config = {
        'botId': 'redis_ready_test',
        'symbol': 'MCL',
        'historicalBarsBack': 5,
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
    
    print(f"[OK] Starting Node.js strategy runner...")
    
    try:
        # Start the Node.js process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"[OK] Node.js process started (PID: {process.pid})")
        
        # Wait for ready signal with timeout
        print("[OK] Waiting for Redis ready signal...")
        
        if ready_event.wait(timeout=20):
            print(f"[SUCCESS] Ready signal received successfully!")
            print(f"Signal data: {ready_received}")
            
            # Verify signal content
            if (ready_received and 
                ready_received.get('botId') == config['botId'] and 
                ready_received.get('ready') == True):
                print(f"[OK] Signal validation passed")
                test_success = True
            else:
                print(f"[FAIL] Signal validation failed")
                test_success = False
                
        else:
            print(f"[FAIL] No ready signal received within timeout")
            test_success = False
        
        # Cleanup
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        
        print(f"\n" + "=" * 60)
        if test_success:
            print(f"[SUCCESS] Redis Ready Signal Communication: WORKING")
            print(f"[OK] Phase 2A Redis-based ready signaling: SUCCESSFUL")
        else:
            print(f"[ERROR] Redis Ready Signal Communication: FAILED") 
        print(f"=" * 60)
        
        return test_success
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_redis_ready_signal()