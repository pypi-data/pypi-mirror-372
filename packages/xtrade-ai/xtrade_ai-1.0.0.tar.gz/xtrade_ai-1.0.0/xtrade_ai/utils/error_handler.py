"""
XTrade-AI Error Handler

Provides comprehensive error handling and recovery mechanisms.
"""

import sys
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

try:
    from .logger import get_logger
except ImportError:
    import logging

    def get_logger(name):
        return logging.getLogger(name)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories."""

    IMPORT = "import"
    MEMORY = "memory"
    THREAD = "thread"
    TRADING = "trading"
    MODEL = "model"
    CONFIGURATION = "configuration"
    NETWORK = "network"
    VALIDATION = "validation"
    TEST = "test"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Information about an error."""

    error_type: str
    message: str
    severity: ErrorSeverity
    category: ErrorCategory
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    recovery_action: Optional[str] = None


class FrameworkError(Exception):
    """Base exception for framework errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: Dict[str, Any] = None,
    ):
        super().__init__(message)
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.timestamp = datetime.now()


class TradingError(FrameworkError):
    """Trading-specific errors."""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.TRADING, context)


class ModelError(FrameworkError):
    """Model-related errors."""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(message, ErrorSeverity.HIGH, ErrorCategory.MODEL, context)


class ConfigurationError(FrameworkError):
    """Configuration-related errors."""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(
            message, ErrorSeverity.MEDIUM, ErrorCategory.CONFIGURATION, context
        )


class ValidationError(FrameworkError):
    """Validation errors."""

    def __init__(self, message: str, context: Dict[str, Any] = None):
        super().__init__(
            message, ErrorSeverity.MEDIUM, ErrorCategory.VALIDATION, context
        )


class ErrorHandler:
    """Comprehensive error handling system."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_counts: Dict[str, int] = {}
        self.error_history: List[ErrorInfo] = []
        self.max_error_history = 1000
        self.recovery_strategies: Dict[ErrorCategory, List[Callable]] = {}
        self.error_callbacks: List[Callable] = []

        # Register default recovery strategies
        self._register_default_strategies()

    def handle_error(
        self,
        error: Exception,
        context: str,
        severity: ErrorSeverity = None,
        category: ErrorCategory = None,
    ) -> ErrorInfo:
        """
        Handle an error with comprehensive logging and recovery.

        Args:
            error: The exception that occurred
            context: Context where the error occurred
            severity: Error severity (auto-detected if None)
            category: Error category (auto-detected if None)

        Returns:
            ErrorInfo object
        """
        # Auto-detect severity and category if not provided
        if severity is None:
            severity = self._detect_severity(error)

        if category is None:
            category = self._detect_category(error)

        # Handle string category input
        if isinstance(category, str):
            try:
                category = ErrorCategory(category)
            except ValueError:
                category = ErrorCategory.UNKNOWN

        # Create error info
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            message=str(error),
            severity=severity,
            category=category,
            timestamp=datetime.now(),
            context={"context": context},
            stack_trace=traceback.format_exc(),
        )

        # Log error
        self._log_error(error_info)

        # Update error counts
        error_key = f"{error_info.error_type}_{error_info.category.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # Add to history
        self.error_history.append(error_info)
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)

        # Execute recovery strategies
        self._execute_recovery_strategies(error_info)

        # Execute callbacks
        self._execute_callbacks(error_info)

        # Check if too many errors
        if self._should_stop_execution(error_key):
            self.logger.critical(f"Too many {error_key} errors, stopping execution")
            raise error

        return error_info

    def _detect_severity(self, error: Exception) -> ErrorSeverity:
        """Auto-detect error severity."""
        error_type = type(error).__name__.lower()

        if any(keyword in error_type for keyword in ["critical", "fatal", "panic"]):
            return ErrorSeverity.CRITICAL
        elif any(keyword in error_type for keyword in ["high", "severe", "serious"]):
            return ErrorSeverity.HIGH
        elif any(keyword in error_type for keyword in ["medium", "moderate"]):
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW

    def _detect_category(self, error: Exception) -> ErrorCategory:
        """Auto-detect error category."""
        error_type = type(error).__name__.lower()
        error_message = str(error).lower()

        if any(
            keyword in error_type or keyword in error_message
            for keyword in ["import", "module", "package"]
        ):
            return ErrorCategory.IMPORT
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["memory", "outofmemory", "memoryerror"]
        ):
            return ErrorCategory.MEMORY
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["thread", "concurrent", "lock"]
        ):
            return ErrorCategory.THREAD
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["trade", "order", "position", "balance"]
        ):
            return ErrorCategory.TRADING
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["model", "neural", "tensor", "gradient"]
        ):
            return ErrorCategory.MODEL
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["config", "setting", "parameter"]
        ):
            return ErrorCategory.CONFIGURATION
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["network", "connection", "timeout", "http"]
        ):
            return ErrorCategory.NETWORK
        elif any(
            keyword in error_type or keyword in error_message
            for keyword in ["validation", "invalid", "format"]
        ):
            return ErrorCategory.VALIDATION
        else:
            return ErrorCategory.UNKNOWN

    def _log_error(self, error_info: ErrorInfo):
        """Log error with appropriate level."""
        log_message = f"Error in {error_info.context.get('context', 'unknown')}: {error_info.message}"

        if error_info.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_info.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_info.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

        # Log stack trace for high severity errors
        if (
            error_info.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]
            and error_info.stack_trace
        ):
            self.logger.debug(f"Stack trace: {error_info.stack_trace}")

    def _execute_recovery_strategies(self, error_info: ErrorInfo):
        """Execute recovery strategies for the error category."""
        if error_info.category in self.recovery_strategies:
            for strategy in self.recovery_strategies[error_info.category]:
                try:
                    strategy(error_info)
                except Exception as e:
                    self.logger.warning(f"Recovery strategy failed: {e}")

    def _execute_callbacks(self, error_info: ErrorInfo):
        """Execute error callbacks."""
        for callback in self.error_callbacks:
            try:
                callback(error_info)
            except Exception as e:
                self.logger.warning(f"Error callback failed: {e}")

    def _should_stop_execution(self, error_key: str) -> bool:
        """Check if execution should stop due to too many errors."""
        error_count = self.error_counts.get(error_key, 0)

        # Stop after 10 critical errors or 50 high severity errors
        if error_count >= 10:
            return True

        return False

    def _register_default_strategies(self):
        """Register default recovery strategies."""
        from .memory_manager import force_cleanup
        from .thread_manager import get_thread_manager

        # Memory error recovery
        self.register_recovery_strategy(
            ErrorCategory.MEMORY, lambda error_info: force_cleanup()
        )

        # Thread error recovery
        self.register_recovery_strategy(
            ErrorCategory.THREAD,
            lambda error_info: get_thread_manager().cleanup_completed_tasks(),
        )

        # Import error recovery
        self.register_recovery_strategy(
            ErrorCategory.IMPORT,
            lambda error_info: self._handle_import_error(error_info),
        )

    def _handle_import_error(self, error_info: ErrorInfo):
        """Handle import errors."""
        # Try to clear import cache
        try:
            from .import_manager import get_import_manager

            import_manager = get_import_manager()
            import_manager.clear_cache()
        except Exception:
            pass

    def register_recovery_strategy(self, category: ErrorCategory, strategy: Callable):
        """Register a recovery strategy for an error category."""
        if category not in self.recovery_strategies:
            self.recovery_strategies[category] = []
        self.recovery_strategies[category].append(strategy)

    def register_error_callback(self, callback: Callable):
        """Register an error callback."""
        self.error_callbacks.append(callback)

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics."""
        return {
            "error_counts": self.error_counts.copy(),
            "total_errors": len(self.error_history),
            "recent_errors": [error_info for error_info in self.error_history[-10:]],
            "severity_distribution": self._get_severity_distribution(),
            "category_distribution": self._get_category_distribution(),
        }

    def _get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of error severities."""
        distribution = {}
        for error_info in self.error_history:
            severity = error_info.severity.value
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution

    def _get_category_distribution(self) -> Dict[str, int]:
        """Get distribution of error categories."""
        distribution = {}
        for error_info in self.error_history:
            category = error_info.category.value
            distribution[category] = distribution.get(category, 0) + 1
        return distribution

    def clear_error_history(self):
        """Clear error history."""
        self.error_history.clear()
        self.error_counts.clear()
        self.logger.info("Error history cleared")


# Global error handler instance
_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _error_handler


def handle_error(error: Exception, context: str, **kwargs) -> ErrorInfo:
    """Convenience function for handling errors."""
    return _error_handler.handle_error(error, context, **kwargs)


def register_recovery_strategy(category: ErrorCategory, strategy: Callable):
    """Convenience function for registering recovery strategies."""
    _error_handler.register_recovery_strategy(category, strategy)


def register_error_callback(callback: Callable):
    """Convenience function for registering error callbacks."""
    _error_handler.register_error_callback(callback)
