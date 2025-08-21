#!/usr/bin/env python3
"""
Portfolio Service - Position Tracking and Equity Curve Management
Port: 8005
Purpose: Portfolio and position management, trade recording, equity curve calculation

Database Tables:
- portfolios: Portfolio configurations (id, name, initial_cash, created_at)
- positions: Current positions (portfolio_id, symbol, quantity, avg_price, timestamp)
- trades: All trade records (portfolio_id, symbol, action, quantity, price, timestamp, strategy_name, pnl)
- portfolio_snapshots: Historical portfolio values (portfolio_id, timestamp, total_value, cash_balance, positions_value)
"""

import sys
import sqlite3
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from decimal import Decimal

sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
import uvicorn

from shared.models import HealthResponse, ServiceStatus
from shared.utils import setup_logging, generate_id, Timer
from shared.redis_client import redis_client
from shared.retry_utils import retry_with_backoff, REDIS_RETRY_CONFIG
from config.settings import SERVICE_PORTS, DATA_DIR

logger = setup_logging("PortfolioService", "INFO")

# Database connection - UPDATED FOR PHASE 1: Using unified futures.db
DATABASE_PATH = DATA_DIR / "futures.db"

app = FastAPI(
    title="Portfolio Service", 
    version="1.0",
    description="Portfolio management, position tracking, and equity curve calculation"
)

