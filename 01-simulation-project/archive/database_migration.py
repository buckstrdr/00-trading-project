#!/usr/bin/env python3
"""
Database Migration Script - Phase 1
Migrate portfolio tables from portfolio.db to futures.db
Create unified database with proper foreign key relationships
"""

import sqlite3
import sys
from pathlib import Path
from datetime import datetime, timezone

def create_unified_schema(futures_db_path: str):
    """Create unified schema in futures.db with portfolio tables"""
    print(f"Creating unified schema in {futures_db_path}...")
    
    conn = sqlite3.connect(futures_db_path)
    cursor = conn.cursor()
    
    # Enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Create portfolios table (enhanced version with futures integration)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                initial_cash REAL NOT NULL,
                current_cash REAL NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        print("   SUCCESS: Created portfolios table")
        
        # Create positions table with futures enhancements
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                portfolio_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                current_price REAL DEFAULT 0,
                unrealized_pnl REAL DEFAULT 0,
                margin_requirement REAL DEFAULT 0,
                contract_size INTEGER DEFAULT 1,
                tick_size REAL DEFAULT 0.01,
                timestamp TEXT NOT NULL,
                PRIMARY KEY (portfolio_id, symbol),
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
                FOREIGN KEY (symbol) REFERENCES contract_specs(symbol)
            )
        """)
        print("   SUCCESS: Created positions table with futures integration")
        
        # Create trades table 
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                portfolio_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,  -- BUY, SELL, CLOSE_LONG, CLOSE_SHORT
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                timestamp TEXT NOT NULL,
                strategy_name TEXT,
                pnl REAL DEFAULT 0,
                commission REAL DEFAULT 0,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id),
                FOREIGN KEY (symbol) REFERENCES contract_specs(symbol)
            )
        """)
        print("   SUCCESS: Created trades table")
        
        # Create portfolio snapshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id TEXT PRIMARY KEY,
                portfolio_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                total_value REAL NOT NULL,
                cash_balance REAL NOT NULL,
                positions_value REAL NOT NULL,
                total_pnl REAL NOT NULL,
                daily_return REAL DEFAULT 0,
                cumulative_return REAL DEFAULT 0,
                FOREIGN KEY (portfolio_id) REFERENCES portfolios(id)
            )
        """)
        print("   SUCCESS: Created portfolio_snapshots table")
        
        # Add contract specifications for futures we'll be using
        # Check if MCL and MES already exist
        cursor.execute("SELECT symbol FROM contract_specs WHERE symbol IN ('MCL', 'MES')")
        existing_symbols = [row[0] for row in cursor.fetchall()]
        
        # Add MCL (Micro WTI Crude Oil) if not exists
        if 'MCL' not in existing_symbols:
            cursor.execute("""
                INSERT INTO contract_specs (symbol, name, tick_size, tick_value, contract_size, margin_requirement, currency, exchange, created_at)
                VALUES ('MCL', 'Micro WTI Crude Oil', 0.01, 1.00, 100, 666.0, 'USD', 'NYMEX', ?)
            """, (datetime.now(timezone.utc).isoformat(),))
            print("   SUCCESS: Added MCL contract specification")
        
        # Add MES (Micro E-mini S&P 500) if not exists  
        if 'MES' not in existing_symbols:
            cursor.execute("""
                INSERT INTO contract_specs (symbol, name, tick_size, tick_value, contract_size, margin_requirement, currency, exchange, created_at)
                VALUES ('MES', 'Micro E-mini S&P 500', 0.25, 1.25, 1, 2455.0, 'USD', 'CME', ?)
            """, (datetime.now(timezone.utc).isoformat(),))
            print("   SUCCESS: Added MES contract specification")
        
        conn.commit()
        print("   SUCCESS: Schema creation completed successfully")
        
    except Exception as e:
        conn.rollback()
        print(f"   ERROR: Schema creation failed: {e}")
        raise
    finally:
        conn.close()

def migrate_portfolio_data(portfolio_db_path: str, futures_db_path: str):
    """Migrate data from portfolio.db to futures.db"""
    print(f"Migrating data from {portfolio_db_path} to {futures_db_path}...")
    
    # Connect to both databases
    portfolio_conn = sqlite3.connect(portfolio_db_path)
    futures_conn = sqlite3.connect(futures_db_path)
    
    portfolio_cursor = portfolio_conn.cursor()
    futures_cursor = futures_conn.cursor()
    
    # Enable foreign key constraints
    futures_cursor.execute("PRAGMA foreign_keys = ON")
    
    try:
        # Migrate portfolios
        print("   Migrating portfolios...")
        portfolio_cursor.execute("SELECT * FROM portfolios")
        portfolios = portfolio_cursor.fetchall()
        
        for portfolio in portfolios:
            futures_cursor.execute("""
                INSERT OR REPLACE INTO portfolios 
                (id, name, initial_cash, current_cash, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, portfolio)
        print(f"   SUCCESS: Migrated {len(portfolios)} portfolios")
        
        # Migrate positions
        print("   Migrating positions...")
        portfolio_cursor.execute("SELECT * FROM positions")
        positions = portfolio_cursor.fetchall()
        
        for position in positions:
            # Original: (portfolio_id, symbol, quantity, avg_price, current_value, unrealized_pnl, timestamp)
            # New: (portfolio_id, symbol, quantity, avg_price, current_price, unrealized_pnl, margin_requirement, contract_size, tick_size, timestamp)
            futures_cursor.execute("""
                INSERT OR REPLACE INTO positions 
                (portfolio_id, symbol, quantity, avg_price, current_price, unrealized_pnl, margin_requirement, contract_size, tick_size, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, 0, 1, 0.01, ?)
            """, (position[0], position[1], position[2], position[3], position[4], position[5], position[6]))
        print(f"   SUCCESS: Migrated {len(positions)} positions")
        
        # Migrate trades
        print("   Migrating trades...")
        portfolio_cursor.execute("SELECT * FROM trades")
        trades = portfolio_cursor.fetchall()
        
        for trade in trades:
            futures_cursor.execute("""
                INSERT OR REPLACE INTO trades 
                (id, portfolio_id, symbol, action, quantity, price, timestamp, strategy_name, pnl, commission)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, trade)
        print(f"   SUCCESS: Migrated {len(trades)} trades")
        
        # Migrate portfolio snapshots
        print("   Migrating portfolio snapshots...")
        portfolio_cursor.execute("SELECT * FROM portfolio_snapshots")
        snapshots = portfolio_cursor.fetchall()
        
        for snapshot in snapshots:
            futures_cursor.execute("""
                INSERT OR REPLACE INTO portfolio_snapshots 
                (id, portfolio_id, timestamp, total_value, cash_balance, positions_value, total_pnl, daily_return, cumulative_return)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, snapshot)
        print(f"   SUCCESS: Migrated {len(snapshots)} portfolio snapshots")
        
        futures_conn.commit()
        print("   SUCCESS: Data migration completed successfully")
        
    except Exception as e:
        futures_conn.rollback()
        print(f"   ERROR: Data migration failed: {e}")
        raise
    finally:
        portfolio_conn.close()
        futures_conn.close()

