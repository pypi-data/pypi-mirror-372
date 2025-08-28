"""
Tool configuration and availability checker for Broadie integrations.

This module provides utilities to check tool availability, show setup instructions,
and manage tool configurations dynamically.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from broadie.config.integrations import get_integrations_config
from broadie.tools import get_global_registry


def check_tool_availability() -> Dict[str, Dict[str, Any]]:
    """
    Check which integration tools are available and properly configured.

    Returns:
        Dictionary with tool categories and their configuration status
    """
    config = get_integrations_config()
    registry = get_global_registry()

    availability = {
        "google_drive": {
            "configured": config.is_google_drive_configured(),
            "tools": [],
            "missing_config": [],
        },
        "slack": {
            "configured": config.is_slack_configured(),
            "tools": [],
            "missing_config": [],
        },
    }

    # Check Google Drive configuration
    if not config.is_google_drive_configured():
        missing = []
        if not config.google_drive.service_account_file:
            missing.append("GOOGLE_SERVICE_ACCOUNT_FILE environment variable")
        elif not Path(config.google_drive.service_account_file).exists():
            missing.append("Service account JSON file not found")
        availability["google_drive"]["missing_config"] = missing
    else:
        availability["google_drive"]["tools"] = registry.list_tools("google_drive")

    # Check Slack configuration
    if not config.is_slack_configured():
        missing = []
        if not config.slack.bot_token:
            missing.append("SLACK_BOT_TOKEN environment variable")
        availability["slack"]["missing_config"] = missing
    else:
        availability["slack"]["tools"] = registry.list_tools("slack")

    return availability


def show_setup_instructions(category: Optional[str] = None):
    """
    Display setup instructions for integration tools.

    Args:
        category: Specific integration category (google_drive, slack) or None for all
    """
    config = get_integrations_config()
    instructions = config.get_setup_instructions()

    if category:
        if category in instructions:
            print(f"\n{instructions[category]}")
        else:
            print(f"No setup needed for {category} - already configured!")
    else:
        if instructions:
            print("\n=== INTEGRATION SETUP INSTRUCTIONS ===")
            for cat, instruction in instructions.items():
                print(f"\n{instruction}")
        else:
            print("All integrations are properly configured!")


def list_available_tools() -> Dict[str, List[str]]:
    """
    List all available integration tools by category.

    Returns:
        Dictionary mapping categories to lists of available tool names
    """
    registry = get_global_registry()

    categories = ["google_drive", "slack"]
    available_tools = {}

    for category in categories:
        tools = registry.list_tools(category)
        if tools:
            available_tools[category] = tools

    return available_tools


def get_tool_configuration_status() -> str:
    """
    Get a human-readable status of tool configurations.

    Returns:
        Status string with configuration information
    """
    availability = check_tool_availability()
    status_lines = []

    status_lines.append("=== INTEGRATION TOOL STATUS ===")

    for category, info in availability.items():
        category_name = category.replace("_", " ").title()

        if info["configured"]:
            tool_count = len(info["tools"])
            status_lines.append(f"✅ {category_name}: {tool_count} tools available")
            if info["tools"]:
                status_lines.append(f"   Tools: {', '.join(info['tools'])}")
        else:
            status_lines.append(f"❌ {category_name}: Not configured")
            if info["missing_config"]:
                status_lines.append(f"   Missing: {', '.join(info['missing_config'])}")

    # Add usage instructions
    status_lines.append("\nTo enable tools, run:")
    status_lines.append(
        '  python -c "from broadie.core.tool_configurator import show_setup_instructions; show_setup_instructions()"'
    )

    return "\n".join(status_lines)


def create_sample_config_file(output_path: Path) -> bool:
    """
    Create a sample configuration file for integrations.

    Args:
        output_path: Path where to create the sample config file

    Returns:
        True if file was created successfully
    """
    import json

    sample_config = {
        "google_drive": {
            "service_account_file": "/path/to/service-account.json",
            "delegated_user": "user@yourdomain.com",
            "scopes": [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/spreadsheets",
            ],
        },
        "slack": {
            "bot_token": "xoxb-your-bot-token-here",
            "user_token": "xoxp-your-user-token-here",
            "signing_secret": "your-signing-secret",
        },
    }

    try:
        with open(output_path, "w") as f:
            json.dump(sample_config, f, indent=2)
        return True
    except Exception as e:
        print(f"Error creating sample config: {e}")
        return False


# CLI utility functions
def main():
    """Main CLI utility for checking tool configuration."""
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "status":
            print(get_tool_configuration_status())
        elif command == "setup":
            category = sys.argv[2] if len(sys.argv) > 2 else None
            show_setup_instructions(category)
        elif command == "list":
            tools = list_available_tools()
            if tools:
                print("=== AVAILABLE TOOLS ===")
                for category, tool_list in tools.items():
                    print(f"{category.replace('_', ' ').title()}:")
                    for tool in tool_list:
                        print(f"  - {tool}")
            else:
                print("No integration tools are currently available.")
                print(
                    "Run 'python -m broadie.core.tool_configurator setup' for instructions."
                )
        elif command == "create-config":
            output_path = (
                Path(sys.argv[2]) if len(sys.argv) > 2 else Path("integrations.json")
            )
            if create_sample_config_file(output_path):
                print(f"Sample configuration created at: {output_path}")
            else:
                print("Failed to create sample configuration file")
        else:
            print(
                "Usage: python -m broadie.core.tool_configurator [status|setup|list|create-config]"
            )
    else:
        print(get_tool_configuration_status())


if __name__ == "__main__":
    main()
