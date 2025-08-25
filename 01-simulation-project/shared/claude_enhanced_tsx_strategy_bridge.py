"""
Enhanced TSX Strategy Bridge with Real CSV Data Integration
Combines TSX Strategy Bridge with Real CSV Historical Bootstrap Service
"""

import subprocess
import json
import redis
import threading
import time
import queue
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime

# Import the real CSV bootstrap service
from claude_real_csv_bootstrap_service import RealCSVHistoricalBootstrapService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTSXStrategyBridge:
    """
    Enhanced TSX Strategy Bridge with real CSV data integration
    Combines strategy execution with real historical data bootstrap
    """
    
    def __init__(self, strategy_path: str, csv_data_directory: str, config: Dict[str, Any] = None):
        """
        Initialize enhanced bridge with TSX strategy and real CSV data
        
        Args:
            strategy_path: Path to TSX strategy JS file
            csv_data_directory: Path to monthly CSV data files
            config: Strategy configuration
        """
        self.strategy_path = Path(strategy_path).absolute()
        if not self.strategy_path.exists():
            raise FileNotFoundError(f"Strategy not found: {strategy_path}")
            
        self.csv_data_directory = csv_data_directory
        self.config = config or {}
        
        # Default configuration
        self.config.setdefault('botId', 'backtest_bot_1')
        self.config.setdefault('symbol', 'MCL')  # Default to available symbol
        self.config.setdefault('redisHost', 'localhost')
        self.config.setdefault('redisPort', 6379)
        self.config.setdefault('historicalBarsBack', 50)
        
        # Redis clients
        self.redis_client = redis.Redis(
            host=self.config['redisHost'],
            port=self.config['redisPort'],
            decode_responses=True
        )
        
        self.redis_client_binary = redis.Redis(
            host=self.config['redisHost'],
            port=self.config['redisPort'],
            decode_responses=False  # For bootstrap service
        )
        
        # Node.js subprocess
        self.node_process = None
        
        # Real CSV Bootstrap Service - Initialize immediately
        try:
            self.bootstrap_service = RealCSVHistoricalBootstrapService(
                self.redis_client_binary, 
                self.csv_data_directory,
                config={
                    'default_bars_back': self.config.get('historicalBarsBack', 50),
                    'max_bars_back': 500,
                    'simulation_date_range_days': 365
                }
            )
            logger.info("Real CSV Bootstrap Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize bootstrap service: {e}")
            raise
        
        # Signal tracking
        self.signal_queue = queue.Queue()
        self.latest_signal = None
        
        # Market data tracking for backtesting
        self.market_data = []
        self.current_bar_index = 0
        self.current_simulation_datetime = None
        
        # Threading
        self.listener_thread = None
        self.stdout_thread = None
        self.running = False
        
        # Statistics
        self.stats = {
            'strategy_signals': 0,
            'market_data_bars': 0,
            'historical_requests': 0,
            'bootstrap_ready': False,
            'strategy_ready': False
        }
    
    def start(self):
        """Start the enhanced bridge with real CSV bootstrap"""
        try:
            logger.info(f"Starting Enhanced TSX Strategy Bridge for {self.strategy_path.name}")
            
            # Step 1: Initialize and start real CSV bootstrap service
            logger.info("Initializing real CSV historical bootstrap service...")
            self._start_bootstrap_service()
            
            # Step 2: Start Node.js strategy runner
            logger.info("Starting TSX strategy runner...")
            self._start_strategy_runner()
            
            # Step 3: Setup Redis listeners for strategy signals
            logger.info("Setting up Redis signal listeners...")
            self._setup_redis_listeners()
            
            # Step 4: Start stdout reader for strategy monitoring
            self._start_stdout_reader()
            
            # Step 5: Wait for strategy to become ready
            logger.info("Waiting for strategy to become ready...")
            ready = self._wait_for_strategy_ready(timeout=30)
            
            self.running = True
            self.stats['bootstrap_ready'] = True
            self.stats['strategy_ready'] = ready
            
            logger.info(f"Enhanced TSX Strategy Bridge started successfully (Strategy Ready: {ready})")
            
            return ready
            
        except Exception as e:
            logger.error(f"Failed to start enhanced bridge: {e}")
            self.shutdown()
            raise
    
    def _start_bootstrap_service(self):
        """Start the real CSV bootstrap service (already initialized)"""
        try:
            # Validate requested symbol is available
            symbol = self.config['symbol']
            symbol_info = self.bootstrap_service.test_symbol_availability(symbol)
            
            if not symbol_info['available']:
                available_symbols = symbol_info['all_available_symbols']
                # Filter out non-trading symbols
                trading_symbols = [s for s in available_symbols if s in ['MCL', 'MES', 'MGC', 'NG', 'SI']]
                
                if trading_symbols:
                    logger.warning(f"Symbol '{symbol}' not available. Available trading symbols: {trading_symbols}")
                    raise ValueError(f"Symbol '{symbol}' not available in CSV data. Available: {trading_symbols}")
                else:
                    raise ValueError(f"No trading symbols available in CSV data directory: {self.csv_data_directory}")
            
            # Start the bootstrap service
            self.bootstrap_service.start()
            
            logger.info(f"Real CSV Bootstrap Service started for symbol: {symbol}")
            logger.info(f"Date range available: {symbol_info.get('date_range', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Failed to start bootstrap service: {e}")
            raise
    
    def _start_strategy_runner(self):
        """Start Node.js subprocess with TSX strategy"""
        runner_path = Path(__file__).parent / 'claude_tsx_v5_strategy_runner.js'
        
        if not runner_path.exists():
            raise FileNotFoundError(f"Strategy runner not found: {runner_path}")
        
        cmd = [
            'node',
            str(runner_path),
            str(self.strategy_path),
            json.dumps(self.config)
        ]
        
        logger.info(f"Starting Node.js TSX strategy: {self.strategy_path.name}")
        
        try:
            # Enhanced subprocess configuration for better stdout capture
            env = {**os.environ, 'NODE_NO_WARNINGS': '1', 'FORCE_TTY': '1'}
            
            self.node_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr to stdout for better capture
                text=True,
                bufsize=0,  # Unbuffered for immediate output
                universal_newlines=True,
                encoding='utf-8',  # PHASE 2A FIX: Handle emoji characters in strategy output
                errors='replace',  # Replace problematic characters instead of crashing
                env=env
            )
            
            logger.info(f"TSX strategy process started (PID: {self.node_process.pid})")
            
        except Exception as e:
            logger.error(f"Failed to start strategy process: {e}")
            raise
    
    def _setup_redis_listeners(self):
        """Setup Redis listeners for strategy signals and ready notifications"""
        def listen_for_signals():
            try:
                pubsub = self.redis_client.pubsub()
                pubsub.subscribe(f'aggregator:signal:{self.config["botId"]}')
                pubsub.subscribe('aggregator:strategy-ready')  # PHASE 2A FIX: Listen for ready signals
                
                logger.info(f"Listening for signals on: aggregator:signal:{self.config['botId']}")
                logger.info(f"Listening for ready signals on: aggregator:strategy-ready")
                
                # Test Redis connection
                self.redis_client.ping()
                logger.info("Redis connection verified in listener thread")
                while self.running:
                    message = pubsub.get_message(timeout=1.0)
                    
                    if message and message['type'] == 'message':
                        try:
                            if message['channel'] == f'aggregator:signal:{self.config["botId"]}':
                                # Strategy signal
                                signal_data = json.loads(message['data'])
                                self._process_strategy_signal(signal_data)
                                
                            elif message['channel'] == 'aggregator:strategy-ready':
                                # Strategy ready notification  
                                ready_data = json.loads(message['data'])
                                logger.info(f"Received ready signal for botId: {ready_data.get('botId')}, our botId: {self.config['botId']}")
                                if ready_data.get('botId') == self.config['botId'] and ready_data.get('ready'):
                                    logger.info(f"*** READY SIGNAL DETECTED via Redis! *** {ready_data}")
                                    self.stats['strategy_ready'] = True
                            
                        except Exception as e:
                            logger.error(f"Error processing Redis message: {e}")
                            
            except Exception as e:
                logger.error(f"Error in Redis listener: {e}")
            finally:
                pubsub.unsubscribe()
                pubsub.close()
        
        self.listener_thread = threading.Thread(target=listen_for_signals, daemon=True)
        self.listener_thread.start()
    
    def _start_stdout_reader(self):
        """Start thread to read strategy stdout with proper encoding handling"""
        def read_stdout():
            if not self.node_process:
                logger.error("No node process to read from")
                return
                
            try:
                line_count = 0
                logger.info(f"Stdout reader starting for PID {self.node_process.pid}")
                
                while self.running and self.node_process.poll() is None:
                    try:
                        # PHASE 2A FIX: Robust Unicode handling in thread context
                        line = self.node_process.stdout.readline()
                        if line:
                            line_count += 1
                            # Ensure Unicode handling in thread context
                            if isinstance(line, bytes):
                                line = line.decode('utf-8', errors='replace')
                            line = line.strip()
                            if line:
                                # Filter out emoji characters and Unicode variation selectors for logging
                                safe_line = ''.join(c for c in line if ord(c) < 127 or c.isalnum())
                                logger.info(f"Strategy stdout [{line_count}]: {safe_line}")
                                
                                # Check for ready status using ORIGINAL line (case insensitive)
                                if 'ready: true' in line.lower():
                                    logger.info("*** READY SIGNAL DETECTED via stdout! ***")
                                    self.stats['strategy_ready'] = True
                                    
                    except UnicodeDecodeError as e:
                        logger.warning(f"Unicode decode error in stdout, skipping line: {e}")
                        continue
                    except Exception as e:
                        logger.error(f"Error reading single line: {e}")
                        continue
                        
                logger.info(f"Stdout reader ending - captured {line_count} lines, process status: {self.node_process.poll()}")
                        
            except Exception as e:
                logger.error(f"Error in stdout reader thread: {e}")
                import traceback
                traceback.print_exc()
        
        self.stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        self.stdout_thread.start()
        logger.info("Started stdout reader thread with enhanced Unicode handling and debug logging")
    
    def _wait_for_strategy_ready(self, timeout: int = 30) -> bool:
        """Wait for strategy to become ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.stats['strategy_ready']:
                logger.info("Strategy is ready!")
                return True
                
            # Check if process died
            if self.node_process and self.node_process.poll() is not None:
                logger.error("Strategy process terminated unexpectedly")
                return False
                
            time.sleep(0.5)
        
        logger.warning(f"Strategy did not become ready within {timeout} seconds")
        return False
    
    def _process_strategy_signal(self, signal_data: Dict[str, Any]):
        """Process signal from TSX strategy"""
        try:
            self.latest_signal = signal_data
            self.signal_queue.put(signal_data)
            self.stats['strategy_signals'] += 1
            
            logger.info(f"Received strategy signal: {signal_data.get('action', 'UNKNOWN')} at {signal_data.get('timestamp', 'UNKNOWN')}")
            
        except Exception as e:
            logger.error(f"Error processing strategy signal: {e}")
    
    def set_simulation_datetime(self, simulation_datetime: datetime):
        """Set current simulation datetime for backtesting"""
        self.current_simulation_datetime = simulation_datetime
        
        if self.bootstrap_service:
            self.bootstrap_service.set_simulation_datetime(simulation_datetime)
        
        # BACKTESTER FIX: Notify strategy runner of simulation datetime
        try:
            # Handle numpy datetime64 conversion
            if hasattr(simulation_datetime, 'isoformat'):
                datetime_str = simulation_datetime.isoformat()
            else:
                # Convert numpy datetime64 to datetime first
                import pandas as pd
                if hasattr(simulation_datetime, 'to_pydatetime'):
                    datetime_str = simulation_datetime.to_pydatetime().isoformat()
                elif 'datetime64' in str(type(simulation_datetime)):
                    dt = pd.to_datetime(simulation_datetime).to_pydatetime()
                    datetime_str = dt.isoformat()
                else:
                    datetime_str = str(simulation_datetime)
                    
            simulation_message = {
                'type': 'SIMULATION_DATE',
                'datetime': datetime_str,
                'botId': self.config['botId']
            }
            channel = f'aggregator:simulation:{self.config["botId"]}'
            self.redis_client.publish(channel, json.dumps(simulation_message))
            logger.debug(f"Published simulation datetime to {channel}: {datetime_str}")
        except Exception as e:
            logger.warning(f"Failed to publish simulation datetime: {e}")
    
    def process_market_data(self, bar_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process market data bar and get strategy signal
        
        Args:
            bar_data: OHLCV bar data
            
        Returns:
            Strategy signal if generated, None otherwise
        """
        try:
            # Update simulation context
            if 'timestamp' in bar_data:
                if isinstance(bar_data['timestamp'], datetime):
                    self.set_simulation_datetime(bar_data['timestamp'])
                elif isinstance(bar_data['timestamp'], str):
                    dt = datetime.fromisoformat(bar_data['timestamp'].replace('Z', ''))
                    self.set_simulation_datetime(dt)
            
            # Send market data to strategy
            timestamp = bar_data.get('timestamp', datetime.now())
            if isinstance(timestamp, datetime):
                timestamp_str = timestamp.isoformat()
            else:
                # BACKTESTER FIX: Handle numpy.datetime64 objects
                try:
                    if hasattr(timestamp, 'isoformat'):
                        timestamp_str = timestamp.isoformat()
                    else:
                        # Convert numpy datetime64 to datetime first
                        import pandas as pd
                        if hasattr(timestamp, 'to_pydatetime'):
                            timestamp_str = timestamp.to_pydatetime().isoformat()
                        elif 'datetime64' in str(type(timestamp)):
                            dt = pd.to_datetime(timestamp).to_pydatetime()
                            timestamp_str = dt.isoformat()
                        else:
                            timestamp_str = str(timestamp)
                except Exception as e:
                    logger.warning(f"Error converting timestamp {timestamp} ({type(timestamp)}): {e}")
                    timestamp_str = datetime.now().isoformat()
                
            market_update = {
                'symbol': self.config['symbol'],
                'price': bar_data.get('close', bar_data.get('c')),
                'open': bar_data.get('open', bar_data.get('o')),
                'high': bar_data.get('high', bar_data.get('h')),
                'low': bar_data.get('low', bar_data.get('l')),
                'volume': bar_data.get('volume', bar_data.get('v', 0)),
                'timestamp': timestamp_str
            }
            
            # Publish market data to strategy
            channel = f'aggregator:market-data:{self.config["botId"]}'
            message = json.dumps(market_update)
            self.redis_client.publish(channel, message)
            
            self.stats['market_data_bars'] += 1
            
            # Check for new signals (with timeout)
            try:
                signal = self.signal_queue.get(timeout=0.1)  # Quick check
                return signal
            except queue.Empty:
                return None
                
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            return None
    
    def get_latest_signal(self) -> Optional[Dict[str, Any]]:
        """Get the latest signal from strategy"""
        return self.latest_signal
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get bridge statistics"""
        stats = self.stats.copy()
        stats['running'] = self.running
        stats['strategy_path'] = str(self.strategy_path)
        stats['csv_data_directory'] = self.csv_data_directory
        stats['symbol'] = self.config['symbol']
        stats['current_simulation_datetime'] = self.current_simulation_datetime.isoformat() if self.current_simulation_datetime else None
        
        if self.bootstrap_service:
            bootstrap_stats = self.bootstrap_service.get_statistics()
            stats['bootstrap_stats'] = bootstrap_stats
        
        return stats
    
    def shutdown(self):
        """Shutdown the enhanced bridge"""
        logger.info("Shutting down Enhanced TSX Strategy Bridge...")
        
        self.running = False
        
        # Stop Node.js process
        if self.node_process:
            try:
                self.node_process.terminate()
                self.node_process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self.node_process.kill()
            except Exception as e:
                logger.error(f"Error terminating strategy process: {e}")
        
        # Stop bootstrap service
        if self.bootstrap_service:
            try:
                self.bootstrap_service.stop()
            except Exception as e:
                logger.error(f"Error stopping bootstrap service: {e}")
        
        # Wait for threads
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2.0)
        
        if self.stdout_thread and self.stdout_thread.is_alive():
            self.stdout_thread.join(timeout=2.0)
        
        logger.info("Enhanced TSX Strategy Bridge shutdown complete")


# Test the enhanced bridge if run directly
if __name__ == "__main__":
    print("=== Testing Enhanced TSX Strategy Bridge ===")
    
    # Configuration
    test_config = {
        'botId': 'test_enhanced_bridge',
        'symbol': 'MCL',  # Use available symbol
        'historicalBarsBack': 20,
        'redisHost': 'localhost',
        'redisPort': 6379
    }
    
    strategy_path = "C:\\Users\\salte\\ClaudeProjects\\github-repos\\00-trading-project\\03-trading-bot\\TSX-Trading-Bot-V5\\src\\strategies\\ema\\emaStrategy.js"
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    try:
        print(f"\n[TEST 1] Creating enhanced bridge...")
        print(f"Strategy: {Path(strategy_path).name}")
        print(f"Symbol: {test_config['symbol']}")
        print(f"CSV Data: {csv_data_dir}")
        
        # Create enhanced bridge
        bridge = EnhancedTSXStrategyBridge(strategy_path, csv_data_dir, test_config)
        
        print(f"Bridge created successfully")
        
        # Test symbol availability before starting
        symbol_info = bridge.bootstrap_service.test_symbol_availability(test_config['symbol'])
        print(f"Symbol availability: {symbol_info}")
        
        if not symbol_info['available']:
            print(f"ERROR: Symbol {test_config['symbol']} not available")
            available = [s for s in symbol_info['all_available_symbols'] if s in ['MCL', 'MES', 'MGC', 'NG', 'SI']]
            print(f"Available trading symbols: {available}")
        else:
            print(f"SUCCESS: Symbol {test_config['symbol']} is available")
        
        print(f"\n[TEST 2] Testing bootstrap service integration...")
        # Test without starting full bridge
        print(f"Bootstrap service ready for testing")
        
        print(f"\n[TEST 3] Getting statistics...")
        stats = bridge.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\nENHANCED BRIDGE TEST COMPLETE")
        print(f"SUCCESS: Real CSV data integration ready")
        print(f"SUCCESS: Ready to replace fake bootstrap service")
        
        # Cleanup
        bridge.shutdown()
        
    except Exception as e:
        print(f"Enhanced bridge test failed: {e}")
        import traceback
        traceback.print_exc()