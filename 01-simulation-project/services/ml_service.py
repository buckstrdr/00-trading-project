#!/usr/bin/env python3
"""
ML Service - Week 7 Implementation
Provides machine learning capabilities including feature engineering, model training,
prediction generation, and trading signal creation for futures backtesting.
"""

import sys
import math
import requests
import pandas as pd
import numpy as np
import talib
import joblib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

# ML imports
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, accuracy_score
import xgboost as xgb

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from shared.utils import setup_logging
from shared.models import HealthResponse, ServiceStatus
from shared.redis_client import redis_client
from config.settings import SERVICE_PORTS

# Initialize logging
logger = setup_logging("MLService", "INFO")

app = FastAPI(
    title="ML Service",
    description="Machine learning models and predictions for futures trading",
    version="1.0.0"
)

class FeatureEngineer:
    """Feature engineering pipeline for financial time series data"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.fitted = False
        
    def calculate_returns(self, prices: pd.Series) -> pd.Series:
        """Calculate percentage returns"""
        return prices.pct_change().fillna(0)
    
    def calculate_volatility(self, returns: pd.Series, window: int = 20) -> pd.Series:
        """Calculate rolling volatility"""
        return returns.rolling(window=window).std().fillna(0)
    
    def calculate_technical_indicators(self, high: np.array, low: np.array, 
                                     close: np.array, volume: np.array) -> Dict:
        """Calculate technical indicators using talib"""
        indicators = {}
        
        # Moving averages
        indicators['sma_10'] = talib.SMA(close, timeperiod=10)
        indicators['sma_20'] = talib.SMA(close, timeperiod=20)
        indicators['ema_10'] = talib.EMA(close, timeperiod=10)
        indicators['ema_20'] = talib.EMA(close, timeperiod=20)
        
        # Momentum indicators
        indicators['rsi'] = talib.RSI(close, timeperiod=14)
        indicators['macd'], indicators['macd_signal'], indicators['macd_hist'] = talib.MACD(close)
        
        # Volatility indicators
        indicators['bb_upper'], indicators['bb_middle'], indicators['bb_lower'] = talib.BBANDS(close)
        indicators['atr'] = talib.ATR(high, low, close, timeperiod=14)
        
        # Volume indicators
        indicators['obv'] = talib.OBV(close, volume)
        indicators['ad'] = talib.AD(high, low, close, volume)
        
        return indicators
    
    def create_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create feature matrix from OHLCV data"""
        features = pd.DataFrame(index=data.index)
        
        # Price features
        features['open'] = data['open']
        features['high'] = data['high']
        features['low'] = data['low'] 
        features['close'] = data['close']
        features['volume'] = data['volume']
        
        # Derived price features
        features['hl_ratio'] = data['high'] / data['low']
        features['oc_ratio'] = data['open'] / data['close']
        features['price_range'] = (data['high'] - data['low']) / data['close']
        
        # Returns and volatility
        features['returns'] = self.calculate_returns(data['close'])
        features['volatility'] = self.calculate_volatility(features['returns'])
        
        # Volume features
        features['volume_sma'] = data['volume'].rolling(window=20).mean()
        features['volume_ratio'] = data['volume'] / features['volume_sma']
        
        # Technical indicators
        if len(data) >= 20:  # Need minimum data for indicators
            indicators = self.calculate_technical_indicators(
                data['high'].values.astype(np.float64),
                data['low'].values.astype(np.float64), 
                data['close'].values.astype(np.float64),
                data['volume'].values.astype(np.float64)
            )
            
            for name, values in indicators.items():
                features[name] = values
        
        # Time features
        features['hour'] = data.index.hour if hasattr(data.index, 'hour') else 0
        features['day_of_week'] = data.index.dayofweek if hasattr(data.index, 'dayofweek') else 0
        
        # Forward fill NaN values
        features = features.fillna(method='ffill').fillna(0)
        
        return features
    
    def fit_scaler(self, features: pd.DataFrame):
        """Fit the scaler to features"""
        numeric_features = features.select_dtypes(include=[np.number])
        self.scaler.fit(numeric_features)
        self.fitted = True
    
    def transform_features(self, features: pd.DataFrame) -> np.array:
        """Scale features using fitted scaler"""
        if not self.fitted:
            raise ValueError("Scaler not fitted. Call fit_scaler first.")
        
        numeric_features = features.select_dtypes(include=[np.number])
        return self.scaler.transform(numeric_features)

