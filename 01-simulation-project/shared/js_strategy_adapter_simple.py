"""
Simplified JavaScript Strategy Adapter for Python Backtesting
Bridge: Python sends price data → JS returns signals → Python executes trades
"""

import json
import subprocess
import os
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from enum import Enum

# Simple signal enum since we can't import from strategy_interface yet
class Signal(Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    CLOSE = "CLOSE"

class JSStrategyAdapter:
    """
    Adapter to run JavaScript TSX Bot V5 strategies in Python backtester
    """
    
    def __init__(self, js_strategy_path: str, config: Dict[str, Any] = None):
        self.js_path = Path(js_strategy_path)
        if not self.js_path.exists():
            raise FileNotFoundError(f"Strategy not found: {js_strategy_path}")
        
        self.name = f"JS_{self.js_path.stem}"
        self.version = "1.0"
        self.config = config or {}
        
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
    
    def analyze(self, price_data: Dict[str, Any]) -> str:
        """Send price data to JS strategy and get signal"""
        
        # Prepare price data message
        message = {
            'type': 'PRICE_UPDATE',
            'data': {
                'open': price_data.get('open', price_data.get('close', 0)),
                'high': price_data.get('high', price_data.get('close', 0)),
                'low': price_data.get('low', price_data.get('close', 0)),
                'close': price_data.get('close', 0),
                'volume': price_data.get('volume', 1000),
                'timestamp': price_data.get('timestamp', datetime.now().isoformat())
            }
        }
        
        # Send and receive
        response = self._send_message(message)
        
        if response and response.get('type') == 'SIGNAL':
            return response.get('signal', 'HOLD').upper()
        
        return 'HOLD'
    
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
