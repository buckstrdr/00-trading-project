#!/usr/bin/env python3
"""
Error Handling and Retry Logic Test
Tests error handling, retry mechanisms, and circuit breaker functionality
"""

import sys
import time
import unittest.mock
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from shared.retry_utils import retry_with_backoff, RetryConfig, circuit_breaker
from shared.utils import setup_logging, ServiceHealthStatus

logger = setup_logging("ErrorHandlingTest", "INFO")

def test_retry_logic():
    """Test retry logic with simulated failures"""
    logger.info("Testing retry logic...")
    
    call_count = 0
    
    @retry_with_backoff(RetryConfig(max_attempts=3, initial_delay=0.1))
    def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError(f"Simulated failure #{call_count}")
        return "Success!"
    
    try:
        result = flaky_function()
        logger.info(f"✅ Retry logic test passed: {result} after {call_count} attempts")
        return True
    except Exception as e:
        logger.error(f"❌ Retry logic test failed: {e}")
        return False

def test_circuit_breaker():
    """Test circuit breaker pattern"""
    logger.info("Testing circuit breaker...")
    
    failure_count = 0
    
    @circuit_breaker(failure_threshold=3, recovery_timeout=1.0)
    def failing_function():
        nonlocal failure_count
        failure_count += 1
        raise ConnectionError(f"Simulated failure #{failure_count}")
    
    try:
        # Test failures until circuit opens
        for i in range(5):  # Try more than threshold
            try:
                failing_function()
            except (ConnectionError, RuntimeError) as e:
                if "Circuit breaker open" in str(e):
                    logger.info(f"✅ Circuit breaker opened after {failure_count} failures")
                    return True
                    
        logger.error("❌ Circuit breaker should have opened but didn't")
        return False
        
    except Exception as e:
        logger.error(f"❌ Circuit breaker test failed: {e}")
        return False

def test_service_health_tracking():
    """Test service health status tracking"""
    logger.info("Testing service health tracking...")
    
    try:
        health = ServiceHealthStatus("TestService")
        
        # Test initial state
        assert health.is_healthy == True
        assert health.consecutive_failures == 0
        
        # Test failure recording
        health.record_failure("Connection timeout")
        health.record_failure("Redis unavailable")
        assert health.consecutive_failures == 2
        assert health.is_healthy == True  # Still healthy
        
        # Test unhealthy state
        health.record_failure("Database error")
        assert health.consecutive_failures == 3
        assert health.is_healthy == False  # Now unhealthy
        
        # Test recovery
        health.record_success()
        assert health.consecutive_failures == 0
        assert health.is_healthy == True
        
        status = health.get_status()
        assert 'service' in status
        assert 'is_healthy' in status
        
        logger.info("✅ Service health tracking test passed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Service health tracking test failed: {e}")
        return False

def test_redis_error_simulation():
    """Test Redis error handling with mocked failures"""
    logger.info("Testing Redis error handling...")
    
    try:
        from shared.redis_client import RedisClient
        
        # Create a test Redis client
        client = RedisClient()
        
        # Mock the Redis client to simulate failures
        original_publish = client.client.publish
        call_count = 0
        
        def mock_publish(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:  # Fail first 2 attempts
                raise ConnectionError("Redis connection failed")
            return original_publish(*args, **kwargs)
        
        # Apply mock
        with unittest.mock.patch.object(client.client, 'publish', side_effect=mock_publish):
            # This should succeed after retries
            result = client.publish("test:channel", {"test": "message"})
            
        if result and call_count == 3:
            logger.info(f"✅ Redis error handling test passed - succeeded after {call_count} attempts")
            return True
        else:
            logger.error(f"❌ Redis error handling test failed - call_count: {call_count}, result: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Redis error handling test failed: {e}")
        return False

def run_all_error_handling_tests():
    """Run all error handling tests"""
    logger.info("🧪 Starting Error Handling and Retry Tests")
    logger.info("=" * 50)
    
    tests = [
        ("Retry Logic", test_retry_logic),
        ("Circuit Breaker", test_circuit_breaker),
        ("Service Health Tracking", test_service_health_tracking),
        ("Redis Error Simulation", test_redis_error_simulation)
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
    
    logger.info(f"\n🏁 Error Handling Test Summary:")
    logger.info(f"Total Tests: {total_tests}")
    logger.info(f"Passed: {passed_tests}")
    logger.info(f"Failed: {total_tests - passed_tests}")
    logger.info(f"Success Rate: {success_rate:.1f}%")
    
    if success_rate == 100.0:
        logger.info("🎉 ALL ERROR HANDLING TESTS PASSED!")
    else:
        logger.error(f"❌ {total_tests - passed_tests} ERROR HANDLING TESTS FAILED")
    
    return results

if __name__ == "__main__":
    results = run_all_error_handling_tests()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    exit(0 if all_passed else 1)