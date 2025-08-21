# Crazy Horse Strategy Specification Document

## Strategy Overview
**Name:** Crazy Horse Strategy  
**Version:** 1.0  
**Type:** Opening Range Breakout  
**Market:** Micro Gold Futures (MGC)  
**Session:** New York Session (9:30 AM EST)  
**Framework:** TSX Trading Bot V5  

## Trading Concept
The Crazy Horse Strategy is a 15-minute opening range breakout strategy that trades the New York session opening. It identifies the high and low of the first 15 minutes after market open and enters positions when price breaks out of this range with confirmation from a 5-minute candle close.

## Framework Compatibility Checklist
- ✅ JavaScript class implementation
- ✅ Implements `processMarketData(price, volume, timestamp)` method
- ✅ Returns standard signal objects to bot
- ✅ Lightweight plugin architecture
- ✅ Configuration via YAML file
- ✅ Integration via `mainBot` reference
- ✅ No direct Redis access
- ✅ No direct database access
- ✅ No position management (bot handles)
- ✅ No risk management beyond signal generation

## Trading Rules

### Entry Conditions

#### Long Entry
1. Wait for 15-minute range to form (9:30-9:45 AM EST)
2. Mark the high and low of the range
3. Enter LONG when a 5-minute candle closes above the range high
4. Stop loss at range low
5. Take profit at 2:1 risk/reward ratio

#### Short Entry
1. Wait for 15-minute range to form (9:30-9:45 AM EST)
2. Mark the high and low of the range
3. Enter SHORT when a 5-minute candle closes below the range low
4. Stop loss at range high
5. Take profit at 2:1 risk/reward ratio

### Position Management (Optional Features)

#### Step 4: Add to Position (Optional)
- If enabled, add to position when price retraces to range midpoint
- Same position size as initial entry
- Only add once per trade

#### Step 5: Deleverage (Optional)
- If position was added and is back in profit
- Close the added portion when position shows 1 point profit

#### Step 6: Shelf Method
- Track consolidation patterns ("shelves")
- Trail stop loss based on shelf formations
- Minimum shelf size: 1 point
- Confirmation: 3 bars of consolidation

#### Step 7: Break-Even Stop
- After first shelf forms, move stop to break-even
- Protects capital while allowing profit run

#### Step 8: Maximum Loss Exit
- Exit if dollar loss exceeds maximum threshold
- Default: $100 or 10% of account

## Signal Generation Criteria

### Entry Signal Requirements
```javascript
{
    direction: 'LONG' | 'SHORT',
    confidence: 'HIGH',
    entryPrice: current_price,
    stopLoss: range_opposite_side,
    takeProfit: entry + (risk * 2),
    instrument: 'MGC',
    riskPoints: abs(entry - stop),
    rewardPoints: abs(target - entry),
    riskRewardRatio: 2.0,
    positionSize: calculated_from_dollar_risk,
    reason: 'Range breakout confirmed',
    indicators: {
        rangeHigh: value,
        rangeLow: value,
        rangeMidpoint: value
    }
}
```

### Exit Signal Requirements
```javascript
{
    direction: 'CLOSE_POSITION',
    confidence: 'HIGH',
    exitPrice: current_price,
    reason: 'Stop loss' | 'Take profit' | 'Max loss',
    closeType: 'full',
    pnl: calculated_pnl
}
```

## Configuration Parameters

### Required Parameters
- `dollarRiskPerTrade`: Risk budget per trade (default: 100)
- `dollarPerPoint`: Contract point value (default: 10)
- `maxRiskPoints`: Maximum allowed risk in points (default: 3.0)
- `riskRewardRatio`: Target reward ratio (default: 2)

### Session Parameters
- `sessionStartHour`: Session start hour (default: 9)
- `sessionStartMinute`: Session start minute (default: 30)
- `rangeMinutes`: Range formation period (default: 15)

### Optional Features
- `enableAddToPosition`: Enable adding at midpoint (default: true)
- `enableDeleveraging`: Enable partial closes (default: true)
- `moveToBreakEven`: Move stop to BE after shelf (default: true)

### Shelf Method Parameters
- `shelfMinPoints`: Minimum shelf size (default: 1.0)
- `shelfConsolidationBars`: Bars to confirm shelf (default: 3)

### Risk Limits
- `maxDollarLoss`: Maximum dollar loss per trade (default: 100)
- `accountSize`: Account size for risk calculation (default: 1000)

## Required Indicators/Calculations

### Primary Indicators
1. **Opening Range**
   - High of first 15 minutes
   - Low of first 15 minutes
   - Midpoint calculation

2. **5-Minute Candles**
   - Track complete 5-minute candles
   - Identify breakout candle closes

3. **Shelf Detection**
   - High/Low watermark tracking
   - Consolidation pattern recognition
   - Pullback measurement

### Derived Calculations
- Position size from dollar risk
- Risk/Reward ratios
- P&L tracking
- Break-even levels

## Risk Management Rules

### Position Sizing
- Calculate based on dollar risk per trade
- Account for contract point value
- Smart rounding (up to 50% over budget allowed)
- Minimum 1 contract

### Stop Loss Management
1. Initial: Opposite side of range
2. Shelf trailing: Below/above shelf levels
3. Break-even: After first shelf
4. Maximum loss: Dollar-based exit

### Risk Filters
- Maximum risk points check
- Position size limits
- Risk budget verification
- Account size considerations

## Data Requirements

### Real-time Data
- Price updates via `processMarketData()`
- Volume data (optional)
- Timestamp for candle formation

### Historical Data (Bootstrap)
- 48 hours of historical bars
- 5-minute candle data
- Used to form opening range if already past 9:45 AM

### State Persistence
- Current position details
- Entry/exit prices
- Stop loss levels
- Shelf tracking
- Position additions

## Integration Points

### Bot Framework Integration
```javascript
constructor(config = {}, mainBot = null) {
    this.mainBot = mainBot;  // Store bot reference
    // Initialize from config
}
```

### Position Check
```javascript
if (this.mainBot?.modules?.positionManagement) {
    const positions = this.mainBot.modules.positionManagement.getAllPositions();
    // Check for existing positions
}
```

### Quiet Mode Respect
```javascript
if (this.mainBot?.modules?.healthMonitoring) {
    const quietStatus = this.mainBot.modules.healthMonitoring.getQuietModeStatus();
    // Respect quiet mode
}
```

## Testing Requirements

### Unit Tests
- Range formation logic
- Breakout detection
- Signal generation
- Position sizing
- Shelf detection
- Stop management

### Integration Tests
- Bot framework compatibility
- Configuration loading
- Signal format validation
- State persistence

### Edge Cases
- Market opens mid-range
- Very wide/narrow ranges
- No breakout days
- Gap opens
- Immediate reversals

## Success Metrics
- Proper range formation
- Accurate breakout detection
- Correct position sizing
- Effective shelf trailing
- Risk limit compliance

## Version History
- v1.0: Initial implementation with all 8 steps from original PDF

## References
- Original PDF: "The Crazy Horse" trading strategy document
- Framework: TSX Trading Bot V5 Strategy Development Framework
- Configuration: BOT_CRAZY_HORSE.yaml