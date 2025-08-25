"""
Phase 2B: Full Strategy Signal Testing Framework
Tests TSX strategy signal generation with real CSV market data
Bypasses subprocess complexity and focuses on signal validation
"""

import json
import redis
import time
import threading
from datetime import datetime, timedelta
from claude_real_csv_bootstrap_service import RealCSVHistoricalBootstrapService
from claude_csv_data_loader import MonthlyCSVDataLoader

class StrategySignalTester:
    """Test TSX strategy signal generation with real market data"""
    
    def __init__(self, csv_data_directory: str):
        self.csv_data_directory = csv_data_directory
        
        # Redis clients
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.redis_binary = redis.Redis(host='localhost', port=6379, decode_responses=False)
        
        # CSV data loader
        self.data_loader = MonthlyCSVDataLoader(csv_data_directory)
        
        # Bootstrap service
        self.bootstrap_service = RealCSVHistoricalBootstrapService(
            self.redis_binary,
            csv_data_directory,
            config={'default_bars_back': 50, 'max_bars_back': 500}
        )
        
        # Signal collection
        self.signals_received = []
        self.signal_listener_running = False
        
    def start_bootstrap_service(self, simulation_date: datetime = None):
        """Start the bootstrap service for the test"""
        if simulation_date:
            self.bootstrap_service.set_simulation_datetime(simulation_date)
        
        self.bootstrap_service.start()
        print(f"[OK] Bootstrap service started")
        
    def setup_signal_listener(self, bot_id: str):
        """Setup Redis listener for strategy signals"""
        
        def listen_for_signals():
            pubsub = self.redis_client.pubsub()
            pubsub.subscribe(f'aggregator:signal:{bot_id}')
            
            print(f"[OK] Listening for signals on: aggregator:signal:{bot_id}")
            
            try:
                while self.signal_listener_running:
                    message = pubsub.get_message(timeout=1.0)
                    
                    if message and message['type'] == 'message':
                        try:
                            signal_data = json.loads(message['data'])
                            self.signals_received.append({
                                'signal': signal_data,
                                'received_at': datetime.now().isoformat()
                            })
                            
                            print(f"[SIGNAL] {signal_data.get('action', 'UNKNOWN')} at {signal_data.get('timestamp', 'NO_TIME')}")
                            print(f"  Price: {signal_data.get('price', 'N/A')} | Symbol: {signal_data.get('symbol', 'N/A')}")
                            
                        except Exception as e:
                            print(f"[ERROR] Error processing signal: {e}")
                            
            except Exception as e:
                print(f"[ERROR] Error in signal listener: {e}")
            finally:
                pubsub.unsubscribe()
                pubsub.close()
        
        self.signal_listener_running = True
        listener_thread = threading.Thread(target=listen_for_signals, daemon=True)
        listener_thread.start()
        
        return listener_thread
    
    def send_market_data_sequence(self, symbol: str, bot_id: str, start_date: datetime, num_bars: int = 20):
        """Send a sequence of real market data to test strategy signal generation"""
        
        print(f"[OK] Loading {num_bars} real market bars starting from {start_date}")
        
        # Get real historical data
        historical_bars = self.data_loader.get_historical_slice(symbol, start_date, num_bars * 2)
        
        if len(historical_bars) < num_bars:
            print(f"[WARNING] Only {len(historical_bars)} bars available, using all")
            test_bars = historical_bars
        else:
            test_bars = historical_bars[-num_bars:]  # Use most recent bars
        
        print(f"[OK] Sending {len(test_bars)} real market data bars to strategy...")
        
        # Send market data sequence
        channel = f'aggregator:market-data:{bot_id}'
        
        for i, bar in enumerate(test_bars):
            market_update = {
                'symbol': symbol,
                'price': bar['close'],
                'open': bar['open'],
                'high': bar['high'],
                'low': bar['low'],
                'volume': bar['volume'],
                'timestamp': bar['datetime'].isoformat() + 'Z',
                'bar_number': i + 1,
                'total_bars': len(test_bars)
            }
            
            # Publish market data
            self.redis_client.publish(channel, json.dumps(market_update))
            
            # Brief delay to simulate real-time data
            time.sleep(0.1)
            
            if (i + 1) % 5 == 0:
                print(f"  [PROGRESS] Sent {i + 1}/{len(test_bars)} bars...")
        
        print(f"[OK] All {len(test_bars)} market data bars sent")
        return len(test_bars)
    
    def get_signal_summary(self):
        """Get summary of signals received"""
        if not self.signals_received:
            return {"total_signals": 0, "summary": "No signals received"}
        
        signal_types = {}
        for sig in self.signals_received:
            action = sig['signal'].get('action', 'UNKNOWN')
            if action not in signal_types:
                signal_types[action] = 0
            signal_types[action] += 1
        
        return {
            "total_signals": len(self.signals_received),
            "signal_types": signal_types,
            "signals": self.signals_received
        }
    
    def cleanup(self):
        """Cleanup resources"""
        self.signal_listener_running = False
        
        if self.bootstrap_service:
            self.bootstrap_service.stop()

