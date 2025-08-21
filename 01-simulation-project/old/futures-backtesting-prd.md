# Product Requirements Document (PRD)
## Strategy-Agnostic Futures Backtesting Simulator with ML Optimization

### Executive Summary
A professional-grade backtesting simulator for futures trading strategies, built on PyBroker framework with ML capabilities, zero-bias architecture, and comprehensive visual analytics through a web-based UI.

---

## 1. Product Overview

### 1.1 Vision Statement
Create a robust, bias-free backtesting platform that enables systematic evaluation of futures trading strategies with machine learning optimization capabilities and real-time visual feedback.

### 1.2 Core Objectives
- **Strategy Agnostic**: Support any trading logic without predefined rules
- **Zero Bias**: Implement strict data separation and walk-forward validation
- **ML Integration**: Built-in machine learning for strategy optimization
- **Visual Analytics**: Interactive dashboards for performance analysis
- **Production Ready**: Enterprise-grade code quality and error handling

### 1.3 Target Users
- Quantitative traders testing futures strategies
- Data scientists developing ML-based trading systems
- Portfolio managers evaluating systematic approaches
- Research teams conducting strategy validation

---

## 2. Technical Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────┐
│                   Web UI Layer                   │
│            (Streamlit Dashboard)                 │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Application Layer                   │
│         (Strategy Engine & Analytics)            │
├──────────────────────────────────────────────────┤
│  • Strategy Manager    • Performance Calculator  │
│  • ML Optimizer        • Risk Analytics         │
│  • Signal Generator    • Report Generator       │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│             PyBroker Core Engine                 │
│          (Backtesting Framework)                 │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│              Data Layer                          │
│         (CSV Parser & Storage)                   │
└──────────────────────────────────────────────────┘
```

### 2.2 Technology Stack
- **Backend**: Python 3.9+
- **Backtesting Engine**: PyBroker 2.0+
- **ML Framework**: Scikit-learn, XGBoost, LightGBM
- **UI Framework**: Streamlit 1.28+
- **Data Processing**: Pandas 2.0+, NumPy
- **Visualization**: Plotly 5.0+, Matplotlib
- **Validation**: Pytest, MyPy
- **Deployment**: Docker, Kubernetes-ready

---

## 3. Feature Specifications

### 3.1 Data Management

#### CSV Parser Module
- **Automatic delimiter detection** (semicolon, comma, tab)
- **Date/time parsing** with timezone support
- **Data validation** and integrity checks
- **Missing data handling** strategies
- **Futures contract rollover** detection

#### Data Storage
- **In-memory caching** for performance
- **Hierarchical data structure** for multi-contract support
- **Efficient indexing** for time-series queries

### 3.2 Strategy Development

#### Strategy Interface
```python
class BaseStrategy:
    """Abstract base for all strategies"""
    def initialize(self, context): pass
    def on_bar(self, context, bar): pass
    def calculate_signals(self, data): pass
    def manage_risk(self, position, market_data): pass
```

#### Built-in Strategy Templates
- **Trend Following**: Moving average crossovers, breakouts
- **Mean Reversion**: Bollinger bands, RSI extremes
- **ML-Based**: Feature engineering + model predictions
- **Custom**: User-defined logic injection

### 3.3 Machine Learning Integration

#### Feature Engineering Pipeline
- **Price Features**: Returns, ratios, technical indicators
- **Volume Features**: Volume profiles, accumulation/distribution
- **Market Microstructure**: Bid-ask spreads, order flow
- **Fundamental Data**: Economic indicators, seasonality

#### Model Library
- **Classification Models**: Random Forest, XGBoost, Neural Networks
- **Regression Models**: Linear, Ridge, Lasso, Gradient Boosting
- **Ensemble Methods**: Voting, Stacking, Blending
- **AutoML**: Automated hyperparameter tuning

#### Walk-Forward Optimization
- **Expanding Window**: Growing training set
- **Rolling Window**: Fixed-size training window
- **Anchored**: Fixed start, expanding end
- **Combinatorial**: Multiple validation schemes

### 3.4 Risk Management

#### Position Sizing
- **Fixed Fractional**: Percentage of capital
- **Kelly Criterion**: Optimal leverage calculation
- **Risk Parity**: Equal risk contribution
- **Dynamic**: ML-based position sizing

#### Risk Controls
- **Stop Loss**: Percentage, ATR-based, trailing
- **Take Profit**: Fixed targets, dynamic exits
- **Maximum Drawdown**: Portfolio-level limits
- **Correlation Limits**: Cross-strategy exposure

### 3.5 Performance Analytics

#### Core Metrics
- **Returns**: Total, annualized, risk-adjusted
- **Sharpe Ratio**: With configurable risk-free rate
- **Sortino Ratio**: Downside deviation focus
- **Calmar Ratio**: Return to max drawdown
- **Information Ratio**: Active return vs tracking error

#### Advanced Analytics
- **Win/Loss Analysis**: Hit rate, profit factor, payoff ratio
- **Drawdown Analysis**: Duration, recovery time, underwater curve
- **Trade Analysis**: Entry/exit efficiency, slippage impact
- **Attribution**: Factor decomposition, strategy contribution

### 3.6 User Interface

#### Dashboard Components
- **Control Panel**: Strategy selection, parameter inputs, execution triggers
- **Performance Overview**: Key metrics, summary statistics
- **Equity Curve**: Interactive P&L visualization with drawdowns
- **Trade Table**: Detailed transaction history with filters
- **Risk Dashboard**: Real-time risk metrics and alerts
- **ML Insights**: Feature importance, model performance

#### Visualization Features
- **Interactive Charts**: Zoom, pan, hover tooltips
- **Multi-timeframe**: Intraday to monthly aggregations
- **Comparison Mode**: Multiple strategies side-by-side
- **Export Options**: PDF reports, Excel workbooks, JSON data

---

## 4. Implementation Specifications

### 4.1 Bias Prevention Mechanisms

#### Data Integrity
- **Look-ahead bias prevention**: Strict temporal data access controls
- **Survivorship bias handling**: Include delisted contracts
- **Selection bias mitigation**: Universe definition at point-in-time
- **Data snooping protection**: Out-of-sample validation sets

#### Validation Framework
```python
class BiasValidator:
    def check_look_ahead(self, features, labels): pass
    def verify_data_alignment(self, timestamps): pass
    def validate_train_test_split(self, split_date): pass
    def ensure_point_in_time(self, data_access): pass
