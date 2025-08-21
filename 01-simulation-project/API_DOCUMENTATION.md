# API Documentation
## Personal Futures Backtesting System

**Version**: 1.0  
**Last Updated**: August 2025  
**Base Architecture**: Microservices with REST APIs

---

## System Overview

The Personal Futures Backtesting System consists of 6 microservices with well-defined REST APIs:

- **Data Service** (Port 8001): Market data management and contract specifications
- **Backtest Service** (Port 8002): Strategy execution and backtesting analysis  
- **Portfolio Service** (Port 8005): Position tracking and equity curve management
- **Risk Service** (Port 8003): Risk calculations and monitoring *(Coming Soon)*
- **ML Service** (Port 8004): Machine learning features *(Coming Soon)*
- **Dashboard** (Port 8501): Streamlit web interface *(Coming Soon)*

---

## Data Service API (Port 8001)

### Health Check
**GET** `/health`

Returns service health status and database information.

**Example Request:**
```bash
GET http://localhost:8001/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "DataService", 
  "details": {
    "database_records": 348130,
    "redis_connected": true,
    "database_path": "/path/to/futures.db"
  }
}
```

### Market Data

#### Get Market Data
**GET** `/api/data/{symbol}`

Retrieve historical market data for a futures symbol.

**Parameters:**
- `symbol` (path): Futures symbol (e.g., MCL, MES, ES, NQ)
- `start_date` (query, optional): Start date in YYYY-MM-DD format
- `end_date` (query, optional): End date in YYYY-MM-DD format  
- `limit` (query, optional): Maximum number of records (default: 1000)

**Example Request:**
```bash
GET http://localhost:8001/api/data/MCL?start_date=2024-01-01&end_date=2024-01-03&limit=100
```

**Response:**
```json
{
  "status": "success",
  "symbol": "MCL",
  "data": [
    {
      "timestamp": "2024-01-01T09:30:00",
      "open": 64.50,
      "high": 65.20,
      "low": 64.30,
      "close": 64.95,
      "volume": 1250
    }
  ],
  "record_count": 1000,
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-03"
  }
}
```

#### Get Contract Specifications
**GET** `/api/contracts/{symbol}`

Get contract specifications for a futures symbol.

**Example Request:**
```bash
GET http://localhost:8001/api/contracts/MCL
```

**Response:**
```json
{
  "status": "success",
  "contract": {
    "symbol": "MCL",
    "name": "Micro WTI Crude Oil",
    "tick_size": 0.01,
    "tick_value": 10.0,
    "contract_size": 100,
    "currency": "USD",
    "exchange": "NYMEX",
    "margin_requirement": 2500
  }
}
```

### Database Information

#### Get Database Info
**GET** `/api/database/info`

Returns detailed database information and statistics.

**Response:**
```json
{
  "status": "success",
  "database_info": {
    "path": "/path/to/futures.db",
    "size_mb": 65.4,
    "tables": 7,
    "total_records": 348130,
    "symbols": ["MCL", "MES", "ES", "NQ"],
    "date_range": {
      "earliest": "2023-01-01",
      "latest": "2024-12-31"
    }
  }
}
```

---

## Backtest Service API (Port 8002)

### Health Check
**GET** `/health`

**Example Request:**
```bash
GET http://localhost:8002/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "BacktestService",
  "details": {
    "database_records": 348130,
    "loaded_strategies": 1,
    "redis_connected": true,
    "strategy_names": ["SimpleMAStrategy"]
  }
}
```

### Strategy Management

#### List Available Strategies
**GET** `/api/strategies`

Get all available trading strategies.

**Example Request:**
```bash
GET http://localhost:8002/api/strategies
```

**Response:**
```json
{
  "strategies": [
    {
      "name": "SimpleMAStrategy",
      "class": "SimpleMAStrategy", 
      "description": "Simple moving average crossover strategy",
      "config_required": true
    }
  ]
}
```

### Backtesting

#### Run Backtest
**POST** `/api/backtest`

Execute a backtest for a specific strategy and symbol.

