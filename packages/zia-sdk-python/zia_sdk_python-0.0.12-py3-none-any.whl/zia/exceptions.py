"""
Custom exceptions for the Neurolabs SDK.
"""

from typing import Any, Optional


class NeurolabsError(Exception):
    """Base exception for all Neurolabs SDK errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_data: Optional[dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.response_data = response_data

    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class NeurolabsAuthError(NeurolabsError):
    """Authentication or authorization error."""

    def __init__(
        self,
        message: str = "Authentication failed. Please check your API key.",
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, status_code, request_id)


class NeurolabsRateLimitError(NeurolabsError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please try again later.",
        retry_after: Optional[int] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, 429, request_id)
        self.retry_after = retry_after


class NeurolabsValidationError(NeurolabsError):
    """Request validation error."""

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        super().__init__(message, 400, request_id)
        self.field = field


class NeurolabsNotFoundError(NeurolabsError):
    """Resource not found error."""

    def __init__(
        self, message: str = "Resource not found.", request_id: Optional[str] = None
    ):
        super().__init__(message, 404, request_id)


class NeurolabsTimeoutError(NeurolabsError):
    """Request timeout error."""

    def __init__(
        self, message: str = "Request timed out.", request_id: Optional[str] = None
    ):
        super().__init__(message, 408, request_id)
