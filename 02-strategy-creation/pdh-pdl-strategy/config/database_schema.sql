-- PDH/PDL Strategy Database Schema
-- Creates all required tables for the trading strategy

-- Historical market data
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open_price DECIMAL(10,4) NOT NULL,
    high_price DECIMAL(10,4) NOT NULL,
    low_price DECIMAL(10,4) NOT NULL,
    close_price DECIMAL(10,4) NOT NULL,
    volume BIGINT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);

-- PDH/PDL reference levels
CREATE TABLE IF NOT EXISTS reference_levels (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    pdh DECIMAL(10,4) NOT NULL,
    pdl DECIMAL(10,4) NOT NULL,
    daily_range DECIMAL(10,4) NOT NULL,
    poc DECIMAL(10,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, trade_date)
);

-- Trade execution log
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    strategy_type VARCHAR(20) NOT NULL,
    direction VARCHAR(5) NOT NULL,
    entry_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    exit_timestamp TIMESTAMP WITH TIME ZONE,
    entry_price DECIMAL(10,4) NOT NULL,
    exit_price DECIMAL(10,4),
    quantity INTEGER NOT NULL,
    stop_loss DECIMAL(10,4) NOT NULL,
    target_price DECIMAL(10,4),
    pnl DECIMAL(10,2),
    commission DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'OPEN',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    gross_profit DECIMAL(10,2) DEFAULT 0,
    gross_loss DECIMAL(10,2) DEFAULT 0,
    net_profit DECIMAL(10,2) DEFAULT 0,
    profit_factor DECIMAL(6,3),
    max_drawdown DECIMAL(6,3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date, symbol)
);

-- System logs table
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(50),
    function VARCHAR(50)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_reference_levels_symbol_date ON reference_levels(symbol, trade_date DESC);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_entry ON trades(symbol, entry_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trades_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_performance_date ON performance_metrics(date DESC);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC);

-- Update function for trades
CREATE OR REPLACE FUNCTION update_trades_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for updating trades timestamp
DROP TRIGGER IF EXISTS tr_trades_updated_at ON trades;
CREATE TRIGGER tr_trades_updated_at
    BEFORE UPDATE ON trades
    FOR EACH ROW
    EXECUTE FUNCTION update_trades_updated_at();