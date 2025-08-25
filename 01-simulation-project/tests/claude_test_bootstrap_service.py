#!/usr/bin/env python3
"""
Test Historical Data Bootstrap Service
Verifies bootstrap service responds to historical data requests
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

def test_bootstrap_service():
    """Test bootstrap service request/response cycle"""
    print("=== Testing Historical Data Bootstrap Service ===")
    print(f"Time: {datetime.now()}")
    print(f"PID: {subprocess.os.getpid()}")
    
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
    
    # Give service time to initialize
    time.sleep(1)
    
    # Test 1: Send historical data request
    print("\n[TEST 1] Sending historical data request...")
    
    request_id = f"test-bootstrap-{int(time.time() * 1000)}"
    request = {
        'requestId': request_id,
        'symbol': 'NQ',
        'barType': 'time',
        'interval': 1,
        'intervalType': 'min',
        'barsBack': 50,
        'sessionTemplate': 'USEQPost'
    }
    
    print(f"Request ID: {request_id}")
    print(f"Request: {json.dumps(request, indent=2)}")
    
    # Set up response listener
    response_received = False
    response_data = None
    
    def response_listener():
        nonlocal response_received, response_data
        pubsub = subscriber.pubsub()
        pubsub.subscribe('aggregator:historical-data:response')
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    if data.get('requestId') == request_id:
                        response_received = True
                        response_data = data
                        break
                except json.JSONDecodeError:
                    continue
    
    # Start response listener
    listener_thread = threading.Thread(target=response_listener, daemon=True)
    listener_thread.start()
    
    # Give listener time to subscribe
    time.sleep(0.5)
    
    # Send request
    publisher.publish(
        'aggregator:historical-data:request',
        json.dumps(request)
    )
    print("Request sent to aggregator:historical-data:request")
    
    # Wait for response
    print("Waiting for response...")
    start_time = time.time()
    timeout = 10  # 10 second timeout
    
    while not response_received and (time.time() - start_time < timeout):
        time.sleep(0.1)
    
    # Check results
    if response_received:
        print("\n=== RESPONSE RECEIVED ===")
        print(f"Success: {response_data.get('success')}")
        print(f"Request ID match: {response_data.get('requestId') == request_id}")
        
        if response_data.get('data', {}).get('bars'):
            bars = response_data['data']['bars']
            print(f"Bars received: {len(bars)}")
            print(f"First bar: {bars[0] if bars else 'None'}")
            print(f"Last bar: {bars[-1] if bars else 'None'}")
            
            # Validate bar format
            if bars:
                first_bar = bars[0]
                required_fields = ['t', 'o', 'h', 'l', 'c', 'v']
                missing_fields = [field for field in required_fields if field not in first_bar]
                
                if missing_fields:
                    print(f"Missing fields in bar: {missing_fields}")
                    return False
                else:
                    print("Bar format validation: PASSED")
            
            test_result = True
        else:
            print("No bars in response")
            test_result = False
    else:
        print("\nNo response received within timeout")
        test_result = False
    
    # Cleanup
    bootstrap_service.stop()
    
    # Test service statistics
    stats = bootstrap_service.get_statistics()
    print(f"\nService statistics: {stats}")
    
    return test_result

if __name__ == "__main__":
    import subprocess
    
    success = test_bootstrap_service()
    
    print(f"\n=== Test Result: {'SUCCESS' if success else 'FAILURE'} ===")
    print(f"Timestamp: {datetime.now()}")
    
    sys.exit(0 if success else 1)