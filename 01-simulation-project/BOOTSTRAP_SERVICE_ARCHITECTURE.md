# Historical Data Bootstrap Service - Architecture Diagram

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           PyBroker Backtesting Environment                      │
│  ┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────────┐ │
│  │   Market Data   │    │  TSX Strategy    │    │    Historical Data          │ │
│  │   (OHLCV Bars)  │    │     Bridge       │    │   Bootstrap Service         │ │
│  │                 │    │   (Python)       │    │     (Python)                │ │
│  └─────────────────┘    └──────────────────┘    └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
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
         │ - emaStrategy.js   │    │    │ - Channel Forward  │
         │ - Creates Redis    │    │    │ - bot: ↔ agg:     │
         │   client           │    │    │ - Position Mgmt    │
         │ - Requests hist    │    │    │                    │
         │   data on startup  │    │    │                    │
         └────────────────────┘    │    └────────────────────┘
                                   │
                        Redis Channels Architecture
```

## Detailed Component Architecture

### 1. Historical Data Bootstrap Service (claude_historical_bootstrap_service.py)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HistoricalDataBootstrapService                    │
├─────────────────────────────────────────────────────────────────────┤
│                          Main Thread                                │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  __init__(redis_client, config)                                 ││
│  │  - Initialize Redis connections                                 ││
│  │  - Set default configuration (base_price, volatility)          ││
│  │  - Create statistics tracking                                  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                  │                                  │
│                          start() method                             │
│                                  │                                  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │                    Background Listener Thread                   ││
│  │  ┌─────────────────────────────────────────────────────────────┐││
│  │  │  _listen_for_requests()                                     │││
│  │  │  - Subscribe to 'aggregator:historical-data:request'       │││
│  │  │  - Listen for Redis pub/sub messages                       │││
│  │  │  - Parse JSON requests                                      │││
│  │  │  - Call _handle_historical_request()                       │││
│  │  └─────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────┘│
│                                  │                                  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  _handle_historical_request(request)                           ││
│  │  - Extract: requestId, symbol, barsBack, interval              ││
│  │  - Call _generate_historical_bars()                            ││
│  │  - Create TSX V5 format response                               ││
│  │  - Publish to 'aggregator:historical-data:response'            ││
│  │  - Update statistics                                            ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                  │                                  │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │  _generate_historical_bars(symbol, bars_back, interval)        ││
│  │  - Calculate time intervals backwards from current time        ││
│  │  - Generate realistic OHLC relationships                       ││
│  │  - Create trending price movements with volatility             ││
│  │  - Format in exact TSX V5 bar format: {t, o, h, l, c, v}      ││
│  │  - Sort chronologically (oldest first)                         ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Redis Channel Communication Flow

### Request/Response Cycle:

```
┌─────────────────┐    Redis Channel: aggregator:historical-data:request    ┌─────────────────┐
│                 │ ──────────────────────────────────────────────────────▶ │                 │
│  TSX Strategy   │                                                         │  Bootstrap      │
│  (emaStrategy)  │                   Request Format:                       │   Service       │
│                 │    {                                                    │                 │
│  - Starts up    │      requestId: "ema-bootstrap-1756031670438",         │  - Listens on   │
│  - Needs hist   │      symbol: "NQ",                                      │    Redis        │
│    data         │      barType: "time",                                   │  - Generates    │
│  - ready: false │      interval: 1,                                       │    OHLCV data   │
│                 │      intervalType: "min",                               │  - Thread-safe  │
│                 │      barsBack: 50,                                      │                 │
│                 │      sessionTemplate: "USEQPost"                        │                 │
│                 │    }                                                    │                 │
│                 │                                                         │                 │
│                 │ ◀──────────────────────────────────────────────────────  │                 │
│                 │    Redis Channel: aggregator:historical-data:response   │                 │
│                 │                                                         └─────────────────┘
│  - Receives     │                   Response Format:                              
│    50 bars      │    {                                                           
│  - ready: true  │      requestId: "ema-bootstrap-1756031670438",                 
│  - Can generate │      success: true,                                            
│    signals      │      data: {                                                   
│                 │        bars: [                                                 
└─────────────────┘          {                                                     
                               t: "2025-08-24T10:44:30.940209Z",                  
                               o: 14983.55,                                        
                               h: 14983.55,                                        
                               l: 14982.8,                                         
                               c: 14982.8,                                         
                               v: 800                                              
                             },                                                    
                             // ... 49 more bars                                  
                           ]                                                       
                         },                                                        
                         timestamp: "2025-08-24T11:34:33.941073Z"                 
                       }                                                           
