#!/usr/bin/env python3

"""
Debug script to test TSX strategy runner directly
"""

import sys
import time
import json
import redis
import subprocess
from pathlib import Path

# Add src to path
sys.path.append('src')
sys.path.append('shared')

def test_strategy_runner():
    """Test the TSX strategy runner in isolation"""
    
    print("=== TESTING TSX STRATEGY RUNNER DIRECTLY ===")
    
    # Paths
    strategy_path = Path('../03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js').absolute()
    runner_path = Path('shared/claude_tsx_v5_strategy_runner.js').absolute()
    
    print(f"Strategy: {strategy_path}")
    print(f"Runner: {runner_path}")
    print(f"Strategy exists: {strategy_path.exists()}")
    print(f"Runner exists: {runner_path.exists()}")
    
    # Configuration
    config = {
        'botId': 'direct_test_bot',
        'symbol': 'MCL',
        'redisHost': 'localhost',
        'redisPort': 6379,
        'historicalBarsBack': 10
    }
    
    print(f"Config: {json.dumps(config, indent=2)}")
    
    # Start Redis listener to capture signals
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    pubsub = redis_client.pubsub()
    pubsub.subscribe('aggregator:signal:direct_test_bot')
    pubsub.subscribe('aggregator:strategy-ready')
    
    print("\n=== STARTING STRATEGY RUNNER ===")
    
    # Run strategy runner
    cmd = [
        'node',
        str(runner_path),
        str(strategy_path),
        json.dumps(config)
    ]
    
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0
    )
    
    print(f"Process started with PID: {process.pid}")
    
    # Monitor for 10 seconds
    start_time = time.time()
    messages_received = 0
    
    print("\n=== MONITORING FOR 10 SECONDS ===")
    
    while time.time() - start_time < 10:
        # Check for Redis messages
        message = pubsub.get_message(timeout=0.1)
        if message and message['type'] == 'message':
            messages_received += 1
            print(f"REDIS MESSAGE #{messages_received}: {message['channel']} -> {message['data']}")
        
        # Check stdout
        if process.poll() is None:
            try:
                line = process.stdout.readline()
                if line:
                    print(f"STDOUT: {line.strip()}")
            except:
                pass
        else:
            break
    
    print(f"\n=== RESULTS AFTER 10 SECONDS ===")
    print(f"Messages received: {messages_received}")
    print(f"Process running: {process.poll() is None}")
    
    # Send test market data
    print("\n=== SENDING TEST MARKET DATA ===")
    test_market_data = {
        'symbol': 'MCL',
        'price': 71.25,
        'open': 71.20,
        'high': 71.30,
        'low': 71.15,
        'volume': 1000,
        'timestamp': '2023-06-01T10:00:00.000Z'
    }
    
    redis_client.publish('aggregator:market-data:direct_test_bot', json.dumps(test_market_data))
    print(f"Sent market data: {test_market_data}")
    
    # Monitor for 5 more seconds
    print("\n=== MONITORING AFTER MARKET DATA ===")
    start_time = time.time()
    while time.time() - start_time < 5:
        message = pubsub.get_message(timeout=0.1)
        if message and message['type'] == 'message':
            messages_received += 1
            print(f"REDIS MESSAGE #{messages_received}: {message['channel']} -> {message['data']}")
        
        # Check stdout
        if process.poll() is None:
            try:
                line = process.stdout.readline()
                if line:
                    print(f"STDOUT: {line.strip()}")
            except:
                pass
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Total messages received: {messages_received}")
    
    # Cleanup
    try:
        process.terminate()
        process.wait(timeout=3)
    except:
        process.kill()
    
    pubsub.unsubscribe()
    pubsub.close()

if __name__ == "__main__":
    test_strategy_runner()