"""
Database models for PDH/PDL trading strategy.
SQLAlchemy ORM models for all database tables.
"""

from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, DateTime, Date, 
    Numeric, BigInteger, Text, Index
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from typing import Optional

Base = declarative_base()


class MarketData(Base):
    """Historical market data model."""
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(Numeric(10, 4), nullable=False)
    high_price = Column(Numeric(10, 4), nullable=False)
    low_price = Column(Numeric(10, 4), nullable=False)
    close_price = Column(Numeric(10, 4), nullable=False)
    volume = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    __table_args__ = (
        Index('idx_market_data_symbol_timestamp', 'symbol', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', timestamp='{self.timestamp}', close={self.close_price})>"


class ReferenceLevel(Base):
    """PDH/PDL reference levels model."""
    __tablename__ = 'reference_levels'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    trade_date = Column(Date, nullable=False)
    pdh = Column(Numeric(10, 4), nullable=False)
    pdl = Column(Numeric(10, 4), nullable=False)
    daily_range = Column(Numeric(10, 4), nullable=False)
    poc = Column(Numeric(10, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    __table_args__ = (
        Index('idx_reference_levels_symbol_date', 'symbol', 'trade_date'),
    )
    
    @property
    def midpoint(self) -> Decimal:
        """Calculate midpoint between PDH and PDL."""
        return (self.pdh + self.pdl) / 2
    
    def __repr__(self):
        return f"<ReferenceLevel(symbol='{self.symbol}', date='{self.trade_date}', pdh={self.pdh}, pdl={self.pdl})>"


class Trade(Base):
    """Trade execution log model."""
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), nullable=False)
    strategy_type = Column(String(20), nullable=False)
    direction = Column(String(5), nullable=False)
    entry_timestamp = Column(DateTime(timezone=True), nullable=False)
    exit_timestamp = Column(DateTime(timezone=True), nullable=True)
    entry_price = Column(Numeric(10, 4), nullable=False)
    exit_price = Column(Numeric(10, 4), nullable=True)
    quantity = Column(Integer, nullable=False)
    stop_loss = Column(Numeric(10, 4), nullable=False)
    target_price = Column(Numeric(10, 4), nullable=True)
    pnl = Column(Numeric(10, 2), nullable=True)
    commission = Column(Numeric(10, 2), default=0)
    status = Column(String(20), default='OPEN')
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_trades_symbol_entry', 'symbol', 'entry_timestamp'),
        Index('idx_trades_status', 'status'),
    )
    
    @property
    def is_open(self) -> bool:
        """Check if trade is still open."""
        return self.status == 'OPEN'
    
    @property
    def is_winner(self) -> bool:
        """Check if trade is profitable."""
        return self.pnl is not None and self.pnl > 0
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate trade duration in minutes."""
        if self.exit_timestamp:
            delta = self.exit_timestamp - self.entry_timestamp
            return int(delta.total_seconds() / 60)
        return None
    
    def calculate_pnl(self, tick_value: Decimal) -> Decimal:
        """Calculate P&L for the trade."""
        if self.exit_price is None:
            return Decimal(0)
        
        if self.direction == 'LONG':
            price_diff = self.exit_price - self.entry_price
        else:  # SHORT
            price_diff = self.entry_price - self.exit_price
        
        gross_pnl = price_diff * self.quantity * tick_value
        net_pnl = gross_pnl - self.commission
        return net_pnl
    
    def __repr__(self):
        return f"<Trade(symbol='{self.symbol}', direction='{self.direction}', entry={self.entry_price}, status='{self.status}')>"


class PerformanceMetrics(Base):
    """Daily performance metrics model."""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    symbol = Column(String(10), nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    gross_profit = Column(Numeric(10, 2), default=0)
    gross_loss = Column(Numeric(10, 2), default=0)
    net_profit = Column(Numeric(10, 2), default=0)
    profit_factor = Column(Numeric(6, 3), nullable=True)
    max_drawdown = Column(Numeric(6, 3), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    
    __table_args__ = (
        Index('idx_performance_date', 'date'),
    )
    
    @property
    def win_rate(self) -> Optional[float]:
        """Calculate win rate percentage."""
        if self.total_trades > 0:
            return (self.winning_trades / self.total_trades) * 100
        return None
    
    def __repr__(self):
        return f"<PerformanceMetrics(date='{self.date}', symbol='{self.symbol}', trades={self.total_trades})>"


class SystemLog(Base):
    """System logging model."""
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    level = Column(String(10), nullable=False)
    message = Column(Text, nullable=False)
    module = Column(String(50), nullable=True)
    function = Column(String(50), nullable=True)
    
    __table_args__ = (
        Index('idx_system_logs_timestamp', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<SystemLog(level='{self.level}', timestamp='{self.timestamp}', message='{self.message[:50]}...')>"