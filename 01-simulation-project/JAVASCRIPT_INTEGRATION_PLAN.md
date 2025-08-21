# JavaScript Strategy Integration Plan
## Complete TSX Trading Bot V5 Strategy Integration with Python Backtesting System

**Constraint**: JavaScript strategy files CANNOT be modified. All changes on backtester side only.

**Discovered Incompatibilities from PDHPDLStrategy-Comprehensive.js Analysis**:

1. **Module System**: Uses CommonJS (`require()`) not ES6 modules (`import`)
2. **Constructor Signature**: `constructor(config = {}, mainBot = null)` - different order
3. **File System Dependencies**: Uses Node.js `fs.promises`, `path` modules
4. **MainBot Dependencies**: Expects complex TSX Bot V5 mainBot object structure
5. **Framework Integration**: Deep integration with TSX Bot V5 modules and services

---

## Phase 1: Node.js Bridge Architecture Redesign

### 1.1 CommonJS Module Loader
**File**: `shared/js_commonjs_loader.js`

```javascript
// CommonJS-compatible strategy loader
const fs = require('fs').promises;
const path = require('path');
const vm = require('vm');

class CommonJSStrategyLoader {
    async loadStrategy(strategyPath, mainBot, config) {
        // Create isolated context with CommonJS support
        const context = {
            require: this.createRequireFunction(strategyPath),
            module: { exports: {} },
            exports: {},
            __filename: strategyPath,
            __dirname: path.dirname(strategyPath),
            console: console,
            Buffer: Buffer,
            process: process,
            global: global
        };
        
        // Read and execute strategy file
        const strategyCode = await fs.readFile(strategyPath, 'utf8');
        vm.createContext(context);
        vm.runInContext(strategyCode, context);
        
        // Extract strategy class
        const StrategyClass = context.module.exports || context.exports;
        
        // Instantiate with correct parameter order
        return new StrategyClass(config, mainBot);
    }
    
    createRequireFunction(basePath) {
        return (moduleName) => {
            if (moduleName === 'fs') return require('fs');
            if (moduleName === 'path') return require('path');
            // Add other Node.js modules as needed
            throw new Error(`Module not supported: ${moduleName}`);
        };
    }
}
```

### 1.2 TSX Bot V5 MainBot Complete Proxy
**File**: `shared/tsx_mainbot_proxy.js`

```javascript
// Complete TSX Trading Bot V5 mainBot proxy
class TSXMainBotProxy {
    constructor(backtestEngine) {
        this.backtestEngine = backtestEngine;
        
        this.modules = {
            positionManagement: new PositionManagementProxy(backtestEngine),
            healthMonitoring: new HealthMonitoringProxy(backtestEngine),
            riskManagement: new RiskManagementProxy(backtestEngine),
            dataManager: new DataManagerProxy(backtestEngine),
            signalManager: new SignalManagerProxy(backtestEngine),
            portfolioManager: new PortfolioManagerProxy(backtestEngine),
            performanceTracker: new PerformanceTrackerProxy(backtestEngine),
            configManager: new ConfigManagerProxy(backtestEngine),
            logManager: new LogManagerProxy(backtestEngine)
        };
        
        this.config = backtestEngine.config;
        this.state = { mode: 'BACKTEST', active: true };
    }
}

class PositionManagementProxy {
    constructor(backtestEngine) {
        this.engine = backtestEngine;
    }
    
    hasPosition() {
        return this.engine.getCurrentPosition() !== null;
    }
    
    getCurrentPosition() {
        return this.engine.getCurrentPosition();
    }
    
    getAccountBalance() {
        return this.engine.getAccountBalance();
    }
    
    getPositionSize() {
        const pos = this.engine.getCurrentPosition();
        return pos ? pos.size : 0;
    }
    
    getPositionPnL() {
        return this.engine.getPositionPnL();
    }
    
    getEntryPrice() {
        const pos = this.engine.getCurrentPosition();
        return pos ? pos.entry_price : null;
    }
    
    // Add all other position management methods...
}

// Implement all other proxy classes...
```

