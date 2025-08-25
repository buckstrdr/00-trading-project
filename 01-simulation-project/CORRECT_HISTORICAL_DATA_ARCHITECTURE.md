# CORRECT Historical Data Architecture - Real Data from PyBroker

## Current Problem: Fake Data Generation ❌

```
┌─────────────────┐    Fake Data Request    ┌─────────────────────┐
│   TSX Strategy  │ ──────────────────────▶ │  Bootstrap Service  │
│                 │                         │                     │
│  - Requests     │    Fake OHLCV Response  │  - Generates FAKE   │
│    historical   │ ◀────────────────────── │    synthetic data   │
│    data         │                         │  - NOT real market  │
│                 │                         │    data             │
│  - Gets fake    │                         │  - Unrealistic      │
│    data         │                         │    price movements  │
│  - Makes        │                         │                     │
│    decisions    │                         │                     │
│    on fake data │                         │                     │
└─────────────────┘                         └─────────────────────┘
```

**Issues with Current Implementation:**
- Strategies make trading decisions based on **synthetic/fake data**
- Backtesting results are **meaningless** - not based on real market conditions
- **No correlation** with actual market behavior
- **Defeats the purpose** of backtesting against historical market data

## CORRECT Architecture: Real Data from PyBroker ✅

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PyBroker Backtesting Engine                           │
│                                                                                 │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐ │
│  │   Historical Data   │    │   Market Data       │    │  TSX Strategy       │ │
│  │   Files/Database    │    │   Manager           │    │  Bridge             │ │
│  │                     │    │                     │    │                     │ │
│  │  - Real OHLCV data  │    │  - Current bar      │    │  - Manages TSX      │ │
│  │  - NYSE/NASDAQ/etc  │    │  - Historical slice │    │    strategy         │ │
│  │  - Multiple         │    │  - Bar indexing     │    │  - Handles requests │ │
│  │    timeframes       │    │                     │    │                     │ │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘ │
│             │                         │                          │             │
│             └─────────────────────────┼──────────────────────────┘             │
│                                       │                                        │
└───────────────────────────────────────┼────────────────────────────────────────┘
                                        │
                            Redis Pub/Sub Server
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
             ┌──────────▼─────────┐    │    ┌──────────▼─────────┐
             │                    │    │    │                    │
             │  TSX Strategy      │    │    │   MockTradingBot   │
             │  (Node.js)         │    │    │   (Node.js)        │
             │                    │    │    │                    │
             │ - Requests REAL    │    │    │ - Forwards         │
             │   historical data  │    │    │   requests         │
             │ - Gets actual      │    │    │                    │
             │   market bars      │    │    │                    │
             │ - Makes realistic  │    │    │                    │
             │   trading decisions│    │    │                    │
             └────────────────────┘    │    └────────────────────┘
                                       │
```

## Corrected Data Flow

### 1. Historical Data Request Flow:
```
┌─────────────────┐                                    ┌─────────────────┐
│   TSX Strategy  │                                    │  PyBroker       │
│                 │  1. Historical Data Request        │  Bridge         │
│  - Needs 50     │ ────────────────────────────────▶  │                 │
│    bars for EMA │    Redis: aggregator:historical-   │  - Has access   │
│    calculation  │    data:request                     │    to real      │
│                 │                                     │    market data  │
│                 │  {                                  │  - Current bar  │
│                 │    requestId: "ema-123",            │    index: 1000  │
│                 │    symbol: "NQ",                    │  - Can slice    │
│                 │    barsBack: 50                     │    bars 950-999 │
│                 │  }                                  │                 │
│                 │                                     │                 │
│                 │  2. Real Historical Data Response   │                 │
│                 │ ◀────────────────────────────────── │                 │
│                 │    Redis: aggregator:historical-   │                 │
│                 │    data:response                    │                 │
│                 │                                     │                 │
│  - Receives     │  {                                  │                 │
│    REAL market  │    requestId: "ema-123",            │                 │
│    data         │    success: true,                   │                 │
│  - Calculates   │    data: {                          │                 │
│    EMAs on      │      bars: [                        │                 │
│    actual       │        // REAL market data from    │                 │
│    prices       │        // PyBroker's dataset       │                 │
│  - Makes        │        {t: "2023-01-03T09:30:00Z", │                 │
│    realistic    │         o: 11250.25,               │                 │
│    decisions    │         h: 11267.50,               │                 │
│                 │         l: 11245.75,               │                 │
│                 │         c: 11261.00,               │                 │
│                 │         v: 156789},                │                 │
│                 │        // ... 49 more REAL bars    │                 │
│                 │      ]                              │                 │
│                 │    }                                │                 │
│                 │  }                                  │                 │
└─────────────────┘                                    └─────────────────┘
```

## Required Implementation Changes

### 1. Remove Fake Data Generator ❌
```python
# REMOVE THIS ENTIRE METHOD:
def _generate_historical_bars(self, symbol, bars_back, interval, interval_type):
    """
    Generate realistic historical OHLCV data for bootstrap  # FAKE DATA!
    """
    # This entire method generates FAKE data and must be removed
