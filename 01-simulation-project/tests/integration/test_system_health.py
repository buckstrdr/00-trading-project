#!/usr/bin/env python3
"""
System Health Monitoring Test
Tests the health monitoring functionality without encoding issues
"""

import requests
import subprocess
import sys

def test_service_health():
    """Test individual service health endpoints"""
    print("=== TESTING SERVICE HEALTH ENDPOINTS ===")
    
    services = [
        ("Data Service", "http://localhost:8001/health"),
        ("Backtest Service", "http://localhost:8002/health"),
        ("Portfolio Service", "http://localhost:8005/health")
    ]
    
    all_healthy = True
    
    for service_name, health_url in services:
        try:
            response = requests.get(health_url, timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                if health_data.get('status') == 'healthy':
                    print(f"[PASS] {service_name}: Healthy")
                    if 'details' in health_data:
                        detail_count = len(health_data['details'])
                        print(f"  Details: {detail_count} health metrics")
                else:
                    print(f"[FAIL] {service_name}: Unhealthy status")
                    all_healthy = False
            else:
                print(f"[FAIL] {service_name}: HTTP {response.status_code}")
                all_healthy = False
        except Exception as e:
            print(f"[FAIL] {service_name}: {e}")
            all_healthy = False
    
    return all_healthy

def test_redis_health():
    """Test Redis health"""
    print("\n=== TESTING REDIS HEALTH ===")
    
    try:
        result = subprocess.run(
            ["redis-cli", "ping"], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0 and "PONG" in result.stdout:
            print("[PASS] Redis: Responding to ping")
            return True
        else:
            print("[FAIL] Redis: Not responding")
            return False
    except Exception as e:
        print(f"[FAIL] Redis test error: {e}")
        return False

def test_service_communication():
    """Test basic service communication"""
    print("\n=== TESTING SERVICE COMMUNICATION ===")
    
    try:
        # Test data service
        response = requests.get("http://localhost:8001/api/data/MCL", 
                              params={'start_date': '2024-01-01', 'end_date': '2024-01-02'}, 
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            record_count = len(data.get('data', []))
            print(f"[PASS] Data Service: Retrieved {record_count} records")
            data_comm_pass = True
        else:
            print(f"[FAIL] Data Service: HTTP {response.status_code}")
            data_comm_pass = False
            
    except Exception as e:
        print(f"[FAIL] Data Service communication: {e}")
        data_comm_pass = False
    
    return data_comm_pass

def main():
    """Main health monitoring test"""
    print("SYSTEM HEALTH MONITORING TEST")
    print("=" * 50)
    
    # Run all health tests
    service_health = test_service_health()
    redis_health = test_redis_health()
    service_comm = test_service_communication()
    
    # Summary
    print("\n=== HEALTH MONITORING SUMMARY ===")
    
    tests = [
        ("Service Health Endpoints", service_health),
        ("Redis Health", redis_health), 
        ("Service Communication", service_comm)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall Health: {passed}/{total} tests passed")
    
    if passed == total:
        print("SYSTEM STATUS: ALL SYSTEMS OPERATIONAL")
        return True
    else:
        print("SYSTEM STATUS: SOME SYSTEMS HAVE ISSUES")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)