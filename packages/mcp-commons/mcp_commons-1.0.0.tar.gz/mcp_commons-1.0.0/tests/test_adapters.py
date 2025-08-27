"""
Tests for MCP result adapters.

Comprehensive test coverage for the core adapter functionality that replaces
500+ lines of boilerplate code.
"""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from mcp_commons import UseCaseResult, create_mcp_adapter, validate_use_case_result
from mcp_commons.adapters import (
    AdapterStats,
    create_command_adapter,
    create_mock_adapter,
    create_query_adapter,
    create_validation_adapter,
    get_adapter_stats,
)


class TestCreateMcpAdapter:
    """Test the core MCP adapter functionality."""

    @pytest.mark.asyncio
    async def test_successful_use_case_result(self):
        """Test adapter with successful UseCaseResult."""

        # Mock use case that returns success
        async def mock_use_case(param1: str, param2: int) -> UseCaseResult[dict]:
            return UseCaseResult.success_with_data({"result": f"{param1}:{param2}"})

        # Create adapter
        adapted = create_mcp_adapter(mock_use_case)

        # Execute
        result = await adapted(param1="test", param2=42)

        # Verify
        assert result == {"result": "test:42"}

    @pytest.mark.asyncio
    async def test_failed_use_case_result(self):
        """Test adapter with failed UseCaseResult."""

        # Mock use case that returns failure
        async def mock_use_case(param: str) -> UseCaseResult[Any]:
            return UseCaseResult.failure("Test error", context="test_context")

        # Create adapter
        adapted = create_mcp_adapter(mock_use_case)

        # Execute
        result = await adapted(param="test")

        # Verify error format
        assert result["success"] is False
        assert result["error"] == "Test error"
        assert result["details"]["context"] == "test_context"

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        """Test adapter handles unexpected exceptions."""

        # Mock use case that raises exception
        async def mock_use_case() -> UseCaseResult[Any]:
            raise ValueError("Unexpected error")

        # Create adapter
        adapted = create_mcp_adapter(mock_use_case)

        # Execute
        result = await adapted()

        # Verify exception handling
        assert result["success"] is False
        assert "Unexpected error" in result["error"]
        assert result["details"]["method"] == "mock_use_case"

    @pytest.mark.asyncio
    async def test_metadata_preservation(self):
        """Test that function metadata is preserved."""

        async def original_function(param: str) -> UseCaseResult[str]:
            """Original docstring."""
            return UseCaseResult.success(param)

        # Create adapter
        adapted = create_mcp_adapter(original_function)

        # Verify metadata preservation
        assert adapted.__name__ == "original_function"
        assert adapted.__doc__ == "Original docstring."
        assert hasattr(adapted, "__signature__")

    @pytest.mark.asyncio
    async def test_custom_success_handler(self):
        """Test adapter with custom success handler."""

        # Mock use case
        async def mock_use_case() -> UseCaseResult[dict]:
            return UseCaseResult.success_with_data({"data": "test"})

        # Custom success handler
        def custom_handler(data: Any) -> dict[str, Any]:
            return {"transformed": data, "custom": True}

        # Create adapter with custom handler
        adapted = create_mcp_adapter(
            mock_use_case, custom_success_handler=custom_handler
        )

        # Execute
        result = await adapted()

        # Verify custom transformation
        assert result["transformed"]["data"] == "test"
        assert result["custom"] is True

    @pytest.mark.asyncio
    async def test_custom_error_handler(self):
        """Test adapter with custom error handler."""

        # Mock use case that raises exception
        async def mock_use_case() -> UseCaseResult[Any]:
            raise ValueError("Test error")

        # Custom error handler
        def custom_error_handler(error: Exception) -> dict[str, Any]:
            return {"custom_error": True, "error_type": error.__class__.__name__}

        # Create adapter with custom error handler
        adapted = create_mcp_adapter(
            mock_use_case, custom_error_handler=custom_error_handler
        )

        # Execute
        result = await adapted()

        # Verify custom error handling
        assert result["custom_error"] is True
        assert result["error_type"] == "ValueError"

    def test_invalid_use_case_method(self):
        """Test adapter with invalid method."""
        with pytest.raises(ValueError, match="use_case_method must be callable"):
            create_mcp_adapter("not_callable")


