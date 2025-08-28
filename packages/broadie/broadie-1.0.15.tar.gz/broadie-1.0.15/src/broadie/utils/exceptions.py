"""
Exception classes for Broadie.

Provides a hierarchy of custom exceptions for different error types.
"""

from typing import Any, Dict, Optional


class BroadieError(Exception):
    """
    Base exception class for all Broadie-related errors.

    Follows the Exception hierarchy pattern for clear error handling.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary representation."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class ConfigurationError(BroadieError):
    """
    Raised when there are configuration-related errors.

    Examples:
    - Invalid configuration files
    - Missing required configuration values
    - Invalid configuration format
    """

    pass


class AgentError(BroadieError):
    """
    Raised when there are agent-related errors.

    Examples:
    - Agent initialization failures
    - Agent execution errors
    - Sub-agent communication issues
    """

    def __init__(self, message: str, agent_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.agent_name = agent_name
        if agent_name:
            self.details["agent_name"] = agent_name


class ToolError(BroadieError):
    """
    Raised when there are tool-related errors.

    Examples:
    - Tool execution failures
    - Invalid tool parameters
    - Tool not found
    """

    def __init__(self, message: str, tool_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.tool_name = tool_name
        if tool_name:
            self.details["tool_name"] = tool_name


class MemoryError(BroadieError):
    """
    Raised when there are memory system errors.

    Examples:
    - Memory storage failures
    - Memory retrieval errors
    - Vector search failures
    """

    def __init__(self, message: str, memory_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.memory_id = memory_id
        if memory_id:
            self.details["memory_id"] = memory_id


class PersistenceError(BroadieError):
    """
    Raised when there are persistence layer errors.

    Examples:
    - Database connection failures
    - Data storage errors
    - Migration failures
    """

    pass


class APIError(BroadieError):
    """
    Raised when there are API-related errors.

    Examples:
    - HTTP request failures
    - Invalid API responses
    - Authentication errors
    """

    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        if status_code:
            self.details["status_code"] = status_code


class A2AError(BroadieError):
    """
    Raised when there are agent-to-agent communication errors.

    Examples:
    - Registry connection failures
    - Peer agent unavailable
    - Trust validation failures
    """

    def __init__(self, message: str, agent_id: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.agent_id = agent_id
        if agent_id:
            self.details["agent_id"] = agent_id


class NotificationError(BroadieError):
    """
    Raised when there are notification system errors.

    Examples:
    - Slack API failures
    - Message formatting errors
    - Notification delivery failures
    """

    def __init__(self, message: str, notification_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.notification_type = notification_type
        if notification_type:
            self.details["notification_type"] = notification_type


class ValidationError(BroadieError):
    """
    Raised when data validation fails.

    Examples:
    - Schema validation failures
    - Input parameter validation errors
    - Data type mismatches
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(value)


class ModelError(BroadieError):
    """
    Raised when there are language model errors.

    Examples:
    - Model initialization failures
    - API key issues
    - Rate limiting errors
    - Model response parsing errors
    """

    def __init__(self, message: str, model_name: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.model_name = model_name
        if model_name:
            self.details["model_name"] = model_name


class SecurityError(BroadieError):
    """
    Raised when there are security-related errors.

    Examples:
    - Authentication failures
    - Authorization errors
    - Trust validation failures
    - Untrusted agent communication attempts
    """

    pass


# Utility functions for error handling


def handle_exception(
    exception: Exception, context: Optional[str] = None, reraise: bool = True
) -> Optional[BroadieError]:
    """
    Convert standard exceptions to Broadie exceptions with context.

    Args:
        exception: The original exception
        context: Additional context about where the error occurred
        reraise: Whether to raise the converted exception

    Returns:
        BroadieError instance if not reraising

    Raises:
        BroadieError: Converted exception if reraise is True
    """
    if isinstance(exception, BroadieError):
        broadie_error = exception
    else:
        message = str(exception)
        if context:
            message = f"{context}: {message}"

        # Map common exception types to Broadie exceptions
        if isinstance(exception, (FileNotFoundError, KeyError)):
            broadie_error = ConfigurationError(message)
        elif isinstance(exception, (ValueError, TypeError)):
            broadie_error = ValidationError(message)
        elif isinstance(exception, ConnectionError):
            broadie_error = APIError(message)
        else:
            broadie_error = BroadieError(message)

        # Preserve original exception context
        broadie_error.__cause__ = exception

    if reraise:
        raise broadie_error
    else:
        return broadie_error


def create_error_response(error: BroadieError) -> Dict[str, Any]:
    """
    Create a standardized error response dictionary.

    Args:
        error: The BroadieError to convert

    Returns:
        Dictionary representation suitable for API responses
    """
    return {
        "success": False,
        "error": error.to_dict(),
        "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
    }
