# Examples and Tutorials

This guide provides comprehensive examples for using the XTrade-AI framework.

## Quick Start

### Basic Framework Setup

```python
from xtrade_ai import XTradeAIFramework
from xtrade_ai.config import FrameworkConfig

# Initialize framework
config = FrameworkConfig(
    environment="development",
    log_level="INFO",
    data_path="./data",
    models_path="./models"
)
framework = XTradeAIFramework(config=config)

# Check health
if framework.is_healthy():
    print("Framework ready!")
```

### Simple Data Loading

```python
from xtrade_ai.data import DataLoader

# Load historical data
data_loader = DataLoader()
data = data_loader.load_data(
    symbols=["AAPL", "GOOGL", "MSFT"],
    start_date="2023-01-01",
    end_date="2023-12-31",
    interval="1d"
)
print(f"Loaded {len(data)} records")
```

## Trading Strategies

### Moving Average Strategy

```python
from xtrade_ai.strategies import MovingAverageStrategy
from xtrade_ai.backtesting import Backtester

# Create strategy
strategy = MovingAverageStrategy(
    short_window=20,
    long_window=50,
    symbols=["AAPL"]
)

# Run backtest
backtester = Backtester(
    strategy=strategy,
    initial_capital=10000,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

results = backtester.run()
print(f"Total Return: {results.total_return:.2%}")
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
```

### RSI Strategy

```python
from xtrade_ai.strategies import RSIStrategy

strategy = RSIStrategy(
    symbols=["TSLA"],
    rsi_period=14,
    oversold_threshold=30,
    overbought_threshold=70
)

backtester = Backtester(
    strategy=strategy,
    initial_capital=50000,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

results = backtester.run()
print(f"Win Rate: {results.win_rate:.2%}")
print(f"Total Trades: {results.total_trades}")
```

## Machine Learning

### Feature Engineering

```python
from xtrade_ai.ml.features import FeatureEngineer

feature_engineer = FeatureEngineer()

# Create technical indicators
features = feature_engineer.create_technical_features(
    data,
    indicators=["sma", "ema", "rsi", "macd"],
    windows=[5, 10, 20, 50]
)

# Create price features
price_features = feature_engineer.create_price_features(
    data,
    features=["returns", "volatility", "momentum"]
)
```

### Model Training

```python
from xtrade_ai.ml.models import MLModel
from xtrade_ai.ml.ensemble import EnsembleModel
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Create models
rf_model = MLModel(
    model=RandomForestClassifier(n_estimators=100),
    name="RandomForest"
)

xgb_model = MLModel(
    model=XGBClassifier(),
    name="XGBoost"
)

# Create ensemble
ensemble = EnsembleModel(
    models=[rf_model, xgb_model],
    weights=[0.5, 0.5]
)

# Train ensemble
ensemble.train(X_train, y_train)
evaluation = ensemble.evaluate(X_test, y_test)
print(f"Accuracy: {evaluation['accuracy']:.3f}")
```

## Reinforcement Learning

### PPO Agent

```python
from xtrade_ai.rl.agents import PPOAgent
from xtrade_ai.rl.environments import TradingEnvironment

# Create environment
env = TradingEnvironment(
    data=data,
    symbols=["AAPL", "GOOGL"],
    initial_capital=10000,
    transaction_fee=0.001
)

# Create agent
agent = PPOAgent(
    environment=env,
    learning_rate=3e-4,
    batch_size=64
)

# Train agent
training_results = agent.train(total_timesteps=100000)

# Evaluate
evaluation_results = agent.evaluate(test_data, n_episodes=10)
print(f"Average Return: {evaluation_results['mean_return']:.2f}")
```

### DQN Agent

```python
from xtrade_ai.rl.agents import DQNAgent

agent = DQNAgent(
    environment=env,
    learning_rate=1e-4,
    buffer_size=100000,
    batch_size=32
)

agent.train(total_timesteps=50000)
```

## Portfolio Management

### Modern Portfolio Theory

```python
from xtrade_ai.portfolio import ModernPortfolioTheory

mpt = ModernPortfolioTheory(
    symbols=["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
    risk_free_rate=0.02
)

# Optimize portfolio
optimal_weights = mpt.optimize_portfolio(
    method="efficient_frontier",
    target_return=0.15
)

# Calculate metrics
metrics = mpt.calculate_metrics(optimal_weights)
print(f"Expected Return: {metrics['expected_return']:.3%}")
print(f"Volatility: {metrics['volatility']:.3%}")
```

### Risk Parity

```python
from xtrade_ai.portfolio import RiskParityPortfolio

risk_parity = RiskParityPortfolio(
    symbols=["SPY", "QQQ", "IWM", "EFA", "AGG"],
    target_risk_contribution=0.2
)

weights = risk_parity.optimize()
risk_contributions = risk_parity.calculate_risk_contributions(weights)
```

