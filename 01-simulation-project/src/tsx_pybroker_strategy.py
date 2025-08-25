"""
Phase 3A: PyBroker Strategy Wrapper for Enhanced TSX Strategy Bridge
Integrates TSX Trading Bot V5 strategies with PyBroker backtesting framework
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

# PyBroker imports
from pybroker import Strategy, ExecContext, StrategyConfig
import pandas as pd
import numpy as np

# Enhanced TSX Strategy Bridge
import sys
sys.path.append(str(Path(__file__).parent.parent / 'shared'))
from claude_enhanced_tsx_strategy_bridge import EnhancedTSXStrategyBridge

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TSXBridgeStrategy:
    """
    PyBroker Strategy wrapper for TSX Trading Bot V5 strategies
    Enables TSX strategies to run in PyBroker backtesting with real CSV data
    """
    
    def __init__(self, tsx_strategy_path: str, csv_data_directory: str, config: Dict[str, Any] = None):
        """
        Initialize TSX Bridge Strategy for PyBroker
        
        Args:
            tsx_strategy_path: Path to TSX strategy JS file
            csv_data_directory: Path to monthly CSV data files
            config: Strategy configuration
        """
        self.tsx_strategy_path = tsx_strategy_path
        self.csv_data_directory = csv_data_directory
        self.config = config or {}
        
        # Default configuration
        self.config.setdefault('botId', 'pybroker_tsx_bot')
        self.config.setdefault('symbol', 'MCL')
        self.config.setdefault('redisHost', 'localhost')
        self.config.setdefault('redisPort', 6379)
        self.config.setdefault('historicalBarsBack', 50)
        
        # Enhanced TSX Strategy Bridge
        self.bridge = None
        
        # Strategy state
        self.initialized = False
        self.signals_generated = []
        self.current_position = None
        self.trade_count = 0
        
        # Performance tracking
        self.performance_stats = {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'trades_executed': 0,
            'market_bars_processed': 0
        }
        
        logger.info(f"TSX Bridge Strategy initialized for {Path(tsx_strategy_path).name}")
    
    def create_pybroker_strategy_function(self):
        """
        Create PyBroker-compatible strategy execution function
        Returns function that can be used with strategy.add_execution()
        """
        
        def tsx_strategy_execution(ctx: ExecContext):
            """
            PyBroker execution function that uses TSX strategy via Enhanced Bridge
            
            Args:
                ctx: PyBroker execution context with market data and trading methods
            """
            try:
                # Initialize bridge on first execution
                if not self.initialized:
                    self._initialize_bridge()
                    
                    # Set simulation datetime to match PyBroker backtest
                    if hasattr(ctx, 'date') and len(ctx.date) > 0:
                        current_date = ctx.date[-1]
                        if hasattr(current_date, 'to_pydatetime'):
                            sim_datetime = current_date.to_pydatetime()
                        else:
                            sim_datetime = current_date
                        self.bridge.set_simulation_datetime(sim_datetime)
                        logger.info(f"Set bridge simulation datetime to: {sim_datetime}")
                
                # Get current bar data from PyBroker context
                current_bar = self._extract_bar_data_from_context(ctx)
                
                # Process market data through Enhanced TSX Bridge
                tsx_signal = self.bridge.process_market_data(current_bar)
                
                self.performance_stats['market_bars_processed'] += 1
                
                # Execute trades based on TSX strategy signals
                if tsx_signal:
                    self._execute_tsx_signal(tsx_signal, ctx)
                    self.performance_stats['total_signals'] += 1
                    
                    signal_action = tsx_signal.get('action', 'UNKNOWN')
                    if 'BUY' in signal_action.upper():
                        self.performance_stats['buy_signals'] += 1
                    elif 'SELL' in signal_action.upper():
                        self.performance_stats['sell_signals'] += 1
                
            except Exception as e:
                logger.error(f"Error in TSX strategy execution: {e}")
                
        return tsx_strategy_execution
    
    def _initialize_bridge(self):
        """Initialize Enhanced TSX Strategy Bridge"""
        try:
            logger.info("Initializing Enhanced TSX Strategy Bridge for PyBroker...")
            
            # Create Enhanced Bridge
            self.bridge = EnhancedTSXStrategyBridge(
                self.tsx_strategy_path,
                self.csv_data_directory,
                self.config
            )
            
            # Start the bridge
            ready = self.bridge.start()
            
            if ready:
                logger.info("Enhanced TSX Strategy Bridge ready for PyBroker integration")
            else:
                logger.warning("Enhanced TSX Strategy Bridge started but ready status unclear")
            
            self.initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize Enhanced TSX Strategy Bridge: {e}")
            raise
    
    def _extract_bar_data_from_context(self, ctx: ExecContext) -> Dict[str, Any]:
        """
        Extract current bar data from PyBroker execution context
        
        Args:
            ctx: PyBroker execution context
            
        Returns:
            Bar data dictionary compatible with Enhanced Bridge
        """
        try:
            # Extract OHLCV data from PyBroker context (current bar = index -1)
            bar_data = {
                'symbol': ctx.symbol,
                'open': float(ctx.open[-1]),
                'high': float(ctx.high[-1]),
                'low': float(ctx.low[-1]),
                'close': float(ctx.close[-1]),
                'volume': float(ctx.volume[-1]) if hasattr(ctx, 'volume') and len(ctx.volume) > 0 else 0,
                'timestamp': ctx.date[-1] if hasattr(ctx, 'date') and len(ctx.date) > 0 else datetime.now()
            }
            
            return bar_data
            
        except Exception as e:
            logger.error(f"Error extracting bar data from PyBroker context: {e}")
            # Return minimal bar data as fallback
            return {
                'symbol': getattr(ctx, 'symbol', 'UNKNOWN'),
                'close': float(ctx.close[-1]) if hasattr(ctx, 'close') and len(ctx.close) > 0 else 0,
                'timestamp': datetime.now()
            }
    
    def _execute_tsx_signal(self, tsx_signal: Dict[str, Any], ctx: ExecContext):
        """
        Execute PyBroker trades based on TSX strategy signals
        
        Args:
            tsx_signal: Signal from TSX strategy
            ctx: PyBroker execution context
        """
        try:
            signal_action = tsx_signal.get('action', '').upper()
            signal_price = tsx_signal.get('price', ctx.close[-1])
            
            logger.info(f"Processing TSX signal: {signal_action} at {signal_price}")
            
            # Convert TSX signals to PyBroker actions
            if 'BUY' in signal_action or 'LONG' in signal_action:
                self._execute_buy_signal(tsx_signal, ctx)
                
            elif 'SELL' in signal_action or 'SHORT' in signal_action:
                self._execute_sell_signal(tsx_signal, ctx)
                
            elif 'CLOSE' in signal_action or 'EXIT' in signal_action:
                self._execute_close_signal(tsx_signal, ctx)
            
            # Store signal for analysis
            self.signals_generated.append({
                'signal': tsx_signal,
                'executed_at': datetime.now().isoformat(),
                'pybroker_index': ctx.index
            })
            
        except Exception as e:
            logger.error(f"Error executing TSX signal: {e}")
    
    def _execute_buy_signal(self, tsx_signal: Dict[str, Any], ctx: ExecContext):
        """Execute buy signal from TSX strategy"""
        try:
            # Close any existing short position first
            if ctx.short_pos():
                ctx.cover_shares = ctx.short_pos().shares
                logger.info(f"Covering short position: {ctx.short_pos().shares} shares")
            
            # Calculate position size (use TSX signal or default)
            shares_to_buy = tsx_signal.get('shares', 100)
            
            # Execute buy order
            if not ctx.long_pos():
                ctx.buy_shares = shares_to_buy
                
                # Set stop loss and take profit if provided by TSX strategy
                if 'stop_loss' in tsx_signal:
                    ctx.stop_loss = tsx_signal['stop_loss']
                if 'take_profit' in tsx_signal:
                    ctx.take_profit = tsx_signal['take_profit']
                
                logger.info(f"Executed BUY: {shares_to_buy} shares")
                self.trade_count += 1
                self.performance_stats['trades_executed'] += 1
                
        except Exception as e:
            logger.error(f"Error executing buy signal: {e}")
    
    def _execute_sell_signal(self, tsx_signal: Dict[str, Any], ctx: ExecContext):
        """Execute sell signal from TSX strategy"""
        try:
            # Close any existing long position first
            if ctx.long_pos():
                ctx.sell_shares = ctx.long_pos().shares
                logger.info(f"Closing long position: {ctx.long_pos().shares} shares")
            
            # Calculate short position size (use TSX signal or default)
            shares_to_short = tsx_signal.get('shares', 100)
            
            # Execute short order
            if not ctx.short_pos():
                ctx.sell_shares = shares_to_short
                
                # Set stop loss and take profit if provided by TSX strategy
                if 'stop_loss' in tsx_signal:
                    ctx.stop_loss = tsx_signal['stop_loss']
                if 'take_profit' in tsx_signal:
                    ctx.take_profit = tsx_signal['take_profit']
                
                logger.info(f"Executed SELL: {shares_to_short} shares")
                self.trade_count += 1
                self.performance_stats['trades_executed'] += 1
                
        except Exception as e:
            logger.error(f"Error executing sell signal: {e}")
    
    def _execute_close_signal(self, tsx_signal: Dict[str, Any], ctx: ExecContext):
        """Execute close/exit signal from TSX strategy"""
        try:
            # Close any open positions
            if ctx.long_pos():
                ctx.sell_shares = ctx.long_pos().shares
                logger.info(f"Closing long position: {ctx.long_pos().shares} shares")
                self.trade_count += 1
                self.performance_stats['trades_executed'] += 1
                
            elif ctx.short_pos():
                ctx.cover_shares = ctx.short_pos().shares
                logger.info(f"Covering short position: {ctx.short_pos().shares} shares")
                self.trade_count += 1
                self.performance_stats['trades_executed'] += 1
                
        except Exception as e:
            logger.error(f"Error executing close signal: {e}")
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get TSX strategy performance statistics"""
        stats = self.performance_stats.copy()
        stats['total_trades'] = self.trade_count
        stats['signals_generated'] = len(self.signals_generated)
        
        if self.bridge:
            bridge_stats = self.bridge.get_statistics()
            stats['bridge_stats'] = bridge_stats
        
        return stats
    
    def cleanup(self):
        """Cleanup Enhanced Bridge resources"""
        if self.bridge:
            self.bridge.shutdown()
            logger.info("Enhanced TSX Strategy Bridge shutdown complete")