**Parameters:**
- `strategy_name` (query): Name of strategy to execute
- `symbol` (query): Futures symbol to trade
- `start_date` (query, optional): Backtest start date (YYYY-MM-DD)
- `end_date` (query, optional): Backtest end date (YYYY-MM-DD)
- `initial_cash` (query): Initial cash for backtest (default: 100000)
- `record_to_portfolio` (query): Record trades to Portfolio Service (default: true)
- `strategy_config` (body, optional): Strategy-specific configuration

**Example Request:**
```bash
POST http://localhost:8002/api/backtest?strategy_name=SimpleMAStrategy&symbol=MCL&start_date=2024-01-01&end_date=2024-01-07&initial_cash=100000&record_to_portfolio=true
```

**Response:**
```json
{
  "strategy_name": "SimpleMAStrategy",
  "strategy_version": "1.0",
  "symbol": "MCL",
  "backtest_period": {
    "start": "2024-01-01T00:00:00",
    "end": "2024-01-07T23:59:59", 
    "total_bars": 2000
  },
  "performance": {
    "total_return_pct": 2.45,
    "total_trades": 73,
    "win_rate_pct": 45.2,
    "profit_factor": 1.23,
    "max_drawdown_pct": -5.8,
    "sharpe_ratio": 0.85
  },
  "configuration": {
    "initial_cash": 100000,
    "commission": 10.0,
    "strategy_config": {
      "fast_period": 10,
      "slow_period": 20
    }
  },
  "portfolio_id": "port_abc123", 
  "trades_recorded": 73,
  "trades": [],
  "equity_curve": [],
  "timestamp": "2024-08-20T12:15:30"
}
```

#### Get Backtest History
**GET** `/api/backtest/history`

Returns placeholder for future backtest history feature.

---

## Portfolio Service API (Port 8005)

### Health Check
**GET** `/health`

**Example Request:**
```bash
GET http://localhost:8005/health
```

**Response:**
```json
{
  "status": "healthy", 
  "service": "PortfolioService",
  "details": {
    "database_status": "healthy",
    "portfolios": 6,
    "total_trades": 84,
    "active_positions": 8,
    "database_path": "/path/to/futures.db"
  }
}
```

### Portfolio Management

#### Create Portfolio
**POST** `/api/portfolio`

Create a new portfolio.

**Parameters:**
- `name` (query): Portfolio name
- `initial_cash` (query): Initial cash amount (default: 100000)

**Example Request:**
```bash
POST http://localhost:8005/api/portfolio?name=My_Trading_Portfolio&initial_cash=50000
```

**Response:**
```json
{
  "status": "success",
  "portfolio_id": "port_abc123",
  "name": "My Trading Portfolio",
  "initial_cash": 100000,
  "created_at": "2024-08-20T12:00:00Z"
}
```

#### Get Portfolio
**GET** `/api/portfolio/{portfolio_id}`

Retrieve portfolio information by ID.

**Response:**
```json
{
  "status": "success",
  "portfolio": {
    "id": "port_abc123", 
    "name": "My Trading Portfolio",
    "initial_cash": 100000,
    "current_cash": 98500,
    "created_at": "2024-08-20T12:00:00Z",
    "updated_at": "2024-08-20T14:30:00Z"
  }
}
```

#### List All Portfolios
**GET** `/api/portfolios`

Get list of all portfolios.

**Response:**
```json
{
  "status": "success",
  "portfolios": [
    {
      "id": "port_abc123",
      "name": "My Trading Portfolio", 
      "initial_cash": 100000,
      "current_cash": 98500,
      "created_at": "2024-08-20T12:00:00Z",
      "updated_at": "2024-08-20T14:30:00Z"
    }
  ]
}
```

### Trade Management

#### Record Trade
**POST** `/api/portfolio/{portfolio_id}/trade`

Record a new trade for a portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio identifier
- `symbol` (query): Trading symbol
- `action` (query): Trade action (BUY, SELL, CLOSE_LONG, CLOSE_SHORT)
- `quantity` (query): Number of contracts
- `price` (query): Execution price
- `strategy_name` (query, optional): Strategy that generated the trade