def validate_migration(futures_db_path: str):
    """Validate the migration was successful"""
    print(f"Validating migration in {futures_db_path}...")
    
    conn = sqlite3.connect(futures_db_path)
    cursor = conn.cursor()
    
    try:
        # Check all expected tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['market_data', 'contract_specs', 'portfolios', 'positions', 'trades', 'portfolio_snapshots']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            raise ValueError(f"Missing tables: {missing_tables}")
        print("   SUCCESS: All required tables present")
        
        # Check data counts
        for table in ['portfolios', 'positions', 'trades', 'portfolio_snapshots']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   {table}: {count} records")
        
        # Validate foreign key relationships
        cursor.execute("PRAGMA foreign_key_check")
        fk_violations = cursor.fetchall()
        
        if fk_violations:
            raise ValueError(f"Foreign key violations: {fk_violations}")
        print("   SUCCESS: Foreign key constraints validated")
        
        print("   SUCCESS: Migration validation completed successfully")
        
    except Exception as e:
        print(f"   ERROR: Migration validation failed: {e}")
        raise
    finally:
        conn.close()

def main():
    """Main migration entry point"""
    print("Phase 1: Database Migration Starting")
    print("=" * 50)
    
    data_dir = Path(__file__).parent / "data"
    portfolio_db = data_dir / "portfolio.db"
    futures_db = data_dir / "futures.db"
    
    if not portfolio_db.exists():
        print(f"ERROR: portfolio.db not found at {portfolio_db}")
        return False
        
    if not futures_db.exists():
        print(f"ERROR: futures.db not found at {futures_db}")
        return False
    
    try:
        # Step 1: Create unified schema
        create_unified_schema(str(futures_db))
        
        # Step 2: Migrate data
        migrate_portfolio_data(str(portfolio_db), str(futures_db))
        
        # Step 3: Validate migration
        validate_migration(str(futures_db))
        
        print("\nDatabase migration completed successfully!")
        print("Portfolio data now unified in futures.db")
        print("Foreign key relationships established")
        print("Enhanced schema ready for PyBroker integration")
        
        return True
        
    except Exception as e:
        print(f"\nMigration failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)