class PortfolioManager:
    """Portfolio management and database operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
        
    def init_database(self):
        """Verify unified database connection - UPDATED FOR PHASE 1"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enable foreign key constraints for unified database
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Verify all required tables exist in futures.db
            required_tables = ['portfolios', 'positions', 'trades', 'portfolio_snapshots', 'contract_specs']
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            missing_tables = [table for table in required_tables if table not in existing_tables]
            if missing_tables:
                raise ValueError(f"Missing required tables in unified database: {missing_tables}")
            
            # Verify contract specs exist for MCL and MES
            cursor.execute("SELECT symbol FROM contract_specs WHERE symbol IN ('MCL', 'MES')")
            futures_symbols = [row[0] for row in cursor.fetchall()]
            
            if 'MCL' not in futures_symbols or 'MES' not in futures_symbols:
                logger.warning("MCL or MES contract specifications missing - Phase 2 PyBroker integration may fail")
            
            conn.close()
            logger.info(f"Portfolio Service connected to unified database: {self.db_path}")
            logger.info(f"Available tables: {existing_tables}")
            logger.info(f"Available futures contracts: {futures_symbols}")
            
        except Exception as e:
            logger.error(f"Unified database connection failed: {e}")
            raise
    
    def create_portfolio(self, name: str, initial_cash: float) -> str:
        """Create a new portfolio"""
        portfolio_id = generate_id("port")
        timestamp = datetime.now(timezone.utc).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO portfolios (id, name, initial_cash, current_cash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (portfolio_id, name, initial_cash, initial_cash, timestamp, timestamp))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created portfolio {portfolio_id} with ${initial_cash:,.2f}")
            return portfolio_id
            
        except Exception as e:
            logger.error(f"Failed to create portfolio: {e}")
            raise
    
    def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """Get portfolio by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, initial_cash, current_cash, created_at, updated_at
                FROM portfolios WHERE id = ?
            """, (portfolio_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'initial_cash': row[2],
                    'current_cash': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            return None
            
        except Exception as e:
            logger.error(f"Failed to get portfolio {portfolio_id}: {e}")
            raise
    
    def record_trade(self, portfolio_id: str, symbol: str, action: str, 
                    quantity: int, price: float, strategy_name: str = None) -> str:
        """Record a trade and update positions"""
        trade_id = generate_id("trade")
        timestamp = datetime.now(timezone.utc).isoformat()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calculate commission (simplified)
            commission = abs(quantity * price * 0.001)  # 0.1% commission
            
            # Record the trade
            cursor.execute("""
                INSERT INTO trades (id, portfolio_id, symbol, action, quantity, price, timestamp, strategy_name, commission)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (trade_id, portfolio_id, symbol, action, quantity, price, timestamp, strategy_name, commission))
            
            # Update positions
            self._update_position(cursor, portfolio_id, symbol, action, quantity, price)
            
            # Update cash balance
            cash_change = -(quantity * price + commission) if action in ['BUY'] else (quantity * price - commission)
            cursor.execute("""
                UPDATE portfolios 
                SET current_cash = current_cash + ?, updated_at = ?
                WHERE id = ?
            """, (cash_change, timestamp, portfolio_id))
            
            conn.commit()
            conn.close()
            
            # Publish trade to Redis
            self._publish_trade_event(portfolio_id, trade_id, symbol, action, quantity, price)
            
            logger.info(f"Recorded trade {trade_id}: {action} {quantity} {symbol} @ ${price:.2f}")
            return trade_id
            
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
            raise
    
    def _update_position(self, cursor, portfolio_id: str, symbol: str, 
                        action: str, quantity: int, price: float):
        """Update position after trade"""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Get current position
        cursor.execute("""
            SELECT quantity, avg_price FROM positions 
            WHERE portfolio_id = ? AND symbol = ?
        """, (portfolio_id, symbol))
        
        current_pos = cursor.fetchone()
        
        if action in ['BUY']:
            if current_pos:
                # Update existing position
                current_qty, current_avg = current_pos
                new_qty = current_qty + quantity
                new_avg = ((current_qty * current_avg) + (quantity * price)) / new_qty
                
                cursor.execute("""
                    UPDATE positions 
                    SET quantity = ?, avg_price = ?, timestamp = ?
                    WHERE portfolio_id = ? AND symbol = ?
                """, (new_qty, new_avg, timestamp, portfolio_id, symbol))
            else:
                # Create new position
                cursor.execute("""
                    INSERT INTO positions (portfolio_id, symbol, quantity, avg_price, timestamp)
                    VALUES (?, ?, ?, ?, ?)
                """, (portfolio_id, symbol, quantity, price, timestamp))
        
        elif action in ['SELL', 'CLOSE_LONG', 'CLOSE_SHORT']:
            if current_pos:
                current_qty, current_avg = current_pos
                new_qty = current_qty - quantity
                
                if new_qty <= 0:
                    # Close position
                    cursor.execute("""
                        DELETE FROM positions 
                        WHERE portfolio_id = ? AND symbol = ?
                    """, (portfolio_id, symbol))
                else:
                    # Reduce position
                    cursor.execute("""
                        UPDATE positions 
                        SET quantity = ?, timestamp = ?
                        WHERE portfolio_id = ? AND symbol = ?
                    """, (new_qty, timestamp, portfolio_id, symbol))
    
    @retry_with_backoff(REDIS_RETRY_CONFIG)
    def _publish_trade_event(self, portfolio_id: str, trade_id: str, symbol: str, 
                           action: str, quantity: int, price: float):
        """Publish trade event to Redis"""
        try:
            event = {
                'event_type': 'trade_executed',
                'portfolio_id': portfolio_id,
                'trade_id': trade_id,
                'symbol': symbol,
                'action': action,
                'quantity': quantity,
                'price': price,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            redis_client.publish('portfolio:trades', event)
            
        except Exception as e:
            logger.warning(f"Failed to publish trade event: {e}")
    
    def get_positions(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """Get current positions for portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # UPDATED FOR PHASE 1: Enhanced position schema with futures fields
            cursor.execute("""
                SELECT symbol, quantity, avg_price, current_price, unrealized_pnl, 
                       margin_requirement, contract_size, tick_size, timestamp
                FROM positions WHERE portfolio_id = ?
                ORDER BY symbol
            """, (portfolio_id,))
            
            positions = []
            for row in cursor.fetchall():
                positions.append({
                    'symbol': row[0],
                    'quantity': row[1],
                    'avg_price': row[2],
                    'current_price': row[3],
                    'unrealized_pnl': row[4],
                    'margin_requirement': row[5],
                    'contract_size': row[6],
                    'tick_size': row[7],
                    'timestamp': row[8]
                })
            
            conn.close()
            return positions
            
        except Exception as e:
            logger.error(f"Failed to get positions for {portfolio_id}: {e}")
            raise
    
    def get_trades(self, portfolio_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get trade history for portfolio"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, symbol, action, quantity, price, timestamp, strategy_name, pnl, commission
                FROM trades WHERE portfolio_id = ?
                ORDER BY timestamp DESC LIMIT ?
            """, (portfolio_id, limit))
            
            trades = []
            for row in cursor.fetchall():
                trades.append({
                    'trade_id': row[0],
                    'symbol': row[1],
                    'action': row[2],
                    'quantity': row[3],
                    'price': row[4],
                    'timestamp': row[5],
                    'strategy_name': row[6],
                    'pnl': row[7],
                    'commission': row[8]
                })
            
            conn.close()
            return trades
            
        except Exception as e:
            logger.error(f"Failed to get trades for {portfolio_id}: {e}")
            raise
    
    def calculate_equity_curve(self, portfolio_id: str) -> Dict[str, Any]:
        """Calculate equity curve and portfolio metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get portfolio info
            portfolio = self.get_portfolio(portfolio_id)
            if not portfolio:
                raise ValueError(f"Portfolio {portfolio_id} not found")
            
            # Calculate current portfolio value
            cursor.execute("""
                SELECT COALESCE(SUM(quantity * avg_price), 0) as positions_value
                FROM positions WHERE portfolio_id = ?
            """, (portfolio_id,))
            
            positions_value = cursor.fetchone()[0] or 0
            cash_balance = portfolio['current_cash']
            total_value = cash_balance + positions_value
            
            # Calculate total PnL
            total_pnl = total_value - portfolio['initial_cash']
            total_return_pct = (total_pnl / portfolio['initial_cash']) * 100
            
            # Get trade statistics
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(pnl), 0), COALESCE(SUM(commission), 0)
                FROM trades WHERE portfolio_id = ?
            """, (portfolio_id,))
            
            trade_count, total_trade_pnl, total_commission = cursor.fetchone()
            
            # Create snapshot
            snapshot_id = generate_id("snap")
            timestamp = datetime.now(timezone.utc).isoformat()
            
            cursor.execute("""
                INSERT INTO portfolio_snapshots 
                (id, portfolio_id, timestamp, total_value, cash_balance, positions_value, total_pnl)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (snapshot_id, portfolio_id, timestamp, total_value, cash_balance, positions_value, total_pnl))
            
            conn.commit()
            conn.close()
            
            equity_curve = {
                'portfolio_id': portfolio_id,
                'portfolio_name': portfolio['name'],
                'timestamp': timestamp,
                'initial_cash': portfolio['initial_cash'],
                'current_cash': cash_balance,
                'positions_value': positions_value,
                'total_value': total_value,
                'total_pnl': total_pnl,
                'total_return_pct': total_return_pct,
                'total_trades': trade_count,
                'total_commission': total_commission,
                'snapshot_id': snapshot_id
            }
            
            return equity_curve
            
        except Exception as e:
            logger.error(f"Failed to calculate equity curve for {portfolio_id}: {e}")
            raise
    
    def list_portfolios(self) -> List[Dict[str, Any]]:
        """List all portfolios"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, initial_cash, current_cash, created_at, updated_at
                FROM portfolios ORDER BY created_at DESC
            """)
            
            portfolios = []
            for row in cursor.fetchall():
                portfolios.append({
                    'id': row[0],
                    'name': row[1],
                    'initial_cash': row[2],
                    'current_cash': row[3],
                    'created_at': row[4],
                    'updated_at': row[5]
                })
            
            conn.close()
            return portfolios
            
        except Exception as e:
            logger.error(f"Failed to list portfolios: {e}")
            raise

