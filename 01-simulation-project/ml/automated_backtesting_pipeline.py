#!/usr/bin/env python3
"""
Automated Backtesting Pipeline - Phase 4A Implementation
TSX Strategy Bridge ML Optimization Framework

Purpose: Generate systematic backtesting datasets for ML analysis
- Multi-symbol backtesting across all instruments
- Multiple date ranges and market conditions
- Parameter variation testing
- Market regime-specific analysis
"""

import os
import sys
import json
import logging
import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import itertools
import time

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))
sys.path.append(str(project_root / "shared"))

try:
    from tsx_backtest_framework import TSXBacktestFramework
    HAS_TSX_FRAMEWORK = True
except ImportError as e:
    print(f"TSX Framework import error: {e}")
    HAS_TSX_FRAMEWORK = False
    print("Available files in src/:")
    if (project_root / "src").exists():
        for file in (project_root / "src").iterdir():
            if file.suffix == '.py':
                print(f"  {file.name}")


class BacktestResultsDB:
    """Store and manage backtesting results for ML analysis"""
    
    def __init__(self, db_path: str = "ml/backtest_results.json"):
        self.db_path = Path(project_root) / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.results = self._load_db()
        
    def _load_db(self) -> List[Dict]:
        """Load existing database"""
        if self.db_path.exists():
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return []
        
    def save_result(self, result: Dict) -> str:
        """Save backtest result and return ID"""
        result_id = f"bt_{int(time.time())}_{len(self.results)}"
        result['backtest_id'] = result_id
        result['timestamp'] = datetime.datetime.now().isoformat()
        
        self.results.append(result)
        
        # Save to file
        with open(self.db_path, 'w') as f:
            json.dump(self.results, f, indent=2)
            
        return result_id
        
    def get_results_count(self) -> int:
        """Get total number of results"""
        return len(self.results)
        
    def get_results_by_symbol(self, symbol: str) -> List[Dict]:
        """Get results for specific symbol"""
        return [r for r in self.results if r.get('symbol') == symbol]


