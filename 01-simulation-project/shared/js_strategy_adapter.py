"""
JavaScript Strategy Adapter for Python Backtesting
Simple bridge: Python sends price data → JS returns signals → Python executes trades
"""

import json
import subprocess
import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .strategy_interface import (
    StrategyInterface, StrategySignal, MarketData, 
    StrategyConfig, StrategyState
)

class JSStrategyAdapter(StrategyInterface):
    """
    Adapter to run JavaScript TSX Bot V5 strategies in Python backtester
    """
    
    def __init__(self, js_strategy_path: str, config: StrategyConfig, backtest_engine=None):
        super().__init__(config, backtest_engine)
        
        self.js_path = Path(js_strategy_path)
        if not self.js_path.exists():
            raise FileNotFoundError(f"Strategy not found: {js_strategy_path}")
        
        self.name = f"JS_{self.js_path.stem}"
        self.version = "1.0"
        
        # Node.js runner path
        self.runner_path = Path(__file__).parent / "strategy_runner.js"
        if not self.runner_path.exists():
            raise FileNotFoundError(f"Runner not found: {self.runner_path}")
        
        self.process = None
        self.is_initialized = False
        
        # Start Node.js process
        self._start_process()
    
    def _start_process(self):
        """Start Node.js process with strategy"""
        self.process = subprocess.Popen(
            ['node', str(self.runner_path), str(self.js_path)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Wait for ready signal
        ready_line = self.process.stdout.readline()
        if ready_line:
            ready_data = json.loads(ready_line)
            if ready_data.get('type') == 'READY':
                self.is_initialized = True
                print(f"JS Strategy loaded: {ready_data.get('strategy')}")
            else:
                raise RuntimeError(f"Strategy failed to start: {ready_line}")
        else:
            raise RuntimeError("No response from strategy runner")
    
    def _send_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send message to JS process and get response"""
        if not self.process or not self.is_initialized:
            raise RuntimeError("Strategy not initialized")
        
        # Send message
        self.process.stdin.write(json.dumps(message) + '\n')
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            return json.loads(response_line)
        return None
    
    def analyze(self, market_data: MarketData) -> StrategySignal:
        """Send price data to JS strategy and get signal"""
        
        # Prepare price data message
        message = {
            'type': 'PRICE_UPDATE',
            'data': {
                'open': market_data.open,
                'high': market_data.high,
                'low': market_data.low,
                'close': market_data.close,
                'volume': market_data.volume,
                'timestamp': market_data.timestamp.isoformat() if hasattr(market_data.timestamp, 'isoformat') else str(market_data.timestamp)
            }
        }
        
        # Send and receive
        response = self._send_message(message)
        
        if response and response.get('type') == 'SIGNAL':
            signal_str = response.get('signal', 'HOLD').upper()
            
            # Convert JS signal to Python StrategySignal
            if signal_str == 'BUY' or signal_str == 'LONG':
                return StrategySignal.BUY
            elif signal_str == 'SELL' or signal_str == 'SHORT':
                return StrategySignal.SELL
            elif signal_str == 'CLOSE' or signal_str == 'EXIT':
                return StrategySignal.CLOSE
            else:
                return StrategySignal.HOLD
        
        return StrategySignal.HOLD
    
    def on_position_opened(self, position: Dict[str, Any]):
        """Notify JS strategy of position change"""
        message = {
            'type': 'POSITION_UPDATE',
            'data': {
                'position': {
                    'size': position.get('size', 0),
                    'entryPrice': position.get('entry_price', 0),
                    'side': position.get('side', 'long')
                }
            }
        }
        self._send_message(message)
    
    def on_position_closed(self, position: Dict[str, Any]):
        """Notify JS strategy that position is closed"""
        message = {
            'type': 'POSITION_UPDATE',
            'data': {
                'position': None
            }
        }
        self._send_message(message)
    
    def cleanup(self):
        """Stop Node.js process"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None
            self.is_initialized = False
    
    def __del__(self):
        """Ensure cleanup on deletion"""
        self.cleanup()
