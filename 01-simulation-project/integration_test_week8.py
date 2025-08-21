#!/usr/bin/env python3
"""
Week 8 Integration Testing - Complete End-to-End Service Integration
Tests the complete futures backtesting workflow across all services:
Data -> ML -> Portfolio -> Risk -> Backtest

Per CLAUDE.md rules: Real testing with timestamps, exit codes, no faking
"""

import requests
import time
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path

class Week8IntegrationTester:
    """Complete end-to-end integration testing for Week 8"""
    
    def __init__(self):
        self.services = {
            'data': 'http://localhost:8001',
            'backtest': 'http://localhost:8002', 
            'risk': 'http://localhost:8003',
            'ml': 'http://localhost:8004',
            'portfolio': 'http://localhost:8005'
        }
        self.test_results = []
        self.test_data = {}  # Store data between test phases
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, passed: bool, details: str = "", metrics: Dict = None):
        """Log test result with timestamp per CLAUDE.md"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        status = "PASS" if passed else "FAIL"
        
        result = {
            "test": test_name,
            "status": status,
            "passed": passed,
            "details": details,
            "metrics": metrics or {},
            "timestamp": timestamp
        }
        
        self.test_results.append(result)
        print(f"[{timestamp}] {status} - {test_name}")
        if details:
            print(f"    {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"    {key}: {value}")
    
    def check_service_health(self) -> bool:
        """Verify all services are healthy before integration testing"""
        print("=== SERVICE HEALTH VERIFICATION ===")
        
        for service_name, url in self.services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    health_data = response.json()
                    self.log_test(f"Service Health - {service_name.title()}", True, 
                                f"Status: {health_data.get('status', 'unknown')}")
                else:
                    self.log_test(f"Service Health - {service_name.title()}", False, 
                                f"HTTP {response.status_code}")
                    return False
            except Exception as e:
                self.log_test(f"Service Health - {service_name.title()}", False, str(e))
                return False
        
        return True
    
    def test_data_service_integration(self) -> bool:
        """Test Data Service provides data for other services"""
        print("\\n=== DATA SERVICE INTEGRATION ===")
        
        try:
            # Test market data retrieval
            response = requests.get(
                f"{self.services['data']}/api/data/MCL",
                params={"start_date": "2024-01-01", "end_date": "2024-01-31", "limit": 100},
                timeout=10
            )
            
            if response.status_code != 200:
                self.log_test("Data Service Integration", False, f"HTTP {response.status_code}")
                return False
            
            data = response.json()
            
            # Verify data structure for other services
            required_fields = ["symbol", "records", "data"]
            for field in required_fields:
                if field not in data:
                    self.log_test("Data Service Integration", False, f"Missing field: {field}")
                    return False
            
            market_data = data["data"]
            if not market_data or len(market_data) < 50:
                self.log_test("Data Service Integration", False, "Insufficient market data")
                return False
            
            # Verify OHLCV structure that other services expect
            sample_record = market_data[0]
            required_ohlcv = ["open", "high", "low", "close", "volume", "timestamp"]
            for field in required_ohlcv:
                if field not in sample_record:
                    self.log_test("Data Service Integration", False, f"Missing OHLCV field: {field}")
                    return False
            
            # Store data for other tests
            self.test_data['market_data'] = market_data
            self.test_data['symbol'] = 'MCL'
            
            metrics = {
                "records_retrieved": len(market_data),
                "date_range": f"{market_data[-1]['timestamp']} to {market_data[0]['timestamp']}",
                "latest_close": sample_record['close']
            }
            
            self.log_test("Data Service Integration", True, 
                         f"Retrieved {len(market_data)} OHLCV records for ML/Portfolio services", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Data Service Integration", False, f"Exception: {e}")
            return False
    
    def test_ml_service_integration(self) -> bool:
        """Test ML Service integration with Data Service"""
        print("\\n=== ML SERVICE INTEGRATION ===")
        
        try:
            # Test ML features extraction (depends on Data Service)
            response = requests.post(
                f"{self.services['ml']}/api/ml/features",
                params={"symbol": self.test_data['symbol'], "days_back": 50},
                timeout=15
            )
            
            if response.status_code != 200:
                self.log_test("ML-Data Integration", False, f"Feature extraction failed: {response.status_code}")
                return False
            
            features_data = response.json()
            
            if features_data.get("status") != "success":
                self.log_test("ML-Data Integration", False, "Feature extraction unsuccessful")
                return False
            
            features = features_data["features"]
            feature_count = features["feature_count"]
            
            # Train ML models for later integration tests
            print("  Training ML models for integration...")
            
            # Train regression model
            train_response = requests.post(
                f"{self.services['ml']}/api/ml/train/regression",
                params={"symbol": self.test_data['symbol'], "start_date": "2024-01-01", "end_date": "2024-01-31"},
                timeout=30
            )
            
            if train_response.status_code != 200:
                self.log_test("ML Model Training", False, f"Regression training failed: {train_response.status_code}")
                return False
            
            # Train classification model  
            classify_response = requests.post(
                f"{self.services['ml']}/api/ml/train/classification", 
                params={"symbol": self.test_data['symbol'], "start_date": "2024-01-01", "end_date": "2024-01-31"},
                timeout=30
            )
            
            if classify_response.status_code != 200:
                self.log_test("ML Model Training", False, f"Classification training failed: {classify_response.status_code}")
                return False
            
            # Test predictions for strategy integration
            predict_response = requests.post(
                f"{self.services['ml']}/api/ml/predict",
                params={"symbol": self.test_data['symbol'], "days_back": 30},
                timeout=10
            )
            
            if predict_response.status_code != 200:
                self.log_test("ML Predictions", False, f"Prediction failed: {predict_response.status_code}")
                return False
            
            predictions = predict_response.json()["predictions"]
            
            # Store ML data for other services
            self.test_data['ml_predictions'] = predictions
            self.test_data['current_price'] = predictions['current_price']
            self.test_data['predicted_price'] = predictions['predicted_price']
            
            metrics = {
                "features_generated": feature_count,
                "current_price": predictions['current_price'],
                "predicted_price": predictions['predicted_price'],
                "predicted_change": predictions['predicted_change'] * 100
            }
            
            self.log_test("ML Service Integration", True, 
                         f"ML pipeline working: {feature_count} features, models trained, predictions generated", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("ML Service Integration", False, f"Exception: {e}")
            return False
    
    def test_portfolio_service_integration(self) -> bool:
        """Test Portfolio Service integration with ML and Risk services"""
        print("\\n=== PORTFOLIO SERVICE INTEGRATION ===")
        
        try:
            # Create test portfolio
            portfolio_response = requests.post(
                f"{self.services['portfolio']}/api/portfolio",
                params={
                    "name": "Week8_Integration_Test",
                    "description": "End-to-end integration test portfolio", 
                    "initial_cash": 100000
                },
                timeout=10
            )
            
            if portfolio_response.status_code != 200:
                self.log_test("Portfolio Creation", False, f"Portfolio creation failed: {portfolio_response.status_code}")
                return False
            
            portfolio_data = portfolio_response.json()
            portfolio_id = portfolio_data['portfolio_id']
            self.test_data['portfolio_id'] = portfolio_id
            
            # Execute trades based on ML predictions
            trades = [
                {
                    "symbol": self.test_data['symbol'],
                    "action": "BUY",
                    "quantity": 2,
                    "price": self.test_data['current_price'] * 0.999  # Slightly below current
                },
                {
                    "symbol": self.test_data['symbol'], 
                    "action": "BUY",
                    "quantity": 1,
                    "price": self.test_data['current_price'] * 1.001  # Slightly above current
                }
            ]
            
            for i, trade in enumerate(trades):
                trade_response = requests.post(
                    f"{self.services['portfolio']}/api/portfolio/{portfolio_id}/trade",
                    params=trade,
                    timeout=10
                )
                
                if trade_response.status_code not in [200, 201]:
                    self.log_test(f"Portfolio Trade {i+1}", False, 
                                f"Trade failed: {trade_response.status_code}")
                    return False
            
            # Get portfolio status for risk analysis
            portfolio_status_response = requests.get(
                f"{self.services['portfolio']}/api/portfolio/{portfolio_id}",
                timeout=10
            )
            
            if portfolio_status_response.status_code != 200:
                self.log_test("Portfolio Status", False, f"Status check failed: {portfolio_status_response.status_code}")
                return False
            
            portfolio_status = portfolio_status_response.json()
            
            metrics = {
                "portfolio_id": portfolio_id,
                "trades_executed": len(trades),
                "total_value": portfolio_status['portfolio'].get('total_value', 'unknown'),
                "position_count": len(portfolio_status['portfolio'].get('positions', []))
            }
            
            self.log_test("Portfolio Service Integration", True, 
                         f"Portfolio created and {len(trades)} trades executed successfully", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Portfolio Service Integration", False, f"Exception: {e}")
            return False
    
    def test_risk_service_integration(self) -> bool:
        """Test Risk Service integration with Portfolio data"""
        print("\\n=== RISK SERVICE INTEGRATION ===")
        
        if 'portfolio_id' not in self.test_data:
            self.log_test("Risk Service Integration", False, "No portfolio available for risk testing")
            return False
        
        try:
            portfolio_id = self.test_data['portfolio_id']
            
            # Test Sharpe ratio calculation
            sharpe_response = requests.post(
                f"{self.services['risk']}/api/risk/sharpe-ratio",
                params={"portfolio_id": portfolio_id, "risk_free_rate": 0.02},
                timeout=10
            )
            
            if sharpe_response.status_code != 200:
                self.log_test("Risk-Portfolio Integration", False, f"Sharpe calculation failed: {sharpe_response.status_code}")
                return False
            
            # Test drawdown calculation
            drawdown_response = requests.post(
                f"{self.services['risk']}/api/risk/drawdown",
                params={"portfolio_id": portfolio_id},
                timeout=10
            )
            
            if drawdown_response.status_code != 200:
                self.log_test("Risk Drawdown", False, f"Drawdown calculation failed: {drawdown_response.status_code}")
                return False
            
            # Test VaR calculation
            var_response = requests.post(
                f"{self.services['risk']}/api/risk/var",
                params={"portfolio_id": portfolio_id, "confidence_level": 0.95},
                timeout=10
            )
            
            if var_response.status_code != 200:
                self.log_test("Risk VaR", False, f"VaR calculation failed: {var_response.status_code}")
                return False
            
            # Test position sizing with ML predictions
            position_response = requests.post(
                f"{self.services['risk']}/api/risk/position-size",
                params={
                    "account_value": 100000,
                    "risk_per_trade": 0.02,
                    "entry_price": self.test_data['current_price'],
                    "stop_loss_price": self.test_data['current_price'] * 0.98,
                    "contract_size": 1000
                },
                timeout=10
            )
            
            if position_response.status_code != 200:
                self.log_test("Risk Position Sizing", False, f"Position sizing failed: {position_response.status_code}")
                return False
            
            # Get comprehensive risk summary
            summary_response = requests.get(
                f"{self.services['risk']}/api/risk/portfolio/{portfolio_id}/summary",
                timeout=10
            )
            
            if summary_response.status_code != 200:
                self.log_test("Risk Summary", False, f"Risk summary failed: {summary_response.status_code}")
                return False
            
            sharpe_data = sharpe_response.json()
            position_data = position_response.json()
            summary_data = summary_response.json()
            
            metrics = {
                "sharpe_ratio": sharpe_data.get('sharpe_ratio', 0),
                "position_size": position_data.get('position_size', 0),
                "risk_amount": position_data.get('risk_amount', 0),
                "portfolio_return": summary_data['portfolio_info'].get('total_return_pct', 0)
            }
            
            self.log_test("Risk Service Integration", True, 
                         "Risk service successfully integrated with portfolio data", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Risk Service Integration", False, f"Exception: {e}")
            return False
    
    def test_backtest_service_integration(self) -> bool:
        """Test Backtest Service integration with all other services"""
        print("\\n=== BACKTEST SERVICE INTEGRATION ===")
        
        try:
            # Test simple backtest creation
            backtest_response = requests.post(
                f"{self.services['backtest']}/api/backtests",
                params={
                    "name": "Week8_Integration_Backtest",
                    "description": "End-to-end integration test backtest",
                    "initial_capital": 100000,
                    "symbol": self.test_data['symbol']
                },
                timeout=10
            )
            
            if backtest_response.status_code not in [200, 201]:
                self.log_test("Backtest Creation", False, f"Backtest creation failed: {backtest_response.status_code}")
                return False
            
            backtest_data = backtest_response.json()
            backtest_id = backtest_data['backtest_id']
            
            # Get backtest status to verify integration
            status_response = requests.get(
                f"{self.services['backtest']}/api/backtests/{backtest_id}",
                timeout=10
            )
            
            if status_response.status_code != 200:
                self.log_test("Backtest Status", False, f"Status check failed: {status_response.status_code}")
                return False
            
            status_data = status_response.json()
            
            metrics = {
                "backtest_id": backtest_id,
                "status": status_data['backtest'].get('status', 'unknown'),
                "symbol": status_data['backtest'].get('symbol', 'unknown'),
                "initial_capital": status_data['backtest'].get('initial_capital', 0)
            }
            
            self.log_test("Backtest Service Integration", True, 
                         "Backtest service successfully integrated with system", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Backtest Service Integration", False, f"Exception: {e}")
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end trading workflow across all services"""
        print("\\n=== END-TO-END WORKFLOW TEST ===")
        
        try:
            workflow_start = time.time()
            
            # Step 1: Get market data (Data Service)
            print("  Step 1: Retrieving market data...")
            data_response = requests.get(
                f"{self.services['data']}/api/data/MCL",
                params={"limit": 30},
                timeout=10
            )
            
            if data_response.status_code != 200:
                self.log_test("E2E Workflow - Data", False, "Market data retrieval failed")
                return False
            
            # Step 2: Generate ML predictions (ML Service)
            print("  Step 2: Generating ML predictions...")
            prediction_response = requests.post(
                f"{self.services['ml']}/api/ml/predict",
                params={"symbol": "MCL", "days_back": 30},
                timeout=15
            )
            
            if prediction_response.status_code != 200:
                self.log_test("E2E Workflow - ML", False, "ML predictions failed")
                return False
            
            # Step 3: Generate trading signals (ML Service)
            print("  Step 3: Generating trading signals...")
            signals_response = requests.post(
                f"{self.services['ml']}/api/ml/signals",
                params={"symbol": "MCL", "days_back": 30},
                timeout=15
            )
            
            if signals_response.status_code != 200:
                self.log_test("E2E Workflow - Signals", False, "Signal generation failed")
                return False
            
            signals = signals_response.json()["signals"]
            current_signal = signals["current_signal"]
            
            # Step 4: Execute trades based on signals (Portfolio Service)
            print("  Step 4: Executing trades based on ML signals...")
            if 'portfolio_id' in self.test_data and current_signal in ["BUY", "SELL"]:
                action = current_signal
                trade_response = requests.post(
                    f"{self.services['portfolio']}/api/portfolio/{self.test_data['portfolio_id']}/trade",
                    params={
                        "symbol": "MCL",
                        "action": action,
                        "quantity": 1,
                        "price": self.test_data.get('current_price', 67.50)
                    },
                    timeout=10
                )
                
                trade_executed = trade_response.status_code in [200, 201]
            else:
                trade_executed = True  # HOLD signal or no portfolio
                print("    Signal is HOLD or no portfolio - no trade executed")
            
            # Step 5: Calculate risk metrics (Risk Service)
            print("  Step 5: Calculating risk metrics...")
            if 'portfolio_id' in self.test_data:
                risk_response = requests.get(
                    f"{self.services['risk']}/api/risk/portfolio/{self.test_data['portfolio_id']}/summary",
                    timeout=10
                )
                risk_calculated = risk_response.status_code == 200
            else:
                # Test position sizing instead
                position_response = requests.post(
                    f"{self.services['risk']}/api/risk/position-size",
                    params={
                        "account_value": 100000,
                        "risk_per_trade": 0.02,
                        "entry_price": 67.50,
                        "stop_loss_price": 66.50,
                        "contract_size": 1000
                    },
                    timeout=10
                )
                risk_calculated = position_response.status_code == 200
            
            workflow_time = time.time() - workflow_start
            
            if not trade_executed or not risk_calculated:
                self.log_test("E2E Workflow", False, "Workflow incomplete")
                return False
            
            metrics = {
                "workflow_time_seconds": round(workflow_time, 2),
                "services_integrated": 5,
                "ml_signal": current_signal,
                "trade_executed": trade_executed,
                "risk_calculated": risk_calculated
            }
            
            self.log_test("End-to-End Workflow", True, 
                         f"Complete trading workflow executed successfully in {workflow_time:.2f}s", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("End-to-End Workflow", False, f"Exception: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test portfolios"""
        try:
            if 'portfolio_id' in self.test_data:
                requests.delete(f"{self.services['portfolio']}/api/portfolio/{self.test_data['portfolio_id']}", timeout=5)
        except:
            pass
    
    def run_integration_tests(self) -> Dict:
        """Run complete Week 8 integration test suite"""
        print("=" * 80)
        print("WEEK 8 SERVICE INTEGRATION - COMPREHENSIVE TESTING")
        print("=" * 80)
        print(f"Test start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("Testing all services working together per CLAUDE.md requirements")
        print()
        
        # Run all integration tests
        test_functions = [
            self.check_service_health,
            self.test_data_service_integration,
            self.test_ml_service_integration,
            self.test_portfolio_service_integration,
            self.test_risk_service_integration,
            self.test_backtest_service_integration,
            self.test_end_to_end_workflow
        ]
        
        for test_func in test_functions:
            if not test_func():
                break  # Stop on first failure
        
        # Cleanup
        self.cleanup_test_data()
        
        # Calculate results
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        total_tests = len(self.test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print("\\n" + "=" * 80)
        print("INTEGRATION TEST RESULTS")
        print("=" * 80)
        
        for result in self.test_results:
            print(f"[{result['timestamp']}] {result['status']} - {result['test']}")
            if result['details']:
                print(f"    {result['details']}")
            if result['metrics']:
                for key, value in result['metrics'].items():
                    print(f"    {key}: {value}")
        
        print()
        print("-" * 80)
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success_rate == 100.0:
            print("STATUS: ✅ INTEGRATION COMPLETE - All services working together!")
            status = "SUCCESS"
        else:
            print("STATUS: ❌ INTEGRATION ISSUES - Some services not properly integrated")
            status = "FAILURE"
        
        print("=" * 80)
        
        return {
            "status": status,
            "passed": passed_tests,
            "total": total_tests,
            "success_rate": success_rate,
            "duration_seconds": duration,
            "test_results": self.test_results
        }

def main():
    """Main integration test function"""
    tester = Week8IntegrationTester()
    results = tester.run_integration_tests()
    
    # Exit with appropriate code per CLAUDE.md requirements
    if results["status"] == "SUCCESS":
        print("\\n✅ Week 8 Service Integration is 100% successful!")
        sys.exit(0)
    else:
        print(f"\\n❌ Week 8 integration failed - {results['success_rate']:.1f}% success rate")
        sys.exit(1)

if __name__ == "__main__":
    main()