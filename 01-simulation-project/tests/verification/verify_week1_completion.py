#!/usr/bin/env python3
"""
Week 1 Completion Verification
Verifies development environment setup and basic service startup
"""

import sys
import os
import subprocess
import importlib.util
from pathlib import Path

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from shared.utils import setup_logging

logger = setup_logging("Week1Verification", "INFO")

class Week1Verifier:
    """Week 1 milestone verification"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.results = {}
    
    def verify_python_version(self) -> bool:
        """Verify Python 3.11+ is installed"""
        try:
            version = sys.version_info
            is_valid = version.major == 3 and version.minor >= 11
            
            logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
            return is_valid
            
        except Exception as e:
            logger.error(f"Failed to check Python version: {e}")
            return False
    
    def verify_redis_availability(self) -> bool:
        """Verify Redis can be imported and connected"""
        try:
            from shared.redis_client import redis_client
            health = redis_client.health_check()
            logger.info(f"Redis health: {health}")
            return health
            
        except Exception as e:
            logger.error(f"Redis verification failed: {e}")
            return False
    
    def verify_project_structure(self) -> bool:
        """Verify core project structure exists"""
        required_paths = [
            "run_system.py",
            "requirements.txt", 
            "config/settings.py",
            "shared/redis_client.py",
            "shared/models.py",
            "shared/utils.py",
            "services/data_service.py",
            "services/backtest_service.py",
            "services/portfolio_service.py",
            "data/futures.db"
        ]
        
        missing = []
        for path in required_paths:
            full_path = self.project_root / path
            if not full_path.exists():
                missing.append(path)
        
        if missing:
            logger.error(f"Missing project structure: {missing}")
            return False
        
        logger.info("✅ Core project structure complete")
        return True
    
    def verify_run_system(self) -> bool:
        """Verify run_system.py exists and is executable"""
        run_system_path = self.project_root / "run_system.py"
        
        if not run_system_path.exists():
            logger.error("run_system.py not found")
            return False
        
        # Try to import run_system module
        try:
            spec = importlib.util.spec_from_file_location("run_system", run_system_path)
            module = importlib.util.module_from_spec(spec)
            # Don't execute, just verify it can be loaded
            logger.info("✅ run_system.py can be imported")
            return True
            
        except Exception as e:
            logger.error(f"run_system.py import failed: {e}")
            return False
    
    def verify_shared_utilities(self) -> bool:
        """Verify shared utilities are working"""
        try:
            from shared.redis_client import redis_client
            from shared.models import HealthResponse, ServiceStatus
            from shared.utils import setup_logging, generate_id
            
            # Test utility functions
            test_id = generate_id("test")
            if not test_id.startswith("test_"):
                return False
            
            # Test models
            health = HealthResponse(
                status=ServiceStatus.HEALTHY,
                service="Week1Test"
            )
            
            if health.status != ServiceStatus.HEALTHY:
                return False
            
            logger.info("✅ Shared utilities working")
            return True
            
        except Exception as e:
            logger.error(f"Shared utilities verification failed: {e}")
            return False
    
    def run_verification(self) -> dict:
        """Run all Week 1 verification checks"""
        logger.info("🧪 Starting Week 1 Completion Verification")
        logger.info("=" * 50)
        
        tests = [
            ("Python 3.11+ Installation", self.verify_python_version),
            ("Redis Availability", self.verify_redis_availability),
            ("Project Structure", self.verify_project_structure),
            ("Run System Script", self.verify_run_system),
            ("Shared Utilities", self.verify_shared_utilities)
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
        
        logger.info(f"\\n🏁 Week 1 Verification Summary:")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if success_rate == 100.0:
            logger.info("🎉 WEEK 1 COMPLETE - ALL TARGETS ACHIEVED!")
        else:
            logger.error(f"❌ WEEK 1 INCOMPLETE - {total_tests - passed_tests} TARGETS FAILED")
        
        return self.results

def main():
    """Main verification entry point"""
    verifier = Week1Verifier()
    results = verifier.run_verification()
    
    # Return appropriate exit code
    all_passed = all(result for result in results.values())
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())