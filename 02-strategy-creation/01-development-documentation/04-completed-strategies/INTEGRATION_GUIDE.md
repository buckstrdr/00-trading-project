# Crazy Horse Strategy - Integration Guide

## Overview
The Crazy Horse Strategy is an opening range breakout strategy that trades the New York session opening (9:30 AM EST). It uses a 15-minute range formation period and enters positions when price breaks out of this range on a 5-minute candle close.

## Key Features
- **15-minute opening range** formation at session start
- **5-minute candle breakout** confirmation for entries
- **Optional position scaling** at range midpoint
- **Shelf method** for trailing profits
- **Automatic stop to break-even** after first shelf
- **Position state persistence** across bot restarts
- **Historical data bootstrapping** for immediate readiness

## Installation Steps

### 1. Create Strategy Directory
```bash
mkdir -p src/strategies/crazy-horse
```

### 2. Copy Strategy Files
Place the following files in the appropriate locations:
- `CrazyHorseStrategy.js` → `src/strategies/crazy-horse/`
- `BOT_CRAZY_HORSE.yaml` → `config/bots/`
- `CrazyHorseStrategy.test.js` → `tests/strategies/`

### 3. Register the Strategy
Add to `src/strategies/index.js`:
```javascript
const CrazyHorseStrategy = require('./crazy-horse/CrazyHorseStrategy');

module.exports = {
    // ... existing strategies ...
    CrazyHorseStrategy: CrazyHorseStrategy
};
```
### 4. Configure the Strategy
Edit `config/bots/BOT_CRAZY_HORSE.yaml`:
```yaml
strategy:
  dollarRiskPerTrade: 100    # Your risk per trade
  accountSize: 1000           # Your account size
  enableAddToPosition: true   # Enable/disable position scaling
  enableDeleveraging: true    # Enable/disable partial closes
```

### 5. Start the Bot
```bash
# Start with the Crazy Horse configuration
node src/index.js --config config/bots/BOT_CRAZY_HORSE.yaml

# Or if using PM2
pm2 start src/index.js --name "crazy-horse-bot" -- --config config/bots/BOT_CRAZY_HORSE.yaml
```

## Trading Logic

### Entry Criteria
1. **Wait** for 15-minute range to form (9:30-9:45 AM EST)
2. **Mark** the high and low of the range
3. **Enter LONG** when 5-minute candle closes above range high
4. **Enter SHORT** when 5-minute candle closes below range low

### Position Management
1. **Initial Stop**: Opposite side of range
2. **Optional Add**: At range midpoint (if enabled)
3. **Optional Deleverage**: When back in profit after adding
4. **Shelf Trailing**: Forms "shelves" during consolidation
5. **Break-Even Stop**: After first shelf formation
6. **Exit**: Stop loss, take profit, or max dollar loss
### Risk Management
- **Position Sizing**: Automatic based on dollar risk
- **Max Risk**: Configurable maximum points risk
- **Max Loss**: Dollar-based maximum loss per trade
- **Risk:Reward**: Configurable ratio (default 1:2)

## Configuration Options

### Required Parameters
```yaml
dollarRiskPerTrade: 100     # Risk budget per trade
dollarPerPoint: 10          # Contract point value
maxRiskPoints: 3.0          # Maximum allowed risk in points
riskRewardRatio: 2          # Target reward ratio
```

### Session Parameters
```yaml
sessionStartHour: 9         # Session start hour (24-hour format)
sessionStartMinute: 30      # Session start minute
rangeMinutes: 15           # Range formation period
```

### Optional Features
```yaml
enableAddToPosition: true   # Add at midpoint retrace
enableDeleveraging: true    # Partial close when profitable
moveToBreakEven: true      # Move stop to BE after shelf
```

### Shelf Method Parameters
```yaml
shelfMinPoints: 1.0        # Minimum shelf size
shelfConsolidationBars: 3  # Bars to confirm shelf
```
## Testing

### Run Unit Tests
```bash
npm test -- CrazyHorseStrategy.test.js
```

### Manual Testing Checklist
- [ ] Range forms correctly at 9:30 AM EST
- [ ] Breakout signals generated on 5-min candle close
- [ ] Stop loss placed at opposite range boundary
- [ ] Position adds at midpoint (if enabled)
- [ ] Deleveraging works when back in profit
- [ ] Shelf formation detected correctly
- [ ] Stop moves to break-even after first shelf
- [ ] Maximum dollar loss exit triggers
- [ ] Position state persists across restarts

## Monitoring

### Key Metrics to Watch
- Range size (should be reasonable, not too wide)
- Entry timing (only after 5-min candle close)
- Shelf formation count
- Stop loss adjustments
- P&L tracking

### Debug Information
The strategy provides detailed debug info via `getStatusSummary()`:
- Range formation status
- Current position details
- Shelf count
- Stop loss level
- Entry/exit prices

## Troubleshooting

### Strategy Not Ready
- Check if range has formed (after 9:45 AM EST)
- Verify historical data bootstrap succeeded
- Ensure market is open

### No Signals Generated
- Verify 5-minute candles are forming correctly
- Check if price has actually broken the range
- Ensure no existing positions blocking signals
- Verify risk parameters allow the trade

### Position Not Adding
- Check `enableAddToPosition` is true
- Verify price retraced to midpoint
- Ensure position hasn't already been added

### Shelf Not Forming
- Verify consolidation period meets requirements
- Check `shelfMinPoints` parameter
- Ensure price pullback is sufficient

## Performance Tips

1. **Historical Bootstrap**: Strategy auto-fetches historical data on startup
2. **Memory Management**: Only keeps last 200 candles
3. **State Persistence**: Saves position state to survive restarts
4. **Quiet Mode**: Respects bot's quiet mode during operations

## Risk Warnings

⚠️ **Important Considerations**:
- This strategy trades breakouts which can be volatile
- Ensure risk parameters match your account size
- Test thoroughly in practice mode first
- Monitor for false breakouts in choppy markets
- Consider market conditions before enabling

## Support Files Location

- **Strategy State**: `data/strategy-state/CRAZY_HORSE_state.json`
- **Logs**: Standard bot logging location
- **Configuration**: `config/bots/BOT_CRAZY_HORSE.yaml`

## Version History

- **v1.0**: Initial implementation with all 8 steps from PDF
  - Opening range formation
  - Breakout entry logic
  - Optional position scaling
  - Shelf method trailing
  - Break-even stop management
  - Maximum loss protection

## Contact & Support

For issues or questions about the Crazy Horse Strategy:
1. Check the debug output for detailed state information
2. Review the test file for expected behavior
3. Ensure all configuration parameters are set correctly
4. Verify the Connection Manager is running (port 7500)