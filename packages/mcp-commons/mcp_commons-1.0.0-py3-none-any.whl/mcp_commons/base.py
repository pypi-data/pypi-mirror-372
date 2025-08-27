"""
Base classes for MCP server use cases and results.

Provides standardized patterns for use case implementation and result handling
across all MCP servers.
"""

import logging
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class UseCaseResult(Generic[T]):
    """
    Standardized use case result with success/failure state and optional data.

    This is the core result type that all use cases should return. It provides
    consistent error handling and data structure across MCP servers.
    """

    success: bool
    data: T | None = None
    error: str | None = None
    details: dict[str, Any] | None = None

    @classmethod
    def success_with_data(cls, data: T, **details) -> "UseCaseResult[T]":
        """Create a successful result with data."""
        return cls(success=True, data=data, details=details if details else None)

    @classmethod
    def failure_with_error(cls, error: str, **details) -> "UseCaseResult[T]":
        """Create a failed result with error message."""
        return cls(success=False, error=error, details=details if details else None)

    @classmethod
    def success(cls, data: T | None = None, **details) -> "UseCaseResult[T]":
        """Create a successful result, optionally with data."""
        return cls(success=True, data=data, details=details if details else None)

    @classmethod
    def failure(cls, error: str, **details) -> "UseCaseResult[T]":
        """Create a failed result with error message."""
        return cls(success=False, error=error, details=details if details else None)

    def get_data(self) -> T | None:
        """Get the result data."""
        return self.data

    def has_data(self) -> bool:
        """Check if result contains data."""
        return self.data is not None

    def is_success(self) -> bool:
        """Check if the result represents success."""
        return self.success

    def is_failure(self) -> bool:
        """Check if the result represents failure."""
        return not self.success


class BaseUseCase:
    """
    Base class for all MCP server use cases.

    Provides common functionality like logging, dependency injection,
    and standardized execution patterns.
    """

    def __init__(self, **dependencies):
        """Initialize use case with dependencies via dependency injection."""
        self._logger = logging.getLogger(self.__class__.__name__)

        # Store dependencies as private attributes
        for key, value in dependencies.items():
            setattr(self, f"_{key}", value)

    async def execute(self, *args, **kwargs) -> UseCaseResult[Any]:
        """
        Execute the use case. Must be implemented by subclasses.

        Returns:
            UseCaseResult with success/failure and optional data
        """
        raise NotImplementedError("Subclasses must implement execute method")

    def _build_context(self, **kwargs) -> dict[str, Any]:
        """Build context dictionary for result details."""
        return {k: v for k, v in kwargs.items() if v is not None}

    def _log_success(self, operation: str, **context) -> None:
        """Log successful operation."""
        self._logger.debug(
            f"Use case {operation} completed successfully", extra=context
        )

    def _log_error(self, operation: str, error: Exception, **context) -> None:
        """Log error during operation."""
        self._logger.error(
            f"Use case {operation} failed: {str(error)}", extra=context, exc_info=True
        )

    def _handle_exception(
        self, error: Exception, operation: str, **context
    ) -> UseCaseResult[Any]:
        """Handle exceptions consistently."""
        self._log_error(operation, error, **context)

        return UseCaseResult.failure(error=str(error), operation=operation, **context)


class QueryUseCase(BaseUseCase):
    """Base class for query (read) operations."""

    async def execute_query(
        self, operation: str, query_func, **context
    ) -> UseCaseResult[Any]:
        """Execute a query operation with standardized error handling."""
        try:
            result = await query_func()
            self._log_success(operation, **context)

            return UseCaseResult.success_with_data(
                data=result, operation=operation, **context
            )

        except Exception as e:
            return self._handle_exception(e, operation, **context)


class CommandUseCase(BaseUseCase):
    """Base class for command (write) operations."""

    async def execute_command(
        self, operation: str, command_func, **context
    ) -> UseCaseResult[Any]:
        """Execute a command operation with standardized error handling."""
        try:
            result = await command_func()
            self._log_success(operation, **context)

            return UseCaseResult.success_with_data(
                data=result, operation=operation, **context
            )

        except Exception as e:
            return self._handle_exception(e, operation, **context)


class UseCaseFactory:
    """
    Factory for creating use cases with dependency injection.

    Allows consistent dependency management across use cases in a server.
    """

    def __init__(self, **default_dependencies):
        """Initialize factory with default dependencies."""
        self._default_dependencies = default_dependencies

    def create_use_case(
        self, use_case_class: type[BaseUseCase], **additional_dependencies
    ) -> BaseUseCase:
        """Create use case instance with injected dependencies."""
        dependencies = {**self._default_dependencies, **additional_dependencies}
        return use_case_class(**dependencies)

    def add_dependency(self, name: str, dependency: Any) -> None:
        """Add or update a default dependency."""
        self._default_dependencies[name] = dependency

    def get_dependency(self, name: str) -> Any:
        """Get a default dependency by name."""
        return self._default_dependencies.get(name)

    def list_dependencies(self) -> dict[str, Any]:
        """Get all default dependencies."""
        return self._default_dependencies.copy()
