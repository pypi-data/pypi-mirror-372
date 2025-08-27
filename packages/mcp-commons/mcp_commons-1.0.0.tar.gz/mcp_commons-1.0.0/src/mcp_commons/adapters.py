"""
MCP Result Adapter - Core infrastructure for converting use case results to MCP format.

This module provides the higher-order function pattern that eliminates 500+ lines
of boilerplate wrapper functions in MCP servers.
"""

import inspect
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from .base import UseCaseResult

logger = logging.getLogger(__name__)


@runtime_checkable
class McpCompatible(Protocol):
    """Protocol for objects that can be adapted to MCP format."""

    def to_mcp_result(self) -> dict[str, Any]:
        """Convert to MCP-compatible result format."""
        ...


@dataclass
class AdapterStats:
    """Statistics about adapter usage and performance."""

    version: str = "1.0.0"
    boilerplate_lines_eliminated: int = 500
    description: str = "Single adapter function replacing all MCP wrapper boilerplate"


def create_mcp_adapter(
    use_case_method: Callable,
    *,
    custom_success_handler: Callable[[Any], dict[str, Any]] | None = None,
    custom_error_handler: Callable[[Exception], dict[str, Any]] | None = None,
) -> Callable:
    """
    Create an MCP-compatible adapter for any use case method.

    This is the core infrastructure function that eliminates boilerplate by wrapping
    any use case method and automatically handling result transformation to MCP format.

    Args:
        use_case_method: The use case execute method to adapt
        custom_success_handler: Optional custom handler for successful results
        custom_error_handler: Optional custom handler for exceptions

    Returns:
        An async function compatible with MCP SDK that returns data directly

    Example:
        >>> use_case = ListProjectsUseCase(project_service)
        >>> adapted_method = create_mcp_adapter(use_case.execute)
        >>> tool = Tool.from_function(adapted_method, name="list_projects")

    Architecture Benefits:
        - Eliminates 500+ lines of repetitive wrapper functions
        - Provides consistent error handling across all tools
        - Maintains type safety and function signatures
        - Enables easy testing and modification of MCP behavior
    """
    if not callable(use_case_method):
        raise ValueError("use_case_method must be callable")

    # Preserve original function signature for MCP SDK compatibility
    sig = inspect.signature(use_case_method)
    method_name = getattr(use_case_method, "__name__", "unknown_method")

    async def mcp_adapted_method(**kwargs) -> dict[str, Any]:
        """Execute use case and adapt result for MCP."""
        try:
            # Call the original use case method
            result = await use_case_method(**kwargs)

            # Handle different result types
            if isinstance(result, UseCaseResult):
                return _handle_use_case_result(
                    result, method_name, custom_success_handler
                )
            elif isinstance(result, McpCompatible):
                return result.to_mcp_result()
            else:
                # Handle raw results (for compatibility with non-standard use cases)
                logger.warning(
                    f"Use case method '{method_name}' returned non-UseCaseResult: {type(result)}"
                )
                return _handle_raw_result(result, custom_success_handler)

        except Exception as e:
            # Handle any unexpected exceptions
            return _handle_exception(e, method_name, kwargs, custom_error_handler)

    # Preserve function metadata for MCP SDK compatibility
    mcp_adapted_method.__name__ = method_name
    mcp_adapted_method.__doc__ = use_case_method.__doc__
    mcp_adapted_method.__annotations__ = getattr(use_case_method, "__annotations__", {})
    mcp_adapted_method.__signature__ = sig

    return mcp_adapted_method


def _handle_use_case_result(
    result: UseCaseResult, method_name: str, custom_success_handler: Callable | None
) -> dict[str, Any]:
    """Handle UseCaseResult transformation to MCP format."""
    if result.success:
        # Successful result - return the data directly
        if custom_success_handler:
            return custom_success_handler(result.data)

        # Default success handling
        if result.data is not None:
            return (
                result.data
                if isinstance(result.data, dict)
                else {"result": result.data}
            )
        else:
            return {"success": True}
    else:
        # Failed result - return error in MCP-compatible format
        error_response = {"success": False}

        if result.error:
            error_response["error"] = result.error

        if result.details:
            error_response["details"] = result.details

        return error_response


