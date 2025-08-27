"""
Exception classes for MCP Commons library.

Provides a hierarchy of exceptions for consistent error handling across
MCP server implementations.
"""

from typing import Any


class McpCommonsError(Exception):
    """Base exception for all MCP Commons errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class UseCaseError(McpCommonsError):
    """Exception raised during use case execution."""

    def __init__(self, message: str, operation: str | None = None, **details):
        super().__init__(message, details)
        self.operation = operation
        if operation:
            self.details["operation"] = operation


class AdapterError(McpCommonsError):
    """Exception raised during MCP adaptation process."""

    def __init__(self, message: str, method_name: str | None = None, **details):
        super().__init__(message, details)
        self.method_name = method_name
        if method_name:
            self.details["method_name"] = method_name


class ValidationError(UseCaseError):
    """Exception raised when validation fails."""

    def __init__(
        self, message: str, field: str | None = None, value: Any = None, **details
    ):
        super().__init__(message, **details)
        self.field = field
        self.value = value
        if field:
            self.details["field"] = field
        if value is not None:
            self.details["value"] = str(
                value
            )  # Convert to string for JSON serialization


class ConfigurationError(McpCommonsError):
    """Exception raised when there are configuration issues."""

    def __init__(self, message: str, config_key: str | None = None, **details):
        super().__init__(message, details)
        self.config_key = config_key
        if config_key:
            self.details["config_key"] = config_key


class DependencyError(McpCommonsError):
    """Exception raised when dependency injection fails."""

    def __init__(self, message: str, dependency_name: str | None = None, **details):
        super().__init__(message, details)
        self.dependency_name = dependency_name
        if dependency_name:
            self.details["dependency_name"] = dependency_name
