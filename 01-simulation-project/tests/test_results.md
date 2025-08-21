# System Functionality Test Results

**Test Date:** 2025-08-20 10:57:18

## Summary
- **Total Tests:** 9
- **Passed:** 9
- **Failed:** 0
- **Success Rate:** 100.0%

## Detailed Results

### Database Connection: PASS

**Details:** Tables found: ['market_data', 'sqlite_sequence', 'contract_specs', 'portfolios', 'positions', 'trades', 'portfolio_snapshots'], Missing: []

- **tables:** ['market_data', 'sqlite_sequence', 'contract_specs', 'portfolios', 'positions', 'trades', 'portfolio_snapshots']
- **missing_tables:** []

### Market Data Availability: PASS

**Details:** Found data for 1 symbols

- **data_summary:** [('MCL', 348130, '2024-01-01T17:00:00', '2024-12-31T15:59:00')]
- **has_null_values:** False

### CSV Import Functionality: PASS

**Details:** Found 12 CSV files, parsing test: PASS

- **found_files:** 12
- **parse_success:** True

### Date Format Detection: PASS

**Details:** Date format detection: 3/3 correct

- **test_results:** [{'test_data': ['01/15/2024', '02/20/2024', '03/25/2024'], 'detected': 'MM/DD/YYYY', 'expected': 'MM/DD/YYYY', 'correct': True}, {'test_data': ['15/01/2024', '20/02/2024', '25/03/2024'], 'detected': 'DD/MM/YYYY', 'expected': 'DD/MM/YYYY', 'correct': True}, {'test_data': ['12/01/2024', '11/02/2024', '10/03/2024'], 'detected': 'MM/DD/YYYY', 'expected': 'MM/DD/YYYY', 'correct': True}]

### Strategy Loading: PASS

**Details:** Loaded 1 strategies: ['SimpleMAStrategy']

- **loaded_strategies:** ['SimpleMAStrategy']
- **instance_creation:** True

### PyBroker Integration: PASS

**Details:** PyBroker v1.2.11 integration test passed

- **version:** 1.2.11
- **strategy_created:** True
- **execution_added:** True

### Data Service API: PASS

**Details:** Health: 200, Data: 200

- **health_status:** 200
- **data_status:** 200

### Backtest Service API: PASS

**Details:** Health: 200, Strategies: 200

- **health_status:** 200
- **strategies_status:** 200
- **available_strategies:** [{'name': 'SimpleMAStrategy', 'class': 'SimpleMAStrategy', 'description': '\nSimple Moving Average Crossover Strategy\n\nGenerates:\n- LONG signals when fast MA crosses above slow MA\n- SHORT signals when fast MA crosses below slow MA\n- CLOSE_POSITION signals based on stop loss/take profit\n', 'config_required': False}]

### End-to-End Backtest: PASS

**Details:** Backtest execution: 200

- **status_code:** 200
- **result_summary:** {'strategy': 'SIMPLE_MA', 'symbol': 'MCL', 'total_trades': 0}

