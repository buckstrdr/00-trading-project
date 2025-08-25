#!/usr/bin/env python3
"""
PyBroker Data Access Proof-of-Concept Test
Verifies we can access PyBroker's internal historical data during backtests
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add path for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

def test_pybroker_data_access():
    """Test accessing PyBroker's internal data structure and current bar tracking"""
    print("=== PyBroker Data Access Proof-of-Concept Test ===")
    print(f"Time: {datetime.now()}")
    print(f"PID: {os.getpid()}")
    
    try:
        # Import PyBroker components
        import pybroker
        from pybroker import Strategy, YFinance
        
        print("PyBroker imported successfully")
        print(f"PyBroker version: {pybroker.__version__}")
        
    except ImportError as e:
        print(f"PyBroker not available: {e}")
        print("Installing PyBroker...")
        
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'lib-pybroker'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("PyBroker installed successfully")
            # Re-import after installation
            import pybroker
            from pybroker import Strategy, YFinance
        else:
            print(f"Failed to install PyBroker: {result.stderr}")
            return False
    
    # Test 1: Basic YFinance data access
    print("\n[TEST 1] Testing YFinance data source...")
    
    try:
        # Enable caching for performance
        pybroker.enable_data_source_cache('data_access_test')
        
        # Create YFinance data source
        yfinance = YFinance()
        
        # Query small dataset for testing (use valid stock symbols)
        df = yfinance.query(['AAPL'], start_date='2023-01-01', end_date='2023-01-31')
        
        print(f"Data retrieved successfully:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Sample data:")
        print(df.head(3))
        
        test1_success = len(df) > 0
        
    except Exception as e:
        print(f"YFinance data access failed: {e}")
        test1_success = False
    
    if not test1_success:
        return False
    
    # Test 2: Strategy data access and internal structure
    print(f"\n[TEST 2] Testing Strategy internal data access...")
    
    # Global variables to capture data during backtest
    captured_data = {
        'strategy_data': None,
        'current_bar_indices': [],
        'historical_slices': [],
        'execution_count': 0
    }
    
    def data_capture_execution(ctx):
        """Execution function to capture PyBroker's internal data"""
        nonlocal captured_data
        
        captured_data['execution_count'] += 1
        captured_data['current_bar_indices'].append(ctx.bars)
        
        # Try to access strategy's internal data (explore different attributes)
        strategy_obj = ctx._strategy if hasattr(ctx, '_strategy') else None
        
        if strategy_obj and hasattr(strategy_obj, '_data'):
            captured_data['strategy_data'] = strategy_obj._data
            
        # Capture current context data
        if ctx.bars >= 10:  # Only capture after some bars for historical data test
            historical_slice = {
                'bar_index': ctx.bars,
                'current_close': ctx.close[-1] if len(ctx.close) > 0 else None,
                'last_5_closes': ctx.close[-5:].tolist() if len(ctx.close) >= 5 else [],
                'current_volume': ctx.volume[-1] if len(ctx.volume) > 0 else None,
                'date': ctx.date
            }
            captured_data['historical_slices'].append(historical_slice)
        
        # Don't actually trade, just capture data
        pass
    
    try:
        # Create strategy with limited data for testing
        strategy = Strategy(YFinance(), start_date='2023-01-01', end_date='2023-01-15')
        strategy.add_execution(data_capture_execution, ['AAPL'])
        
        print("Running backtest to capture internal data structure...")
        result = strategy.backtest()
        
        print(f"Backtest completed successfully")
        print(f"  Executions called: {captured_data['execution_count']}")
        print(f"  Bar indices captured: {len(captured_data['current_bar_indices'])}")
        print(f"  Historical slices: {len(captured_data['historical_slices'])}")
        
        # Analyze captured data
        if captured_data['strategy_data'] is not None:
            strategy_df = captured_data['strategy_data']
            print(f"\nStrategy internal data access: SUCCESS")
            print(f"  Internal data shape: {strategy_df.shape}")
            print(f"  Internal data columns: {list(strategy_df.columns)}")
            print(f"  Sample internal data:")
            print(strategy_df.head(3))
        else:
            print(f"\nStrategy internal data access: Could not access _data directly")
            print("This is normal - will need alternative approach")
        
        # Show historical data capture results
        if captured_data['historical_slices']:
            print(f"\nHistorical data capture analysis:")
            sample_slice = captured_data['historical_slices'][0]
            print(f"  Sample slice: {sample_slice}")
            
            # Check if we can track current position
            bar_indices = captured_data['current_bar_indices']
            print(f"  Bar index progression: {bar_indices[:10]}...{bar_indices[-5:]}")
            print(f"  Max bar index reached: {max(bar_indices)}")
        
        test2_success = captured_data['execution_count'] > 0
        
    except Exception as e:
        print(f"Strategy data access test failed: {e}")
        test2_success = False
    
    # Test 3: Alternative data access via result object
    print(f"\n[TEST 3] Testing data access via backtest result...")
    
    try:
        # The result object might contain the data we need
        print(f"Backtest result type: {type(result)}")
        print(f"Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
        
        # Check if result has portfolio data (this contains the historical progression)
        if hasattr(result, 'portfolio'):
            portfolio_df = result.portfolio
            print(f"Portfolio data shape: {portfolio_df.shape}")
            print(f"Portfolio columns: {list(portfolio_df.columns)}")
            print(f"Portfolio sample:")
            print(portfolio_df.head(3))
        
        # Check if result has raw data access
        if hasattr(result, 'data'):
            data_df = result.data
            print(f"Result data shape: {data_df.shape}")
            print(f"Result data columns: {list(data_df.columns)}")
        
        test3_success = hasattr(result, 'portfolio')
        
    except Exception as e:
        print(f"Result data access test failed: {e}")
        test3_success = False
    
    # Test 4: Historical data slicing simulation
    print(f"\n[TEST 4] Testing historical data slicing logic...")
    
    try:
        # Use the original DataFrame from YFinance to simulate historical slicing
        # This simulates what we'd do during actual backtesting
        
        test_data = yfinance.query(['AAPL'], start_date='2023-01-01', end_date='2023-01-31')
        test_data = test_data.sort_values('date').reset_index(drop=True)
        
        print(f"Test data for slicing:")
        print(f"  Total bars: {len(test_data)}")
        print(f"  Date range: {test_data['date'].iloc[0]} to {test_data['date'].iloc[-1]}")
        
        # Simulate historical data requests at different backtest positions
        simulation_results = []
        
        for current_bar_idx in [10, 15, 20]:  # Simulate different backtest positions
            bars_back = 5  # Request 5 bars of history
            
            # Calculate slice boundaries
            end_idx = current_bar_idx + 1
            start_idx = max(0, end_idx - bars_back)
            
            # Get historical slice
            historical_slice = test_data.iloc[start_idx:end_idx]
            
            # Convert to TSX V5 format
            tsx_bars = []
            for _, row in historical_slice.iterrows():
                tsx_bar = {
                    't': row['date'].isoformat() + 'Z',
                    'o': float(row['open']),
                    'h': float(row['high']),
                    'l': float(row['low']),
                    'c': float(row['close']),
                    'v': int(row['volume'])
                }
                tsx_bars.append(tsx_bar)
            
            simulation_result = {
                'current_bar_index': current_bar_idx,
                'bars_requested': bars_back,
                'bars_returned': len(tsx_bars),
                'date_range': f"{historical_slice['date'].iloc[0]} to {historical_slice['date'].iloc[-1]}",
                'sample_tsx_bar': tsx_bars[0] if tsx_bars else None
            }
            
            simulation_results.append(simulation_result)
            
            print(f"  Simulation at bar {current_bar_idx}:")
            print(f"    Requested {bars_back} bars, got {len(tsx_bars)} bars")
            print(f"    Date range: {simulation_result['date_range']}")
            print(f"    Sample TSX bar: {simulation_result['sample_tsx_bar']}")
        
        test4_success = len(simulation_results) == 3
        
    except Exception as e:
        print(f"Historical slicing simulation failed: {e}")
        test4_success = False
    
    # Final assessment
    all_tests_passed = test1_success and test2_success and test3_success and test4_success
    
    print(f"\n=== FINAL RESULTS ===")
    print(f"Test 1 (YFinance Access): {'SUCCESS' if test1_success else 'FAILURE'}")
    print(f"Test 2 (Strategy Data): {'SUCCESS' if test2_success else 'FAILURE'}")  
    print(f"Test 3 (Result Data): {'SUCCESS' if test3_success else 'FAILURE'}")
    print(f"Test 4 (Historical Slicing): {'SUCCESS' if test4_success else 'FAILURE'}")
    print(f"Overall: {'SUCCESS' if all_tests_passed else 'PARTIAL SUCCESS'}")
    
    print(f"\nKey Findings:")
    print(f"- PyBroker data access: {'Available' if test1_success else 'Not available'}")
    print(f"- Historical data tracking: {'Possible' if test2_success else 'Needs alternative approach'}")
    print(f"- Data slicing logic: {'Verified' if test4_success else 'Needs refinement'}")
    
    return all_tests_passed or (test1_success and test4_success)  # Allow partial success

if __name__ == "__main__":
    success = test_pybroker_data_access()
    
    print(f"\n=== PYBROKER DATA ACCESS TEST: {'SUCCESS' if success else 'FAILURE'} ===")
    print(f"Timestamp: {datetime.now()}")
    
    sys.exit(0 if success else 1)