```

### 2. Integrate with PyBroker Data Source ✅
```python
class HistoricalDataService:
    """
    Provides REAL historical data from PyBroker's dataset
    """
    
    def __init__(self, pybroker_data_manager, redis_client):
        self.data_manager = pybroker_data_manager  # PyBroker's data source
        self.redis_client = redis_client
        self.current_bar_index = 0  # Current position in backtest
    
    def _handle_historical_request(self, request):
        """Handle historical data request with REAL data"""
        request_id = request.get('requestId')
        symbol = request.get('symbol')
        bars_back = request.get('barsBack', 50)
        
        # Get REAL data from PyBroker
        end_index = self.current_bar_index
        start_index = max(0, end_index - bars_back)
        
        # Slice actual historical data
        real_bars = self.data_manager.get_bars_slice(
            symbol=symbol,
            start_index=start_index,
            end_index=end_index
        )
        
        # Convert to TSX V5 format but keep REAL prices
        tsx_bars = []
        for bar in real_bars:
            tsx_bar = {
                't': bar.timestamp.isoformat() + 'Z',
                'o': float(bar.open),
                'h': float(bar.high), 
                'l': float(bar.low),
                'c': float(bar.close),
                'v': int(bar.volume)
            }
            tsx_bars.append(tsx_bar)
        
        # Send REAL data response
        response = {
            'requestId': request_id,
            'success': True,
            'data': {'bars': tsx_bars},
            'timestamp': datetime.now().isoformat() + 'Z'
        }
        
        self.redis_client.publish(
            'aggregator:historical-data:response',
            json.dumps(response)
        )
```

### 3. Integration with PyBroker Bridge
```python
class TSXStrategyBridge:
    """Enhanced bridge with real historical data"""
    
    def __init__(self, strategy_path, pybroker_data, config):
        self.strategy_path = strategy_path
        self.market_data = pybroker_data  # REAL market data from PyBroker
        self.current_bar_index = 0
        
        # Start historical data service with REAL data
        self.historical_service = HistoricalDataService(
            pybroker_data_manager=pybroker_data,
            redis_client=self.redis_client
        )
        self.historical_service.start()
    
    def process_bar(self, bar_index, bar_data):
        """Process next bar in backtest"""
        self.current_bar_index = bar_index
        
        # Update historical service with current position
        self.historical_service.current_bar_index = bar_index
        
        # Send current bar to strategy
        # Strategy can request historical data up to current position
        return self._send_market_data_to_strategy(bar_data)
```

## Corrected Architecture Benefits

### ✅ Real Market Data
- Strategies train on **actual market conditions**
- **Realistic price movements** and volatility
- **Accurate volume patterns**
- **Real market correlations**

### ✅ Valid Backtesting
- Results reflect **actual trading performance**
- Strategy behavior matches **real market conditions**
- **Meaningful risk assessment**
- **Accurate profit/loss calculations**

### ✅ Proper Historical Context
- Strategies get **actual price history** leading up to current bar
- **Real support/resistance levels**
- **Actual trend patterns**
- **Historical volatility context**

## Implementation Priority

This is a **CRITICAL FIX** that must be implemented before any further testing:

1. **Remove fake data generator** from bootstrap service
2. **Integrate with PyBroker's real data source**
3. **Modify TSX Bridge** to pass real data manager
4. **Update all tests** to verify real data is being used
5. **Verify strategies receive actual market data**

The current fake data implementation makes the entire backtesting system **meaningless** from a trading perspective. Strategies need to learn from and adapt to **real market conditions**, not synthetic patterns.

Should I proceed with implementing the corrected architecture that uses PyBroker's real historical data?