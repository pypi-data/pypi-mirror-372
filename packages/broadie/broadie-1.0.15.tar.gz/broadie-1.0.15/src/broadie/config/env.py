"""
Environment configuration utilities.
Provides helpers for loading and validating environment variables.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, cast

T = TypeVar("T")


class EnvironmentConfig:
    """
    Utility class for handling environment variable configuration.

    Provides type-safe environment variable loading with defaults and validation.
    """

    @staticmethod
    def get_str(key: str, default: str = "") -> str:
        """Get string environment variable."""
        return os.getenv(key, default)

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' must be an integer, got: {value}"
            )

    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """Get float environment variable."""
        value = os.getenv(key)
        if value is None:
            return default
        try:
            return float(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' must be a float, got: {value}"
            )

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = os.getenv(key)
        if value is None:
            return default

        return value.lower() in ("true", "1", "yes", "on")

    @staticmethod
    def get_list(
        key: str, separator: str = ",", default: Optional[List[str]] = None
    ) -> List[str]:
        """Get list environment variable by splitting on separator."""
        if default is None:
            default = []

        value = os.getenv(key)
        if value is None:
            return default

        return [item.strip() for item in value.split(separator) if item.strip()]

    @staticmethod
    def get_path(
        key: str, default: Optional[Union[str, Path]] = None
    ) -> Optional[Path]:
        """Get Path environment variable."""
        value = os.getenv(key)
        if value is None:
            return Path(default) if default else None

        return Path(value)

    @staticmethod
    def require_str(key: str) -> str:
        """Get required string environment variable."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    @staticmethod
    def require_int(key: str) -> int:
        """Get required integer environment variable."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        try:
            return int(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' must be an integer, got: {value}"
            )

    @staticmethod
    def require_float(key: str) -> float:
        """Get required float environment variable."""
        value = os.getenv(key)
        if value is None:
            raise ValueError(f"Required environment variable '{key}' is not set")
        try:
            return float(value)
        except ValueError:
            raise ValueError(
                f"Environment variable '{key}' must be a float, got: {value}"
            )

    @staticmethod
    def get_typed(key: str, type_: Type[T], default: T) -> T:
        """Get environment variable with type conversion."""
        value = os.getenv(key)
        if value is None:
            return default

        try:
            if type_ == bool:
                return cast(T, value.lower() in ("true", "1", "yes", "on"))
            else:
                return type_(value)
        except (ValueError, TypeError):
            raise ValueError(
                f"Environment variable '{key}' cannot be converted to {type_.__name__}, got: {value}"
            )

    @classmethod
    def load_env_file(
        cls, env_file: Union[str, Path] = ".env", verbose: bool = False
    ) -> Dict[str, str]:
        """
        Load environment variables from a file.

        Args:
            env_file: Path to the .env file
            verbose: Whether to print loaded variables

        Returns:
            Dictionary of loaded environment variables
        """
        from dotenv import load_dotenv

        env_path = Path(env_file)
        if not env_path.exists():
            if verbose:
                print(f"Environment file {env_path} not found")
            return {}

        # Store original environment
        original_env = dict(os.environ)

        # Load the .env file
        load_dotenv(env_path, verbose=verbose)

        # Return only the newly loaded variables
        loaded_vars = {}
        for key, value in os.environ.items():
            if key not in original_env or original_env[key] != value:
                loaded_vars[key] = value

        return loaded_vars

    @classmethod
    def validate_required_vars(cls, required_vars: List[str]) -> Dict[str, str]:
        """
        Validate that all required environment variables are set.

        Args:
            required_vars: List of required environment variable names

        Returns:
            Dictionary of validated environment variables

        Raises:
            ValueError: If any required variables are missing
        """
        missing_vars = []
        validated_vars = {}

        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            else:
                validated_vars[var] = value

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        return validated_vars

    @classmethod
    def get_config_dict(
        cls, prefix: str = "", strip_prefix: bool = True
    ) -> Dict[str, str]:
        """
        Get all environment variables with a given prefix.

        Args:
            prefix: Environment variable prefix to filter by
            strip_prefix: Whether to remove the prefix from keys in the result

        Returns:
            Dictionary of filtered environment variables
        """
        config = {}

        for key, value in os.environ.items():
            if key.startswith(prefix):
                result_key = key[len(prefix) :] if strip_prefix else key
                config[result_key] = value

        return config

    @classmethod
    def export_to_file(
        cls,
        output_file: Union[str, Path],
        prefix: str = "",
        exclude: Optional[List[str]] = None,
    ):
        """
        Export environment variables to a .env file.

        Args:
            output_file: Path to output .env file
            prefix: Only export variables with this prefix
            exclude: List of variable names to exclude
        """
        exclude = exclude or []

        with open(output_file, "w") as f:
            for key, value in sorted(os.environ.items()):
                if prefix and not key.startswith(prefix):
                    continue
                if key in exclude:
                    continue

                # Escape quotes in values
                escaped_value = value.replace('"', '\\"')
                f.write(f'{key}="{escaped_value}"\n')


def load_env_with_validation() -> Dict[str, Any]:
    """
    Load environment variables with basic validation for Broadie.

    Returns:
        Dictionary of validated environment variables
    """
    env = EnvironmentConfig()

    # Load .env file if it exists
    env.load_env_file(verbose=True)

    # Basic configuration
    config = {
        "default_model": env.get_str("DEFAULT_GEMINI_MODEL", "gemini-2.0-flash"),
        "log_level": env.get_str("LOG_LEVEL", "INFO"),
        "debug": env.get_bool("DEBUG", False),
        "google_api_key": env.get_str("GOOGLE_API_KEY"),
        "google_genai_use_vertexai": env.get_bool("GOOGLE_GENAI_USE_VERTEXAI", True),
    }

    # A2A configuration
    a2a_config = {
        "enabled": env.get_bool("A2A_ENABLED", True),
        "agent_id": env.get_str("A2A_AGENT_ID"),
        "agent_name": env.get_str("A2A_AGENT_NAME"),
        "trusted_agents": env.get_list("A2A_TRUSTED_AGENTS"),
        "registry_url": env.get_str("A2A_REGISTRY_URL"),
    }

    # Database configuration
    db_config = {
        "url": env.get_str("DATABASE_URL"),
        "driver": env.get_str("DB_DRIVER", "sqlite"),
        "name": env.get_str("DB_NAME", "broadie.db"),
        "host": env.get_str("DB_HOST", "localhost"),
        "port": env.get_int("DB_PORT", 5432),
        "username": env.get_str("DB_USERNAME"),
        "password": env.get_str("DB_PASSWORD"),
    }

    # Slack configuration
    slack_config = {
        "bot_token": env.get_str("SLACK_BOT_TOKEN"),
        "channel": env.get_str("SLACK_CHANNEL"),
        "webhook_url": env.get_str("SLACK_WEBHOOK_URL"),
    }

    return {
        **config,
        "a2a": a2a_config,
        "database": db_config,
        "slack": slack_config,
    }
