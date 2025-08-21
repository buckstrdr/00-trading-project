# Strategy Creation Process - MANDATORY CHECKLIST

**CRITICAL: READ THIS FIRST BEFORE CREATING ANY STRATEGY**

This document prevents architectural mistakes and ensures all strategies are compatible with the TSX Trading Bot V5 framework.

## 🚨 MANDATORY PROCESS - NO EXCEPTIONS

### STEP 1: UNDERSTAND THE FRAMEWORK FIRST ⭐⭐⭐
**Location:** `01-Framework-MD/Strategy-Development-Framework.md`

**MUST READ AND CONFIRM:**
- [ ] Strategy is a **JavaScript class** (NOT Python)
- [ ] Strategy implements `processMarketData(price, volume, timestamp)` method
- [ ] Strategy returns signal objects to the bot
- [ ] Bot handles ALL infrastructure (Redis, database, position management, risk management)
- [ ] Strategy is a **lightweight plugin**, not a standalone system
- [ ] Configuration comes from YAML files
- [ ] Integration is via `mainBot` reference

**ARCHITECTURE CONFIRMATION:**
```
Market Data → Strategy.processMarketData() → Signal → TradingBot → AggregatorClient → Connection Manager → TopStepX API
```

### STEP 2: REVIEW CONCEPT DOCUMENTS
**Location:** `02-Concept-Documents/`

**Review relevant concept files:**
- [ ] Read strategy concept document (e.g., `PDH-PDL-DF.md`)
- [ ] Understand trading logic and rules
- [ ] Identify key indicators and data requirements
- [ ] Note risk management requirements

### STEP 3: CREATE STRATEGY SPECIFICATION
**Location:** `03-Strategy-Specification-Documents/`

**Create strategy specification document:**
- [ ] Define strategy name and version
- [ ] Document trading rules and logic
- [ ] Specify signal generation criteria
- [ ] Define configuration parameters
- [ ] List required indicators/calculations
- [ ] Specify risk management rules

**Template:** Use existing specification documents as templates.

### STEP 4: VERIFY FRAMEWORK COMPATIBILITY
**BEFORE WRITING ANY CODE:**

**Confirm strategy will:**
- [ ] Be a single JavaScript class
- [ ] Receive data through `processMarketData()` only
- [ ] Calculate indicators internally or use helper functions
- [ ] Generate signal objects in standard format
- [ ] Use YAML configuration for parameters
- [ ] Integrate with bot via `mainBot` reference
- [ ] NOT access Redis directly
- [ ] NOT access database directly
- [ ] NOT handle position management
- [ ] NOT handle risk management beyond signal generation

### STEP 5: CREATE JAVASCRIPT STRATEGY
**Location:** Should be in bot's strategy directory, NOT in this repo

**File Structure:**
```
src/strategies/strategy-name/
├── StrategyName.js           # Main strategy class
├── StrategyNameSignalGenerator.js  # Optional: Signal logic
└── helpers/                  # Optional: Strategy utilities
```

**Required Interface:**
```javascript
class StrategyName {
    constructor(config = {}, mainBot = null) {
        // Initialize with config and bot reference
    }

    processMarketData(price, volume = 1000, timestamp = null) {
        // Process data and return { ready, signal, environment, debug }
    }

    isStrategyReady() {
        // Return boolean
    }

    getStatusSummary() {
        // Return status object for UI
    }

    reset() {
        // Reset strategy state
    }
}
```

### STEP 6: CREATE CONFIGURATION FILE
**Create YAML configuration:**
```yaml
bot:
  name: "BOT_STRATEGY_NAME"
  strategy: "StrategyName"
  enabled: true

strategy:
  dollarRiskPerTrade: 100
  dollarPerPoint: 10
  maxRiskPoints: 3.0
  # Strategy-specific parameters
```

### STEP 7: TEST AND VALIDATE
- [ ] Unit tests for strategy logic
- [ ] Integration tests with bot framework
- [ ] Configuration validation
- [ ] Signal format validation

## 🚫 WHAT NOT TO DO - COMMON MISTAKES

### ❌ ARCHITECTURAL MISTAKES TO AVOID:
- **Creating Python strategies** (Framework is JavaScript only)
- **Creating standalone trading systems** (Strategy is a plugin component)
- **Direct Redis integration** (Bot handles all communication)
- **Direct database access** (Bot handles data persistence)
- **Complex data feed handling** (Bot provides data via processMarketData)
- **Position management logic** (Bot handles positions)
- **Risk management systems** (Bot handles risk, strategy generates signals)

### ❌ LOCATION MISTAKES TO AVOID:
- **Creating code in this documentation repo** (Code goes in bot repo)
- **Creating separate repositories** (Strategy integrates with existing bot)
- **Wrong file structures** (Follow framework directory structure)

### ❌ INTEGRATION MISTAKES TO AVOID:
- **Missing mainBot reference** (Required for bot integration)
- **Wrong signal format** (Must match framework specification)
- **Missing required methods** (All interface methods must be implemented)
- **Configuration hardcoding** (Use YAML configuration system)

## ✅ SUCCESS CRITERIA

**Before considering strategy complete:**
- [ ] Strategy follows JavaScript framework template exactly
- [ ] All required interface methods implemented
- [ ] Configuration via YAML file works
- [ ] Integration with bot framework tested
- [ ] Signal generation logic validated
- [ ] No direct infrastructure dependencies
- [ ] Documentation updated in bot repo

## 🔄 RECOVERY FROM MISTAKES

**If you created the wrong architecture:**
1. **STOP** - Don't continue with wrong approach
2. **Archive** - Move wrong implementation to backup location
3. **RESTART** - Follow this process from Step 1
4. **LEARN** - Update this document with additional prevention measures

## 📋 FINAL CHECKLIST

**Before declaring strategy complete:**
- [ ] Read framework documentation ✓
- [ ] Created strategy specification ✓
- [ ] Verified framework compatibility ✓
- [ ] Created JavaScript strategy class ✓
- [ ] Implemented all required methods ✓
- [ ] Created YAML configuration ✓
- [ ] Tested integration with bot ✓
- [ ] Validated signal generation ✓
- [ ] No architectural mistakes ✓
- [ ] Strategy is lightweight plugin, not standalone system ✓

## 📞 ESCALATION

**If unclear about any step:**
1. Re-read framework documentation
2. Review existing strategy examples in bot repo
3. Ask for clarification before proceeding
4. Better to ask than create wrong architecture

---

**REMEMBER: The goal is a lightweight JavaScript strategy plugin that integrates with the existing TSX Trading Bot framework. NOT a standalone trading system.**

**This checklist prevents the architectural mistakes that led to building a complete Python trading system when only a simple JavaScript strategy component was needed.**