"""
Settings management for Broadie based on existing patterns.
Reuses the existing settings structure and extends it.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from dotenv import load_dotenv

    # Load environment variables from .env if available
    load_dotenv(verbose=True)
except ImportError:
    # Fallback stub if python-dotenv not installed
    def load_dotenv(verbose=False):
        return None


class ModelConfig(BaseModel):
    """Model configuration."""

    provider: str = "google"
    name: str = "gemini-2.0-flash"
    temperature: float = 0.2
    max_tokens: int = 50000
    max_retries: int = 2
    timeout: Optional[float] = None


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: Optional[str] = None
    driver: str = "sqlite"  # sqlite, postgresql
    name: str = "broadie.db"
    host: str = "localhost"
    port: int = 5432
    username: Optional[str] = None
    password: Optional[str] = None


class A2AConfig(BaseModel):
    """Agent-to-Agent communication configuration."""

    enabled: bool = True
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    trusted_agents: List[str] = Field(default_factory=list)
    registry_url: Optional[str] = None
    heartbeat_interval: int = 30  # seconds
    discovery_interval: int = 60  # seconds


class SlackConfig(BaseModel):
    """Slack notification configuration."""

    enabled: bool = False
    bot_token: Optional[str] = None
    channel: Optional[str] = None
    webhook_url: Optional[str] = None


class EmailConfig(BaseModel):
    """Email notification configuration."""

    enabled: bool = False
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_address: Optional[str] = None
    from_name: str = "Broadie Agent"
    use_tls: bool = True


class BroadieSettings(BaseSettings):
    """
    Main settings class for Broadie application.

    Inherits from existing settings patterns and extends with new features.
    """

    # Basic settings
    app_name: str = "Broadie"
    debug: bool = False
    log_level: str = "INFO"

    # Model settings (reuse existing pattern)
    default_model: str = Field(default="gemini-2.0-flash", alias="DEFAULT_GEMINI_MODEL")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    google_genai_use_vertexai: bool = Field(
        default=True, alias="GOOGLE_GENAI_USE_VERTEXAI"
    )

    # API server settings
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, alias="PORT")
    api_prefix: str = ""

    # Database settings
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    # A2A settings
    a2a: A2AConfig = Field(default_factory=A2AConfig)

    # Notification settings
    slack: SlackConfig = Field(default_factory=SlackConfig)
    email: EmailConfig = Field(default_factory=EmailConfig)

    # File paths
    config_dir: Path = Field(default_factory=lambda: Path.cwd() / "config")
    data_dir: Path = Field(default_factory=lambda: Path.cwd() / "data")
    logs_dir: Path = Field(default_factory=lambda: Path.cwd() / "logs")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_nested_delimiter="__",
        # Custom field mappings for environment variables
        env_ignore_empty=True,
        extra="ignore",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load A2A settings from environment
        self.a2a.agent_id = os.getenv("A2A_AGENT_ID", self.a2a.agent_id)
        self.a2a.agent_name = os.getenv("A2A_AGENT_NAME", self.a2a.agent_name)
        self.a2a.enabled = os.getenv("A2A_ENABLED", "true").lower() == "true"

        # Parse trusted agents list
        trusted_agents_str = os.getenv("A2A_TRUSTED_AGENTS", "")
        if trusted_agents_str:
            self.a2a.trusted_agents = [
                agent.strip()
                for agent in trusted_agents_str.split(",")
                if agent.strip()
            ]

        self.a2a.registry_url = os.getenv("A2A_REGISTRY_URL", self.a2a.registry_url)

        # Load Slack settings
        self.slack.bot_token = os.getenv("SLACK_BOT_TOKEN", self.slack.bot_token)
        self.slack.channel = os.getenv("SLACK_CHANNEL", self.slack.channel)
        self.slack.webhook_url = os.getenv("SLACK_WEBHOOK_URL", self.slack.webhook_url)
        self.slack.enabled = bool(self.slack.bot_token or self.slack.webhook_url)

        # Load Email settings
        self.email.smtp_host = os.getenv("EMAIL_SMTP_HOST", self.email.smtp_host)
        self.email.smtp_port = int(
            os.getenv("EMAIL_SMTP_PORT", str(self.email.smtp_port))
        )
        self.email.smtp_user = os.getenv("EMAIL_SMTP_USER", self.email.smtp_user)
        self.email.smtp_password = os.getenv(
            "EMAIL_SMTP_PASSWORD", self.email.smtp_password
        )
        self.email.from_address = os.getenv(
            "EMAIL_FROM_ADDRESS", self.email.from_address
        )
        self.email.from_name = os.getenv("EMAIL_FROM_NAME", self.email.from_name)
        self.email.use_tls = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"
        self.email.enabled = bool(
            self.email.smtp_host and self.email.smtp_user and self.email.smtp_password
        )

        # Load database settings
        db_url = os.getenv("DATABASE_URL")
        if db_url:
            self.database.url = db_url
        else:
            self.database.driver = os.getenv("DB_DRIVER", "sqlite")
            self.database.name = os.getenv("DB_NAME", "broadie.db")
            self.database.host = os.getenv("DB_HOST", "localhost")
            self.database.port = int(os.getenv("DB_PORT", "5432"))
            self.database.username = os.getenv("DB_USERNAME")
            self.database.password = os.getenv("DB_PASSWORD")

        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        if self.database.url:
            return self.database.url

        if self.database.driver == "sqlite":
            return f"sqlite:///{self.data_dir / self.database.name}"
        elif self.database.driver == "postgresql":
            if self.database.username and self.database.password:
                return f"postgresql://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.name}"
            else:
                return f"postgresql://{self.database.host}:{self.database.port}/{self.database.name}"
        else:
            raise ValueError(f"Unsupported database driver: {self.database.driver}")

    @property
    def email_smtp_host(self) -> Optional[str]:
        """Get SMTP host for email."""
        return self.email.smtp_host

    @property
    def email_smtp_port(self) -> int:
        """Get SMTP port for email."""
        return self.email.smtp_port

    @property
    def email_smtp_user(self) -> Optional[str]:
        """Get SMTP user for email."""
        return self.email.smtp_user

    @property
    def email_smtp_password(self) -> Optional[str]:
        """Get SMTP password for email."""
        return self.email.smtp_password

    @property
    def email_from_address(self) -> Optional[str]:
        """Get from address for email."""
        return self.email.from_address

    @property
    def email_from_name(self) -> str:
        """Get from name for email."""
        return self.email.from_name

    def get_model_config(
        self, overrides: Optional[Dict[str, Any]] = None
    ) -> ModelConfig:
        """Get model configuration with optional overrides."""
        config = ModelConfig(
            provider="google",
            name=self.default_model,
        )

        if overrides:
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)

        return config

    def is_a2a_enabled(self) -> bool:
        """Check if A2A communication is enabled and properly configured."""
        return (
            self.a2a.enabled
            and self.a2a.agent_id is not None
            and self.a2a.agent_name is not None
        )

    def is_slack_enabled(self) -> bool:
        """Check if Slack notifications are enabled and configured."""
        return self.slack.enabled and (
            self.slack.bot_token is not None or self.slack.webhook_url is not None
        )

    @property
    def slack_bot_token(self) -> Optional[str]:
        """Get Slack bot token."""
        return self.slack.bot_token

    @property
    def slack_channel(self) -> Optional[str]:
        """Get Slack channel."""
        return self.slack.channel

    @property
    def slack_webhook_url(self) -> Optional[str]:
        """Get Slack webhook URL."""
        return self.slack.webhook_url


# Backward compatibility - reuse existing pattern
DEFAULT_GEMINI_MODEL = os.getenv("DEFAULT_GEMINI_MODEL", "gemini-2.0-flash")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GOOGLE_GENAI_USE_VERTEXAI = os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "1")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
