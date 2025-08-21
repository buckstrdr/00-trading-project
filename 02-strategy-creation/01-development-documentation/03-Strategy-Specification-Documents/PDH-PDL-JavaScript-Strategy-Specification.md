# PDH/PDL Daily Flip Strategy - JavaScript Framework Implementation Specification

**Strategy Name:** `PDHPDLStrategy`  
**Version:** 1.0  
**Framework:** TSX Trading Bot V5 (JavaScript)  
**Target Symbol:** MGC (Micro Gold Futures)  
**Status:** Framework-Compatible Specification  

## Overview

This specification defines a lightweight JavaScript strategy component that implements PDH (Previous Day High) and PDL (Previous Day Low) trading logic within the TSX Trading Bot V5 framework. The strategy generates signals based on breakout and fade patterns at key reference levels.

## Framework Integration Requirements

### Required Interface Implementation
```javascript
class PDHPDLStrategy {
    constructor(config = {}, mainBot = null) {
        // Initialize with configuration and bot reference
    }

    processMarketData(price, volume = 1000, timestamp = null) {
        // Main strategy logic - returns { ready, signal, environment, debug }
    }

    isStrategyReady() {
        // Returns boolean indicating strategy readiness
    }

    getStatusSummary() {
        // Returns status object for UI display
    }

    reset() {
        // Resets strategy state for bot restart
    }
}
```

### Bot Framework Responsibilities
The TSX Trading Bot handles:
- ✅ Data feeds and market data delivery via `processMarketData()`
- ✅ Redis communication and order management
- ✅ Position management and tracking
- ✅ Risk management enforcement
- ✅ Database persistence
- ✅ Order execution through AggregatorClient
- ✅ Configuration loading from YAML

### Strategy Component Responsibilities
The strategy component handles:
- ✅ PDH/PDL level calculations from historical price data
- ✅ Technical indicator calculations (VWAP, ATR, volume analysis)
- ✅ Signal generation based on breakout/fade patterns
- ✅ Internal state management (candle building, level tracking)
- ✅ Signal confidence scoring and validation

## Trading Logic Specification

### Core Strategy Components

#### 1. PDH/PDL Level Calculation
**Previous Day High/Low from Regular Trading Hours (8:30 AM - 3:15 PM CT)**

```javascript
// PDH/PDL levels calculated from previous trading day RTH session
const pdhPdlLevels = {
    pdh: 2385.50,           // Previous day high
    pdl: 2378.20,           // Previous day low
    range: 7.30,            // PDH - PDL
    midpoint: 2381.85,      // (PDH + PDL) / 2
    breakoutBuffer: 0.20,   // 2 ticks above/below for entry
    tradeDate: '2025-08-20' // Reference date
};
```

#### 2. Signal Generation Strategies

**Breakout Strategy (Primary)**
- **Entry Trigger**: Price closes above PDH with volume confirmation
- **Volume Confirmation**: Current volume > 1.5x average volume (20-period)
- **VWAP Filter**: Price must be above VWAP for long signals
- **Entry**: PDH + 0.20 (2 tick buffer)
- **Stop Loss**: PDH - (ATR * 1.5) or 8-12 ticks minimum
- **Take Profit**: 2:1 risk-reward ratio

**Fade Strategy (Secondary)**  
- **Entry Trigger**: Price touches PDH/PDL but fails to break with rejection
- **Rejection Pattern**: Long wick/doji at level with volume divergence
- **Entry**: Market price on bounce/rejection confirmation
- **Stop Loss**: 5-10 ticks beyond PDH/PDL level
- **Take Profit**: Opposite level or midpoint

**Flip Zone Strategy (Advanced)**
- **Entry Trigger**: Retest of broken PDH/PDL level from opposite side
- **Confirmation**: Volume decreases on retest (bearish divergence)
- **Entry**: Market price when retest fails
- **Stop Loss**: 10 ticks beyond flip zone
- **Take Profit**: Next significant level

#### 3. Technical Indicators Required

**Volume Weighted Average Price (VWAP)**
- Daily VWAP calculation from market open
- Used for trend bias confirmation
- Above VWAP = bullish bias, below VWAP = bearish bias

