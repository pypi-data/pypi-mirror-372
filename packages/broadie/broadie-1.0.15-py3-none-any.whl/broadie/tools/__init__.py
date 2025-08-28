"""
Tool system for Broadie agents.

This module provides a consolidated tool system with clean separation:
- builtin: Core file system and agent management tools
- slack: Slack integration tools
- google: Google Drive/Sheets integration tools
- notifications: Multi-destination notification tools
- registry: Tool registration and management
"""

from .registry import (
    FunctionTool,
    PersistenceContext,
    Tool,
    ToolMetadata,
    ToolRegistry,
    get_global_registry,
    register_builtin_tools,
    register_integration_tools,
    register_notification_tools,
    set_global_registry,
    tool,
)

# Import the factory functions for backend-dependent tools
from .builtin.conversation_tools import create_conversation_tools
from .builtin.memory_tools import create_memory_tools
from .builtin.todo_tools import create_todo_tools

__all__ = [
    "Tool",
    "FunctionTool",
    "ToolRegistry",
    "ToolMetadata",
    "PersistenceContext",
    "tool",
    "get_global_registry",
    "set_global_registry",
    "register_builtin_tools",
    "register_integration_tools",
    "register_notification_tools",
    # Backend-dependent tool creators
    "create_conversation_tools",
    "create_memory_tools",
    "create_todo_tools",
]
