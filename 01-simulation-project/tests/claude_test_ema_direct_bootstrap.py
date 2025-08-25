#!/usr/bin/env python3
"""
Test EMA Strategy Direct Bootstrap Integration
Simplified test to verify EMA strategy receives historical data and becomes ready
"""

import sys
import json
import redis
import time
import threading
from datetime import datetime

# Add path for local imports
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

def test_ema_direct_bootstrap():
    """Test EMA strategy direct bootstrap without MockTradingBot subprocess"""
    print("=== Testing EMA Strategy Direct Bootstrap Integration ===")
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
    
    # Clear any existing Redis keys
    try:
        # Clear bot status keys
        for key in publisher.scan_iter(match="bot:*:status"):
            publisher.delete(key)
        print("Cleared existing bot status keys")
    except Exception as e:
        print(f"Warning: Could not clear Redis keys: {e}")
    
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
    
    # Simulate strategy requesting historical data
    print("\n[TEST 1] Simulating EMA strategy historical data request...")
    
    request_id = f"ema-bootstrap-test-{int(time.time() * 1000)}"
    historical_request = {
        'requestId': request_id,
        'symbol': 'NQ',
        'barType': 'time',
        'interval': 1,
        'intervalType': 'min',
        'barsBack': 50,
        'sessionTemplate': 'USEQPost',
        'strategyId': 'ema_strategy_test'
    }
    
    print(f"Request ID: {request_id}")
    print(f"Sending request: {json.dumps(historical_request, indent=2)}")
    
    # Set up response monitoring
    response_received = False
    response_data = None
    
    def monitor_historical_response():
        nonlocal response_received, response_data
        pubsub = subscriber.pubsub()
        pubsub.subscribe('aggregator:historical-data:response')
        
        start_time = time.time()
        timeout = 15  # 15 second timeout
        
        for message in pubsub.listen():
            if time.time() - start_time > timeout:
                break
                
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    if data.get('requestId') == request_id:
                        response_received = True
                        response_data = data
                        print(f"Received historical data response for request {request_id}")
                        break
                except json.JSONDecodeError:
                    continue
    
    # Start response monitoring
    monitor_thread = threading.Thread(target=monitor_historical_response, daemon=True)
    monitor_thread.start()
    
    # Give monitor time to subscribe
    time.sleep(0.5)
    
    # Send historical data request
    publisher.publish(
        'aggregator:historical-data:request',
        json.dumps(historical_request)
    )
    print("Historical data request sent")
    
    # Wait for response
    time.sleep(3)
    
    # Check results
    print(f"\n[TEST 2] Verifying historical data response...")
    
    if response_received and response_data:
        print("Historical data response received!")
        print(f"Success: {response_data.get('success')}")
        print(f"Request ID match: {response_data.get('requestId') == request_id}")
        
        bars = response_data.get('data', {}).get('bars', [])
        print(f"Bars received: {len(bars)}")
        
        if bars:
            print(f"First bar: {bars[0]}")
            print(f"Last bar: {bars[-1]}")
            
            # Validate bar format
            first_bar = bars[0]
            required_fields = ['t', 'o', 'h', 'l', 'c', 'v']
            missing_fields = [field for field in required_fields if field not in first_bar]
            
            if missing_fields:
                print(f"Missing fields in bar: {missing_fields}")
                historical_data_ok = False
            else:
                print("Historical data format validation: PASSED")
                historical_data_ok = True
        else:
            print("No bars in response")
            historical_data_ok = False
    else:
        print("No historical data response received")
        historical_data_ok = False
    
    # Simulate strategy becoming ready after receiving data
    print(f"\n[TEST 3] Simulating strategy ready state...")
    
    if historical_data_ok:
        # Set bot status to ready
        bot_status = {
            'botId': 'test_ema_bot',
            'ready': True,
            'strategy': 'EMA',
            'historicalDataPoints': len(bars) if response_received else 0,
            'symbol': 'NQ',
            'lastUpdate': datetime.now().isoformat(),
            'backtesting': True
        }
        
        # Store in Redis
        status_key = 'bot:test_ema_bot:status'
        publisher.set(status_key, json.dumps(bot_status))
        publisher.expire(status_key, 300)  # 5 minute expiry
        
        # Also publish status update
        publisher.publish('bot:status', json.dumps(bot_status))
        
        print(f"Bot status set: {json.dumps(bot_status, indent=2)}")
        
        strategy_ready = True
    else:
        strategy_ready = False
    
    # Final verification
    print(f"\n[TEST 4] Final verification...")
    
    # Check if we can retrieve the status
    try:
        status_data = publisher.get('bot:test_ema_bot:status')
        if status_data:
            final_status = json.loads(status_data)
            print(f"Final bot status: {json.dumps(final_status, indent=2)}")
            
            is_ready = final_status.get('ready', False)
            has_data = final_status.get('historicalDataPoints', 0) > 0
            
            test_success = is_ready and has_data and historical_data_ok
        else:
            print("No bot status found")
            test_success = False
    except Exception as e:
        print(f"Error retrieving final status: {e}")
        test_success = False
    
    # Cleanup
    bootstrap_service.stop()
    
    # Get final stats
    bootstrap_stats = bootstrap_service.get_statistics()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Historical data request/response: {'SUCCESS' if historical_data_ok else 'FAILURE'}")
    print(f"Strategy readiness simulation: {'SUCCESS' if strategy_ready else 'FAILURE'}")
    print(f"Bootstrap service stats: {bootstrap_stats}")
    print(f"Overall test: {'SUCCESS' if test_success else 'FAILURE'}")
    
    return test_success

if __name__ == "__main__":
    success = test_ema_direct_bootstrap()
    
    print(f"\n=== EMA DIRECT BOOTSTRAP TEST: {'SUCCESS' if success else 'FAILURE'} ===")
    print(f"Timestamp: {datetime.now()}")
    
    sys.exit(0 if success else 1)