# Initialize portfolio manager
portfolio_manager = PortfolioManager()

# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Service health check"""
    try:
        # Test database connection
        conn = sqlite3.connect(portfolio_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM portfolios")
        portfolio_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades")
        trade_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM positions")
        position_count = cursor.fetchone()[0]
        
        conn.close()
        
        return HealthResponse(
            status=ServiceStatus.HEALTHY,
            service="PortfolioService",
            details={
                "database_status": "healthy",
                "portfolios": portfolio_count,
                "total_trades": trade_count,
                "active_positions": position_count,
                "database_path": str(portfolio_manager.db_path)
            }
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthResponse(
            status=ServiceStatus.UNHEALTHY,
            service="PortfolioService",
            details={"error": str(e)}
        )

@app.post("/api/portfolio")
async def create_portfolio(name: str, initial_cash: float = 100000):
    """Create a new portfolio"""
    try:
        if initial_cash <= 0:
            raise HTTPException(status_code=400, detail="Initial cash must be positive")
        
        portfolio_id = portfolio_manager.create_portfolio(name, initial_cash)
        
        return {
            "status": "success",
            "portfolio_id": portfolio_id,
            "name": name,
            "initial_cash": initial_cash,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Create portfolio error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/{portfolio_id}")
async def get_portfolio(portfolio_id: str):
    """Get portfolio by ID"""
    try:
        portfolio = portfolio_manager.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return {"status": "success", "portfolio": portfolio}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get portfolio error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolios")
async def list_portfolios():
    """List all portfolios"""
    try:
        portfolios = portfolio_manager.list_portfolios()
        return {"status": "success", "portfolios": portfolios}
        
    except Exception as e:
        logger.error(f"List portfolios error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio/{portfolio_id}/trade")
async def record_trade(
    portfolio_id: str,
    symbol: str,
    action: str,
    quantity: int,
    price: float,
    strategy_name: str = None
):
    """Record a trade"""
    try:
        if action not in ['BUY', 'SELL', 'CLOSE_LONG', 'CLOSE_SHORT']:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be positive")
        
        if price <= 0:
            raise HTTPException(status_code=400, detail="Price must be positive")
        
        # Check portfolio exists
        portfolio = portfolio_manager.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        trade_id = portfolio_manager.record_trade(
            portfolio_id, symbol, action, quantity, price, strategy_name
        )
        
        return {
            "status": "success",
            "trade_id": trade_id,
            "portfolio_id": portfolio_id,
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": price,
            "strategy_name": strategy_name,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record trade error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/{portfolio_id}/positions")
async def get_positions(portfolio_id: str):
    """Get current positions"""
    try:
        # Check portfolio exists
        portfolio = portfolio_manager.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        positions = portfolio_manager.get_positions(portfolio_id)
        
        return {
            "status": "success",
            "portfolio_id": portfolio_id,
            "positions": positions,
            "position_count": len(positions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get positions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/{portfolio_id}/trades")
async def get_trades(portfolio_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Get trade history"""
    try:
        # Check portfolio exists
        portfolio = portfolio_manager.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        trades = portfolio_manager.get_trades(portfolio_id, limit)
        
        return {
            "status": "success",
            "portfolio_id": portfolio_id,
            "trades": trades,
            "trade_count": len(trades)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get trades error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/portfolio/{portfolio_id}/equity-curve")
async def get_equity_curve(portfolio_id: str):
    """Get equity curve and portfolio performance"""
    try:
        # Check portfolio exists
        portfolio = portfolio_manager.get_portfolio(portfolio_id)
        if not portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        equity_curve = portfolio_manager.calculate_equity_curve(portfolio_id)
        
        return {"status": "success", "equity_curve": equity_curve}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get equity curve error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Get service statistics"""
    try:
        conn = sqlite3.connect(portfolio_manager.db_path)
        cursor = conn.cursor()
        
        # Get comprehensive stats
        cursor.execute("SELECT COUNT(*) FROM portfolios")
        total_portfolios = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM positions")
        active_positions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM portfolio_snapshots")
        total_snapshots = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COALESCE(SUM(initial_cash), 0), COALESCE(SUM(current_cash), 0)
            FROM portfolios
        """)
        
        total_initial_cash, total_current_cash = cursor.fetchone()
        
        conn.close()
        
        return {
            "status": "success",
            "statistics": {
                "total_portfolios": total_portfolios,
                "total_trades": total_trades,
                "active_positions": active_positions,
                "total_snapshots": total_snapshots,
                "total_initial_cash": total_initial_cash or 0,
                "total_current_cash": total_current_cash or 0,
                "database_size_mb": round(DATABASE_PATH.stat().st_size / (1024 * 1024), 2) if DATABASE_PATH.exists() else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Start Portfolio Service"""
    logger.info("Portfolio Service v1.0")
    logger.info(f"Database: {DATABASE_PATH}")
    logger.info(f"Starting Portfolio Service on port {SERVICE_PORTS['portfolio']}...")
    
    uvicorn.run(
        app,
        host="localhost",
        port=SERVICE_PORTS['portfolio'],
        log_level="info"
    )

if __name__ == "__main__":
    main()