"""Enhanced exception classes for the Snail Orbit client.

This module provides a comprehensive exception hierarchy with context information,
structured error details, and proper HTTP status code mapping for better error
handling and debugging.
"""

from __future__ import annotations

from typing import Any


class SnailOrbitError(Exception):
    """Base exception for all Snail Orbit client errors.

    This is the root exception that all other client exceptions inherit from.
    It provides common functionality for error context and details.
    """

    def __init__(
        self,
        message: str,
        details: Any = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize base exception.

        Args:
            message: Human-readable error message
            details: Additional error details (e.g., from API response)
            context: Contextual information about when the error occurred
        """
        super().__init__(message)
        self.message = message
        self.details = details
        self.context = context or {}

    def __str__(self) -> str:
        """String representation of the error."""
        return self.message

    def __repr__(self) -> str:
        """Developer representation of the error."""
        return f'{self.__class__.__name__}({self.message!r})'

    def add_context(self, **kwargs: Any) -> None:
        """Add contextual information to the error.

        Args:
            **kwargs: Key-value pairs to add to error context
        """
        self.context.update(kwargs)


class ClientError(SnailOrbitError):
    """Client-side errors (4xx HTTP status codes).

    These errors indicate issues with the request itself, such as
    authentication failures, validation errors, or missing resources.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        details: Any = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize client error.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
            context: Error context
        """
        super().__init__(message, details, context)
        self.status_code = status_code


class ServerError(SnailOrbitError):
    """Server-side errors (5xx HTTP status codes).

    These errors indicate issues on the server side that are typically
    temporary and may be resolved by retrying the request.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        details: Any = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Initialize server error.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
            context: Error context
        """
        super().__init__(message, details, context)
        self.status_code = status_code


class AuthenticationError(ClientError):
    """Authentication failed (401 Unauthorized).

    This error occurs when the provided credentials are invalid,
    expired, or missing.
    """

    def __init__(
        self, message: str = 'Authentication failed', details: Any = None
    ) -> None:
        super().__init__(message, 401, details)


class AuthorizationError(ClientError):
    """Authorization failed (403 Forbidden).

    This error occurs when the user is authenticated but doesn't have
    permission to access the requested resource or perform the action.
    """

    def __init__(self, message: str = 'Access forbidden', details: Any = None) -> None:
        super().__init__(message, 403, details)


class NotFoundError(ClientError):
    """Resource not found (404 Not Found).

    This error occurs when the requested resource doesn't exist.
    """

    def __init__(
        self, message: str = 'Resource not found', details: Any = None
    ) -> None:
        super().__init__(message, 404, details)


class ValidationError(ClientError):
    """Request validation failed (422 Unprocessable Entity).

    This error occurs when the request is syntactically correct but
    semantically invalid (e.g., missing required fields, invalid values).
    """

    def __init__(
        self,
        message: str = 'Validation failed',
        validation_errors: list[dict[str, Any]] | None = None,
    ) -> None:
        """Initialize validation error.

        Args:
            message: Error message
            validation_errors: List of specific validation error details
        """
        super().__init__(message, 422, validation_errors)
        self.validation_errors = validation_errors or []

    def get_field_errors(self) -> dict[str, list[str]]:
        """Get validation errors grouped by field name.

        Returns:
            Dictionary mapping field names to lists of error messages
        """
        field_errors: dict[str, list[str]] = {}

        for error in self.validation_errors:
            if isinstance(error, dict):
                field = error.get('field', 'unknown')
                message = error.get('message', str(error))

                if field not in field_errors:
                    field_errors[field] = []
                field_errors[field].append(message)

        return field_errors


class ConflictError(ClientError):
    """Resource conflict (409 Conflict).

    This error occurs when the request conflicts with the current state
    of the resource (e.g., trying to create a resource that already exists).
    """

    def __init__(self, message: str = 'Resource conflict', details: Any = None) -> None:
        super().__init__(message, 409, details)


class RateLimitError(ClientError):
    """Rate limit exceeded (429 Too Many Requests).

    This error occurs when the client has exceeded the allowed request rate.
    """

    def __init__(
        self,
        message: str = 'Rate limit exceeded',
        retry_after: int | None = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
        """
        super().__init__(message, 429)
        self.retry_after = retry_after


class ConnectionError(SnailOrbitError):
    """Network connection error.

    This error occurs when there are network-level issues connecting
    to the server.
    """

    def __init__(
        self, message: str = 'Connection failed', cause: Exception | None = None
    ) -> None:
        """Initialize connection error.

        Args:
            message: Error message
            cause: Underlying exception that caused this error
        """
        super().__init__(message)
        self.cause = cause


class TimeoutError(SnailOrbitError):
    """Request timeout error.

    This error occurs when a request takes longer than the configured
    timeout period.
    """

    def __init__(
        self, message: str = 'Request timed out', timeout: float | None = None
    ) -> None:
        """Initialize timeout error.

        Args:
            message: Error message
            timeout: Timeout value that was exceeded
        """
        super().__init__(message)
        self.timeout = timeout


class ConfigurationError(SnailOrbitError):
    """Client configuration error.

    This error occurs when the client is configured incorrectly.
    """

    def __init__(self, message: str, parameter: str | None = None) -> None:
        """Initialize configuration error.

        Args:
            message: Error message
            parameter: Name of the configuration parameter that's invalid
        """
        super().__init__(message)
        self.parameter = parameter


class WorkflowError(SnailOrbitError):
    """Workflow execution error.

    This error occurs when there are issues with workflow operations.
    """

    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        execution_details: dict[str, Any] | None = None,
    ) -> None:
        """Initialize workflow error.

        Args:
            message: Error message
            workflow_id: ID of the workflow that failed
            execution_details: Details about the workflow execution
        """
        super().__init__(message, execution_details)
        self.workflow_id = workflow_id


