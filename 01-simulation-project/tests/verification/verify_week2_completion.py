#!/usr/bin/env python3
"""
Week 2 Completion Verification
Verifies Data Service foundation and basic data management
"""

import sys
import sqlite3
import requests
from pathlib import Path
from datetime import datetime

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import setup_logging
from config.settings import SERVICE_PORTS, DATA_DIR

logger = setup_logging("Week2Verification", "INFO")

class Week2Verifier:
    """Week 2 milestone verification"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_service_url = f"http://localhost:{SERVICE_PORTS['data']}"
        self.db_path = DATA_DIR / "futures.db"
        self.results = {}
    
    def verify_data_service_api(self) -> bool:
        """Verify Data Service FastAPI is working"""
        try:
            # Test health endpoint
            response = requests.get(f"{self.data_service_url}/health", timeout=5)
            if response.status_code != 200:
                logger.error(f"Data Service health check failed: {response.status_code}")
                return False
            
            health_data = response.json()
            if health_data.get('status') != 'healthy':
                logger.error(f"Data Service not healthy: {health_data}")
                return False
            
            logger.info("✅ Data Service API responding")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Data Service API verification failed: {e}")
            return False
    
    def verify_sqlite_database(self) -> bool:
        """Verify SQLite database exists and has basic schema"""
        try:
            if not self.db_path.exists():
                logger.error(f"Database file not found: {self.db_path}")
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for required tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            required_tables = ['market_data', 'contract_specs']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"Missing required tables: {missing_tables}")
                conn.close()
                return False
            
            # Check if market_data has data
            cursor.execute("SELECT COUNT(*) FROM market_data")
            data_count = cursor.fetchone()[0]
            
            conn.close()
            
            if data_count == 0:
                logger.warning("No market data found in database")
                return False
            
            logger.info(f"✅ SQLite database operational with {data_count} market data records")
            return True
            
        except Exception as e:
            logger.error(f"SQLite database verification failed: {e}")
            return False
    
    def verify_data_import_capability(self) -> bool:
        """Verify data import functionality exists"""
        try:
            from scripts.data_importer import CSVDataImporter
            
            importer = CSVDataImporter()
            
            # Test basic import functionality (without actually importing)
            if hasattr(importer, 'import_csv_file') and hasattr(importer, 'parse_csv_file'):
                logger.info("✅ Data import functionality available")
                return True
            else:
                logger.error("Data import methods not found")
                return False
                
        except Exception as e:
            logger.error(f"Data import verification failed: {e}")
            return False
    
    def verify_data_validation(self) -> bool:
        """Verify data validation checks exist"""
        try:
            # Test Data Service data endpoint
            response = requests.get(
                f"{self.data_service_url}/api/data/MCL",
                params={"start_date": "2024-01-01", "end_date": "2024-01-02"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check data structure
                if isinstance(data, dict) and 'data' in data:
                    sample_data = data['data']
                    if len(sample_data) > 0:
                        # Verify required fields exist
                        required_fields = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                        first_record = sample_data[0]
                        
                        missing_fields = [field for field in required_fields if field not in first_record]
                        if missing_fields:
                            logger.error(f"Missing required fields in data: {missing_fields}")
                            return False
                        
                        logger.info("✅ Data validation working - proper data structure")
                        return True
                    
            logger.error("Data validation check failed - no valid data returned")
            return False
            
        except Exception as e:
            logger.error(f"Data validation verification failed: {e}")
            return False
    
    def verify_sample_data(self) -> bool:
        """Verify sample futures data is available"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for futures symbols
            cursor.execute("""
                SELECT symbol, COUNT(*) as record_count
                FROM market_data 
                GROUP BY symbol 
                ORDER BY record_count DESC
                LIMIT 5
            """)
            
            symbols_data = cursor.fetchall()
            conn.close()
            
            if not symbols_data:
                logger.error("No sample futures data found")
                return False
            
            futures_symbols = ['ES', 'MCL', 'MES', 'NQ']  # Common futures symbols
            found_futures = any(symbol[0] in futures_symbols for symbol in symbols_data)
            
            if not found_futures:
                logger.warning(f"No recognized futures symbols found. Available: {[s[0] for s in symbols_data]}")
            
            logger.info(f"✅ Sample data available for symbols: {[f'{s[0]}({s[1]} records)' for s in symbols_data]}")
            return True
            
        except Exception as e:
            logger.error(f"Sample data verification failed: {e}")
            return False
    
    def run_verification(self) -> dict:
        """Run all Week 2 verification checks"""
        logger.info("🧪 Starting Week 2 Completion Verification")
        logger.info("=" * 50)
        
        tests = [
            ("Data Service FastAPI", self.verify_data_service_api),
            ("SQLite Database Setup", self.verify_sqlite_database),
            ("Data Import Capability", self.verify_data_import_capability),
            ("Data Validation Checks", self.verify_data_validation),
            ("Sample Futures Data", self.verify_sample_data)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\\n--- {test_name} ---")
            try:
                result = test_func()
                self.results[test_name] = result
                status = "PASS" if result else "FAIL"
                logger.info(f"{test_name}: {status}")
                
            except Exception as e:
                logger.error(f"{test_name} FAILED with exception: {e}")
                self.results[test_name] = False
        
        # Generate summary
        total_tests = len(tests)
        passed_tests = sum(1 for result in self.results.values() if result)
        success_rate = (passed_tests / total_tests) * 100
        
        logger.info(f"\\n🏁 Week 2 Verification Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            logger.info("🎉 WEEK 2 COMPLETE - DATA SERVICE FOUNDATION SOLID!")
        else:
            logger.error(f"❌ WEEK 2 INCOMPLETE - {total_tests - passed_tests} TARGETS FAILED")
        
        return self.results

def main():
    """Main verification entry point"""
    verifier = Week2Verifier()
    results = verifier.run_verification()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())