"""
Advanced logging functionality for Syntha SDK.

Provides structured logging with:
- Context-aware logging
- Performance tracking
- Security event logging
- Multi-format output (JSON, detailed, standard)
- File rotation and management
"""

import json
import logging
import logging.handlers
import os
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union


class SynthaFormatter(logging.Formatter):
    """Custom formatter for Syntha logs."""

    def __init__(self, format_type: str = "standard", include_context: bool = True):
        """
        Initialize formatter.

        Args:
            format_type: Format type (standard, detailed, json)
            include_context: Whether to include context in logs
        """
        super().__init__()
        self.format_type = format_type
        self.include_context = include_context

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        if self.format_type == "json":
            return self._format_json(record)
        elif self.format_type == "detailed":
            return self._format_detailed(record)
        else:
            return self._format_standard(record)

    def _format_json(self, record: logging.LogRecord) -> str:
        """Format as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add context if available
        if self.include_context and hasattr(record, "context"):
            log_data["context"] = record.context

        # Add agent information if available
        if hasattr(record, "agent_name"):
            log_data["agent_name"] = record.agent_name

        # Add performance metrics if available
        if hasattr(record, "metrics"):
            log_data["metrics"] = record.metrics

        # Add security context if available
        if hasattr(record, "security_context"):
            log_data["security_context"] = record.security_context

        # Add exception information
        if record.exc_info:
            log_data["exception"] = {
                "type": (
                    record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
                ),
                "message": str(record.exc_info[1]) if record.exc_info[1] else "Unknown",
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data)

    def _format_detailed(self, record: logging.LogRecord) -> str:
        """Format with detailed information."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S")
        base_msg = f"[{timestamp}] [{record.levelname:8}] [{record.name}] {record.getMessage()}"

        # Add context information
        context_parts = []
        if self.include_context and hasattr(record, "context") and record.context:
            context_parts.append(f"Context: {record.context}")

        if hasattr(record, "agent_name") and record.agent_name:
            context_parts.append(f"Agent: {record.agent_name}")

        if hasattr(record, "metrics") and record.metrics:
            context_parts.append(f"Metrics: {record.metrics}")

        if context_parts:
            base_msg += f" | {' | '.join(context_parts)}"

        # Add location information
        base_msg += f" [{record.module}:{record.funcName}:{record.lineno}]"

        # Add exception if present
        if record.exc_info:
            base_msg += f"\n{self.formatException(record.exc_info)}"

        return base_msg

    def _format_standard(self, record: logging.LogRecord) -> str:
        """Format with standard information."""
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        return f"[{timestamp}] [{record.levelname:5}] {record.getMessage()}"


class SynthaLogger:
    """Main logging class for Syntha SDK."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern implementation."""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the logger."""
        if not hasattr(self, "initialized"):
            self.loggers: Dict[str, logging.Logger] = {}
            self.level = logging.INFO
            self.initialized = True

    def configure_logging(
        self,
        level: str = "INFO",
        format_type: str = "standard",
        log_file: Optional[str] = None,
        enable_console: bool = True,
        enable_file: bool = False,
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
    ):
        """
        Configure logging for the entire SDK.

        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            format_type: Format type (standard, detailed, json)
            log_file: Path to log file
            enable_console: Enable console logging
            enable_file: Enable file logging
            max_file_size: Maximum file size before rotation (0 = no rotation)
            backup_count: Number of backup files to keep
        """
        # Set level
        self.level = getattr(logging, level.upper())

        # Get root logger for syntha
        root_logger = logging.getLogger("syntha")
        root_logger.setLevel(self.level)

        # Clear existing handlers
        root_logger.handlers.clear()

        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)
            console_handler.setFormatter(SynthaFormatter(format_type))
            root_logger.addHandler(console_handler)

        # File handler
        if enable_file and log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            if max_file_size > 0:
                file_handler: logging.Handler = logging.handlers.RotatingFileHandler(
                    log_file, maxBytes=max_file_size, backupCount=backup_count
                )
            else:
                file_handler = logging.FileHandler(log_file)

            file_handler.setLevel(self.level)
            file_handler.setFormatter(SynthaFormatter("json", include_context=True))
            root_logger.addHandler(file_handler)

        # Prevent duplicate logs
        root_logger.propagate = False

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger for a specific component."""
        if name not in self.loggers:
            self.loggers[name] = logging.getLogger(f"syntha.{name}")
        return self.loggers[name]

    def configure_from_env(self):
        """Configure logging from environment variables."""
        level = os.getenv("SYNTHA_LOG_LEVEL", "INFO")
        format_type = os.getenv("SYNTHA_LOG_FORMAT", "standard")
        log_file = os.getenv("SYNTHA_LOG_FILE")
        enable_console = os.getenv("SYNTHA_LOG_CONSOLE", "true").lower() == "true"
        enable_file = os.getenv("SYNTHA_LOG_FILE_ENABLE", "false").lower() == "true"
        max_file_size = int(os.getenv("SYNTHA_LOG_MAX_SIZE", "10485760"))  # 10MB
        backup_count = int(os.getenv("SYNTHA_LOG_BACKUP_COUNT", "5"))

        self.configure_logging(
            level=level,
            format_type=format_type,
            log_file=log_file,
            enable_console=enable_console,
            enable_file=enable_file,
            max_file_size=max_file_size,
            backup_count=backup_count,
        )


