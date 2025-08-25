# PyBroker Data Integration Research Report
**Date:** 2025-08-24  
**Objective:** Understand PyBroker's data management system for real historical data integration

## PyBroker Data Architecture Overview

### **Data Sources Available**
PyBroker supports multiple data sources for historical data:
- **YFinance** - Yahoo Finance (most common for backtesting)
- **Alpaca** - Real-time and historical market data
- **AlpacaCrypto** - Cryptocurrency data
- **AKShare** - Chinese market data
- **Custom DataSource** - User-defined data sources (CSV, databases, APIs)
- **Direct DataFrame** - Pandas DataFrame input

### **Key PyBroker Data Management Components**

#### 1. **Strategy Class Data Integration**
```python
# PyBroker Strategy accepts data source in constructor
strategy = Strategy(YFinance(), start_date='1/1/2022', end_date='7/1/2022')

# Alternative: Direct DataFrame usage
df = pd.read_csv('historical_data.csv')
strategy = Strategy(df, start_date='1/1/2022', end_date='7/1/2022')
```

#### 2. **Data Source Query Pattern**
```python
# Data sources have standardized query() method
yfinance = YFinance()
df = yfinance.query(['AAPL', 'MSFT'], start_date='3/1/2021', end_date='3/1/2022')

# Returns standardized DataFrame format:
# Columns: symbol, date, open, high, low, close, volume, adj_close
```

#### 3. **Data Caching System**
```python
# PyBroker has built-in caching for performance
pybroker.enable_data_source_cache('my_strategy')
# Caches data per unique combination of ticker + date range
# Dramatically speeds up repeated backtests
```

## **Critical Discovery: PyBroker's Backtest Data Flow**

### **How PyBroker Manages Historical Data During Backtests**

#### 1. **Data Loading Phase**
```python
# When Strategy.backtest() is called:
# 1. Strategy loads ENTIRE historical dataset for all symbols
# 2. Data is stored internally in the Strategy object
# 3. Data includes ALL bars from start_date to end_date
```

#### 2. **Bar-by-Bar Processing**
```python
# During backtest execution:
# 1. Strategy iterates through each date/bar chronologically
# 2. For each bar, ExecContext provides:
#    - ctx.bars: Current bar index (position in dataset)
#    - ctx.close[-1]: Current bar's close price
#    - ctx.close[-2]: Previous bar's close price
#    - ctx.foreign('SYMBOL'): Access other symbol's current bar data
```

#### 3. **Historical Data Access Within ExecContext**
```python
def exec_fn(ctx: ExecContext):
    # Current position in backtest (bar index)
    current_bar_index = ctx.bars
    
    # Access historical price data (all previous bars available)
    last_10_closes = ctx.close[-10:]  # Last 10 closing prices
    last_high = ctx.high[-1]          # Current bar's high
    previous_low = ctx.low[-2]        # Previous bar's low
    
    # Access indicators calculated on historical data
    moving_avg = ctx.indicator('ma_20')[-1]  # Current MA value
    previous_ma = ctx.indicator('ma_20')[-2]  # Previous MA value
```

## **Key Integration Points for TSX Strategy Bridge**

### **1. Data Structure in PyBroker**
```python
# PyBroker stores data as pandas DataFrame internally
# Standard format:
{
    'symbol': str,     # Ticker symbol
    'date': datetime,  # Bar timestamp
    'open': float,     # Opening price
    'high': float,     # High price
    'low': float,      # Low price
    'close': float,    # Closing price
    'volume': int,     # Volume
    'adj_close': float # Adjusted closing price
}
```

### **2. Current Bar Tracking**
```python
# PyBroker tracks current position during backtest
class Strategy:
    def __init__(self, data_source, start_date, end_date):
        self._data = None          # Full historical dataset
        self._current_bar_idx = 0  # Current position in backtest
        
    def backtest(self):
        # Iterate through each bar chronologically
        for bar_idx in range(len(self._data)):
            self._current_bar_idx = bar_idx
            # Execute strategy for current bar
            self._execute_strategies(bar_idx)
```

### **3. Historical Data Slicing for Strategies**
```python
# For TSX strategies requesting historical data:
# Need to slice data from current backtest position backwards

def get_historical_slice(strategy_instance, symbol, bars_back):
    """Get historical data slice for TSX strategy bootstrap"""
    
    # Get current position in backtest
    current_idx = strategy_instance._current_bar_idx
    
    # Calculate slice boundaries
    start_idx = max(0, current_idx - bars_back + 1)
    end_idx = current_idx + 1
    
    # Get symbol's data slice
    symbol_data = strategy_instance._data[
        strategy_instance._data['symbol'] == symbol
    ]
    
    # Return historical slice (bars_back bars leading up to current)
    historical_slice = symbol_data.iloc[start_idx:end_idx]
    
    return historical_slice
```

## **Integration Architecture Design**

### **Proposed TSX-PyBroker Bridge Architecture**
```python
class TSXStrategyBridge:
    def __init__(self, strategy_path, pybroker_strategy):
        self.strategy_path = strategy_path
        self.pybroker_strategy = pybroker_strategy  # PyBroker Strategy instance
        self.current_bar_index = 0
        
        # Historical data service with real PyBroker data access
        self.historical_service = RealHistoricalDataService(
            pybroker_strategy=pybroker_strategy
        )
        
    def process_bar(self, bar_index, bar_data):
        """Called by PyBroker for each bar during backtest"""
        self.current_bar_index = bar_index
        
        # Update historical service with current position
        self.historical_service.update_current_position(bar_index)
        
        # Send market data to TSX strategy
        # TSX strategy can now request historical data via Redis
        # Historical service will provide real data from PyBroker
        
        return self._process_tsx_strategy(bar_data)
```

