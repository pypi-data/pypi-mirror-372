"""
Command Line Interface for XTrade-AI Framework.

This module provides a comprehensive CLI for interacting with the XTrade-AI framework,
including training, prediction, backtesting, and model management.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import click
import yaml

# Import framework components
try:
    from . import XTradeAIConfig, XTradeAIFramework, get_info, get_version, health_check
    from .data_preprocessor import DataPreprocessor
    from .utils.model_manager import ModelManager
    from .utils.performance_monitor import PerformanceMonitor
except ImportError as e:
    print(f"Error importing framework components: {e}")
    sys.exit(1)


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler("xtrade_ai.log")],
    )


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Configuration file path"
)
@click.pass_context
def cli(ctx, verbose: bool, config: Optional[str]):
    """
    XTrade-AI Framework Command Line Interface.

    A comprehensive trading framework with deep learning and reinforcement learning capabilities.
    """
    setup_logging(verbose)

    # Store configuration in context
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["config"] = config

    # Load configuration if provided
    if config:
        try:
            config_path = Path(config)
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                with open(config_path, "r") as f:
                    ctx.obj["config_data"] = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                with open(config_path, "r") as f:
                    ctx.obj["config_data"] = json.load(f)
        except Exception as e:
            click.echo(f"Error loading configuration: {e}", err=True)
            sys.exit(1)


@cli.command()
def version():
    """Show framework version and information."""
    info = get_info()
    click.echo(f"XTrade-AI Framework v{info['version']}")
    click.echo(f"Author: {info['author']}")
    click.echo(f"Email: {info['email']}")
    click.echo(f"GitHub: {info['github']}")
    click.echo(f"Description: {info['description']}")


@cli.command()
def health():
    """Check framework health and dependencies."""
    health_status = health_check()

    if health_status["overall_status"] == "healthy":
        click.echo("✅ Framework is healthy!")
    else:
        click.echo(f"❌ Framework has issues: {health_status['overall_status']}")

    click.echo("\nDependencies:")
    for dep, available in health_status["dependencies"].items():
        status = "✅" if available else "❌"
        click.echo(f"  {status} {dep}")

    click.echo("\nCritical Components:")
    for component, available in health_status["critical_components"].items():
        status = "✅" if available else "❌"
        click.echo(f"  {status} {component}")


@cli.command()
@click.option("--data-path", "-d", required=True, help="Path to market data file")
@click.option(
    "--output-path", "-o", default="./models", help="Output path for trained models"
)
@click.option("--epochs", "-e", default=100, help="Number of training epochs")
@click.option(
    "--algorithm", "-a", default="PPO", help="RL algorithm to use (PPO/DQN/SAC)"
)
@click.option("--validation-split", default=0.2, help="Validation data split ratio")
@click.pass_context
def train(
    ctx,
    data_path: str,
    output_path: str,
    epochs: int,
    algorithm: str,
    validation_split: float,
):
    """Train the XTrade-AI framework on market data."""
    try:
        # Load configuration
        if ctx.obj.get("config_data"):
            config = XTradeAIConfig.from_dict(ctx.obj["config_data"])
        else:
            config = XTradeAIConfig()

        # Update config with CLI parameters
        config.model.baseline_algorithm = algorithm
        config.model.validation_split = validation_split
        config.save_path = output_path

        click.echo(f"Initializing XTrade-AI Framework...")
        framework = XTradeAIFramework(config)

        # Load and preprocess data
        click.echo(f"Loading data from {data_path}...")
        data_path = Path(data_path)

        if data_path.suffix.lower() == ".csv":
            import pandas as pd

            market_data = pd.read_csv(data_path)
        elif data_path.suffix.lower() in [".parquet", ".pq"]:
            import pandas as pd

            market_data = pd.read_parquet(data_path)
        else:
            click.echo(f"Unsupported file format: {data_path.suffix}", err=True)
            return

        # Preprocess data
        click.echo("Preprocessing data...")
        preprocessor = DataPreprocessor(config.to_dict())
        processed_data = preprocessor.preprocess_data(market_data)

        # Convert to numpy array for training
        training_data = processed_data.values

        # Split data
        split_idx = int(len(training_data) * (1 - validation_split))
        train_data = training_data[:split_idx]
        val_data = training_data[split_idx:]

        click.echo(f"Training data shape: {train_data.shape}")
        click.echo(f"Validation data shape: {val_data.shape}")

        # Train framework
        click.echo(f"Starting training with {algorithm} for {epochs} epochs...")
        results = framework.train(train_data, epochs=epochs, validation_data=val_data)

        # Save models
        click.echo(f"Saving models to {output_path}...")
        framework.save_model(output_path)

        # Display results
        click.echo("\nTraining Results:")
        for model_name, result in results.items():
            click.echo(f"  {model_name}: {result}")

        click.echo("✅ Training completed successfully!")

    except Exception as e:
        click.echo(f"❌ Training failed: {e}", err=True)
        if ctx.obj["verbose"]:
            import traceback

            traceback.print_exc()


@cli.command()
@click.option("--data-path", "-d", required=True, help="Path to market data file")
@click.option("--model-path", "-m", required=True, help="Path to trained model")
@click.option(
    "--output-path",
    "-o",
    default="./predictions.json",
    help="Output path for predictions",
)
@click.pass_context
def predict(ctx, data_path: str, model_path: str, output_path: str):
    """Make predictions using trained models."""
    try:
        # Load configuration
        if ctx.obj.get("config_data"):
            config = XTradeAIConfig.from_dict(ctx.obj["config_data"])
        else:
            config = XTradeAIConfig()

        click.echo(f"Loading framework from {model_path}...")
        framework = XTradeAIFramework(config)
        if not framework.load_model(model_path, critical=False):
            click.echo(
                f"Warning: Could not load models from {model_path}, proceeding without pre-trained models"
            )

        # Load and preprocess data
        click.echo(f"Loading data from {data_path}...")
        data_path = Path(data_path)

        if data_path.suffix.lower() == ".csv":
            import pandas as pd

            market_data = pd.read_csv(data_path)
        elif data_path.suffix.lower() in [".parquet", ".pq"]:
            import pandas as pd

            market_data = pd.read_parquet(data_path)
        else:
            click.echo(f"Unsupported file format: {data_path.suffix}", err=True)
            return

        # Preprocess data
        click.echo("Preprocessing data...")
        preprocessor = DataPreprocessor(config.to_dict())
        processed_data = preprocessor.preprocess_data(market_data)

        # Make predictions
        click.echo("Making predictions...")
        predictions = []

        for i in range(len(processed_data)):
            data_point = processed_data.iloc[i : i + 1].values
            prediction = framework.predict(data_point)
            predictions.append(
                {
                    "timestamp": (
                        market_data.index[i]
                        if hasattr(market_data.index[i], "isoformat")
                        else str(i)
                    ),
                    "prediction": prediction,
                }
            )

        # Save predictions
        click.echo(f"Saving predictions to {output_path}...")
        with open(output_path, "w") as f:
            json.dump(predictions, f, indent=2)

        # Display summary
        actions = [p["prediction"]["action"] for p in predictions]
        action_counts = {}
        for action in actions:
            action_counts[action] = action_counts.get(action, 0) + 1

        click.echo("\nPrediction Summary:")
        for action, count in action_counts.items():
            percentage = (count / len(actions)) * 100
            click.echo(f"  {action}: {count} ({percentage:.1f}%)")

        click.echo("✅ Predictions completed successfully!")

    except Exception as e:
        click.echo(f"❌ Prediction failed: {e}", err=True)
        if ctx.obj["verbose"]:
            import traceback

            traceback.print_exc()


@cli.command()
@click.option("--data-path", "-d", required=True, help="Path to market data file")
@click.option("--model-path", "-m", required=True, help="Path to trained model")
@click.option(
    "--output-path",
    "-o",
    default="./backtest_results",
    help="Output path for backtest results",
)
@click.option("--initial-balance", default=10000.0, help="Initial account balance")
@click.pass_context
def backtest(
    ctx, data_path: str, model_path: str, output_path: str, initial_balance: float
):
    """Run backtest on historical data."""
    try:
        # Load configuration
        if ctx.obj.get("config_data"):
            config = XTradeAIConfig.from_dict(ctx.obj["config_data"])
        else:
            config = XTradeAIConfig()

        config.trading.initial_balance = initial_balance

        click.echo(f"Loading framework from {model_path}...")
        framework = XTradeAIFramework(config)
        if not framework.load_model(model_path, critical=False):
            click.echo(
                f"Warning: Could not load models from {model_path}, proceeding without pre-trained models"
            )

        # Load and preprocess data
        click.echo(f"Loading data from {data_path}...")
        data_path = Path(data_path)

        if data_path.suffix.lower() == ".csv":
            import pandas as pd

            market_data = pd.read_csv(data_path)
        elif data_path.suffix.lower() in [".parquet", ".pq"]:
            import pandas as pd

            market_data = pd.read_parquet(data_path)
        else:
            click.echo(f"Unsupported file format: {data_path.suffix}", err=True)
            return

        # Preprocess data
        click.echo("Preprocessing data...")
        preprocessor = DataPreprocessor(config.to_dict())
        processed_data = preprocessor.preprocess_data(market_data)

        # Run backtest
        click.echo("Running backtest...")
        results = framework.backtest(processed_data.values)

        # Initialize performance monitor
        monitor = PerformanceMonitor(initial_balance)

        # Simulate trading
        balance = initial_balance
        for i in range(len(processed_data)):
            data_point = processed_data.iloc[i : i + 1].values
            prediction = framework.predict(data_point)

            # Simple trading simulation
            current_price = market_data.iloc[i]["close"]

            if prediction["action"] == "BUY" and balance > 0:
                # Simple buy logic
                trade_amount = balance * 0.1  # Use 10% of balance
                balance -= trade_amount
                # In a real implementation, you'd track positions
            elif prediction["action"] == "SELL":
                # Simple sell logic
                # In a real implementation, you'd close positions
                pass

            monitor.update_balance(balance, timestamp=datetime.now())

        # Calculate performance metrics
        metrics = monitor.calculate_metrics()

        # Save results
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save backtest results
        with open(output_path / "backtest_results.json", "w") as f:
            json.dump(results, f, indent=2)

        # Save performance metrics
        with open(output_path / "performance_metrics.json", "w") as f:
            json.dump(metrics.to_dict(), f, indent=2)

        # Generate report
        report = monitor.generate_report(str(output_path / "performance_report.txt"))

        # Create plots
        monitor.plot_equity_curve(str(output_path / "equity_curve.png"))
        monitor.plot_trade_analysis(str(output_path / "trade_analysis.png"))

        # Display summary
        click.echo("\nBacktest Results:")
        click.echo(f"  Total Return: {metrics.total_return:.2%}")
        click.echo(f"  Sharpe Ratio: {metrics.sharpe_ratio:.2f}")
        click.echo(f"  Max Drawdown: {metrics.max_drawdown:.2%}")
        click.echo(f"  Win Rate: {metrics.win_rate:.2%}")
        click.echo(f"  Total Trades: {metrics.total_trades}")

        click.echo(f"\nResults saved to: {output_path}")
        click.echo("✅ Backtest completed successfully!")

    except Exception as e:
        click.echo(f"❌ Backtest failed: {e}", err=True)
        if ctx.obj["verbose"]:
            import traceback

            traceback.print_exc()


@cli.group()
def model():
    """Model management commands."""
    pass


@model.command("list")
@click.option("--model-path", "-m", default="./models", help="Path to models directory")
def list_models(model_path: str):
    """List all available models."""
    try:
        manager = ModelManager(model_path)
        models = manager.list_models()

        if not models:
            click.echo("No models found.")
            return

        click.echo(f"Found {len(models)} models:")
        for model_info in models:
            click.echo(f"\n📁 {model_info['name']}")
            click.echo(f"   Latest Version: {model_info['latest_version']}")
            click.echo(f"   Total Versions: {model_info['total_versions']}")

            # Show latest version details
            latest_version = model_info["versions"][0]
            click.echo(f"   Created: {latest_version['created_at']}")
            click.echo(f"   Size: {latest_version['model_size']:,} bytes")

            if latest_version["tags"]:
                click.echo(f"   Tags: {', '.join(latest_version['tags'])}")

    except Exception as e:
        click.echo(f"❌ Failed to list models: {e}", err=True)


@model.command("info")
@click.argument("model_name")
@click.option("--version", "-v", help="Model version (latest if not specified)")
@click.option("--model-path", "-m", default="./models", help="Path to models directory")
def model_info(model_name: str, version: Optional[str], model_path: str):
    """Show detailed information about a model."""
    try:
        manager = ModelManager(model_path)
        model, metadata = manager.load_model(model_name, version)

        click.echo(f"📊 Model Information: {model_name}")
        click.echo(f"   Version: {metadata.version}")
        click.echo(f"   Created: {metadata.created_at}")
        click.echo(f"   Framework Version: {metadata.framework_version}")
        click.echo(f"   Size: {metadata.model_size:,} bytes")
        click.echo(f"   Checksum: {metadata.checksum[:16]}...")

        if metadata.tags:
            click.echo(f"   Tags: {', '.join(metadata.tags)}")

        if metadata.description:
            click.echo(f"   Description: {metadata.description}")

        click.echo(f"\n📈 Performance Metrics:")
        for metric, value in metadata.performance_metrics.items():
            if isinstance(value, float):
                click.echo(f"   {metric}: {value:.4f}")
            else:
                click.echo(f"   {metric}: {value}")

        click.echo(f"\n🔧 Dependencies:")
        for dep, version in metadata.dependencies.items():
            click.echo(f"   {dep}: {version}")

        click.echo(f"\n⚙️  Configuration:")
        for key, value in metadata.config.items():
            click.echo(f"   {key}: {value}")

    except Exception as e:
        click.echo(f"❌ Failed to get model info: {e}", err=True)


@model.command("delete")
@click.argument("model_name")
@click.option("--version", "-v", help="Model version (all versions if not specified)")
@click.option("--model-path", "-m", default="./models", help="Path to models directory")
@click.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
def delete_model(model_name: str, version: Optional[str], model_path: str, force: bool):
    """Delete a model or model version."""
    try:
        if not force:
            if version:
                confirm = click.confirm(
                    f"Are you sure you want to delete {model_name} v{version}?"
                )
            else:
                confirm = click.confirm(
                    f"Are you sure you want to delete all versions of {model_name}?"
                )

            if not confirm:
                click.echo("Deletion cancelled.")
                return

        manager = ModelManager(model_path)
        success = manager.delete_model(model_name, version)

        if success:
            if version:
                click.echo(f"✅ Deleted {model_name} v{version}")
            else:
                click.echo(f"✅ Deleted all versions of {model_name}")
        else:
            click.echo(f"❌ Failed to delete model")

    except Exception as e:
        click.echo(f"❌ Failed to delete model: {e}", err=True)


@model.command("deploy")
@click.argument("model_name")
@click.option("--version", "-v", help="Model version (latest if not specified)")
@click.option(
    "--deployment-name", "-d", help="Deployment name (auto-generated if not specified)"
)
@click.option("--model-path", "-m", default="./models", help="Path to models directory")
def deploy_model(
    model_name: str,
    version: Optional[str],
    deployment_name: Optional[str],
    model_path: str,
):
    """Deploy a model for serving."""
    try:
        manager = ModelManager(model_path)
        deployment_id = manager.deploy_model(model_name, version, deployment_name)

        click.echo(f"✅ Model {model_name} deployed as {deployment_id}")

        # Show deployment status
        status = manager.get_deployment_status(deployment_id)
        click.echo(f"   Status: {status['status']}")
        click.echo(f"   Endpoint: {status['endpoint']}")

    except Exception as e:
        click.echo(f"❌ Failed to deploy model: {e}", err=True)


@model.command("list-deployments")
@click.option("--model-path", "-m", default="./models", help="Path to models directory")
def list_deployments(model_path: str):
    """List all model deployments."""
    try:
        manager = ModelManager(model_path)
        deployments = manager.list_deployments()

        if not deployments:
            click.echo("No deployments found.")
            return

        click.echo(f"Found {len(deployments)} deployments:")
        for deployment in deployments:
            click.echo(f"\n🚀 {deployment['deployment_name']}")
            click.echo(
                f"   Model: {deployment['model_name']} v{deployment['model_version']}"
            )
            click.echo(f"   Status: {deployment['status']}")
            click.echo(f"   Deployed: {deployment['deployed_at']}")
            click.echo(f"   Endpoint: {deployment['endpoint']}")

    except Exception as e:
        click.echo(f"❌ Failed to list deployments: {e}", err=True)


@cli.command()
@click.option(
    "--config-template",
    "-t",
    default="config_template.yaml",
    help="Output path for config template",
)
def init(config_template: str):
    """Initialize a new XTrade-AI project with configuration template."""
    try:
        # Create default configuration
        config = XTradeAIConfig()

        # Save configuration template
        config.save(config_template)

        click.echo(f"✅ Configuration template created: {config_template}")
        click.echo("\nNext steps:")
        click.echo("1. Edit the configuration file to match your requirements")
        click.echo("2. Prepare your market data")
        click.echo("3. Run 'xtrade-ai train' to start training")
        click.echo("4. Run 'xtrade-ai predict' to make predictions")
        click.echo("5. Run 'xtrade-ai backtest' to evaluate performance")

    except Exception as e:
        click.echo(f"❌ Failed to initialize project: {e}", err=True)


@cli.command()
@click.option("--data-path", "-d", required=True, help="Path to market data file")
@click.option(
    "--output-path",
    "-o",
    default="./preprocessed_data.csv",
    help="Output path for preprocessed data",
)
@click.option("--indicators", "-i", help="Comma-separated list of technical indicators")
@click.pass_context
def preprocess(ctx, data_path: str, output_path: str, indicators: Optional[str]):
    """Preprocess market data with technical indicators."""
    try:
        # Load configuration
        if ctx.obj.get("config_data"):
            config = XTradeAIConfig.from_dict(ctx.obj["config_data"])
        else:
            config = XTradeAIConfig()

        # Parse indicators
        technical_indicators = None
        if indicators:
            technical_indicators = [ind.strip() for ind in indicators.split(",")]

        click.echo(f"Loading data from {data_path}...")
        data_path = Path(data_path)

        if data_path.suffix.lower() == ".csv":
            import pandas as pd

            market_data = pd.read_csv(data_path)
        elif data_path.suffix.lower() in [".parquet", ".pq"]:
            import pandas as pd

            market_data = pd.read_parquet(data_path)
        else:
            click.echo(f"Unsupported file format: {data_path.suffix}", err=True)
            return

        click.echo(f"Original data shape: {market_data.shape}")

        # Preprocess data
        click.echo("Preprocessing data...")
        preprocessor = DataPreprocessor(config.to_dict())
        processed_data = preprocessor.preprocess_data(market_data, technical_indicators)

        click.echo(f"Processed data shape: {processed_data.shape}")

        # Save preprocessed data
        click.echo(f"Saving preprocessed data to {output_path}...")
        processed_data.to_csv(output_path, index=False)

        # Show feature importance
        feature_importance = preprocessor.get_feature_importance(processed_data)
        click.echo("\nTop 10 Most Important Features:")
        for i, (feature, importance) in enumerate(
            list(feature_importance.items())[:10]
        ):
            click.echo(f"  {i+1}. {feature}: {importance:.4f}")

        click.echo("✅ Data preprocessing completed successfully!")

    except Exception as e:
        click.echo(f"❌ Data preprocessing failed: {e}", err=True)
        if ctx.obj["verbose"]:
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    cli()