class MLModelManager:
    """Machine learning model training and prediction manager"""
    
    def __init__(self):
        self.regression_model = None
        self.classification_model = None
        self.feature_engineer = FeatureEngineer()
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        
    def prepare_regression_target(self, data: pd.DataFrame, lookahead: int = 1) -> pd.Series:
        """Prepare target variable for regression (future price)"""
        return data['close'].shift(-lookahead)
    
    def prepare_classification_target(self, data: pd.DataFrame, lookahead: int = 1, 
                                   threshold: float = 0.002) -> pd.Series:
        """Prepare target variable for classification (signal)"""
        future_returns = data['close'].pct_change(lookahead).shift(-lookahead)
        
        # Create signals: 1=BUY, 0=HOLD, -1=SELL
        signals = pd.Series(0, index=data.index)
        signals[future_returns > threshold] = 1
        signals[future_returns < -threshold] = -1
        
        return signals
    
    def train_regression_model(self, data: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """Train Random Forest regression model"""
        logger.info("Training regression model...")
        
        # Create features and target
        features = self.feature_engineer.create_features(data)
        target = self.prepare_regression_target(data)
        
        # Remove rows with NaN target
        valid_idx = ~target.isna()
        features = features[valid_idx]
        target = target[valid_idx]
        
        if len(features) < 50:
            raise ValueError("Insufficient data for training (need at least 50 samples)")
        
        # Fit scaler
        self.feature_engineer.fit_scaler(features)
        
        # Scale features
        X = self.feature_engineer.transform_features(features)
        y = target.values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )
        
        # Train Random Forest
        self.regression_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.regression_model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.regression_model.predict(X_train)
        test_pred = self.regression_model.predict(X_test)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        
        # Cross validation
        cv_scores = cross_val_score(self.regression_model, X, y, cv=5, 
                                  scoring='neg_mean_squared_error')
        
        results = {
            "model_type": "RandomForestRegressor",
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_mse": float(train_mse),
            "test_mse": float(test_mse),
            "cv_score_mean": float(-cv_scores.mean()),
            "cv_score_std": float(cv_scores.std()),
            "feature_count": X.shape[1],
            "trained_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Regression model trained: MSE={test_mse:.6f}")
        return results
    
    def train_classification_model(self, data: pd.DataFrame, test_size: float = 0.2) -> Dict:
        """Train Random Forest classification model"""
        logger.info("Training classification model...")
        
        # Create features and target
        features = self.feature_engineer.create_features(data)
        target = self.prepare_classification_target(data)
        
        # Remove rows with NaN target
        valid_idx = ~target.isna()
        features = features[valid_idx]
        target = target[valid_idx]
        
        if len(features) < 50:
            raise ValueError("Insufficient data for training (need at least 50 samples)")
        
        # If scaler not fitted yet, fit it
        if not self.feature_engineer.fitted:
            self.feature_engineer.fit_scaler(features)
        
        # Scale features
        X = self.feature_engineer.transform_features(features)
        y = target.values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, shuffle=False
        )
        
        # Train Random Forest
        self.classification_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        
        self.classification_model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = self.classification_model.predict(X_train)
        test_pred = self.classification_model.predict(X_test)
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        
        # Cross validation
        cv_scores = cross_val_score(self.classification_model, X, y, cv=5, scoring='accuracy')
        
        results = {
            "model_type": "RandomForestClassifier",
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "train_accuracy": float(train_acc),
            "test_accuracy": float(test_acc),
            "cv_score_mean": float(cv_scores.mean()),
            "cv_score_std": float(cv_scores.std()),
            "feature_count": X.shape[1],
            "trained_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Classification model trained: Accuracy={test_acc:.4f}")
        return results
    
    def predict_price(self, data: pd.DataFrame) -> Dict:
        """Generate price predictions"""
        if self.regression_model is None:
            raise ValueError("Regression model not trained")
        
        features = self.feature_engineer.create_features(data)
        X = self.feature_engineer.transform_features(features)
        
        predictions = self.regression_model.predict(X)
        
        return {
            "predictions": predictions.tolist(),
            "prediction_count": len(predictions),
            "current_price": float(data['close'].iloc[-1]),
            "predicted_price": float(predictions[-1]),
            "predicted_change": float((predictions[-1] - data['close'].iloc[-1]) / data['close'].iloc[-1]),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def generate_signals(self, data: pd.DataFrame) -> Dict:
        """Generate trading signals"""
        if self.classification_model is None:
            raise ValueError("Classification model not trained")
        
        features = self.feature_engineer.create_features(data)
        X = self.feature_engineer.transform_features(features)
        
        signals = self.classification_model.predict(X)
        probabilities = self.classification_model.predict_proba(X)
        
        signal_names = {-1: "SELL", 0: "HOLD", 1: "BUY"}
        
        return {
            "signals": signals.tolist(),
            "signal_names": [signal_names[s] for s in signals],
            "probabilities": probabilities.tolist(),
            "current_signal": signal_names[signals[-1]],
            "current_probabilities": {
                "SELL": float(probabilities[-1][0]) if len(probabilities[-1]) > 0 else 0.0,
                "HOLD": float(probabilities[-1][1]) if len(probabilities[-1]) > 1 else 0.0,
                "BUY": float(probabilities[-1][2]) if len(probabilities[-1]) > 2 else 0.0
            },
            "generated_at": datetime.utcnow().isoformat()
        }
    
    def save_models(self):
        """Save trained models to disk"""
        if self.regression_model:
            joblib.dump(self.regression_model, self.models_dir / "regression_model.joblib")
            logger.info("Regression model saved")
        
        if self.classification_model:
            joblib.dump(self.classification_model, self.models_dir / "classification_model.joblib")
            logger.info("Classification model saved")
        
        if self.feature_engineer.fitted:
            joblib.dump(self.feature_engineer, self.models_dir / "feature_engineer.joblib")
            logger.info("Feature engineer saved")
    
    def load_models(self):
        """Load trained models from disk"""
        try:
            if (self.models_dir / "regression_model.joblib").exists():
                self.regression_model = joblib.load(self.models_dir / "regression_model.joblib")
                logger.info("Regression model loaded")
            
            if (self.models_dir / "classification_model.joblib").exists():
                self.classification_model = joblib.load(self.models_dir / "classification_model.joblib")
                logger.info("Classification model loaded")
            
            if (self.models_dir / "feature_engineer.joblib").exists():
                self.feature_engineer = joblib.load(self.models_dir / "feature_engineer.joblib")
                logger.info("Feature engineer loaded")
        
        except Exception as e:
            logger.warning(f"Error loading models: {e}")

# Initialize ML manager
ml_manager = MLModelManager()

# Load existing models on startup
ml_manager.load_models()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_healthy = redis_client.health_check()
        
        # Test Data Service connection
        data_response = requests.get(
            f"http://localhost:{SERVICE_PORTS['data']}/health",
            timeout=2
        )
        data_healthy = data_response.status_code == 200
        
        if redis_healthy and data_healthy:
            return HealthResponse(
                status=ServiceStatus.HEALTHY,
                service="MLService",
                timestamp=datetime.utcnow(),
                details={
                    "redis": "connected",
                    "data_service": "connected",
                    "regression_model": "loaded" if ml_manager.regression_model else "not_loaded",
                    "classification_model": "loaded" if ml_manager.classification_model else "not_loaded"
                }
            )
        else:
            return HealthResponse(
                status=ServiceStatus.DEGRADED,
                service="MLService",
                timestamp=datetime.utcnow(),
                details={
                    "redis": "connected" if redis_healthy else "disconnected",
                    "data_service": "connected" if data_healthy else "disconnected",
                    "regression_model": "loaded" if ml_manager.regression_model else "not_loaded",
                    "classification_model": "loaded" if ml_manager.classification_model else "not_loaded"
                }
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status=ServiceStatus.UNHEALTHY,
            service="MLService",
            timestamp=datetime.utcnow(),
            details={"error": str(e)}
        )

@app.post("/api/ml/train/regression")
async def train_regression(symbol: str, start_date: str = None, end_date: str = None):
    """Train regression model for price prediction"""
    try:
        # Get market data from Data Service
        params = {"symbol": symbol}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = requests.get(
            f"http://localhost:{SERVICE_PORTS['data']}/api/data/{symbol}",
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get market data")
        
        data_json = response.json()
        data = pd.DataFrame(data_json['data'])
        
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
        
        # Train model
        results = ml_manager.train_regression_model(data)
        
        # Save model
        ml_manager.save_models()
        
        return {
            "status": "success",
            "symbol": symbol,
            "training_results": results
        }
        
    except Exception as e:
        logger.error(f"Regression training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/train/classification")
async def train_classification(symbol: str, start_date: str = None, end_date: str = None):
    """Train classification model for signal generation"""
    try:
        # Get market data from Data Service
        params = {"symbol": symbol}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
            
        response = requests.get(
            f"http://localhost:{SERVICE_PORTS['data']}/api/data/{symbol}",
            params=params,
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get market data")
        
        data_json = response.json()
        data = pd.DataFrame(data_json['data'])
        
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
        
        # Train model
        results = ml_manager.train_classification_model(data)
        
        # Save model
        ml_manager.save_models()
        
        return {
            "status": "success", 
            "symbol": symbol,
            "training_results": results
        }
        
    except Exception as e:
        logger.error(f"Classification training failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/predict")
async def predict(symbol: str, days_back: int = 50):
    """Generate price predictions"""
    try:
        # Get recent market data
        response = requests.get(
            f"http://localhost:{SERVICE_PORTS['data']}/api/data/{symbol}",
            params={"limit": days_back},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get market data")
        
        data_json = response.json()
        data = pd.DataFrame(data_json['data'])
        
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
        
        # Generate predictions
        predictions = ml_manager.predict_price(data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "predictions": predictions
        }
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/signals")
async def generate_signals(symbol: str, days_back: int = 50):
    """Generate trading signals"""
    try:
        # Get recent market data
        response = requests.get(
            f"http://localhost:{SERVICE_PORTS['data']}/api/data/{symbol}",
            params={"limit": days_back},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get market data")
        
        data_json = response.json()
        data = pd.DataFrame(data_json['data'])
        
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
        
        # Generate signals
        signals = ml_manager.generate_signals(data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "signals": signals
        }
        
    except Exception as e:
        logger.error(f"Signal generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ml/features")
async def extract_features(symbol: str, days_back: int = 50):
    """Extract features from market data"""
    try:
        # Get recent market data
        response = requests.get(
            f"http://localhost:{SERVICE_PORTS['data']}/api/data/{symbol}",
            params={"limit": days_back},
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get market data")
        
        data_json = response.json()
        data = pd.DataFrame(data_json['data'])
        
        if 'timestamp' in data.columns:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
            data.set_index('timestamp', inplace=True)
        
        # Extract features
        features = ml_manager.feature_engineer.create_features(data)
        
        return {
            "status": "success",
            "symbol": symbol,
            "features": {
                "feature_names": features.columns.tolist(),
                "feature_count": len(features.columns),
                "sample_count": len(features),
                "latest_features": features.iloc[-1].to_dict()
            }
        }
        
    except Exception as e:
        logger.error(f"Feature extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ml/model/status")
async def model_status():
    """Get model training status"""
    return {
        "regression_model": {
            "loaded": ml_manager.regression_model is not None,
            "type": "RandomForestRegressor" if ml_manager.regression_model else None
        },
        "classification_model": {
            "loaded": ml_manager.classification_model is not None,
            "type": "RandomForestClassifier" if ml_manager.classification_model else None
        },
        "feature_engineer": {
            "fitted": ml_manager.feature_engineer.fitted
        },
        "models_directory": str(ml_manager.models_dir),
        "saved_models": [f.name for f in ml_manager.models_dir.glob("*.joblib")]
    }

def main():
    """Main entry point"""
    logger.info("Starting ML Service on port 8004...")
    
    try:
        uvicorn.run(
            "ml_service:app",
            host="0.0.0.0",
            port=SERVICE_PORTS['ml'],
            reload=False,
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start ML Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()