### **Real Historical Data Service**
```python
class RealHistoricalDataService:
    def __init__(self, pybroker_strategy):
        self.pybroker_strategy = pybroker_strategy
        self.current_bar_index = 0
        
    def handle_historical_request(self, request):
        """Handle TSX strategy historical data request with REAL data"""
        
        symbol = request.get('symbol')
        bars_back = request.get('barsBack', 50)
        
        # Get REAL historical data from PyBroker's dataset
        historical_slice = self._get_real_historical_data(symbol, bars_back)
        
        # Convert to TSX V5 format
        tsx_bars = self._convert_to_tsx_format(historical_slice)
        
        # Send real data response
        return {
            'requestId': request.get('requestId'),
            'success': True,
            'data': {'bars': tsx_bars},
            'timestamp': datetime.now().isoformat() + 'Z'
        }
    
    def _get_real_historical_data(self, symbol, bars_back):
        """Get real historical data slice from PyBroker's dataset"""
        
        # Access PyBroker's internal data
        full_data = self.pybroker_strategy._data
        symbol_data = full_data[full_data['symbol'] == symbol]
        
        # Calculate slice boundaries from current backtest position
        end_idx = self.current_bar_index + 1
        start_idx = max(0, end_idx - bars_back)
        
        # Return real historical slice
        return symbol_data.iloc[start_idx:end_idx]
    
    def _convert_to_tsx_format(self, df):
        """Convert PyBroker DataFrame to TSX V5 bar format"""
        tsx_bars = []
        
        for _, row in df.iterrows():
            tsx_bar = {
                't': row['date'].isoformat() + 'Z',
                'o': float(row['open']),
                'h': float(row['high']),
                'l': float(row['low']),
                'c': float(row['close']),
                'v': int(row['volume'])
            }
            tsx_bars.append(tsx_bar)
        
        return tsx_bars
```

## **Implementation Requirements**

### **1. PyBroker Integration Points**
- **Access Strategy._data**: Need access to PyBroker's internal dataset
- **Track Current Bar Index**: Synchronize with PyBroker's backtest progress  
- **Historical Slicing Logic**: Implement proper data slicing from current position
- **Format Conversion**: Convert PyBroker DataFrame to TSX V5 format

### **2. TSX Bridge Modifications Required**
```python
# Current TSX Bridge needs major modifications:

class TSXStrategyBridge:
    # OLD (with fake data):
    def __init__(self, strategy_path, config):
        self.fake_bootstrap = FakeDataGenerator()  # REMOVE
    
    # NEW (with PyBroker integration):
    def __init__(self, strategy_path, pybroker_strategy, config):
        self.pybroker_strategy = pybroker_strategy  # ADD
        self.real_bootstrap = RealHistoricalDataService(pybroker_strategy)  # ADD
```

### **3. PyBroker Strategy Execution Flow**
```python
# Integrated execution flow:

def create_integrated_strategy():
    # 1. Create PyBroker Strategy with real data source
    pybroker_strategy = Strategy(YFinance(), start_date='1/1/2022', end_date='1/1/2023')
    
    # 2. Create TSX Bridge with PyBroker integration
    tsx_bridge = TSXStrategyBridge('path/to/ema_strategy.js', pybroker_strategy)
    
    # 3. Add execution function that uses TSX Bridge
    def tsx_execution_wrapper(ctx):
        # This is called by PyBroker for each bar
        signal = tsx_bridge.process_bar(ctx.bars, {
            'open': ctx.open[-1],
            'high': ctx.high[-1], 
            'low': ctx.low[-1],
            'close': ctx.close[-1],
            'volume': ctx.volume[-1],
            'timestamp': ctx.date
        })
        
        # Process signal from TSX strategy
        if signal and signal.get('action') == 'BUY':
            ctx.buy_shares = 100
        elif signal and signal.get('action') == 'SELL':
            ctx.sell_all_shares()
    
    # 4. Run backtest with integrated TSX strategy
    pybroker_strategy.add_execution(tsx_execution_wrapper, ['NQ'])
    result = pybroker_strategy.backtest()
    
    return result
```

## **Next Steps for Implementation**

### **Phase 1A: PyBroker Data Access Proof-of-Concept**
1. Create test script to access PyBroker Strategy's internal data
2. Verify data format and structure  
3. Test historical data slicing from current bar position
4. Confirm data availability during backtest execution

### **Phase 1B: Real Historical Data Service**
1. Implement RealHistoricalDataService class
2. Add PyBroker data manager integration
3. Test real data serving vs fake data serving
4. Verify TSX V5 format conversion accuracy

### **Phase 1C: Enhanced TSX Bridge**
1. Modify TSXStrategyBridge for PyBroker integration
2. Add current bar position tracking
3. Replace fake bootstrap service with real data service
4. Test end-to-end integration

### **Success Criteria**
- ✅ TSX strategies receive REAL historical market data
- ✅ Historical data reflects actual market conditions leading up to current backtest bar
- ✅ Strategy bootstrap and signal generation based on real market patterns
- ✅ Backtesting results meaningful for trading analysis

## **Critical Findings Summary**

1. **PyBroker stores complete historical dataset** - All data available during backtest
2. **Current bar tracking** - PyBroker maintains position in dataset via bar index  
3. **Historical slicing possible** - Can extract previous N bars from current position
4. **Standard DataFrame format** - Easy conversion to TSX V5 format required
5. **Integration architecture clear** - TSX Bridge needs PyBroker Strategy reference

The fake data generation approach was fundamentally wrong - PyBroker already has all the real historical data we need. The solution is to integrate the bootstrap service directly with PyBroker's data management system.

**Ready to proceed with proof-of-concept implementation.**