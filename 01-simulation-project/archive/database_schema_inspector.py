#!/usr/bin/env python3
"""
Database Schema Inspector
Examine current database schemas before migration
"""

import sqlite3
import sys
from pathlib import Path

def inspect_database(db_path: str, db_name: str):
    """Inspect database schema and data"""
    print(f"\n=== {db_name} Database Schema ===")
    print(f"Path: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Tables: {[table[0] for table in tables]}")
        
        for table in tables:
            table_name = table[0]
            if table_name == 'sqlite_sequence':
                continue
                
            print(f"\n--- Table: {table_name} ---")
            
            # Get schema
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Columns:")
            for col in columns:
                print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else 'NULL'} {'PK' if col[5] else ''}")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Row count: {count}")
            
            # Show sample data if exists
            if count > 0:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                rows = cursor.fetchall()
                print("Sample data:")
                for row in rows:
                    print(f"  {row}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error inspecting {db_name}: {e}")

def main():
    """Main inspector"""
    data_dir = Path(__file__).parent / "data"
    
    # Inspect futures.db
    futures_db = data_dir / "futures.db"
    if futures_db.exists():
        inspect_database(str(futures_db), "futures.db")
    else:
        print("futures.db not found")
    
    # Inspect portfolio.db  
    portfolio_db = data_dir / "portfolio.db"
    if portfolio_db.exists():
        inspect_database(str(portfolio_db), "portfolio.db")
    else:
        print("portfolio.db not found")

if __name__ == "__main__":
    main()