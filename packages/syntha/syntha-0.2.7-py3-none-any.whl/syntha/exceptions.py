"""
Syntha SDK Exception Classes

Comprehensive error handling for the Syntha SDK with:
- Custom exception hierarchy
- Detailed error messages
- Context preservation
- Error recovery suggestions
- Logging integration
"""

import traceback
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


class SynthaError(Exception):
    """Base exception class for all Syntha SDK errors."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
        suggestions: Optional[List[Any]] = None,
    ):
        """
        Initialize base Syntha error.

        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            context: Additional context information
            cause: Original exception that caused this error
            suggestions: List of suggestions for fixing the error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause
        self.suggestions = suggestions or []
        self.timestamp = datetime.now().isoformat()

    def __str__(self) -> str:
        """String representation of the error."""
        parts = [f"[{self.error_code}] {self.message}"]

        if self.context:
            parts.append(f"Context: {self.context}")

        if self.cause:
            parts.append(f"Caused by: {self.cause}")

        if self.suggestions:
            parts.append(f"Suggestions: {', '.join(self.suggestions)}")

        return "\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "context": self.context,
            "cause": str(self.cause) if self.cause else None,
            "suggestions": self.suggestions,
            "timestamp": self.timestamp,
            "traceback": traceback.format_exc(),
        }


class SynthaConfigurationError(SynthaError):
    """Configuration-related errors."""

    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        """
        Initialize configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.config_key = config_key

        # Add configuration-specific context
        if config_key:
            self.context["config_key"] = config_key
            self.suggestions.append(f"Check configuration for key: {config_key}")


class SynthaConnectionError(SynthaError):
    """Connection and network-related errors."""

    def __init__(self, message: str, service: Optional[str] = None, **kwargs):
        """
        Initialize connection error.

        Args:
            message: Error message
            service: Service that failed to connect
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.service = service

        # Add connection-specific context
        if service:
            self.context["service"] = service
            self.suggestions.extend(
                [
                    f"Check {service} service availability",
                    "Verify network connectivity",
                    "Check authentication credentials",
                ]
            )


class SynthaValidationError(SynthaError):
    """Data validation errors."""

    def __init__(
        self, message: str, field: Optional[str] = None, value: Any = None, **kwargs
    ):
        """
        Initialize validation error.

        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value

        # Add validation-specific context
        if field:
            self.context["field"] = field
        if value is not None:
            self.context["value"] = value
            self.suggestions.append(f"Check value for field '{field}': {value}")


class SynthaPermissionError(SynthaError):
    """Permission and authorization errors."""

    def __init__(
        self,
        message: str,
        agent: Optional[str] = None,
        resource: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize permission error.

        Args:
            message: Error message
            agent: Agent that was denied access
            resource: Resource that was accessed
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.agent = agent
        self.resource = resource

        # Add permission-specific context
        if agent:
            self.context["agent"] = agent
        if resource:
            self.context["resource"] = resource
            self.suggestions.extend(
                [
                    f"Check permissions for agent: {agent}",
                    f"Verify access to resource: {resource}",
                    "Review security policies",
                ]
            )


class SynthaContextError(SynthaError):
    """Context management errors."""

    def __init__(
        self,
        message: str,
        key: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize context error.

        Args:
            message: Error message
            key: Context key involved in error
            operation: Operation that failed
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.key = key
        self.operation = operation

        # Add context-specific information
        if key:
            self.context["key"] = key
        if operation:
            self.context["operation"] = operation
            self.suggestions.extend(
                [
                    f"Check context key: {key}",
                    f"Verify operation: {operation}",
                    "Review context state",
                ]
            )


class SynthaPersistenceError(SynthaError):
    """Persistence and storage errors."""

    def __init__(
        self,
        message: str,
        backend: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize persistence error.

        Args:
            message: Error message
            backend: Storage backend that failed
            operation: Operation that failed
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.backend = backend
        self.operation = operation

        # Add persistence-specific context
        if backend:
            self.context["backend"] = backend
        if operation:
            self.context["operation"] = operation
            self.suggestions.extend(
                [
                    f"Check {backend} backend availability",
                    f"Verify operation: {operation}",
                    "Check storage permissions",
                    "Review database connection",
                ]
            )


class SynthaToolError(SynthaError):
    """Tool execution and management errors."""

    def __init__(
        self,
        message: str,
        tool: Optional[str] = None,
        agent: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize tool error.

        Args:
            message: Error message
            tool: Tool that failed
            agent: Agent that was using the tool
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.tool = tool
        self.agent = agent

        # Add tool-specific context
        if tool:
            self.context["tool"] = tool
        if agent:
            self.context["agent"] = agent
            self.suggestions.extend(
                [
                    f"Check tool availability: {tool}",
                    f"Verify agent permissions: {agent}",
                    "Review tool configuration",
                ]
            )


class SynthaSecurityError(SynthaError):
    """Security-related errors."""

    def __init__(self, message: str, security_event: Optional[str] = None, **kwargs):
        """
        Initialize security error.

        Args:
            message: Error message
            security_event: Type of security event
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.security_event = security_event

        # Add security-specific context
        if security_event:
            self.context["security_event"] = security_event
            self.suggestions.extend(
                [
                    "Review security policies",
                    "Check authentication status",
                    "Verify authorization levels",
                    f"Investigate security event: {security_event}",
                ]
            )