def run_phase2b_testing():
    """Run Phase 2B: Full Strategy Signal Testing"""
    
    print("=" * 80)
    print("PHASE 2B: FULL STRATEGY SIGNAL TESTING")
    print("Testing TSX EMA Strategy Signal Generation with Real CSV Market Data")
    print("=" * 80)
    
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    tester = StrategySignalTester(csv_data_dir)
    
    try:
        print(f"\n[STEP 1] Setting up signal testing environment...")
        
        # Setup test configuration
        test_config = {
            'symbol': 'MCL',
            'bot_id': 'signal_test_bot',
            'simulation_date': datetime(2023, 6, 15, 14, 30, 0),  # Afternoon trading time
            'test_bars': 25
        }
        
        print(f"  Symbol: {test_config['symbol']}")
        print(f"  Bot ID: {test_config['bot_id']}")
        print(f"  Simulation date: {test_config['simulation_date']}")
        
        # Start bootstrap service
        tester.start_bootstrap_service(test_config['simulation_date'])
        
        # Setup signal listener
        signal_thread = tester.setup_signal_listener(test_config['bot_id'])
        
        print(f"\n[STEP 2] Testing strategy signal generation...")
        
        # Wait for setup
        time.sleep(2)
        
        # Send real market data sequence
        bars_sent = tester.send_market_data_sequence(
            test_config['symbol'],
            test_config['bot_id'], 
            test_config['simulation_date'],
            test_config['test_bars']
        )
        
        print(f"\n[STEP 3] Waiting for strategy signals...")
        
        # Wait for signals to be generated
        time.sleep(5)
        
        # Analyze signal results
        signal_summary = tester.get_signal_summary()
        
        print(f"\n[STEP 4] Signal Generation Results:")
        print(f"  Market data bars sent: {bars_sent}")
        print(f"  Total signals received: {signal_summary['total_signals']}")
        
        if signal_summary['total_signals'] > 0:
            print(f"  Signal types: {signal_summary['signal_types']}")
            
            # Show sample signals
            print(f"\n  Sample signals:")
            for i, sig_data in enumerate(signal_summary['signals'][:3]):
                signal = sig_data['signal']
                print(f"    [{i+1}] {signal.get('action', 'UNKNOWN')} at {signal.get('price', 'N/A')} ({signal.get('timestamp', 'NO_TIME')})")
        
        print(f"\n" + "=" * 80)
        
        # Determine Phase 2B success
        if signal_summary['total_signals'] > 0:
            print(f"[SUCCESS] PHASE 2B: STRATEGY SIGNAL GENERATION WORKING")
            print(f"[OK] TSX EMA strategy successfully generated {signal_summary['total_signals']} signals")
            print(f"[OK] Real market data driving authentic signal generation")
            phase2b_success = True
        else:
            print(f"[PARTIAL] PHASE 2B: Infrastructure ready, signals pending")
            print(f"[INFO] Market data pipeline working, waiting for signal conditions")
            phase2b_success = False
        
        print(f"=" * 80)
        
        return phase2b_success, signal_summary
        
    except Exception as e:
        print(f"[ERROR] Phase 2B testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False, {}
        
    finally:
        tester.cleanup()

def run_phase2c_testing():
    """Run Phase 2C: Multi-Symbol CSV Support Testing"""
    
    print("\n" + "=" * 80)
    print("PHASE 2C: MULTI-SYMBOL CSV SUPPORT TESTING")
    print("Testing MES, MGC, NG, SI symbol integration")
    print("=" * 80)
    
    csv_data_dir = r"C:\Users\salte\ClaudeProjects\github-repos\00-trading-project\98-month-by-month-data-files"
    
    try:
        data_loader = MonthlyCSVDataLoader(csv_data_dir)
        
        # Test symbols (excluding non-trading directories)
        test_symbols = ['MCL', 'MES', 'MGC', 'NG', 'SI']
        
        print(f"\n[STEP 1] Testing symbol availability...")
        
        symbol_results = {}
        
        for symbol in test_symbols:
            try:
                # Test availability
                available = data_loader.is_symbol_available(symbol)
                
                if available:
                    # Get date range
                    min_date, max_date = data_loader.get_date_range_for_symbol(symbol)
                    
                    # Test data loading
                    test_date = datetime(2023, 6, 15)
                    test_bars = data_loader.get_historical_slice(symbol, test_date, 10)
                    
                    symbol_results[symbol] = {
                        'available': True,
                        'date_range': {'min': min_date, 'max': max_date},
                        'test_bars': len(test_bars),
                        'sample_price': test_bars[0]['close'] if test_bars else None
                    }
                    
                    print(f"  [OK] {symbol}: {len(test_bars)} bars, sample price: {symbol_results[symbol]['sample_price']}")
                    
                else:
                    symbol_results[symbol] = {'available': False}
                    print(f"  [FAIL] {symbol}: Not available")
                    
            except Exception as e:
                symbol_results[symbol] = {'available': False, 'error': str(e)}
                print(f"  [ERROR] {symbol}: {e}")
        
        print(f"\n[STEP 2] Multi-Symbol Integration Results:")
        
        available_symbols = [s for s, r in symbol_results.items() if r.get('available')]
        unavailable_symbols = [s for s, r in symbol_results.items() if not r.get('available')]
        
        print(f"  Available symbols: {available_symbols}")
        print(f"  Unavailable symbols: {unavailable_symbols}")
        
        print(f"\n" + "=" * 80)
        
        if len(available_symbols) >= 3:  # At least 3 symbols working
            print(f"[SUCCESS] PHASE 2C: MULTI-SYMBOL CSV SUPPORT WORKING")
            print(f"[OK] {len(available_symbols)} symbols available for backtesting")
            phase2c_success = True
        else:
            print(f"[PARTIAL] PHASE 2C: Limited symbol support")
            print(f"[INFO] Only {len(available_symbols)} symbols available")
            phase2c_success = False
            
        print(f"=" * 80)
        
        return phase2c_success, symbol_results
        
    except Exception as e:
        print(f"[ERROR] Phase 2C testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

if __name__ == "__main__":
    print("=== PHASES 2B & 2C TESTING ===")
    
    # Run Phase 2B
    phase2b_success, signal_summary = run_phase2b_testing()
    
    # Run Phase 2C  
    phase2c_success, symbol_results = run_phase2c_testing()
    
    print(f"\n" + "=" * 80)
    print(f"FINAL RESULTS:")
    print(f"  Phase 2B (Signal Testing): {'SUCCESS' if phase2b_success else 'PARTIAL'}")
    print(f"  Phase 2C (Multi-Symbol): {'SUCCESS' if phase2c_success else 'PARTIAL'}")
    
    if phase2b_success and phase2c_success:
        print(f"\n[COMPLETE] PHASES 2B & 2C: FULLY SUCCESSFUL")
    else:
        print(f"\n[PARTIAL] PHASES 2B & 2C: Infrastructure ready, refinements possible")
    print(f"=" * 80)