**Response:**
```json
{
  "status": "success",
  "trade_id": "trade_xyz789",
  "portfolio_id": "port_abc123",
  "symbol": "MCL",
  "action": "BUY", 
  "quantity": 5,
  "price": 65.50,
  "strategy_name": "SimpleMAStrategy",
  "timestamp": "2024-08-20T14:30:00Z"
}
```

#### Get Trade History
**GET** `/api/portfolio/{portfolio_id}/trades`

Get trade history for a portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio identifier
- `limit` (query, optional): Maximum trades to return (1-1000, default: 100)

**Response:**
```json
{
  "status": "success",
  "portfolio_id": "port_abc123",
  "trades": [
    {
      "trade_id": "trade_xyz789",
      "symbol": "MCL",
      "action": "BUY",
      "quantity": 5, 
      "price": 65.50,
      "timestamp": "2024-08-20T14:30:00Z",
      "strategy_name": "SimpleMAStrategy",
      "pnl": 0.0,
      "commission": 32.75
    }
  ],
  "trade_count": 1
}
```

### Position Management

#### Get Current Positions
**GET** `/api/portfolio/{portfolio_id}/positions`

Get current positions for a portfolio.

**Response:**
```json
{
  "status": "success",
  "portfolio_id": "port_abc123",
  "positions": [
    {
      "symbol": "MCL",
      "quantity": 5,
      "avg_price": 65.50,
      "current_price": 66.20,
      "unrealized_pnl": 350.0,
      "margin_requirement": 12500,
      "contract_size": 100,
      "tick_size": 0.01,
      "timestamp": "2024-08-20T14:30:00Z"
    }
  ],
  "position_count": 1
}
```

### Performance Analytics

#### Get Equity Curve
**GET** `/api/portfolio/{portfolio_id}/equity-curve`

Calculate portfolio performance and equity curve.

**Response:**
```json
{
  "status": "success",
  "equity_curve": {
    "portfolio_id": "port_abc123",
    "portfolio_name": "My Trading Portfolio",
    "timestamp": "2024-08-20T15:00:00Z",
    "initial_cash": 100000,
    "current_cash": 98500,
    "positions_value": 3275,
    "total_value": 101775,
    "total_pnl": 1775,
    "total_return_pct": 1.78,
    "total_trades": 10,
    "total_commission": 327.5,
    "snapshot_id": "snap_def456"
  }
}
```

### Service Statistics

#### Get Service Statistics
**GET** `/api/stats`

Get comprehensive service statistics.

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_portfolios": 6,
    "total_trades": 84,
    "active_positions": 8, 
    "total_snapshots": 12,
    "total_initial_cash": 600000,
    "total_current_cash": 598450,
    "database_size_mb": 65.4
  }
}
```

---

## Error Handling

All APIs use consistent HTTP status codes and error response format:

### Success Responses
- `200 OK`: Successful request
- `201 Created`: Resource created successfully

### Error Responses
- `400 Bad Request`: Invalid parameters or request format
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Examples

#### Invalid Portfolio ID
**Status**: 404 Not Found
```json
{
  "detail": "Portfolio not found"
}
```

#### Invalid Trade Parameters
**Status**: 400 Bad Request
```json
{
  "detail": "Invalid action" 
}
```

#### Service Unavailable
**Status**: 500 Internal Server Error
```json
{
  "detail": "Database connection failed"
}
```

---

## Authentication & Security

Currently, the system runs in a local development environment without authentication. For production deployment, consider:

- API key authentication for service-to-service communication
- Rate limiting for external API access
- Input validation and sanitization
- HTTPS/TLS encryption
- Database access controls

---

## Rate Limits & Performance

### Current Limits
- **Request Timeout**: 30 seconds for backtests, 5 seconds for other operations
- **Concurrent Requests**: No explicit limit (bounded by system resources)
- **Data Retrieval**: 1000 records default limit for market data queries
- **Trade History**: 1000 trades maximum per query

### Performance Characteristics
- **Market Data Query**: ~100ms for 1000 records
- **Simple Backtest**: ~2-5 seconds for 1 week of data
- **Portfolio Operations**: ~50ms average response time
- **Database Size**: 65.4 MB with 348K market data records

---

## Integration Examples

### Python Integration Example
```python
import requests

