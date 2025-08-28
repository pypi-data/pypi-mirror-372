# XTrade-AI Framework API Reference

## Table of Contents

- [Core Framework](#core-framework)
- [Configuration](#configuration)
- [Data Structures](#data-structures)
- [Data Processing](#data-processing)
- [Modules](#modules)
- [Utilities](#utilities)
- [CLI Interface](#cli-interface)

## Core Framework

### XTradeAIFramework

Main orchestrator class for the XTrade-AI framework.

**Location**: `xtrade_ai.xtrade_ai_framework`

#### Constructor

```python
XTradeAIFramework(config: Optional[XTradeAIConfig] = None)
```

**Parameters:**
- `config` (Optional[XTradeAIConfig]): Configuration object. If None, default configuration is used.

**Example:**
```python
from xtrade_ai import XTradeAIFramework, XTradeAIConfig

config = XTradeAIConfig()
framework = XTradeAIFramework(config)
```

#### Methods

##### train()

```python
train(
    data: pd.DataFrame,
    epochs: int = 100,
    validation_split: float = 0.2,
    **kwargs
) -> Dict[str, Any]
```

Train the framework with provided data.

**Parameters:**
- `data` (pd.DataFrame): Training data with OHLCV columns
- `epochs` (int): Number of training epochs (default: 100)
- `validation_split` (float): Validation data split ratio (default: 0.2)
- `**kwargs`: Additional training parameters

**Returns:**
- `Dict[str, Any]`: Training results including loss history, validation metrics

**Example:**
```python
results = framework.train(training_data, epochs=200, validation_split=0.3)
print(f"Final loss: {results['final_loss']}")
```

##### predict()

```python
predict(
    data: pd.DataFrame,
    ensemble: bool = True,
    **kwargs
) -> Dict[str, Any]
```

Make predictions on new data.

**Parameters:**
- `data` (pd.DataFrame): Market data for prediction
- `ensemble` (bool): Use ensemble prediction (default: True)
- `**kwargs`: Additional prediction parameters

**Returns:**
- `Dict[str, Any]`: Prediction results including action, confidence, model weights

**Example:**
```python
prediction = framework.predict(market_data)
print(f"Action: {prediction['action']}")
print(f"Confidence: {prediction['confidence']}")
```

##### backtest()

```python
backtest(
    data: pd.DataFrame,
    initial_balance: float = 10000.0,
    commission_rate: float = 0.001,
    **kwargs
) -> Dict[str, Any]
```

Run backtesting on historical data.

**Parameters:**
- `data` (pd.DataFrame): Historical market data
- `initial_balance` (float): Initial portfolio balance (default: 10000.0)
- `commission_rate` (float): Trading commission rate (default: 0.001)
- `**kwargs`: Additional backtesting parameters

**Returns:**
- `Dict[str, Any]`: Backtesting results including returns, Sharpe ratio, drawdown

**Example:**
```python
results = framework.backtest(historical_data, initial_balance=50000.0)
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

##### save_model()

```python
save_model(path: str, include_data: bool = False) -> None
```

Save the trained model to disk.

**Parameters:**
- `path` (str): File path to save the model
- `include_data` (bool): Include training data in save (default: False)

**Example:**
```python
framework.save_model('models/trained_model.pkl')
```

##### load_model()

```python
@classmethod
load_model(cls, path: str) -> 'XTradeAIFramework'
```

Load a trained model from disk.

**Parameters:**
- `path` (str): File path to load the model from

**Returns:**
- `XTradeAIFramework`: Loaded framework instance

**Example:**
```python
framework = XTradeAIFramework.load_model('models/trained_model.pkl')
```

##### get_model_info()

```python
get_model_info() -> Dict[str, Any]
```

Get information about all registered models.

**Returns:**
- `Dict[str, Any]`: Model information including names, states, performance

**Example:**
```python
model_info = framework.get_model_info()
for model_name, info in model_info.items():
    print(f"{model_name}: {info['state']}")
```

##### enable_model()

```python
enable_model(model_name: str) -> bool
```

Enable a specific model for predictions.

**Parameters:**
- `model_name` (str): Name of the model to enable

**Returns:**
- `bool`: True if model was enabled successfully

**Example:**
```python
success = framework.enable_model('PPO')
```

##### disable_model()

```python
disable_model(model_name: str) -> bool
```

Disable a specific model from predictions.

**Parameters:**
- `model_name` (str): Name of the model to disable

**Returns:**
- `bool`: True if model was disabled successfully

**Example:**
```python
success = framework.disable_model('XGBoost')
```

## Configuration

### XTradeAIConfig

Configuration management class for the framework.

**Location**: `xtrade_ai.config`

#### Constructor

```python
XTradeAIConfig(config_file: Optional[str] = None)
```

**Parameters:**
- `config_file` (Optional[str]): Path to configuration file (YAML/JSON)

**Example:**
```python
from xtrade_ai import XTradeAIConfig

# Create with default configuration
config = XTradeAIConfig()

# Create from file
config = XTradeAIConfig('config.yaml')
```

#### Properties

##### model

```python
model: ModelConfig
```

Model configuration including algorithm, hyperparameters, and training settings.

**Example:**
```python
config.model.baseline_algorithm = "PPO"
config.model.learning_rate = 3e-4
config.model.batch_size = 64
```

##### trading

```python
trading: TradingConfig
```

Trading configuration including balance, commission, and risk parameters.

**Example:**
```python
config.trading.initial_balance = 10000.0
config.trading.commission_rate = 0.001
config.trading.max_position_size = 0.1
```

##### data

```python
data: DataConfig
```

Data configuration including preprocessing and feature engineering settings.

**Example:**
```python
config.data.lookback_window = 100
config.data.feature_columns = ["open", "high", "low", "close", "volume"]
config.data.target_column = "returns"
```

#### Methods

##### to_dict()

```python
to_dict() -> Dict[str, Any]
```

Convert configuration to dictionary.

**Returns:**
- `Dict[str, Any]`: Configuration as dictionary

**Example:**
```python
config_dict = config.to_dict()
```

##### from_dict()

```python
from_dict(config_dict: Dict[str, Any]) -> None
```

Load configuration from dictionary.

**Parameters:**
- `config_dict` (Dict[str, Any]): Configuration dictionary

**Example:**
```python
config.from_dict(config_dict)
```

##### save()

```python
save(path: str, format: str = 'yaml') -> None
```

Save configuration to file.

**Parameters:**
- `path` (str): File path to save configuration
- `format` (str): File format ('yaml' or 'json', default: 'yaml')

**Example:**
```python
config.save('my_config.yaml')
```

##### load()

```python
load(path: str) -> None
```

Load configuration from file.

**Parameters:**
- `path` (str): File path to load configuration from

**Example:**
```python
config.load('my_config.yaml')
```

### ModelConfig

Configuration for model parameters.

**Location**: `xtrade_ai.config`

#### Attributes

```python
state_dim: int = 545
action_dim: int = 4
hidden_dim: int = 128
learning_rate: float = 3e-4
batch_size: int = 64
baseline_algorithm: str = "PPO"
enable_xgboost: bool = True
enable_risk_management: bool = True
enable_technical_analysis: bool = True
enable_monitoring: bool = True
max_episode_steps: int = 1000
n_envs: int = 4
buffer_size: int = 100000
target_update_freq: int = 1000
gradient_steps: int = 1
train_freq: int = 4
learning_starts: int = 1000
policy_kwargs: Optional[Dict[str, Any]] = None

# XGBoost specific parameters
xgb_n_estimators: int = 100
xgb_max_depth: int = 6
xgb_learning_rate: float = 0.1
xgb_top_k_features: int = 50

# Neural network specific parameters
lstm_hidden_size: int = 64
transformer_heads: int = 8
attention_dropout: float = 0.1

# Training specific parameters
validation_split: float = 0.2
early_stopping_patience: int = 10
model_checkpoint_freq: int = 1000
```

### TradingConfig

Configuration for trading parameters.

**Location**: `xtrade_ai.config`

#### Attributes

```python
initial_balance: float = 10000.0
commission_rate: float = 0.001
max_position_size: float = 0.1
stop_loss_pct: float = 0.02
take_profit_pct: float = 0.05
max_drawdown_pct: float = 0.15
risk_free_rate: float = 0.02
leverage: float = 1.0
margin_requirement: float = 0.1
slippage: float = 0.0001
min_trade_size: float = 0.01
max_trades_per_day: int = 10
cooldown_period: int = 60
```

### DataConfig

Configuration for data processing parameters.

**Location**: `xtrade_ai.config`

#### Attributes

```python
lookback_window: int = 100
feature_columns: List[str] = field(default_factory=lambda: ["open", "high", "low", "close", "volume"])
target_column: str = "returns"
train_split: float = 0.8
validation_split: float = 0.1
test_split: float = 0.1
normalization_method: str = "zscore"
technical_indicators: List[str] = field(default_factory=list)
feature_selection: bool = True
feature_selection_method: str = "mutual_info"
max_features: int = 100
```

## Data Structures

### TradingDecision

Trading decision data structure.

**Location**: `xtrade_ai.data_structures`

#### Attributes

```python
action: ActionType
confidence: float
timestamp: datetime
market_state: MarketState
risk_assessment: RiskAssessment
```

#### Example

```python
from xtrade_ai import TradingDecision, ActionType

decision = TradingDecision(
    action=ActionType.BUY,
    confidence=0.85,
    timestamp=datetime.now(),
    market_state=market_state,
    risk_assessment=risk_assessment
)
```

### MarketState

Market state data structure.

**Location**: `xtrade_ai.data_structures`

#### Attributes

```python
price: float
volume: float
technical_indicators: Dict[str, float]
market_sentiment: float
volatility: float
timestamp: datetime
```

### Portfolio

Portfolio data structure.

**Location**: `xtrade_ai.data_structures`

#### Attributes

```python
balance: float
positions: Dict[str, Position]
total_value: float
pnl: float
risk_metrics: Dict[str, float]
timestamp: datetime
```

#### Methods

##### update_position()

```python
update_position(symbol: str, quantity: float, price: float) -> None
```

Update portfolio position.

**Parameters:**
- `symbol` (str): Trading symbol
- `quantity` (float): Position quantity
- `price` (float): Current price

##### calculate_pnl()

```python
calculate_pnl() -> float
```

Calculate portfolio profit/loss.

**Returns:**
- `float`: Current P&L

##### get_risk_metrics()

```python
get_risk_metrics() -> Dict[str, float]
```

Calculate portfolio risk metrics.

**Returns:**
- `Dict[str, float]`: Risk metrics including VaR, Sharpe ratio, etc.

### ActionType

Enumeration of trading actions.

**Location**: `xtrade_ai.data_structures`

#### Values

```python
class ActionType(Enum):
    HOLD = 0
    BUY = 1
    SELL = 2
    CLOSE = 3
```

## Data Processing

### DataPreprocessor

Data preprocessing and feature engineering.

**Location**: `xtrade_ai.data_preprocessor`

#### Constructor

```python
DataPreprocessor(config: XTradeAIConfig)
```

**Parameters:**
- `config` (XTradeAIConfig): Configuration object

#### Methods

##### preprocess()

```python
preprocess(data: pd.DataFrame) -> pd.DataFrame
```

Main preprocessing pipeline.

**Parameters:**
- `data` (pd.DataFrame): Raw market data

**Returns:**
- `pd.DataFrame`: Preprocessed data

**Example:**
```python
from xtrade_ai import DataPreprocessor, XTradeAIConfig

config = XTradeAIConfig()
preprocessor = DataPreprocessor(config)
processed_data = preprocessor.preprocess(raw_data)
```

##### add_technical_indicators()

```python
add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame
```

Add technical indicators to data.

**Parameters:**
- `data` (pd.DataFrame): Market data

**Returns:**
- `pd.DataFrame`: Data with technical indicators

**Example:**
```python
data_with_indicators = preprocessor.add_technical_indicators(data)
```

##### normalize_features()

```python
normalize_features(data: pd.DataFrame) -> pd.DataFrame
```

Normalize features using specified method.

**Parameters:**
- `data` (pd.DataFrame): Data with features

**Returns:**
- `pd.DataFrame`: Normalized data

**Example:**
```python
normalized_data = preprocessor.normalize_features(data)
```

##### build_state_vector()

```python
build_state_vector(data: pd.DataFrame) -> np.ndarray
```

Build state vectors for reinforcement learning.

**Parameters:**
- `data` (pd.DataFrame): Preprocessed data

**Returns:**
- `np.ndarray`: State vectors

**Example:**
```python
state_vectors = preprocessor.build_state_vector(data)
```

##### calculate_rewards()

```python
calculate_rewards(data: pd.DataFrame, actions: np.ndarray) -> np.ndarray
```

Calculate rewards for training.

**Parameters:**
- `data` (pd.DataFrame): Market data
- `actions` (np.ndarray): Actions taken

**Returns:**
- `np.ndarray`: Calculated rewards

**Example:**
```python
rewards = preprocessor.calculate_rewards(data, actions)
```

## Modules

### Baseline3Integration

Integration with Stable-Baselines3 algorithms.

**Location**: `xtrade_ai.modules.baseline3_integration`

#### Constructor

```python
Baseline3Integration(config: XTradeAIConfig)
```

#### Methods

##### create_model()

```python
create_model(env) -> Any
```

Create Stable-Baselines3 model.

**Parameters:**
- `env`: Gymnasium environment

**Returns:**
- `Any`: Created model

##### train()

```python
train(env, total_timesteps: int) -> Dict[str, Any]
```

Train the model.

**Parameters:**
- `env`: Training environment
- `total_timesteps` (int): Total training timesteps

**Returns:**
- `Dict[str, Any]`: Training results

##### predict()

```python
predict(observation: np.ndarray) -> Tuple[np.ndarray, Optional[Dict[str, Any]]]
```

Make predictions.

**Parameters:**
- `observation` (np.ndarray): Current observation

**Returns:**
- `Tuple[np.ndarray, Optional[Dict[str, Any]]]`: Action and additional info

### XGBoostModule

XGBoost integration for gradient boosting.

**Location**: `xtrade_ai.modules.xgboost_module`

#### Constructor

```python
XGBoostModule(config: XTradeAIConfig)
```

#### Methods

##### train()

```python
train(X: np.ndarray, y: np.ndarray) -> None
```

Train XGBoost model.

**Parameters:**
- `X` (np.ndarray): Feature matrix
- `y` (np.ndarray): Target values

##### predict()

```python
predict(X: np.ndarray) -> np.ndarray
```

Make predictions.

**Parameters:**
- `X` (np.ndarray): Feature matrix

**Returns:**
- `np.ndarray`: Predictions

##### feature_importance()

```python
feature_importance() -> Dict[str, float]
```

Get feature importance scores.

**Returns:**
- `Dict[str, float]`: Feature importance mapping

### RiskManagementModule

Risk management and position sizing.

**Location**: `xtrade_ai.modules.risk_management`

#### Constructor

```python
RiskManagementModule(config: XTradeAIConfig)
```

#### Methods

##### assess_risk()

```python
assess_risk(market_state: MarketState, portfolio: Portfolio) -> RiskAssessment
```

Assess current risk level.

**Parameters:**
- `market_state` (MarketState): Current market state
- `portfolio` (Portfolio): Current portfolio

**Returns:**
- `RiskAssessment`: Risk assessment result

##### calculate_position_size()

```python
calculate_position_size(signal_strength: float, risk_level: float) -> float
```

Calculate optimal position size.

**Parameters:**
- `signal_strength` (float): Signal strength (0-1)
- `risk_level` (float): Current risk level

**Returns:**
- `float`: Optimal position size

##### check_stop_loss()

```python
check_stop_loss(position: Position, current_price: float) -> bool
```

Check if stop loss should be triggered.

**Parameters:**
- `position` (Position): Current position
- `current_price` (float): Current market price

**Returns:**
- `bool`: True if stop loss should be triggered

### TechnicalAnalysisModule

Technical indicator calculation and analysis.

**Location**: `xtrade_ai.modules.technical_analysis`

#### Constructor

```python
TechnicalAnalysisModule(config: XTradeAIConfig)
```

#### Methods

##### calculate_indicators()

```python
calculate_indicators(data: pd.DataFrame) -> pd.DataFrame
```

Calculate all technical indicators.

**Parameters:**
- `data` (pd.DataFrame): Market data

**Returns:**
- `pd.DataFrame`: Data with technical indicators

##### adaptive_parameters()

```python
adaptive_parameters(market_conditions: Dict[str, Any]) -> Dict[str, Any]
```

Adjust parameters based on market conditions.

**Parameters:**
- `market_conditions` (Dict[str, Any]): Current market conditions

**Returns:**
- `Dict[str, Any]`: Adjusted parameters

##### signal_generation()

```python
signal_generation(indicators: pd.DataFrame) -> Dict[str, float]
```

Generate trading signals from indicators.

**Parameters:**
- `indicators` (pd.DataFrame): Technical indicators

**Returns:**
- `Dict[str, float]`: Trading signals

## Utilities

### MemoryManager

Memory management and optimization.

**Location**: `xtrade_ai.utils.memory_manager`

#### Constructor

```python
MemoryManager()
```

#### Methods

##### monitor_memory()

```python
monitor_memory() -> Dict[str, float]
```

Monitor memory usage.

**Returns:**
- `Dict[str, float]`: Memory usage statistics

##### cleanup_memory()

```python
cleanup_memory() -> None
```

Perform memory cleanup.

##### optimize_memory()

```python
optimize_memory() -> None
```

Optimize memory usage.

### ThreadManager

Multi-threaded execution and task management.

**Location**: `xtrade_ai.utils.thread_manager`

#### Constructor

```python
ThreadManager(max_workers: int = 4)
```

**Parameters:**
- `max_workers` (int): Maximum number of worker threads

#### Methods

##### submit_task()

```python
submit_task(func: Callable, *args, **kwargs) -> str
```

Submit task for execution.

**Parameters:**
- `func` (Callable): Function to execute
- `*args`: Function arguments
- `**kwargs`: Function keyword arguments

**Returns:**
- `str`: Task ID

##### wait_for_all()

```python
wait_for_all() -> List[Any]
```

Wait for all tasks to complete.

**Returns:**
- `List[Any]`: Task results

##### cancel_task()

```python
cancel_task(task_id: str) -> bool
```

Cancel running task.

**Parameters:**
- `task_id` (str): Task ID to cancel

**Returns:**
- `bool`: True if task was cancelled

### ErrorHandler

Error handling and recovery.

**Location**: `xtrade_ai.utils.error_handler`

#### Constructor

```python
ErrorHandler()
```

#### Methods

##### handle_error()

```python
handle_error(error: Exception, context: Dict[str, Any]) -> None
```

Handle errors with appropriate recovery strategies.

**Parameters:**
- `error` (Exception): Error to handle
- `context` (Dict[str, Any]): Error context

##### log_error()

```python
log_error(error: Exception, context: Dict[str, Any]) -> None
```

Log error for analysis.

**Parameters:**
- `error` (Exception): Error to log
- `context` (Dict[str, Any]): Error context

##### recover_from_error()

```python
recover_from_error(error_type: str) -> bool
```

Attempt to recover from error.

**Parameters:**
- `error_type` (str): Type of error to recover from

**Returns:**
- `bool`: True if recovery was successful

### Logger

Logging utilities.

**Location**: `xtrade_ai.utils.logger`

#### Functions

##### get_logger()

```python
get_logger(name: str = None, level: str = "INFO") -> logging.Logger
```

Get configured logger instance.

**Parameters:**
- `name` (str): Logger name
- `level` (str): Logging level

**Returns:**
- `logging.Logger`: Configured logger

**Example:**
```python
from xtrade_ai.utils.logger import get_logger

logger = get_logger("my_module", "DEBUG")
logger.info("This is an info message")
```

## CLI Interface

### Main CLI Commands

#### version

```bash
xtrade-ai version
```

Show framework version and information.

#### health

```bash
xtrade-ai health
```

Check framework health and dependencies.

#### train

```bash
xtrade-ai train --config config.yaml --data training_data.csv
```

Train a model.

**Options:**
- `--config, -c`: Configuration file path
- `--data, -d`: Training data file path
- `--epochs, -e`: Number of training epochs
- `--output, -o`: Output model file path

#### predict

```bash
xtrade-ai predict --model model.pkl --data market_data.csv
```

Make predictions.

**Options:**
- `--model, -m`: Model file path
- `--data, -d`: Market data file path
- `--output, -o`: Output file path

#### backtest

```bash
xtrade-ai backtest --model model.pkl --data historical_data.csv
```

Run backtesting.

**Options:**
- `--model, -m`: Model file path
- `--data, -d`: Historical data file path
- `--initial-balance`: Initial portfolio balance
- `--commission-rate`: Trading commission rate
- `--output, -o`: Output file path

#### validate

```bash
xtrade-ai validate --data data.csv
```

Validate data quality.

**Options:**
- `--data, -d`: Data file path
- `--config, -c`: Configuration file path

#### optimize

```bash
xtrade-ai optimize --config config.yaml --data data.csv
```

Optimize hyperparameters.

**Options:**
- `--config, -c`: Configuration file path
- `--data, -d`: Data file path
- `--trials`: Number of optimization trials
- `--output, -o`: Output file path

### CLI Configuration

The CLI supports configuration through:

1. **Command line arguments**: Direct parameter specification
2. **Configuration files**: YAML/JSON configuration files
3. **Environment variables**: Environment variable overrides

**Example configuration file (config.yaml):**
```yaml
model:
  baseline_algorithm: "PPO"
  learning_rate: 3e-4
  batch_size: 64

trading:
  initial_balance: 10000.0
  commission_rate: 0.001

data:
  lookback_window: 100
  feature_columns: ["open", "high", "low", "close", "volume"]
```

**Example usage with configuration:**
```bash
xtrade-ai train --config config.yaml --data data.csv --epochs 200
```

### CLI Output Formats

The CLI supports multiple output formats:

1. **JSON**: Machine-readable output
2. **CSV**: Tabular data output
3. **Human-readable**: Formatted text output

**Example:**
```bash
# JSON output
xtrade-ai predict --model model.pkl --data data.csv --format json

# CSV output
xtrade-ai backtest --model model.pkl --data data.csv --format csv
```