class TestValidateUseCaseResult:
    """Test UseCaseResult validation."""

    def test_valid_result(self):
        """Test validation of valid UseCaseResult."""
        result = UseCaseResult.success("test")
        assert validate_use_case_result(result) is True

    def test_invalid_type(self):
        """Test validation with wrong type."""
        assert validate_use_case_result("not_a_result") is False

    def test_missing_attributes(self):
        """Test validation with missing attributes."""

        class MockResult:
            success = True
            # Missing other attributes

        assert validate_use_case_result(MockResult()) is False

    def test_invalid_attribute_types(self):
        """Test validation with wrong attribute types."""

        class MockResult:
            success = "not_bool"  # Should be bool
            data = None
            error = None
            details = {}

        assert validate_use_case_result(MockResult()) is False


class TestSpecializedAdapters:
    """Test specialized adapter creation functions."""

    @pytest.mark.asyncio
    async def test_query_adapter(self):
        """Test query-optimized adapter."""

        async def mock_query() -> UseCaseResult[list]:
            return UseCaseResult.success_with_data([1, 2, 3])

        adapted = create_query_adapter(mock_query)
        result = await adapted()

        assert result["data"] == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_command_adapter(self):
        """Test command-optimized adapter."""

        async def mock_command() -> UseCaseResult[str]:
            return UseCaseResult.success_with_data("created")

        adapted = create_command_adapter(mock_command)
        result = await adapted()

        assert result["success"] is True
        assert result["result"] == "created"

    @pytest.mark.asyncio
    async def test_validation_adapter(self):
        """Test validation-enhanced adapter."""

        async def mock_validation() -> UseCaseResult[Any]:
            raise ValueError("Invalid input")

        adapted = create_validation_adapter(mock_validation)
        result = await adapted()

        assert result["success"] is False
        assert result["error"] == "Validation failed"
        assert result["validation_error"] == "Invalid input"


class TestMockAdapter:
    """Test mock adapter for testing purposes."""

    @pytest.mark.asyncio
    async def test_mock_with_use_case_result(self):
        """Test mock adapter with UseCaseResult."""
        mock_result = UseCaseResult.success_with_data({"test": "data"})
        adapted = create_mock_adapter(mock_result)

        result = await adapted(param="ignored")
        assert result == {"test": "data"}

    @pytest.mark.asyncio
    async def test_mock_with_raw_result(self):
        """Test mock adapter with raw result."""
        mock_result = {"raw": "data"}
        adapted = create_mock_adapter(mock_result)

        result = await adapted()
        assert result == {"raw": "data"}


class TestAdapterStats:
    """Test adapter statistics functionality."""

    def test_get_adapter_stats(self):
        """Test adapter statistics retrieval."""
        stats = get_adapter_stats()

        assert isinstance(stats, AdapterStats)
        assert stats.version == "1.0.0"
        assert stats.boilerplate_lines_eliminated == 500
        assert "boilerplate" in stats.description


@pytest.mark.asyncio
async def test_integration_with_real_use_case_pattern():
    """Test integration with realistic use case pattern."""

    # Simulate a real use case class
    class ListProjectsUseCase:
        def __init__(self, project_service):
            self._project_service = project_service

        async def execute(self, instance_name: str) -> UseCaseResult[list[dict]]:
            try:
                projects = await self._project_service.get_projects(instance_name)
                return UseCaseResult.success_with_data(projects)
            except Exception as e:
                return UseCaseResult.failure(f"Failed to fetch projects: {str(e)}")

    # Mock service
    mock_service = AsyncMock()
    mock_service.get_projects.return_value = [
        {"key": "PROJ1", "name": "Project 1"},
        {"key": "PROJ2", "name": "Project 2"},
    ]

    # Create use case
    use_case = ListProjectsUseCase(mock_service)

    # Create MCP adapter
    adapted_method = create_mcp_adapter(use_case.execute)

    # Execute
    result = await adapted_method(instance_name="test")

    # Verify
    assert "result" in result
    projects = result["result"]
    assert len(projects) == 2
    assert projects[0]["key"] == "PROJ1"
    assert projects[1]["key"] == "PROJ2"

    # Verify service was called correctly
    mock_service.get_projects.assert_called_once_with("test")
