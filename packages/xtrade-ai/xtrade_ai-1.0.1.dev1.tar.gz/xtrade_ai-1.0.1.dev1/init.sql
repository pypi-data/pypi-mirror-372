-- XTrade-AI Database Initialization Script
-- This script creates the necessary tables and indexes for the XTrade-AI framework

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS trading;
CREATE SCHEMA IF NOT EXISTS models;
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Trading data tables
CREATE TABLE IF NOT EXISTS trading.market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    open DECIMAL(15, 8) NOT NULL,
    high DECIMAL(15, 8) NOT NULL,
    low DECIMAL(15, 8) NOT NULL,
    close DECIMAL(15, 8) NOT NULL,
    volume DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, timestamp)
);

CREATE TABLE IF NOT EXISTS trading.positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(15, 8) NOT NULL,
    entry_price DECIMAL(15, 8) NOT NULL,
    current_price DECIMAL(15, 8),
    pnl DECIMAL(15, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'CLOSED', 'CANCELLED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS trading.orders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID REFERENCES trading.positions(id),
    symbol VARCHAR(20) NOT NULL,
    order_type VARCHAR(20) NOT NULL CHECK (order_type IN ('MARKET', 'LIMIT', 'STOP', 'STOP_LIMIT')),
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(15, 8) NOT NULL,
    price DECIMAL(15, 8),
    status VARCHAR(20) DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'FILLED', 'CANCELLED', 'REJECTED')),
    filled_quantity DECIMAL(15, 8) DEFAULT 0,
    filled_price DECIMAL(15, 8),
    commission DECIMAL(15, 8) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    filled_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS trading.trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id UUID REFERENCES trading.orders(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL CHECK (side IN ('BUY', 'SELL')),
    quantity DECIMAL(15, 8) NOT NULL,
    price DECIMAL(15, 8) NOT NULL,
    commission DECIMAL(15, 8) DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trading.portfolio (
    id SERIAL PRIMARY KEY,
    balance DECIMAL(15, 8) NOT NULL DEFAULT 0,
    equity DECIMAL(15, 8) NOT NULL DEFAULT 0,
    margin DECIMAL(15, 8) NOT NULL DEFAULT 0,
    free_margin DECIMAL(15, 8) NOT NULL DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Model management tables
CREATE TABLE IF NOT EXISTS models.model_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    file_path TEXT NOT NULL,
    parameters JSONB,
    metrics JSONB,
    status VARCHAR(20) DEFAULT 'TRAINING' CHECK (status IN ('TRAINING', 'READY', 'DEPRECATED', 'ERROR')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(model_name, version)
);

CREATE TABLE IF NOT EXISTS models.training_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models.model_metadata(id),
    epoch INTEGER NOT NULL,
    loss DECIMAL(15, 8),
    accuracy DECIMAL(15, 8),
    validation_loss DECIMAL(15, 8),
    validation_accuracy DECIMAL(15, 8),
    learning_rate DECIMAL(15, 8),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS models.predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models.model_metadata(id),
    symbol VARCHAR(20) NOT NULL,
    prediction_type VARCHAR(50) NOT NULL,
    prediction_value DECIMAL(15, 8),
    confidence DECIMAL(15, 8),
    actual_value DECIMAL(15, 8),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Monitoring tables
CREATE TABLE IF NOT EXISTS monitoring.system_metrics (
    id SERIAL PRIMARY KEY,
    cpu_usage DECIMAL(5, 2),
    memory_usage DECIMAL(5, 2),
    disk_usage DECIMAL(5, 2),
    network_in DECIMAL(15, 2),
    network_out DECIMAL(15, 2),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monitoring.application_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 8),
    metric_unit VARCHAR(20),
    tags JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monitoring.trading_metrics (
    id SERIAL PRIMARY KEY,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 4) DEFAULT 0,
    total_pnl DECIMAL(15, 8) DEFAULT 0,
    max_drawdown DECIMAL(15, 8) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4) DEFAULT 0,
    sortino_ratio DECIMAL(10, 4) DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monitoring.logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL,
    logger VARCHAR(100),
    message TEXT NOT NULL,
    exception TEXT,
    stack_trace TEXT,
    context JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON trading.market_data(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON trading.market_data(timestamp);

CREATE INDEX IF NOT EXISTS idx_positions_symbol ON trading.positions(symbol);
CREATE INDEX IF NOT EXISTS idx_positions_status ON trading.positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_created_at ON trading.positions(created_at);

CREATE INDEX IF NOT EXISTS idx_orders_symbol ON trading.orders(symbol);
CREATE INDEX IF NOT EXISTS idx_orders_status ON trading.orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON trading.orders(created_at);

CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trading.trades(symbol);
CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trading.trades(timestamp);

CREATE INDEX IF NOT EXISTS idx_portfolio_timestamp ON trading.portfolio(timestamp);

CREATE INDEX IF NOT EXISTS idx_model_metadata_name_version ON models.model_metadata(model_name, version);
CREATE INDEX IF NOT EXISTS idx_model_metadata_status ON models.model_metadata(status);

CREATE INDEX IF NOT EXISTS idx_training_history_model_epoch ON models.training_history(model_id, epoch);
CREATE INDEX IF NOT EXISTS idx_training_history_timestamp ON models.training_history(timestamp);

CREATE INDEX IF NOT EXISTS idx_predictions_model_symbol ON models.predictions(model_id, symbol);
CREATE INDEX IF NOT EXISTS idx_predictions_timestamp ON models.predictions(timestamp);

CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON monitoring.system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_application_metrics_name_timestamp ON monitoring.application_metrics(metric_name, timestamp);
CREATE INDEX IF NOT EXISTS idx_trading_metrics_timestamp ON monitoring.trading_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_level_timestamp ON monitoring.logs(level, timestamp);

-- Create views for common queries
CREATE OR REPLACE VIEW trading.current_positions AS
SELECT 
    p.*,
    o.quantity as order_quantity,
    o.price as order_price
FROM trading.positions p
LEFT JOIN trading.orders o ON p.id = o.position_id
WHERE p.status = 'OPEN';

CREATE OR REPLACE VIEW trading.position_summary AS
SELECT 
    symbol,
    COUNT(*) as total_positions,
    SUM(CASE WHEN side = 'BUY' THEN 1 ELSE 0 END) as buy_positions,
    SUM(CASE WHEN side = 'SELL' THEN 1 ELSE 0 END) as sell_positions,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl
FROM trading.positions
WHERE status = 'OPEN'
GROUP BY symbol;

CREATE OR REPLACE VIEW monitoring.performance_summary AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    COUNT(*) as total_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    AVG(pnl) as avg_pnl,
    SUM(pnl) as total_pnl,
    MAX(pnl) as max_profit,
    MIN(pnl) as max_loss
FROM trading.positions
WHERE status = 'CLOSED'
GROUP BY DATE_TRUNC('day', timestamp)
ORDER BY date DESC;

-- Create functions for common operations
CREATE OR REPLACE FUNCTION trading.update_position_pnl()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.current_price IS NOT NULL AND NEW.entry_price IS NOT NULL THEN
        IF NEW.side = 'BUY' THEN
            NEW.pnl = (NEW.current_price - NEW.entry_price) * NEW.quantity;
        ELSE
            NEW.pnl = (NEW.entry_price - NEW.current_price) * NEW.quantity;
        END IF;
    END IF;
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_position_pnl
    BEFORE UPDATE ON trading.positions
    FOR EACH ROW
    EXECUTE FUNCTION trading.update_position_pnl();

-- Insert initial data
INSERT INTO trading.portfolio (balance, equity, margin, free_margin, timestamp) 
VALUES (10000.0, 10000.0, 0.0, 10000.0, NOW())
ON CONFLICT DO NOTHING;

-- Create user roles and permissions
DO $$
BEGIN
    -- Create read-only role
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'xtrade_readonly') THEN
        CREATE ROLE xtrade_readonly;
    END IF;
    
    -- Create read-write role
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'xtrade_readwrite') THEN
        CREATE ROLE xtrade_readwrite;
    END IF;
    
    -- Grant permissions
    GRANT CONNECT ON DATABASE xtrade_ai TO xtrade_readonly, xtrade_readwrite;
    GRANT USAGE ON SCHEMA trading, models, monitoring TO xtrade_readonly, xtrade_readwrite;
    GRANT SELECT ON ALL TABLES IN SCHEMA trading, models, monitoring TO xtrade_readonly;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA trading, models, monitoring TO xtrade_readwrite;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA trading, models, monitoring TO xtrade_readwrite;
    
    -- Grant permissions to default user
    GRANT xtrade_readwrite TO xtrade_user;
END
$$;
