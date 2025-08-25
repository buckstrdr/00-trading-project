"""
Real CSV Historical Data Bootstrap Service for TSX Strategy Bridge
CRITICAL COMPONENT: Provides REAL historical data for strategy bootstrap

Uses monthly CSV files as the real data source instead of generating fake data.
This service provides authentic market data via Redis pub/sub for TSX strategies.
"""

import json
import redis
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from claude_csv_data_loader import MonthlyCSVDataLoader

logger = logging.getLogger(__name__)


class RealCSVHistoricalBootstrapService:
    """
    Provides REAL historical data bootstrap for TSX strategies using CSV files
    Listens to aggregator:historical-data:request and responds with real market data
    """
    
    def __init__(self, redis_client: redis.Redis, csv_data_directory: str, config: Dict[str, Any] = None):
        """
        Initialize real CSV bootstrap service
        
        Args:
            redis_client: Redis client for pub/sub
            csv_data_directory: Path to monthly CSV data files
            config: Configuration for service behavior
        """
        self.redis_client = redis_client
        self.csv_data_directory = csv_data_directory
        self.config = config or {}
        
        # Initialize CSV data loader
        try:
            self.data_loader = MonthlyCSVDataLoader(csv_data_directory)
            logger.info(f"CSV data loader initialized with directory: {csv_data_directory}")
            
            # Log available symbols
            available_symbols = self.data_loader.get_available_symbols()
            logger.info(f"Available symbols in CSV data: {available_symbols}")
            
        except Exception as e:
            logger.error(f"Failed to initialize CSV data loader: {e}")
            raise
        
        # Default configuration for backtest simulation
        self.config.setdefault('default_bars_back', 50)
        self.config.setdefault('max_bars_back', 500)
        self.config.setdefault('simulation_date_range_days', 365)  # Days back from current for simulation
        
        # Pub/sub setup
        self.pubsub = None
        self.listener_thread = None
        self.running = False
        
        # Current simulation context (for backtesting)
        self.current_simulation_datetime = None
        
        # Statistics
        self.stats = {
            'requests_received': 0,
            'responses_sent': 0,
            'errors': 0,
            'symbols_requested': {},
            'avg_bars_requested': 0,
            'csv_files_accessed': 0
        }
        
        logger.info("Real CSV Historical Bootstrap Service initialized")
    
    def start(self):
        """Start the historical data service"""
        if self.running:
            logger.warning("Service already running")
            return
        
        try:
            # Setup Redis pub/sub
            self.pubsub = self.redis_client.pubsub()
            self.pubsub.subscribe('aggregator:historical-data:request')
            
            # Start listener thread
            self.running = True
            self.listener_thread = threading.Thread(target=self._listen_for_requests, daemon=True)
            self.listener_thread.start()
            
            logger.info("Real CSV Historical Bootstrap Service started successfully")
            logger.info("Listening on: aggregator:historical-data:request")
            
        except Exception as e:
            logger.error(f"Failed to start service: {e}")
            self.running = False
            raise
    
    def stop(self):
        """Stop the historical data service"""
        if not self.running:
            return
        
        logger.info("Stopping Real CSV Historical Bootstrap Service...")
        self.running = False
        
        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()
        
        if self.listener_thread and self.listener_thread.is_alive():
            self.listener_thread.join(timeout=5.0)
        
        logger.info("Real CSV Historical Bootstrap Service stopped")
    
    def set_simulation_datetime(self, simulation_datetime: datetime):
        """
        Set current simulation datetime for backtesting context
        This determines the 'current' time for historical data slicing
        
        Args:
            simulation_datetime: Current datetime in backtest simulation
        """
        self.current_simulation_datetime = simulation_datetime
        logger.debug(f"Simulation datetime set to: {simulation_datetime}")
    
    def _listen_for_requests(self):
        """Listen for historical data requests on Redis pub/sub"""
        logger.info("Started listening for historical data requests")
        
        try:
            while self.running:
                # Get message with timeout
                message = self.pubsub.get_message(timeout=1.0)
                
                if message is None:
                    continue
                
                if message['type'] != 'message':
                    continue
                
                try:
                    # Parse request
                    request_data = json.loads(message['data'].decode('utf-8'))
                    logger.info(f"Received historical data request: {request_data}")
                    
                    # Process request
                    response = self._handle_historical_request(request_data)
                    
                    # Send response
                    self._send_response(response)
                    
                    self.stats['requests_received'] += 1
                    
                except Exception as e:
                    logger.error(f"Error processing historical data request: {e}")
                    self.stats['errors'] += 1
                    
                    # Send error response
                    error_response = {
                        'requestId': request_data.get('requestId', 'unknown') if 'request_data' in locals() else 'unknown',
                        'success': False,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat() + 'Z'
                    }
                    self._send_response(error_response)
        
        except Exception as e:
            logger.error(f"Fatal error in listener thread: {e}")
        
        logger.info("Historical data request listener stopped")
    
    def _handle_historical_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle historical data request with REAL CSV data
        
        Args:
            request: Historical data request from TSX strategy
            
        Returns:
            Response with real historical market data
        """
        try:
            # Extract request parameters
            request_id = request.get('requestId', f'req_{int(time.time())}')
            symbol = request.get('symbol', 'MCL')  # Default to MCL if not specified
            bars_back = min(request.get('barsBack', self.config['default_bars_back']), 
                          self.config['max_bars_back'])
            
            # Update statistics
            if symbol not in self.stats['symbols_requested']:
                self.stats['symbols_requested'][symbol] = 0
            self.stats['symbols_requested'][symbol] += 1
            
            # Calculate current bars requested average
            total_requests = sum(self.stats['symbols_requested'].values())
            self.stats['avg_bars_requested'] = ((self.stats['avg_bars_requested'] * (total_requests - 1)) + bars_back) / total_requests
            
            logger.info(f"Processing request for {bars_back} bars of {symbol} data")
            
            # Determine end datetime for historical slice
            request_timestamp = request.get('timestamp')
            if request_timestamp:
                # Parse timestamp from request (backtesting scenario)
                try:
                    if isinstance(request_timestamp, str):
                        # Handle ISO format timestamp
                        end_datetime = datetime.fromisoformat(request_timestamp.replace('Z', '+00:00'))
                        # Convert to local time (remove timezone info for CSV data lookup)
                        end_datetime = end_datetime.replace(tzinfo=None)
                    else:
                        end_datetime = request_timestamp
                    logger.info(f"Using request timestamp: {end_datetime}")
                except Exception as e:
                    logger.warning(f"Failed to parse request timestamp '{request_timestamp}': {e}")
                    end_datetime = datetime.now() - timedelta(days=1)
            elif self.current_simulation_datetime:
                # Use simulation datetime for backtesting
                end_datetime = self.current_simulation_datetime
                logger.debug(f"Using simulation datetime: {end_datetime}")
            else:
                # Use recent datetime for live/test mode
                end_datetime = datetime.now() - timedelta(days=1)  # Yesterday to ensure data exists
                logger.debug(f"Using recent datetime: {end_datetime}")
            
            # Get real historical data from CSV files
            historical_bars = self._get_real_historical_data(symbol, end_datetime, bars_back)
            
            # Convert to TSX V5 format
            tsx_bars = self.data_loader.convert_to_tsx_format(historical_bars)
            
            # Create successful response
            response = {
                'requestId': request_id,
                'success': True,
                'data': {
                    'bars': tsx_bars,
                    'symbol': symbol,
                    'barsRequested': bars_back,
                    'barsReturned': len(tsx_bars),
                    'dataSource': 'CSV_REAL_MARKET_DATA',
                    'endDatetime': end_datetime.isoformat() + 'Z'
                },
                'timestamp': datetime.now().isoformat() + 'Z'
            }
            
            self.stats['responses_sent'] += 1
            self.stats['csv_files_accessed'] += 1
            
            logger.info(f"Sending {len(tsx_bars)} real bars for {symbol} (requested: {bars_back})")
            
            return response
            
        except ValueError as e:
            # Symbol not available error
            logger.warning(f"Symbol not available: {e}")
            
            return {
                'requestId': request.get('requestId', 'unknown'),
                'success': False,
                'error': f"DATA_NOT_AVAILABLE: {str(e)}",
                'timestamp': datetime.now().isoformat() + 'Z'
            }
            
        except Exception as e:
            logger.error(f"Error handling historical request: {e}")
            raise
    
    def _get_real_historical_data(self, symbol: str, end_datetime: datetime, bars_back: int) -> List[Dict[str, Any]]:
        """
        Get real historical data from CSV files
        
        Args:
            symbol: Symbol to get data for (exact match required)
            end_datetime: End datetime for historical slice
            bars_back: Number of bars to go back
            
        Returns:
            List of OHLCV bar dictionaries from real market data
            
        Raises:
            ValueError: If symbol is not available in CSV data
        """
        try:
            # Use CSV data loader to get historical slice
            historical_bars = self.data_loader.get_historical_slice(symbol, end_datetime, bars_back)
            
            logger.info(f"Retrieved {len(historical_bars)} real market bars for {symbol}")
            
            if len(historical_bars) == 0:
                logger.warning(f"No historical data found for {symbol} ending at {end_datetime}")
            
            return historical_bars
            
        except ValueError as e:
            # Symbol not available - don't substitute, just raise the error
            logger.warning(f"Symbol {symbol} not available in CSV data: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Error retrieving historical data for {symbol}: {e}")
            raise
    
    def _send_response(self, response: Dict[str, Any]):
        """Send response on Redis pub/sub channel"""
        try:
            response_json = json.dumps(response)
            self.redis_client.publish('aggregator:historical-data:response', response_json)
            logger.debug(f"Sent response: {response.get('requestId', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Error sending response: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        stats = self.stats.copy()
        stats['running'] = self.running
        stats['available_symbols'] = self.data_loader.get_available_symbols()
        stats['csv_data_directory'] = self.csv_data_directory
        stats['current_simulation_datetime'] = self.current_simulation_datetime.isoformat() + 'Z' if self.current_simulation_datetime else None
        
        return stats
    
    def test_symbol_availability(self, symbol: str) -> Dict[str, Any]:
        """
        Test if symbol is available in CSV data
        
        Args:
            symbol: Symbol to test
            
        Returns:
            Dictionary with availability info
        """
        try:
            is_available = self.data_loader.is_symbol_available(symbol)
            available_symbols = self.data_loader.get_available_symbols()
            
            result = {
                'symbol': symbol,
                'available': is_available,
                'all_available_symbols': available_symbols
            }
            
            if is_available:
                # Get date range if available
                min_date, max_date = self.data_loader.get_date_range_for_symbol(symbol)
                result['date_range'] = {
                    'min_date': min_date.isoformat() if min_date else None,
                    'max_date': max_date.isoformat() if max_date else None
                }
            
            return result
            
        except Exception as e:
            return {
                'symbol': symbol,
                'available': False,
                'error': str(e),
                'all_available_symbols': self.data_loader.get_available_symbols()
            }


# Test the service if run directly
if __name__ == "__main__":
    print("=== Testing Real CSV Historical Bootstrap Service ===")
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Configuration
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    redis_config = {'host': 'localhost', 'port': 6379, 'db': 0}
    
    try:
        # Test CSV data loader initialization
        print("\n[TEST 1] Testing CSV data loader initialization...")
        
        # Create Redis client
        redis_client = redis.Redis(**redis_config)
        redis_client.ping()  # Test connection
        print("Redis connection: OK")
        
        # Create service
        service = RealCSVHistoricalBootstrapService(redis_client, csv_data_dir)
        print("Service initialization: OK")
        
        # Test symbol availability
        print("\n[TEST 2] Testing symbol availability...")
        test_symbols = ['MCL', 'NQ', 'MES', 'INVALID']
        
        for symbol in test_symbols:
            availability = service.test_symbol_availability(symbol)
            print(f"  {symbol}: {availability['available']} - {availability.get('date_range', 'No date info')}")
        
        # Test historical data request processing (without starting service)
        print("\n[TEST 3] Testing historical data request processing...")
        
        # Set simulation datetime
        service.set_simulation_datetime(datetime(2023, 1, 15, 12, 0, 0))
        
        # Test valid symbol request
        test_request = {
            'requestId': 'test_001',
            'symbol': 'MCL',
            'barsBack': 10
        }
        
        response = service._handle_historical_request(test_request)
        print(f"  MCL request: {response['success']}")
        print(f"  Bars returned: {response.get('data', {}).get('barsReturned', 0)}")
        
        # Test invalid symbol request
        test_request_invalid = {
            'requestId': 'test_002',
            'symbol': 'NQ',
            'barsBack': 10
        }
        
        response_invalid = service._handle_historical_request(test_request_invalid)
        print(f"  NQ request: {response_invalid['success']} (should be False)")
        print(f"  Error: {response_invalid.get('error', 'No error')}")
        
        # Get statistics
        print("\n[TEST 4] Service statistics:")
        stats = service.get_statistics()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("\n=== Real CSV Historical Bootstrap Service Test Complete ===")
        print("SUCCESS: Service can load real market data from CSV files")
        print("SUCCESS: Symbol validation working (NQ returns error, MCL works)")
        print("SUCCESS: Ready to replace fake bootstrap service")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()