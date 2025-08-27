"""
Common server startup utilities for MCP servers.

This module provides standardized server initialization, configuration management,
and startup patterns that can be shared across all MCP servers.
"""

import logging
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from .bulk_registration import bulk_register_tools, log_registration_summary

# Set up logging
logger = logging.getLogger(__name__)


class MCPServerBuilder:
    """
    Builder class for creating standardized MCP servers with common patterns.

    This eliminates duplicated server setup code across different MCP server implementations.
    """

    def __init__(self, server_name: str):
        """
        Initialize the MCP server builder.

        Args:
            server_name: Name of the MCP server
        """
        self.server_name = server_name
        self.server_instance: FastMCP | None = None
        self.tools_config: dict[str, dict[str, Any]] = {}
        self.config = {}
        self.debug = True
        self.log_level = "INFO"

    def with_tools_config(
        self, tools_config: dict[str, dict[str, Any]]
    ) -> "MCPServerBuilder":
        """
        Configure the tools that will be registered with the server.

        Args:
            tools_config: Dictionary mapping tool names to their configuration

        Returns:
            Self for method chaining
        """
        self.tools_config = tools_config
        return self

    def with_config(self, config: dict[str, Any]) -> "MCPServerBuilder":
        """
        Set server configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Self for method chaining
        """
        self.config = config
        return self

    def with_debug(self, debug: bool = True) -> "MCPServerBuilder":
        """
        Enable or disable debug mode.

        Args:
            debug: Whether to enable debug mode

        Returns:
            Self for method chaining
        """
        self.debug = debug
        return self

    def with_log_level(self, log_level: str = "INFO") -> "MCPServerBuilder":
        """
        Set logging level.

        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

        Returns:
            Self for method chaining
        """
        self.log_level = log_level
        return self

    def build(self) -> FastMCP:
        """
        Build and configure the MCP server instance.

        Returns:
            Configured FastMCP server instance
        """
        # Create the MCP server
        self.server_instance = FastMCP(self.server_name)

        # Register tools if provided
        if self.tools_config:
            registered_tools = bulk_register_tools(
                self.server_instance, self.tools_config
            )
            log_registration_summary(
                registered_tools, len(self.tools_config), self.server_name
            )

        # Configure server settings
        self.server_instance.settings.debug = self.debug
        self.server_instance.settings.log_level = self.log_level

        logger.info(f"{self.server_name} MCP server built successfully")
        return self.server_instance


def setup_logging(log_level: str = "INFO") -> None:
    """
    Set up standardized logging configuration for MCP servers.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def run_mcp_server(
    server_name: str,
    tools_config: dict[str, dict[str, Any]],
    config: dict[str, Any] | None = None,
    transport: str = "sse",
    host: str = "localhost",
    port: int = 7501,
) -> None:
    """
    Run an MCP server with standardized configuration.

    This function eliminates boilerplate server startup code that's common
    across all MCP server implementations.

    Args:
        server_name: Name of the MCP server
        tools_config: Dictionary mapping tool names to their configuration
        config: Optional server configuration dictionary
        transport: Transport type ("sse" or "stdio")
        host: Host for SSE transport (default: localhost)
        port: Port for SSE transport (default: 7501)
    """
    # Set up logging
    setup_logging()

    # Build the server
    builder = MCPServerBuilder(server_name)
    builder.with_tools_config(tools_config)

    if config:
        builder.with_config(config)

    server = builder.build()

    # Configure transport settings
    if transport == "sse":
        server.settings.host = host
        server.settings.port = port
        logger.info(f"Starting {server_name} with HTTP+SSE transport on {host}:{port}")
    else:  # stdio
        logger.info(f"Starting {server_name} with stdio transport")

    # Run the server
    server.run(transport)


def create_mcp_app(
    server_name: str,
    tools_config: dict[str, dict[str, Any]],
    config: dict[str, Any] | None = None,
) -> Any:
    """
    Create an ASGI application for use with an external ASGI server.

    This function standardizes ASGI app creation across MCP servers.

    Args:
        server_name: Name of the MCP server
        tools_config: Dictionary mapping tool names to their configuration
        config: Optional server configuration dictionary

    Returns:
        ASGI application instance
    """
    # Build the server
    builder = MCPServerBuilder(server_name)
    builder.with_tools_config(tools_config)

    if config:
        builder.with_config(config)

    server = builder.build()

    logger.info(f"{server_name} ASGI app created successfully")
    return server.sse_app()


def print_mcp_help(server_name: str, description: str = "MCP Server") -> None:
    """
    Print standardized help information for MCP servers.

    Args:
        server_name: Name of the MCP server
        description: Description of what the server does
    """
    help_text = f"""
{server_name} {description} Usage Guide
{'=' * (len(server_name) + len(description) + 13)}

BASIC USAGE:
-----------
  python main.py sse        # Run as HTTP+SSE server (for network/container use)
  python main.py stdio      # Run as stdio server (for local development)
  python main.py help       # Show this help message

CONNECTING TO CLAUDE/CLINE:
------------------------
To connect this MCP server to Claude Desktop or Cline in VS Code:

1. First make sure your MCP server is running with the sse transport:
   python main.py sse

2. For Cline in VS Code, edit the settings file:
   ~/.config/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json

   Example configuration:
   {{
     "mcpServers": {{
       "{server_name}": {{
         "url": "http://localhost:7501/sse",
         "apiKey": "example_key",
         "disabled": false,
         "autoApprove": []
       }}
     }}
   }}

3. For Claude Desktop, go to:
   Settings → Advanced → MCP Servers → Add MCP Server

   Enter:
   - Name: {server_name}
   - URL: http://localhost:7501
   - API Key: example_key (or your custom API key)

4. Restart Claude/VS Code to apply the changes

DEPLOYMENT:
----------
- For local development: Use 'stdio' transport
- For Docker/containers: Use 'sse' transport with port 7501
- Configure with environment variables or .env file

For more information, see the MCP SDK documentation at:
https://github.com/modelcontextprotocol/python-sdk
"""
    print(help_text)
