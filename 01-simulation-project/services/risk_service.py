#!/usr/bin/env python3
"""
Risk Service - Week 6 Implementation
Provides essential risk management calculations including Sharpe ratio, drawdown, VaR, 
position sizing, and risk limit monitoring.
"""

import sys
import math
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from shared.utils import setup_logging
from shared.models import HealthResponse, ServiceStatus
from shared.redis_client import redis_client
from config.settings import SERVICE_PORTS

# Initialize logging
logger = setup_logging("RiskService", "INFO")

app = FastAPI(
    title="Risk Service",
    description="Risk management calculations and position sizing",
    version="1.0.0"
)

class RiskCalculator:
    """Core risk calculation engine"""
    
    def __init__(self):
        self.portfolio_service_url = f"http://localhost:{SERVICE_PORTS['portfolio']}"
        self.backtest_service_url = f"http://localhost:{SERVICE_PORTS['backtest']}"
        
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio from returns series
        
        Args:
            returns: List of period returns (e.g., daily returns)
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio (annualized)
        """
        if not returns or len(returns) < 2:
            return 0.0
            
        returns_array = np.array(returns)
        
        # Convert to excess returns
        daily_rf_rate = risk_free_rate / 252  # Assuming 252 trading days
        excess_returns = returns_array - daily_rf_rate
        
        # Calculate Sharpe ratio
        if np.std(excess_returns) == 0:
            return 0.0
            
        sharpe = np.mean(excess_returns) / np.std(excess_returns)
        
        # Annualize (multiply by sqrt of 252 trading days)
        return sharpe * math.sqrt(252)
    
    def calculate_maximum_drawdown(self, equity_curve: List[float]) -> Dict:
        """
        Calculate maximum drawdown from equity curve
        
        Args:
            equity_curve: List of portfolio values over time
            
        Returns:
            Dict with max_drawdown, peak_value, trough_value, drawdown_duration
        """
        if not equity_curve or len(equity_curve) < 2:
            return {
                'max_drawdown': 0.0,
                'max_drawdown_pct': 0.0,
                'peak_value': 0.0,
                'trough_value': 0.0,
                'drawdown_duration': 0
            }
            
        equity_array = np.array(equity_curve)
        
        # Calculate running maximum (peak)
        running_max = np.maximum.accumulate(equity_array)
        
        # Calculate drawdown
        drawdown = equity_array - running_max
        drawdown_pct = drawdown / running_max * 100
        
        # Find maximum drawdown
        max_dd_idx = np.argmin(drawdown)
        max_drawdown = drawdown[max_dd_idx]
        max_drawdown_pct = drawdown_pct[max_dd_idx]
        
        # Find peak before max drawdown
        peak_idx = np.argmax(running_max[:max_dd_idx + 1])
        
        return {
            'max_drawdown': float(abs(max_drawdown)),
            'max_drawdown_pct': float(abs(max_drawdown_pct)),
            'peak_value': float(equity_array[peak_idx]),
            'trough_value': float(equity_array[max_dd_idx]),
            'drawdown_duration': int(max_dd_idx - peak_idx)
        }
    
    def calculate_var(self, returns: List[float], confidence_level: float = 0.95) -> Dict:
        """
        Calculate Value at Risk using historical simulation
        
        Args:
            returns: List of portfolio returns
            confidence_level: Confidence level (default 95%)
            
        Returns:
            Dict with VaR values for different time horizons
        """
        if not returns or len(returns) < 10:
            return {
                'daily_var': 0.0,
                'weekly_var': 0.0,
                'monthly_var': 0.0,
                'confidence_level': confidence_level
            }
            
        returns_array = np.array(returns)
        
        # Calculate daily VaR
        daily_var = np.percentile(returns_array, (1 - confidence_level) * 100)
        
        # Scale to different time horizons (assuming independence)
        weekly_var = daily_var * math.sqrt(5)  # 5 trading days
        monthly_var = daily_var * math.sqrt(21)  # 21 trading days
        
        return {
            'daily_var': float(abs(daily_var)),
            'weekly_var': float(abs(weekly_var)),
            'monthly_var': float(abs(monthly_var)),
            'confidence_level': float(confidence_level)
        }
    
    def calculate_position_size(self, 
                              account_value: float, 
                              risk_per_trade: float,
                              entry_price: float,
                              stop_loss_price: float,
                              contract_size: int = 1) -> Dict:
        """
        Calculate position size based on risk parameters
        
        Args:
            account_value: Total account value
            risk_per_trade: Risk per trade as percentage (e.g., 0.02 for 2%)
            entry_price: Entry price per contract
            stop_loss_price: Stop loss price per contract
            contract_size: Contract multiplier
            
        Returns:
            Dict with position sizing recommendations
        """
        if entry_price <= 0 or account_value <= 0 or risk_per_trade <= 0:
            return {
                'position_size': 0,
                'risk_amount': 0.0,
                'margin_required': 0.0,
                'leverage_ratio': 0.0
            }
        
        # Calculate risk per contract
        risk_per_contract = abs(entry_price - stop_loss_price) * contract_size
        
        if risk_per_contract <= 0:
            return {
                'position_size': 0,
                'risk_amount': 0.0,
                'margin_required': 0.0,
                'leverage_ratio': 0.0
            }
        
        # Calculate maximum risk amount
        max_risk_amount = account_value * risk_per_trade
        
        # Calculate position size
        position_size = int(max_risk_amount / risk_per_contract)
        
        # Calculate actual risk and margin
        actual_risk = position_size * risk_per_contract
        margin_required = position_size * entry_price * contract_size * 0.10  # 10% margin
        leverage_ratio = (position_size * entry_price * contract_size) / account_value
        
        return {
            'position_size': position_size,
            'risk_amount': actual_risk,
            'margin_required': margin_required,
            'leverage_ratio': leverage_ratio
        }
    
    def get_portfolio_data(self, portfolio_id: str) -> Optional[Dict]:
        """Get portfolio data from Portfolio Service"""
        try:
            response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{portfolio_id}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"Failed to get portfolio data: {e}")
            return None
    
    def get_portfolio_trades(self, portfolio_id: str) -> Optional[List[Dict]]:
        """Get portfolio trade history from Portfolio Service"""
        try:
            response = requests.get(
                f"{self.portfolio_service_url}/api/portfolio/{portfolio_id}/trades",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return data.get('trades', [])
            return None
        except Exception as e:
            logger.error(f"Failed to get portfolio trades: {e}")
            return None

# Initialize risk calculator
risk_calculator = RiskCalculator()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        redis_healthy = redis_client.health_check()
        
        # Test Portfolio Service connection
        portfolio_response = requests.get(
            f"http://localhost:{SERVICE_PORTS['portfolio']}/health",
            timeout=2
        )
        portfolio_healthy = portfolio_response.status_code == 200
        
        if redis_healthy and portfolio_healthy:
            return HealthResponse(
                status=ServiceStatus.HEALTHY,
                service="RiskService",
                timestamp=datetime.utcnow(),
                details={
                    "redis": "connected",
                    "portfolio_service": "connected"
                }
            )
        else:
            return HealthResponse(
                status=ServiceStatus.DEGRADED,
                service="RiskService",
                timestamp=datetime.utcnow(),
                details={
                    "redis": "connected" if redis_healthy else "disconnected",
                    "portfolio_service": "connected" if portfolio_healthy else "disconnected"
                }
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status=ServiceStatus.UNHEALTHY,
            service="RiskService",
            timestamp=datetime.utcnow(),
            details={"error": str(e)}
        )

@app.post("/api/risk/sharpe-ratio")
async def calculate_sharpe(portfolio_id: str, risk_free_rate: float = 0.02):
    """
    Calculate Sharpe ratio for a portfolio
    
    Args:
        portfolio_id: Portfolio identifier
        risk_free_rate: Annual risk-free rate (default 2%)
    """
    try:
        # Get portfolio trades to calculate returns
        trades = risk_calculator.get_portfolio_trades(portfolio_id)
        if not trades:
            raise HTTPException(status_code=404, detail="Portfolio or trades not found")
        
        # Calculate daily returns from trades
        returns = []
        if len(trades) >= 2:
            # Simple return calculation based on trade P&L
            for trade in trades:
                if 'pnl' in trade and trade['pnl'] is not None:
                    # Convert P&L to return (assuming initial portfolio value)
                    portfolio_data = risk_calculator.get_portfolio_data(portfolio_id)
                    if portfolio_data and 'portfolio' in portfolio_data:
                        initial_cash = portfolio_data['portfolio'].get('initial_cash', 100000)
                        if initial_cash > 0:
                            returns.append(trade['pnl'] / initial_cash)
        
        sharpe_ratio = risk_calculator.calculate_sharpe_ratio(returns, risk_free_rate)
        
        return {
            "portfolio_id": portfolio_id,
            "sharpe_ratio": sharpe_ratio,
            "risk_free_rate": risk_free_rate,
            "number_of_returns": len(returns),
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sharpe ratio calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/risk/drawdown")
async def calculate_drawdown(portfolio_id: str):
    """
    Calculate maximum drawdown for a portfolio
    
    Args:
        portfolio_id: Portfolio identifier
    """
    try:
        # Get portfolio equity curve
        equity_response = requests.get(
            f"http://localhost:{SERVICE_PORTS['portfolio']}/api/portfolio/{portfolio_id}/equity-curve",
            timeout=5
        )
        
        if equity_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Portfolio equity curve not found")
        
        equity_data = equity_response.json()
        equity_curve = equity_data.get('equity_curve', {})
        
        # Create simple equity curve from current values
        current_value = equity_curve.get('total_value', 0)
        initial_value = equity_curve.get('initial_cash', 100000)
        
        # For now, create a simple two-point curve
        # In a real implementation, this would be historical equity values
        equity_values = [initial_value, current_value]
        
        drawdown_metrics = risk_calculator.calculate_maximum_drawdown(equity_values)
        
        return {
            "portfolio_id": portfolio_id,
            **drawdown_metrics,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Drawdown calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/risk/var")
async def calculate_value_at_risk(portfolio_id: str, confidence_level: float = 0.95):
    """
    Calculate Value at Risk for a portfolio
    
    Args:
        portfolio_id: Portfolio identifier  
        confidence_level: Confidence level (default 95%)
    """
    try:
        # Get portfolio trades to calculate returns
        trades = risk_calculator.get_portfolio_trades(portfolio_id)
        if not trades:
            raise HTTPException(status_code=404, detail="Portfolio or trades not found")
        
        # Calculate returns from trades
        returns = []
        portfolio_data = risk_calculator.get_portfolio_data(portfolio_id)
        if portfolio_data and 'portfolio' in portfolio_data:
            initial_cash = portfolio_data['portfolio'].get('initial_cash', 100000)
            
            for trade in trades:
                if 'pnl' in trade and trade['pnl'] is not None and initial_cash > 0:
                    returns.append(trade['pnl'] / initial_cash)
        
        var_metrics = risk_calculator.calculate_var(returns, confidence_level)
        
        return {
            "portfolio_id": portfolio_id,
            **var_metrics,
            "number_of_returns": len(returns),
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"VaR calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/risk/position-size")
async def calculate_position_sizing(
    account_value: float,
    risk_per_trade: float,
    entry_price: float,
    stop_loss_price: float,
    contract_size: int = 1
):
    """
    Calculate optimal position size based on risk parameters
    
    Args:
        account_value: Total account value
        risk_per_trade: Risk per trade as decimal (e.g., 0.02 for 2%)
        entry_price: Entry price per contract
        stop_loss_price: Stop loss price per contract
        contract_size: Contract multiplier (default 1)
    """
    try:
        position_metrics = risk_calculator.calculate_position_size(
            account_value=account_value,
            risk_per_trade=risk_per_trade,
            entry_price=entry_price,
            stop_loss_price=stop_loss_price,
            contract_size=contract_size
        )
        
        return {
            **position_metrics,
            "account_value": account_value,
            "risk_per_trade_pct": risk_per_trade * 100,
            "entry_price": entry_price,
            "stop_loss_price": stop_loss_price,
            "contract_size": contract_size,
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Position sizing calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/portfolio/{portfolio_id}/summary")
async def get_risk_summary(portfolio_id: str):
    """
    Get comprehensive risk summary for a portfolio
    
    Args:
        portfolio_id: Portfolio identifier
    """
    try:
        # Get portfolio data
        portfolio_data = risk_calculator.get_portfolio_data(portfolio_id)
        if not portfolio_data:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        portfolio_info = portfolio_data.get('portfolio', {})
        current_value = portfolio_info.get('current_cash', 0)
        initial_value = portfolio_info.get('initial_cash', 100000)
        
        # Get trades for return calculations
        trades = risk_calculator.get_portfolio_trades(portfolio_id)
        returns = []
        
        if trades and initial_value > 0:
            for trade in trades:
                if 'pnl' in trade and trade['pnl'] is not None:
                    returns.append(trade['pnl'] / initial_value)
        
        # Calculate all risk metrics
        sharpe_ratio = risk_calculator.calculate_sharpe_ratio(returns) if returns else 0.0
        
        equity_values = [initial_value, current_value]
        drawdown_metrics = risk_calculator.calculate_maximum_drawdown(equity_values)
        
        var_metrics = risk_calculator.calculate_var(returns) if returns else {
            'daily_var': 0.0, 'weekly_var': 0.0, 'monthly_var': 0.0, 'confidence_level': 0.95
        }
        
        # Calculate total return
        total_return = ((current_value - initial_value) / initial_value * 100) if initial_value > 0 else 0.0
        
        return {
            "portfolio_id": portfolio_id,
            "portfolio_info": {
                "initial_value": initial_value,
                "current_value": current_value,
                "total_return_pct": total_return,
                "number_of_trades": len(trades) if trades else 0
            },
            "risk_metrics": {
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": drawdown_metrics['max_drawdown'],
                "max_drawdown_pct": drawdown_metrics['max_drawdown_pct'],
                "daily_var": var_metrics['daily_var'],
                "weekly_var": var_metrics['weekly_var'],
                "monthly_var": var_metrics['monthly_var']
            },
            "calculated_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Risk summary calculation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/risk/limits")
async def get_risk_limits():
    """Get current risk limits and monitoring settings"""
    return {
        "risk_limits": {
            "max_portfolio_risk": 0.10,  # 10% max portfolio risk
            "max_single_trade_risk": 0.02,  # 2% max per trade
            "max_drawdown_limit": 0.15,  # 15% max drawdown before alert
            "min_sharpe_ratio": 1.0,  # Minimum acceptable Sharpe ratio
            "max_leverage": 3.0  # Maximum leverage ratio
        },
        "monitoring_enabled": True,
        "alert_channels": ["log", "redis"]
    }

def main():
    """Main entry point"""
    logger.info("🎯 Starting Risk Service on port 8003...")
    
    try:
        uvicorn.run(
            "risk_service:app",
            host="0.0.0.0",
            port=SERVICE_PORTS['risk'],
            reload=False,
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start Risk Service: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()