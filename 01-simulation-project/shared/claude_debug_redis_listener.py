"""
Debug Redis listener to see all messages on strategy-ready channel
"""

import redis
import json
import threading
import time

def debug_redis_listener():
    """Listen for all Redis messages to debug the issue"""
    
    print("=== DEBUG REDIS LISTENER ===")
    
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    def listen_all_ready():
        pubsub = redis_client.pubsub()
        pubsub.subscribe('aggregator:strategy-ready')
        
        print("Listening for ALL strategy-ready messages...")
        
        try:
            while True:
                message = pubsub.get_message(timeout=1.0)
                if message and message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        print(f"[READY SIGNAL] {data}")
                    except:
                        print(f"[READY SIGNAL RAW] {message['data']}")
        except KeyboardInterrupt:
            print("Stopping listener...")
        finally:
            pubsub.unsubscribe()
            pubsub.close()
    
    # Start listener thread
    thread = threading.Thread(target=listen_all_ready, daemon=True)
    thread.start()
    
    print("Redis listener started. Will monitor for 20 seconds...")
    time.sleep(20)
    print("Debug listener finished")

if __name__ == "__main__":
    debug_redis_listener()