```

## Data Generation Algorithm

### Bar Generation Process:

```
┌─────────────────────────────────────────────────────────────────┐
│                    _generate_historical_bars()                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  for i in range(barsBack):  # Generate 50 bars backwards       │
│                                                                 │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │              Time Calculation                            │ │
│    │  bar_time = current_time - timedelta(                   │ │
│    │    seconds=interval_seconds * (bars_back - i)           │ │
│    │  )                                                      │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                │                                │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │              Price Generation                           │ │
│    │  trend_factor = i * 0.1      # Slight upward trend     │ │
│    │  volatility = (i % 7 - 3) * 5.0  # Oscillating        │ │
│    │  noise = random_component * 0.02  # Small variations   │ │
│    │  center_price = base_price + trend + volatility + noise│ │
│    └─────────────────────────────────────────────────────────┘ │
│                                │                                │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │              OHLC Relationships                         │ │
│    │  open_price = center_price + small_offset               │ │
│    │  close_price = center_price + different_offset          │ │
│    │  high_price = max(open, close) + positive_offset        │ │
│    │  low_price = min(open, close) - positive_offset         │ │
│    │  volume = base_volume + variation                       │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                │                                │
│    ┌─────────────────────────────────────────────────────────┐ │
│    │              TSX V5 Format                              │ │
│    │  bar = {                                                │ │
│    │    t: bar_time.isoformat() + 'Z',  # ISO + Z suffix    │ │
│    │    o: round(open_price, 2),                             │ │
│    │    h: round(high_price, 2),                             │ │
│    │    l: round(low_price, 2),                              │ │
│    │    c: round(close_price, 2),                            │ │
│    │    v: volume                                            │ │
│    │  }                                                      │ │
│    └─────────────────────────────────────────────────────────┘ │
│                                                                 │
│  bars.sort(key=lambda x: x['t'])  # Sort chronologically       │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. TSX Strategy Integration:
```
┌─────────────────────────────────────────────────────┐
│              EMA Strategy Startup                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. Strategy loads with MockTradingBot              │
│  2. Strategy creates own Redis client                │
│  3. Strategy publishes historical data request       │
│  4. Bootstrap service responds with 50 bars         │
│  5. Strategy processes bars, calculates EMAs        │
│  6. Strategy sets ready: true                       │
│  7. Strategy can now generate BUY/SELL signals      │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### 2. PyBroker Integration (Future):
```
┌─────────────────────────────────────────────────────┐
│              PyBroker Bridge Integration             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. PyBroker starts TSX Strategy Bridge             │
│  2. Bridge starts Bootstrap Service                 │
│  3. Bridge starts MockTradingBot + Strategy         │
│  4. Strategy bootstraps via Bootstrap Service       │
│  5. PyBroker sends market data → Strategy           │
│  6. Strategy generates signals → PyBroker           │
│  7. PyBroker executes trades                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## Thread Safety & Error Handling

### Service Architecture:
```
┌─────────────────────────────────────────────────────┐
│                Main Thread                          │
│  - Service initialization                           │
│  - Statistics tracking                              │
│  - start() / stop() methods                        │
├─────────────────────────────────────────────────────┤
│                Background Thread                    │
│  - Redis pub/sub listener                          │
│  - Message processing                               │
│  - Request handling                                 │
├─────────────────────────────────────────────────────┤
│                Error Handling                       │
│  - JSON parsing errors                              │
│  - Redis connection errors                          │
│  - Thread cleanup on shutdown                      │
│  - Statistics for failed requests                  │
├─────────────────────────────────────────────────────┤
│                Resource Management                  │
│  - Proper Redis connection cleanup                 │
│  - Thread join with timeout                        │
│  - Context manager support                         │
└─────────────────────────────────────────────────────┘
```

## Service Statistics

The bootstrap service tracks:
- `requests_received`: Total historical data requests
- `requests_processed`: Successfully processed requests  
- `requests_failed`: Failed requests (JSON errors, etc.)
- `bars_generated`: Total OHLCV bars created
- `running`: Service status
- `thread_alive`: Background thread status

This architecture enables TSX strategies to bootstrap with historical data and become operational for signal generation in the PyBroker backtesting environment.