**Average True Range (ATR)**
- 14-period ATR for volatility measurement  
- Used for dynamic stop loss calculation
- ATR-based stops: ATR(14) × 1.5

**Volume Analysis**
- 20-period average volume for confirmation
- Volume surge detection (>1.5x average)
- Volume divergence analysis for fade setups

#### 4. Time-Based Position Management

**9 PM CT Mandatory Close Integration**
- Strategy reduces signal generation as close approaches
- Position sizing scales down with time decay
- Final hour (8-9 PM): High-probability setups only

**Time Decay Formula**
```javascript
const timeDecayFactor = Math.sqrt(minutesUntilClose / 390);
const adjustedPositionSize = basePositionSize * timeDecayFactor;
```

**Exit Schedule**
- 8:30 PM CT: Reduce signal confidence by 25%
- 8:45 PM CT: Reduce signal confidence by 50%  
- 8:55 PM CT: Stop generating new signals

### Signal Output Specification

**Standard Signal Format**
```javascript
const signal = {
    // REQUIRED CORE PROPERTIES
    direction: 'LONG' | 'SHORT' | 'CLOSE_POSITION',
    confidence: 'LOW' | 'MEDIUM' | 'HIGH' | 'TEST',
    entryPrice: 2385.70,
    stopLoss: 2381.50,
    takeProfit: 2394.10,
    instrument: 'MGC',
    
    // REQUIRED RISK METRICS
    riskPoints: 4.20,
    rewardPoints: 8.40,
    riskRewardRatio: 2.00,
    
    // REQUIRED POSITION SIZING (calculated by strategy)
    positionSize: 1,
    dollarRisk: 42.00,
    dollarReward: 84.00,
    
    // REQUIRED METADATA
    timestamp: Date.now(),
    reason: 'PDH breakout with volume confirmation',
    strategyName: 'PDHPDLStrategy',
    strategyVersion: '1.0',
    signalStrength: 0.85,
    
    // PDH/PDL SPECIFIC DATA
    subStrategy: 'BREAKOUT' | 'FADE' | 'FLIP_ZONE',
    indicators: {
        pdh: 2385.50,
        pdl: 2378.20,
        vwap: 2382.15,
        atr: 2.80,
        volumeRatio: 1.7
    },
    environment: {
        sessionTime: 'NEW_YORK_MORNING',
        marketStructure: 'TRENDING_UP',
        volatilityRegime: 'NORMAL'
    }
};
```

### Configuration Parameters

**YAML Configuration Structure**
```yaml
bot:
  name: "BOT_PDH_PDL"
  strategy: "PDHPDLStrategy"
  enabled: true
  port: 3011

strategy:
  # Risk Management (handled by bot)
  dollarRiskPerTrade: 100
  dollarPerPoint: 10
  maxRiskPoints: 3.0
  riskRewardRatio: 2.0
  
  # PDH/PDL Specific Parameters
  volumeConfirmationMultiplier: 1.5
  breakoutBufferTicks: 2
  atrMultiplier: 1.5
  minStopTicks: 8
  maxStopTicks: 15
  
  # Strategy Selection
  enableBreakoutStrategy: true
  enableFadeStrategy: true
  enableFlipZoneStrategy: false
  
  # Time-Based Settings
  enableTimeDecay: true
  stopNewSignalsAt: "20:55"  # 8:55 PM CT
  
  # Market Structure Filters
  requireVwapAlignment: true
  minVolumeRatio: 1.5
  enableMarketStructureFilter: true
```

### Internal State Management

**Strategy State Structure**
```javascript
this.state = {
    // Position tracking
    currentPosition: null,
    lastSignalTime: null,
    
    // PDH/PDL levels
    pdhPdlLevels: {
        pdh: null,
        pdl: null,
        range: null,
        midpoint: null,
        calculatedAt: null
    },
    
    // Technical indicators
    indicators: {
        vwap: null,
        atr: null,
        volumeAvg: null
    },
    
    // Market structure
    marketStructure: 'NEUTRAL', // TRENDING_UP, TRENDING_DOWN, RANGE_BOUND
    sessionPhase: 'PRE_MARKET', // MORNING, AFTERNOON, EVENING
    
    // Strategy readiness
    isReady: false,
    dataPointsCollected: 0
};
```

