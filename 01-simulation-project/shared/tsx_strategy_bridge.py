"""
TSX Strategy Bridge for PyBroker
Enables TSX Trading Bot V5 strategies to run in PyBroker backtesting
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TSXStrategyBridge:
    """Bridge between TSX strategies (Node.js) and PyBroker (Python)"""
    
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
        
        # Redis client
        self.redis_client = redis.Redis(
            host=self.config['redisHost'],
            port=self.config['redisPort'],
            decode_responses=True
        )
        
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
        self.stdout_thread = None
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
            
            # Start stdout reader
            self._start_stdout_reader()
            
            self.running = True
            logger.info(f"TSX Strategy Bridge started for {self.strategy_path.name}")
            
        except Exception as e:
            logger.error(f"Failed to start bridge: {e}")
            self.shutdown()
            raise
    
    def _start_strategy_runner(self):
        """Start Node.js subprocess with strategy"""
        runner_path = Path(__file__).parent / 'strategy_runner_enhanced.js'
        
        cmd = [
            'node',
            str(runner_path),
            str(self.strategy_path),
            json.dumps(self.config)
        ]
        
        logger.info(f"Starting Node.js process: {' '.join(cmd[:3])}")
        
        self.node_process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for ready signal
        time.sleep(1)
    
    def _start_stdout_reader(self):
        """Start thread to read Node.js stdout"""
        def read_stdout():
            while self.running and self.node_process:
                try:
                    line = self.node_process.stdout.readline()
                    if not line:
                        break
                    
                    message = json.loads(line.strip())
                    self._handle_node_message(message)
                    
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from Node.js: {line}")
                except Exception as e:
                    logger.error(f"Error reading stdout: {e}")
        
        self.stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        self.stdout_thread.start()
    
    def _handle_node_message(self, message: Dict[str, Any]):
        """Handle messages from Node.js process"""
        msg_type = message.get('type')
        
        if msg_type == 'READY':
            logger.info(f"Strategy ready: {message}")
        elif msg_type == 'SIGNAL':
            self.latest_signal = message.get('data')
            self.signal_queue.put(self.latest_signal)
            logger.info(f"Received signal: {self.latest_signal}")
        elif msg_type == 'ERROR':
            logger.error(f"Strategy error: {message.get('error')}")
        elif msg_type == 'SHUTDOWN_COMPLETE':
            logger.info("Strategy shutdown complete")
        else:
            logger.debug(f"Node.js message: {message}")
    
    def _setup_redis_listeners(self):
        """Set up Redis pub/sub listeners"""
        def listen_for_signals():
            pubsub = self.redis_client.pubsub()
            
            # Subscribe to aggregator channels (where MockTradingBot forwards signals)
            channels = [
                'aggregator:signal',
                'aggregator:trade:request',
                'aggregator:historical-data:request'
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
                    logger.error(f"Redis listener error: {e}")
        
        self.listener_thread = threading.Thread(target=listen_for_signals, daemon=True)
        self.listener_thread.start()
    
    def _handle_redis_message(self, channel: str, data: str):
        """Handle Redis pub/sub messages"""
        try:
            message = json.loads(data)
            
            if channel == 'aggregator:signal':
                # Strategy sent a signal
                self.latest_signal = message
                self.signal_queue.put(message)
                logger.info(f"Signal from Redis: {message}")
                
            elif channel == 'aggregator:historical-data:request':
                # Strategy requesting historical data
                self._handle_historical_request(message)
                
        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")
    
    def _handle_historical_request(self, request: Dict[str, Any]):
        """Handle historical data requests from strategies"""
        try:
            bars_back = request.get('barsBack', 100)
            
            # Get historical data slice
            start_idx = max(0, self.current_bar_index - bars_back)
            historical_slice = self.market_data[start_idx:self.current_bar_index]
            
            # Format response
            response = {
                'requestId': request.get('requestId'),
                'symbol': request.get('symbol', self.config['symbol']),
                'timeframe': request.get('timeframe', '1m'),
                'data': historical_slice,
                'timestamp': time.time()
            }
            
            # Send to Node.js process
            self._send_to_node({
                'type': 'HISTORICAL_DATA',
                'data': response
            })
            
            # Also publish to Redis
            self.redis_client.publish(
                'aggregator:historical-data:response',
                json.dumps(response)
            )
            
            logger.info(f"Sent historical data: {len(historical_slice)} bars")
            
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
            
            # Send market data to strategy
            self._send_to_node({
                'type': 'MARKET_DATA',
                'data': bar_data
            })
            
            # Also publish to Redis (strategies may listen directly)
            self.redis_client.publish('bot:market-data', json.dumps({
                'botId': self.config['botId'],
                'symbol': self.config['symbol'],
                'price': bar_data['close'],
                'volume': bar_data['volume'],
                'timestamp': bar_data.get('timestamp', time.time()),
                **bar_data
            }))
            
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
            # Send to Node.js
            self._send_to_node({
                'type': 'POSITION_UPDATE',
                'data': {'positions': positions}
            })
            
            # Publish to Redis
            self.redis_client.publish(
                'aggregator:position:response',
                json.dumps({
                    'botId': self.config['botId'],
                    'positions': positions,
                    'timestamp': time.time()
                })
            )
            
            logger.debug(f"Updated positions: {len(positions)}")
            
        except Exception as e:
            logger.error(f"Error updating positions: {e}")
    
    def _send_to_node(self, message: Dict[str, Any]):
        """Send message to Node.js process"""
        if self.node_process and self.node_process.stdin:
            try:
                self.node_process.stdin.write(json.dumps(message) + '\n')
                self.node_process.stdin.flush()
            except Exception as e:
                logger.error(f"Error sending to Node.js: {e}")
    
    def get_latest_signal(self) -> Optional[Dict[str, Any]]:
        """Get the latest signal if available"""
        return self.latest_signal
    
    def shutdown(self):
        """Clean shutdown of bridge"""
        logger.info("Shutting down TSX Strategy Bridge...")
        
        self.running = False
        
        # Send shutdown to Node.js
        if self.node_process:
            self._send_to_node({'type': 'SHUTDOWN'})
            time.sleep(0.5)
            
            if self.node_process.poll() is None:
                self.node_process.terminate()
                time.sleep(0.5)
                
                if self.node_process.poll() is None:
                    self.node_process.kill()
        
        # Wait for threads
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
        if self.stdout_thread:
            self.stdout_thread.join(timeout=2)
        
        logger.info("TSX Strategy Bridge shutdown complete")


# Example usage for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python tsx_strategy_bridge.py <strategy_path>")
        sys.exit(1)
    
    strategy_path = sys.argv[1]
    
    # Create bridge
    bridge = TSXStrategyBridge(strategy_path)
    
    try:
        # Simulate some market data
        for i in range(10):
            bar = {
                'open': 100 + i,
                'high': 102 + i,
                'low': 99 + i,
                'close': 101 + i,
                'volume': 1000 + i * 10,
                'timestamp': time.time()
            }
            
            signal = bridge.process_bar(bar)
            if signal:
                print(f"Got signal: {signal}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        bridge.shutdown()