class CustomFieldError(SnailOrbitError):
    """Custom field operation error.

    This error occurs when there are issues with custom field operations.
    """

    def __init__(
        self,
        message: str,
        field_name: str | None = None,
        field_type: str | None = None,
    ) -> None:
        """Initialize custom field error.

        Args:
            message: Error message
            field_name: Name of the custom field
            field_type: Type of the custom field
        """
        super().__init__(message)
        self.field_name = field_name
        self.field_type = field_type


class APIError(SnailOrbitError):
    """Generic API error for unexpected status codes.

    This error is used when the server returns a status code that doesn't
    map to a more specific exception type.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        response_data: Any = None,
    ) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Raw response data from the server
        """
        super().__init__(message, response_data)
        self.status_code = status_code


def create_exception_from_response(
    status_code: int,
    message: str,
    data: Any = None,
) -> SnailOrbitError:
    """Create appropriate exception based on HTTP status code.

    This function maps HTTP status codes to specific exception types,
    providing better error handling and debugging capabilities.

    Args:
        status_code: HTTP status code
        message: Error message
        data: Additional error data from response

    Returns:
        Appropriate exception instance
    """
    # Authentication and authorization errors
    if status_code == 401:
        return AuthenticationError(message, data)
    elif status_code == 403:
        return AuthorizationError(message, data)

    # Client errors
    elif status_code == 404:
        return NotFoundError(message, data)
    elif status_code == 409:
        return ConflictError(message, data)
    elif status_code == 422:
        validation_errors = []
        if isinstance(data, dict) and 'detail' in data:
            validation_errors = data['detail']
        return ValidationError(message, validation_errors)
    elif status_code == 429:
        retry_after = None
        if isinstance(data, dict) and 'retry_after' in data:
            retry_after = data['retry_after']
        return RateLimitError(message, retry_after)

    # Server errors
    elif 500 <= status_code < 600:
        return ServerError(message, status_code, data)

    # Other client errors
    elif 400 <= status_code < 500:
        return ClientError(message, status_code, data)

    # Generic API error for unexpected status codes
    else:
        return APIError(message, status_code, data)
