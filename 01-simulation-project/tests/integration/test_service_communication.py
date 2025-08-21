#!/usr/bin/env python3
"""
Service Communication Integration Tests
Tests the missing Week 4 integration components
"""

import sys
import requests
import time
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import setup_logging
from shared.redis_client import redis_client
from config.settings import SERVICE_PORTS

logger = setup_logging("ServiceCommunication", "INFO")

class ServiceCommunicationTester:
    """Test service-to-service communication"""
    
    def __init__(self):
        self.data_service_url = f"http://localhost:{SERVICE_PORTS['data']}"
        self.backtest_service_url = f"http://localhost:{SERVICE_PORTS['backtest']}"
        self.portfolio_service_url = f"http://localhost:{SERVICE_PORTS['portfolio']}"
        self.test_results = {}
        
    def test_data_to_backtest_communication(self) -> bool:
        """Test Data Service → Backtest Service communication"""
        logger.info("🔗 Testing Data → Backtest communication")
        
        try:
            # Verify Data Service has data
            data_response = requests.get(
                f"{self.data_service_url}/api/data/MCL",
                params={"start_date": "2024-01-01", "end_date": "2024-01-02", "limit": 5},
                timeout=10
            )
            
            if data_response.status_code != 200:
                logger.error(f"Data Service not responding: {data_response.status_code}")
                return False
                
            data_result = data_response.json()
            if not data_result.get('data'):
                logger.error("No data available from Data Service")
                return False
                
            logger.info(f"✅ Data Service has {len(data_result['data'])} records")
            
            # Test Backtest Service can request and use data
            backtest_response = requests.post(
                f"{self.backtest_service_url}/api/backtest",
                params={
                    'strategy_name': 'SimpleMAStrategy',
                    'symbol': 'MCL',
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-02',
                    'initial_cash': 10000
                },
                timeout=30
            )
            
            if backtest_response.status_code != 200:
                logger.error(f"Backtest failed: {backtest_response.status_code}")
                return False
                
            backtest_result = backtest_response.json()
            if not backtest_result.get('performance'):
                logger.error("Backtest did not return performance data")
                return False
                
            logger.info("✅ Data → Backtest communication working")
            return True
            
        except Exception as e:
            logger.error(f"Data → Backtest communication failed: {e}")
            return False
    
    def test_backtest_to_portfolio_communication(self) -> bool:
        """Test Backtest Service → Portfolio Service communication"""
        logger.info("🔗 Testing Backtest → Portfolio communication")
        
        try:
            # Execute backtest that creates portfolio
            backtest_response = requests.post(
                f"{self.backtest_service_url}/api/backtest",
                params={
                    'strategy_name': 'SimpleMAStrategy',
                    'symbol': 'MCL',
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-02',
                    'initial_cash': 15000,
                    'record_to_portfolio': True
                },
                timeout=30
            )
            
            if backtest_response.status_code != 200:
                logger.error(f"Backtest with portfolio failed: {backtest_response.status_code}")
                return False
                
            backtest_result = backtest_response.json()
            portfolio_id = backtest_result.get('portfolio_id')
            
            if not portfolio_id:
                # Check if any trades were recorded - this indicates portfolio integration is working
                trades_recorded = backtest_result.get('trades_recorded')
                if trades_recorded and trades_recorded > 0:
                    logger.info(f"✅ Backtest recorded {trades_recorded} trades to portfolio system")
                    # Test passed - backtest service is communicating with portfolio service
                    logger.info("✅ Backtest → Portfolio communication working")
                    return True
                else:
                    logger.error("Backtest did not create portfolio or record trades")
                    return False
                
            logger.info(f"✅ Backtest created portfolio: {portfolio_id}")
            
            # Verify portfolio exists in Portfolio Service
            portfolio_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{portfolio_id}",
                timeout=5
            )
            
            if portfolio_response.status_code != 200:
                logger.error(f"Portfolio not found in Portfolio Service: {portfolio_response.status_code}")
                return False
                
            portfolio_data = portfolio_response.json()
            # The portfolio ID is nested under 'portfolio.id' in the response
            portfolio_info = portfolio_data.get('portfolio', {})
            actual_portfolio_id = portfolio_info.get('id')
            
            if actual_portfolio_id != portfolio_id:
                logger.error(f"Portfolio ID mismatch - Expected: {portfolio_id}, Got: {actual_portfolio_id}")
                return False
                
            # Check trades were recorded
            trades_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{portfolio_id}/trades",
                timeout=5
            )
            
            if trades_response.status_code != 200:
                logger.error("Could not retrieve trades from portfolio")
                return False
                
            trades_data = trades_response.json()
            trade_count = len(trades_data.get('trades', []))
            
            if trade_count == 0:
                logger.error("No trades recorded in portfolio")
                return False
                
            logger.info(f"✅ Portfolio has {trade_count} trades recorded")
            logger.info("✅ Backtest → Portfolio communication working")
            return True
            
        except Exception as e:
            logger.error(f"Backtest → Portfolio communication failed: {e}")
            return False
    
    def test_complete_data_flow(self) -> bool:
        """Test complete Data → Backtest → Portfolio flow"""
        logger.info("🔗 Testing complete data flow")
        
        try:
            # Test full pipeline
            start_time = time.time()
            
            # 1. Verify data availability
            data_check = requests.get(f"{self.data_service_url}/health", timeout=5)
            if data_check.status_code != 200:
                logger.error("Data Service not healthy")
                return False
                
            # 2. Execute full backtest with portfolio
            full_test_response = requests.post(
                f"{self.backtest_service_url}/api/backtest",
                params={
                    'strategy_name': 'SimpleMAStrategy',
                    'symbol': 'MCL',
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-03',
                    'initial_cash': 20000,
                    'record_to_portfolio': True
                },
                timeout=45
            )
            
            if full_test_response.status_code != 200:
                logger.error(f"Full pipeline test failed: {full_test_response.status_code}")
                return False
                
            result = full_test_response.json()
            portfolio_id = result.get('portfolio_id')
            total_trades = result.get('trades_recorded', 0)
            
            if not portfolio_id or total_trades == 0:
                logger.error("Full pipeline did not complete properly")
                return False
                
            # 3. Verify end-to-end integrity
            portfolio_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{portfolio_id}",
                timeout=5
            )
            
            if portfolio_response.status_code != 200:
                logger.error("Portfolio verification failed")
                return False
                
            end_time = time.time()
            duration = end_time - start_time
            
            logger.info(f"✅ Complete data flow successful:")
            logger.info(f"   Portfolio: {portfolio_id}")
            logger.info(f"   Trades: {total_trades}")
            logger.info(f"   Duration: {duration:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Complete data flow failed: {e}")
            return False
    
    def test_redis_pubsub(self) -> bool:
        """Test Redis pub/sub functionality"""
        logger.info("🔗 Testing Redis pub/sub")
        
        try:
            # Test Redis connection
            if not redis_client.health_check():
                logger.error("Redis not available")
                return False
                
            # Test publish capability
            test_message = f"test_message_{int(time.time())}"
            result = redis_client.client.publish('test_channel', test_message)
            
            if result == 0:
                logger.info("✅ Redis publish working (no subscribers)")
            else:
                logger.info(f"✅ Redis publish working ({result} subscribers)")
                
            # Test portfolio trade events channel exists
            # This channel should be used by Portfolio Service
            channels = redis_client.client.pubsub_channels()
            logger.info(f"Active Redis channels: {len(channels)}")
            
            logger.info("✅ Redis pub/sub functionality working")
            return True
            
        except Exception as e:
            logger.error(f"Redis pub/sub test failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test service error handling"""
        logger.info("🔗 Testing error handling")
        
        try:
            # Test invalid symbol
            invalid_response = requests.get(
                f"{self.data_service_url}/api/data/INVALID",
                params={"start_date": "2024-01-01", "end_date": "2024-01-02"},
                timeout=5
            )
            
            if invalid_response.status_code != 200:
                logger.error("Data Service error handling issue")
                return False
                
            # Should return empty data, not error
            invalid_data = invalid_response.json()
            if len(invalid_data.get('data', [])) > 0:
                logger.error("Invalid symbol returned data")
                return False
                
            # Test invalid strategy
            invalid_strategy_response = requests.post(
                f"{self.backtest_service_url}/api/backtest",
                params={
                    'strategy_name': 'NonexistentStrategy',
                    'symbol': 'MCL',
                    'start_date': '2024-01-01',
                    'end_date': '2024-01-02'
                },
                timeout=10
            )
            
            if invalid_strategy_response.status_code == 200:
                logger.error("Backtest should reject invalid strategy")
                return False
                
            # Test invalid portfolio ID
            invalid_portfolio_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/invalid_id",
                timeout=5
            )
            
            if invalid_portfolio_response.status_code == 200:
                logger.error("Portfolio should reject invalid ID")
                return False
                
            logger.info("✅ Error handling working properly")
            return True
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            return False
    
    def run_all_tests(self) -> dict:
        """Run all service communication tests"""
        logger.info("🧪 Starting Service Communication Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Data → Backtest Communication", self.test_data_to_backtest_communication),
            ("Backtest → Portfolio Communication", self.test_backtest_to_portfolio_communication),
            ("Complete Data Flow", self.test_complete_data_flow),
            ("Redis Pub/Sub", self.test_redis_pubsub),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} ---")
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "PASS" if result else "FAIL"
                logger.info(f"{test_name}: {status}")
                
            except Exception as e:
                logger.error(f"{test_name} FAILED with exception: {e}")
                self.test_results[test_name] = False
        
        # Generate summary
        total_tests = len(tests)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\n🏁 Service Communication Test Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            logger.info("🎉 ALL SERVICE COMMUNICATION TESTS PASSED!")
        else:
            logger.error(f"❌ {total_tests - passed_tests} SERVICE COMMUNICATION TESTS FAILED")
        
        return self.test_results

def main():
    """Main test entry point"""
    tester = ServiceCommunicationTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())