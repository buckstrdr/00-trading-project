#!/usr/bin/env python3
"""
Service Health Monitor
Monitors health of all microservices and provides comprehensive status reporting
"""

import sys
import requests
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from shared.redis_client import redis_client
from shared.utils import setup_logging, ServiceHealthStatus
from config.settings import SERVICE_PORTS, DATABASE_URL, DATA_DIR

logger = setup_logging("HealthMonitor", "INFO")

class SystemHealthMonitor:
    """Comprehensive system health monitoring"""
    
    def __init__(self):
        self.services = {
            'data_service': {'port': SERVICE_PORTS['data'], 'name': 'Data Service'},
            'backtest_service': {'port': SERVICE_PORTS['backtest'], 'name': 'Backtest Service'},
            'redis': {'port': 6379, 'name': 'Redis Server'},
            'database': {'path': DATA_DIR / "futures.db", 'name': 'SQLite Database'}
        }
        
        # Track service health over time
        self.service_health = {
            service: ServiceHealthStatus(service) 
            for service in self.services.keys()
        }
        
        self.last_check_time = None
        self.check_count = 0
        
    def check_http_service(self, service_name: str, port: int, timeout: float = 5.0) -> Dict[str, Any]:
        """Check health of HTTP service"""
        url = f"http://localhost:{port}"
        
        try:
            # Test health endpoint
            start_time = time.time()
            response = requests.get(f"{url}/health", timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.status_code == 200:
                health_data = response.json()
                self.service_health[service_name].record_success()
                
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'details': health_data.get('details', {}),
                    'service_info': health_data.get('service', service_name),
                    'url': url
                }
            else:
                error_msg = f"HTTP {response.status_code}"
                self.service_health[service_name].record_failure(error_msg)
                return {
                    'status': 'unhealthy',
                    'error': error_msg,
                    'response_time_ms': round(response_time, 2),
                    'url': url
                }
                
        except requests.exceptions.ConnectionError:
            error_msg = "Connection refused - service may not be running"
            self.service_health[service_name].record_failure(error_msg)
            return {
                'status': 'down',
                'error': error_msg,
                'url': url
            }
        except requests.exceptions.Timeout:
            error_msg = f"Timeout after {timeout}s"
            self.service_health[service_name].record_failure(error_msg)
            return {
                'status': 'timeout',
                'error': error_msg,
                'url': url
            }
        except Exception as e:
            error_msg = str(e)
            self.service_health[service_name].record_failure(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'url': url
            }
    
    def check_redis_service(self) -> Dict[str, Any]:
        """Check Redis health"""
        try:
            start_time = time.time()
            
            # Test basic connection
            ping_result = redis_client.client.ping()
            response_time = (time.time() - start_time) * 1000
            
            if ping_result:
                # Get Redis info
                info = redis_client.client.info()
                memory_usage = info.get('used_memory_human', 'Unknown')
                connected_clients = info.get('connected_clients', 0)
                
                # Test pub/sub functionality
                test_channel = "health:test"
                redis_client.client.publish(test_channel, "health_check")
                
                self.service_health['redis'].record_success()
                
                return {
                    'status': 'healthy',
                    'response_time_ms': round(response_time, 2),
                    'details': {
                        'memory_usage': memory_usage,
                        'connected_clients': connected_clients,
                        'version': info.get('redis_version', 'Unknown'),
                        'uptime_seconds': info.get('uptime_in_seconds', 0),
                        'pub_sub_test': 'passed'
                    }
                }
            else:
                error_msg = "Redis ping failed"
                self.service_health['redis'].record_failure(error_msg)
                return {
                    'status': 'unhealthy',
                    'error': error_msg
                }
                
        except Exception as e:
            error_msg = str(e)
            self.service_health['redis'].record_failure(error_msg)
            return {
                'status': 'down',
                'error': error_msg
            }
    
    def check_database(self, db_path: Path) -> Dict[str, Any]:
        """Check SQLite database health"""
        try:
            if not db_path.exists():
                error_msg = f"Database file not found: {db_path}"
                self.service_health['database'].record_failure(error_msg)
                return {
                    'status': 'missing',
                    'error': error_msg,
                    'path': str(db_path)
                }
            
            start_time = time.time()
            
            # Test database connection and queries
            conn = sqlite3.connect(db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # Check tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Get record counts
            table_counts = {}
            for table in tables:
                if table != 'sqlite_sequence':  # Skip internal table
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    table_counts[table] = cursor.fetchone()[0]
            
            # Get database file size
            file_size = db_path.stat().st_size / (1024 * 1024)  # MB
            
            conn.close()
            response_time = (time.time() - start_time) * 1000
            
            self.service_health['database'].record_success()
            
            return {
                'status': 'healthy',
                'response_time_ms': round(response_time, 2),
                'details': {
                    'tables': tables,
                    'record_counts': table_counts,
                    'file_size_mb': round(file_size, 2),
                    'path': str(db_path)
                }
            }
            
        except Exception as e:
            error_msg = str(e)
            self.service_health['database'].record_failure(error_msg)
            return {
                'status': 'error',
                'error': error_msg,
                'path': str(db_path)
            }
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check of all services"""
        self.check_count += 1
        self.last_check_time = datetime.now()
        
        logger.info(f"[HEALTH] Performing health check #{self.check_count}...")
        
        results = {
            'timestamp': self.last_check_time.isoformat(),
            'check_number': self.check_count,
            'services': {}
        }
        
        # Check HTTP services
        for service_key, service_config in self.services.items():
            if 'port' in service_config and service_key not in ['redis', 'database']:
                logger.info(f"   Checking {service_config['name']}...")
                results['services'][service_key] = self.check_http_service(
                    service_key, 
                    service_config['port']
                )
        
        # Check Redis
        logger.info("   Checking Redis Server...")
        results['services']['redis'] = self.check_redis_service()
        
        # Check Database
        logger.info("   Checking SQLite Database...")
        results['services']['database'] = self.check_database(
            self.services['database']['path']
        )
        
        return results
    
    def get_system_summary(self, health_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate system health summary"""
        total_services = len(health_results['services'])
        healthy_services = sum(
            1 for service in health_results['services'].values() 
            if service['status'] == 'healthy'
        )
        
        unhealthy_services = []
        warning_services = []
        
        for service_name, service_health in health_results['services'].items():
            if service_health['status'] != 'healthy':
                service_info = {
                    'name': self.services[service_name]['name'],
                    'status': service_health['status'],
                    'error': service_health.get('error', 'Unknown error')
                }
                
                if service_health['status'] in ['down', 'missing']:
                    unhealthy_services.append(service_info)
                else:
                    warning_services.append(service_info)
        
        health_percentage = (healthy_services / total_services) * 100
        
        # Determine overall system status
        if health_percentage == 100:
            system_status = 'healthy'
            status_emoji = 'HEALTHY'
        elif health_percentage >= 75:
            system_status = 'degraded'
            status_emoji = 'DEGRADED'
        else:
            system_status = 'critical'
            status_emoji = 'CRITICAL'
        
        return {
            'overall_status': system_status,
            'status_emoji': status_emoji,
            'health_percentage': round(health_percentage, 1),
            'total_services': total_services,
            'healthy_services': healthy_services,
            'unhealthy_services': unhealthy_services,
            'warning_services': warning_services,
            'last_check': health_results['timestamp']
        }
    
    def print_health_report(self, health_results: Dict[str, Any]):
        """Print formatted health report"""
        summary = self.get_system_summary(health_results)
        
        print(f"\n{summary['status_emoji']} System Health Report - {summary['last_check']}")
        print("=" * 60)
        print(f"Overall Status: {summary['overall_status'].upper()}")
        print(f"Health Score: {summary['health_percentage']}% ({summary['healthy_services']}/{summary['total_services']} services healthy)")
        
        print(f"\n[SERVICES] Service Details:")
        print("-" * 40)
        
        for service_name, service_health in health_results['services'].items():
            service_config = self.services[service_name]
            status = service_health['status']
            
            # Status indicator
            if status == 'healthy':
                emoji = '[OK]'
            elif status in ['down', 'missing']:
                emoji = '[FAIL]'
            else:
                emoji = '[WARN]'
            
            print(f"{emoji} {service_config['name']:<20} {status.upper()}")
            
            # Show additional details
            if 'response_time_ms' in service_health:
                print(f"   Response Time: {service_health['response_time_ms']}ms")
            
            if 'error' in service_health:
                print(f"   Error: {service_health['error']}")
            
            if 'details' in service_health:
                details = service_health['details']
                if isinstance(details, dict):
                    for key, value in details.items():
                        if key in ['database_records', 'loaded_strategies', 'memory_usage', 'file_size_mb']:
                            print(f"   {key.replace('_', ' ').title()}: {value}")
            
            print()
        
        # Show unhealthy services summary
        if summary['unhealthy_services'] or summary['warning_services']:
            print("[ISSUES] Problems Found:")
            for service in summary['unhealthy_services'] + summary['warning_services']:
                print(f"   * {service['name']}: {service['status']} - {service['error']}")
        
        print("=" * 60)
    
    def monitor_continuously(self, interval_seconds: int = 30, max_checks: int = 0):
        """Monitor services continuously"""
        logger.info(f"[MONITOR] Starting continuous health monitoring (interval: {interval_seconds}s)")
        
        try:
            check_count = 0
            while True:
                check_count += 1
                
                # Perform health check
                results = self.perform_health_check()
                self.print_health_report(results)
                
                # Check if we should stop
                if max_checks > 0 and check_count >= max_checks:
                    logger.info(f"Completed {max_checks} health checks")
                    break
                
                # Wait for next check
                if max_checks == 0 or check_count < max_checks:
                    logger.info(f"Next check in {interval_seconds} seconds...")
                    time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("Health monitoring stopped by user")
        except Exception as e:
            logger.error(f"Health monitoring error: {e}")

def main():
    """Main health monitor entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Service Health Monitor')
    parser.add_argument('--continuous', action='store_true', help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--max-checks', type=int, default=0, help='Maximum number of checks (0 = infinite)')
    
    args = parser.parse_args()
    
    monitor = SystemHealthMonitor()
    
    if args.continuous:
        monitor.monitor_continuously(args.interval, args.max_checks)
    else:
        # Single health check
        results = monitor.perform_health_check()
        monitor.print_health_report(results)

if __name__ == "__main__":
    main()