class ContextLogger:
    """Context-aware logger for agent operations."""

    def __init__(self, logger: logging.Logger, agent_name: Optional[str] = None):
        """
        Initialize context logger.

        Args:
            logger: Base logger instance
            agent_name: Name of the agent for context
        """
        self.logger = logger
        self.agent_name = agent_name
        self.context: Dict[str, Any] = {}

    def set_context(self, **kwargs):
        """Set context variables."""
        self.context.update(kwargs)

    def clear_context(self):
        """Clear all context variables."""
        self.context.clear()

    def _log_with_context(self, level: int, message: str, **kwargs):
        """Log with context."""
        extra: Dict[str, Any] = {"context": {**self.context, **kwargs}}
        if self.agent_name:
            extra["agent_name"] = self.agent_name
        self.logger.log(level, message, extra=extra)

    def debug(self, message: str, **kwargs):
        """Log debug message with context."""
        self._log_with_context(logging.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        """Log info message with context."""
        self._log_with_context(logging.INFO, message, **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context."""
        self._log_with_context(logging.WARNING, message, **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with context."""
        self._log_with_context(logging.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with context."""
        self._log_with_context(logging.CRITICAL, message, **kwargs)


class PerformanceLogger:
    """Performance tracking logger."""

    def __init__(self, logger: logging.Logger):
        """Initialize performance logger."""
        self.logger = logger
        self.timers: Dict[str, float] = {}

    def start_timer(self, operation: str, **context):
        """Start a performance timer."""
        timer_id = f"{operation}_{int(time.time() * 1000)}"
        self.timers[timer_id] = time.perf_counter()
        self.logger.info(
            f"Started operation: {operation}",
            extra={
                "metrics": {"operation": operation, "timer_id": timer_id},
                "context": context,
            },
        )
        return timer_id

    def end_timer(self, timer_id: str, **additional_metrics):
        """End a performance timer."""
        if timer_id not in self.timers:
            self.logger.warning(f"Timer {timer_id} not found")
            return

        duration = time.perf_counter() - self.timers[timer_id]
        del self.timers[timer_id]

        metrics = {
            "timer_id": timer_id,
            "duration_seconds": duration,
            "duration_ms": duration * 1000,
            **additional_metrics,
        }

        self.logger.info(
            f"Completed operation in {duration:.3f}s", extra={"metrics": metrics}
        )

    def log_metrics(self, operation: str, metrics: Dict[str, Any], **context):
        """Log custom metrics."""
        self.logger.info(
            f"Metrics for {operation}",
            extra={"metrics": {"operation": operation, **metrics}, "context": context},
        )


class SecurityLogger:
    """Security event logger."""

    def __init__(self, logger: logging.Logger):
        """Initialize security logger."""
        self.logger = logger

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        description: str,
        agent_name: Optional[str] = None,
        **context,
    ):
        """
        Log a security event.

        Args:
            event_type: Type of security event
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            description: Event description
            agent_name: Agent involved in the event
            **context: Additional context
        """
        security_context = {
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            **context,
        }

        if agent_name:
            security_context["agent_name"] = agent_name

        self.logger.warning(
            f"Security event: {event_type} - {description}",
            extra={"security_context": security_context},
        )

    def log_access_attempt(
        self,
        agent_name: str,
        resource: str,
        success: bool,
        reason: Optional[str] = None,
    ):
        """Log an access attempt."""
        event_type = "access_granted" if success else "access_denied"
        severity = "LOW" if success else "MEDIUM"
        description = f"Agent {agent_name} {'accessed' if success else 'denied access to'} {resource}"

        context: Dict[str, Any] = {"resource": resource, "success": success}
        if reason:
            context["reason"] = reason

        self.log_security_event(
            event_type, severity, description, agent_name, **context
        )

    def log_authentication_event(
        self,
        agent_name: str,
        success: bool,
        method: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        """Log an authentication event."""
        event_type = "authentication_success" if success else "authentication_failure"
        severity = "LOW" if success else "HIGH"
        description = f"Agent {agent_name} {'authenticated' if success else 'failed authentication'}"

        context: Dict[str, Any] = {"success": success}
        if method:
            context["method"] = method
        if reason:
            context["reason"] = reason

        self.log_security_event(
            event_type, severity, description, agent_name, **context
        )


# Convenience functions


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return SynthaLogger().get_logger(name)


def get_context_logger(name: str, agent_name: Optional[str] = None) -> ContextLogger:
    """Get a context-aware logger."""
    base_logger = get_logger(name)
    return ContextLogger(base_logger, agent_name)


def get_performance_logger(name: str) -> PerformanceLogger:
    """Get a performance logger."""
    base_logger = get_logger(name)
    return PerformanceLogger(base_logger)


def get_security_logger(name: str) -> SecurityLogger:
    """Get a security logger."""
    base_logger = get_logger(name)
    return SecurityLogger(base_logger)


def configure_logging(**kwargs):
    """Configure logging with the given parameters."""
    SynthaLogger().configure_logging(**kwargs)


def configure_from_env():
    """Configure logging from environment variables."""
    SynthaLogger().configure_from_env()


# Auto-configure from environment on import
try:
    configure_from_env()
except Exception:
    # Fall back to default configuration if env config fails
    configure_logging()
