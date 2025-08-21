"""
Simplified JavaScript Strategy Bridge
Focuses only on: Price Data → JS Strategy → Trade Signals → Python Execution
"""

import json
import subprocess
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

class JSStrategyBridge:
    """Minimal bridge to run JS strategies and get signals"""
    
    def __init__(self, js_strategy_path: str):
        self.js_path = Path(js_strategy_path)
        if not self.js_path.exists():
            raise FileNotFoundError(f"Strategy not found: {js_strategy_path}")
        
        # Create Node.js runner script
        self.runner_path = Path(__file__).parent / "strategy_runner.js"
        self._create_runner_script()
    
    def _create_runner_script(self):
        """Create minimal Node.js runner that loads strategy and processes data"""
        runner_code = '''
const fs = require('fs');
const path = require('path');

// Load strategy file
const strategyPath = process.argv[2];
const StrategyClass = require(strategyPath);

// Create minimal mock mainBot (only what strategies actually use)
const mockMainBot = {
    modules: {
        positionManagement: {
            hasPosition: () => false,
            getCurrentPosition: () => null
        }
    }
};

// Initialize strategy
const strategy = new StrategyClass({}, mockMainBot);

// Process incoming price data
process.stdin.on('data', (data) => {
    try {
        const priceData = JSON.parse(data);
        
        // Call strategy's analyze method
        const signal = strategy.analyze(priceData);
        
        // Send signal back to Python
        process.stdout.write(JSON.stringify({
            signal: signal,
            timestamp: new Date().toISOString()
        }) + '\n');
        
    } catch (error) {
        process.stderr.write(`Error: ${error.message}\n`);
    }
});

// Ready signal
console.log(JSON.stringify({ready: true, strategy: strategyPath}));
'''
        self.runner_path.write_text(runner_code)
    
    def start(self):
        """Start Node.js process with strategy loaded"""
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
        ready_data = json.loads(ready_line)
        if not ready_data.get('ready'):
            raise RuntimeError("Strategy failed to initialize")
        
        return ready_data
    
    def get_signal(self, price_data: Dict[str, Any]) -> Optional[str]:
        """Send price data to JS strategy and get trading signal"""
        if not self.process:
            raise RuntimeError("Strategy not started")
        
        # Send price data
        self.process.stdin.write(json.dumps(price_data) + '\n')
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
            return response.get('signal')
        
        return None
    
    def stop(self):
        """Stop Node.js process"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
