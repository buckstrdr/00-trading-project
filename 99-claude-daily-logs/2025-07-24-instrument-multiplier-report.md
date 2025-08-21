# Instrument Multiplier Investigation Report
**Date:** July 24, 2025
**Reporter:** Data Team Analysis

## Issue Summary
P&L calculations are missing instrument multipliers/point values, which will result in incorrect profit/loss calculations.

## Current State

### 1. **Multiplier Definitions Found**
✅ **Global Config** (`TSX_TRADING_BOT_V4/config/global.yaml`):
```yaml
instruments:
  MGC: multiplier: 10    # Micro Gold - $10/point
  MNQ: multiplier: 2     # Micro NASDAQ - $2/point
  MES: multiplier: 5     # Micro S&P 500 - $5/point
  MCL: multiplier: 10    # Micro Crude Oil - $10/point
  M2K: multiplier: 5     # Micro Russell - $5/point
  MYM: multiplier: 0.50  # Micro Dow - $0.50/point
  M6E: multiplier: 12.50 # Micro Euro - $12.50/point
  M6B: multiplier: 6.25  # Micro British Pound - $6.25/point
```

✅ **Manual Trading Server** (`manual-trading-v2/manual-trading-server-v2.js`):
- Has `getContractMultiplier()` function with correct values
- Uses multipliers correctly in P&L calculations

✅ **Instrument Model** (`TSX_TRADING_BOT_V4/src/core/market-data/models/Instrument.ts`):
- Has `pointValue` and `contractSize` fields defined
- Provides `calculateTickValue()` helper function

### 2. **Where Multipliers Are Missing**

❌ **SLTPCalculator** (`TSX_TRADING_BOT_V4/src/core/aggregator/core/SLTPCalculator.js`):
```javascript
// Line 84-85: Missing multiplier!
const slDistance = stopLossAmount / quantity;  // Should be: / (quantity * multiplier)
const tpDistance = takeProfitAmount / quantity; // Should be: / (quantity * multiplier)

// Line 125-126: Missing multiplier!
const stopLossAmountCalc = Math.abs(fillPrice - sl) * quantity;    // Should be: * quantity * multiplier
const takeProfitAmountCalc = Math.abs(tp - fillPrice) * quantity;  // Should be: * quantity * multiplier
```

❌ **Connection Manager**: No instrument multiplier handling found

## Impact
Without multipliers, P&L calculations will be wrong by these factors:
- MGC: Off by 10x (shows $1 instead of $10)
- MNQ: Off by 2x (shows $1 instead of $2)  
- MES: Off by 5x (shows $1 instead of $5)
- M6E: Off by 12.5x (shows $1 instead of $12.50)

## Recommendations

### 1. **Immediate Fix for SLTPCalculator**
Add multiplier parameter and update calculations:
```javascript
calculateFromFill(fill, params = {}) {
    const { multiplier = 1 } = params; // Add multiplier param
    
    // Update dollar amount calculations
    const slDistance = stopLossAmount / (quantity * multiplier);
    const stopLossAmountCalc = Math.abs(fillPrice - sl) * quantity * multiplier;
}
```

### 2. **Create Centralized Instrument Service**
- Load instrument data from global.yaml
- Provide getInstrument(symbol) method
- Share across all components needing multipliers

### 3. **Update Connection Manager**
- Add instrument data to position/order messages
- Include multiplier in all P&L-related broadcasts

### 4. **Ensure Consistency**
- All P&L calculations should use the same multiplier source
- Add unit tests to verify calculations with different multipliers

## Data Flow Recommendation
```
global.yaml → InstrumentService → Components
                     ↓
            ConnectionManager
                     ↓
         [Manual Trading, Aggregator, etc.]
```

## Next Steps
1. Fix SLTPCalculator to accept and use multipliers
2. Create shared InstrumentService 
3. Update Connection Manager to include multipliers
4. Add comprehensive tests for P&L calculations
5. Verify all components use consistent multiplier values