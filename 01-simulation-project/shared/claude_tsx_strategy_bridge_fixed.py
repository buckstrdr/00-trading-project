"""
TSX Strategy Bridge for PyBroker - FIXED for Windows
Uses Redis for all communication instead of stdin/stdout
"""

import subprocess
import json
import redis
import threading
import time
import queue
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TSXStrategyBridgeFixed:
    """Bridge between TSX strategies (Node.js) and PyBroker (Python) - Windows Fixed"""
    
    def __init__(self, strategy_path: str, config: Dict[str, Any] = None):
        """
        Initialize bridge with TSX strategy
        
        Args:
            strategy_path: Path to TSX strategy JS file
            config: Strategy configuration
        """
        self.strategy_path = Path(strategy_path).absolute()
        if not self.strategy_path.exists():
            raise FileNotFoundError(f"Strategy not found: {strategy_path}")
            
        self.config = config or {}
        self.config.setdefault('botId', 'backtest_bot_1')
        self.config.setdefault('symbol', 'NQ')
        self.config.setdefault('redisHost', 'localhost')
        self.config.setdefault('redisPort', 6379)
        
        # Redis clients - one for pub, one for sub
        self.redis_pub = redis.Redis(
            host=self.config['redisHost'],
            port=self.config['redisPort'],
            decode_responses=True
        )
        
        self.redis_sub = redis.Redis(
            host=self.config['redisHost'],
            port=self.config['redisPort'],
            decode_responses=True
        )
        
        # Test Redis connection
        try:
            self.redis_pub.ping()
            logger.info("Redis connection successful")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise
        
        # Node.js subprocess
        self.node_process = None
        
        # Signal tracking
        self.signal_queue = queue.Queue()
        self.latest_signal = None
        
        # Historical data tracking
        self.market_data = []
        self.current_bar_index = 0
        
        # Threading
        self.listener_thread = None
        self.running = False
        
        # Start the bridge
        self._start()
    
    def _start(self):
        """Start Node.js strategy runner and Redis listeners"""
        try:
            # Start strategy runner subprocess
            self._start_strategy_runner()
            
            # Start Redis listeners
            self._setup_redis_listeners()
            
            self.running = True
            logger.info(f"TSX Strategy Bridge started for {self.strategy_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to start bridge: {e}")
            self.shutdown()
            raise
    
    def _start_strategy_runner(self):
        """Start Node.js subprocess with strategy - Windows compatible"""
        runner_path = Path(__file__).parent / 'strategy_runner_enhanced.js'
        
        # Check if runner exists, if not use the basic one
        if not runner_path.exists():
            runner_path = Path(__file__).parent / 'strategy_runner.js'
        
        if not runner_path.exists():
            raise FileNotFoundError(f"Strategy runner not found at {runner_path}")
        
        # Build command - use shell=True on Windows for better compatibility
        cmd = [
            'node',
            str(runner_path),
            str(self.strategy_path),
            json.dumps(self.config)
        ]
        
        logger.info(f"Starting Node.js process: {' '.join(cmd[:3])}")
        
        # Use different approach for Windows
        if sys.platform == 'win32':
            # On Windows, avoid stdin/stdout issues by using shell
            self.node_process = subprocess.Popen(
                cmd,
                shell=False,  # Don't use shell to avoid security issues
                stdout=subprocess.DEVNULL,  # Ignore stdout
                stderr=subprocess.PIPE,  # Capture errors
                stdin=subprocess.DEVNULL,  # Don't use stdin
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
            )
        else:
            self.node_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        
        # Give it time to start
        time.sleep(2)
        
        # Check if process started successfully
        if self.node_process.poll() is not None:
            stderr = self.node_process.stderr.read() if self.node_process.stderr else "Unknown error"
            raise RuntimeError(f"Node.js process failed to start: {stderr}")
        
        logger.info(f"Node.js process started with PID: {self.node_process.pid}")
    
    def _setup_redis_listeners(self):
        """Set up Redis pub/sub listeners"""
        def listen_for_signals():
            pubsub = self.redis_sub.pubsub()
            
            # Subscribe to aggregator channels (where MockTradingBot forwards signals)
            channels = [
                'aggregator:signal',
                'aggregator:trade:request',
                'aggregator:historical-data:request',
                'bridge:signal',  # Direct channel for strategy signals
                'bridge:ready'    # Ready signal from strategy
            ]
            
            for channel in channels:
                pubsub.subscribe(channel)
                logger.info(f"Subscribed to {channel}")
            
            while self.running:
                try:
                    message = pubsub.get_message(timeout=1.0)
                    if message and message['type'] == 'message':
                        self._handle_redis_message(message['channel'], message['data'])
                except Exception as e:
                    if self.running:  # Only log if we're not shutting down
                        logger.error(f"Redis listener error: {e}")
            
            pubsub.close()
        
        self.listener_thread = threading.Thread(target=listen_for_signals, daemon=True)
        self.listener_thread.start()
    
    def _handle_redis_message(self, channel: str, data: str):
        """Handle Redis pub/sub messages"""
        try:
            # Parse message
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            message = json.loads(data) if data else {}
            
            if channel in ['aggregator:signal', 'bridge:signal']:
                # Strategy sent a signal
                self.latest_signal = message
                self.signal_queue.put(message)
                logger.info(f"Signal received from {channel}: {message}")
                
            elif channel == 'aggregator:historical-data:request':
                # Strategy requesting historical data
                self._handle_historical_request(message)
            
            elif channel == 'bridge:ready':
                logger.info(f"Strategy ready: {message}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON on {channel}: {data[:100]}")
        except Exception as e:
            logger.error(f"Error handling Redis message on {channel}: {e}")
    
    def _handle_historical_request(self, request: Dict[str, Any]):
        """Handle historical data requests from strategies"""
        try:
            bars_back = request.get('barsBack', 100)
            request_id = request.get('requestId', 'unknown')
            
            # Get historical data slice
            start_idx = max(0, self.current_bar_index - bars_back)
            historical_slice = self.market_data[start_idx:self.current_bar_index]
            
            # Format response
            response = {
                'requestId': request_id,
                'botId': self.config['botId'],
                'symbol': request.get('symbol', self.config['symbol']),
                'timeframe': request.get('timeframe', '1m'),
                'data': historical_slice,
                'timestamp': time.time()
            }
            
            # Send response via Redis
            self.redis_pub.publish(
                'aggregator:historical-data:response',
                json.dumps(response)
            )
            
            logger.info(f"Sent historical data: {len(historical_slice)} bars for request {request_id}")
            
        except Exception as e:
            logger.error(f"Error handling historical request: {e}")
    
    def process_bar(self, bar_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a market data bar and get signal
        
        Args:
            bar_data: Dict with open, high, low, close, volume, timestamp
            
        Returns:
            Signal dict or None
        """
        try:
            # Store for historical requests
            self.market_data.append(bar_data)
            self.current_bar_index = len(self.market_data)
            
            # Send market data via Redis (not stdin)
            market_message = {
                'botId': self.config['botId'],
                'symbol': self.config['symbol'],
                'price': bar_data.get('close', 0),
                'volume': bar_data.get('volume', 0),
                'timestamp': bar_data.get('timestamp', time.time()),
                'open': bar_data.get('open', 0),
                'high': bar_data.get('high', 0),
                'low': bar_data.get('low', 0),
                'close': bar_data.get('close', 0)
            }
            
            # Publish to bot channel (strategies listen here)
            self.redis_pub.publish('bot:market-data', json.dumps(market_message))
            
            # Also publish to bridge channel for direct communication
            self.redis_pub.publish('bridge:market-data', json.dumps(market_message))
            
            logger.debug(f"Sent market data: close={bar_data.get('close')}, volume={bar_data.get('volume')}")
            
            # Wait briefly for signal (non-blocking check)
            try:
                signal = self.signal_queue.get(timeout=0.1)
                return signal
            except queue.Empty:
                return None
                
        except Exception as e:
            logger.error(f"Error processing bar: {e}")
            return None
    
    def update_positions(self, positions: List[Dict[str, Any]]):
        """
        Update position state from PyBroker
        
        Args:
            positions: List of position dicts
        """
        try:
            position_message = {
                'botId': self.config['botId'],
                'positions': positions,
                'timestamp': time.time()
            }
            
            # Publish to Redis channels
            self.redis_pub.publish('aggregator:position:response', json.dumps(position_message))
            self.redis_pub.publish('bridge:positions', json.dumps(position_message))
            
            logger.debug(f"Updated positions: {len(positions)} position(s)")
            
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def get_latest_signal(self) -> Optional[Dict[str, Any]]:
        """Get the latest signal if available"""
        return self.latest_signal
    
    def shutdown(self):
        """Clean shutdown of bridge"""
        logger.info("Shutting down TSX Strategy Bridge...")
        
        self.running = False
        
        # Send shutdown signal via Redis
        try:
            self.redis_pub.publish('bridge:shutdown', json.dumps({
                'botId': self.config['botId'],
                'timestamp': time.time()
            }))
        except:
            pass
        
        # Wait for listener thread
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2)
        
        # Terminate Node.js process
        if self.node_process:
            try:
                if sys.platform == 'win32':
                    # Windows-specific termination
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.node_process.pid)], 
                                 capture_output=True, timeout=5)
                else:
                    self.node_process.terminate()
                    self.node_process.wait(timeout=5)
            except Exception as e:
                logger.error(f"Error terminating Node.js process: {e}")
                try:
                    self.node_process.kill()
                except:
                    pass
        
        logger.info("TSX Strategy Bridge shutdown complete")


# Alias for compatibility
TSXStrategyBridge = TSXStrategyBridgeFixed