def create_tsx_pybroker_strategy(tsx_strategy_path: str, csv_data_directory: str, symbol: str, 
                                start_date: str, end_date: str, config: Dict[str, Any] = None) -> Strategy:
    """
    Create a complete PyBroker Strategy using TSX Trading Bot V5 strategy
    
    Args:
        tsx_strategy_path: Path to TSX strategy JS file
        csv_data_directory: Path to monthly CSV data files  
        symbol: Trading symbol (MCL, MES, MGC, NG, SI)
        start_date: Backtest start date (YYYY-MM-DD)
        end_date: Backtest end date (YYYY-MM-DD)
        config: TSX strategy configuration
        
    Returns:
        Configured PyBroker Strategy ready for backtesting
    """
    
    logger.info(f"Creating TSX PyBroker Strategy for {symbol} from {start_date} to {end_date}")
    
    # Update config with symbol
    if config is None:
        config = {}
    config['symbol'] = symbol
    config['botId'] = f'pybroker_{symbol.lower()}_bot'
    
    # Create TSX Bridge Strategy wrapper
    tsx_wrapper = TSXBridgeStrategy(tsx_strategy_path, csv_data_directory, config)
    
    # Get PyBroker execution function
    tsx_execution_func = tsx_wrapper.create_pybroker_strategy_function()
    
    # Create CSV data source for PyBroker
    # Note: This will need to be implemented based on our CSV data format
    from claude_csv_data_loader import MonthlyCSVDataLoader
    csv_loader = MonthlyCSVDataLoader(csv_data_directory)
    
    # Load data for PyBroker
    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
    
    # BACKTESTER FIX: For same-day backtests, include the full day
    if start_date == end_date:
        end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        logger.info(f"Same-day backtest detected, extending end time to: {end_dt}")
    
    # Get historical data as DataFrame for PyBroker
    # Load more data to ensure we have full date range coverage
    historical_bars = csv_loader.get_historical_slice(symbol, end_dt, 5000)  # Load from end date backwards
    
    if not historical_bars:
        raise ValueError(f"No historical data found for {symbol} in range {start_date} to {end_date}")
    
    # Convert to PyBroker DataFrame format
    df_data = []
    for bar in historical_bars:
        if start_dt <= bar['datetime'] <= end_dt:
            df_data.append({
                'symbol': symbol,
                'date': bar['datetime'],
                'open': bar['open'],
                'high': bar['high'], 
                'low': bar['low'],
                'close': bar['close'],
                'volume': bar['volume']
            })
    
    if not df_data:
        raise ValueError(f"No data in specified date range for {symbol}")
    
    df = pd.DataFrame(df_data)
    df['date'] = pd.to_datetime(df['date'])
    # PyBroker expects 'date' column, not as index
    df = df.reset_index(drop=True)
    
    logger.info(f"Loaded {len(df)} bars for PyBroker backtesting")
    
    # Create PyBroker Strategy with CSV data
    strategy_config = StrategyConfig(
        initial_cash=100000,  # $100k starting capital
        max_long_positions=1,  # TSX strategies typically single position
        max_short_positions=1
    )
    
    strategy = Strategy(df, start_date, end_date, config=strategy_config)
    
    # Add TSX strategy execution to the symbol
    strategy.add_execution(tsx_execution_func, [symbol])
    
    # Store reference to wrapper for cleanup
    strategy._tsx_wrapper = tsx_wrapper
    
    logger.info(f"PyBroker Strategy created for TSX strategy: {Path(tsx_strategy_path).name}")
    
    return strategy


