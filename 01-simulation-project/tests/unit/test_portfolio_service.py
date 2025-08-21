#!/usr/bin/env python3
"""
Portfolio Service Test Suite
Tests portfolio management, position tracking, trade recording, and equity curve calculation
"""

import sys
import time
import requests
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from shared.utils import setup_logging
from config.settings import SERVICE_PORTS

logger = setup_logging("PortfolioServiceTest", "INFO")

class PortfolioServiceTester:
    """Portfolio Service test suite"""
    
    def __init__(self):
        self.portfolio_service_url = f"http://localhost:{SERVICE_PORTS['portfolio']}"
        self.test_portfolio_id = None
        self.test_trade_ids = []
        self.test_results = {}
        
    def test_service_health(self) -> bool:
        """Test Portfolio Service health endpoint"""
        logger.info("Testing Portfolio Service health...")
        
        try:
            response = requests.get(f"{self.portfolio_service_url}/health", timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"   Health check failed with status {response.status_code}")
                return False
            
            health_data = response.json()
            
            required_fields = ['status', 'service', 'details']
            for field in required_fields:
                if field not in health_data:
                    logger.error(f"   Missing health field: {field}")
                    return False
            
            if health_data['service'] != 'PortfolioService':
                logger.error(f"   Unexpected service name: {health_data['service']}")
                return False
            
            logger.info(f"   Portfolio Service health: {health_data['status']}")
            logger.info(f"   Portfolios: {health_data['details'].get('portfolios', 0)}")
            logger.info(f"   Total Trades: {health_data['details'].get('total_trades', 0)}")
            logger.info(f"   Active Positions: {health_data['details'].get('active_positions', 0)}")
            
            logger.info("   ✅ Portfolio Service health check passed")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Portfolio Service health test failed: {e}")
            return False
    
    def test_create_portfolio(self) -> bool:
        """Test portfolio creation"""
        logger.info("Testing portfolio creation...")
        
        try:
            # Create test portfolio
            portfolio_data = {
                "name": "Test Portfolio",
                "initial_cash": 100000.0
            }
            
            response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio",
                params=portfolio_data,
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Portfolio creation failed with status {response.status_code}")
                logger.error(f"   Response: {response.text}")
                return False
            
            result = response.json()
            
            required_fields = ['status', 'portfolio_id', 'name', 'initial_cash']
            for field in required_fields:
                if field not in result:
                    logger.error(f"   Missing response field: {field}")
                    return False
            
            if result['status'] != 'success':
                logger.error(f"   Unexpected status: {result['status']}")
                return False
            
            # Store test portfolio ID for other tests
            self.test_portfolio_id = result['portfolio_id']
            
            logger.info(f"   ✅ Created portfolio: {self.test_portfolio_id}")
            logger.info(f"   Name: {result['name']}, Initial Cash: ${result['initial_cash']:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Portfolio creation test failed: {e}")
            return False
    
    def test_get_portfolio(self) -> bool:
        """Test retrieving portfolio information"""
        logger.info("Testing portfolio retrieval...")
        
        if not self.test_portfolio_id:
            logger.error("   ❌ No test portfolio ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}",
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Portfolio retrieval failed with status {response.status_code}")
                return False
            
            result = response.json()
            
            if result['status'] != 'success':
                logger.error(f"   Unexpected status: {result['status']}")
                return False
            
            portfolio = result['portfolio']
            required_fields = ['id', 'name', 'initial_cash', 'current_cash', 'created_at', 'updated_at']
            for field in required_fields:
                if field not in portfolio:
                    logger.error(f"   Missing portfolio field: {field}")
                    return False
            
            logger.info(f"   ✅ Retrieved portfolio: {portfolio['id']}")
            logger.info(f"   Name: {portfolio['name']}, Current Cash: ${portfolio['current_cash']:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Portfolio retrieval test failed: {e}")
            return False
    
    def test_record_trades(self) -> bool:
        """Test trade recording and position tracking"""
        logger.info("Testing trade recording and position tracking...")
        
        if not self.test_portfolio_id:
            logger.error("   ❌ No test portfolio ID available")
            return False
        
        try:
            # Test trades to create multiple positions
            test_trades = [
                {"symbol": "MCL", "action": "BUY", "quantity": 10, "price": 75.50, "strategy": "TestStrategy1"},
                {"symbol": "MCL", "action": "BUY", "quantity": 5, "price": 76.00, "strategy": "TestStrategy1"},
                {"symbol": "ES", "action": "BUY", "quantity": 3, "price": 4250.00, "strategy": "TestStrategy2"},
                {"symbol": "MCL", "action": "SELL", "quantity": 5, "price": 77.00, "strategy": "TestStrategy1"},
            ]
            
            for i, trade in enumerate(test_trades):
                logger.info(f"   Recording trade {i+1}: {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
                
                response = requests.post(
                    f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/trade",
                    params={
                        "symbol": trade["symbol"],
                        "action": trade["action"],
                        "quantity": trade["quantity"],
                        "price": trade["price"],
                        "strategy_name": trade["strategy"]
                    },
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"   Trade recording failed with status {response.status_code}")
                    logger.error(f"   Response: {response.text}")
                    return False
                
                result = response.json()
                
                if result['status'] != 'success':
                    logger.error(f"   Trade recording failed: {result}")
                    return False
                
                self.test_trade_ids.append(result['trade_id'])
                time.sleep(0.5)  # Small delay between trades
            
            logger.info(f"   ✅ Recorded {len(test_trades)} trades successfully")
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Trade recording test failed: {e}")
            return False
    
    def test_get_positions(self) -> bool:
        """Test position retrieval and validation"""
        logger.info("Testing position retrieval...")
        
        if not self.test_portfolio_id:
            logger.error("   ❌ No test portfolio ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/positions",
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Position retrieval failed with status {response.status_code}")
                return False
            
            result = response.json()
            
            if result['status'] != 'success':
                logger.error(f"   Position retrieval failed: {result}")
                return False
            
            positions = result['positions']
            position_count = result['position_count']
            
            logger.info(f"   ✅ Retrieved {position_count} positions")
            
            # Validate positions
            expected_positions = {
                'MCL': 10,  # 10 + 5 - 5 = 10
                'ES': 3     # 3
            }
            
            actual_positions = {pos['symbol']: pos['quantity'] for pos in positions}
            
            for symbol, expected_qty in expected_positions.items():
                if symbol not in actual_positions:
                    logger.error(f"   ❌ Missing expected position for {symbol}")
                    return False
                
                if actual_positions[symbol] != expected_qty:
                    logger.error(f"   ❌ Position quantity mismatch for {symbol}: expected {expected_qty}, got {actual_positions[symbol]}")
                    return False
                
                logger.info(f"   ✅ {symbol}: {actual_positions[symbol]} contracts")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Position retrieval test failed: {e}")
            return False
    
    def test_get_trades(self) -> bool:
        """Test trade history retrieval"""
        logger.info("Testing trade history retrieval...")
        
        if not self.test_portfolio_id:
            logger.error("   ❌ No test portfolio ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/trades",
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Trade history retrieval failed with status {response.status_code}")
                return False
            
            result = response.json()
            
            if result['status'] != 'success':
                logger.error(f"   Trade history retrieval failed: {result}")
                return False
            
            trades = result['trades']
            trade_count = result['trade_count']
            
            logger.info(f"   ✅ Retrieved {trade_count} trades")
            
            # Validate trade count
            if trade_count != 4:
                logger.error(f"   ❌ Expected 4 trades, got {trade_count}")
                return False
            
            # Validate trade structure
            required_fields = ['trade_id', 'symbol', 'action', 'quantity', 'price', 'timestamp', 'strategy_name']
            for i, trade in enumerate(trades):
                for field in required_fields:
                    if field not in trade:
                        logger.error(f"   ❌ Missing trade field in trade {i+1}: {field}")
                        return False
                
                logger.info(f"   Trade {i+1}: {trade['action']} {trade['quantity']} {trade['symbol']} @ ${trade['price']:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Trade history retrieval test failed: {e}")
            return False
    
    def test_equity_curve_calculation(self) -> bool:
        """Test equity curve calculation"""
        logger.info("Testing equity curve calculation...")
        
        if not self.test_portfolio_id:
            logger.error("   ❌ No test portfolio ID available")
            return False
        
        try:
            response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/equity-curve",
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Equity curve calculation failed with status {response.status_code}")
                return False
            
            result = response.json()
            
            if result['status'] != 'success':
                logger.error(f"   Equity curve calculation failed: {result}")
                return False
            
            equity_curve = result['equity_curve']
            
            required_fields = [
                'portfolio_id', 'portfolio_name', 'timestamp', 'initial_cash', 
                'current_cash', 'positions_value', 'total_value', 'total_pnl', 
                'total_return_pct', 'total_trades', 'total_commission', 'snapshot_id'
            ]
            
            for field in required_fields:
                if field not in equity_curve:
                    logger.error(f"   ❌ Missing equity curve field: {field}")
                    return False
            
            logger.info(f"   ✅ Equity curve calculated successfully")
            logger.info(f"   Initial Cash: ${equity_curve['initial_cash']:,.2f}")
            logger.info(f"   Current Cash: ${equity_curve['current_cash']:,.2f}")
            logger.info(f"   Positions Value: ${equity_curve['positions_value']:,.2f}")
            logger.info(f"   Total Value: ${equity_curve['total_value']:,.2f}")
            logger.info(f"   Total PnL: ${equity_curve['total_pnl']:,.2f}")
            logger.info(f"   Total Return: {equity_curve['total_return_pct']:.2f}%")
            logger.info(f"   Total Trades: {equity_curve['total_trades']}")
            logger.info(f"   Total Commission: ${equity_curve['total_commission']:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Equity curve calculation test failed: {e}")
            return False
    
    def test_service_stats(self) -> bool:
        """Test service statistics endpoint"""
        logger.info("Testing service statistics...")
        
        try:
            response = requests.get(f"{self.portfolio_service_url}/api/stats", timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"   Service stats failed with status {response.status_code}")
                return False
            
            result = response.json()
            
            if result['status'] != 'success':
                logger.error(f"   Service stats failed: {result}")
                return False
            
            stats = result['statistics']
            
            required_fields = [
                'total_portfolios', 'total_trades', 'active_positions', 
                'total_snapshots', 'total_initial_cash', 'total_current_cash', 'database_size_mb'
            ]
            
            for field in required_fields:
                if field not in stats:
                    logger.error(f"   ❌ Missing stats field: {field}")
                    return False
            
            logger.info(f"   ✅ Service statistics retrieved")
            logger.info(f"   Total Portfolios: {stats['total_portfolios']}")
            logger.info(f"   Total Trades: {stats['total_trades']}")
            logger.info(f"   Active Positions: {stats['active_positions']}")
            logger.info(f"   Total Snapshots: {stats['total_snapshots']}")
            logger.info(f"   Database Size: {stats['database_size_mb']} MB")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Service statistics test failed: {e}")
            return False
    
    def test_multiple_portfolios(self) -> bool:
        """Test creating and managing multiple portfolios"""
        logger.info("Testing multiple portfolio management...")
        
        try:
            # Create second portfolio
            portfolio_data = {
                "name": "Second Test Portfolio",
                "initial_cash": 50000.0
            }
            
            response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio",
                params=portfolio_data,
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Second portfolio creation failed with status {response.status_code}")
                return False
            
            result = response.json()
            second_portfolio_id = result['portfolio_id']
            
            # Record trade in second portfolio
            response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio/{second_portfolio_id}/trade",
                params={
                    "symbol": "NQ",
                    "action": "BUY",
                    "quantity": 2,
                    "price": 15000.0,
                    "strategy_name": "SecondPortfolioStrategy"
                },
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.error(f"   Trade in second portfolio failed")
                return False
            
            # List all portfolios
            response = requests.get(f"{self.portfolio_service_url}/api/portfolios", timeout=10.0)
            
            if response.status_code != 200:
                logger.error(f"   Portfolio listing failed")
                return False
            
            result = response.json()
            portfolios = result['portfolios']
            
            if len(portfolios) < 2:
                logger.error(f"   Expected at least 2 portfolios, got {len(portfolios)}")
                return False
            
            logger.info(f"   ✅ Multiple portfolio management test passed")
            logger.info(f"   Total portfolios: {len(portfolios)}")
            
            return True
            
        except Exception as e:
            logger.error(f"   ❌ Multiple portfolio test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all Portfolio Service tests"""
        logger.info("🧪 Starting Portfolio Service Tests")
        logger.info("=" * 50)
        
        tests = [
            ("Service Health Check", self.test_service_health),
            ("Portfolio Creation", self.test_create_portfolio),
            ("Portfolio Retrieval", self.test_get_portfolio),
            ("Trade Recording", self.test_record_trades),
            ("Position Tracking", self.test_get_positions),
            ("Trade History", self.test_get_trades),
            ("Equity Curve Calculation", self.test_equity_curve_calculation),
            ("Service Statistics", self.test_service_stats),
            ("Multiple Portfolios", self.test_multiple_portfolios)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            logger.info(f"\n--- Running Test: {test_name} ---")
            try:
                start_time = time.time()
                result = test_func()
                end_time = time.time()
                
                results[test_name] = result
                status = "PASS" if result else "FAIL"
                duration = end_time - start_time
                logger.info(f"Test {test_name}: {status} ({duration:.2f}s)")
                
            except Exception as e:
                logger.error(f"Test {test_name} FAILED with exception: {e}")
                results[test_name] = False
        
        # Generate summary
        total_tests = len(tests)
        passed_tests = sum(1 for result in results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\n🏁 Portfolio Service Test Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            logger.info("🎉 ALL PORTFOLIO SERVICE TESTS PASSED!")
        else:
            logger.error(f"❌ {total_tests - passed_tests} PORTFOLIO SERVICE TESTS FAILED")
        
        return results

def main():
    """Main test entry point"""
    tester = PortfolioServiceTester()
    results = tester.run_all_tests()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())