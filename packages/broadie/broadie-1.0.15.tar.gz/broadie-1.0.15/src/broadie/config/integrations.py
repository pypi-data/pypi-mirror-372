"""
Configuration system for integration tools.

This module provides configuration management for Google Drive, Slack,
and other integration tools used by Broadie agents.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class GoogleDriveConfig(BaseModel):
    """Configuration for Google Drive integration."""

    service_account_file: Optional[str] = Field(
        default=None, description="Path to Google service account JSON file"
    )
    delegated_user: Optional[str] = Field(
        default=None,
        description="Email of user to impersonate (for domain-wide delegation)",
    )
    scopes: list[str] = Field(
        default=[
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets",
        ],
        description="OAuth scopes for Google Drive access",
    )


class SlackConfig(BaseModel):
    """Configuration for Slack integration."""

    bot_token: Optional[str] = Field(
        default=None, description="Slack bot token (xoxb-...)"
    )
    user_token: Optional[str] = Field(
        default=None,
        description="Slack user token (xoxp-...) for additional permissions",
    )
    signing_secret: Optional[str] = Field(
        default=None, description="Slack signing secret for webhook verification"
    )


class IntegrationsConfig(BaseSettings):
    """Main configuration class for all integrations."""

    google_drive: GoogleDriveConfig = Field(
        default_factory=GoogleDriveConfig,
        description="Google Drive integration settings",
    )

    slack: SlackConfig = Field(
        default_factory=SlackConfig, description="Slack integration settings"
    )

    class Config:
        env_prefix = "BROADIE_"
        env_nested_delimiter = "__"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "IntegrationsConfig":
        """Create configuration from environment variables."""
        return cls(
            google_drive=GoogleDriveConfig(
                service_account_file=os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE"),
                delegated_user=os.getenv("GOOGLE_DELEGATED_USER"),
            ),
            slack=SlackConfig(
                bot_token=os.getenv("SLACK_BOT_TOKEN"),
                user_token=os.getenv("SLACK_USER_TOKEN"),
                signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
            ),
        )

    @classmethod
    def from_file(cls, config_path: Path) -> "IntegrationsConfig":
        """Load configuration from JSON file."""
        import json

        with open(config_path, "r") as f:
            data = json.load(f)
        return cls(**data)

    def is_google_drive_configured(self) -> bool:
        """Check if Google Drive is properly configured."""
        return (
            self.google_drive.service_account_file is not None
            and Path(self.google_drive.service_account_file).exists()
        )

    def is_slack_configured(self) -> bool:
        """Check if Slack is properly configured."""
        return self.slack.bot_token is not None

    def get_available_tools(self) -> Dict[str, list[str]]:
        """Get list of available integration tools by category."""
        tools = {}

        if self.is_google_drive_configured():
            tools["google_drive"] = [
                "search_google_drive",
                "read_google_drive_file",
                "write_google_drive_file",
                "create_google_sheet",
                "update_google_sheet",
                "list_drive_folders",
            ]

        if self.is_slack_configured():
            tools["slack"] = [
                "search_slack_messages",
                "send_slack_message",
                "send_slack_dm",
                "list_slack_channels",
                "list_slack_users",
                "get_slack_user_info",
                "create_slack_thread",
                "upload_slack_file",
            ]

        return tools

    def get_setup_instructions(self) -> Dict[str, str]:
        """Get setup instructions for unconfigured integrations."""
        instructions = {}

        if not self.is_google_drive_configured():
            instructions[
                "google_drive"
            ] = """
Google Drive Setup Instructions:
1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Drive API and Google Sheets API
4. Create a Service Account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Fill in details and create
5. Generate JSON key:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key" > "JSON"
   - Download the JSON file
6. Set environment variable:
   export GOOGLE_SERVICE_ACCOUNT_FILE="/path/to/service-account.json"
7. (Optional) For domain-wide delegation:
   export GOOGLE_DELEGATED_USER="user@yourdomain.com"
"""

        if not self.is_slack_configured():
            instructions[
                "slack"
            ] = """
Slack Setup Instructions:
1. Go to https://api.slack.com/apps
2. Click "Create New App" > "From scratch"
3. Give it a name and select your workspace
4. Go to "OAuth & Permissions":
   - Add bot token scopes: channels:read, chat:write, files:write, users:read, etc.
   - Install app to workspace
   - Copy "Bot User OAuth Token" (starts with xoxb-)
5. Set environment variable:
   export SLACK_BOT_TOKEN="xoxb-your-token-here"
6. (Optional) For user token scopes:
   export SLACK_USER_TOKEN="xoxp-your-user-token"
"""

        return instructions


# Global configuration instance
_integrations_config: Optional[IntegrationsConfig] = None


def get_integrations_config() -> IntegrationsConfig:
    """Get the global integrations configuration."""
    global _integrations_config
    if _integrations_config is None:
        _integrations_config = IntegrationsConfig.from_env()
    return _integrations_config


def set_integrations_config(config: IntegrationsConfig):
    """Set the global integrations configuration."""
    global _integrations_config
    _integrations_config = config


def reload_integrations_config():
    """Reload configuration from environment."""
    global _integrations_config
    _integrations_config = IntegrationsConfig.from_env()
