#!/usr/bin/env python3
"""
Personal Futures Backtesting System - Main Controller
One script to rule them all - starts and manages all microservices
"""

import subprocess
import time
import signal
import sys
import requests
from datetime import datetime
from pathlib import Path

class FuturesBacktestingSystem:
    """Main system controller for the futures backtesting platform"""
    
    def __init__(self):
        self.services = [
            {"name": "Redis", "cmd": "redis-server --daemonize yes", "port": 6379, "cwd": "."},
            {"name": "Data Service", "cmd": "python data_service.py", "port": 8001, "cwd": "services"},
            {"name": "Risk Service", "cmd": "python risk_service.py", "port": 8003, "cwd": "services"},
            {"name": "ML Service", "cmd": "python ml_service.py", "port": 8004, "cwd": "services"},
            {"name": "Portfolio Service", "cmd": "python portfolio_service.py", "port": 8005, "cwd": "services"},
            {"name": "Backtest Service", "cmd": "python backtest_service.py", "port": 8002, "cwd": "services"},
        ]
        self.processes = []
        
    def start_service(self, service):
        """Start a single service with proper error handling"""
        print(f"[STARTING] Starting {service['name']}...")
        
        if service['name'] == 'Redis':
            # Start Redis in daemon mode
            try:
                subprocess.run(service['cmd'], shell=True, cwd=service['cwd'], check=True)
                print(f"[OK] {service['name']} started successfully")
            except subprocess.CalledProcessError:
                print(f"[WARNING] {service['name']} failed to start - Redis not installed, services will run without pub/sub")
                return True  # Continue without Redis
        else:
            # Start Python services
            try:
                proc = subprocess.Popen(
                    service['cmd'].split(),
                    cwd=service['cwd'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes.append((service['name'], proc))
                
                # Wait for service to start
                time.sleep(3)
                if self.check_health(service):
                    print(f"[OK] {service['name']} started successfully")
                    return True
                else:
                    print(f"[ERROR] {service['name']} failed to start")
                    return False
            except Exception as e:
                print(f"[ERROR] {service['name']} failed to start: {e}")
                return False
                
    def check_health(self, service):
        """Check if a service is responding"""
        try:
            if service['port']:
                response = requests.get(f"http://localhost:{service['port']}/health", timeout=2)
                return response.status_code == 200
        except:
            return False
            
    def start_all(self):
        """Start all services in the correct order"""
        print(">>> Starting Personal Futures Backtesting System...")
        print("=" * 50)
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Check if services directory exists
        if not Path("services").exists():
            print("WARNING: Services directory not found. Run development setup first.")
            return False
            
        try:
            # Start services in order
            for service in self.services:
                success = self.start_service(service)
                if not success and service['name'] != 'Redis':
                    print(f"[WARNING]  Continuing without {service['name']}")
                    
            print("\\n[SUCCESS] System startup complete!")
            print("[INFO] Dashboard will be available at: http://localhost:8501")
            print("[INFO] Press Ctrl+C to stop all services")
            
            # Start dashboard (foreground)
            if Path("dashboard/main.py").exists():
                print("\\n[STARTING] Starting Dashboard...")
                dashboard_proc = subprocess.run(
                    ["streamlit", "run", "main.py"], 
                    cwd="dashboard"
                )
            else:
                print("\\n[WARNING]  Dashboard not yet created. Starting interactive mode...")
                self.interactive_mode()
                
        except KeyboardInterrupt:
            self.cleanup()
            
    def interactive_mode(self):
        """Interactive mode when dashboard isn't ready"""
        print("\\n[INTERACTIVE] Interactive Mode - Available Commands:")
        print("   status  - Check service status")
        print("   stop    - Stop all services")
        print("   exit    - Exit system")
        
        while True:
            try:
                command = input("\\n> ").strip().lower()
                
                if command == 'status':
                    self.status()
                elif command == 'stop' or command == 'exit':
                    break
                elif command == 'help':
                    print("   status  - Check service status")
                    print("   stop    - Stop all services") 
                    print("   exit    - Exit system")
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                break
                
        self.cleanup()
            
    def cleanup(self):
        """Stop all services cleanly"""
        print("\\n[STOPPING] Shutting down all services...")
        
        # Stop Python services
        for name, proc in self.processes:
            print(f"   Stopping {name}...")
            proc.terminate()
            
        # Stop Redis
        try:
            subprocess.run("redis-cli shutdown", shell=True, stderr=subprocess.DEVNULL)
            print("   Redis stopped")
        except:
            pass
            
        print("[OK] All services stopped")
        
    def status(self):
        """Check status of all services"""
        print("[STATUS] Service Status:")
        print("-" * 30)
        
        for service in self.services:
            if service['name'] == 'Redis':
                # Check Redis
                try:
                    result = subprocess.run("redis-cli ping", shell=True, check=True, 
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"[OK] {service['name']:<20} Running")
                except:
                    print(f"[ERROR] {service['name']:<20} Stopped")
            else:
                # Check HTTP services
                if self.check_health(service):
                    print(f"[OK] {service['name']:<20} Running")
                else:
                    print(f"[ERROR] {service['name']:<20} Stopped")

def main():
    """Main entry point"""
    system = FuturesBacktestingSystem()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "status":
            system.status()
        elif command == "stop":
            system.cleanup()
        else:
            print("Usage: python run_system.py [status|stop]")
    else:
        # Register signal handler for clean shutdown
        signal.signal(signal.SIGINT, lambda s, f: system.cleanup())
        system.start_all()

if __name__ == "__main__":
    main()