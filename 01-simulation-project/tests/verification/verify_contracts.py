#!/usr/bin/env python3
"""Verify MCL and MES contract specifications"""

import sqlite3
from pathlib import Path

def verify_contracts():
    data_dir = Path(__file__).parent / "data"
    futures_db = data_dir / "futures.db"
    
    conn = sqlite3.connect(str(futures_db))
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT symbol, name, tick_size, tick_value, margin_requirement, exchange 
        FROM contract_specs 
        WHERE symbol IN ('MCL', 'MES')
        ORDER BY symbol
    """)
    
    contracts = cursor.fetchall()
    
    print("MCL and MES Contract Verification:")
    print("=" * 50)
    
    for contract in contracts:
        symbol, name, tick_size, tick_value, margin_req, exchange = contract
        print(f"Symbol: {symbol}")
        print(f"Name: {name}")
        print(f"Tick Size: {tick_size}")
        print(f"Tick Value: {tick_value}")
        print(f"Margin Requirement: {margin_req}")
        print(f"Exchange: {exchange}")
        print("-" * 30)
    
    conn.close()
    
    if len(contracts) == 2:
        print("✅ VERIFIED: Both MCL and MES contracts exist")
    else:
        print(f"❌ ISSUE: Expected 2 contracts, found {len(contracts)}")

if __name__ == "__main__":
    verify_contracts()