---

## Phase 2: Python Backtesting Engine Integration

### 2.1 Enhanced JSStrategyAdapter
**File**: `shared/js_strategy_adapter_v2.py`

```python
class JSStrategyAdapterV2(StrategyInterface):
    """
    TSX Trading Bot V5 compatible JavaScript strategy adapter
    Handles CommonJS modules and complete mainBot proxy
    """
    
    def __init__(self, js_strategy_path: str, config: StrategyConfig, backtest_engine=None):
        super().__init__(config, backtest_engine)
        
        # Strategy file validation
        self.js_strategy_path = Path(js_strategy_path)
        if not self.js_strategy_path.exists():
            raise FileNotFoundError(f"JavaScript strategy not found: {js_strategy_path}")
        
        # Validate it's a TSX Bot V5 strategy
        self._validate_tsx_strategy()
        
        # Node.js process with CommonJS support
        self.node_process = None
        self.strategy_loader = None
        self.mainbot_proxy = None
        
        # Initialize with correct parameter mapping
        self._initialize_strategy()
    
    def _validate_tsx_strategy(self):
        """Validate this is a TSX Bot V5 compatible strategy"""
        with open(self.js_strategy_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for TSX Bot V5 patterns
        required_patterns = [
            'constructor(',
            'processMarketData',
            'mainBot'
        ]
        
        for pattern in required_patterns:
            if pattern not in content:
                raise ValueError(f"Not a valid TSX Bot V5 strategy - missing {pattern}")
    
    def _create_strategy_config(self) -> Dict[str, Any]:
        """Convert Python config to TSX Bot V5 format"""
        return {
            'dollarRiskPerTrade': self.config.dollar_risk_per_trade,
            'dollarPerPoint': self.config.dollar_per_point,
            'maxRiskPoints': self.config.max_risk_points,
            'riskRewardRatio': self.config.risk_reward_ratio,
            'symbol': self.config.parameters.get('instrument', 'MCL'),
            # Map all other configuration parameters
        }
    
    def _create_mainbot_data(self) -> Dict[str, Any]:
        """Create mainBot proxy data for Node.js"""
        return {
            'currentPosition': self.current_position,
            'accountBalance': self.account_balance,
            'positionPnL': self._calculate_position_pnl(),
            'entryPrice': self.position_entry_price,
            'positionSize': 1 if self.current_position else 0,
            'trades': self.trade_history,
            'performance': self._get_performance_metrics(),
            # Add all required mainBot state data
        }
```

### 2.2 Backtesting Engine Enhancement
**File**: `engines/backtest_engine_js.py`

```python
class JSCompatibleBacktestEngine:
    """
    Enhanced backtest engine with JavaScript strategy support
    Provides all data and methods that TSX Bot V5 mainBot expects
    """
    
    def __init__(self):
        self.positions = {}
        self.account_balance = 100000.0  # Starting balance
        self.trade_history = []
        self.performance_metrics = {}
        
    def getCurrentPosition(self):
        """Get current position in TSX Bot V5 format"""
        # Return position object matching TSX Bot expectations
        
    def getAccountBalance(self):
        """Get account balance"""
        return self.account_balance
    
    def getPositionPnL(self):
        """Calculate position P&L"""
        # Implement P&L calculation
        
    def executeSignal(self, signal):
        """Execute trading signal from JavaScript strategy"""
        # Convert JS signal format to backtest execution
        
    # Implement all methods that TSX Bot V5 mainBot modules expect
```

---

## Phase 3: Complete Module Mapping

### 3.1 File System Compatibility
**Challenge**: JavaScript strategy uses `fs.promises` and `path` modules
**Solution**: Provide compatible implementations in Node.js bridge

### 3.2 Module Dependencies Mapping
Map all TSX Bot V5 modules that strategies might use:

```python
REQUIRED_MAINBOT_MODULES = {
    'positionManagement': [
        'hasPosition', 'getCurrentPosition', 'getAccountBalance',
        'getPositionSize', 'getPositionPnL', 'getEntryPrice'
    ],
    'healthMonitoring': [
        'isQuietMode', 'getSystemStatus', 'isMarketOpen'
    ],
    'riskManagement': [
        'calculatePositionSize', 'validateTrade', 'checkRiskLimits'
    ],
    'dataManager': [
        'getMarketData', 'getHistoricalData', 'getVolumeProfile'
    ],
    'signalManager': [
        'sendSignal', 'getLastSignal', 'getSignalHistory'
    ],
    # Add all other modules...
}
```

### 3.3 Strategy Parameter Translation
**Challenge**: TSX strategies expect specific configuration format
**Solution**: Parameter translation layer

---

## Phase 4: Testing & Validation

### 4.1 Compatibility Test Suite
**File**: `tests/test_tsx_integration.py`

```python
class TSXIntegrationTestSuite:
    """
    Comprehensive test suite for TSX Bot V5 strategy integration
    Tests real strategies with real mainBot proxy
    """
    
    def test_pdhpdl_strategy_loading(self):
        """Test PDHPDLStrategy-Comprehensive.js loads correctly"""
        
    def test_mainbot_proxy_completeness(self):
        """Test all required mainBot modules are implemented"""
        
    def test_signal_generation(self):
        """Test strategy generates valid trading signals"""
        
    def test_position_management(self):
        """Test position tracking matches strategy expectations"""
        
    def test_performance_metrics(self):
        """Test performance calculation accuracy"""
```

### 4.2 Real Strategy Validation
Test with actual TSX Bot V5 strategies:
- PDHPDLStrategy-Comprehensive.js
- Any other strategies in your framework

---

## Phase 5: Integration Points

### 5.1 Strategy Registry Updates
**File**: `shared/strategy_registry.py`

```python
# Add JavaScript strategy support
def register_js_strategy(self, js_file_path):
    """Register JavaScript strategy from TSX Bot V5 framework"""
    
def discover_js_strategies(self, directory):
    """Auto-discover JavaScript strategies"""
```

### 5.2 Backtest Service Integration
**File**: `services/backtest_service.py`

```python
# Add JavaScript strategy endpoint
@app.post("/api/backtest/js")
async def run_js_backtest(
    js_strategy_path: str,
    symbol: str,
    # ... other parameters
):
    """Run backtest with JavaScript strategy"""
```

---

## Phase 6: Documentation & Examples

### 6.1 Integration Guide
Complete documentation on how to use TSX Bot V5 strategies in Python backtesting

### 6.2 Example Usage
```python
# Example of running TSX Bot V5 strategy in Python backtester
strategy_path = "TSX-Trading-Bot-V5/src/strategies/PDHPDLStrategy-Comprehensive.js"
adapter = JSStrategyAdapterV2(strategy_path, config, backtest_engine)
# Strategy runs with full TSX Bot V5 compatibility
```

---

## Implementation Timeline

**Phase 1**: 1-2 days (Node.js bridge redesign)
**Phase 2**: 1-2 days (Python integration)
**Phase 3**: 1 day (Module mapping)
**Phase 4**: 1 day (Testing)
**Phase 5**: 0.5 days (Integration)
**Phase 6**: 0.5 days (Documentation)

**Total**: 5-7 days of development work

---

## Success Criteria

✅ PDHPDLStrategy-Comprehensive.js loads and initializes
✅ Strategy receives proper mainBot proxy with all expected modules
✅ Strategy generates valid trading signals
✅ Position management works correctly with strategy expectations
✅ All Node.js dependencies (fs, path) work properly
✅ Performance matches expectations from TSX Bot V5 framework
✅ No modifications required to existing JavaScript strategy files

This plan addresses all the real incompatibilities discovered and provides a complete roadmap for genuine integration.