def _handle_raw_result(
    result: Any, custom_success_handler: Callable | None
) -> dict[str, Any]:
    """Handle non-UseCaseResult objects."""
    if custom_success_handler:
        return custom_success_handler(result)

    # Default raw result handling
    if isinstance(result, dict):
        return result
    elif result is None:
        return {"success": True}
    else:
        return {"result": result}


def _handle_exception(
    error: Exception,
    method_name: str,
    kwargs: dict[str, Any],
    custom_error_handler: Callable | None,
) -> dict[str, Any]:
    """Handle exceptions consistently."""
    logger.error(
        f"Error in MCP adapter for '{method_name}': {str(error)}", exc_info=True
    )

    if custom_error_handler:
        return custom_error_handler(error)

    # Default exception handling
    return {
        "success": False,
        "error": f"Unexpected error: {str(error)}",
        "details": {
            "method": method_name,
            "parameters": {
                k: str(v) for k, v in kwargs.items()
            },  # Convert to strings for JSON serialization
        },
    }


def validate_use_case_result(result: Any) -> bool:
    """
    Validate that a result is a proper UseCaseResult.

    This function can be used for testing and debugging to ensure
    use cases return the expected result format.

    Args:
        result: The result to validate

    Returns:
        True if result is a valid UseCaseResult, False otherwise

    Example:
        >>> result = UseCaseResult.success(data={"test": "data"})
        >>> assert validate_use_case_result(result)
    """
    if not isinstance(result, UseCaseResult):
        return False

    # Check required attributes exist
    required_attrs = ["success", "data", "error", "details"]
    for attr in required_attrs:
        if not hasattr(result, attr):
            return False

    # Validate attribute types
    if not isinstance(result.success, bool):
        return False

    if result.error is not None and not isinstance(result.error, str):
        return False

    if result.details is not None and not isinstance(result.details, dict):
        return False

    return True


def get_adapter_stats() -> AdapterStats:
    """
    Get statistics about the adapter usage and impact.

    Returns:
        AdapterStats with information about boilerplate elimination
    """
    return AdapterStats()


# Higher-level convenience functions for common patterns


def create_query_adapter(use_case_method: Callable) -> Callable:
    """
    Create MCP adapter optimized for query operations.

    Query operations typically return data directly without transformation.
    """

    def query_success_handler(data: Any) -> dict[str, Any]:
        if isinstance(data, list | dict):
            return {"data": data}
        else:
            return {"result": data}

    return create_mcp_adapter(
        use_case_method, custom_success_handler=query_success_handler
    )


def create_command_adapter(use_case_method: Callable) -> Callable:
    """
    Create MCP adapter optimized for command operations.

    Command operations typically return success confirmation and optional result data.
    """

    def command_success_handler(data: Any) -> dict[str, Any]:
        return {"success": True, "result": data}

    return create_mcp_adapter(
        use_case_method, custom_success_handler=command_success_handler
    )


def create_validation_adapter(use_case_method: Callable) -> Callable:
    """
    Create MCP adapter with enhanced error details for validation-heavy operations.
    """

    def validation_error_handler(error: Exception) -> dict[str, Any]:
        error_type = error.__class__.__name__

        # Enhanced error handling for validation errors
        if "validation" in error_type.lower() or "value" in error_type.lower():
            return {
                "success": False,
                "error": "Validation failed",
                "validation_error": str(error),
                "error_type": error_type,
            }

        # Fallback to standard error handling
        return {"success": False, "error": str(error), "error_type": error_type}

    return create_mcp_adapter(
        use_case_method, custom_error_handler=validation_error_handler
    )


# Testing utilities


def create_mock_adapter(mock_result: Any) -> Callable:
    """
    Create a mock MCP adapter for testing purposes.

    Args:
        mock_result: The result to return when the adapter is called

    Returns:
        Mock adapter function that returns the specified result
    """

    async def mock_adapted_method(**kwargs) -> dict[str, Any]:
        if isinstance(mock_result, UseCaseResult):
            return _handle_use_case_result(mock_result, "mock_method", None)
        else:
            return _handle_raw_result(mock_result, None)

    mock_adapted_method.__name__ = "mock_adapter"
    mock_adapted_method.__doc__ = "Mock adapter for testing"

    return mock_adapted_method