# Create portfolio
response = requests.post('http://localhost:8005/api/portfolio', params={
    'name': 'My Algorithm Portfolio',
    'initial_cash': 50000
})
portfolio = response.json()
portfolio_id = portfolio['portfolio_id']

# Run backtest with portfolio integration
response = requests.post('http://localhost:8002/api/backtest', params={
    'strategy_name': 'SimpleMAStrategy',
    'symbol': 'MCL',
    'start_date': '2024-01-01', 
    'end_date': '2024-01-07',
    'initial_cash': 50000,
    'record_to_portfolio': True
})
backtest_result = response.json()

# Get portfolio performance
response = requests.get(f'http://localhost:8005/api/portfolio/{portfolio_id}/equity-curve')
performance = response.json()

print(f"Total Return: {performance['equity_curve']['total_return_pct']:.2f}%")
```

### cURL Integration Example
```bash
# Health check all services
curl http://localhost:8001/health
curl http://localhost:8002/health  
curl http://localhost:8005/health

# Get market data
curl "http://localhost:8001/api/data/MCL?start_date=2024-01-01&end_date=2024-01-02"

# Run backtest
curl -X POST "http://localhost:8002/api/backtest?strategy_name=SimpleMAStrategy&symbol=MCL&start_date=2024-01-01&end_date=2024-01-02&initial_cash=25000&record_to_portfolio=true"
```

---

## Service Dependencies

### Internal Dependencies
- **Backtest Service** → **Data Service**: Market data retrieval
- **Backtest Service** → **Portfolio Service**: Trade recording (optional)  
- **All Services** → **Redis**: Pub/sub messaging and caching
- **All Services** → **SQLite Database**: Data persistence

### External Dependencies
- **Python 3.11+**: Runtime environment
- **Redis Server**: Message bus and caching
- **SQLite**: Database engine
- **PyBroker**: Backtesting framework

---

## Version History

### Version 1.0 (Current)
- ✅ Data Service: Market data management and contract specifications
- ✅ Backtest Service: PyBroker integration with strategy execution
- ✅ Portfolio Service: Trade recording and equity curve calculation
- ✅ Service Integration: Automatic trade recording from backtests
- ✅ Health Monitoring: Comprehensive health checks for all services
- ✅ Error Handling: Consistent error responses and validation

### Planned Features (Version 1.1)
- 🔄 Risk Service: Risk metrics and position sizing
- 🔄 ML Service: Feature engineering and model training
- 🔄 Dashboard: Streamlit web interface
- 🔄 API Authentication: Security and access controls
- 🔄 Enhanced Documentation: OpenAPI/Swagger integration

---

## Support & Troubleshooting

### Common Issues

#### Services Not Starting
1. Check if ports 8001, 8002, 8005 are available
2. Verify Redis server is running (`redis-cli ping`)
3. Ensure database file exists at expected location
4. Check service logs for specific error messages

#### Database Connection Errors
1. Verify database file permissions
2. Check available disk space
3. Ensure SQLite is properly installed
4. Look for file locking issues

#### Backtest Integration Issues
1. Confirm Portfolio Service is running and healthy
2. Verify `record_to_portfolio=true` parameter
3. Check for sufficient initial cash for position sizing
4. Review strategy configuration and market data availability

### Service Health Monitoring
Use the health check endpoints to monitor service status:
```bash
# Check all services
python run_system.py status

# Individual service health
curl http://localhost:8001/health
curl http://localhost:8002/health  
curl http://localhost:8005/health
```

---

**Last Updated**: August 20, 2025  
**API Version**: 1.0  
**System Status**: Production Ready (Weeks 1-5 Complete)