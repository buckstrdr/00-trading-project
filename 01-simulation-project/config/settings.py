"""
System Configuration Settings
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))

# Service Ports
SERVICE_PORTS = {
    'data': 8001,
    'backtest': 8002,
    'risk': 8003,
    'ml': 8004,
    'portfolio': 8005,
    'dashboard': 8501
}

# Database Configuration
DATABASE_URL = f"sqlite:///{DATA_DIR}/futures.db"

# System Settings
MAX_WORKERS = os.getenv('MAX_WORKERS', 4)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Backtesting Defaults
DEFAULT_INITIAL_CASH = 100000
DEFAULT_COMMISSION = 2.50  # per contract
DEFAULT_SLIPPAGE = 1  # ticks
DEFAULT_MARGIN_REQUIREMENT = 0.10

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)