**Candle Data Management**
- Maintain rolling 200-candle history for calculations
- Build 5-minute candles from tick data via `processMarketData()`
- Calculate indicators on candle close only

## Implementation Requirements

### Mandatory Framework Compliance

1. **No Direct Infrastructure Access**
   - ❌ No Redis client instantiation
   - ❌ No database connections
   - ❌ No direct API calls to external services
   - ✅ Receive all data through `processMarketData()` method

2. **Bot Integration Requirements**
   - ✅ Store `mainBot` reference in constructor
   - ✅ Check position status via `mainBot.modules.positionManagement`
   - ✅ Respect quiet mode via `mainBot.modules.healthMonitoring`
   - ✅ Provide status for UI via `getStatusSummary()`

3. **Configuration Management**
   - ✅ Accept all parameters through config object
   - ✅ Provide sensible defaults for all parameters
   - ✅ Validate configuration in constructor

### Performance Requirements

- **Memory Usage**: <10MB total memory footprint
- **Processing Time**: <50ms per `processMarketData()` call
- **History Management**: Maintain only essential historical data
- **CPU Efficiency**: Use efficient algorithms for indicator calculations

### Error Handling Requirements

```javascript
// Graceful error handling in processMarketData
try {
    const result = this.processMarketDataInternal(price, volume, timestamp);
    return result;
} catch (error) {
    console.log(`❌ PDH/PDL Strategy Error: ${error.message}`);
    return {
        ready: false,
        signal: null,
        debug: { reason: 'Processing error', error: error.message }
    };
}
```

## Validation Criteria

### Signal Quality Gates
- **Minimum Confidence**: Only generate HIGH confidence signals
- **Risk-Reward**: Minimum 1.5:1 risk-reward ratio
- **Volume Confirmation**: Required for all breakout signals
- **Time Validation**: No signals within 30 minutes of PDH/PDL touch

### Integration Testing Requirements
- **Bot Framework Integration**: Strategy initializes with bot reference
- **Configuration Loading**: YAML parameters load correctly
- **Signal Generation**: Valid signals generated in test conditions
- **State Management**: Strategy survives bot restart via `reset()` method
- **UI Integration**: Status displays correctly in bot dashboard

## Success Metrics

**Strategy Performance Targets**
- **Win Rate**: 60-70% (based on concept document research)
- **Risk-Reward**: Average 2:1 or better
- **Sharpe Ratio**: Target >1.1
- **Maximum Drawdown**: <15%
- **Processing Reliability**: >99% successful `processMarketData()` calls

**Framework Integration Targets**
- **Initialization Time**: <2 seconds from bot startup
- **Memory Efficiency**: Stable memory usage over extended operation
- **Configuration Flexibility**: All parameters adjustable via YAML
- **Error Recovery**: Graceful handling of invalid market data

## Development Timeline

**Phase 1: Core Implementation (2 days)**
- Implement required framework interface methods
- Create PDH/PDL calculation logic
- Build basic signal generation (breakout strategy)
- Add configuration management

**Phase 2: Strategy Enhancement (1 day)**  
- Add technical indicators (VWAP, ATR, volume analysis)
- Implement fade and flip zone strategies
- Add time-based position management
- Create comprehensive error handling

**Phase 3: Integration & Testing (1 day)**
- Test with bot framework
- Validate signal generation
- Performance optimization
- Documentation completion

## File Structure

**Strategy Implementation Location**
```
src/strategies/pdh-pdl/
├── PDHPDLStrategy.js                 # Main strategy class
├── PDHPDLCalculator.js              # PDH/PDL calculation helper
├── TechnicalIndicators.js           # VWAP, ATR, volume helpers
└── helpers/
    ├── MarketStructure.js           # Market condition analysis
    └── SignalValidator.js           # Signal quality validation
```

**Configuration File Location**
```
config/bots/BOT_PDH_PDL.yaml         # Strategy configuration
```

This specification ensures the PDH/PDL strategy integrates seamlessly with the TSX Trading Bot V5 framework while maintaining the trading edge documented in the concept paper. The implementation will be a lightweight, efficient component that focuses purely on signal generation while leveraging the bot's infrastructure for execution and management.

---

**Next Step**: Implement the JavaScript strategy following this specification exactly, ensuring framework compatibility and trading effectiveness.