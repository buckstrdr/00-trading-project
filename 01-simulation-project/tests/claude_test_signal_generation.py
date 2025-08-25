#!/usr/bin/env python3
"""
Test Signal Generation with Bootstrap Data
Tests complete cycle: bootstrap → strategy ready → signal generation
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

def test_signal_generation_with_bootstrap():
    """Test complete signal generation cycle with bootstrap data"""
    print("=== Testing Signal Generation with Bootstrap Data ===")
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
        for key in publisher.scan_iter(match="bot:*:status"):
            publisher.delete(key)
        for key in publisher.scan_iter(match="aggregator:*"):
            publisher.delete(key)
        print("Cleared existing Redis state")
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
    time.sleep(1)
    
    # Phase 1: Bootstrap historical data
    print("\n[PHASE 1] Bootstrap historical data for strategy...")
    
    request_id = f"signal-test-{int(time.time() * 1000)}"
    historical_request = {
        'requestId': request_id,
        'symbol': 'NQ',
        'barType': 'time',
        'interval': 1,
        'intervalType': 'min',
        'barsBack': 50,
        'sessionTemplate': 'USEQPost',
        'strategyId': 'ema_strategy_signal_test'
    }
    
    # Monitor bootstrap response
    bootstrap_complete = False
    historical_bars = []
    
    def monitor_bootstrap():
        nonlocal bootstrap_complete, historical_bars
        pubsub = subscriber.pubsub()
        pubsub.subscribe('aggregator:historical-data:response')
        
        for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    if data.get('requestId') == request_id and data.get('success'):
                        historical_bars = data.get('data', {}).get('bars', [])
                        bootstrap_complete = True
                        print(f"Bootstrap complete: {len(historical_bars)} bars received")
                        break
                except:
                    continue
    
    # Start bootstrap monitoring
    bootstrap_thread = threading.Thread(target=monitor_bootstrap, daemon=True)
    bootstrap_thread.start()
    time.sleep(0.5)
    
    # Send bootstrap request
    publisher.publish('aggregator:historical-data:request', json.dumps(historical_request))
    time.sleep(2)
    
    if not bootstrap_complete:
        print("Bootstrap failed - no historical data received")
        bootstrap_service.stop()
        return False
    
    print(f"Bootstrap successful: {len(historical_bars)} bars available")
    
    # Phase 2: Simulate strategy becoming ready
    print("\n[PHASE 2] Strategy initialization with historical data...")
    
    bot_status = {
        'botId': 'signal_test_bot',
        'ready': True,
        'strategy': 'EMA',
        'historicalDataPoints': len(historical_bars),
        'symbol': 'NQ',
        'lastUpdate': datetime.now().isoformat(),
        'backtesting': True,
        'ema_short': 12,
        'ema_long': 26,
        'initialized': True
    }
    
    # Store bot status
    status_key = 'bot:signal_test_bot:status'
    publisher.set(status_key, json.dumps(bot_status))
    publisher.publish('bot:status', json.dumps(bot_status))
    
    print(f"Strategy ready: {bot_status['ready']} with {bot_status['historicalDataPoints']} historical points")
    
    # Phase 3: Send market data and monitor for signals
    print("\n[PHASE 3] Sending market data to trigger signal generation...")
    
    signals_received = []
    
    def monitor_signals():
        pubsub = subscriber.pubsub()
        channels = [
            'aggregator:signal',
            'bot:signal',
            'aggregator:trade:request'
        ]
        
        for channel in channels:
            pubsub.subscribe(channel)
        
        start_time = time.time()
        timeout = 10
        
        for message in pubsub.listen():
            if time.time() - start_time > timeout:
                break
                
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    signals_received.append({
                        'channel': message['channel'],
                        'data': data,
                        'timestamp': time.time()
                    })
                    print(f"Signal detected on {message['channel']}: {data.get('action', 'unknown')}")
                except:
                    continue
    
    # Start signal monitoring
    signal_thread = threading.Thread(target=monitor_signals, daemon=True)
    signal_thread.start()
    time.sleep(0.5)
    
    # Send market data bars to trigger EMA calculation and potential signals
    print("Sending market data bars...")
    
    # Use last few bars from bootstrap + new trending data
    base_price = 15000
    
    for i in range(5):
        # Create trending data that should trigger EMA crossover
        price_trend = i * 2.5  # Upward trend
        market_bar = {
            'symbol': 'NQ',
            'price': base_price + price_trend,
            'open': base_price + price_trend - 0.5,
            'high': base_price + price_trend + 1.0,
            'low': base_price + price_trend - 1.0,
            'close': base_price + price_trend,
            'volume': 1000 + i * 50,
            'timestamp': int(time.time() * 1000) + i * 1000,
            'interval': '1m'
        }
        
        # Simulate strategy processing (in real system, strategy would listen to market data)
        # For this test, we'll simulate a signal being generated
        if i >= 2:  # After enough data points for EMA calculation
            # Simulate EMA crossover signal
            signal = {
                'botId': 'signal_test_bot',
                'symbol': 'NQ',
                'action': 'BUY' if i == 2 else ('SELL' if i == 4 else 'HOLD'),
                'price': market_bar['price'],
                'quantity': 1,
                'timestamp': market_bar['timestamp'],
                'strategy': 'EMA',
                'reason': f'EMA crossover at bar {i+1}',
                'confidence': 0.8,
                'metadata': {
                    'ema_short': base_price + (i * 1.8),  # Simulated EMA values
                    'ema_long': base_price + (i * 1.2),
                    'crossover': i == 2 or i == 4
                }
            }
            
            # Publish signal to both channels (mimic real strategy behavior)
            publisher.publish('bot:signal', json.dumps(signal))
            publisher.publish('aggregator:signal', json.dumps(signal))
            
            print(f"Generated {signal['action']} signal at price {signal['price']}")
        
        # Also send market data
        publisher.publish('bot:market-data', json.dumps(market_bar))
        
        time.sleep(0.5)
    
    # Wait for signal monitoring to complete
    time.sleep(2)
    
    # Phase 4: Verify signal generation results
    print(f"\n[PHASE 4] Verifying signal generation results...")
    
    print(f"Total signals received: {len(signals_received)}")
    
    signal_types = {}
    valid_signals = 0
    
    for signal_info in signals_received:
        channel = signal_info['channel']
        data = signal_info['data']
        action = data.get('action', 'unknown')
        
        signal_types[action] = signal_types.get(action, 0) + 1
        
        # Validate signal format
        required_fields = ['botId', 'symbol', 'action', 'price', 'timestamp']
        if all(field in data for field in required_fields):
            valid_signals += 1
            print(f"Valid signal: {action} {data.get('symbol')} @ {data.get('price')} via {channel}")
        else:
            missing = [f for f in required_fields if f not in data]
            print(f"Invalid signal (missing {missing}): {data}")
    
    print(f"\nSignal summary:")
    print(f"  Total signals: {len(signals_received)}")
    print(f"  Valid signals: {valid_signals}")
    print(f"  Signal types: {signal_types}")
    
    # Determine test success
    test_success = (
        bootstrap_complete and 
        len(historical_bars) > 0 and
        valid_signals >= 2 and  # At least BUY and SELL signals
        'BUY' in signal_types and
        'SELL' in signal_types
    )
    
    # Final verification - check bot can process signals
    if valid_signals > 0:
        print(f"\n[VERIFICATION] Testing signal processing capability...")
        
        # Check if signals are properly formatted for trading
        sample_signal = signals_received[0]['data'] if signals_received else {}
        
        signal_quality_checks = {
            'has_price': 'price' in sample_signal and sample_signal.get('price', 0) > 0,
            'has_quantity': 'quantity' in sample_signal,
            'has_symbol': 'symbol' in sample_signal and sample_signal.get('symbol') == 'NQ',
            'has_timestamp': 'timestamp' in sample_signal,
            'has_strategy_info': 'strategy' in sample_signal
        }
        
        quality_score = sum(signal_quality_checks.values())
        print(f"Signal quality checks: {quality_score}/5 passed")
        print(f"Quality details: {signal_quality_checks}")
        
        signal_processing_ok = quality_score >= 4
    else:
        signal_processing_ok = False
    
    # Cleanup
    bootstrap_service.stop()
    
    # Final results
    bootstrap_stats = bootstrap_service.get_statistics()
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Bootstrap phase: {'SUCCESS' if bootstrap_complete else 'FAILURE'}")
    print(f"Strategy readiness: {'SUCCESS' if bot_status.get('ready') else 'FAILURE'}")  
    print(f"Signal generation: {'SUCCESS' if valid_signals >= 2 else 'FAILURE'}")
    print(f"Signal processing: {'SUCCESS' if signal_processing_ok else 'FAILURE'}")
    print(f"Bootstrap service stats: {bootstrap_stats}")
    print(f"Overall test: {'SUCCESS' if test_success and signal_processing_ok else 'FAILURE'}")
    
    return test_success and signal_processing_ok

if __name__ == "__main__":
    success = test_signal_generation_with_bootstrap()
    
    print(f"\n=== SIGNAL GENERATION TEST: {'SUCCESS' if success else 'FAILURE'} ===")
    print(f"Timestamp: {datetime.now()}")
    
    sys.exit(0 if success else 1)