# Test function for Phase 3A verification
def test_phase3a_tsx_pybroker_strategy():
    """Test Phase 3A: PyBroker Strategy wrapper creation"""
    
    print("=" * 80)
    print("PHASE 3A: TSX PYBROKER STRATEGY WRAPPER TEST")
    print("=" * 80)
    
    try:
        # Configuration
        tsx_strategy = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\03-trading-bot\TSX-Trading-Bot-V5\src\strategies\ema\emaStrategy.js"
        csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
        
        config = {
            'symbol': 'MCL',
            'historicalBarsBack': 20
        }
        
        print(f"[STEP 1] Creating TSX PyBroker Strategy...")
        print(f"  TSX Strategy: emaStrategy.js")
        print(f"  Symbol: MCL") 
        print(f"  Date Range: 2023-06-01 to 2023-06-30")
        
        # Create PyBroker Strategy with TSX integration
        strategy = create_tsx_pybroker_strategy(
            tsx_strategy,
            csv_data_dir,
            'MCL',
            '2023-06-01',
            '2023-06-30',
            config
        )
        
        print(f"[STEP 2] Strategy created successfully")
        print(f"  Strategy type: {type(strategy)}")
        print(f"  Executions count: {len(strategy._executions)}")
        
        # Get performance stats from wrapper
        performance = strategy._tsx_wrapper.get_performance_stats()
        print(f"[STEP 3] TSX Bridge wrapper statistics:")
        for key, value in performance.items():
            print(f"  {key}: {value}")
        
        print(f"\n[SUCCESS] PHASE 3A: TSX PYBROKER STRATEGY WRAPPER CREATED")
        print(f"[OK] Enhanced Bridge integrated with PyBroker Strategy class")
        print(f"[OK] Real CSV data loaded for PyBroker backtesting")
        print(f"[OK] TSX strategy execution function ready")
        
        # Cleanup
        strategy._tsx_wrapper.cleanup()
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Phase 3A test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_phase3a_tsx_pybroker_strategy()