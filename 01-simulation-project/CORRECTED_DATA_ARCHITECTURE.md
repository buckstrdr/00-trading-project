# CORRECTED Data Architecture - Monthly CSV Files Integration

## Critical Error Correction

**❌ WRONG APPROACH:** Using PyBroker with YFinance data  
**✅ CORRECT APPROACH:** Using your monthly CSV files as the real data source

## Real Data Source Structure

### **Monthly CSV Files Location:**
```
C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files\
├── MCL\ (Light Crude Oil)
│   ├── 2008\ - 2025\ (by year)
│   │   ├── 01-January\ - 12-December\ (by month)  
│   │   │   └── MCL_YYYY_MM_Month.csv
├── MES\ (S&P 500 E-Mini)
├── MGC\ (Gold)
├── NG\ (Natural Gas)
└── SI\ (Silver)
```

### **CSV Data Format:**
```csv
Date (D);Time (T);Open (O);High (H);Low (L);Close (C);Volume (V)
02/01/2023;17:00;71.392769;71.578849;71.206689;71.268716;283
02/01/2023;17:01;71.233272;71.410491;71.197828;71.339603;124
```

**Key Details:**
- **Delimiter:** Semicolon (`;`)
- **Date Format:** DD/MM/YYYY  
- **Time Format:** HH:MM
- **Data Resolution:** 1-minute bars
- **Symbols:** MCL, MES, MGC, NG, SI (futures contracts)

## Corrected Architecture

### **1. Historical Data Bootstrap Service - REAL Implementation**
```python
class RealHistoricalDataService:
    """Uses monthly CSV files as the REAL data source"""
    
    def __init__(self, data_directory):
        self.data_directory = data_directory
        self.loaded_data = {}  # Cache for loaded monthly files
        
    def handle_historical_request(self, request):
        """Handle TSX strategy request with REAL CSV data"""
        
        symbol = request.get('symbol', 'MCL')  # MCL = Light Crude (NQ equivalent)
        bars_back = request.get('barsBack', 50)
        
        # Get current month's data (during backtest simulation)
        current_date = self._get_current_backtest_date()
        
        # Load required monthly CSV files to get historical data
        historical_bars = self._load_historical_bars(symbol, current_date, bars_back)
        
        # Convert to TSX V5 format
        tsx_bars = self._convert_csv_to_tsx_format(historical_bars)
        
        return {
            'requestId': request.get('requestId'),
            'success': True,
            'data': {'bars': tsx_bars},
            'timestamp': datetime.now().isoformat() + 'Z'
        }
    
    def _load_historical_bars(self, symbol, current_date, bars_back):
        """Load historical bars from monthly CSV files"""
        
        bars = []
        files_to_load = self._get_required_csv_files(symbol, current_date, bars_back)
        
        for csv_file_path in files_to_load:
            monthly_data = self._load_monthly_csv(csv_file_path)
            bars.extend(monthly_data)
        
        # Sort by datetime and return last N bars
        bars.sort(key=lambda x: x['datetime'])
        return bars[-bars_back:]
    
    def _load_monthly_csv(self, file_path):
        """Load and parse monthly CSV file"""
        
        bars = []
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f, delimiter=';')
            
            for row in reader:
                # Parse CSV format to standard OHLCV
                date_str = row['Date (D)']
                time_str = row['Time (T)']
                
                # Convert DD/MM/YYYY HH:MM to datetime
                dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M")
                
                bar = {
                    'datetime': dt,
                    'open': float(row['Open (O)']),
                    'high': float(row['High (H)']),
                    'low': float(row['Low (L)']),
                    'close': float(row['Close (C)']),
                    'volume': int(row['Volume (V)'])
                }
                bars.append(bar)
        
        return bars
    
    def _convert_csv_to_tsx_format(self, bars):
        """Convert CSV data to TSX V5 format"""
        
        tsx_bars = []
        for bar in bars:
            tsx_bar = {
                't': bar['datetime'].isoformat() + 'Z',
                'o': bar['open'],
                'h': bar['high'], 
                'l': bar['low'],
                'c': bar['close'],
                'v': bar['volume']
            }
            tsx_bars.append(tsx_bar)
            
        return tsx_bars
```

