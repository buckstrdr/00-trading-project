#!/usr/bin/env python3
"""
Redis Pub/Sub Communication Test
Tests inter-service communication via Redis messaging
"""

import sys
import time
import json
import threading
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from shared.redis_client import redis_client
from shared.utils import setup_logging

logger = setup_logging("RedisPubSubTest", "INFO")

class RedisPubSubTester:
    """Test Redis pub/sub communication between services"""
    
    def __init__(self):
        self.messages_received = []
        self.test_results = {}
        self.pubsub = None
        
    def test_basic_pubsub(self):
        """Test basic Redis pub/sub functionality"""
        logger.info("Testing basic Redis pub/sub...")
        
        try:
            # Test 1: Basic publish/subscribe
            channel = "test:basic"
            test_message = {"test": "basic_pubsub", "timestamp": datetime.now().isoformat()}
            
            # Subscribe to channel
            self.pubsub = redis_client.pubsub()
            self.pubsub.subscribe(channel)
            
            # Skip subscription message
            for message in self.pubsub.listen():
                if message['type'] == 'subscribe':
                    break
            
            # Publish test message
            redis_client.publish(channel, json.dumps(test_message))
            
            # Listen for message with timeout
            received = False
            timeout_start = time.time()
            while time.time() - timeout_start < 5:  # 5 second timeout
                message = self.pubsub.get_message(timeout=1)
                if message and message['type'] == 'message':
                    received_data = json.loads(message['data'])
                    if received_data['test'] == 'basic_pubsub':
                        received = True
                        logger.info("✅ Basic pub/sub test passed")
                        break
            
            self.pubsub.close()
            
            if not received:
                logger.error("❌ Basic pub/sub test failed - no message received")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Basic pub/sub test failed: {e}")
            return False
    
    def test_service_communication(self):
        """Test communication between actual services"""
        logger.info("Testing service-to-service communication...")
        
        try:
            # Test backtest completion notification
            channel = "backtest:results"
            test_result = {
                'action': 'test_communication',
                'service': 'test_suite',
                'timestamp': datetime.now().isoformat(),
                'data': {'test': True}
            }
            
            # Subscribe to backtest results channel
            self.pubsub = redis_client.pubsub()
            self.pubsub.subscribe(channel)
            
            # Skip subscription message
            for message in self.pubsub.listen():
                if message['type'] == 'subscribe':
                    break
            
            # Publish test message
            redis_client.publish(channel, json.dumps(test_result))
            
            # Listen for echo with timeout
            received = False
            timeout_start = time.time()
            while time.time() - timeout_start < 5:
                message = self.pubsub.get_message(timeout=1)
                if message and message['type'] == 'message':
                    received_data = json.loads(message['data'])
                    if received_data.get('action') == 'test_communication':
                        received = True
                        logger.info("✅ Service communication test passed")
                        break
            
            self.pubsub.close()
            
            if not received:
                logger.error("❌ Service communication test failed")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"❌ Service communication test failed: {e}")
            return False
    
    def test_multiple_subscribers(self):
        """Test multiple subscribers to same channel"""
        logger.info("Testing multiple subscribers...")
        
        try:
            channel = "test:multi"
            messages_received = []
            
            def subscriber_thread(subscriber_id):
                """Subscriber thread function"""
                pubsub = redis_client.pubsub()
                pubsub.subscribe(channel)
                
                # Skip subscription message
                for message in pubsub.listen():
                    if message['type'] == 'subscribe':
                        break
                
                # Listen for test message
                timeout_start = time.time()
                while time.time() - timeout_start < 10:
                    message = pubsub.get_message(timeout=1)
                    if message and message['type'] == 'message':
                        data = json.loads(message['data'])
                        messages_received.append(f"subscriber_{subscriber_id}")
                        break
                
                pubsub.close()
            
            # Start multiple subscriber threads
            threads = []
            for i in range(3):
                thread = threading.Thread(target=subscriber_thread, args=(i,))
                thread.start()
                threads.append(thread)
            
            # Give threads time to subscribe
            time.sleep(2)
            
            # Publish test message
            test_message = {"test": "multi_subscriber", "timestamp": datetime.now().isoformat()}
            redis_client.publish(channel, json.dumps(test_message))
            
            # Wait for threads to complete
            for thread in threads:
                thread.join(timeout=10)
            
            if len(messages_received) == 3:
                logger.info("✅ Multiple subscribers test passed")
                return True
            else:
                logger.error(f"❌ Multiple subscribers test failed - only {len(messages_received)}/3 subscribers received message")
                return False
                
        except Exception as e:
            logger.error(f"❌ Multiple subscribers test failed: {e}")
            return False
    
    def test_message_persistence(self):
        """Test Redis message handling and persistence"""
        logger.info("Testing message persistence...")
        
        try:
            # Test setting and getting data from Redis
            test_key = "test:persistence"
            test_data = {
                "timestamp": datetime.now().isoformat(),
                "data": "persistence_test",
                "value": 12345
            }
            
            # Store data in Redis
            redis_client.set(test_key, json.dumps(test_data), ex=60)  # 60 second expiry
            
            # Retrieve data from Redis
            stored_data = redis_client.get(test_key)
            if stored_data:
                retrieved_data = json.loads(stored_data)
                if retrieved_data['data'] == 'persistence_test' and retrieved_data['value'] == 12345:
                    logger.info("✅ Message persistence test passed")
                    
                    # Clean up
                    redis_client.delete(test_key)
                    return True
                else:
                    logger.error("❌ Message persistence test failed - data mismatch")
                    return False
            else:
                logger.error("❌ Message persistence test failed - no data retrieved")
                return False
                
        except Exception as e:
            logger.error(f"❌ Message persistence test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all Redis pub/sub tests"""
        logger.info("🧪 Starting Redis Pub/Sub Communication Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Basic Pub/Sub", self.test_basic_pubsub),
            ("Service Communication", self.test_service_communication),
            ("Multiple Subscribers", self.test_multiple_subscribers),
            ("Message Persistence", self.test_message_persistence)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running Test: {test_name} ---")
            try:
                result = test_func()
                results[test_name] = result
                status = "PASS" if result else "FAIL"
                logger.info(f"Test {test_name}: {status}")
            except Exception as e:
                logger.error(f"Test {test_name} FAILED with exception: {e}")
                results[test_name] = False
        
        # Generate summary
        total_tests = len(tests)
        passed_tests = sum(1 for result in results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\n🏁 Redis Pub/Sub Test Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            logger.info("🎉 ALL REDIS PUB/SUB TESTS PASSED!")
        else:
            logger.error(f"❌ {total_tests - passed_tests} TESTS FAILED - Redis pub/sub communication has issues")
        
        return results

def main():
    """Main test execution"""
    tester = RedisPubSubTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())