"""
XTrade-AI Logger Module

Provides logging functionality for the framework.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    log_level: str = "INFO", log_file: Optional[str] = None, log_dir: str = "logs"
) -> None:
    """Setup logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file name
        log_dir: Directory for log files
    """
    # Create log directory if needed
    if log_file:
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Generate log file name with timestamp if not provided
        if log_file == "auto":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = log_path / f"xtrade_ai_{timestamp}.log"
        else:
            log_file = log_path / log_file

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Setup handlers
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )

    # Set third-party library log levels
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class TradingLogger:
    """Specialized logger for trading events"""

    def __init__(self, name: str = "TradingLogger"):
        self.logger = get_logger(name)

    def log_trade(
        self, action: str, symbol: str, quantity: float, price: float, **kwargs
    ):
        """Log trading action"""
        self.logger.info(
            f"TRADE: {action} {quantity} {symbol} @ {price:.4f}", extra=kwargs
        )

    def log_position_opened(
        self, position_id: str, side: str, entry_price: float, quantity: float
    ):
        """Log position opening"""
        self.logger.info(
            f"POSITION OPENED: {position_id} - {side} {quantity} @ {entry_price:.4f}"
        )

    def log_position_closed(
        self, position_id: str, exit_price: float, pnl: float, pnl_pct: float
    ):
        """Log position closing"""
        color = "🟢" if pnl > 0 else "🔴"
        self.logger.info(
            f"POSITION CLOSED: {position_id} @ {exit_price:.4f} - "
            f"PnL: {color} ${pnl:.2f} ({pnl_pct:.2%})"
        )

    def log_model_prediction(self, model_name: str, prediction: str, confidence: float):
        """Log model prediction"""
        self.logger.debug(
            f"MODEL PREDICTION: {model_name} - {prediction} (confidence: {confidence:.2%})"
        )

    def log_risk_alert(self, risk_score: float, message: str):
        """Log risk alert"""
        level = logging.WARNING if risk_score > 0.7 else logging.INFO
        self.logger.log(level, f"RISK ALERT: Score={risk_score:.2f} - {message}")

    def log_performance_metrics(self, metrics: dict):
        """Log performance metrics"""
        self.logger.info(
            f"PERFORMANCE: Win Rate={metrics.get('win_rate', 0):.2%}, "
            f"Sharpe={metrics.get('sharpe_ratio', 0):.2f}, "
            f"Total PnL=${metrics.get('total_pnl', 0):.2f}"
        )

    def log_training_progress(self, epoch: int, loss: float, **kwargs):
        """Log training progress"""
        self.logger.info(f"TRAINING: Epoch {epoch} - Loss: {loss:.4f}", extra=kwargs)

    def log_error(self, error: Exception, context: str = ""):
        """Log error with context"""
        self.logger.error(
            f"ERROR in {context}: {type(error).__name__}: {str(error)}", exc_info=True
        )

    def log_market_update(self, symbol: str, price: float, volume: float, **kwargs):
        """Log market update"""
        self.logger.debug(
            f"MARKET: {symbol} - Price: {price:.4f}, Volume: {volume:.0f}", extra=kwargs
        )
