"""
Historical Data Bootstrap Service for TSX Strategy Bridge
CRITICAL COMPONENT: Provides historical data for strategy bootstrap

Without this service, TSX strategies remain in "not ready" state forever.
This service mimics TSX V5 historical data format via Redis pub/sub.
"""

import json
import redis
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class HistoricalDataBootstrapService:
    """
    Provides historical data bootstrap for TSX strategies
    Listens to aggregator:historical-data:request and responds with data
    """
    
    def __init__(self, redis_client: redis.Redis, config: Dict[str, Any] = None):
        """
        Initialize bootstrap service
        
        Args:
            redis_client: Redis client for pub/sub
            config: Configuration for data generation
        """
        self.redis_client = redis_client
        self.config = config or {}
        
        # Default configuration
        self.config.setdefault('base_price_nq', 15000)
        self.config.setdefault('price_volatility', 5.0)
        self.config.setdefault('volume_base', 800)
        self.config.setdefault('volume_range', 200)
        
        # Pub/sub setup
        self.pubsub = None
        self.listener_thread = None
        self.running = False
        
        # Statistics
        self.stats = {
            'requests_received': 0,
            'requests_processed': 0,
            'requests_failed': 0,
            'bars_generated': 0
        }
        
        logger.info("Historical Data Bootstrap Service initialized")
        
    def start(self):
        """Start the bootstrap service listener"""
        try:
            logger.info("Starting Historical Data Bootstrap Service...")
            
            # Create pubsub connection
            self.pubsub = self.redis_client.pubsub()
            
            # Subscribe to historical data requests
            self.pubsub.subscribe('aggregator:historical-data:request')
            logger.info("Subscribed to aggregator:historical-data:request")
            
            # Start listener thread
            self.running = True
            self.listener_thread = threading.Thread(
                target=self._listen_for_requests,
                daemon=True
            )
            self.listener_thread.start()
            
            logger.info("Historical Data Bootstrap Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start bootstrap service: {e}")
            return False
    
    def _listen_for_requests(self):
        """Listen for historical data requests and respond"""
        logger.info("Bootstrap service listener thread started")
        
        try:
            for message in self.pubsub.listen():
                if not self.running:
                    break
                    
                if message['type'] == 'message':
                    try:
                        request_data = json.loads(message['data'])
                        self._handle_historical_request(request_data)
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON in historical data request: {e}")
                        self.stats['requests_failed'] += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing historical data request: {e}")
                        self.stats['requests_failed'] += 1
                        
        except Exception as e:
            logger.error(f"Bootstrap service listener error: {e}")
        finally:
            logger.info("Bootstrap service listener thread ended")
    
    def _handle_historical_request(self, request: Dict[str, Any]):
        """Handle incoming historical data request"""
        self.stats['requests_received'] += 1
        
        request_id = request.get('requestId')
        symbol = request.get('symbol', 'NQ')
        bars_back = request.get('barsBack', 50)
        interval = request.get('interval', 1)
        interval_type = request.get('intervalType', 'min')
        
        logger.info(f"📊 [BOOTSTRAP] Processing request {request_id}")
        logger.info(f"   Symbol: {symbol}, Bars: {bars_back}, Interval: {interval}{interval_type}")
        
        try:
            # Generate historical data
            bars = self._generate_historical_bars(
                symbol=symbol,
                bars_back=bars_back,
                interval=interval,
                interval_type=interval_type
            )
            
            # Create response in exact TSX V5 format
            response = {
                'requestId': request_id,
                'success': True,
                'data': {
                    'bars': bars
                },
                'timestamp': datetime.now().isoformat() + 'Z'
            }
            
            # Publish response
            self.redis_client.publish(
                'aggregator:historical-data:response',
                json.dumps(response)
            )
            
            self.stats['requests_processed'] += 1
            self.stats['bars_generated'] += len(bars)
            
            logger.info(f"[BOOTSTRAP] Sent {len(bars)} bars for {symbol} (request: {request_id})")
            
        except Exception as e:
            logger.error(f"[BOOTSTRAP] Failed to process request {request_id}: {e}")
            
            # Send error response
            error_response = {
                'requestId': request_id,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat() + 'Z'
            }
            
            try:
                self.redis_client.publish(
                    'aggregator:historical-data:response',
                    json.dumps(error_response)
                )
            except Exception as publish_error:
                logger.error(f"Failed to send error response: {publish_error}")
            
            self.stats['requests_failed'] += 1
    
    def _generate_historical_bars(self, symbol: str, bars_back: int, interval: int, interval_type: str) -> List[Dict[str, Any]]:
        """
        Generate realistic historical OHLCV data for bootstrap
        Format matches exact TSX V5 bar format
        """
        bars = []
        
        # Calculate interval in seconds
        interval_seconds = self._get_interval_seconds(interval, interval_type)
        
        # Generate bars going backwards from current time
        current_time = datetime.now()
        base_price = self.config['base_price_nq']
        
        for i in range(bars_back):
            # Calculate timestamp for this bar (going backwards)
            bar_time = current_time - timedelta(seconds=interval_seconds * (bars_back - i))
            
            # Generate realistic price movement
            # Create slight trend with random volatility
            trend_factor = i * 0.1  # Slight upward trend
            volatility = (i % 7 - 3) * self.config['price_volatility']  # Oscillating movement
            noise = (time.time() * 1000 % 100 - 50) * 0.02  # Small random component
            
            center_price = base_price + trend_factor + volatility + noise
            
            # Generate OHLC with realistic relationships
            open_price = center_price + ((i % 3 - 1) * 1.25)
            close_price = center_price + ((i % 5 - 2) * 1.0)
            high_price = max(open_price, close_price) + abs((i % 4) * 0.75)
            low_price = min(open_price, close_price) - abs((i % 3) * 0.75)
            
            # Generate volume
            volume = self.config['volume_base'] + (i % self.config['volume_range'])
            
            # Create bar in exact TSX V5 format
            bar = {
                't': bar_time.isoformat() + 'Z',  # ISO format with Z suffix
                'o': round(open_price, 2),
                'h': round(high_price, 2),
                'l': round(low_price, 2),
                'c': round(close_price, 2),
                'v': volume
            }
            
            bars.append(bar)
        
        # Sort by timestamp (oldest first)
        bars.sort(key=lambda x: x['t'])
        
        logger.info(f"Generated {len(bars)} bars for {symbol}")
        logger.info(f"Time range: {bars[0]['t']} to {bars[-1]['t']}")
        logger.info(f"Price range: {min(bar['l'] for bar in bars):.2f} - {max(bar['h'] for bar in bars):.2f}")
        
        return bars
    
    def _get_interval_seconds(self, interval: int, interval_type: str) -> int:
        """Convert interval to seconds"""
        multipliers = {
            'sec': 1,
            'second': 1,
            'min': 60,
            'minute': 60,
            'hour': 3600,
            'day': 86400
        }
        
        multiplier = multipliers.get(interval_type.lower(), 60)  # Default to minutes
        return interval * multiplier
    
    def stop(self):
        """Stop the bootstrap service"""
        logger.info("Stopping Historical Data Bootstrap Service...")
        
        self.running = False
        
        if self.pubsub:
            try:
                self.pubsub.unsubscribe('aggregator:historical-data:request')
                self.pubsub.close()
            except Exception as e:
                logger.error(f"Error closing pubsub: {e}")
        
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=2.0)
        
        logger.info("Historical Data Bootstrap Service stopped")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            **self.stats,
            'running': self.running,
            'thread_alive': self.listener_thread.is_alive() if self.listener_thread else False
        }
    
    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# Test the service if run directly
if __name__ == "__main__":
    print("=== Testing Historical Data Bootstrap Service ===")
    
    # Create Redis client
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Test Redis connection
    try:
        redis_client.ping()
        print("Redis connection successful")
    except Exception as e:
        print(f"Redis connection failed: {e}")
        exit(1)
    
    # Create and start service
    service = HistoricalDataBootstrapService(redis_client)
    
    print("Starting bootstrap service...")
    if service.start():
        print("Service started successfully")
        
        # Keep service running for testing
        try:
            time.sleep(5)
            stats = service.get_statistics()
            print(f"Service stats: {stats}")
        except KeyboardInterrupt:
            print("Interrupted by user")
        finally:
            service.stop()
    else:
        print("Failed to start service")
        exit(1)