# MCP Commons

A Python library that simplifies building MCP (Model Context Protocol) servers by providing reusable infrastructure and eliminating repetitive boilerplate code.

## Why MCP Commons?

Building MCP servers often requires writing the same patterns repeatedly:
- Converting your business logic to MCP-compatible formats
- Handling errors consistently across tools
- Registering multiple tools with similar patterns
- Testing MCP tool implementations

MCP Commons solves these problems by providing a clean adapter pattern and bulk registration utilities, letting you focus on your core logic instead of MCP plumbing.

## Key Features

🔧 **Smart Adapters** - Automatically convert your functions to MCP-compatible tools
📦 **Bulk Registration** - Register multiple tools at once with consistent patterns  
🛡️ **Type Safety** - Preserve function signatures and type hints
🧪 **Testing Support** - Built-in utilities for testing your MCP tools
⚡ **Zero Dependencies** - Minimal footprint, works with any MCP setup

## Installation

```bash
pip install mcp-commons
```

## Quick Start

### Basic Adapter Usage

Instead of manually wrapping every function for MCP compatibility:

```python
from mcp_commons import create_mcp_adapter, UseCaseResult
from mcp import Tool

# Your business logic
async def search_documents(query: str, limit: int = 10) -> UseCaseResult:
    # Your implementation here
    results = await document_service.search(query, limit)
    return UseCaseResult.success_with_data(results)

# Convert to MCP tool automatically
search_tool = Tool.from_function(
    create_mcp_adapter(search_documents), 
    name="search_documents"
)
```

### Bulk Registration

Register multiple related tools at once:

```python
from mcp_commons import bulk_register_tools

# Define your tools
tools_config = [
    ("list_projects", list_projects_use_case),
    ("create_project", create_project_use_case), 
    ("delete_project", delete_project_use_case),
]

# Register them all with consistent error handling
tools = bulk_register_tools(tools_config)
```

### Error Handling

The adapter automatically handles errors and provides consistent response formats:

```python
async def might_fail() -> UseCaseResult:
    try:
        result = await risky_operation()
        return UseCaseResult.success_with_data(result)
    except ValidationError as e:
        return UseCaseResult.failure(f"Invalid input: {e}")
    except Exception as e:
        return UseCaseResult.failure(f"Operation failed: {e}")

# Errors are automatically converted to proper MCP error responses
safe_tool = Tool.from_function(create_mcp_adapter(might_fail), name="safe_operation")
```

## Use Cases

- **Enterprise MCP Servers**: Standardize tool creation across multiple servers
- **Rapid Prototyping**: Quickly convert existing functions to MCP tools
- **Testing & Development**: Mock and test MCP tools without complex setup
- **Legacy Integration**: Adapt existing business logic to MCP without rewrites

## Documentation

- [API Reference](https://github.com/dawsonlp/mcp-commons/wiki)
- [Examples](https://github.com/dawsonlp/mcp-commons/tree/main/examples)
- [Contributing](https://github.com/dawsonlp/mcp-commons/blob/main/CONTRIBUTING.md)

## Requirements

- Python 3.11+
- MCP SDK 1.13.1+

## License

MIT License - see [LICENSE](LICENSE) for details.
