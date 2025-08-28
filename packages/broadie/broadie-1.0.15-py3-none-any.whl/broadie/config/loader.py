"""
Configuration loader for Broadie agents.
Handles loading and validation of JSON configuration files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ValidationError

from ..utils.exceptions import ConfigurationError


class AgentConfigSchema(BaseModel):
    """Schema for agent configuration validation."""

    name: str
    description: str = ""
    instruction: str = ""
    model: Optional[Dict[str, Any]] = None
    tools: List[str] = []
    model_settings: Dict[str, Any] = {}
    sub_agents: List[str] = []  # File paths to sub-agent configs


class SubAgentConfigSchema(BaseModel):
    """Schema for sub-agent configuration validation."""

    name: str
    description: str = ""
    prompt: str = ""
    tools: List[str] = []
    model_settings: Dict[str, Any] = {}


class ConfigLoader:
    """
    Configuration loader with validation and schema support.

    Follows the Single Responsibility Principle by focusing solely on
    configuration loading and validation.
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path.cwd()

    def load_agent_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load and validate agent configuration from JSON file.

        Args:
            config_path: Path to the agent configuration file

        Returns:
            Validated configuration dictionary

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            config_path = self._resolve_path(config_path)

            if not config_path.exists():
                raise ConfigurationError(f"Configuration file not found: {config_path}")

            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # If model not provided, assume sensible default (Gemini 2.0 Flash)
            if not isinstance(config_data.get("model"), dict):
                config_data["model"] = {
                    "provider": "google",
                    "name": "gemini-2.0-flash",
                }

            # Validate against schema
            try:
                validated_config = AgentConfigSchema(**config_data)
                return validated_config.model_dump()
            except ValidationError as e:
                raise ConfigurationError(
                    f"Invalid agent configuration in {config_path}: {e}"
                )

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(
                f"Error loading configuration from {config_path}: {e}"
            )

    def load_sub_agent_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load and validate sub-agent configuration from JSON file.

        Args:
            config_path: Path to the sub-agent configuration file

        Returns:
            Validated configuration dictionary
        """
        try:
            config_path = self._resolve_path(config_path)

            if not config_path.exists():
                raise ConfigurationError(
                    f"Sub-agent configuration file not found: {config_path}"
                )

            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            # Validate against schema
            try:
                validated_config = SubAgentConfigSchema(**config_data)
                return validated_config.model_dump()
            except ValidationError as e:
                raise ConfigurationError(
                    f"Invalid sub-agent configuration in {config_path}: {e}"
                )

        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in {config_path}: {e}")
        except Exception as e:
            raise ConfigurationError(
                f"Error loading sub-agent configuration from {config_path}: {e}"
            )

    def load_agent_with_sub_agents(
        self, config_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Load agent configuration including all referenced sub-agents.

        Args:
            config_path: Path to the main agent configuration file

        Returns:
            Configuration dictionary with loaded sub-agents
        """
        # Load main agent config
        agent_config = self.load_agent_config(config_path)

        # Load sub-agent configurations
        loaded_sub_agents = []
        for sub_agent_path in agent_config.get("sub_agents", []):
            try:
                sub_agent_config = self.load_sub_agent_config(sub_agent_path)
                loaded_sub_agents.append(sub_agent_config)
            except ConfigurationError as e:
                raise ConfigurationError(
                    f"Error loading sub-agent '{sub_agent_path}': {e}"
                )

        # Replace file paths with loaded configurations
        agent_config["sub_agents"] = loaded_sub_agents

        return agent_config

    def save_agent_config(self, config: Dict[str, Any], output_path: Union[str, Path]):
        """
        Save agent configuration to JSON file.

        Args:
            config: Configuration dictionary to save
            output_path: Path where to save the configuration
        """
        try:
            # Validate configuration before saving
            AgentConfigSchema(**config)

            output_path = self._resolve_path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except ValidationError as e:
            raise ConfigurationError(f"Invalid configuration for saving: {e}")
        except Exception as e:
            raise ConfigurationError(
                f"Error saving configuration to {output_path}: {e}"
            )

    def save_sub_agent_config(
        self, config: Dict[str, Any], output_path: Union[str, Path]
    ):
        """
        Save sub-agent configuration to JSON file.

        Args:
            config: Sub-agent configuration dictionary to save
            output_path: Path where to save the configuration
        """
        try:
            # Validate configuration before saving
            SubAgentConfigSchema(**config)

            output_path = self._resolve_path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

        except ValidationError as e:
            raise ConfigurationError(f"Invalid sub-agent configuration for saving: {e}")
        except Exception as e:
            raise ConfigurationError(
                f"Error saving sub-agent configuration to {output_path}: {e}"
            )

    def validate_config_file(
        self, config_path: Union[str, Path], config_type: str = "agent"
    ) -> bool:
        """
        Validate a configuration file without loading it completely.

        Args:
            config_path: Path to the configuration file
            config_type: Type of configuration ("agent" or "sub_agent")

        Returns:
            True if valid, False otherwise

        Raises:
            ConfigurationError: If validation fails
        """
        try:
            if config_type == "agent":
                self.load_agent_config(config_path)
            elif config_type == "sub_agent":
                self.load_sub_agent_config(config_path)
            else:
                raise ValueError(f"Unknown config type: {config_type}")

            return True

        except ConfigurationError:
            return False

    def list_config_files(
        self, directory: Union[str, Path], pattern: str = "*.json"
    ) -> List[Path]:
        """
        List all configuration files in a directory.

        Args:
            directory: Directory to search for configuration files
            pattern: File pattern to match (default: "*.json")

        Returns:
            List of configuration file paths
        """
        directory = self._resolve_path(directory)

        if not directory.exists() or not directory.is_dir():
            return []

        return list(directory.glob(pattern))

    def merge_configs(
        self, base_config: Dict[str, Any], override_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge two configuration dictionaries.

        Args:
            base_config: Base configuration
            override_config: Configuration to merge in (takes precedence)

        Returns:
            Merged configuration dictionary
        """
        merged = base_config.copy()

        for key, value in override_config.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self.merge_configs(merged[key], value)
            else:
                merged[key] = value

        return merged

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """Resolve a path relative to the base path."""
        path = Path(path)

        if path.is_absolute():
            return path
        else:
            return self.base_path / path

    def create_template_config(
        self, config_type: str = "agent", **kwargs
    ) -> Dict[str, Any]:
        """
        Create a template configuration with default values.

        Args:
            config_type: Type of configuration to create ("agent" or "sub_agent")
            **kwargs: Override default values

        Returns:
            Template configuration dictionary
        """
        if config_type == "agent":
            template = {
                "name": kwargs.get("name", "my_agent"),
                "description": kwargs.get("description", "A Broadie agent"),
                "instruction": kwargs.get(
                    "instruction", "You are a helpful AI assistant."
                ),
                "model": kwargs.get(
                    "model", {"provider": "google", "name": "gemini-2.0-flash"}
                ),
                "tools": kwargs.get("tools", []),
                "model_settings": kwargs.get("model_settings", {}),
                "sub_agents": kwargs.get("sub_agents", []),
            }
        elif config_type == "sub_agent":
            template = {
                "name": kwargs.get("name", "my_sub_agent"),
                "description": kwargs.get("description", "A specialized sub-agent"),
                "prompt": kwargs.get("prompt", "You are a specialized assistant."),
                "tools": kwargs.get("tools", []),
                "model_settings": kwargs.get("model_settings", {}),
            }
        else:
            raise ValueError(f"Unknown config type: {config_type}")

        return template