class MarketConditionAnalyzer:
    """Classify market conditions for correlation analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_market_data(self, data: pd.DataFrame, symbol: str, period: str) -> Dict[str, Any]:
        """Analyze market conditions from OHLCV data"""
        try:
            if data.empty:
                return self._default_conditions()
                
            # Basic price statistics
            high_low_range = (data['high'].max() - data['low'].min()) / data['close'].mean()
            volatility = data['close'].pct_change().std() * np.sqrt(252)  # Annualized
            
            # Trend analysis
            price_change = (data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]
            trend_strength = abs(price_change)
            
            # Volume analysis (if available)
            avg_volume = data.get('volume', pd.Series([1000] * len(data))).mean()
            
            # Market regime classification
            regime = self._classify_regime(data)
            
            return {
                'symbol': symbol,
                'period': period,
                'volatility_regime': 'high' if volatility > 0.25 else 'low',
                'trend_strength': float(trend_strength),
                'trend_direction': 'bullish' if price_change > 0 else 'bearish',
                'market_regime': regime,
                'volatility_value': float(volatility),
                'price_range_pct': float(high_low_range),
                'avg_volume': float(avg_volume),
                'total_bars': len(data)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market data for {symbol}: {e}")
            return self._default_conditions()
            
    def _classify_regime(self, data: pd.DataFrame) -> str:
        """Classify market regime as trending or ranging"""
        try:
            # Simple trend detection using moving averages
            if len(data) < 20:
                return 'insufficient_data'
                
            sma_10 = data['close'].rolling(10).mean()
            sma_20 = data['close'].rolling(20).mean()
            
            # Count periods where short MA > long MA
            trending_periods = (sma_10 > sma_20).sum()
            trend_ratio = trending_periods / len(sma_10.dropna())
            
            if trend_ratio > 0.7:
                return 'strong_uptrend'
            elif trend_ratio < 0.3:
                return 'strong_downtrend'
            else:
                return 'ranging'
                
        except Exception:
            return 'unknown'
            
    def _default_conditions(self) -> Dict[str, Any]:
        """Return default market conditions for error cases"""
        return {
            'volatility_regime': 'unknown',
            'trend_strength': 0.0,
            'trend_direction': 'unknown',
            'market_regime': 'unknown',
            'volatility_value': 0.0,
            'price_range_pct': 0.0,
            'avg_volume': 0.0,
            'total_bars': 0
        }


class BacktestConfigGenerator:
    """Generate systematic parameter variations for testing"""
    
    def __init__(self):
        self.strategy_configs = {
            'EMA_CROSS': {
                'base_params': {
                    'fast_period': 10,
                    'slow_period': 20,
                    'risk_per_trade': 50
                },
                'variations': {
                    'fast_period': [5, 8, 10, 12, 15],
                    'slow_period': [15, 20, 25, 30, 35],
                    'risk_per_trade': [25, 50, 75, 100]
                }
            },
            'ORB_RUBBER_BAND': {
                'base_params': {
                    'orb_period': 30,
                    'rubber_band_pct': 0.5,
                    'risk_per_trade': 50
                },
                'variations': {
                    'orb_period': [15, 20, 30, 45, 60],
                    'rubber_band_pct': [0.3, 0.5, 0.7, 1.0],
                    'risk_per_trade': [25, 50, 75, 100]
                }
            },
            'TEST_TIME_STRATEGY': {
                'base_params': {
                    'interval_minutes': 5,
                    'hold_minutes': 3,
                    'risk_per_trade': 50
                },
                'variations': {
                    'interval_minutes': [3, 5, 10, 15],
                    'hold_minutes': [2, 3, 5, 10],
                    'risk_per_trade': [25, 50, 75, 100]
                }
            },
            'PDHPDL_COMPREHENSIVE': {
                'base_params': {
                    'lookback_days': 1,
                    'breakout_threshold': 0.1,
                    'risk_per_trade': 50
                },
                'variations': {
                    'lookback_days': [1, 2, 3],
                    'breakout_threshold': [0.05, 0.1, 0.15, 0.2],
                    'risk_per_trade': [25, 50, 75, 100]
                }
            }
        }
        
    def generate_parameter_combinations(self, strategy: str, max_combinations: int = 50) -> List[Dict]:
        """Generate parameter combinations for strategy"""
        if strategy not in self.strategy_configs:
            return [{}]
            
        config = self.strategy_configs[strategy]
        base_params = config['base_params']
        variations = config['variations']
        
        # Generate all combinations
        param_names = list(variations.keys())
        param_values = list(variations.values())
        
        combinations = []
        for combo in itertools.product(*param_values):
            params = base_params.copy()
            for i, param_name in enumerate(param_names):
                params[param_name] = combo[i]
            combinations.append(params)
            
            if len(combinations) >= max_combinations:
                break
                
        return combinations


class AutomatedBacktestingPipeline:
    """Main pipeline for systematic backtesting across multiple conditions"""
    
    def __init__(self, symbols: List[str] = None, max_workers: int = 4):
        self.symbols = symbols or ['MCL', 'MES', 'MGC', 'NG', 'SI']
        self.max_workers = max_workers
        self.logger = self._setup_logging()
        
        # Initialize components
        self.results_db = BacktestResultsDB()
        self.market_analyzer = MarketConditionAnalyzer()
        self.config_generator = BacktestConfigGenerator()
        
        # Available strategies
        self.strategies = ['EMA_CROSS', 'ORB_RUBBER_BAND', 'TEST_TIME_STRATEGY', 'PDHPDL_COMPREHENSIVE']
        
        # Date ranges for testing (August 2023 as example)
        self.test_periods = [
            ('2023-08-01', '2023-08-31')  # Full month
        ]
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the pipeline"""
        logger = logging.getLogger('AutomatedBacktesting')
        logger.setLevel(logging.INFO)
        
        # Create handler if not exists
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def generate_systematic_backtests(self, target_backtests: int = 100) -> Dict[str, Any]:
        """Generate comprehensive backtesting dataset"""
        self.logger.info(f"Starting systematic backtesting - Target: {target_backtests} results")
        
        start_time = time.time()
        completed_backtests = 0
        errors = 0
        
        results_summary = {
            'total_backtests': 0,
            'successful_backtests': 0,
            'failed_backtests': 0,
            'symbols_tested': {},
            'strategies_tested': {},
            'execution_time': 0,
            'results_by_symbol': {}
        }
        
        # Generate backtest jobs
        backtest_jobs = self._generate_backtest_jobs(target_backtests)
        
        self.logger.info(f"Generated {len(backtest_jobs)} backtest jobs")
        
        # Execute backtests
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_job = {
                executor.submit(self._execute_single_backtest, job): job 
                for job in backtest_jobs
            }
            
            for future in as_completed(future_to_job):
                job = future_to_job[future]
                try:
                    result = future.result()
                    if result and result.get('success', False):
                        # Save successful result
                        result_id = self.results_db.save_result(result)
                        completed_backtests += 1
                        
                        # Update summary
                        symbol = result.get('symbol', 'unknown')
                        strategy = result.get('strategy', 'unknown')
                        
                        if symbol not in results_summary['symbols_tested']:
                            results_summary['symbols_tested'][symbol] = 0
                        results_summary['symbols_tested'][symbol] += 1
                        
                        if strategy not in results_summary['strategies_tested']:
                            results_summary['strategies_tested'][strategy] = 0
                        results_summary['strategies_tested'][strategy] += 1
                        
                        if symbol not in results_summary['results_by_symbol']:
                            results_summary['results_by_symbol'][symbol] = []
                        results_summary['results_by_symbol'][symbol].append(result_id)
                        
                        self.logger.info(
                            f"Completed backtest {completed_backtests}/{len(backtest_jobs)}: "
                            f"{symbol}-{strategy} ({result.get('total_trades', 0)} trades)"
                        )
                    else:
                        errors += 1
                        self.logger.warning(f"Backtest failed: {job}")
                        
                except Exception as e:
                    errors += 1
                    self.logger.error(f"Error in backtest execution: {e}")
                    
        # Finalize results
        execution_time = time.time() - start_time
        results_summary.update({
            'total_backtests': len(backtest_jobs),
            'successful_backtests': completed_backtests,
            'failed_backtests': errors,
            'execution_time': execution_time,
            'backtests_per_hour': completed_backtests / (execution_time / 3600) if execution_time > 0 else 0
        })
        
        self.logger.info(f"Pipeline completed: {completed_backtests} successful backtests in {execution_time:.2f}s")
        return results_summary
        
    def _generate_backtest_jobs(self, target_count: int) -> List[Dict]:
        """Generate list of backtest jobs to execute"""
        jobs = []
        
        # Distribute jobs across symbols and strategies
        jobs_per_symbol = target_count // len(self.symbols)
        jobs_per_strategy = jobs_per_symbol // len(self.strategies)
        
        for symbol in self.symbols:
            for strategy in self.strategies:
                # Generate parameter variations
                param_combinations = self.config_generator.generate_parameter_combinations(
                    strategy, max_combinations=jobs_per_strategy
                )
                
                for i, params in enumerate(param_combinations):
                    if len(jobs) >= target_count:
                        break
                        
                    for start_date, end_date in self.test_periods:
                        job = {
                            'symbol': symbol,
                            'strategy': strategy,
                            'start_date': start_date,
                            'end_date': end_date,
                            'parameters': params,
                            'job_id': f"{symbol}_{strategy}_{i}_{start_date}"
                        }
                        jobs.append(job)
                        
                        if len(jobs) >= target_count:
                            break
                    
                    if len(jobs) >= target_count:
                        break
                
                if len(jobs) >= target_count:
                    break
            
            if len(jobs) >= target_count:
                break
                
        return jobs[:target_count]
        
    def _execute_single_backtest(self, job: Dict) -> Dict[str, Any]:
        """Execute a single REAL backtest job using TSX framework"""
        try:
            symbol = job['symbol']
            strategy = job['strategy']
            start_date = job['start_date']
            end_date = job['end_date']
            parameters = job['parameters']
            
            self.logger.info(f"Starting REAL backtest: {symbol}-{strategy} {start_date} to {end_date}")
            
            if not HAS_TSX_FRAMEWORK:
                return {'success': False, 'error': 'TSX Framework not available - cannot run real backtests'}
                
            # Load market data file
            data_file = self._get_data_file(symbol, start_date)
            if not data_file or not os.path.exists(data_file):
                return {'success': False, 'error': f'Data file not found for {symbol}: {data_file}'}
                
            # Load data for market analysis
            try:
                data = pd.read_csv(data_file)
                if data.empty:
                    return {'success': False, 'error': f'Empty data file for {symbol}'}
                    
                self.logger.info(f"Loaded {len(data)} data points for {symbol}")
                    
            except Exception as e:
                return {'success': False, 'error': f'Failed to load data: {e}'}
                
            # Get strategy file path
            strategy_file = self._get_strategy_file(strategy)
            if not strategy_file or not os.path.exists(strategy_file):
                return {'success': False, 'error': f'Strategy file not found: {strategy}'}
                
            # Analyze market conditions
            market_conditions = self.market_analyzer.analyze_market_data(data, symbol, f"{start_date}_{end_date}")
            
            # Execute REAL backtest using TSX framework
            try:
                # Fix data directory path: go up to 98-month-by-month-data-files root
                # data_file is: .../98-month-by-month-data-files/MCL/2023/08-August/MCL_2023_08_August.csv
                # We need: .../98-month-by-month-data-files
                csv_data_dir = str(Path(data_file).parent.parent.parent.parent)  # Go up 4 levels
                
                backtest_framework = TSXBacktestFramework(
                    tsx_strategy_path=strategy_file,
                    csv_data_directory=csv_data_dir
                )
                
                # Run the actual backtest
                self.logger.info(f"Executing real backtest with TSX framework...")
                backtest_result = backtest_framework.run_single_backtest(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date
                )
                
                if not backtest_result or not backtest_result.get('success', True):
                    error_msg = backtest_result.get('error', 'Unknown backtest error') if backtest_result else 'No result returned'
                    return {'success': False, 'error': f'Backtest execution failed: {error_msg}'}
                    
                # Extract performance metrics from real backtest
                performance_metrics = self._extract_performance_metrics(backtest_result)
                
                self.logger.info(f"Real backtest completed: {performance_metrics.get('total_trades', 0)} trades, {performance_metrics.get('total_return', 0):.4f} return")
                
            except Exception as e:
                self.logger.error(f"TSX Framework execution error: {e}")
                return {'success': False, 'error': f'Backtest execution error: {str(e)}'}
            
            # Compile result with REAL data
            result = {
                'success': True,
                'backtest_id': job['job_id'],
                'symbol': symbol,
                'strategy': strategy,
                'start_date': start_date,
                'end_date': end_date,
                'strategy_params': parameters,
                'market_conditions': market_conditions.to_dict() if hasattr(market_conditions, 'to_dict') else market_conditions,
                'performance_metrics': performance_metrics,
                'data_points': len(data),
                'execution_timestamp': datetime.datetime.now().isoformat(),
                'backtest_type': 'REAL_TSX_FRAMEWORK',
                'raw_backtest_result': backtest_result  # Include full result for debugging
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in real backtest execution: {e}")
            return {'success': False, 'error': str(e)}
            
    def _get_data_file(self, symbol: str, start_date: str) -> str:
        """Get CSV data file path for symbol and date"""
        # Extract year and month from start_date
        try:
            date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            year = date_obj.year
            month = date_obj.strftime('%m-%B')
            
            # Construct path based on project structure
            data_path = (project_root.parent / "98-month-by-month-data-files" / 
                        symbol / str(year) / month / f"{symbol}_{year}_{date_obj.strftime('%m')}_{date_obj.strftime('%B')}.csv")
            
            return str(data_path) if data_path.exists() else None
            
        except Exception:
            return None
            
    def _get_strategy_file(self, strategy: str) -> str:
        """Get strategy file path for TSX strategy"""
        strategy_paths = {
            'EMA_CROSS': '03-trading-bot/TSX-Trading-Bot-V5/src/strategies/ema/emaStrategy.js',
            'ORB_RUBBER_BAND': '03-trading-bot/TSX-Trading-Bot-V5/src/strategies/orb-rubber-band/ORBRubberBandStrategy.js',
            'TEST_TIME_STRATEGY': '03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js',
            'PDHPDL_COMPREHENSIVE': '03-trading-bot/TSX-Trading-Bot-V5/src/strategies/PDHPDL/PDHPDLStrategy-Comprehensive.js'
        }
        
        strategy_path = strategy_paths.get(strategy)
        if strategy_path:
            full_path = project_root.parent / strategy_path
            return str(full_path) if full_path.exists() else None
        return None
        
    def _extract_performance_metrics(self, backtest_result: Dict) -> Dict[str, float]:
        """Extract performance metrics from TSX backtest result"""
        try:
            if not backtest_result:
                return self._default_performance_metrics()
                
            # Extract from PyBroker results
            pybroker_results = backtest_result.get('pybroker_results', {})
            trade_analysis = backtest_result.get('trade_analysis', {})
            
            # Core performance metrics
            total_return = pybroker_results.get('total_return', 0.0)
            total_trades = pybroker_results.get('total_trades', 0)
            max_drawdown = pybroker_results.get('max_drawdown', 0.0)
            sharpe_ratio = pybroker_results.get('sharpe_ratio', 0.0)
            
            # Trade analysis metrics
            win_rate = trade_analysis.get('win_rate', 0.0)
            profit_factor = trade_analysis.get('profit_factor', 0.0)
            avg_win = trade_analysis.get('avg_win', 0.0)
            avg_loss = trade_analysis.get('avg_loss', 0.0)
            
            # Calculate additional metrics
            initial_capital = pybroker_results.get('initial_capital', 100000)
            total_pnl = total_return * initial_capital
            
            return {
                'total_trades': total_trades,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'total_return': total_return,
                'profit_factor': profit_factor,
                'avg_win': avg_win,
                'avg_loss': abs(avg_loss),  # Make loss positive for consistency
                'max_drawdown': abs(max_drawdown),
                'sharpe_ratio': sharpe_ratio,
                'max_win': trade_analysis.get('max_win', 0.0),
                'max_loss': abs(trade_analysis.get('max_loss', 0.0))
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting performance metrics: {e}")
            return self._default_performance_metrics()
            
    def _default_performance_metrics(self) -> Dict[str, float]:
        """Return default performance metrics for error cases"""
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'total_pnl': 0.0,
            'total_return': 0.0,
            'profit_factor': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'max_win': 0.0,
            'max_loss': 0.0
        }
            
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get current pipeline status and statistics"""
        total_results = self.results_db.get_results_count()
        
        status = {
            'total_backtests_completed': total_results,
            'results_by_symbol': {},
            'results_by_strategy': {},
            'latest_execution': None
        }
        
        # Analyze results by symbol and strategy
        for result in self.results_db.results:
            symbol = result.get('symbol', 'unknown')
            strategy = result.get('strategy', 'unknown')
            
            if symbol not in status['results_by_symbol']:
                status['results_by_symbol'][symbol] = 0
            status['results_by_symbol'][symbol] += 1
            
            if strategy not in status['results_by_strategy']:
                status['results_by_strategy'][strategy] = 0
            status['results_by_strategy'][strategy] += 1
            
        # Get latest execution timestamp
        if self.results_db.results:
            status['latest_execution'] = max(
                result.get('execution_timestamp', '') for result in self.results_db.results
            )
            
        return status


def main():
    """Main execution for REAL backtesting pipeline test"""
    print("=== REAL Automated Backtesting Pipeline - Phase 4A CORRECTED ===")
    print(f"Start time: {datetime.datetime.now()}")
    print("WARNING: This will run REAL backtests and may take several minutes")
    
    # Check if TSX framework is available
    if not HAS_TSX_FRAMEWORK:
        print("ERROR: TSX Framework not available - cannot run real backtests")
        print("Available files in src/:")
        if (project_root / "src").exists():
            for file in (project_root / "src").iterdir():
                if file.suffix == '.py':
                    print(f"  {file.name}")
        return
        
    # Verify strategy files exist
    print("\nVerifying strategy files...")
    strategy_paths = {
        'EMA_CROSS': '03-trading-bot/TSX-Trading-Bot-V5/src/strategies/ema/emaStrategy.js',
        'TEST_TIME_STRATEGY': '03-trading-bot/TSX-Trading-Bot-V5/src/strategies/test/testTimeStrategy.js'
    }
    
    available_strategies = []
    for strategy, path in strategy_paths.items():
        full_path = project_root.parent / path
        if full_path.exists():
            available_strategies.append(strategy)
            print(f"FOUND {strategy}: {path}")
        else:
            print(f"NOT FOUND {strategy}: {path}")
            
    if not available_strategies:
        print("ERROR: No strategy files found - cannot run real backtests")
        return
        
    # Verify data files exist
    print("\nVerifying data files...")
    data_files_found = 0
    for symbol in ['MCL', 'MES']:
        data_path = project_root.parent / "98-month-by-month-data-files" / symbol / "2023" / "08-August" / f"{symbol}_2023_08_August.csv"
        if data_path.exists():
            data_files_found += 1
            print(f"FOUND {symbol}: {data_path}")
        else:
            print(f"NOT FOUND {symbol}: {data_path}")
            
    if data_files_found == 0:
        print("ERROR: No data files found - cannot run real backtests")
        return
    
    # Initialize pipeline with all verified symbols
    verified_symbols = []
    for symbol in ['MCL', 'MES', 'MGC', 'NG', 'SI']:
        data_path = project_root.parent / "98-month-by-month-data-files" / symbol / "2023" / "08-August" / f"{symbol}_2023_08_August.csv"
        if data_path.exists():
            verified_symbols.append(symbol)
    
    pipeline = AutomatedBacktestingPipeline(verified_symbols, max_workers=1)
    
    # Run pipeline with FULL REAL test batch
    target_backtests = len(available_strategies) * len(verified_symbols)  # Full matrix
    print(f"\nGenerating {target_backtests} REAL backtests...")
    print(f"Testing {len(available_strategies)} strategies × {len(verified_symbols)} symbols")
    print(f"Expected total time: {target_backtests * 5}-{target_backtests * 15} minutes")
    print("WARNING: This is a comprehensive test that will take significant time...")
    
    start_time = datetime.datetime.now()
    results = pipeline.generate_systematic_backtests(target_backtests=target_backtests)
    end_time = datetime.datetime.now()
    
    print(f"\nREAL Pipeline Results:")
    print(f"- Total backtests: {results['total_backtests']}")
    print(f"- Successful: {results['successful_backtests']}")
    print(f"- Failed: {results['failed_backtests']}")
    print(f"- Execution time: {results['execution_time']:.2f}s ({(end_time-start_time).total_seconds():.2f}s wall time)")
    
    if results['successful_backtests'] > 0:
        print(f"- Average time per backtest: {results['execution_time']/results['successful_backtests']:.2f}s")
    
    print(f"\nSymbols tested: {results['symbols_tested']}")
    print(f"Strategies tested: {results['strategies_tested']}")
    
    # Show pipeline status  
    status = pipeline.get_pipeline_status()
    print(f"\nPipeline Status:")
    print(f"- Total results in database: {status['total_backtests_completed']}")
    print(f"- Latest execution: {status['latest_execution']}")
    
    # Show sample results if any successful
    if results['successful_backtests'] > 0 and pipeline.results_db.results:
        print(f"\nSample REAL backtest result:")
        sample_result = pipeline.results_db.results[-1]  # Latest result
        perf = sample_result.get('performance_metrics', {})
        print(f"- Symbol: {sample_result.get('symbol')}")
        print(f"- Strategy: {sample_result.get('strategy')}")
        print(f"- Trades: {perf.get('total_trades', 0)}")
        print(f"- Win Rate: {perf.get('win_rate', 0):.2f}%")
        print(f"- Total Return: {perf.get('total_return', 0):.4f}")
        print(f"- Total P&L: ${perf.get('total_pnl', 0):.2f}")
        print(f"- Backtest Type: {sample_result.get('backtest_type', 'unknown')}")
    
    print(f"\nREAL execution completed at: {datetime.datetime.now()}")


if __name__ == "__main__":
    main()