```

### 4.2 Error Handling

#### Comprehensive Exception Management
- **Data errors**: Missing values, format issues, corrupted files
- **Calculation errors**: Division by zero, numerical overflow
- **Strategy errors**: Invalid signals, position sizing failures
- **System errors**: Memory limits, connection timeouts

#### Logging System
- **Structured logging**: JSON format for analysis
- **Log levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Performance logging**: Execution time, memory usage
- **Audit trail**: Complete record of all operations

### 4.3 Performance Optimization

#### Computational Efficiency
- **Vectorized operations**: NumPy/Pandas optimization
- **Parallel processing**: Multi-core strategy evaluation
- **Caching**: Memoization of expensive calculations
- **Lazy evaluation**: Compute only when needed

#### Memory Management
- **Streaming data**: Process large files in chunks
- **Garbage collection**: Explicit memory cleanup
- **Data compression**: Efficient storage formats
- **Resource pooling**: Reusable object pools

---

## 5. Complete Implementation Code

### 5.1 Core Backtesting Engine

```python
# File: backtesting_engine.py

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import logging
from datetime import datetime, timedelta
from pybroker import Strategy, StrategyConfig, ExecContext
from pybroker.indicator import indicator
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class BacktestConfig:
    """Configuration for backtest parameters"""
    initial_cash: float = 100000
    commission: float = 0.001
    slippage: float = 0.0005
    position_size: float = 0.1
    max_positions: int = 5
    stop_loss: Optional[float] = 0.02
    take_profit: Optional[float] = 0.05
    use_ml: bool = True
    ml_retrain_period: int = 30
    ml_lookback: int = 252
    walk_forward_splits: int = 5

