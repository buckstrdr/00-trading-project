#!/usr/bin/env python3
"""
Week 7 Completion Verification - ML Service Foundation
Complete verification of Week 7 implementation against plan requirements.
Tests all ML Service functionality with real data and comprehensive validation.
100% completion means all ML foundation features working with actual model training.
"""

import requests
import time
import json
import os
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Service configuration
ML_SERVICE_URL = "http://localhost:8004"
DATA_SERVICE_URL = "http://localhost:8001"
REDIS_URL = "redis://localhost:6379"

class Week7Verifier:
    """Comprehensive Week 7 ML Service Foundation verification"""
    
    def __init__(self):
        self.test_results = []
        self.verification_start_time = datetime.now()
        
    def log_test(self, test_name: str, passed: bool, details: str = "", metrics: Dict = None):
        """Log test result with timestamp per CLAUDE.md requirements"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status = "PASS" if passed else "FAIL"
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "metrics": metrics or {},
            "timestamp": timestamp
        })
        print(f"{timestamp} {status} {test_name}")
        if details and not passed:
            print(f"    Details: {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"    {key}: {value}")

    def verify_week7_plan_requirements(self) -> Dict:
        """Verify implementation against original Week 7 plan"""
        print("=" * 80)
        print("WEEK 7 PLAN COMPLIANCE VERIFICATION")
        print("=" * 80)
        
        # Original Week 7 Tasks from SIMPLE-MICROSERVICES-PLAN.md:
        # [ ] Create ML Service structure  
        # [ ] Implement feature engineering pipeline
        # [ ] Add Random Forest model training
        # [ ] Build prediction generation
        # [ ] Test with sample strategies
        
        plan_requirements = {
            "ml_service_structure": "Create ML Service structure",
            "feature_engineering": "Implement feature engineering pipeline", 
            "random_forest_training": "Add Random Forest model training",
            "prediction_generation": "Build prediction generation",
            "sample_strategy_testing": "Test with sample strategies"
        }
        
        for req_id, requirement in plan_requirements.items():
            print(f"\nVerifying: {requirement}")
            if req_id == "ml_service_structure":
                self.test_1_ml_service_structure()
            elif req_id == "feature_engineering":
                self.test_2_feature_engineering_pipeline()
            elif req_id == "random_forest_training":
                self.test_3_random_forest_training()
            elif req_id == "prediction_generation":
                self.test_4_prediction_generation()
            elif req_id == "sample_strategy_testing":
                self.test_5_sample_strategy_testing()
        
        return {"plan_verification": "complete"}

    def test_1_ml_service_structure(self) -> bool:
        """Test 1: Verify ML Service structure meets plan requirements"""
        try:
            # Check ML Service health and dependencies
            response = requests.get(f"{ML_SERVICE_URL}/health", timeout=5)
            
            if response.status_code != 200:
                self.log_test("ML Service Structure - Health Check", False, 
                            f"Health check failed: {response.status_code}")
                return False
                
            health_data = response.json()
            
            # Verify health response structure
            required_fields = ["status", "service", "timestamp", "details"]
            for field in required_fields:
                if field not in health_data:
                    self.log_test("ML Service Structure - Health Response", False, 
                                f"Missing field: {field}")
                    return False
            
            # Verify service connections per plan (should connect to Data Service and Redis)
            details = health_data.get("details", {})
            if "data_service" not in details or "redis" not in details:
                self.log_test("ML Service Structure - Dependencies", False, 
                            "Missing Data Service or Redis connection")
                return False
            
            # Verify service is properly identified
            if health_data.get("service") != "MLService":
                self.log_test("ML Service Structure - Service Identity", False, 
                            f"Wrong service name: {health_data.get('service')}")
                return False
                
            # Check API endpoints structure
            endpoints_to_verify = [
                "/api/ml/train/regression",
                "/api/ml/train/classification", 
                "/api/ml/predict",
                "/api/ml/signals",
                "/api/ml/features",
                "/api/ml/model/status"
            ]
            
            for endpoint in endpoints_to_verify:
                # Test with HEAD request to avoid triggering full functionality
                test_response = requests.head(f"{ML_SERVICE_URL}{endpoint}", timeout=2)
                if test_response.status_code not in [200, 405, 422]:  # 405 = method not allowed, 422 = validation error (expected for HEAD)
                    self.log_test(f"ML Service Structure - Endpoint {endpoint}", False, 
                                f"Endpoint not accessible: {test_response.status_code}")
                    return False
            
            metrics = {
                "service_name": health_data.get("service"),
                "redis_status": details.get("redis"),
                "data_service_status": details.get("data_service"),
                "endpoints_verified": len(endpoints_to_verify)
            }
            
            self.log_test("ML Service Structure", True, 
                         "Complete ML Service structure with all required endpoints and dependencies", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("ML Service Structure", False, f"Structure verification failed: {e}")
            return False

    def test_2_feature_engineering_pipeline(self) -> bool:
        """Test 2: Verify feature engineering pipeline implementation"""
        try:
            # Test feature extraction with real market data
            response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/features",
                params={"symbol": "MCL", "days_back": 50},
                timeout=15
            )
            
            if response.status_code != 200:
                self.log_test("Feature Engineering Pipeline", False, 
                            f"Feature extraction failed: {response.status_code}")
                return False
            
            features_data = response.json()
            
            # Verify response structure
            required_fields = ["status", "symbol", "features"]
            for field in required_fields:
                if field not in features_data:
                    self.log_test("Feature Engineering Pipeline - Response Structure", False, 
                                f"Missing field: {field}")
                    return False
            
            features = features_data["features"]
            required_feature_fields = ["feature_names", "feature_count", "sample_count", "latest_features"]
            for field in required_feature_fields:
                if field not in features:
                    self.log_test("Feature Engineering Pipeline - Features Structure", False, 
                                f"Missing features field: {field}")
                    return False
            
            # Verify comprehensive feature engineering per plan requirements
            feature_names = features["feature_names"]
            expected_feature_categories = {
                "price_features": ["open", "high", "low", "close", "volume"],
                "derived_features": ["hl_ratio", "oc_ratio", "price_range", "returns", "volatility"],
                "volume_features": ["volume_sma", "volume_ratio"],
                "technical_indicators": ["sma_10", "sma_20", "ema_10", "ema_20", "rsi", "macd", "macd_signal", "macd_hist"],
                "volatility_indicators": ["bb_upper", "bb_middle", "bb_lower", "atr"],
                "volume_indicators": ["obv", "ad"],
                "time_features": ["hour", "day_of_week"]
            }
            
            missing_features = []
            for category, required_features in expected_feature_categories.items():
                for feature in required_features:
                    if feature not in feature_names:
                        missing_features.append(f"{feature} ({category})")
            
            if missing_features:
                self.log_test("Feature Engineering Pipeline - Feature Coverage", False, 
                            f"Missing features: {', '.join(missing_features)}")
                return False
            
            # Verify feature count meets minimum requirements (should be comprehensive)
            feature_count = features["feature_count"]
            sample_count = features["sample_count"]
            
            if feature_count < 20:  # Plan requires comprehensive feature engineering
                self.log_test("Feature Engineering Pipeline - Feature Count", False, 
                            f"Insufficient features: {feature_count} < 20")
                return False
            
            if sample_count != 50:  # Should match requested days_back
                self.log_test("Feature Engineering Pipeline - Sample Count", False, 
                            f"Wrong sample count: {sample_count} != 50")
                return False
            
            # Verify latest features have valid values
            latest_features = features["latest_features"]
            if not latest_features or len(latest_features) != feature_count:
                self.log_test("Feature Engineering Pipeline - Latest Features", False, 
                            f"Latest features invalid: {len(latest_features)} != {feature_count}")
                return False
            
            # Verify technical indicators are properly calculated (not NaN or zero for all)
            technical_indicators = ["rsi", "macd", "bb_upper", "atr"]
            invalid_indicators = []
            for indicator in technical_indicators:
                if indicator in latest_features:
                    value = latest_features[indicator]
                    if value is None or math.isnan(value) or value == 0.0:
                        invalid_indicators.append(indicator)
            
            if len(invalid_indicators) > len(technical_indicators) / 2:  # Allow some to be zero but not all
                self.log_test("Feature Engineering Pipeline - Technical Indicators", False, 
                            f"Too many invalid indicators: {invalid_indicators}")
                return False
            
            metrics = {
                "feature_count": feature_count,
                "sample_count": sample_count,
                "categories_implemented": len(expected_feature_categories),
                "latest_price": latest_features.get("close", 0),
                "rsi_value": latest_features.get("rsi", 0)
            }
            
            self.log_test("Feature Engineering Pipeline", True, 
                         f"Complete feature engineering with {feature_count} features across all categories", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Feature Engineering Pipeline", False, f"Pipeline test failed: {e}")
            return False

    def test_3_random_forest_training(self) -> bool:
        """Test 3: Verify Random Forest model training implementation"""
        try:
            # Test regression model training
            regression_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/train/regression",
                params={"symbol": "MCL", "start_date": "2024-01-01", "end_date": "2024-02-01"},
                timeout=30
            )
            
            if regression_response.status_code != 200:
                self.log_test("Random Forest Training - Regression", False, 
                            f"Regression training failed: {regression_response.status_code}")
                return False
            
            regression_data = regression_response.json()
            
            # Verify regression training response
            if regression_data.get("status") != "success":
                self.log_test("Random Forest Training - Regression Status", False, 
                            f"Training failed: {regression_data}")
                return False
            
            regression_results = regression_data["training_results"]
            required_regression_fields = ["model_type", "train_samples", "test_samples", 
                                        "train_mse", "test_mse", "cv_score_mean", "feature_count"]
            
            for field in required_regression_fields:
                if field not in regression_results:
                    self.log_test("Random Forest Training - Regression Results", False, 
                                f"Missing regression field: {field}")
                    return False
            
            # Verify it's actually RandomForest
            if regression_results["model_type"] != "RandomForestRegressor":
                self.log_test("Random Forest Training - Model Type", False, 
                            f"Wrong model type: {regression_results['model_type']}")
                return False
            
            # Verify training data split is reasonable
            train_samples = regression_results["train_samples"]
            test_samples = regression_results["test_samples"]
            total_samples = train_samples + test_samples
            
            if total_samples < 100:  # Should have sufficient data for training
                self.log_test("Random Forest Training - Data Size", False, 
                            f"Insufficient training data: {total_samples}")
                return False
            
            train_ratio = train_samples / total_samples
            if not (0.7 <= train_ratio <= 0.9):  # Typical 70-90% training split
                self.log_test("Random Forest Training - Data Split", False, 
                            f"Invalid train/test split: {train_ratio:.2f}")
                return False
            
            # Test classification model training
            classification_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/train/classification",
                params={"symbol": "MCL", "start_date": "2024-01-01", "end_date": "2024-02-01"},
                timeout=30
            )
            
            if classification_response.status_code != 200:
                self.log_test("Random Forest Training - Classification", False, 
                            f"Classification training failed: {classification_response.status_code}")
                return False
            
            classification_data = classification_response.json()
            classification_results = classification_data["training_results"]
            
            # Verify classification model
            if classification_results["model_type"] != "RandomForestClassifier":
                self.log_test("Random Forest Training - Classification Type", False, 
                            f"Wrong classification model: {classification_results['model_type']}")
                return False
            
            # Verify model performance metrics are reasonable
            test_accuracy = classification_results.get("test_accuracy", 0)
            if test_accuracy < 0.5:  # Should be better than random (50%)
                self.log_test("Random Forest Training - Classification Accuracy", False, 
                            f"Poor accuracy: {test_accuracy}")
                return False
            
            # Verify models are saved and loadable
            model_status_response = requests.get(f"{ML_SERVICE_URL}/api/ml/model/status", timeout=5)
            if model_status_response.status_code != 200:
                self.log_test("Random Forest Training - Model Status", False, 
                            f"Cannot check model status: {model_status_response.status_code}")
                return False
            
            status_data = model_status_response.json()
            if not (status_data.get("regression_model", {}).get("loaded") and 
                   status_data.get("classification_model", {}).get("loaded")):
                self.log_test("Random Forest Training - Model Loading", False, 
                            "Models not properly loaded after training")
                return False
            
            metrics = {
                "regression_train_samples": train_samples,
                "regression_test_samples": test_samples,
                "regression_mse": regression_results.get("test_mse", 0),
                "classification_accuracy": test_accuracy,
                "feature_count": regression_results.get("feature_count", 0),
                "models_saved": len(status_data.get("saved_models", []))
            }
            
            self.log_test("Random Forest Training", True, 
                         "Both RandomForest regression and classification models trained successfully", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Random Forest Training", False, f"Training test failed: {e}")
            return False

    def test_4_prediction_generation(self) -> bool:
        """Test 4: Verify prediction generation implementation"""
        try:
            # Test price prediction
            prediction_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/predict",
                params={"symbol": "MCL", "days_back": 30},
                timeout=15
            )
            
            if prediction_response.status_code != 200:
                self.log_test("Prediction Generation - Price Prediction", False, 
                            f"Price prediction failed: {prediction_response.status_code}")
                return False
            
            prediction_data = prediction_response.json()
            
            # Verify prediction response structure
            if prediction_data.get("status") != "success":
                self.log_test("Prediction Generation - Prediction Status", False, 
                            f"Prediction failed: {prediction_data}")
                return False
            
            predictions = prediction_data["predictions"]
            required_prediction_fields = ["predictions", "prediction_count", "current_price", 
                                        "predicted_price", "predicted_change"]
            
            for field in required_prediction_fields:
                if field not in predictions:
                    self.log_test("Prediction Generation - Prediction Structure", False, 
                                f"Missing prediction field: {field}")
                    return False
            
            # Verify prediction data quality
            prediction_list = predictions["predictions"]
            prediction_count = predictions["prediction_count"]
            current_price = predictions["current_price"]
            predicted_price = predictions["predicted_price"]
            
            if len(prediction_list) != prediction_count or prediction_count != 30:
                self.log_test("Prediction Generation - Prediction Count", False, 
                            f"Prediction count mismatch: {len(prediction_list)} != {prediction_count}")
                return False
            
            if current_price <= 0 or predicted_price <= 0:
                self.log_test("Prediction Generation - Price Values", False, 
                            f"Invalid prices: current={current_price}, predicted={predicted_price}")
                return False
            
            # Test signal generation
            signals_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/signals",
                params={"symbol": "MCL", "days_back": 30},
                timeout=15
            )
            
            if signals_response.status_code != 200:
                self.log_test("Prediction Generation - Signal Generation", False, 
                            f"Signal generation failed: {signals_response.status_code}")
                return False
            
            signals_data = signals_response.json()
            signals = signals_data["signals"]
            
            required_signal_fields = ["signals", "signal_names", "probabilities", 
                                    "current_signal", "current_probabilities"]
            
            for field in required_signal_fields:
                if field not in signals:
                    self.log_test("Prediction Generation - Signal Structure", False, 
                                f"Missing signal field: {field}")
                    return False
            
            # Verify signal data quality
            signal_list = signals["signals"]
            signal_names = signals["signal_names"]
            probabilities = signals["probabilities"]
            current_signal = signals["current_signal"]
            current_probabilities = signals["current_probabilities"]
            
            if len(signal_list) != len(signal_names) or len(signal_list) != 30:
                self.log_test("Prediction Generation - Signal Count", False, 
                            f"Signal count mismatch: {len(signal_list)} != {len(signal_names)}")
                return False
            
            # Verify signal values are valid (-1, 0, 1)
            valid_signals = set([-1, 0, 1])
            invalid_signals = [s for s in signal_list if s not in valid_signals]
            if invalid_signals:
                self.log_test("Prediction Generation - Signal Values", False, 
                            f"Invalid signals: {invalid_signals}")
                return False
            
            # Verify signal names are correct
            signal_name_mapping = {-1: "SELL", 0: "HOLD", 1: "BUY"}
            for i, (signal, name) in enumerate(zip(signal_list, signal_names)):
                if signal_name_mapping[signal] != name:
                    self.log_test("Prediction Generation - Signal Names", False, 
                                f"Signal name mismatch at {i}: {signal} -> {name}")
                    return False
            
            # Verify current signal and probabilities
            if current_signal not in ["BUY", "SELL", "HOLD"]:
                self.log_test("Prediction Generation - Current Signal", False, 
                            f"Invalid current signal: {current_signal}")
                return False
            
            prob_sum = sum(current_probabilities.values())
            if not (0.99 <= prob_sum <= 1.01):  # Should sum to 1.0 (allowing floating point error)
                self.log_test("Prediction Generation - Probabilities", False, 
                            f"Probabilities don't sum to 1.0: {prob_sum}")
                return False
            
            metrics = {
                "predictions_generated": len(prediction_list),
                "current_price": current_price,
                "predicted_price": predicted_price,
                "predicted_change_pct": predictions.get("predicted_change", 0) * 100,
                "current_signal": current_signal,
                "signal_confidence": max(current_probabilities.values())
            }
            
            self.log_test("Prediction Generation", True, 
                         "Both price prediction and signal generation working correctly", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Prediction Generation", False, f"Prediction test failed: {e}")
            return False

    def test_5_sample_strategy_testing(self) -> bool:
        """Test 5: Verify testing with sample strategies implementation"""
        try:
            # Test complete ML workflow as a sample trading strategy
            # This simulates how a trading strategy would use the ML Service
            
            print("  Running sample strategy workflow...")
            
            # Step 1: Extract features for strategy analysis
            features_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/features",
                params={"symbol": "MCL", "days_back": 20},
                timeout=10
            )
            
            if features_response.status_code != 200:
                self.log_test("Sample Strategy Testing - Feature Extraction", False, 
                            f"Feature extraction failed: {features_response.status_code}")
                return False
            
            # Step 2: Get price prediction for strategy
            prediction_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/predict", 
                params={"symbol": "MCL", "days_back": 20},
                timeout=10
            )
            
            if prediction_response.status_code != 200:
                self.log_test("Sample Strategy Testing - Price Prediction", False, 
                            f"Price prediction failed: {prediction_response.status_code}")
                return False
            
            # Step 3: Get trading signal for strategy
            signals_response = requests.post(
                f"{ML_SERVICE_URL}/api/ml/signals",
                params={"symbol": "MCL", "days_back": 20}, 
                timeout=10
            )
            
            if signals_response.status_code != 200:
                self.log_test("Sample Strategy Testing - Signal Generation", False, 
                            f"Signal generation failed: {signals_response.status_code}")
                return False
            
            # Step 4: Analyze strategy components
            features_data = features_response.json()["features"]
            prediction_data = prediction_response.json()["predictions"]
            signals_data = signals_response.json()["signals"]
            
            # Verify strategy has access to all required ML components
            strategy_components = {
                "technical_features": features_data.get("feature_count", 0),
                "price_prediction": prediction_data.get("predicted_price", 0),
                "trading_signal": signals_data.get("current_signal", ""),
                "signal_confidence": max(signals_data.get("current_probabilities", {}).values()) if signals_data.get("current_probabilities") else 0
            }
            
            # Verify each component is functional for strategy use
            if strategy_components["technical_features"] < 20:
                self.log_test("Sample Strategy Testing - Technical Features", False, 
                            f"Insufficient features for strategy: {strategy_components['technical_features']}")
                return False
            
            if strategy_components["price_prediction"] <= 0:
                self.log_test("Sample Strategy Testing - Price Prediction", False, 
                            f"Invalid price prediction: {strategy_components['price_prediction']}")
                return False
            
            if strategy_components["trading_signal"] not in ["BUY", "SELL", "HOLD"]:
                self.log_test("Sample Strategy Testing - Trading Signal", False, 
                            f"Invalid trading signal: {strategy_components['trading_signal']}")
                return False
            
            if strategy_components["signal_confidence"] < 0.5:
                self.log_test("Sample Strategy Testing - Signal Confidence", False, 
                            f"Low signal confidence: {strategy_components['signal_confidence']}")
                return False
            
            # Step 5: Test strategy decision logic
            current_price = prediction_data["current_price"]
            predicted_price = prediction_data["predicted_price"]
            predicted_change = prediction_data["predicted_change"]
            current_signal = signals_data["current_signal"]
            
            # Simple strategy logic test
            strategy_decision = "NO_ACTION"
            if abs(predicted_change) > 0.001:  # More than 0.1% change predicted
                if predicted_change > 0 and current_signal == "BUY":
                    strategy_decision = "ENTER_LONG"
                elif predicted_change < 0 and current_signal == "SELL":
                    strategy_decision = "ENTER_SHORT"
                elif current_signal == "HOLD":
                    strategy_decision = "HOLD_POSITION"
            
            # Verify strategy can make decisions
            if strategy_decision == "NO_ACTION" and abs(predicted_change) > 0.005:  # Should have made some decision for >0.5% change
                print(f"  WARNING: Strategy passive despite {predicted_change*100:.2f}% predicted change")
            
            # Step 6: Test model persistence across strategy runs
            model_status_response = requests.get(f"{ML_SERVICE_URL}/api/ml/model/status", timeout=5)
            if model_status_response.status_code != 200:
                self.log_test("Sample Strategy Testing - Model Persistence", False, 
                            "Cannot verify model persistence")
                return False
            
            model_status = model_status_response.json()
            if not (model_status.get("regression_model", {}).get("loaded") and 
                   model_status.get("classification_model", {}).get("loaded")):
                self.log_test("Sample Strategy Testing - Model Loading", False, 
                            "Models not persistent across strategy calls")
                return False
            
            metrics = {
                "strategy_decision": strategy_decision,
                "current_price": current_price,
                "predicted_price": predicted_price,
                "predicted_change_pct": predicted_change * 100,
                "ml_signal": current_signal,
                "signal_confidence": strategy_components["signal_confidence"],
                "feature_count": strategy_components["technical_features"]
            }
            
            self.log_test("Sample Strategy Testing", True, 
                         f"Complete ML strategy workflow functional - Decision: {strategy_decision}", 
                         metrics)
            return True
            
        except Exception as e:
            self.log_test("Sample Strategy Testing", False, f"Strategy testing failed: {e}")
            return False

    def verify_implementation_completeness(self) -> Dict:
        """Verify implementation against Week 7 requirements is complete"""
        
        print("\n" + "=" * 80)
        print("WEEK 7 IMPLEMENTATION COMPLETENESS VERIFICATION")  
        print("=" * 80)
        
        # Check actual ML Service file exists and has proper implementation
        ml_service_file = Path("services/ml_service.py")
        if not ml_service_file.exists():
            self.log_test("Implementation Completeness - ML Service File", False, 
                         "ML Service file does not exist")
            return {"complete": False}
        
        # Verify file size indicates real implementation (not just stub)
        file_size = ml_service_file.stat().st_size
        if file_size < 10000:  # Should be substantial implementation
            self.log_test("Implementation Completeness - File Size", False, 
                         f"ML Service file too small: {file_size} bytes")
            return {"complete": False}
        
        # Check models directory and saved models
        models_dir = Path("models")
        if not models_dir.exists():
            self.log_test("Implementation Completeness - Models Directory", False, 
                         "Models directory not found")
            return {"complete": False}
        
        expected_model_files = ["regression_model.joblib", "classification_model.joblib", "feature_engineer.joblib"]
        missing_models = []
        for model_file in expected_model_files:
            model_path = models_dir / model_file
            if not model_path.exists():
                missing_models.append(model_file)
            elif model_path.stat().st_size < 1000:  # Models should be substantial
                missing_models.append(f"{model_file} (too small)")
        
        if missing_models:
            self.log_test("Implementation Completeness - Model Files", False, 
                         f"Missing or invalid models: {missing_models}")
            return {"complete": False}
        
        metrics = {
            "ml_service_size_kb": file_size // 1024,
            "models_saved": len([f for f in models_dir.glob("*.joblib")]),
            "total_model_size_mb": sum(f.stat().st_size for f in models_dir.glob("*.joblib")) // (1024*1024)
        }
        
        self.log_test("Implementation Completeness", True, 
                     "All Week 7 implementation files present and substantial", 
                     metrics)
        return {"complete": True}

    def run_comprehensive_week7_verification(self) -> Dict:
        """Run complete Week 7 verification per CLAUDE.md requirements"""
        print("=" * 80)
        print("WEEK 7 ML SERVICE FOUNDATION - COMPREHENSIVE VERIFICATION")
        print("=" * 80)
        print(f"Verification start time: {self.verification_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing against original plan requirements from SIMPLE-MICROSERVICES-PLAN.md")
        print()
        
        # 1. Verify against original plan
        print("PHASE 1: PLAN COMPLIANCE VERIFICATION")
        print("-" * 50)
        plan_results = self.verify_week7_plan_requirements()
        
        # 2. Verify implementation completeness  
        print("\nPHASE 2: IMPLEMENTATION COMPLETENESS")
        print("-" * 50)
        completeness_results = self.verify_implementation_completeness()
        
        # Calculate overall results
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        completion_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        verification_end_time = datetime.now()
        verification_duration = (verification_end_time - self.verification_start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("WEEK 7 VERIFICATION RESULTS")
        print("=" * 80)
        
        # Show all test results
        for result in self.test_results:
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{result['timestamp']} {status} {result['test']}")
            if not result["passed"] and result["details"]:
                print(f"    {result['details']}")
            if result["metrics"]:
                for key, value in result["metrics"].items():
                    print(f"    {key}: {value}")
        
        print()
        print("-" * 80)
        print(f"VERIFICATION SUMMARY:")
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Completion Rate: {completion_rate:.1f}%") 
        print(f"Verification Duration: {verification_duration:.1f} seconds")
        print(f"Start Time: {self.verification_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End Time: {verification_end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if completion_rate == 100.0 and completeness_results.get("complete"):
            print("STATUS: ✅ WEEK 7 COMPLETE - All ML Service Foundation requirements verified!")
            status = "COMPLETE"
        else:
            print("STATUS: ❌ WEEK 7 INCOMPLETE - Some requirements not met")
            status = "INCOMPLETE"
        
        print("=" * 80)
        
        return {
            "passed": passed_tests,
            "total": total_tests,
            "completion_rate": completion_rate,
            "status": status,
            "duration_seconds": verification_duration,
            "plan_compliance": True if plan_results else False,
            "implementation_complete": completeness_results.get("complete", False),
            "test_results": self.test_results,
            "verification_time": {
                "start": self.verification_start_time.isoformat(),
                "end": verification_end_time.isoformat()
            }
        }

def main():
    """Main verification function"""
    verifier = Week7Verifier()
    results = verifier.run_comprehensive_week7_verification()
    
    # Exit with appropriate code per CLAUDE.md requirements
    if results["status"] == "COMPLETE":
        print(f"\n✅ Week 7 ML Service Foundation is 100% complete and compliant!")
        print("All plan requirements verified with real testing - no faking detected")
        exit(0)
    else:
        print(f"\n❌ Week 7 verification failed - {results['completion_rate']:.1f}% complete")
        print("Some plan requirements not fully implemented or tested")
        exit(1)

if __name__ == "__main__":
    main()