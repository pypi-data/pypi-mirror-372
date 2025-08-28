"""
Interrupt configuration functionality for Broadie agents.
Provides human-in-the-loop capabilities using LangGraph prebuilts.
"""

from typing import Any, Callable, Dict, List

from langgraph.prebuilt.interrupt import (
    ActionRequest,
    HumanInterrupt,
    HumanInterruptConfig,
    HumanResponse,
)
from langgraph.types import interrupt

from broadie.utils.exceptions import BroadieError

# Type alias for interrupt configurations
ToolInterruptConfig = Dict[str, HumanInterruptConfig]


def create_interrupt_hook(
    tool_configs: ToolInterruptConfig,
    message_prefix: str = "Tool execution requires approval",
) -> Callable:
    """
    Create a post model hook that handles interrupts using native LangGraph schemas.

    This allows for human-in-the-loop control where specific tool executions
    can be paused for human approval or modification before proceeding.

    Args:
        tool_configs: Dict mapping tool names to HumanInterruptConfig objects
        message_prefix: Optional message prefix for interrupt descriptions

    Returns:
        Callable hook function for use with LangGraph agents
    """

    def interrupt_hook(state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Post model hook that checks for tool calls and triggers interrupts if needed.

        Args:
            state: Current agent state

        Returns:
            Updated state with approved tool calls
        """
        messages = state.get("messages", [])
        if not messages:
            return

        last_message = messages[-1]

        # Check if the last message has tool calls
        if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
            return

        # Separate tool calls that need interrupts from those that don't
        interrupt_tool_calls = []
        auto_approved_tool_calls = []

        for tool_call in last_message.tool_calls:
            tool_name = tool_call["name"]
            if tool_name in tool_configs:
                interrupt_tool_calls.append(tool_call)
            else:
                auto_approved_tool_calls.append(tool_call)

        # If no interrupts needed, return early
        if not interrupt_tool_calls:
            return

        approved_tool_calls = auto_approved_tool_calls.copy()

        # Process all tool calls that need interrupts in parallel
        requests = []

        for tool_call in interrupt_tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            description = f"{message_prefix}\n\nTool: {tool_name}\nArgs: {tool_args}"
            tool_config = tool_configs[tool_name]

            request: HumanInterrupt = {
                "action_request": ActionRequest(
                    action=tool_name,
                    args=tool_args,
                ),
                "config": tool_config,
                "description": description,
            }
            requests.append(request)

        # Send interrupts and wait for responses
        try:
            responses: List[HumanResponse] = interrupt(requests)
        except Exception as e:
            raise BroadieError(f"Error processing interrupts: {e}")

        # Process responses
        for i, response in enumerate(responses):
            tool_call = interrupt_tool_calls[i]

            if response["type"] == "accept":
                # User approved the tool call as-is
                approved_tool_calls.append(tool_call)
            elif response["type"] == "edit":
                # User modified the tool call
                edited: ActionRequest = response["args"]
                new_tool_call = {
                    "name": tool_call["name"],
                    "args": edited["args"],
                    "id": tool_call["id"],
                }
                approved_tool_calls.append(new_tool_call)
            elif response["type"] == "reject":
                # User rejected the tool call - skip it
                continue
            else:
                raise ValueError(f"Unknown response type: {response['type']}")

        # Update the message with approved tool calls
        last_message.tool_calls = approved_tool_calls

        return {"messages": [last_message]}

    return interrupt_hook


class InterruptManager:
    """
    Manager for handling different types of interrupts in Broadie agents.

    Provides utilities for creating and managing interrupt configurations
    for different tools and scenarios.
    """

    def __init__(self):
        self.configs: ToolInterruptConfig = {}

    def add_tool_interrupt(self, tool_name: str, config: HumanInterruptConfig):
        """Add an interrupt configuration for a specific tool."""
        self.configs[tool_name] = config

    def remove_tool_interrupt(self, tool_name: str):
        """Remove interrupt configuration for a tool."""
        if tool_name in self.configs:
            del self.configs[tool_name]

    def create_hook(
        self, message_prefix: str = "Tool execution requires approval"
    ) -> Callable:
        """Create an interrupt hook with the current configurations."""
        return create_interrupt_hook(self.configs, message_prefix)

    def has_interrupt(self, tool_name: str) -> bool:
        """Check if a tool has an interrupt configuration."""
        return tool_name in self.configs

    def get_interrupt_tools(self) -> List[str]:
        """Get list of tools that have interrupt configurations."""
        return list(self.configs.keys())

    def clear_interrupts(self):
        """Clear all interrupt configurations."""
        self.configs.clear()


def create_approval_interrupt_config(
    message: str = "Do you want to execute this tool?", timeout: int = 300
) -> HumanInterruptConfig:
    """
    Create a simple approval interrupt configuration.

    Args:
        message: Message to display to the human
        timeout: Timeout in seconds for response

    Returns:
        HumanInterruptConfig for simple approval
    """
    return {
        "message": message,
        "timeout": timeout,
        "allow_edit": False,
        "allow_reject": True,
    }


def create_edit_interrupt_config(
    message: str = "Review and optionally edit this tool call:", timeout: int = 600
) -> HumanInterruptConfig:
    """
    Create an edit interrupt configuration.

    Args:
        message: Message to display to the human
        timeout: Timeout in seconds for response

    Returns:
        HumanInterruptConfig that allows editing
    """
    return {
        "message": message,
        "timeout": timeout,
        "allow_edit": True,
        "allow_reject": True,
    }


def create_sensitive_tool_interrupt(
    tool_name: str, sensitivity_level: str = "high"
) -> HumanInterruptConfig:
    """
    Create interrupt configuration for sensitive tools.

    Args:
        tool_name: Name of the sensitive tool
        sensitivity_level: Level of sensitivity (low, medium, high, critical)

    Returns:
        HumanInterruptConfig appropriate for sensitivity level
    """

    timeout_map = {
        "low": 180,  # 3 minutes
        "medium": 300,  # 5 minutes
        "high": 600,  # 10 minutes
        "critical": 1800,  # 30 minutes
    }

    message_map = {
        "low": f"Confirm execution of {tool_name}",
        "medium": f"Review and approve execution of {tool_name}",
        "high": f"ATTENTION: High-sensitivity tool {tool_name} requires approval",
        "critical": f"CRITICAL: {tool_name} requires immediate review and approval",
    }

    timeout = timeout_map.get(sensitivity_level, 300)
    message = message_map.get(sensitivity_level, f"Approve execution of {tool_name}")

    return {
        "message": message,
        "timeout": timeout,
        "allow_edit": sensitivity_level in ["high", "critical"],
        "allow_reject": True,
    }


# Predefined interrupt configurations for common scenarios
COMMON_INTERRUPT_CONFIGS = {
    "file_operations": create_sensitive_tool_interrupt("file operations", "medium"),
    "external_api": create_sensitive_tool_interrupt("external API calls", "high"),
    "system_commands": create_sensitive_tool_interrupt("system commands", "critical"),
    "data_deletion": create_sensitive_tool_interrupt("data deletion", "critical"),
    "network_requests": create_sensitive_tool_interrupt("network requests", "medium"),
}