### **2. Custom CSV Data Source for Backtesting**
```python
class MonthlyCSVDataSource:
    """Custom data source that loads from monthly CSV files"""
    
    def __init__(self, data_directory):
        self.data_directory = data_directory
        
    def load_symbol_data(self, symbol, start_date, end_date):
        """Load data for backtesting from CSV files"""
        
        all_bars = []
        
        # Get list of monthly files in date range
        csv_files = self._get_csv_files_for_range(symbol, start_date, end_date)
        
        for csv_file in csv_files:
            monthly_bars = self._load_monthly_csv(csv_file)
            all_bars.extend(monthly_bars)
        
        # Filter by exact date range
        filtered_bars = [
            bar for bar in all_bars 
            if start_date <= bar['datetime'] <= end_date
        ]
        
        # Convert to backtesting format
        return self._to_backtest_dataframe(filtered_bars)
    
    def _to_backtest_dataframe(self, bars):
        """Convert to DataFrame for backtesting engine"""
        
        df_data = []
        for bar in bars:
            df_data.append({
                'date': bar['datetime'],
                'symbol': 'MCL',  # Map to standard symbol
                'open': bar['open'],
                'high': bar['high'],
                'low': bar['low'],
                'close': bar['close'],
                'volume': bar['volume'],
                'adj_close': bar['close']  # No adjustment for futures
            })
        
        return pd.DataFrame(df_data)
```

## Revised Integration Architecture

### **Complete Data Flow - CORRECT**
```
Monthly CSV Files → Custom Data Source → Backtesting Engine → TSX Strategy → Historical Bootstrap → TSX Strategy Ready
```

**NOT:**
```
YFinance → PyBroker → Fake Data Generator ❌
```

### **TSX Strategy Bridge - Corrected**
```python
class TSXStrategyBridge:
    def __init__(self, strategy_path, csv_data_directory, config):
        self.strategy_path = strategy_path
        self.csv_data_directory = csv_data_directory
        self.config = config
        
        # Real data source using monthly CSV files
        self.data_source = MonthlyCSVDataSource(csv_data_directory)
        
        # Real bootstrap service using CSV data
        self.historical_service = RealHistoricalDataService(csv_data_directory)
        
        # Current backtest position (for historical data slicing)
        self.current_datetime = None
        self.loaded_data = None
        
    def start_backtest(self, symbol, start_date, end_date):
        """Start backtest using CSV data"""
        
        # Load all data for date range from CSV files
        self.loaded_data = self.data_source.load_symbol_data(symbol, start_date, end_date)
        
        # Start TSX strategy with CSV historical bootstrap
        self._start_tsx_strategy_with_real_data()
        
        # Return backtest results
        return self._run_backtest()
    
    def _start_tsx_strategy_with_real_data(self):
        """Start TSX strategy with access to real CSV historical data"""
        
        # Start historical bootstrap service with CSV data access
        self.historical_service.set_loaded_data(self.loaded_data)
        self.historical_service.start()
        
        # Start MockTradingBot + TSX Strategy
        self._start_mock_trading_bot()
        
    def process_bar(self, bar_index, bar_data):
        """Process each bar during backtest with real data context"""
        
        # Update current position for historical data requests
        self.current_datetime = bar_data['datetime']
        self.historical_service.set_current_position(bar_index, self.current_datetime)
        
        # Send market data to TSX strategy
        # Strategy can now request REAL historical data via Redis
        signal = self._send_market_data_to_strategy(bar_data)
        
        return signal
```

## Implementation Priority - CORRECTED

### **Phase 1A: CSV Data Integration (HIGHEST PRIORITY)**
1. ✅ **Identify CSV file structure** - DONE
2. ⚠️ **Create MonthlyCSVDataSource class**
3. ⚠️ **Test CSV data loading and parsing**  
4. ⚠️ **Verify data format conversion to TSX V5**

### **Phase 1B: Real Historical Bootstrap Service**  
1. ⚠️ **Replace fake data generator with CSV data loader**
2. ⚠️ **Implement historical data slicing from CSV files**
3. ⚠️ **Test bootstrap service with real CSV data**
4. ⚠️ **Verify TSX strategies become ready with real data**

### **Phase 1C: Integrated Backtesting**
1. ⚠️ **Create complete CSV-based backtesting system**
2. ⚠️ **Test EMA strategy with real MCL data**
3. ⚠️ **Verify signal generation with actual market conditions**
4. ⚠️ **Document results vs fake data comparison**

## Symbol Mapping for TSX Strategies

### **Your CSV Data → TSX Strategy Symbols**
- **MCL (Light Crude Oil)** → **NQ** (for TSX strategies expecting NQ)
- **MES (S&P 500 E-Mini)** → **ES** (for equity strategies)
- **MGC (Gold)** → **GC** (for gold strategies)
- **NG (Natural Gas)** → **NG** (direct mapping)
- **SI (Silver)** → **SI** (direct mapping)

## Critical Success Criteria - REVISED

### **✅ With Real CSV Data Integration:**
- TSX strategies receive REAL market data from your CSV files
- Historical bootstrap uses actual price movements and volatility patterns
- Backtesting results reflect real trading conditions
- Strategy signals based on genuine market behavior
- Meaningful backtesting for trading decisions

**This is the correct approach - using your actual market data files instead of external data sources or fake generators.**

Ready to implement CSV data integration immediately.