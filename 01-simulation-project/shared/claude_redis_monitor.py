"""
Monitor Redis channels to see what's actually being published
"""

import redis
import json
import time
import threading

def monitor_redis_channels():
    """Monitor Redis channels for debugging"""
    
    print("=== REDIS CHANNEL MONITOR ===")
    
    # Redis client
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Monitor channels
    channels_to_monitor = [
        'aggregator:strategy-ready',
        'aggregator:signal:simple_test',
        'aggregator:historical-data:request',
        'aggregator:historical-data:response'
    ]
    
    def monitor_channel(channel):
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel)
        
        print(f"[MONITOR] Listening on: {channel}")
        
        try:
            while True:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        print(f"[{channel}] {data}")
                    except:
                        print(f"[{channel}] {message['data']}")
        except KeyboardInterrupt:
            pass
        finally:
            pubsub.unsubscribe()
            pubsub.close()
    
    # Start monitoring threads
    threads = []
    for channel in channels_to_monitor:
        thread = threading.Thread(target=monitor_channel, args=(channel,), daemon=True)
        thread.start()
        threads.append(thread)
    
    print("Press Ctrl+C to stop monitoring...")
    
    try:
        # Monitor for 30 seconds
        time.sleep(30)
    except KeyboardInterrupt:
        pass
    
    print("Monitoring stopped")

if __name__ == "__main__":
    monitor_redis_channels()