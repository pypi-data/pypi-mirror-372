"""
Common configuration management for MCP servers.

This module provides standardized configuration loading, environment variable management,
and validation patterns that can be shared across all MCP servers.
"""

import logging
import os
from pathlib import Path
from typing import Any

import yaml

from .exceptions import McpCommonsError

logger = logging.getLogger(__name__)


class ConfigurationError(McpCommonsError):
    """Raised when there are configuration-related errors."""

    pass


class MCPConfig:
    """
    Standardized configuration management for MCP servers.

    This class provides a unified way to handle configuration across MCP servers,
    eliminating duplicated configuration management code.
    """

    def __init__(self, config_file: str | None = None, env_prefix: str = "MCP"):
        """
        Initialize configuration management.

        Args:
            config_file: Path to configuration file (YAML format)
            env_prefix: Prefix for environment variables (default: "MCP")
        """
        self.env_prefix = env_prefix
        self.config_data: dict[str, Any] = {}
        self.config_file = config_file

        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)

    def load_from_file(self, config_file: str) -> None:
        """
        Load configuration from a YAML file.

        Args:
            config_file: Path to the configuration file

        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        try:
            config_path = Path(config_file)
            if not config_path.exists():
                logger.warning(f"Configuration file {config_file} does not exist")
                return

            with open(config_path) as f:
                file_config = yaml.safe_load(f) or {}
                self.config_data.update(file_config)
                logger.info(f"Loaded configuration from {config_file}")

        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Failed to parse YAML configuration file {config_file}: {e}"
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration file {config_file}: {e}"
            )

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a configuration value with environment variable override support.

        The lookup order is:
        1. Environment variable: {ENV_PREFIX}_{SECTION}_{KEY} (uppercase)
        2. Configuration file: section.key
        3. Default value

        Args:
            section: Configuration section name
            key: Configuration key name
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Check environment variable first
        env_var = f"{self.env_prefix}_{section.upper()}_{key.upper()}"
        env_value = os.getenv(env_var)
        if env_value is not None:
            return self._convert_env_value(env_value)

        # Check configuration file
        if section in self.config_data and key in self.config_data[section]:
            return self.config_data[section][key]

        # Return default
        return default

    def get_section(
        self, section: str, defaults: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Get an entire configuration section with environment variable overrides.

        Args:
            section: Configuration section name
            defaults: Default values for the section

        Returns:
            Dictionary containing the section configuration
        """
        result = {}

        # Start with defaults
        if defaults:
            result.update(defaults)

        # Add configuration file values
        if section in self.config_data:
            result.update(self.config_data[section])

        # Override with environment variables
        env_prefix = f"{self.env_prefix}_{section.upper()}_"
        for env_var, value in os.environ.items():
            if env_var.startswith(env_prefix):
                key = env_var[len(env_prefix) :].lower()
                result[key] = self._convert_env_value(value)

        return result

    def require(self, section: str, key: str) -> Any:
        """
        Get a required configuration value, raising an error if not found.

        Args:
            section: Configuration section name
            key: Configuration key name

        Returns:
            Configuration value

        Raises:
            ConfigurationError: If the required value is not found
        """
        value = self.get(section, key)
        if value is None:
            env_var = f"{self.env_prefix}_{section.upper()}_{key.upper()}"
            raise ConfigurationError(
                f"Required configuration value missing: {section}.{key} "
                f"(can also be set via environment variable {env_var})"
            )
        return value

    def validate_required(self, required_config: list[tuple]) -> None:
        """
        Validate that all required configuration values are present.

        Args:
            required_config: List of (section, key) tuples for required config

        Raises:
            ConfigurationError: If any required values are missing
        """
        missing = []
        for section, key in required_config:
            if self.get(section, key) is None:
                env_var = f"{self.env_prefix}_{section.upper()}_{key.upper()}"
                missing.append(f"{section}.{key} (or {env_var})")

        if missing:
            raise ConfigurationError(
                f"Missing required configuration values: {', '.join(missing)}"
            )

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a configuration value programmatically.

        Args:
            section: Configuration section name
            key: Configuration key name
            value: Value to set
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value

    def update_section(self, section: str, values: dict[str, Any]) -> None:
        """
        Update an entire configuration section.

        Args:
            section: Configuration section name
            values: Dictionary of key-value pairs to update
        """
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section].update(values)

    def _convert_env_value(self, value: str) -> str | int | float | bool:
        """
        Convert environment variable string to appropriate Python type.

        Args:
            value: String value from environment variable

        Returns:
            Converted value (str, int, float, or bool)
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        if value.lower() in ("false", "no", "0", "off"):
            return False

        # Try to convert to number
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass

        # Return as string
        return value

    def get_server_defaults(self) -> dict[str, Any]:
        """
        Get standard server configuration defaults.

        Returns:
            Dictionary containing default server configuration
        """
        return {
            "name": "mcp-server",
            "host": "localhost",
            "port": 7501,
            "debug": True,
            "log_level": "INFO",
        }

    def to_dict(self) -> dict[str, Any]:
        """
        Get the complete configuration as a dictionary.

        Returns:
            Complete configuration dictionary
        """
        return self.config_data.copy()


def create_config(
    config_file: str | None = None,
    env_prefix: str = "MCP",
    required_config: list[tuple] | None = None,
) -> MCPConfig:
    """
    Create and validate a standardized MCP server configuration.

    This function provides a common pattern for initializing configuration
    that can be used across all MCP servers.

    Args:
        config_file: Path to configuration file (optional)
        env_prefix: Prefix for environment variables
        required_config: List of (section, key) tuples for required config

    Returns:
        Configured MCPConfig instance

    Raises:
        ConfigurationError: If required configuration is missing
    """
    # Look for common config file locations if not specified
    if config_file is None:
        possible_locations = ["config.yaml", "config.yml", ".env.yaml", ".env.yml"]
        for location in possible_locations:
            if os.path.exists(location):
                config_file = location
                break

    # Create configuration instance
    config = MCPConfig(config_file=config_file, env_prefix=env_prefix)

    # Validate required configuration if specified
    if required_config:
        config.validate_required(required_config)

    logger.info(
        f"Configuration initialized (file: {config_file or 'none'}, prefix: {env_prefix})"
    )
    return config


def load_dotenv_file(dotenv_path: str = ".env") -> None:
    """
    Load environment variables from a .env file.

    This provides a simple way to load environment variables without
    requiring the python-dotenv dependency in every server.

    Args:
        dotenv_path: Path to the .env file
    """
    if not os.path.exists(dotenv_path):
        logger.debug(f"No .env file found at {dotenv_path}")
        return

    try:
        with open(dotenv_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key not in os.environ:  # Don't override existing env vars
                        os.environ[key] = value

        logger.info(f"Loaded environment variables from {dotenv_path}")

    except Exception as e:
        logger.warning(f"Failed to load .env file {dotenv_path}: {e}")
