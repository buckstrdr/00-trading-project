#!/usr/bin/env python3
"""
Week 6 Completion Verification - Risk Service
Tests all Risk Service functionality with real data and comprehensive validation.
100% completion means all risk management features working with actual portfolio data.
"""

import requests
import time
import json
import math
from datetime import datetime
from typing import Dict, List, Optional

# Service configuration
RISK_SERVICE_URL = "http://localhost:8003"
PORTFOLIO_SERVICE_URL = "http://localhost:8005"

class Week6Verifier:
    """Comprehensive Week 6 Risk Service verification"""
    
    def __init__(self):
        self.test_results = []
        self.portfolio_id = None
        
    def log_test(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        print(f"{status} {test_name}")
        if details and not passed:
            print(f"    Details: {details}")
    
    def setup_test_portfolio(self) -> bool:
        """Create test portfolio with real trades for comprehensive testing"""
        try:
            # Create test portfolio using query parameters
            params = {
                "name": "Week6_RiskVerification",
                "description": "Verification portfolio for Week 6 risk testing",
                "initial_cash": 100000
            }
            
            response = requests.post(
                f"{PORTFOLIO_SERVICE_URL}/api/portfolio",
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                print(f"Portfolio creation failed: {response.status_code} - {response.text}")
                return False
                
            result = response.json()
            self.portfolio_id = result['portfolio_id']
            
            # Add multiple trades with different outcomes for comprehensive risk testing
            trades = [
                {
                    "symbol": "ES",
                    "quantity": 2,
                    "entry_price": 4500.25,
                    "exit_price": 4520.75,
                    "entry_time": "2024-01-15T09:30:00",
                    "exit_time": "2024-01-15T10:30:00",
                    "side": "long",
                    "commission": 5.0
                },
                {
                    "symbol": "ES", 
                    "quantity": 3,
                    "entry_price": 4525.50,
                    "exit_price": 4515.25,
                    "entry_time": "2024-01-16T14:00:00",
                    "exit_time": "2024-01-16T15:30:00",
                    "side": "long",
                    "commission": 7.5
                },
                {
                    "symbol": "NQ",
                    "quantity": 1,
                    "entry_price": 15500.75,
                    "exit_price": 15650.25,
                    "entry_time": "2024-01-17T11:00:00",
                    "exit_time": "2024-01-17T13:15:00",
                    "side": "long",
                    "commission": 2.5
                },
                {
                    "symbol": "ES",
                    "quantity": 1,
                    "entry_price": 4540.00,
                    "exit_price": 4495.50,
                    "entry_time": "2024-01-18T10:15:00",
                    "exit_time": "2024-01-18T11:45:00",
                    "side": "long",
                    "commission": 2.5
                },
                {
                    "symbol": "NQ",
                    "quantity": 2,
                    "entry_price": 15600.00,
                    "exit_price": 15725.50,
                    "entry_time": "2024-01-19T09:45:00",
                    "exit_time": "2024-01-19T12:30:00",
                    "side": "long",
                    "commission": 5.0
                }
            ]
            
            # Add all trades
            for trade in trades:
                # Convert trade to query parameters
                trade_params = {
                    "symbol": trade["symbol"],
                    "action": "BUY" if trade["side"] == "long" else "SELL",
                    "quantity": trade["quantity"],
                    "price": trade["entry_price"]
                }
                
                response = requests.post(
                    f"{PORTFOLIO_SERVICE_URL}/api/portfolio/{self.portfolio_id}/trade",
                    params=trade_params,
                    timeout=10
                )
                if response.status_code not in [200, 201]:
                    print(f"Trade creation failed: {response.status_code} - {response.text}")
                    return False
                    
            time.sleep(1)  # Allow portfolio to process trades
            return True
            
        except Exception as e:
            print(f"Portfolio setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_1_risk_service_health(self) -> bool:
        """Test 1: Risk Service health check with dependencies"""
        try:
            response = requests.get(f"{RISK_SERVICE_URL}/health", timeout=5)
            
            if response.status_code != 200:
                self.log_test("Risk Service Health", False, f"Status code: {response.status_code}")
                return False
                
            health_data = response.json()
            
            # Verify health response structure
            required_fields = ["status", "service", "timestamp", "details"]
            for field in required_fields:
                if field not in health_data:
                    self.log_test("Risk Service Health", False, f"Missing field: {field}")
                    return False
            
            # Verify service connections
            if health_data["status"] not in ["HEALTHY", "DEGRADED", "healthy", "degraded"]:
                self.log_test("Risk Service Health", False, f"Unexpected status: {health_data['status']}")
                return False
                
            details = health_data.get("details", {})
            if "redis" not in details or "portfolio_service" not in details:
                self.log_test("Risk Service Health", False, "Missing connection details")
                return False
            
            self.log_test("Risk Service Health", True, f"Status: {health_data['status']}")
            return True
            
        except Exception as e:
            self.log_test("Risk Service Health", False, str(e))
            return False
    
    def test_2_sharpe_ratio_calculation(self) -> bool:
        """Test 2: Sharpe ratio calculation with real portfolio data"""
        try:
            if not self.portfolio_id:
                self.log_test("Sharpe Ratio Calculation", False, "No test portfolio")
                return False
            
            response = requests.post(
                f"{RISK_SERVICE_URL}/api/risk/sharpe-ratio",
                params={"portfolio_id": self.portfolio_id, "risk_free_rate": 0.02},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Sharpe Ratio Calculation", False, f"Status code: {response.status_code}")
                return False
            
            sharpe_data = response.json()
            
            # Verify response structure
            required_fields = ["portfolio_id", "sharpe_ratio", "risk_free_rate", "number_of_returns", "calculated_at"]
            for field in required_fields:
                if field not in sharpe_data:
                    self.log_test("Sharpe Ratio Calculation", False, f"Missing field: {field}")
                    return False
            
            # Verify data validity
            if not isinstance(sharpe_data["sharpe_ratio"], (int, float)):
                self.log_test("Sharpe Ratio Calculation", False, "Invalid Sharpe ratio type")
                return False
                
            if sharpe_data["number_of_returns"] <= 0:
                self.log_test("Sharpe Ratio Calculation", False, f"Invalid returns count: {sharpe_data['number_of_returns']}")
                return False
            
            # Verify Sharpe ratio is reasonable (between -5 and 5 for most strategies)
            sharpe_ratio = sharpe_data["sharpe_ratio"]
            if not -5 <= sharpe_ratio <= 5:
                self.log_test("Sharpe Ratio Calculation", False, f"Unreasonable Sharpe ratio: {sharpe_ratio}")
                return False
            
            self.log_test("Sharpe Ratio Calculation", True, 
                         f"Sharpe: {sharpe_ratio:.3f}, Returns: {sharpe_data['number_of_returns']}")
            return True
            
        except Exception as e:
            self.log_test("Sharpe Ratio Calculation", False, str(e))
            return False
    
    def test_3_maximum_drawdown_calculation(self) -> bool:
        """Test 3: Maximum drawdown calculation"""
        try:
            if not self.portfolio_id:
                self.log_test("Maximum Drawdown Calculation", False, "No test portfolio")
                return False
            
            response = requests.post(
                f"{RISK_SERVICE_URL}/api/risk/drawdown",
                params={"portfolio_id": self.portfolio_id},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Maximum Drawdown Calculation", False, f"Status code: {response.status_code}")
                return False
            
            dd_data = response.json()
            
            # Verify response structure
            required_fields = ["portfolio_id", "max_drawdown", "max_drawdown_pct", "peak_value", "trough_value", "drawdown_duration", "calculated_at"]
            for field in required_fields:
                if field not in dd_data:
                    self.log_test("Maximum Drawdown Calculation", False, f"Missing field: {field}")
                    return False
            
            # Verify data validity
            max_dd = dd_data["max_drawdown"]
            max_dd_pct = dd_data["max_drawdown_pct"]
            
            if not isinstance(max_dd, (int, float)) or max_dd < 0:
                self.log_test("Maximum Drawdown Calculation", False, f"Invalid drawdown value: {max_dd}")
                return False
            
            if not isinstance(max_dd_pct, (int, float)) or max_dd_pct < 0:
                self.log_test("Maximum Drawdown Calculation", False, f"Invalid drawdown percentage: {max_dd_pct}")
                return False
                
            # Verify peak >= trough (logical constraint)
            peak_value = dd_data["peak_value"]
            trough_value = dd_data["trough_value"]
            
            if peak_value < trough_value:
                self.log_test("Maximum Drawdown Calculation", False, f"Peak {peak_value} < Trough {trough_value}")
                return False
            
            self.log_test("Maximum Drawdown Calculation", True, 
                         f"Max DD: ${max_dd:.2f} ({max_dd_pct:.2f}%)")
            return True
            
        except Exception as e:
            self.log_test("Maximum Drawdown Calculation", False, str(e))
            return False
    
    def test_4_value_at_risk_calculation(self) -> bool:
        """Test 4: Value at Risk (VaR) calculation"""
        try:
            if not self.portfolio_id:
                self.log_test("Value at Risk Calculation", False, "No test portfolio")
                return False
            
            response = requests.post(
                f"{RISK_SERVICE_URL}/api/risk/var",
                params={"portfolio_id": self.portfolio_id, "confidence_level": 0.95},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Value at Risk Calculation", False, f"Status code: {response.status_code}")
                return False
            
            var_data = response.json()
            
            # Verify response structure
            required_fields = ["portfolio_id", "daily_var", "weekly_var", "monthly_var", "confidence_level", "number_of_returns", "calculated_at"]
            for field in required_fields:
                if field not in var_data:
                    self.log_test("Value at Risk Calculation", False, f"Missing field: {field}")
                    return False
            
            # Verify data validity
            daily_var = var_data["daily_var"]
            weekly_var = var_data["weekly_var"]
            monthly_var = var_data["monthly_var"]
            
            if not all(isinstance(var, (int, float)) and var >= 0 for var in [daily_var, weekly_var, monthly_var]):
                self.log_test("Value at Risk Calculation", False, "Invalid VaR values")
                return False
            
            # Verify scaling relationship (weekly > daily, monthly > weekly)
            if not (daily_var <= weekly_var <= monthly_var):
                self.log_test("Value at Risk Calculation", False, 
                             f"Invalid VaR scaling: D={daily_var}, W={weekly_var}, M={monthly_var}")
                return False
            
            # Verify confidence level
            if var_data["confidence_level"] != 0.95:
                self.log_test("Value at Risk Calculation", False, f"Wrong confidence level: {var_data['confidence_level']}")
                return False
            
            self.log_test("Value at Risk Calculation", True, 
                         f"Daily VaR: {daily_var:.4f}, Weekly: {weekly_var:.4f}")
            return True
            
        except Exception as e:
            self.log_test("Value at Risk Calculation", False, str(e))
            return False
    
    def test_5_position_sizing_calculation(self) -> bool:
        """Test 5: Position sizing with risk parameters"""
        try:
            # Test with realistic trading parameters
            params = {
                "account_value": 100000,
                "risk_per_trade": 0.02,  # 2%
                "entry_price": 4500.25,
                "stop_loss_price": 4480.75,
                "contract_size": 50
            }
            
            response = requests.post(
                f"{RISK_SERVICE_URL}/api/risk/position-size",
                params=params,
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Position Sizing Calculation", False, f"Status code: {response.status_code}")
                return False
            
            pos_data = response.json()
            
            # Verify response structure
            required_fields = ["position_size", "risk_amount", "margin_required", "leverage_ratio", 
                              "account_value", "risk_per_trade_pct", "entry_price", "stop_loss_price", 
                              "contract_size", "calculated_at"]
            for field in required_fields:
                if field not in pos_data:
                    self.log_test("Position Sizing Calculation", False, f"Missing field: {field}")
                    return False
            
            # Verify calculation logic
            position_size = pos_data["position_size"]
            risk_amount = pos_data["risk_amount"]
            margin_required = pos_data["margin_required"]
            leverage_ratio = pos_data["leverage_ratio"]
            
            # Verify position size is positive integer
            if not isinstance(position_size, int) or position_size < 0:
                self.log_test("Position Sizing Calculation", False, f"Invalid position size: {position_size}")
                return False
            
            # Verify risk amount doesn't exceed account risk limit (2% = $2000)
            expected_max_risk = params["account_value"] * params["risk_per_trade"]
            if risk_amount > expected_max_risk * 1.01:  # 1% tolerance
                self.log_test("Position Sizing Calculation", False, 
                             f"Risk amount {risk_amount} exceeds limit {expected_max_risk}")
                return False
            
            # Verify margin requirement is reasonable
            if margin_required < 0 or margin_required > params["account_value"]:
                self.log_test("Position Sizing Calculation", False, f"Invalid margin requirement: {margin_required}")
                return False
            
            # Verify leverage ratio is reasonable (should be > 0 if position size > 0)
            if position_size > 0 and leverage_ratio <= 0:
                self.log_test("Position Sizing Calculation", False, f"Invalid leverage ratio: {leverage_ratio}")
                return False
            
            self.log_test("Position Sizing Calculation", True, 
                         f"Size: {position_size} contracts, Risk: ${risk_amount:.2f}, Margin: ${margin_required:.2f}")
            return True
            
        except Exception as e:
            self.log_test("Position Sizing Calculation", False, str(e))
            return False
    
    def test_6_risk_summary_comprehensive(self) -> bool:
        """Test 6: Comprehensive risk summary with all metrics"""
        try:
            if not self.portfolio_id:
                self.log_test("Risk Summary Comprehensive", False, "No test portfolio")
                return False
            
            response = requests.get(
                f"{RISK_SERVICE_URL}/api/risk/portfolio/{self.portfolio_id}/summary",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Risk Summary Comprehensive", False, f"Status code: {response.status_code}")
                return False
            
            summary_data = response.json()
            
            # Verify response structure
            required_fields = ["portfolio_id", "portfolio_info", "risk_metrics", "calculated_at"]
            for field in required_fields:
                if field not in summary_data:
                    self.log_test("Risk Summary Comprehensive", False, f"Missing field: {field}")
                    return False
            
            # Verify portfolio info
            portfolio_info = summary_data["portfolio_info"]
            required_portfolio_fields = ["initial_value", "current_value", "total_return_pct", "number_of_trades"]
            for field in required_portfolio_fields:
                if field not in portfolio_info:
                    self.log_test("Risk Summary Comprehensive", False, f"Missing portfolio field: {field}")
                    return False
            
            # Verify risk metrics
            risk_metrics = summary_data["risk_metrics"]
            required_risk_fields = ["sharpe_ratio", "max_drawdown", "max_drawdown_pct", "daily_var", "weekly_var", "monthly_var"]
            for field in required_risk_fields:
                if field not in risk_metrics:
                    self.log_test("Risk Summary Comprehensive", False, f"Missing risk field: {field}")
                    return False
            
            # Verify data consistency
            initial_value = portfolio_info["initial_value"]
            current_value = portfolio_info["current_value"]
            total_return_pct = portfolio_info["total_return_pct"]
            number_of_trades = portfolio_info["number_of_trades"]
            
            # Check return calculation consistency
            if initial_value > 0:
                expected_return = ((current_value - initial_value) / initial_value) * 100
                if abs(total_return_pct - expected_return) > 0.01:  # 0.01% tolerance
                    self.log_test("Risk Summary Comprehensive", False, 
                                 f"Return calculation error: expected {expected_return:.2f}%, got {total_return_pct:.2f}%")
                    return False
            
            # Verify we have trades (should be 5 from setup)
            if number_of_trades != 5:
                self.log_test("Risk Summary Comprehensive", False, f"Expected 5 trades, got {number_of_trades}")
                return False
            
            # Verify risk metrics are reasonable
            sharpe_ratio = risk_metrics["sharpe_ratio"]
            max_drawdown = risk_metrics["max_drawdown"]
            
            if not isinstance(sharpe_ratio, (int, float)):
                self.log_test("Risk Summary Comprehensive", False, f"Invalid Sharpe ratio: {sharpe_ratio}")
                return False
                
            if not isinstance(max_drawdown, (int, float)) or max_drawdown < 0:
                self.log_test("Risk Summary Comprehensive", False, f"Invalid max drawdown: {max_drawdown}")
                return False
            
            self.log_test("Risk Summary Comprehensive", True, 
                         f"Return: {total_return_pct:.2f}%, Sharpe: {sharpe_ratio:.3f}, DD: {max_drawdown:.2f}")
            return True
            
        except Exception as e:
            self.log_test("Risk Summary Comprehensive", False, str(e))
            return False
    
    def test_7_risk_limits_monitoring(self) -> bool:
        """Test 7: Risk limits and monitoring settings"""
        try:
            response = requests.get(
                f"{RISK_SERVICE_URL}/api/risk/limits",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Risk Limits Monitoring", False, f"Status code: {response.status_code}")
                return False
            
            limits_data = response.json()
            
            # Verify response structure
            required_fields = ["risk_limits", "monitoring_enabled", "alert_channels"]
            for field in required_fields:
                if field not in limits_data:
                    self.log_test("Risk Limits Monitoring", False, f"Missing field: {field}")
                    return False
            
            # Verify risk limits structure
            risk_limits = limits_data["risk_limits"]
            required_limits = ["max_portfolio_risk", "max_single_trade_risk", "max_drawdown_limit", "min_sharpe_ratio", "max_leverage"]
            for limit in required_limits:
                if limit not in risk_limits:
                    self.log_test("Risk Limits Monitoring", False, f"Missing risk limit: {limit}")
                    return False
            
            # Verify limit values are reasonable
            max_portfolio_risk = risk_limits["max_portfolio_risk"]
            max_single_trade_risk = risk_limits["max_single_trade_risk"]
            max_drawdown_limit = risk_limits["max_drawdown_limit"]
            min_sharpe_ratio = risk_limits["min_sharpe_ratio"]
            max_leverage = risk_limits["max_leverage"]
            
            # Check reasonable limits
            if not (0 < max_portfolio_risk <= 1):
                self.log_test("Risk Limits Monitoring", False, f"Invalid portfolio risk limit: {max_portfolio_risk}")
                return False
                
            if not (0 < max_single_trade_risk <= max_portfolio_risk):
                self.log_test("Risk Limits Monitoring", False, f"Invalid trade risk limit: {max_single_trade_risk}")
                return False
                
            if not (0 < max_drawdown_limit <= 1):
                self.log_test("Risk Limits Monitoring", False, f"Invalid drawdown limit: {max_drawdown_limit}")
                return False
                
            if not (-5 <= min_sharpe_ratio <= 10):
                self.log_test("Risk Limits Monitoring", False, f"Invalid Sharpe limit: {min_sharpe_ratio}")
                return False
                
            if not (1 <= max_leverage <= 20):
                self.log_test("Risk Limits Monitoring", False, f"Invalid leverage limit: {max_leverage}")
                return False
            
            # Verify monitoring settings
            if not isinstance(limits_data["monitoring_enabled"], bool):
                self.log_test("Risk Limits Monitoring", False, "Invalid monitoring_enabled type")
                return False
                
            if not isinstance(limits_data["alert_channels"], list):
                self.log_test("Risk Limits Monitoring", False, "Invalid alert_channels type")
                return False
            
            self.log_test("Risk Limits Monitoring", True, 
                         f"Portfolio: {max_portfolio_risk*100}%, Trade: {max_single_trade_risk*100}%, DD: {max_drawdown_limit*100}%")
            return True
            
        except Exception as e:
            self.log_test("Risk Limits Monitoring", False, str(e))
            return False
    
    def test_8_integration_with_portfolio_service(self) -> bool:
        """Test 8: Integration with Portfolio Service for data retrieval"""
        try:
            if not self.portfolio_id:
                self.log_test("Portfolio Service Integration", False, "No test portfolio")
                return False
            
            # Test that Risk Service can retrieve portfolio data
            # We'll verify this by calling risk endpoints that depend on portfolio data
            
            # Test Sharpe ratio (requires trade data from Portfolio Service)
            response = requests.post(
                f"{RISK_SERVICE_URL}/api/risk/sharpe-ratio",
                params={"portfolio_id": self.portfolio_id},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Portfolio Service Integration", False, "Failed to get trade data for Sharpe calculation")
                return False
            
            sharpe_data = response.json()
            if sharpe_data["number_of_returns"] != 5:  # Should match our 5 test trades
                self.log_test("Portfolio Service Integration", False, 
                             f"Expected 5 returns from Portfolio Service, got {sharpe_data['number_of_returns']}")
                return False
            
            # Test drawdown (requires equity curve from Portfolio Service)
            response = requests.post(
                f"{RISK_SERVICE_URL}/api/risk/drawdown",
                params={"portfolio_id": self.portfolio_id},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Portfolio Service Integration", False, "Failed to get equity data for drawdown calculation")
                return False
            
            # Verify we can get portfolio summary through Risk Service
            response = requests.get(
                f"{RISK_SERVICE_URL}/api/risk/portfolio/{self.portfolio_id}/summary",
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Portfolio Service Integration", False, "Failed to get portfolio summary")
                return False
                
            summary = response.json()
            if summary["portfolio_info"]["number_of_trades"] != 5:
                self.log_test("Portfolio Service Integration", False, 
                             f"Portfolio integration error: expected 5 trades, got {summary['portfolio_info']['number_of_trades']}")
                return False
            
            self.log_test("Portfolio Service Integration", True, "Successfully integrated with Portfolio Service")
            return True
            
        except Exception as e:
            self.log_test("Portfolio Service Integration", False, str(e))
            return False
    
    def cleanup_test_data(self):
        """Clean up test portfolio"""
        try:
            if self.portfolio_id:
                requests.delete(f"{PORTFOLIO_SERVICE_URL}/api/portfolio/{self.portfolio_id}", timeout=5)
        except:
            pass  # Best effort cleanup
    
    def run_all_tests(self) -> Dict:
        """Run all Week 6 verification tests"""
        print("=" * 70)
        print("WEEK 6 COMPLETION VERIFICATION - RISK SERVICE")
        print("=" * 70)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Setup test data
        print("Setting up test portfolio with real trades...")
        if not self.setup_test_portfolio():
            print("CRITICAL: Failed to setup test portfolio - cannot proceed")
            return {"passed": 0, "total": 8, "completion_rate": 0.0, "status": "FAILED"}
        
        print(f"Test portfolio created: {self.portfolio_id}")
        print()
        
        # Run all tests
        test_functions = [
            self.test_1_risk_service_health,
            self.test_2_sharpe_ratio_calculation,
            self.test_3_maximum_drawdown_calculation,
            self.test_4_value_at_risk_calculation,
            self.test_5_position_sizing_calculation,
            self.test_6_risk_summary_comprehensive,
            self.test_7_risk_limits_monitoring,
            self.test_8_integration_with_portfolio_service
        ]
        
        print("Running Risk Service verification tests...")
        print("-" * 70)
        
        for test_func in test_functions:
            test_func()
        
        # Cleanup
        print()
        print("Cleaning up test data...")
        self.cleanup_test_data()
        
        # Calculate results
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        completion_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print()
        print("=" * 70)
        print("WEEK 6 VERIFICATION RESULTS")
        print("=" * 70)
        
        for result in self.test_results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {result['test']}")
            if not result["passed"] and result["details"]:
                print(f"    {result['details']}")
        
        print()
        print("-" * 70)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Completion Rate: {completion_rate:.1f}%")
        
        if completion_rate == 100.0:
            print("WEEK 6 COMPLETE - All Risk Service features verified!")
            status = "COMPLETE"
        else:
            print("WEEK 6 INCOMPLETE - Some tests failed")
            status = "INCOMPLETE"
        
        print(f"Completion time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        return {
            "passed": passed_tests,
            "total": total_tests,
            "completion_rate": completion_rate,
            "status": status,
            "test_results": self.test_results
        }

def main():
    """Main verification function"""
    verifier = Week6Verifier()
    results = verifier.run_all_tests()
    
    # Exit with appropriate code
    if results["status"] == "COMPLETE":
        print("\nWeek 6 Risk Service is 100% complete and tested with real data!")
        exit(0)
    else:
        print(f"\nWeek 6 verification failed - {results['completion_rate']:.1f}% complete")
        exit(1)

if __name__ == "__main__":
    main()