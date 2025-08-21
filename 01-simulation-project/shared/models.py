"""
Shared data models for all services
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ServiceStatus(str, Enum):
    """Service status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"

class HealthResponse(BaseModel):
    """Standard health check response"""
    status: ServiceStatus
    service: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None

class ContractSpec(BaseModel):
    """Futures contract specification"""
    symbol: str
    name: str
    tick_size: float
    tick_value: float
    contract_size: int
    margin_requirement: float
    currency: str = "USD"
    exchange: str
    
class MarketDataRequest(BaseModel):
    """Market data request model"""
    symbol: str
    start_date: datetime
    end_date: datetime
    timeframe: str = "1D"
    
class BacktestConfig(BaseModel):
    """Backtest configuration"""
    strategy_name: str
    symbol: str
    start_date: datetime
    end_date: datetime
    initial_cash: float = 100000
    commission: float = 2.50
    slippage: int = 1
    parameters: Dict[str, Any] = Field(default_factory=dict)
    strategy_config: Optional[Dict[str, Any]] = None  # Strategy-specific configuration
    
class Trade(BaseModel):
    """Individual trade record"""
    entry_time: datetime
    exit_time: Optional[datetime] = None
    symbol: str
    side: str  # "long" or "short"
    quantity: int
    entry_price: float
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    commission: float = 0
    
class BacktestResult(BaseModel):
    """Backtest results"""
    id: str
    config: BacktestConfig
    trades: list[Trade]
    metrics: Dict[str, float]
    equity_curve: list[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.now)
    
class RiskMetrics(BaseModel):
    """Risk analysis metrics"""
    total_return: float
    annual_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    var_95: float
    avg_win_loss_ratio: float