## Risk Management

### Position Sizing

```python
from xtrade_ai.risk import PositionSizer
from xtrade_ai.risk import KellyCriterion

# Kelly Criterion
kelly = KellyCriterion(
    win_rate=0.6,
    avg_win=0.02,
    avg_loss=0.01
)

kelly_fraction = kelly.calculate_fraction()
print(f"Kelly Fraction: {kelly_fraction:.3f}")

# Position sizing
position_sizer = PositionSizer(
    max_position_size=0.1,
    max_portfolio_risk=0.02
)

position_size = position_sizer.calculate_size(
    portfolio_value=100000,
    stock_price=150,
    volatility=0.25
)
```

### Stop Loss Management

```python
from xtrade_ai.risk import StopLossManager

stop_loss = StopLossManager(
    stop_loss_type="trailing",
    initial_stop=0.05,
    trailing_stop=0.03
)

entry_price = 100
current_price = 105
stop_price = stop_loss.calculate_stop_price(
    entry_price=entry_price,
    current_price=current_price
)
```

## Real-time Trading

### Live Trading Setup

```python
from xtrade_ai.trading import LiveTrader
from xtrade_ai.brokers import AlpacaBroker

# Initialize broker
broker = AlpacaBroker(
    api_key="your_api_key",
    secret_key="your_secret_key",
    paper_trading=True
)

# Create trader
trader = LiveTrader(
    broker=broker,
    strategy=strategy,
    risk_manager=risk_monitor
)

# Start trading
trader.start(
    trading_hours="09:30-16:00",
    check_interval=60
)
```

### WebSocket Streaming

```python
from xtrade_ai.data import WebSocketDataStream

data_stream = WebSocketDataStream(
    symbols=["AAPL", "GOOGL", "MSFT"],
    data_types=["trade", "quote", "bar"],
    broker=broker
)

@data_stream.on_trade
def handle_trade(trade_data):
    print(f"Trade: {trade_data['symbol']} @ ${trade_data['price']}")
    
    signal = strategy.generate_signal(trade_data)
    if signal:
        trader.execute_signal(signal)

data_stream.start()
```

## Backtesting

### Comprehensive Backtest

```python
from xtrade_ai.backtesting import ComprehensiveBacktester

backtester = ComprehensiveBacktester(
    strategy=strategy,
    initial_capital=100000,
    start_date="2022-01-01",
    end_date="2023-12-31",
    benchmark="SPY"
)

backtester.configure(
    transaction_fee=0.001,
    slippage=0.0005,
    rebalance_frequency="daily"
)

results = backtester.run()
report = backtester.generate_report()
print(report)
```

### Walk-Forward Analysis

```python
from xtrade_ai.backtesting import WalkForwardAnalyzer

wfa = WalkForwardAnalyzer(
    strategy=strategy,
    initial_capital=50000,
    train_period=252,
    test_period=63,
    step_size=21
)

wfa_results = wfa.run(
    start_date="2020-01-01",
    end_date="2023-12-31"
)

analysis = wfa.analyze_results()
print(f"Strategy Stability: {analysis['stability_score']:.3f}")
```

## Custom Strategies

### Mean Reversion with Volatility Filter

```python
from xtrade_ai.strategies import BaseStrategy

class VolatilityFilteredMeanReversion(BaseStrategy):
    def __init__(self, symbols, lookback=20, std_threshold=2.0, vol_filter=0.3):
        super().__init__(symbols)
        self.lookback = lookback
        self.std_threshold = std_threshold
        self.vol_filter = vol_filter
    
    def generate_signals(self, data):
        signals = {}
        
        for symbol in self.symbols:
            if symbol not in data.columns:
                continue
            
            prices = data[symbol].dropna()
            returns = prices.pct_change().dropna()
            
            # Calculate statistics
            rolling_mean = returns.rolling(self.lookback).mean()
            rolling_std = returns.rolling(self.lookback).std()
            rolling_vol = returns.rolling(self.lookback).std()
            
            # Z-score
            z_score = (returns - rolling_mean) / rolling_std
            
            # Volatility filter
            vol_condition = rolling_vol < self.vol_filter
            
            # Generate signals
            long_signal = (z_score < -self.std_threshold) & vol_condition
            short_signal = (z_score > self.std_threshold) & vol_condition
            
            signals[symbol] = {
                "long": long_signal.iloc[-1] if len(long_signal) > 0 else False,
                "short": short_signal.iloc[-1] if len(short_signal) > 0 else False,
                "strength": abs(z_score.iloc[-1]) if len(z_score) > 0 else 0
            }
        
        return signals

# Use strategy
strategy = VolatilityFilteredMeanReversion(
    symbols=["AAPL", "GOOGL", "MSFT"],
    lookback=30,
    std_threshold=2.5,
    vol_filter=0.25
)

backtester = Backtester(
    strategy=strategy,
    initial_capital=10000,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

results = backtester.run()
```

