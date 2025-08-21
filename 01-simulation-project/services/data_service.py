#!/usr/bin/env python3
"""
Data Service - Market Data Management
Port: 8001
Purpose: Handle market data import, storage, and serving
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

import sqlite3
import pandas as pd
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import shared utilities
from shared.redis_client import redis_client
from shared.models import HealthResponse, ServiceStatus, MarketDataRequest, ContractSpec
from shared.utils import setup_logging, Timer
from config.settings import (
    DATABASE_URL, DATA_DIR, SERVICE_PORTS, 
    DEFAULT_COMMISSION, DEFAULT_SLIPPAGE
)

# Set up logging
logger = setup_logging("DataService", "INFO")

class DataService:
    """Market data management service"""
    
    def __init__(self):
        self.app = FastAPI(
            title="Data Service",
            description="Market data management for futures backtesting",
            version="1.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Database connection
        self.db_path = DATA_DIR / "futures.db"
        
        # Initialize database on startup
        self.setup_database()
        
        # Set up API routes
        self.setup_routes()
        
        logger.info(f"Data Service initialized with database: {self.db_path}")
    
    def setup_database(self):
        """Initialize SQLite database with required tables"""
        logger.info("Setting up database schema...")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create market_data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol VARCHAR(10) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    open REAL NOT NULL,
                    high REAL NOT NULL,
                    low REAL NOT NULL,
                    close REAL NOT NULL,
                    volume INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, timestamp)
                )
            """)
            
            # Create contract_specs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contract_specs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    tick_size REAL NOT NULL,
                    tick_value REAL NOT NULL,
                    contract_size INTEGER NOT NULL,
                    margin_requirement REAL NOT NULL,
                    currency VARCHAR(3) DEFAULT 'USD',
                    exchange VARCHAR(20) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
                ON market_data(symbol, timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_market_data_timestamp 
                ON market_data(timestamp)
            """)
            
            conn.commit()
            
            # Insert default contract specifications
            self.insert_default_contracts(cursor)
            conn.commit()
            
            conn.close()
            logger.info("✅ Database schema created successfully")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def insert_default_contracts(self, cursor):
        """Insert default futures contract specifications"""
        default_contracts = [
            # ES - S&P 500 E-mini
            ('ES', 'S&P 500 E-mini', 0.25, 12.50, 50, 0.05, 'USD', 'CME'),
            # NQ - NASDAQ 100 E-mini  
            ('NQ', 'NASDAQ 100 E-mini', 0.25, 5.00, 20, 0.08, 'USD', 'CME'),
            # CL - Crude Oil
            ('CL', 'Light Sweet Crude Oil', 0.01, 10.00, 1000, 0.10, 'USD', 'NYMEX'),
            # GC - Gold
            ('GC', 'Gold', 0.10, 10.00, 100, 0.05, 'USD', 'COMEX'),
            # ZB - 30-Year Treasury Bond
            ('ZB', '30-Year Treasury Bond', 0.03125, 31.25, 100000, 0.03, 'USD', 'CBOT')
        ]
        
        for contract in default_contracts:
            cursor.execute("""
                INSERT OR IGNORE INTO contract_specs 
                (symbol, name, tick_size, tick_value, contract_size, margin_requirement, currency, exchange)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, contract)
            
        logger.info(f"✅ Inserted {len(default_contracts)} default contract specifications")
    
    def setup_routes(self):
        """Set up FastAPI routes"""
        
        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint"""
            try:
                # Test database connection
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM market_data")
                data_count = cursor.fetchone()[0]
                conn.close()
                
                # Test Redis connection
                redis_healthy = redis_client.health_check()
                
                return HealthResponse(
                    status=ServiceStatus.HEALTHY,
                    service="DataService",
                    details={
                        "database_records": data_count,
                        "redis_connected": redis_healthy,
                        "database_path": str(self.db_path)
                    }
                )
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return HealthResponse(
                    status=ServiceStatus.UNHEALTHY,
                    service="DataService",
                    details={"error": str(e)}
                )
        
        @self.app.get("/api/data/{symbol}")
        async def get_market_data(
            symbol: str,
            start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
            end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
            limit: Optional[int] = Query(1000, description="Maximum number of records")
        ):
            """Get market data for a symbol"""
            try:
                with Timer(f"Fetching data for {symbol}"):
                    conn = sqlite3.connect(self.db_path)
                    
                    # Build query
                    query = "SELECT * FROM market_data WHERE symbol = ?"
                    params = [symbol.upper()]
                    
                    if start_date:
                        query += " AND timestamp >= ?"
                        params.append(start_date)
                    
                    if end_date:
                        query += " AND timestamp <= ?"
                        params.append(end_date)
                    
                    query += " ORDER BY timestamp DESC"
                    
                    if limit:
                        query += " LIMIT ?"
                        params.append(limit)
                    
                    # Execute query
                    df = pd.read_sql(query, conn, params=params)
                    conn.close()
                    
                    if df.empty:
                        # Return empty data with 200 status instead of 404 error
                        logger.info(f"📊 No data found for symbol {symbol}, returning empty result")
                        return {
                            "status": "success",
                            "symbol": symbol,
                            "data": [],
                            "record_count": 0,
                            "date_range": {
                                "start": start_date,
                                "end": end_date
                            }
                        }
                    
                    # Convert to records and return
                    records = df.to_dict('records')
                    
                    # Publish data request to Redis for other services
                    redis_client.publish('data:requests', {
                        'action': 'data_served',
                        'symbol': symbol,
                        'records': len(records),
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    logger.info(f"📊 Served {len(records)} records for {symbol}")
                    
                    return {
                        "symbol": symbol,
                        "records": len(records),
                        "start_date": start_date,
                        "end_date": end_date,
                        "data": records
                    }
                    
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/contracts")
        async def get_contracts():
            """Get all contract specifications"""
            try:
                conn = sqlite3.connect(self.db_path)
                df = pd.read_sql("SELECT * FROM contract_specs ORDER BY symbol", conn)
                conn.close()
                
                if df.empty:
                    return {"contracts": []}
                
                contracts = df.to_dict('records')
                logger.info(f"📋 Served {len(contracts)} contract specifications")
                
                return {"contracts": contracts}
                
            except Exception as e:
                logger.error(f"Error fetching contracts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/contracts/{symbol}")
        async def get_contract(symbol: str):
            """Get contract specification for a symbol"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM contract_specs WHERE symbol = ?", (symbol.upper(),))
                result = cursor.fetchone()
                conn.close()
                
                if not result:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Contract specification not found for {symbol}"
                    )
                
                # Convert to dictionary
                columns = [desc[0] for desc in cursor.description]
                contract = dict(zip(columns, result))
                
                logger.info(f"📋 Served contract specification for {symbol}")
                
                return {"contract": contract}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error fetching contract {symbol}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/data/import")
        async def import_data(
            symbol: str,
            data: List[Dict[str, Any]]
        ):
            """Import market data from API call"""
            try:
                if not data:
                    raise HTTPException(status_code=400, detail="No data provided")
                
                # Validate data format
                required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                for record in data[:3]:  # Check first 3 records
                    missing = [field for field in required_fields if field not in record]
                    if missing:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Missing required fields: {missing}"
                        )
                
                # Import to database
                imported_count = await self.import_records(symbol.upper(), data)
                
                # Notify other services
                redis_client.publish('data:updates', {
                    'action': 'data_imported',
                    'symbol': symbol.upper(),
                    'records': imported_count,
                    'timestamp': datetime.now().isoformat()
                })
                
                logger.info(f"📥 Imported {imported_count} records for {symbol}")
                
                return {
                    "symbol": symbol.upper(),
                    "imported_records": imported_count,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error importing data for {symbol}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/stats")
        async def get_stats():
            """Get database statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get record counts by symbol
                cursor.execute("""
                    SELECT symbol, COUNT(*) as record_count, 
                           MIN(timestamp) as earliest_date,
                           MAX(timestamp) as latest_date
                    FROM market_data 
                    GROUP BY symbol 
                    ORDER BY symbol
                """)
                
                symbol_stats = []
                for row in cursor.fetchall():
                    symbol_stats.append({
                        'symbol': row[0],
                        'record_count': row[1],
                        'earliest_date': row[2],
                        'latest_date': row[3]
                    })
                
                # Get total records
                cursor.execute("SELECT COUNT(*) FROM market_data")
                total_records = cursor.fetchone()[0]
                
                # Get contract count
                cursor.execute("SELECT COUNT(*) FROM contract_specs")
                total_contracts = cursor.fetchone()[0]
                
                conn.close()
                
                return {
                    "total_records": total_records,
                    "total_contracts": total_contracts,
                    "symbol_stats": symbol_stats,
                    "database_size_mb": round(self.db_path.stat().st_size / 1024 / 1024, 2)
                }
                
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/database/info")
        async def get_database_info():
            """Get detailed database information and statistics"""
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Get basic database info
                db_file_size = self.db_path.stat().st_size / 1024 / 1024  # MB
                
                # Get table info
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Get total records
                cursor.execute("SELECT COUNT(*) FROM market_data")
                total_records = cursor.fetchone()[0]
                
                # Get available symbols
                cursor.execute("SELECT DISTINCT symbol FROM market_data ORDER BY symbol")
                symbols = [row[0] for row in cursor.fetchall()]
                
                # Get date range
                cursor.execute("SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest FROM market_data")
                date_range = cursor.fetchone()
                
                conn.close()
                
                return {
                    "status": "success",
                    "database_info": {
                        "path": str(self.db_path),
                        "size_mb": round(db_file_size, 2),
                        "tables": len(tables),
                        "total_records": total_records,
                        "symbols": symbols,
                        "date_range": {
                            "earliest": date_range[0],
                            "latest": date_range[1]
                        }
                    }
                }
                
            except Exception as e:
                logger.error(f"Error getting database info: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def import_records(self, symbol: str, data: List[Dict[str, Any]]) -> int:
        """Import market data records to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            imported_count = 0
            for record in data:
                try:
                    cursor.execute("""
                        INSERT OR REPLACE INTO market_data 
                        (symbol, timestamp, open, high, low, close, volume)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        symbol,
                        record['timestamp'],
                        float(record['open']),
                        float(record['high']),
                        float(record['low']),
                        float(record['close']),
                        int(record['volume'])
                    ))
                    imported_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import record: {record} - {e}")
                    continue
            
            conn.commit()
            conn.close()
            
            return imported_count
            
        except Exception as e:
            logger.error(f"Database import error: {e}")
            raise
    
    def run(self, host="0.0.0.0", port=8001):
        """Run the data service"""
        logger.info(f"🚀 Starting Data Service on {host}:{port}")
        
        # Test Redis connection on startup
        if redis_client.health_check():
            logger.info("✅ Redis connection verified")
        else:
            logger.warning("⚠️ Redis connection failed - service will continue without pub/sub")
        
        # Run the service
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )

def main():
    """Main entry point"""
    service = DataService()
    service.run(port=SERVICE_PORTS['data'])

if __name__ == "__main__":
    main()