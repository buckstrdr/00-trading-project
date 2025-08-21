# PyBroker Complete Documentation

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Data Sources](#data-sources)
5. [Strategy Creation](#strategy-creation)
6. [Indicators](#indicators)
7. [Trading Rules](#trading-rules)
8. [Machine Learning Integration](#machine-learning-integration)
9. [Backtesting](#backtesting)
10. [Walkforward Analysis](#walkforward-analysis)
11. [Position Management](#position-management)
12. [Risk Management](#risk-management)
13. [Portfolio Optimization](#portfolio-optimization)
14. [Performance Metrics](#performance-metrics)
15. [Bootstrap Analysis](#bootstrap-analysis)
16. [Order Execution](#order-execution)
17. [Advanced Features](#advanced-features)
18. [Configuration](#configuration)
19. [Live Trading](#live-trading)
20. [Best Practices](#best-practices)

## Introduction

PyBroker is a Python framework designed for developing algorithmic trading strategies with a focus on machine learning integration. It features a fast backtesting engine built with NumPy and accelerated with Numba, making it ideal for both rule-based and ML-driven trading strategies.

### Key Features
- **Fast Backtesting**: NumPy and Numba-accelerated engine
- **Machine Learning**: Built-in support for ML model training and integration
- **Multiple Data Sources**: Yahoo Finance, Alpaca, AKShare, and custom sources
- **Walkforward Analysis**: Robust model validation and testing
- **Bootstrap Metrics**: Statistical validation of strategy performance
- **Portfolio Optimization**: Integration with portfolio optimization libraries
- **Caching**: Smart caching for data, indicators, and models
- **Parallelization**: Multi-core support for faster computation

## Installation

### Basic Installation
```bash
# Install via pip
pip install pybroker

# Install with optional dependencies
pip install pybroker[all]

# Development installation
git clone https://github.com/edtechre/pybroker
cd pybroker
pip install -e .
```

### Dependencies
```python
# Core dependencies
numpy
pandas
numba
yfinance

# Optional dependencies
alpaca-py          # For Alpaca broker
akshare           # For Chinese market data
scikit-learn      # For machine learning
ta-lib            # For technical indicators
riskfolio-lib     # For portfolio optimization
```

## Getting Started

### Basic Setup
```python
import pybroker as pyb
from pybroker import Strategy, StrategyConfig, YFinance

# Enable caching for performance
pyb.enable_data_source_cache('my_strategy')
pyb.enable_indicator_cache('my_indicators')

# Configure initial parameters
config = StrategyConfig(
    initial_cash=100_000,
    fee_mode='percentage',
    fee_amount=0.001,  # 0.1% commission
)

# Create strategy
strategy = Strategy(
    data_source=YFinance(),
    start_date='2020-01-01',
    end_date='2023-01-01',
    config=config
)
```

### Simple Trading Strategy
```python
from pybroker import Strategy, YFinance

def buy_low(ctx):
    """Buy when price drops below previous day's low"""
    # Skip if already holding position
    if ctx.long_pos():
        return
    
    # Check for buy signal
    if ctx.bars >= 2 and ctx.close[-1] < ctx.low[-2]:
        # Buy 25% of portfolio
        ctx.buy_shares = ctx.calc_target_shares(0.25)
        ctx.buy_limit_price = ctx.close[-1] - 0.01
        ctx.hold_bars = 3  # Hold for 3 days

# Create and run strategy
strategy = Strategy(YFinance(), '2022-01-01', '2023-01-01')
strategy.add_execution(buy_low, ['AAPL', 'MSFT'])
result = strategy.backtest()
print(result.metrics_df)
```

## Data Sources

### Yahoo Finance
```python
from pybroker import YFinance

# Initialize data source
yfinance = YFinance()

# Query single symbol
df = yfinance.query('AAPL', '2022-01-01', '2023-01-01')

# Query multiple symbols
df = yfinance.query(['AAPL', 'MSFT', 'GOOGL'], '2022-01-01', '2023-01-01')

# Query with specific timeframe
df = yfinance.query('SPY', '2022-01-01', '2023-01-01', timeframe='1d')
```

### Alpaca
```python
from pybroker import Alpaca

# Initialize with credentials
alpaca = Alpaca(
    api_key='your_api_key',
    api_secret='your_api_secret',
    paper=True  # Use paper trading
)

# Query data
df = alpaca.query(
    symbols=['AAPL', 'MSFT'],
    start_date='2022-01-01',
    end_date='2023-01-01',
    timeframe='1m'  # 1-minute bars
)
```

### AKShare (Chinese Markets)
```python
import akshare

# Query Chinese stock data
df = akshare.query(
    symbols=['000001.SZ', '600000.SH'],
    start_date='2022-01-01',
    end_date='2023-01-01',
    adjust='',
    timeframe='1d'
)
```

### Custom Data Source
```python
from pybroker import DataSource
import pandas as pd

class CSVDataSource(DataSource):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
    
    def query(self, symbols, start_date, end_date, timeframe=None):
        df = pd.read_csv(self.file_path)
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter by date range
        df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
        
        # Filter by symbols
        if symbols:
            df = df[df['symbol'].isin(symbols)]
        
        return df

# Use custom data source
csv_source = CSVDataSource('data/prices.csv')
strategy = Strategy(csv_source, '2022-01-01', '2023-01-01')
```

### Direct DataFrame Usage
```python
import pandas as pd
import pybroker

# Load data into DataFrame
df = pd.read_csv('data/prices.csv')
df['date'] = pd.to_datetime(df['date'])

# Register custom columns
pybroker.register_columns('rsi', 'macd')

# Use DataFrame directly
strategy = Strategy(df, '2022-01-01', '2023-01-01')
```

## Strategy Creation

### Execution Context
```python
def trading_logic(ctx):
    """
    ctx provides access to:
    - Market data: close, open, high, low, volume
    - Position info: long_pos(), short_pos()
    - Order methods: buy_shares, sell_shares
    - Calculations: calc_target_shares()
    - Indicators: indicator('name')
    - Predictions: preds('model_name')
    """
    
    # Access price data (as numpy arrays)
    current_close = ctx.close[-1]
    previous_close = ctx.close[-2]
    
    # Check positions
    if ctx.long_pos():
        position = ctx.long_pos()
        print(f"Holding {position.shares} shares")
    
    # Place orders
    if not ctx.long_pos():
        ctx.buy_shares = 100
        ctx.buy_limit_price = current_close * 0.99
```

### Multiple Execution Functions
```python
def buy_strategy(ctx):
    if not ctx.long_pos() and ctx.close[-1] < ctx.low[-2]:
        ctx.buy_shares = ctx.calc_target_shares(0.5)
        ctx.hold_bars = 5

def short_strategy(ctx):
    if not ctx.short_pos() and ctx.close[-1] > ctx.high[-2]:
        ctx.sell_shares = 100
        ctx.hold_bars = 3

# Add different strategies to different symbols
strategy = Strategy(YFinance(), '2022-01-01', '2023-01-01')
strategy.add_execution(buy_strategy, ['AAPL', 'MSFT'])
strategy.add_execution(short_strategy, ['TSLA'])
```

### Before/After Execution Hooks
```python
def rank_stocks(ctxs: dict[str, ExecContext]):
    """Called before individual execution functions"""
    scores = {}
    for symbol, ctx in ctxs.items():
        scores[symbol] = ctx.volume[-1]
    
    # Store top symbols globally
    top_symbols = sorted(scores, key=scores.get, reverse=True)[:3]
    pyb.param('top_symbols', top_symbols)

def rebalance(ctxs: dict[str, ExecContext]):
    """Called after individual execution functions"""
    # Equal weight rebalancing
    target = 1 / len(ctxs)
    for ctx in ctxs.values():
        target_shares = ctx.calc_target_shares(target)
        pos = ctx.long_pos()
        
        if pos is None:
            ctx.buy_shares = target_shares
        elif pos.shares < target_shares:
            ctx.buy_shares = target_shares - pos.shares
        elif pos.shares > target_shares:
            ctx.sell_shares = pos.shares - target_shares

strategy.set_before_exec(rank_stocks)
strategy.set_after_exec(rebalance)
```

## Indicators

### Creating Custom Indicators
```python
import numpy as np
from numba import njit

def cmma(bar_data, lookback):
    """Close Minus Moving Average"""
    
    @njit  # Numba JIT compilation for speed
    def vec_cmma(values):
        n = len(values)
        out = np.array([np.nan for _ in range(n)])
        
        for i in range(lookback, n):
            # Calculate moving average
            ma = 0
            for j in range(i - lookback, i):
                ma += values[j]
            ma /= lookback
            # Subtract from current value
            out[i] = values[i] - ma
        return out
    
    return vec_cmma(bar_data.close)

# Register indicator
cmma_20 = pyb.indicator('cmma_20', cmma, lookback=20)
```

### Using Built-in Helpers
```python
from pybroker import highest, lowest, highv, lowv

# Highest high over period
hhv_10 = highest('hhv_10', 'high', period=10)

# Lowest low over period
llv_10 = lowest('llv_10', 'low', period=10)

# Custom indicator using helpers
def breakout_indicator(bar_data, period):
    highs = highv(bar_data.high, period)
    lows = lowv(bar_data.low, period)
    return (bar_data.close - lows) / (highs - lows)

breakout = pyb.indicator('breakout', breakout_indicator, period=20)
```

### TA-Lib Integration
```python
import talib

# Register TA-Lib indicators
rsi_14 = pyb.indicator('rsi_14', lambda data: talib.RSI(data.close, timeperiod=14))
macd = pyb.indicator('macd', lambda data: talib.MACD(data.close)[0])
bbands = pyb.indicator('bbands', lambda data: talib.BBANDS(data.close)[0])

# ROC indicator
roc_20 = pyb.indicator('roc_20', lambda data: talib.ROC(data.close, timeperiod=20))
```

### Using Indicators in Strategy
```python
def strategy_with_indicators(ctx):
    # Access indicator values
    rsi = ctx.indicator('rsi_14')
    cmma = ctx.indicator('cmma_20')
    
    # Use in trading logic
    if not ctx.long_pos():
        if rsi[-1] < 30 and cmma[-1] < 0:
            ctx.buy_shares = ctx.calc_target_shares(0.5)
    elif ctx.long_pos():
        if rsi[-1] > 70:
            ctx.sell_all_shares()

# Add strategy with indicators
strategy.add_execution(
    strategy_with_indicators,
    ['AAPL', 'MSFT'],
    indicators=[rsi_14, cmma_20]
)
```

### Indicator Sets
```python
from pybroker import IndicatorSet

# Create indicator set
indicator_set = IndicatorSet()
indicator_set.add(rsi_14, macd, bbands)

# Apply to data
df = yfinance.query('AAPL', '2022-01-01', '2023-01-01')
indicators_df = indicator_set(df)
```

## Trading Rules

### Position Management
```python
def position_management(ctx):
    # Check for existing positions
    long_pos = ctx.long_pos()
    short_pos = ctx.short_pos()
    
    if long_pos:
        # Access position details
        entry_price = long_pos.entry_price
        shares = long_pos.shares
        market_value = long_pos.market_value
        pnl = long_pos.pnl
        bars_held = long_pos.bars
        
        # Exit conditions
        if pnl > 1000 or bars_held > 20:
            ctx.sell_all_shares()
    
    if not long_pos and not short_pos:
        # Entry logic
        ctx.buy_shares = 100
```

### Order Types
```python
def order_types_example(ctx):
    # Market orders
    ctx.buy_shares = 100  # Market buy
    ctx.sell_shares = 50  # Market sell
    
    # Limit orders
    ctx.buy_shares = 100
    ctx.buy_limit_price = ctx.close[-1] * 0.99
    
    ctx.sell_shares = 50
    ctx.sell_limit_price = ctx.close[-1] * 1.01
    
    # Hold duration
    ctx.buy_shares = 100
    ctx.hold_bars = 5  # Automatically sell after 5 bars
    
    # Target allocation
    ctx.buy_shares = ctx.calc_target_shares(0.25)  # 25% of portfolio
    
    # Sell all
    ctx.sell_all_shares()  # Close long position
    ctx.cover_all_shares()  # Close short position
```

### Stop Loss and Take Profit
```python
def stops_example(ctx):
    if not ctx.long_pos():
        ctx.buy_shares = ctx.calc_target_shares(1)
        
        # Stop loss
        ctx.stop_loss_pct = 5  # 5% stop loss
        
        # Take profit
        ctx.stop_profit_pct = 10  # 10% take profit
        
        # Trailing stop
        ctx.stop_trailing_pct = 3  # 3% trailing stop
        
        # Limit prices on stops
        ctx.stop_loss_limit = ctx.close[-1] * 0.94
        ctx.stop_profit_limit = ctx.close[-1] * 1.11

def cancel_stops(ctx):
    pos = ctx.long_pos()
    if pos and pos.bars > 10:
        # Cancel stops after 10 bars
        ctx.cancel_stops(ctx.symbol)
```

### Ranking and Scoring
```python
def buy_highest_volume(ctx):
    """Buy stock with highest volume"""
    # Check if no positions across all symbols
    if not tuple(ctx.long_positions()):
        ctx.buy_shares = ctx.calc_target_shares(1)
        ctx.hold_bars = 5
        ctx.score = ctx.volume[-1]  # Set score for ranking

# Strategy will automatically select highest scoring symbol
config = StrategyConfig(max_long_positions=1)
strategy = Strategy(YFinance(), '2022-01-01', '2023-01-01', config)
strategy.add_execution(buy_highest_volume, ['AAPL', 'MSFT', 'GOOGL'])
```

## Machine Learning Integration

### Training Function
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np

def train_model(symbol, train_data, test_data):
    """Train a model to predict next day's return"""
    
    # Prepare training data
    train_data = train_data.copy()
    train_prev_close = train_data['close'].shift(1)
    train_returns = (train_data['close'] - train_prev_close) / train_prev_close
    train_data['target'] = train_returns.shift(-1)  # Next day's return
    train_data = train_data.dropna()
    
    # Features and target
    X_train = train_data[['cmma_20', 'rsi_14']]
    y_train = train_data['target']
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Test model
    test_data = test_data.copy()
    test_prev_close = test_data['close'].shift(1)
    test_returns = (test_data['close'] - test_prev_close) / test_prev_close
    test_data['target'] = test_returns.shift(-1)
    test_data = test_data.dropna()
    
    X_test = test_data[['cmma_20', 'rsi_14']]
    y_test = test_data['target']
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    print(f"{symbol} R²: {r2:.4f}")
    
    # Return model and feature columns
    return model, ['cmma_20', 'rsi_14']

# Register model
model = pyb.model('lr_model', train_model, indicators=[cmma_20, rsi_14])
```

### Using Model Predictions
```python
def ml_strategy(ctx):
    """Trade based on model predictions"""
    
    # Get model predictions
    predictions = ctx.preds('lr_model')
    
    if not ctx.long_pos():
        # Buy if positive return predicted
        if predictions[-1] > 0:
            ctx.buy_shares = 100
    else:
        # Sell if negative return predicted
        if predictions[-1] < 0:
            ctx.sell_all_shares()

# Add ML strategy
strategy.add_execution(ml_strategy, ['AAPL', 'MSFT'], models=model)
```

### Custom Model Classes
```python
from pybroker.model import Model

class CustomModel(Model):
    def __init__(self, name, train_fn, indicators):
        super().__init__(name, train_fn, indicators)
    
    def input_data_fn(self, data):
        """Custom input data preparation"""
        # For autoregressive models (ARMA, RNN)
        return prepare_sequences(data)
    
    def predict_fn(self, model, data):
        """Custom prediction logic"""
        # For ensemble or complex predictions
        return custom_predict(model, data)
```

## Backtesting

### Basic Backtest
```python
# Run backtest
result = strategy.backtest()

# Access results
print(result.metrics_df)    # Performance metrics
print(result.trades)         # Individual trades
print(result.orders)         # Order execution details
print(result.positions)      # Position history
print(result.portfolio)      # Portfolio value over time
```

### Backtest with Warmup
```python
# Skip initial bars for indicator calculation
result = strategy.backtest(warmup=20)
```

### Filtered Backtesting
```python
# Backtest specific days
result = strategy.backtest(days='mon,wed,fri')

# Backtest specific time range
result = strategy.backtest(between_time='09:30-15:30')

# Combine filters
result = strategy.backtest(
    days='mon,tue,wed,thu,fri',
    between_time='09:30-16:00',
    warmup=20
)
```

### Train/Test Split
```python
# Use first 50% for training, rest for testing
result = strategy.backtest(train_size=0.5)
```

## Walkforward Analysis

### Basic Walkforward
```python
# Walkforward analysis for robust model testing
result = strategy.walkforward(
    windows=5,          # Number of windows
    train_size=0.6,     # 60% train, 40% test
    lookahead=1,        # Bars to look ahead (match model)
    timeframe='1d'      # Data timeframe
)

print(result.metrics_df)
```

### Advanced Walkforward
```python
result = strategy.walkforward(
    windows=10,
    train_size=0.7,
    lookahead=1,
    warmup=20,          # Warmup period for indicators
    calc_bootstrap=True # Calculate bootstrap metrics
)

# Access window-specific results
for i, window in enumerate(result.windows):
    print(f"Window {i}: Train {window.train_start} to {window.train_end}")
    print(f"         Test {window.test_start} to {window.test_end}")
```

## Position Management

### Position Sizing
```python
def position_sizing(ctx):
    # Fixed shares
    ctx.buy_shares = 100
    
    # Percentage of portfolio
    ctx.buy_shares = ctx.calc_target_shares(0.25)  # 25% allocation
    
    # Dollar amount
    shares = 10000 / ctx.close[-1]  # $10,000 position
    ctx.buy_shares = int(shares)
    
    # Risk-based sizing (2% risk per trade)
    account_value = ctx.total_equity
    risk_amount = account_value * 0.02
    stop_distance = ctx.close[-1] * 0.05  # 5% stop
    ctx.buy_shares = int(risk_amount / stop_distance)
```

### Custom Position Sizing Handler
```python
def volatility_sizing(ctx):
    """Size positions based on inverse volatility"""
    
    # Get all buy signals
    signals = tuple(ctx.signals("buy"))
    if not signals:
        return
    
    # Calculate inverse volatility for each signal
    total_inv_vol = 0
    inv_vols = {}
    
    for signal in signals:
        volatility = np.std(signal.bar_data.close[-20:])
        inv_vol = 1 / volatility if volatility > 0 else 0
        inv_vols[signal] = inv_vol
        total_inv_vol += inv_vol
    
    # Allocate based on inverse volatility
    for signal in signals:
        if total_inv_vol > 0:
            allocation = inv_vols[signal] / total_inv_vol
            shares = ctx.calc_target_shares(
                allocation,
                signal.bar_data.close[-1],
                cash=ctx.total_equity * 0.95
            )
            ctx.set_shares(signal, shares)

strategy.set_pos_size_handler(volatility_sizing)
```

### Multi-Asset Position Management
```python
def manage_multiple_positions(ctx):
    # Get all positions
    all_positions = tuple(ctx.positions())
    long_positions = tuple(ctx.long_positions())
    short_positions = tuple(ctx.short_positions())
    
    # Check specific symbol
    aapl_pos = ctx.long_pos('AAPL')
    
    # Manage based on total exposure
    total_long_value = sum(pos.market_value for pos in long_positions)
    
    if total_long_value > ctx.total_equity * 0.8:
        # Reduce exposure if over 80%
        for pos in long_positions:
            if pos.pnl_pct < 0:
                ctx.sell_shares = pos.shares
                break
```

## Risk Management

### Stop Losses
```python
def stop_loss_management(ctx):
    if not ctx.long_pos():
        ctx.buy_shares = 100
        
        # Percentage stop loss
        ctx.stop_loss_pct = 5
        
        # Dollar stop loss
        ctx.stop_loss_price = ctx.close[-1] - 2.0
        
        # ATR-based stop
        atr = ctx.indicator('atr_14')[-1]
        ctx.stop_loss_price = ctx.close[-1] - (2 * atr)
```

### Trailing Stops
```python
def trailing_stop_management(ctx):
    if not ctx.long_pos():
        ctx.buy_shares = 100
        
        # Percentage trailing stop
        ctx.stop_trailing_pct = 3
        
        # Dollar trailing stop
        ctx.stop_trailing_amount = 1.5
        
        # Chandelier exit (ATR-based)
        atr = ctx.indicator('atr_14')[-1]
        ctx.stop_trailing_amount = 3 * atr
```

### Position Limits
```python
config = StrategyConfig(
    initial_cash=100_000,
    max_long_positions=5,      # Maximum 5 long positions
    max_short_positions=3,      # Maximum 3 short positions
    max_position_size=0.2       # Max 20% in single position
)
```

### Margin Control
```python
def margin_control(ctx):
    """Control margin usage for short selling"""
    
    margin_requirement = 0.25  # 25% margin requirement
    max_margin = ctx.total_equity / margin_requirement - ctx.total_equity
    
    if not ctx.short_pos():
        available_margin = max_margin - ctx.total_margin
        ctx.sell_shares = ctx.calc_target_shares(0.5, cash=available_margin)
        ctx.hold_bars = 5
```

## Portfolio Optimization

### Equal Weight Rebalancing
```python
def equal_weight_rebalance(ctxs: dict[str, ExecContext]):
    """Rebalance to equal weights monthly"""
    
    # Check if it's the start of a new month
    dt = list(ctxs.values())[0].dt
    if dt.day != 1:
        return
    
    # Calculate equal weight
    target = 1 / len(ctxs)
    
    # Set target shares for each symbol
    for symbol, ctx in ctxs.items():
        target_shares = ctx.calc_target_shares(target)
        pos = ctx.long_pos()
        
        if pos is None:
            ctx.buy_shares = target_shares
        elif pos.shares != target_shares:
            diff = target_shares - pos.shares
            if diff > 0:
                ctx.buy_shares = diff
            else:
                ctx.sell_shares = -diff

strategy.set_after_exec(equal_weight_rebalance)
```

### Minimum Risk Portfolio
```python
import pandas as pd
import riskfolio as rp

def minimum_risk_optimization(ctxs: dict[str, ExecContext]):
    """Optimize for minimum risk using CVaR"""
    
    # Calculate returns
    lookback = 252  # One year
    prices = {}
    for symbol, ctx in ctxs.items():
        prices[symbol] = ctx.adj_close[-lookback:]
    
    df = pd.DataFrame(prices)
    returns = df.pct_change().dropna()
    
    # Create portfolio object
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu='hist', method_cov='hist')
    
    # Optimize for minimum CVaR
    weights = port.optimization(
        model='Classic',
        rm='CVaR',           # Risk measure
        obj='MinRisk',       # Objective
        rf=0,               # Risk-free rate
        l=0,                # Risk aversion
        hist=True           # Use historical scenarios
    )
    
    # Set target allocations
    for symbol in ctxs.keys():
        target = weights.T[symbol].values[0]
        ctx = ctxs[symbol]
        target_shares = ctx.calc_target_shares(target)
        
        pos = ctx.long_pos()
        if pos is None:
            ctx.buy_shares = target_shares
        else:
            diff = target_shares - pos.shares
            if diff > 0:
                ctx.buy_shares = diff
            elif diff < 0:
                ctx.sell_shares = -diff

strategy.set_after_exec(minimum_risk_optimization)
```

### Rotational Strategy
```python
def rank_by_momentum(ctxs: dict[str, ExecContext]):
    """Rank stocks by momentum"""
    scores = {}
    for symbol, ctx in ctxs.items():
        # Calculate momentum (20-day ROC)
        roc = ctx.indicator('roc_20')[-1]
        scores[symbol] = roc
    
    # Get top N stocks
    n_stocks = 3
    sorted_symbols = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_symbols = [s[0] for s in sorted_symbols[:n_stocks]]
    
    pyb.param('top_symbols', top_symbols)

def rotate_portfolio(ctx):
    """Buy top momentum stocks, sell others"""
    top_symbols = pyb.param('top_symbols')
    
    if ctx.long_pos():
        # Sell if not in top stocks
        if ctx.symbol not in top_symbols:
            ctx.sell_all_shares()
    else:
        # Buy if in top stocks
        if ctx.symbol in top_symbols:
            allocation = 1 / len(top_symbols)
            ctx.buy_shares = ctx.calc_target_shares(allocation)
            ctx.score = ctx.indicator('roc_20')[-1]

strategy.set_before_exec(rank_by_momentum)
strategy.add_execution(rotate_portfolio, symbols, indicators=roc_20)
```

## Performance Metrics

### Basic Metrics
```python
result = strategy.backtest()

# Access metrics
metrics = result.metrics_df
print(f"Total Return: {metrics['total_return'].values[0]:.2%}")
print(f"Sharpe Ratio: {metrics['sharpe'].values[0]:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown'].values[0]:.2%}")
print(f"Win Rate: {metrics['win_rate'].values[0]:.2%}")

# All available metrics
print(metrics.columns.tolist())
```

### Custom Metrics
```python
# Calculate custom metrics from trades
trades = result.trades
if not trades.empty:
    # Average trade duration
    avg_duration = trades['bars'].mean()
    
    # Profit factor
    wins = trades[trades['pnl'] > 0]['pnl'].sum()
    losses = abs(trades[trades['pnl'] < 0]['pnl'].sum())
    profit_factor = wins / losses if losses > 0 else float('inf')
    
    # Maximum consecutive losses
    trades['is_loss'] = trades['pnl'] < 0
    max_consecutive_losses = trades.groupby(
        (trades['is_loss'] != trades['is_loss'].shift()).cumsum()
    )['is_loss'].sum().max()
```

## Bootstrap Analysis

### Enable Bootstrap Metrics
```python
config = StrategyConfig(
    initial_cash=100_000,
    bootstrap_samples=1000,      # Number of bootstrap samples
    bootstrap_sample_size=100    # Size of each sample
)

# Run backtest with bootstrap
result = strategy.backtest(calc_bootstrap=True)

# Access bootstrap results
print(result.bootstrap.conf_intervals)  # Confidence intervals
print(result.bootstrap.drawdown_conf)   # Drawdown confidence
```

### Interpreting Bootstrap Results
```python
# Confidence intervals for key metrics
conf_intervals = result.bootstrap.conf_intervals

for metric, intervals in conf_intervals.items():
    lower = intervals['lower']
    upper = intervals['upper']
    mean = intervals['mean']
    print(f"{metric}: {mean:.3f} [{lower:.3f}, {upper:.3f}]")

# Drawdown confidence levels
drawdown_conf = result.bootstrap.drawdown_conf
print(f"95% confidence max drawdown won't exceed: {drawdown_conf['95%']:.2%}")
```

## Order Execution

### Order Configuration
```python
config = StrategyConfig(
    buy_delay=1,           # Delay buy orders by 1 bar
    sell_delay=0,          # No delay for sells
    buy_fill_price='open', # Fill at open price
    sell_fill_price='close' # Fill at close price
)
```

### Slippage Models
```python
from pybroker import RandomSlippageModel, FixedSlippageModel

# Random slippage
slippage = RandomSlippageModel(
    min_pct=0.1,   # Minimum 0.1% slippage
    max_pct=0.5    # Maximum 0.5% slippage
)
strategy.set_slippage_model(slippage)

# Fixed slippage
slippage = FixedSlippageModel(pct=0.2)  # Fixed 0.2% slippage
strategy.set_slippage_model(slippage)
```

### Pending Orders
```python
def manage_pending_orders(ctx):
    # Check pending orders
    pending = tuple(ctx.pending_orders())
    
    if pending:
        for order in pending:
            print(f"Pending: {order.type} {order.shares} shares at {order.limit_price}")
        
        # Cancel if price moved too far
        if ctx.close[-1] > pending[0].limit_price * 1.02:
            ctx.cancel_all_pending_orders(ctx.symbol)
    
    # Place new order with delay
    if not pending and not ctx.long_pos():
        ctx.buy_shares = 100
        ctx.buy_limit_price = ctx.close[-1] * 0.98
```

## Advanced Features

### Multi-Symbol Operations
```python
def pairs_trading(ctxs: dict[str, ExecContext]):
    """Trade pairs based on spread"""
    
    ctx_a = ctxs['AAPL']
    ctx_b = ctxs['MSFT']
    
    # Calculate spread
    spread = ctx_a.close[-1] / ctx_b.close[-1]
    ma_spread = np.mean([ctx_a.close[i] / ctx_b.close[i] 
                         for i in range(-20, 0)])
    
    # Trade based on spread deviation
    if spread > ma_spread * 1.02:
        # Spread too high: short A, long B
        if not ctx_a.short_pos():
            ctx_a.sell_shares = 100
        if not ctx_b.long_pos():
            ctx_b.buy_shares = 100
    elif spread < ma_spread * 0.98:
        # Spread too low: long A, short B
        if not ctx_a.long_pos():
            ctx_a.buy_shares = 100
        if not ctx_b.short_pos():
            ctx_b.sell_shares = 100

strategy.set_after_exec(pairs_trading)
```

### Session Data Persistence
```python
def strategy_with_state(ctx):
    """Maintain state across bars"""
    
    # Initialize session data
    if 'entry_count' not in ctx.session:
        ctx.session['entry_count'] = 0
        ctx.session['total_profit'] = 0
    
    # Use and update session data
    if not ctx.long_pos():
        if ctx.session['entry_count'] < 5:
            ctx.buy_shares = 100
            ctx.hold_bars = 10
            ctx.session['entry_count'] += 1
    else:
        pos = ctx.long_pos()
        if pos.pnl > 0:
            ctx.session['total_profit'] += pos.pnl
            ctx.sell_all_shares()
```

### Cross-Symbol Data Access
```python
def correlation_strategy(ctx):
    """Access data from other symbols"""
    
    if ctx.symbol == 'AAPL':
        # Get data from another symbol
        msft_data = ctx.foreign('MSFT')
        msft_close = msft_data.close[-1]
        
        # Get indicator from another symbol
        msft_rsi = ctx.indicator('rsi_14', 'MSFT')[-1]
        
        # Trade based on correlation
        if ctx.close[-1] < ctx.low[-2] and msft_close > msft_data.high[-2]:
            ctx.buy_shares = 100
```

### Global Parameters
```python
# Set global parameters
pyb.param('risk_level', 0.02)
pyb.param('lookback', 20)

def use_global_params(ctx):
    risk = pyb.param('risk_level')
    lookback = pyb.param('lookback')
    
    # Use in calculations
    volatility = np.std(ctx.close[-lookback:])
    position_size = (ctx.total_equity * risk) / volatility
    ctx.buy_shares = int(position_size)
```

## Configuration

### Strategy Configuration
```python
config = StrategyConfig(
    # Capital and fees
    initial_cash=100_000,
    fee_mode='percentage',      # 'fixed' or 'percentage'
    fee_amount=0.001,           # 0.1% commission
    
    # Position limits
    max_long_positions=10,
    max_short_positions=5,
    
    # Order execution
    buy_delay=0,
    sell_delay=0,
    enable_fractional_shares=True,
    
    # Exit behavior
    exit_on_last_bar=True,
    exit_sell_fill_price='close',
    exit_cover_fill_price='close',
    
    # Bootstrap settings
    bootstrap_samples=1000,
    bootstrap_sample_size=100,
    
    # Annualization
    bars_per_year=252,          # For daily data
    
    # Debugging
    return_signals=True,
    return_stops=True
)
```

### Fill Price Options
```python
from pybroker import PriceType

def custom_fill_prices(ctx):
    # Available price types
    ctx.buy_fill_price = PriceType.OPEN
    ctx.buy_fill_price = PriceType.HIGH
    ctx.buy_fill_price = PriceType.LOW
    ctx.buy_fill_price = PriceType.CLOSE
    ctx.buy_fill_price = PriceType.AVERAGE  # OHLC average
    
    # Custom price
    ctx.buy_fill_price = ctx.close[-1] * 1.001  # 0.1% above close
```

## Live Trading

### Alpaca Integration
```python
from pybroker import Alpaca

# Initialize for live trading
alpaca = Alpaca(
    api_key='your_api_key',
    api_secret='your_secret',
    paper=False  # Set to False for live trading
)

# Create strategy with live data
strategy = Strategy(
    data_source=alpaca,
    start_date='2023-01-01',
    end_date='2023-12-31'
)

# Execute live (same as backtest)
strategy.add_execution(trading_logic, symbols)
result = strategy.execute()  # For live execution
```

### Paper Trading
```python
# Paper trading with Alpaca
alpaca_paper = Alpaca(
    api_key='paper_api_key',
    api_secret='paper_secret',
    paper=True
)

# Test strategy with paper trading
strategy = Strategy(alpaca_paper, start_date='today')
strategy.add_execution(trading_logic, symbols)
```

## Best Practices

### Performance Optimization
```python
# 1. Enable caching
pyb.enable_data_source_cache('cache_dir')
pyb.enable_indicator_cache('indicators_cache')
pyb.enable_model_cache('models_cache')

# 2. Use Numba JIT
@njit
def fast_calculation(data):
    # Numba-accelerated code
    return result

# 3. Vectorize operations
# Good
returns = (prices[1:] - prices[:-1]) / prices[:-1]

# Bad
returns = []
for i in range(1, len(prices)):
    returns.append((prices[i] - prices[i-1]) / prices[i-1])

# 4. Minimize data copies
df = df.copy()  # Only when necessary
```

### Strategy Development Workflow
```python
# 1. Start simple
def simple_strategy(ctx):
    if not ctx.long_pos() and ctx.close[-1] < ctx.low[-2]:
        ctx.buy_shares = 100
        ctx.hold_bars = 5

# 2. Add indicators
def strategy_with_indicators(ctx):
    rsi = ctx.indicator('rsi_14')
    if not ctx.long_pos() and rsi[-1] < 30:
        ctx.buy_shares = ctx.calc_target_shares(0.25)

# 3. Add risk management
def strategy_with_stops(ctx):
    if not ctx.long_pos() and ctx.indicator('rsi_14')[-1] < 30:
        ctx.buy_shares = ctx.calc_target_shares(0.25)
        ctx.stop_loss_pct = 5
        ctx.stop_profit_pct = 10

# 4. Validate with walkforward
result = strategy.walkforward(windows=5, train_size=0.6)

# 5. Analyze with bootstrap
result = strategy.backtest(calc_bootstrap=True)
print(result.bootstrap.conf_intervals)
```

### Common Patterns
```python
# Pattern 1: Momentum Strategy
def momentum_strategy(ctx):
    roc = ctx.indicator('roc_20')
    if not ctx.long_pos() and roc[-1] > roc[-2]:
        ctx.buy_shares = ctx.calc_target_shares(0.5)
        ctx.stop_trailing_pct = 5

# Pattern 2: Mean Reversion
def mean_reversion(ctx):
    bb_lower = ctx.indicator('bb_lower')
    bb_upper = ctx.indicator('bb_upper')
    
    if not ctx.long_pos() and ctx.close[-1] < bb_lower[-1]:
        ctx.buy_shares = ctx.calc_target_shares(0.3)
    elif ctx.long_pos() and ctx.close[-1] > bb_upper[-1]:
        ctx.sell_all_shares()

# Pattern 3: Breakout Strategy
def breakout_strategy(ctx):
    high_20 = ctx.indicator('high_20')
    if not ctx.long_pos() and ctx.close[-1] > high_20[-2]:
        ctx.buy_shares = ctx.calc_target_shares(1)
        ctx.stop_loss_pct = 3
        ctx.hold_bars = 10
```

### Debugging Tips
```python
# 1. Print debug information
def debug_strategy(ctx):
    print(f"Symbol: {ctx.symbol}, Date: {ctx.dt}")
    print(f"Close: {ctx.close[-1]}, Volume: {ctx.volume[-1]}")
    
    if ctx.long_pos():
        pos = ctx.long_pos()
        print(f"Position: {pos.shares} shares, PnL: {pos.pnl:.2f}")

# 2. Use config for debugging
config = StrategyConfig(
    return_signals=True,  # Return all signals
    return_stops=True     # Return stop information
)

# 3. Examine specific dates
result = strategy.backtest(between_time='2023-01-01-2023-01-31')

# 4. Check intermediate results
result = strategy.backtest()
print(result.signals)  # All buy/sell signals
print(result.stops)    # Stop loss/profit triggers
```

## Conclusion

PyBroker provides a comprehensive framework for algorithmic trading with strong support for:

1. **Fast Backtesting**: NumPy/Numba accelerated engine
2. **Machine Learning**: Seamless integration of ML models
3. **Risk Management**: Built-in stops, position sizing, and portfolio optimization
4. **Statistical Validation**: Bootstrap analysis and walkforward testing
5. **Flexibility**: Support for custom indicators, models, and data sources

Key advantages:
- **Performance**: Caching and parallelization for speed
- **Reliability**: Statistical validation through bootstrapping
- **Extensibility**: Easy to add custom components
- **Integration**: Works with popular libraries (scikit-learn, TA-Lib, etc.)

For more information:
- [GitHub Repository](https://github.com/edtechre/pybroker)
- [Documentation](https://www.pybroker.com)
- [Examples](https://github.com/edtechre/pybroker/tree/master/docs/source/notebooks)