### ML Enhanced Strategy

```python
from xtrade_ai.strategies import MLEnhancedStrategy
from sklearn.ensemble import RandomForestClassifier

class MLEnhancedMomentum(MLEnhancedStrategy):
    def __init__(self, symbols, ml_model=None, feature_window=20):
        super().__init__(symbols)
        self.feature_window = feature_window
        self.ml_model = ml_model or RandomForestClassifier(n_estimators=100)
        self.is_trained = False
    
    def create_features(self, data):
        features = {}
        
        for symbol in self.symbols:
            if symbol not in data.columns:
                continue
            
            prices = data[symbol].dropna()
            
            # Technical indicators
            sma_5 = prices.rolling(5).mean()
            sma_20 = prices.rolling(20).mean()
            rsi = self.calculate_rsi(prices, 14)
            volatility = prices.pct_change().rolling(self.feature_window).std()
            
            # Price momentum
            momentum_5 = prices.pct_change(5)
            momentum_20 = prices.pct_change(20)
            
            symbol_features = pd.DataFrame({
                "sma_ratio": sma_5 / sma_20,
                "rsi": rsi,
                "volatility": volatility,
                "momentum_5": momentum_5,
                "momentum_20": momentum_20
            })
            
            features[symbol] = symbol_features
        
        return features
    
    def train_model(self, data, labels):
        features = self.create_features(data)
        
        X = []
        y = []
        
        for symbol in self.symbols:
            if symbol in features:
                symbol_features = features[symbol].dropna()
                symbol_labels = labels[symbol].loc[symbol_features.index]
                
                common_index = symbol_features.index.intersection(symbol_labels.index)
                X.extend(symbol_features.loc[common_index].values)
                y.extend(symbol_labels.loc[common_index].values)
        
        self.ml_model.fit(X, y)
        self.is_trained = True
    
    def generate_signals(self, data):
        if not self.is_trained:
            return {}
        
        features = self.create_features(data)
        signals = {}
        
        for symbol in self.symbols:
            if symbol not in features:
                continue
            
            symbol_features = features[symbol].dropna()
            if len(symbol_features) == 0:
                continue
            
            latest_features = symbol_features.iloc[-1:].values
            prediction = self.ml_model.predict(latest_features)[0]
            probability = self.ml_model.predict_proba(latest_features)[0]
            
            signals[symbol] = {
                "long": prediction == 1 and probability[1] > 0.6,
                "short": prediction == -1 and probability[2] > 0.6,
                "confidence": max(probability),
                "prediction": prediction
            }
        
        return signals

# Use ML strategy
strategy = MLEnhancedMomentum(
    symbols=["AAPL", "GOOGL", "MSFT"],
    feature_window=30
)

strategy.train_model(training_data, training_labels)

backtester = Backtester(
    strategy=strategy,
    initial_capital=50000,
    start_date="2023-01-01",
    end_date="2023-12-31"
)

results = backtester.run()
```

## API Integration

### Custom Data Provider

```python
from xtrade_ai.data import DataProvider
import yfinance as yf

class YahooFinanceProvider(DataProvider):
    def fetch_data(self, symbols, start_date, end_date, interval="1d"):
        data = {}
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date, interval=interval)
            data[symbol] = hist
        return data
    
    def get_latest_price(self, symbol):
        ticker = yf.Ticker(symbol)
        return ticker.info['regularMarketPrice']

# Use provider
provider = YahooFinanceProvider()
data = provider.fetch_data(
    symbols=["AAPL", "GOOGL"],
    start_date="2023-01-01",
    end_date="2023-12-31"
)
```

### Custom Broker

```python
from xtrade_ai.brokers import Broker
import requests

class CustomBroker(Broker):
    def __init__(self, api_key, api_secret, base_url):
        super().__init__()
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })
    
    def place_order(self, symbol, quantity, side, order_type="market"):
        order_data = {
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "type": order_type
        }
        
        response = self.session.post(
            f"{self.base_url}/orders",
            json=order_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Order failed: {response.text}")
    
    def get_account_info(self):
        response = self.session.get(f"{self.base_url}/account")
        return response.json()

# Use broker
broker = CustomBroker(
    api_key="your_api_key",
    api_secret="your_secret",
    base_url="https://api.yourbroker.com/v1"
)

order = broker.place_order(
    symbol="AAPL",
    quantity=100,
    side="buy"
)
```

These examples demonstrate the comprehensive capabilities of the XTrade-AI framework, from basic usage to advanced trading strategies. Each example can be customized and extended based on specific requirements.