class SynthaPerformanceError(SynthaError):
    """Performance and resource errors."""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        duration: Optional[float] = None,
        **kwargs,
    ):
        """
        Initialize performance error.

        Args:
            message: Error message
            operation: Operation that was slow
            duration: Duration of the operation
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.operation = operation
        self.duration = duration

        # Add performance-specific context
        if operation:
            self.context["operation"] = operation
        if duration:
            self.context["duration"] = duration
            self.suggestions.extend(
                [
                    f"Optimize operation: {operation}",
                    f"Consider timeout adjustment (took {duration}s)",
                    "Review resource allocation",
                    "Check system performance",
                ]
            )


class SynthaTimeoutError(SynthaError):
    """Timeout-related errors."""

    def __init__(
        self,
        message: str,
        timeout: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize timeout error.

        Args:
            message: Error message
            timeout: Timeout value that was exceeded
            operation: Operation that timed out
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.timeout = timeout
        self.operation = operation

        # Add timeout-specific context
        if timeout:
            self.context["timeout"] = timeout
        if operation:
            self.context["operation"] = operation
            self.suggestions.extend(
                [
                    f"Increase timeout from {timeout}s",
                    f"Optimize operation: {operation}",
                    "Check network latency",
                    "Review system resources",
                ]
            )


class SynthaFrameworkError(SynthaError):
    """Framework integration-related errors."""

    def __init__(
        self,
        message: str,
        framework: Optional[str] = None,
        tool_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize framework error.

        Args:
            message: Error message
            framework: Framework name that caused the error
            tool_name: Tool name that caused the error
            **kwargs: Additional arguments passed to parent class
        """
        super().__init__(message, **kwargs)
        self.framework = framework
        self.tool_name = tool_name

        # Add framework-specific context
        if framework:
            self.context["framework"] = framework
        if tool_name:
            self.context["tool_name"] = tool_name

        # Add framework-specific suggestions
        if framework:
            self.suggestions.extend(
                [
                    f"Check if {framework} is properly installed",
                    f"Verify {framework} version compatibility",
                    "Review framework documentation",
                    "Check for missing dependencies",
                ]
            )


class ErrorHandler:
    """Centralized error handling and logging."""

    def __init__(self, logger=None):
        """
        Initialize error handler.

        Args:
            logger: Logger instance for error reporting
        """
        self.logger = logger

    def handle_error(
        self, error: Exception, context: Optional[Dict[str, Any]] = None
    ) -> SynthaError:
        """
        Handle any exception and convert to appropriate Syntha error.

        Args:
            error: Original exception
            context: Additional context information

        Returns:
            Appropriate SynthaError instance
        """
        context = context or {}

        # Log the error
        if self.logger:
            self.logger.error(f"Error occurred: {error}", extra=context)

        # Convert to appropriate Syntha error
        if isinstance(error, SynthaError):
            return error

        # Map common exceptions to Syntha errors
        error_message = str(error)

        if "connection" in error_message.lower():
            return SynthaConnectionError(
                f"Connection failed: {error_message}",
                context=context,
                cause=error,
            )
        elif "validation" in error_message.lower():
            return SynthaValidationError(
                f"Validation failed: {error_message}",
                context=context,
                cause=error,
            )
        elif "permission" in error_message.lower():
            return SynthaPermissionError(
                f"Permission denied: {error_message}",
                context=context,
                cause=error,
            )
        elif "timeout" in error_message.lower():
            return SynthaTimeoutError(
                f"Operation timed out: {error_message}",
                context=context,
                cause=error,
            )
        else:
            return SynthaError(
                f"Unexpected error: {error_message}",
                context=context,
                cause=error,
            )

    def wrap_function(self, func, context: Optional[Dict[str, Any]] = None):
        """
        Wrap a function with error handling.

        Args:
            func: Function to wrap
            context: Additional context for error handling

        Returns:
            Wrapped function
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                syntha_error = self.handle_error(e, context)
                raise syntha_error

        return wrapper


def handle_syntha_error(func):
    """
    Decorator for automatic error handling.

    Args:
        func: Function to decorate

    Returns:
        Decorated function with error handling
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler = ErrorHandler()
            syntha_error = handler.handle_error(e)
            raise syntha_error

    return wrapper


# Export all exception classes
__all__ = [
    "SynthaError",
    "SynthaConfigurationError",
    "SynthaConnectionError",
    "SynthaValidationError",
    "SynthaPermissionError",
    "SynthaContextError",
    "SynthaPersistenceError",
    "SynthaToolError",
    "SynthaSecurityError",
    "SynthaPerformanceError",
    "SynthaTimeoutError",
    "SynthaFrameworkError",
    "ErrorHandler",
    "handle_syntha_error",
]
