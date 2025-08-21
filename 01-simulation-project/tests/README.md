# Test Suite Organization

This directory contains all tests for the Personal Futures Backtesting System.

## Directory Structure

### `/integration/`
**Service interaction and end-to-end tests**
- `test_integration.py` - Core integration test suite
- `test_integration_comprehensive.py` - Comprehensive integration tests (8 test scenarios)
- `test_system_functionality.py` - System functionality verification
- `test_system_health.py` - System health monitoring tests

### `/unit/`
**Individual component tests**
- `test_portfolio_service.py` - Portfolio service unit tests
- `test_redis_pubsub.py` - Redis pub/sub functionality tests
- `test_date_detection.py` - Date format detection tests
- `test_error_handling.py` - Error handling mechanism tests
- `test_strategy_fix.py` - Strategy implementation tests

### `/verification/`
**Weekly milestone and target verification**
- `verify_week1_completion.py` - Week 1: Development environment setup
- `verify_week2_completion.py` - Week 2: Data Service foundation  
- `verify_week3_completion.py` - Week 3: Backtest Service core
- `verify_week4_completion.py` - Week 4: Redis pub/sub and error handling
- `verify_week5_completion.py` - Week 5: Portfolio Service implementation
- `verify_contracts.py` - Contract specification verification

## Running Tests

### Integration Tests
```bash
# Run all integration tests
python tests/integration/test_integration_comprehensive.py

# Run specific integration test
python tests/integration/test_integration.py
```

### Unit Tests
```bash
# Run specific unit test
python tests/unit/test_portfolio_service.py
```

### Verification Tests
```bash
# Run weekly milestone verifications
python tests/verification/verify_week1_completion.py
python tests/verification/verify_week2_completion.py  
python tests/verification/verify_week3_completion.py
python tests/verification/verify_week4_completion.py
python tests/verification/verify_week5_completion.py

# Run contract verification
python tests/verification/verify_contracts.py
```

## Test Results
- `test_results.md` - Generated test result reports

## Prerequisites
- All services must be running for integration tests
- Redis server must be operational
- Database must be properly initialized

## Test Coverage
- **Integration**: Service communication and workflows
- **Unit**: Individual component functionality
- **Verification**: Milestone and target achievement