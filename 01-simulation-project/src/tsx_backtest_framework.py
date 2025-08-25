"""
Phase 3C: Complete Backtest Execution Framework
Comprehensive backtesting workflows for TSX strategies with PyBroker
"""

import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np

from tsx_pybroker_strategy import create_tsx_pybroker_strategy, TSXBridgeStrategy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TSXBacktestFramework:
    """
    Complete backtesting framework for TSX strategies with PyBroker integration
    Supports multiple symbols, date ranges, and comprehensive result analysis
    """
    
    def __init__(self, tsx_strategy_path: str, csv_data_directory: str):
        """
        Initialize TSX Backtesting Framework
        
        Args:
            tsx_strategy_path: Path to TSX strategy JS file
            csv_data_directory: Path to monthly CSV data files
        """
        self.tsx_strategy_path = tsx_strategy_path
        self.csv_data_directory = csv_data_directory
        
        # Framework configuration
        self.framework_config = {
            'initial_capital': 100000,  # $100k starting capital
            'symbols_supported': ['MCL', 'MES', 'MGC', 'NG', 'SI'],
            'default_symbol': 'MCL',
            'max_concurrent_positions': 1,  # TSX strategies typically single position
            'commission_per_trade': 2.50,  # Typical futures commission
            'slippage_percent': 0.01  # 1 basis point slippage
        }
        
        # Results storage
        self.backtest_results = []
        self.performance_summary = {}
        
        logger.info(f"TSX Backtest Framework initialized for {Path(tsx_strategy_path).name}")
    
    def run_single_backtest(self, symbol: str, start_date: str, end_date: str, 
                           config: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute single backtest for specified symbol and date range
        
        Args:
            symbol: Trading symbol (MCL, MES, MGC, NG, SI)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            config: Optional TSX strategy configuration
            
        Returns:
            Complete backtest results dictionary
        """
        
        logger.info(f"Running backtest: {symbol} from {start_date} to {end_date}")
        
        try:
            # Create strategy configuration
            strategy_config = config or {}
            strategy_config.update({
                'symbol': symbol,
                'botId': f'backtest_{symbol.lower()}_{int(time.time())}',
                'historicalBarsBack': 50
            })
            
            # Create PyBroker strategy with TSX integration
            start_time = time.time()
            
            strategy = create_tsx_pybroker_strategy(
                self.tsx_strategy_path,
                self.csv_data_directory,
                symbol,
                start_date,
                end_date,
                strategy_config
            )
            
            # Execute backtest
            logger.info(f"Executing PyBroker backtest...")
            backtest_result = strategy.backtest()
            
            execution_time = time.time() - start_time
            
            # Get TSX strategy performance stats
            tsx_stats = strategy._tsx_wrapper.get_performance_stats()
            
            # Compile comprehensive results
            result = {
                'execution_info': {
                    'symbol': symbol,
                    'start_date': start_date,
                    'end_date': end_date,
                    'execution_time_seconds': round(execution_time, 2),
                    'strategy_path': str(Path(self.tsx_strategy_path).name),
                    'timestamp': datetime.now().isoformat()
                },
                'pybroker_results': {
                    'initial_capital': self.framework_config['initial_capital'],
                    'final_portfolio_value': backtest_result.portfolio_value,
                    'total_return': backtest_result.total_return,
                    'total_return_percent': backtest_result.total_return * 100,
                    'max_drawdown': backtest_result.max_drawdown,
                    'max_drawdown_percent': backtest_result.max_drawdown * 100,
                    'sharpe_ratio': getattr(backtest_result, 'sharpe_ratio', None),
                    'total_trades': len(backtest_result.trades)
                },
                'tsx_strategy_stats': tsx_stats,
                'trade_analysis': self._analyze_trades(backtest_result.trades),
                'pybroker_result': backtest_result  # Store but will be processed by _prepare_for_json
            }
            
            # Cleanup strategy resources
            strategy._tsx_wrapper.cleanup()
            
            logger.info(f"Backtest completed: {result['pybroker_results']['total_return_percent']:.2f}% return")
            
            return result
            
        except Exception as e:
            logger.error(f"Backtest failed for {symbol} {start_date}-{end_date}: {e}")
            return {
                'execution_info': {
                    'symbol': symbol,
                    'start_date': start_date,
                    'end_date': end_date,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                },
                'success': False
            }
    
    def run_multi_period_backtest(self, symbol: str, base_start_date: str, 
                                 periods: int = 4, period_days: int = 30) -> List[Dict[str, Any]]:
        """
        Run multiple backtests across different time periods
        
        Args:
            symbol: Trading symbol
            base_start_date: Base start date
            periods: Number of periods to test
            period_days: Days per period
            
        Returns:
            List of backtest results
        """
        
        logger.info(f"Running multi-period backtest: {periods} periods of {period_days} days each")
        
        results = []
        base_date = datetime.strptime(base_start_date, '%Y-%m-%d')
        
        for i in range(periods):
            start_date = base_date + timedelta(days=i * period_days)
            end_date = start_date + timedelta(days=period_days)
            
            start_str = start_date.strftime('%Y-%m-%d')
            end_str = end_date.strftime('%Y-%m-%d')
            
            logger.info(f"Period {i+1}/{periods}: {start_str} to {end_str}")
            
            result = self.run_single_backtest(symbol, start_str, end_str)
            result['execution_info']['period_number'] = i + 1
            results.append(result)
            
            # Brief pause between tests
            time.sleep(1)
        
        return results
    
    def run_multi_symbol_backtest(self, start_date: str, end_date: str, 
                                 symbols: List[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run backtests across multiple symbols
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)  
            symbols: List of symbols to test (default: all supported)
            
        Returns:
            Dictionary of results keyed by symbol
        """
        
        if symbols is None:
            symbols = self.framework_config['symbols_supported']
        
        logger.info(f"Running multi-symbol backtest: {symbols}")
        
        results = {}
        
        for symbol in symbols:
            logger.info(f"Testing symbol: {symbol}")
            
            try:
                result = self.run_single_backtest(symbol, start_date, end_date)
                results[symbol] = result
                
                # Brief pause between symbols
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Failed to test {symbol}: {e}")
                results[symbol] = {
                    'execution_info': {
                        'symbol': symbol,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    },
                    'success': False
                }
        
        return results
    
    def _analyze_trades(self, trades_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze trade execution details"""
        
        if len(trades_df) == 0:
            return {
                'total_trades': 0,
                'profitable_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'average_profit': 0.0,
                'average_loss': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
        
        # Calculate trade statistics
        profitable_trades = trades_df[trades_df['pnl'] > 0] if 'pnl' in trades_df.columns else pd.DataFrame()
        losing_trades = trades_df[trades_df['pnl'] < 0] if 'pnl' in trades_df.columns else pd.DataFrame()
        
        return {
            'total_trades': len(trades_df),
            'long_trades': len(trades_df[trades_df['type'] == 'long']) if 'type' in trades_df.columns else 0,
            'short_trades': len(trades_df[trades_df['type'] == 'short']) if 'type' in trades_df.columns else 0,
            'profitable_trades': len(profitable_trades),
            'losing_trades': len(losing_trades),
            'win_rate': len(profitable_trades) / len(trades_df) * 100 if len(trades_df) > 0 else 0,
            'average_profit': profitable_trades['pnl'].mean() if len(profitable_trades) > 0 and 'pnl' in profitable_trades.columns else 0,
            'average_loss': losing_trades['pnl'].mean() if len(losing_trades) > 0 and 'pnl' in losing_trades.columns else 0,
            'largest_win': profitable_trades['pnl'].max() if len(profitable_trades) > 0 and 'pnl' in profitable_trades.columns else 0,
            'largest_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 and 'pnl' in losing_trades.columns else 0
        }
    
    def generate_performance_report(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive performance report from backtest results"""
        
        if not results:
            return {'error': 'No results to analyze'}
        
        # Filter successful results
        successful_results = [r for r in results if r.get('success', True) and 'pybroker_results' in r]
        
        if not successful_results:
            return {'error': 'No successful backtests to analyze'}
        
        # Calculate aggregate statistics
        returns = [r['pybroker_results']['total_return_percent'] for r in successful_results]
        drawdowns = [abs(r['pybroker_results']['max_drawdown_percent']) for r in successful_results]
        trade_counts = [r['pybroker_results']['total_trades'] for r in successful_results]
        
        # TSX strategy statistics
        total_signals = sum(r['tsx_strategy_stats']['total_signals'] for r in successful_results)
        total_market_bars = sum(r['tsx_strategy_stats']['market_bars_processed'] for r in successful_results)
        
        report = {
            'summary': {
                'total_backtests': len(results),
                'successful_backtests': len(successful_results),
                'success_rate': len(successful_results) / len(results) * 100,
                'strategy_name': Path(self.tsx_strategy_path).name
            },
            'performance_metrics': {
                'average_return_percent': sum(returns) / len(returns) if returns else 0,
                'best_return_percent': max(returns) if returns else 0,
                'worst_return_percent': min(returns) if returns else 0,
                'average_max_drawdown_percent': sum(drawdowns) / len(drawdowns) if drawdowns else 0,
                'worst_drawdown_percent': max(drawdowns) if drawdowns else 0,
                'average_trades_per_backtest': sum(trade_counts) / len(trade_counts) if trade_counts else 0
            },
            'tsx_strategy_metrics': {
                'total_signals_generated': total_signals,
                'total_market_bars_processed': total_market_bars,
                'signal_generation_rate': total_signals / total_market_bars * 100 if total_market_bars > 0 else 0
            },
            'detailed_results': successful_results
        }
        
        return report
    
    def save_results(self, results: Any, filename: str):
        """Save backtest results to JSON file"""
        
        output_path = Path(__file__).parent.parent / 'results' / f'{filename}.json'
        output_path.parent.mkdir(exist_ok=True)
        
        # Prepare results for JSON serialization
        json_results = self._prepare_for_json(results)
        
        with open(output_path, 'w') as f:
            json.dump(json_results, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {output_path}")
        return output_path
    
    def _prepare_for_json(self, obj):
        """Prepare object for JSON serialization"""
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        elif isinstance(obj, dict):
            return {k: self._prepare_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._prepare_for_json(item) for item in obj]
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        elif isinstance(obj, np.datetime64):
            # Convert numpy datetime64 to pandas Timestamp then to isoformat
            return pd.Timestamp(obj).isoformat()
        elif hasattr(obj, 'timestamp') and callable(getattr(obj, 'timestamp')):
            # Handle other datetime-like objects by converting to timestamp
            return datetime.fromtimestamp(obj.timestamp()).isoformat()
        else:
            return obj


def test_phase3c_backtest_framework():
    """Test Phase 3C: Complete Backtest Execution Framework"""
    
    print("=" * 80)
    print("PHASE 3C: COMPLETE BACKTEST EXECUTION FRAMEWORK TEST")
    print("Testing comprehensive backtesting workflows with TSX-PyBroker integration")
    print("=" * 80)
    
    try:
        print(f"[STEP 1] Initializing TSX Backtest Framework...")
        
        # Framework configuration
        tsx_strategy = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
        csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        framework = TSXBacktestFramework(tsx_strategy, csv_data_dir)
        
        print(f"  Framework initialized for EMA strategy")
        print(f"  Supported symbols: {framework.framework_config['symbols_supported']}")
        print(f"  Initial capital: ${framework.framework_config['initial_capital']:,}")
        
        print(f"\n[STEP 2] Testing single backtest execution...")
        
        # Single backtest test
        single_result = framework.run_single_backtest('MCL', '2023-06-05', '2023-06-07')
        
        if single_result.get('success', True):
            print(f"  Single backtest successful:")
            print(f"    Return: {single_result['pybroker_results']['total_return_percent']:.2f}%")
            print(f"    Trades: {single_result['pybroker_results']['total_trades']}")
            print(f"    TSX signals: {single_result['tsx_strategy_stats']['total_signals']}")
            print(f"    Execution time: {single_result['execution_info']['execution_time_seconds']}s")
        else:
            print(f"  Single backtest had issues: {single_result.get('execution_info', {}).get('error', 'Unknown error')}")
        
        print(f"\n[STEP 3] Testing multi-symbol backtest...")
        
        # Multi-symbol test (smaller subset)
        multi_symbol_results = framework.run_multi_symbol_backtest(
            '2023-06-01', 
            '2023-06-03',  # Short period for testing
            ['MCL', 'MES']  # Just 2 symbols for testing
        )
        
        print(f"  Multi-symbol backtest completed:")
        for symbol, result in multi_symbol_results.items():
            if result.get('success', True):
                returns = result['pybroker_results']['total_return_percent']
                trades = result['pybroker_results']['total_trades']
                print(f"    {symbol}: {returns:.2f}% return, {trades} trades")
            else:
                print(f"    {symbol}: Failed - {result.get('execution_info', {}).get('error', 'Unknown')}")
        
        print(f"\n[STEP 4] Generating performance report...")
        
        # Create comprehensive report
        all_results = [single_result] + list(multi_symbol_results.values())
        performance_report = framework.generate_performance_report(all_results)
        
        print(f"  Performance Report Generated:")
        if 'error' not in performance_report:
            summary = performance_report['summary']
            metrics = performance_report['performance_metrics']
            
            print(f"    Total backtests: {summary['total_backtests']}")
            print(f"    Success rate: {summary['success_rate']:.1f}%")
            print(f"    Average return: {metrics['average_return_percent']:.2f}%")
            print(f"    Best return: {metrics['best_return_percent']:.2f}%")
            print(f"    Average drawdown: {metrics['average_max_drawdown_percent']:.2f}%")
        else:
            print(f"    Report generation error: {performance_report['error']}")
        
        print(f"\n[STEP 5] Testing results persistence...")
        
        # Save results
        results_file = framework.save_results(performance_report, f'phase3c_test_{int(time.time())}')
        print(f"  Results saved to: {results_file}")
        
        # Verify file exists
        if results_file.exists():
            file_size = results_file.stat().st_size
            print(f"  Results file verified: {file_size} bytes")
        
        print(f"\n" + "=" * 80)
        
        # Phase 3C success criteria
        phase3c_success = (
            single_result.get('success', True) and
            len([r for r in multi_symbol_results.values() if r.get('success', True)]) > 0 and
            'error' not in performance_report and
            results_file.exists()
        )
        
        if phase3c_success:
            print(f"[SUCCESS] PHASE 3C: COMPLETE BACKTEST EXECUTION FRAMEWORK WORKING")
            print(f"[OK] Single backtest execution: OPERATIONAL")
            print(f"[OK] Multi-symbol backtesting: OPERATIONAL") 
            print(f"[OK] Performance reporting: OPERATIONAL")
            print(f"[OK] Results persistence: OPERATIONAL")
            print(f"[OK] End-to-end TSX-PyBroker backtesting framework: COMPLETE")
        else:
            print(f"[PARTIAL] PHASE 3C: Core framework working, refinements needed")
        
        print(f"=" * 80)
        
        return phase3c_success, performance_report
        
    except Exception as e:
        print(f"[ERROR] Phase 3C test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


if __name__ == "__main__":
    print(f"Session verification: {time.time()} at {datetime.now()}")
    
    success, report = test_phase3c_backtest_framework()
    
    if success:
        print(f"\nPHASE 3C COMPLETE - Ready for Phase 3D: Backtesting Reports")
    else:
        print(f"\nPHASE 3C needs refinement before proceeding")