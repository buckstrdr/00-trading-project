#!/usr/bin/env python3
"""
Test EMA Strategy Readiness with Bootstrap Service
Verifies EMA strategy becomes ready after receiving historical data from bootstrap
"""

import sys
import json
import redis
import time
import threading
import subprocess
from datetime import datetime

# Add path for local imports
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

def test_ema_strategy_with_bootstrap():
    """Test that EMA strategy becomes ready after bootstrap service provides historical data"""
    print("=== Testing EMA Strategy Readiness with Bootstrap ==")
    print(f"Time: {datetime.now()}")
    print(f"PID: {os.getpid()}")
    
    # Create Redis clients
    publisher = redis.Redis(host='localhost', port=6379, decode_responses=True)
    subscriber = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Test Redis connection
    try:
        publisher.ping()
        subscriber.ping()
        print("Redis connections established")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return False
    
    # Start bootstrap service
    print("\nStarting bootstrap service...")
    from claude_historical_bootstrap_service import HistoricalDataBootstrapService
    
    bootstrap_service = HistoricalDataBootstrapService(publisher)
    if not bootstrap_service.start():
        print("Failed to start bootstrap service")
        return False
    
    print("Bootstrap service started successfully")
    
    # Give bootstrap service time to initialize
    time.sleep(1)
    
    # Start MockTradingBot with EMA strategy
    print("\n[TEST 1] Starting MockTradingBot with EMA strategy...")
    
    mock_bot_path = os.path.join(os.path.dirname(__file__), '..', 'shared', 'mock_trading_bot_real_redis.js')
    ema_strategy_path = "C:\\Users\\salte\\ClaudeProjects\\github-repos\\00-trading-project\\03-trading-bot\\TSX-Trading-Bot-V5\\src\\strategies\\ema\\emaStrategy.js"
    
    print(f"MockBot path: {mock_bot_path}")
    print(f"EMA strategy path: {ema_strategy_path}")
    
    # Check files exist
    if not os.path.exists(mock_bot_path):
        print(f"MockTradingBot not found at {mock_bot_path}")
        return False
    if not os.path.exists(ema_strategy_path):
        print(f"EMA strategy not found at {ema_strategy_path}")
        return False
    
    # Start MockTradingBot subprocess
    cmd = [
        'node',
        mock_bot_path,
        '--strategy', ema_strategy_path,
        '--botId', 'test_ema_bot',
        '--symbol', 'NQ',
        '--test-mode'
    ]
    
    print(f"Starting MockTradingBot: {' '.join(cmd[:3])}")
    
    try:
        bot_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("MockTradingBot started successfully")
        
    except Exception as e:
        print(f"Failed to start MockTradingBot: {e}")
        bootstrap_service.stop()
        return False
    
    # Give bot time to initialize and request historical data
    print("\nWaiting for bot initialization and historical data request...")
    time.sleep(3)
    
    # Monitor Redis traffic to verify data flow
    print("\n[TEST 2] Monitoring Redis traffic...")
    
    traffic_data = {
        'historical_requests': 0,
        'historical_responses': 0,
        'bot_ready_status': None
    }
    
    def monitor_redis_traffic():
        pubsub = subscriber.pubsub()
        channels = [
            'aggregator:historical-data:request',
            'aggregator:historical-data:response',
            'bot:status'
        ]
        
        for channel in channels:
            pubsub.subscribe(channel)
        
        start_time = time.time()
        timeout = 10  # 10 second timeout
        
        for message in pubsub.listen():
            if time.time() - start_time > timeout:
                break
                
            if message['type'] == 'message':
                channel = message['channel']
                
                if channel == 'aggregator:historical-data:request':
                    traffic_data['historical_requests'] += 1
                    print(f"Detected historical data request #{traffic_data['historical_requests']}")
                    
                elif channel == 'aggregator:historical-data:response':
                    traffic_data['historical_responses'] += 1
                    try:
                        response = json.loads(message['data'])
                        bars_count = len(response.get('data', {}).get('bars', []))
                        print(f"Detected historical data response #{traffic_data['historical_responses']} with {bars_count} bars")
                    except:
                        print(f"Detected historical data response #{traffic_data['historical_responses']}")
                        
                elif channel == 'bot:status':
                    try:
                        status = json.loads(message['data'])
                        if status.get('botId') == 'test_ema_bot':
                            traffic_data['bot_ready_status'] = status
                            print(f"Bot status update: ready={status.get('ready')}, historicalDataPoints={status.get('historicalDataPoints', 0)}")
                    except:
                        pass
    
    # Start traffic monitoring in background
    monitor_thread = threading.Thread(target=monitor_redis_traffic, daemon=True)
    monitor_thread.start()
    
    # Wait for monitoring to complete
    time.sleep(12)
    
    # Check bot status directly via Redis
    print("\n[TEST 3] Checking final bot status...")
    
    try:
        # Get bot status from Redis
        status_key = 'bot:test_ema_bot:status'
        status_data = publisher.get(status_key)
        
        if status_data:
            status = json.loads(status_data)
            print(f"Final bot status from Redis: {json.dumps(status, indent=2)}")
            
            is_ready = status.get('ready', False)
            historical_points = status.get('historicalDataPoints', 0)
            
            print(f"\nBOT READINESS VERIFICATION:")
            print(f"  Ready: {is_ready}")
            print(f"  Historical Data Points: {historical_points}")
            print(f"  Strategy: {status.get('strategy', 'Unknown')}")
            
            test_result = is_ready and historical_points > 0
            
        else:
            print("No bot status found in Redis")
            test_result = False
            
    except Exception as e:
        print(f"Error checking bot status: {e}")
        test_result = False
    
    # Cleanup
    print("\n[CLEANUP] Stopping services...")
    
    try:
        bot_process.terminate()
        time.sleep(1)
        if bot_process.poll() is None:
            bot_process.kill()
    except:
        pass
    
    bootstrap_service.stop()
    
    # Final results
    print(f"\n=== TEST RESULTS ===")
    print(f"Historical requests sent: {traffic_data['historical_requests']}")
    print(f"Historical responses received: {traffic_data['historical_responses']}")
    print(f"Data flow established: {traffic_data['historical_requests'] > 0 and traffic_data['historical_responses'] > 0}")
    
    bootstrap_stats = bootstrap_service.get_statistics()
    print(f"Bootstrap service stats: {bootstrap_stats}")
    
    return test_result

if __name__ == "__main__":
    success = test_ema_strategy_with_bootstrap()
    
    print(f"\n=== EMA STRATEGY BOOTSTRAP TEST: {'SUCCESS' if success else 'FAILURE'} ===")
    print(f"Timestamp: {datetime.now()}")
    
    sys.exit(0 if success else 1)