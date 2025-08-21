#!/usr/bin/env python3
"""
Week 5 Completion Verification
Verifies Portfolio Service implementation and position tracking
"""

import sys
import requests
import time
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import setup_logging, generate_id
from config.settings import SERVICE_PORTS

logger = setup_logging("Week5Verification", "INFO")

class Week5Verifier:
    """Week 5 milestone verification"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.portfolio_service_url = f"http://localhost:{SERVICE_PORTS['portfolio']}"
        self.backtest_service_url = f"http://localhost:{SERVICE_PORTS['backtest']}"
        self.test_portfolio_id = None
        self.results = {}
    
    def verify_portfolio_service_api(self) -> bool:
        """Verify Portfolio Service API endpoints"""
        try:
            # Test health endpoint
            response = requests.get(f"{self.portfolio_service_url}/health", timeout=5)
            if response.status_code != 200:
                logger.error(f"Portfolio Service health check failed: {response.status_code}")
                return False
            
            health_data = response.json()
            if health_data.get('status') != 'healthy':
                logger.error(f"Portfolio Service not healthy: {health_data}")
                return False
            
            # Test create portfolio
            create_response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio",
                params={'name': 'Week5_Test', 'initial_cash': 25000}
            )
            
            if create_response.status_code != 200:
                logger.error(f"Portfolio creation failed: {create_response.status_code}")
                return False
            
            portfolio_data = create_response.json()
            self.test_portfolio_id = portfolio_data.get('portfolio_id')
            
            if not self.test_portfolio_id:
                logger.error("Portfolio creation did not return portfolio ID")
                return False
            
            # Test get portfolio
            get_response = requests.get(f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}")
            
            if get_response.status_code != 200:
                logger.error(f"Portfolio retrieval failed: {get_response.status_code}")
                return False
            
            logger.info("✅ Portfolio Service API working")
            return True
            
        except Exception as e:
            logger.error(f"Portfolio Service API verification failed: {e}")
            return False
    
    def verify_position_tracking(self) -> bool:
        """Verify position tracking logic"""
        if not self.test_portfolio_id:
            logger.error("No test portfolio available for position tracking")
            return False
        
        try:
            # Record first trade
            trade1_response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/trade",
                params={
                    'symbol': 'MCL',
                    'action': 'BUY',
                    'quantity': 3,
                    'price': 65.00,
                    'strategy_name': 'Week5Test'
                }
            )
            
            if trade1_response.status_code != 200:
                logger.error("First trade recording failed")
                return False
            
            # Record second trade (different price - test averaging)
            trade2_response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/trade",
                params={
                    'symbol': 'MCL',
                    'action': 'BUY',
                    'quantity': 2,
                    'price': 66.00,
                    'strategy_name': 'Week5Test'
                }
            )
            
            if trade2_response.status_code != 200:
                logger.error("Second trade recording failed")
                return False
            
            # Check positions
            positions_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/positions"
            )
            
            if positions_response.status_code != 200:
                logger.error("Position retrieval failed")
                return False
            
            positions_data = positions_response.json()
            positions = positions_data.get('positions', [])
            
            if len(positions) != 1:
                logger.error(f"Expected 1 position, got {len(positions)}")
                return False
            
            position = positions[0]
            
            # Verify position details
            if position.get('symbol') != 'MCL':
                logger.error(f"Position symbol mismatch: {position.get('symbol')}")
                return False
            
            if position.get('quantity') != 5:  # 3 + 2
                logger.error(f"Position quantity mismatch: {position.get('quantity')}")
                return False
            
            # Verify average price calculation: (3*65.00 + 2*66.00) / 5 = 65.40
            expected_avg = (3 * 65.00 + 2 * 66.00) / 5
            actual_avg = position.get('avg_price', 0)
            
            if abs(actual_avg - expected_avg) > 0.01:
                logger.error(f"Average price calculation error: expected {expected_avg}, got {actual_avg}")
                return False
            
            logger.info("✅ Position tracking and averaging working correctly")
            return True
            
        except Exception as e:
            logger.error(f"Position tracking verification failed: {e}")
            return False
    
    def verify_equity_curve_calculation(self) -> bool:
        """Verify equity curve calculation"""
        if not self.test_portfolio_id:
            logger.error("No test portfolio available for equity curve")
            return False
        
        try:
            # Get equity curve
            equity_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/equity-curve"
            )
            
            if equity_response.status_code != 200:
                logger.error("Equity curve retrieval failed")
                return False
            
            equity_data = equity_response.json()
            equity_curve = equity_data.get('equity_curve', {})
            
            # Verify equity curve structure
            required_fields = [
                'portfolio_id', 'initial_cash', 'current_cash', 
                'positions_value', 'total_value', 'total_pnl', 
                'total_return_pct', 'total_trades'
            ]
            
            missing_fields = [field for field in required_fields if field not in equity_curve]
            if missing_fields:
                logger.error(f"Equity curve missing fields: {missing_fields}")
                return False
            
            # Verify calculations make sense
            if equity_curve.get('total_trades') != 2:
                logger.error(f"Trade count mismatch in equity curve: {equity_curve.get('total_trades')}")
                return False
            
            if equity_curve.get('portfolio_id') != self.test_portfolio_id:
                logger.error("Portfolio ID mismatch in equity curve")
                return False
            
            logger.info("✅ Equity curve calculation working")
            return True
            
        except Exception as e:
            logger.error(f"Equity curve verification failed: {e}")
            return False
    
    def verify_trade_recording(self) -> bool:
        """Verify trade recording functionality"""
        if not self.test_portfolio_id:
            logger.error("No test portfolio available for trade recording")
            return False
        
        try:
            # Get trade history
            trades_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/trades"
            )
            
            if trades_response.status_code != 200:
                logger.error("Trade history retrieval failed")
                return False
            
            trades_data = trades_response.json()
            trades = trades_data.get('trades', [])
            
            if len(trades) != 2:  # We recorded 2 trades
                logger.error(f"Expected 2 trades, found {len(trades)}")
                return False
            
            # Verify trade structure
            for trade in trades:
                required_fields = ['trade_id', 'symbol', 'action', 'quantity', 'price', 'timestamp']
                missing_fields = [field for field in required_fields if field not in trade]
                
                if missing_fields:
                    logger.error(f"Trade missing fields: {missing_fields}")
                    return False
            
            logger.info("✅ Trade recording functionality working")
            return True
            
        except Exception as e:
            logger.error(f"Trade recording verification failed: {e}")
            return False
    
    def verify_multiple_positions(self) -> bool:
        """Verify multiple positions handling"""
        if not self.test_portfolio_id:
            logger.error("No test portfolio available for multiple positions")
            return False
        
        try:
            # Add a different symbol
            trade_response = requests.post(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/trade",
                params={
                    'symbol': 'MES',
                    'action': 'BUY',
                    'quantity': 10,
                    'price': 4250.0,
                    'strategy_name': 'Week5Test'
                }
            )
            
            if trade_response.status_code != 200:
                logger.error("Multiple position trade failed")
                return False
            
            # Check positions now include both symbols
            positions_response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{self.test_portfolio_id}/positions"
            )
            
            if positions_response.status_code != 200:
                logger.error("Multiple positions retrieval failed")
                return False
            
            positions_data = positions_response.json()
            positions = positions_data.get('positions', [])
            
            if len(positions) != 2:
                logger.error(f"Expected 2 positions (MCL + MES), got {len(positions)}")
                return False
            
            symbols = [pos.get('symbol') for pos in positions]
            expected_symbols = ['MCL', 'MES']
            
            for symbol in expected_symbols:
                if symbol not in symbols:
                    logger.error(f"Missing expected symbol: {symbol}")
                    return False
            
            logger.info("✅ Multiple positions handling working")
            return True
            
        except Exception as e:
            logger.error(f"Multiple positions verification failed: {e}")
            return False
    
    def verify_backtest_integration(self) -> bool:
        """Verify integration with Backtest Service"""
        try:
            # Test backtest with portfolio recording
            backtest_params = {
                'strategy_name': 'SimpleMAStrategy',
                'symbol': 'MCL',
                'start_date': '2024-01-01',
                'end_date': '2024-01-02',
                'initial_cash': 15000,
                'record_to_portfolio': True
            }
            
            response = requests.post(
                f"{self.backtest_service_url}/api/backtest",
                params=backtest_params,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Integrated backtest failed: {response.status_code}")
                return False
            
            backtest_result = response.json()
            
            # Check if portfolio was created
            if 'portfolio_id' not in backtest_result:
                logger.error("Backtest integration did not create portfolio")
                return False
            
            if 'trades_recorded' not in backtest_result:
                logger.error("Backtest integration did not record trades count")
                return False
            
            logger.info("✅ Backtest-Portfolio integration working")
            return True
            
        except Exception as e:
            logger.error(f"Backtest integration verification failed: {e}")
            return False
    
    def run_verification(self) -> dict:
        """Run all Week 5 verification checks"""
        logger.info("🧪 Starting Week 5 Completion Verification")
        logger.info("=" * 50)
        
        tests = [
            ("Portfolio Service API", self.verify_portfolio_service_api),
            ("Position Tracking Logic", self.verify_position_tracking),
            ("Equity Curve Calculation", self.verify_equity_curve_calculation),
            ("Trade Recording Functionality", self.verify_trade_recording),
            ("Multiple Positions Handling", self.verify_multiple_positions),
            ("Backtest Integration", self.verify_backtest_integration)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\\n--- {test_name} ---")
            try:
                result = test_func()
                self.results[test_name] = result
                status = "PASS" if result else "FAIL"
                logger.info(f"{test_name}: {status}")
                
            except Exception as e:
                logger.error(f"{test_name} FAILED with exception: {e}")
                self.results[test_name] = False
        
        # Generate summary
        total_tests = len(tests)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\\n🏁 Week 5 Verification Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            logger.info("🎉 WEEK 5 COMPLETE - PORTFOLIO SERVICE EXCELLENCE!")
        else:
            logger.error(f"❌ WEEK 5 INCOMPLETE - {total_tests - passed_tests} TARGETS FAILED")
        
        return self.results

def main():
    """Main verification entry point"""
    verifier = Week5Verifier()
    results = verifier.run_verification()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())