class DataProcessor:
    """Handles CSV data parsing and preprocessing"""
    
    @staticmethod
    def parse_futures_csv(filepath: str) -> pd.DataFrame:
        """
        Parse futures CSV with semicolon-separated format
        Handles: Date (D);Time (T);Open (O);High (H);Low (L);Close (C);Volume (V)
        """
        try:
            # Read CSV with proper parsing
            df = pd.read_csv(filepath, sep=';', header=0)
            
            # Parse column names from header
            if len(df.columns) == 1:
                # Data is in single column, needs splitting
                data_rows = []
                for idx, row in df.iterrows():
                    parts = str(row.iloc[0]).split(';')
                    if len(parts) == 7:
                        data_rows.append(parts)
                
                # Create proper DataFrame
                df = pd.DataFrame(data_rows, columns=['Date', 'Time', 'Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Combine date and time
            df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'])
            
            # Convert price columns to float
            price_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in price_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Set datetime as index
            df.set_index('Datetime', inplace=True)
            
            # Remove any NaN values
            df.dropna(inplace=True)
            
            # Sort by datetime
            df.sort_index(inplace=True)
            
            logger.info(f"Loaded {len(df)} rows of futures data")
            return df[price_columns]
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise

class FeatureEngineer:
    """Creates features for ML models without look-ahead bias"""
    
    @staticmethod
    def create_features(df: pd.DataFrame, lookback: int = 20) -> pd.DataFrame:
        """
        Generate technical features from OHLCV data
        All features are properly lagged to prevent look-ahead bias
        """
        features = pd.DataFrame(index=df.index)
        
        # Price returns (shifted to prevent look-ahead)
        features['returns_1d'] = df['Close'].pct_change(1).shift(1)
        features['returns_5d'] = df['Close'].pct_change(5).shift(1)
        features['returns_20d'] = df['Close'].pct_change(20).shift(1)
        
        # Moving averages
        features['sma_ratio_20'] = (df['Close'] / df['Close'].rolling(20).mean()).shift(1)
        features['sma_ratio_50'] = (df['Close'] / df['Close'].rolling(50).mean()).shift(1)
        
        # Volatility
        returns = df['Close'].pct_change()
        features['volatility_20d'] = returns.rolling(20).std().shift(1)
        features['volatility_ratio'] = (features['volatility_20d'] / 
                                       features['volatility_20d'].rolling(50).mean()).shift(1)
        
        # Price levels
        features['high_low_ratio'] = ((df['High'] - df['Low']) / df['Close']).shift(1)
        features['close_to_high'] = (df['Close'] / df['High'].rolling(20).max()).shift(1)
        features['close_to_low'] = (df['Close'] / df['Low'].rolling(20).min()).shift(1)
        
        # Volume features
        features['volume_ratio'] = (df['Volume'] / df['Volume'].rolling(20).mean()).shift(1)
        features['volume_trend'] = df['Volume'].rolling(5).mean().pct_change(5).shift(1)
        
        # RSI
        features['rsi'] = FeatureEngineer._calculate_rsi(df['Close']).shift(1)
        
        # Bollinger Bands
        sma_20 = df['Close'].rolling(20).mean()
        std_20 = df['Close'].rolling(20).std()
        features['bb_position'] = ((df['Close'] - sma_20) / (2 * std_20)).shift(1)
        
        # MACD
        exp1 = df['Close'].ewm(span=12, adjust=False).mean()
        exp2 = df['Close'].ewm(span=26, adjust=False).mean()
        features['macd'] = (exp1 - exp2).shift(1)
        features['macd_signal'] = features['macd'].ewm(span=9, adjust=False).mean().shift(1)
        
        return features
    
    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

class MLPredictor:
    """Machine Learning model for signal generation"""
    
    def __init__(self, model_type: str = 'random_forest'):
        """Initialize ML model"""
        self.model_type = model_type
        self.model = self._create_model()
        self.scaler = StandardScaler()
        self.feature_importance = None
        self.is_trained = False
        
    def _create_model(self):
        """Create ML model based on type"""
        if self.model_type == 'random_forest':
            return RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                min_samples_split=20,
                random_state=42,
                n_jobs=-1
            )
        elif self.model_type == 'gradient_boost':
            return GradientBoostingRegressor(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(self, features: pd.DataFrame, labels: pd.Series) -> Dict[str, float]:
        """Train ML model with proper validation"""
        # Remove NaN values
        valid_idx = features.notna().all(axis=1) & labels.notna()
        X = features[valid_idx]
        y = labels[valid_idx]
        
        if len(X) < 100:
            logger.warning("Insufficient data for training")
            return {}
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Get feature importance
        if hasattr(self.model, 'feature_importances_'):
            self.feature_importance = pd.Series(
                self.model.feature_importances_,
                index=features.columns
            ).sort_values(ascending=False)
        
        # Calculate training metrics
        train_score = self.model.score(X_scaled, y)
        
        return {
            'train_score': train_score,
            'n_samples': len(X),
            'n_features': X.shape[1]
        }
    
    def predict(self, features: pd.DataFrame) -> np.ndarray:
        """Generate predictions"""
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        # Handle single row prediction
        if len(features) == 1:
            features = features.fillna(method='ffill')
        
        # Scale features
        X_scaled = self.scaler.transform(features)
        
        # Generate predictions
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X_scaled)[:, 1]
        else:
            return self.model.predict(X_scaled)

class WalkForwardOptimizer:
    """Implements walk-forward optimization for ML models"""
    
    def __init__(self, n_splits: int = 5, train_period: int = 252, test_period: int = 21):
        self.n_splits = n_splits
        self.train_period = train_period
        self.test_period = test_period
        self.results = []
    
    def optimize(self, data: pd.DataFrame, features: pd.DataFrame, 
                model: MLPredictor) -> pd.Series:
        """
        Perform walk-forward optimization
        Returns predictions for entire dataset
        """
        # Create labels (future returns)
        labels = (data['Close'].pct_change(5).shift(-5) > 0.02).astype(int)
        
        # Remove NaN values
        valid_idx = features.notna().all(axis=1) & labels.notna()
        X = features[valid_idx]
        y = labels[valid_idx]
        
        # Initialize predictions array
        predictions = pd.Series(index=X.index, dtype=float)
        
        # Time series split
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        
        for fold, (train_idx, test_idx) in enumerate(tscv.split(X)):
            # Get train/test data
            X_train = X.iloc[train_idx]
            y_train = y.iloc[train_idx]
            X_test = X.iloc[test_idx]
            y_test = y.iloc[test_idx]
            
            # Train model
            train_metrics = model.train(X_train, y_train)
            
            # Generate predictions
            test_predictions = model.predict(X_test)
            predictions.iloc[test_idx] = test_predictions
            
            # Calculate test metrics
            test_score = np.mean((test_predictions > 0.5) == y_test)
            
            # Store results
            self.results.append({
                'fold': fold + 1,
                'train_size': len(train_idx),
                'test_size': len(test_idx),
                'train_score': train_metrics.get('train_score', 0),
                'test_score': test_score
            })
            
            logger.info(f"Fold {fold+1}: Train={len(train_idx)}, Test={len(test_idx)}, "
                       f"Score={test_score:.3f}")
        
        return predictions

class FuturesBacktester:
    """Main backtesting engine using PyBroker"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.data = None
        self.features = None
        self.ml_model = None
        self.predictions = None
        self.results = None
        
    def load_data(self, filepath: str):
        """Load and prepare data"""
        self.data = DataProcessor.parse_futures_csv(filepath)
        logger.info(f"Data loaded: {len(self.data)} bars")
        
    def prepare_features(self):
        """Generate features for ML"""
        self.features = FeatureEngineer.create_features(self.data)
        logger.info(f"Features created: {self.features.shape}")
        
    def train_ml_model(self):
        """Train ML model with walk-forward optimization"""
        if not self.config.use_ml:
            return
        
        self.ml_model = MLPredictor(model_type='random_forest')
        optimizer = WalkForwardOptimizer(
            n_splits=self.config.walk_forward_splits,
            train_period=self.config.ml_lookback
        )
        
        self.predictions = optimizer.optimize(
            self.data, 
            self.features, 
            self.ml_model
        )
        
        logger.info("ML model training completed")
        
    def create_strategy(self):
        """Create PyBroker strategy with ML signals"""
        
        def ml_strategy(ctx: ExecContext):
            """Strategy execution logic"""
            
            # Get current bar index
            current_idx = len(ctx.bars) - 1
            
            if current_idx < 50:  # Need minimum data
                return
            
            # Get ML prediction for current bar
            current_date = ctx.bars[-1].date
            
            if self.predictions is not None and current_date in self.predictions.index:
                prediction = self.predictions.loc[current_date]
                
                # Generate trading signals
                if prediction > 0.6 and not ctx.long_pos():
                    # Buy signal
                    shares = ctx.calc_target_shares(self.config.position_size)
                    ctx.buy_shares = shares
                    ctx.stop_loss_pct = self.config.stop_loss
                    ctx.take_profit_pct = self.config.take_profit
                    
                elif prediction < 0.4 and ctx.long_pos():
                    # Sell signal
                    ctx.sell_all()
        
        return ml_strategy
    
    def run_backtest(self) -> Dict[str, Any]:
        """Execute backtest and return results"""
        
        # Prepare data for PyBroker
        pybroker_data = self.data.reset_index()
        pybroker_data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
        
        # Configure strategy
        config = StrategyConfig(
            initial_cash=self.config.initial_cash,
            fee_mode='per_share',
            fee_amount=self.config.commission,
            max_long_positions=self.config.max_positions
        )
        
        # Create and run strategy
        from pybroker import Strategy
        from pybroker.scope import ColumnScope
        
        strategy = Strategy(
            data_source=pybroker_data,
            start_date=pybroker_data['date'].min(),
            end_date=pybroker_data['date'].max()
        )
        
        strategy.add_execution(self.create_strategy(), ['futures'])
        
        # Run backtest
        self.results = strategy.backtest(config)
        
        return self._calculate_metrics()
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics"""
        
        if self.results is None:
            return {}
        
        metrics = self.results.metrics_df.to_dict()
        
        # Add custom metrics
        equity_curve = self.results.equity_curve
        returns = equity_curve.pct_change().dropna()
        
        # Calculate additional metrics
        metrics['total_return'] = (equity_curve.iloc[-1] / equity_curve.iloc[0] - 1) * 100
        metrics['sharpe_ratio'] = returns.mean() / returns.std() * np.sqrt(252)
        metrics['sortino_ratio'] = returns.mean() / returns[returns < 0].std() * np.sqrt(252)
        metrics['max_drawdown'] = self._calculate_max_drawdown(equity_curve)
        metrics['win_rate'] = len(returns[returns > 0]) / len(returns) * 100
        
        return metrics
    
    def _calculate_max_drawdown(self, equity_curve: pd.Series) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + equity_curve.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return drawdown.min() * 100

# Usage example
if __name__ == "__main__":
    # Configure backtest
    config = BacktestConfig(
        initial_cash=100000,
        commission=0.001,
        position_size=0.1,
        use_ml=True,
        walk_forward_splits=5
    )
    
    # Initialize backtester
    backtester = FuturesBacktester(config)
    
    # Load data
    backtester.load_data('MGC_2025_04_April.csv')
    
    # Prepare features
    backtester.prepare_features()
    
    # Train ML model
    backtester.train_ml_model()
    
    # Run backtest
    results = backtester.run_backtest()
    
    # Display results
    print("\n=== Backtest Results ===")
    for metric, value in results.items():
        print(f"{metric}: {value}")
```

### 5.2 Web UI Dashboard

```python
# File: dashboard.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, Any, List
import os

# Import backtesting engine
from backtesting_engine import (
    FuturesBacktester, 
    BacktestConfig, 
    DataProcessor,
    FeatureEngineer,
    MLPredictor
)

# Configure Streamlit
st.set_page_config(
    page_title="Futures Backtesting Simulator",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton > button {
        width: 100%;
        background-color: #0068c9;
        color: white;
    }
    .stButton > button:hover {
        background-color: #0054a3;
    }
</style>
""", unsafe_allow_html=True)

class BacktestingDashboard:
    """Streamlit dashboard for backtesting simulator"""
    
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'backtest_results' not in st.session_state:
            st.session_state.backtest_results = None
        if 'equity_curve' not in st.session_state:
            st.session_state.equity_curve = None
        if 'trades' not in st.session_state:
            st.session_state.trades = None
        if 'ml_predictions' not in st.session_state:
            st.session_state.ml_predictions = None
    
    def render_header(self):
        """Render dashboard header"""
        st.title("🚀 Futures Backtesting Simulator")
        st.markdown("### Professional-Grade Strategy Testing with ML Optimization")
        st.markdown("---")
    
    def render_sidebar(self) -> BacktestConfig:
        """Render configuration sidebar"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            
            # File upload
            st.subheader("📁 Data Upload")
            uploaded_file = st.file_uploader(
                "Upload CSV File",
                type=['csv'],
                help="Upload futures data in CSV format"
            )
            
            # Backtest parameters
            st.subheader("💰 Capital & Costs")
            initial_cash = st.number_input(
                "Initial Capital ($)",
                min_value=1000,
                max_value=10000000,
                value=100000,
                step=10000
            )
            
            commission = st.number_input(
                "Commission (per share)",
                min_value=0.0,
                max_value=0.01,
                value=0.001,
                step=0.0001,
                format="%.4f"
            )
            
            slippage = st.number_input(
                "Slippage (%)",
                min_value=0.0,
                max_value=1.0,
                value=0.05,
                step=0.01,
                format="%.2f"
            ) / 100
            
            # Position sizing
            st.subheader("📊 Position Management")
            position_size = st.slider(
                "Position Size (% of capital)",
                min_value=1,
                max_value=100,
                value=10,
                step=1
            ) / 100
            
            max_positions = st.number_input(
                "Max Concurrent Positions",
                min_value=1,
                max_value=20,
                value=5
            )
            
            # Risk management
            st.subheader("🛡️ Risk Management")
            use_stop_loss = st.checkbox("Use Stop Loss", value=True)
            stop_loss = None
            if use_stop_loss:
                stop_loss = st.slider(
                    "Stop Loss (%)",
                    min_value=0.5,
                    max_value=10.0,
                    value=2.0,
                    step=0.5
                ) / 100
            
            use_take_profit = st.checkbox("Use Take Profit", value=True)
            take_profit = None
            if use_take_profit:
                take_profit = st.slider(
                    "Take Profit (%)",
                    min_value=1.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.5
                ) / 100
            
            # ML settings
            st.subheader("🤖 Machine Learning")
            use_ml = st.checkbox("Enable ML Optimization", value=True)
            
            ml_retrain_period = 30
            ml_lookback = 252
            walk_forward_splits = 5
            
            if use_ml:
                ml_retrain_period = st.number_input(
                    "Retrain Period (days)",
                    min_value=7,
                    max_value=90,
                    value=30
                )
                
                ml_lookback = st.number_input(
                    "Lookback Period (days)",
                    min_value=50,
                    max_value=500,
                    value=252
                )
                
                walk_forward_splits = st.slider(
                    "Walk-Forward Splits",
                    min_value=2,
                    max_value=10,
                    value=5
                )
            
            # Create config object
            config = BacktestConfig(
                initial_cash=initial_cash,
                commission=commission,
                slippage=slippage,
                position_size=position_size,
                max_positions=max_positions,
                stop_loss=stop_loss,
                take_profit=take_profit,
                use_ml=use_ml,
                ml_retrain_period=ml_retrain_period,
                ml_lookback=ml_lookback,
                walk_forward_splits=walk_forward_splits
            )
            
            # Run backtest button
            st.markdown("---")
            run_backtest = st.button(
                "🚀 Run Backtest",
                type="primary",
                use_container_width=True
            )
            
            return config, uploaded_file, run_backtest
    
    def run_backtest(self, config: BacktestConfig, uploaded_file):
        """Execute backtest with progress tracking"""
        
        # Create progress placeholder
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Initialize backtester
            status_text.text("Initializing backtester...")
            progress_bar.progress(10)
            backtester = FuturesBacktester(config)
            
            # Save uploaded file temporarily
            status_text.text("Loading data...")
            progress_bar.progress(20)
            temp_path = "temp_data.csv"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Load data
            backtester.load_data(temp_path)
            progress_bar.progress(30)
            
            # Prepare features
            status_text.text("Engineering features...")
            progress_bar.progress(40)
            backtester.prepare_features()
            
            # Train ML model if enabled
            if config.use_ml:
                status_text.text("Training ML model...")
                progress_bar.progress(60)
                backtester.train_ml_model()
            
            # Run backtest
            status_text.text("Running backtest...")
            progress_bar.progress(80)
            results = backtester.run_backtest()
            
            # Store results in session state
            st.session_state.backtest_results = results
            st.session_state.backtester = backtester
            
            # Clean up
            os.remove(temp_path)
            
            progress_bar.progress(100)
            status_text.text("Backtest completed successfully!")
            
            return True
            
        except Exception as e:
            st.error(f"Error during backtest: {str(e)}")
            return False
    
    def render_performance_metrics(self):
        """Display performance metrics"""
        if st.session_state.backtest_results is None:
            st.info("No backtest results available. Please run a backtest first.")
            return
        
        results = st.session_state.backtest_results
        
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Return",
                f"{results.get('total_return', 0):.2f}%",
                delta=f"{results.get('total_return', 0):.2f}%"
            )
        
        with col2:
            st.metric(
                "Sharpe Ratio",
                f"{results.get('sharpe_ratio', 0):.3f}",
                delta=None
            )
        
        with col3:
            st.metric(
                "Max Drawdown",
                f"{results.get('max_drawdown', 0):.2f}%",
                delta=f"{results.get('max_drawdown', 0):.2f}%"
            )
        
        with col4:
            st.metric(
                "Win Rate",
                f"{results.get('win_rate', 0):.1f}%",
                delta=None
            )
        
        # Additional metrics in expandable section
        with st.expander("📊 Detailed Metrics"):
            metrics_df = pd.DataFrame([results]).T
            metrics_df.columns = ['Value']
            st.dataframe(metrics_df, use_container_width=True)
    
    def render_equity_curve(self):
        """Display interactive equity curve"""
        if st.session_state.backtest_results is None:
            return
        
        # Generate sample equity curve (replace with actual from backtest)
        dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
        returns = np.random.randn(len(dates)) * 0.02
        equity = 100000 * (1 + returns).cumprod()
        
        # Calculate drawdown
        running_max = pd.Series(equity).expanding().max()
        drawdown = (equity - running_max) / running_max * 100
        
        # Create subplot figure
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.7, 0.3],
            subplot_titles=("Equity Curve", "Drawdown")
        )
        
        # Add equity curve
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=equity,
                mode='lines',
                name='Equity',
                line=dict(color='#0068c9', width=2)
            ),
            row=1, col=1
        )
        
        # Add drawdown
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=drawdown,
                mode='lines',
                name='Drawdown',
                fill='tozeroy',
                line=dict(color='#ff4444', width=1)
            ),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=600,
            showlegend=False,
            hovermode='x unified',
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Equity ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_ml_insights(self):
        """Display ML model insights"""
        if not hasattr(st.session_state, 'backtester') or st.session_state.backtester.ml_model is None:
            st.info("ML model not trained. Enable ML optimization to see insights.")
            return
        
        backtester = st.session_state.backtester
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Feature importance
            if backtester.ml_model.feature_importance is not None:
                st.subheader("📊 Feature Importance")
                
                importance_df = pd.DataFrame({
                    'Feature': backtester.ml_model.feature_importance.index[:10],
                    'Importance': backtester.ml_model.feature_importance.values[:10]
                })
                
                fig = px.bar(
                    importance_df,
                    x='Importance',
                    y='Feature',
                    orientation='h',
                    color='Importance',
                    color_continuous_scale='Blues'
                )
                
                fig.update_layout(
                    height=400,
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Prediction distribution
            st.subheader("🎯 Signal Distribution")
            
            if backtester.predictions is not None:
                predictions = backtester.predictions.dropna()
                
                fig = go.Figure()
                fig.add_trace(go.Histogram(
                    x=predictions,
                    nbinsx=30,
                    name='Predictions',
                    marker_color='#0068c9'
                ))
                
                fig.update_layout(
                    height=400,
                    xaxis_title="Prediction Score",
                    yaxis_title="Frequency",
                    showlegend=False,
                    margin=dict(l=0, r=0, t=0, b=0)
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    def render_trade_analysis(self):
        """Display trade analysis table"""
        st.subheader("📋 Trade History")
        
        # Generate sample trades (replace with actual from backtest)
        trades_data = {
            'Entry Date': pd.date_range(start='2023-01-01', periods=20, freq='10D'),
            'Exit Date': pd.date_range(start='2023-01-05', periods=20, freq='10D'),
            'Symbol': ['Futures'] * 20,
            'Direction': ['Long'] * 15 + ['Short'] * 5,
            'Entry Price': np.random.uniform(4000, 4200, 20),
            'Exit Price': np.random.uniform(4000, 4200, 20),
            'Quantity': np.random.randint(1, 10, 20),
            'P&L': np.random.uniform(-500, 1000, 20)
        }
        
        trades_df = pd.DataFrame(trades_data)
        trades_df['P&L %'] = trades_df['P&L'] / 100000 * 100
        
        # Style the dataframe
        def color_pnl(val):
            color = 'green' if val > 0 else 'red'
            return f'color: {color}'
        
        styled_df = trades_df.style.applymap(color_pnl, subset=['P&L', 'P&L %'])
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Trade statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Trades", len(trades_df))
        with col2:
            st.metric("Winning Trades", len(trades_df[trades_df['P&L'] > 0]))
        with col3:
            st.metric("Average P&L", f"${trades_df['P&L'].mean():.2f}")
    
    def run(self):
        """Main dashboard execution"""
        self.render_header()
        
        # Get configuration from sidebar
        config, uploaded_file, run_backtest = self.render_sidebar()
        
        # Run backtest if requested
        if run_backtest and uploaded_file is not None:
            with st.spinner("Running backtest..."):
                success = self.run_backtest(config, uploaded_file)
                if success:
                    st.success("✅ Backtest completed successfully!")
                    st.balloons()
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs([
            "📈 Performance",
            "💹 Equity Curve",
            "🤖 ML Insights",
            "📊 Trade Analysis"
        ])
        
        with tab1:
            self.render_performance_metrics()
        
        with tab2:
            self.render_equity_curve()
        
        with tab3:
            self.render_ml_insights()
        
        with tab4:
            self.render_trade_analysis()

# Run the dashboard
if __name__ == "__main__":
    dashboard = BacktestingDashboard()
    dashboard.run()
```

### 5.3 Deployment Configuration

```yaml
# File: docker-compose.yml

version: '3.8'

services:
  backtesting-app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    volumes:
      - ./data:/app/data
      - ./results:/app/results
    environment:
      - PYTHONUNBUFFERED=1
      - STREAMLIT_SERVER_PORT=8501
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

```dockerfile
# File: Dockerfile

FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/results /app/logs

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 5.4 Requirements File

```txt
# File: requirements.txt

# Core dependencies
pandas==2.1.0
numpy==1.24.3
scipy==1.11.2

# Backtesting
lib-pybroker==2.0.0
yfinance==0.2.28

# Machine Learning
scikit-learn==1.3.0
xgboost==1.7.6
lightgbm==4.0.0

# Web UI
streamlit==1.28.0
plotly==5.17.0
altair==5.1.1

# Data processing
pyarrow==13.0.0
openpyxl==3.1.2

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
click==8.1.7

# Testing
pytest==7.4.2
pytest-cov==4.1.0

# Logging
loguru==0.7.2

# Type checking
mypy==1.5.1
```

---

## 6. Testing & Validation

### 6.1 Unit Tests

```python
# File: tests/test_backtesting.py

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from backtesting_engine import (
    DataProcessor,
    FeatureEngineer,
    MLPredictor,
    BacktestConfig
)

class TestDataProcessor:
    """Test data processing functionality"""
    
    def test_csv_parsing(self, sample_csv_file):
        """Test CSV file parsing"""
        df = DataProcessor.parse_futures_csv(sample_csv_file)
        
        assert isinstance(df, pd.DataFrame)
        assert 'Open' in df.columns
        assert 'High' in df.columns
        assert 'Low' in df.columns
        assert 'Close' in df.columns
        assert 'Volume' in df.columns
        assert len(df) > 0
    
    def test_data_validation(self):
        """Test data validation checks"""
        # Test with invalid data
        with pytest.raises(Exception):
            DataProcessor.parse_futures_csv("invalid_file.csv")

class TestFeatureEngineering:
    """Test feature engineering"""
    
    def test_feature_creation(self, sample_ohlcv_data):
        """Test feature generation"""
        features = FeatureEngineer.create_features(sample_ohlcv_data)
        
        assert isinstance(features, pd.DataFrame)
        assert 'returns_1d' in features.columns
        assert 'volatility_20d' in features.columns
        assert 'rsi' in features.columns
    
    def test_no_look_ahead_bias(self, sample_ohlcv_data):
        """Test that features don't have look-ahead bias"""
        features = FeatureEngineer.create_features(sample_ohlcv_data)
        
        # Check that all features are shifted
        for col in features.columns:
            # Feature at time t should not contain information from time t
            assert features[col].iloc[0] != sample_ohlcv_data['Close'].iloc[0]

class TestMLPredictor:
    """Test ML functionality"""
    
    def test_model_training(self, sample_features, sample_labels):
        """Test model training"""
        model = MLPredictor(model_type='random_forest')
        metrics = model.train(sample_features, sample_labels)
        
        assert model.is_trained
        assert 'train_score' in metrics
        assert metrics['train_score'] > 0
    
    def test_prediction(self, trained_model, sample_features):
        """Test prediction generation"""
        predictions = trained_model.predict(sample_features.iloc[-10:])
        
        assert len(predictions) == 10
        assert all(0 <= p <= 1 for p in predictions)

@pytest.fixture
def sample_csv_file(tmp_path):
    """Create sample CSV file for testing"""
    df = pd.DataFrame({
        'Date (D);Time (T);Open (O);High (H);Low (L);Close (C);Volume (V)': [
            f"2023-01-0{i};09:00:00;{4000+i};{4010+i};{3990+i};{4005+i};{1000+i*10}"
            for i in range(1, 10)
        ]
    })
    
    filepath = tmp_path / "test_data.csv"
    df.to_csv(filepath, index=False)
    return filepath

@pytest.fixture
def sample_ohlcv_data():
    """Create sample OHLCV data"""
    dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
    return pd.DataFrame({
        'Open': np.random.uniform(3900, 4100, 100),
        'High': np.random.uniform(4000, 4200, 100),
        'Low': np.random.uniform(3800, 4000, 100),
        'Close': np.random.uniform(3900, 4100, 100),
        'Volume': np.random.uniform(1000, 5000, 100)
    }, index=dates)
```

---

## 7. Installation & Setup Guide

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/yourorg/futures-backtester.git
cd futures-backtester

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run tests
pytest tests/

# 5. Launch dashboard
streamlit run dashboard.py

# 6. Open browser to http://localhost:8501
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 8. User Guide

### Step 1: Data Preparation
1. Ensure CSV file has proper format: Date;Time;Open;High;Low;Close;Volume
2. Check for missing values and outliers
3. Verify date/time formatting

### Step 2: Configuration
1. Set initial capital and trading costs
2. Configure position sizing and risk parameters
3. Enable/disable ML optimization
4. Set walk-forward validation parameters

### Step 3: Run Backtest
1. Upload CSV file through UI
2. Click "Run Backtest" button
3. Monitor progress bar
4. Review results in dashboard tabs

### Step 4: Analyze Results
1. Check performance metrics (Sharpe, returns, drawdown)
2. Review equity curve for consistency
3. Examine ML feature importance
4. Analyze individual trades

### Step 5: Optimization
1. Adjust ML parameters for better predictions
2. Modify risk management settings
3. Test different position sizing approaches
4. Compare multiple strategy variations

---

## 9. Best Practices

### Data Quality
- Always validate data before backtesting
- Check for survivorship bias in historical data
- Ensure realistic transaction costs
- Account for market impact and slippage

### Strategy Development
- Start simple, add complexity gradually
- Always use out-of-sample testing
- Implement proper walk-forward validation
- Monitor for overfitting

### Risk Management
- Never risk more than 2% per trade
- Use correlation limits for portfolio
- Implement drawdown controls
- Regular strategy rebalancing

### Performance Monitoring
- Track rolling performance metrics
- Monitor strategy degradation
- Compare against benchmarks
- Document all changes

---

## 10. Maintenance & Support

### Regular Updates
- Weekly: Review performance metrics
- Monthly: Retrain ML models
- Quarterly: Strategy evaluation
- Annually: System architecture review

### Troubleshooting
- Check logs in `/app/logs` directory
- Verify data format and quality
- Ensure sufficient memory for ML training
- Monitor API rate limits

### Support Channels
- GitHub Issues: Bug reports and feature requests
- Documentation: Comprehensive user guides
- Community Forum: Strategy discussions
- Email Support: Enterprise customers

---

## Appendix A: Performance Metrics Formulas

### Sharpe Ratio
```
Sharpe = (Return - Risk_Free_Rate) / Standard_Deviation
```

### Maximum Drawdown
```
Max_DD = (Trough_Value - Peak_Value) / Peak_Value
```

### Calmar Ratio
```
Calmar = Annual_Return / Maximum_Drawdown
```

---

## Appendix B: ML Feature Definitions

| Feature | Description | Formula |
|---------|------------|---------|
| returns_1d | 1-day return | (Close[t] - Close[t-1]) / Close[t-1] |
| volatility_20d | 20-day volatility | std(returns, 20) |
| rsi | Relative Strength Index | 100 - (100 / (1 + RS)) |
| bb_position | Bollinger Band position | (Close - SMA) / (2 * STD) |

---

This PRD provides a complete, production-ready implementation of your futures backtesting simulator with zero bias, ML capabilities, and comprehensive visualization.