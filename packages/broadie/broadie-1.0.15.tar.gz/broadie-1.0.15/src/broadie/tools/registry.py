"""
Tool registry and base classes for Broadie agents.
Provides tool registration, management, and execution capabilities.
Integrates with existing LangChain tools and state management.
"""

import asyncio
import inspect
import uuid
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from contextvars import ContextVar
from functools import wraps
from typing import Annotated, Any, Callable, Dict, List, Optional, Union

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId
from langchain_core.tools import tool as langchain_tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import BaseModel, Field

from broadie.core.state import BroadieState, Todo
from broadie.utils.exceptions import ConfigurationError, ToolError


class ToolMetadata(BaseModel):
    """Metadata for a tool."""

    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    return_type: Optional[str] = None
    async_capable: bool = False


# Context variables for managing conversation and message IDs
_conversation_id_context: ContextVar[Optional[str]] = ContextVar(
    "conversation_id", default=None
)
_message_id_context: ContextVar[Optional[int]] = ContextVar("message_id", default=None)
_agent_id_context: ContextVar[Optional[str]] = ContextVar("agent_id", default=None)


class PersistenceContext:
    """Context manager for managing conversation, message, and agent IDs across tool calls."""

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        message_id: Optional[int] = None,
        agent_id: Optional[str] = None,
        backend=None,
    ):
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.message_id = message_id
        self.agent_id = agent_id
        self.backend = backend

        # Store tokens for context cleanup
        self._tokens = []

    def __enter__(self):
        """Enter the context and set context variables."""
        self._tokens.append(_conversation_id_context.set(self.conversation_id))
        self._tokens.append(_message_id_context.set(self.message_id))
        self._tokens.append(_agent_id_context.set(self.agent_id))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context and clean up context variables."""
        # Reset context variables in reverse order
        for token in reversed(self._tokens):
            if token:
                try:
                    token.reset()
                except ValueError:
                    pass  # Token already reset
        self._tokens.clear()

    @asynccontextmanager
    async def async_context(self):
        """Async context manager version."""
        try:
            self.__enter__()
            yield self
        finally:
            self.__exit__(None, None, None)

    async def ensure_conversation_exists(self):
        """Ensure conversation exists in backend, creating it if necessary."""
        if self.backend and self.conversation_id and self.agent_id:
            try:
                conversation = await self.backend.get_conversation(self.conversation_id)
                if not conversation:
                    await self.backend.create_conversation(
                        conversation_id=self.conversation_id,
                        agent_id=self.agent_id,
                        title="New Conversation",
                    )
            except Exception as e:
                # Log but don't fail - conversation creation is optional
                pass

    @classmethod
    def get_current_conversation_id(cls) -> Optional[str]:
        """Get the current conversation ID from context."""
        return _conversation_id_context.get()

    @classmethod
    def get_current_message_id(cls) -> Optional[int]:
        """Get the current message ID from context."""
        return _message_id_context.get()

    @classmethod
    def get_current_agent_id(cls) -> Optional[str]:
        """Get the current agent ID from context."""
        return _agent_id_context.get()

    @classmethod
    def get_current_context(cls) -> Dict[str, Optional[Union[str, int]]]:
        """Get all current context values."""
        return {
            "conversation_id": cls.get_current_conversation_id(),
            "message_id": cls.get_current_message_id(),
            "agent_id": cls.get_current_agent_id(),
        }


class Tool(ABC):
    """
    Abstract base class for Broadie tools.

    Tools are functions that agents can call to perform specific tasks.
    They follow SOLID principles with clear interfaces and responsibilities.
    """

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self._metadata: Optional[ToolMetadata] = None

    @property
    def metadata(self) -> ToolMetadata:
        """Get tool metadata."""
        if self._metadata is None:
            self._metadata = self._generate_metadata()
        return self._metadata

    @abstractmethod
    async def execute(self, *args, **kwargs) -> Any:
        """Execute the tool with given arguments."""
        pass

    @abstractmethod
    def _generate_metadata(self) -> ToolMetadata:
        """Generate metadata for this tool."""
        pass

    def to_langchain_tool(self) -> BaseTool:
        """Convert this tool to a LangChain BaseTool."""

        # Create a wrapper function for LangChain
        if asyncio.iscoroutinefunction(self.execute):

            async def wrapper(*args, **kwargs):
                return await self.execute(*args, **kwargs)

        else:

            def wrapper(*args, **kwargs):
                return self.execute(*args, **kwargs)

        # Use LangChain's tool decorator
        return langchain_tool(description=self.description)(wrapper)

    def __str__(self) -> str:
        return f"Tool(name='{self.name}', description='{self.description}')"

    def __repr__(self) -> str:
        return self.__str__()


class FunctionTool(Tool):
    """
    A tool that wraps a Python function.

    This allows easy integration of existing functions as agent tools.
    """

    def __init__(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.func = func

        # Auto-derive name and description if not provided
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Execute {func.__name__}"

        super().__init__(tool_name, tool_description)

        # Check if function is async
        self.is_async = asyncio.iscoroutinefunction(func)

    async def execute(self, *args, **kwargs) -> Any:
        """Execute the wrapped function."""
        try:
            if self.is_async:
                return await self.func(*args, **kwargs)
            else:
                return self.func(*args, **kwargs)
        except Exception as e:
            raise ToolError(f"Error executing tool '{self.name}': {str(e)}") from e

    def to_langchain_tool(self) -> BaseTool:
        """Expose the original function to LangChain to preserve its signature.

        Important: wrapping with a generic *args/**kwargs function leads to
        invalid tool schemas for some providers (e.g., Gemini), because the
        generated parameter 'args' lacks a valid JSON schema for items.
        """
        return langchain_tool(description=self.description)(self.func)

    def _generate_metadata(self) -> ToolMetadata:
        """Generate metadata from function signature."""
        sig = inspect.signature(self.func)

        parameters = {}
        for param_name, param in sig.parameters.items():
            param_info = {
                "type": (
                    str(param.annotation)
                    if param.annotation != inspect.Parameter.empty
                    else "Any"
                ),
                "required": param.default == inspect.Parameter.empty,
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default

            parameters[param_name] = param_info

        return_type = (
            str(sig.return_annotation)
            if sig.return_annotation != inspect.Parameter.empty
            else None
        )

        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=parameters,
            return_type=return_type,
            async_capable=self.is_async,
        )


class ToolRegistry:
    """
    Registry for managing tools across the application.

    Follows the Registry pattern to provide centralized tool management.
    """

    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, List[str]] = {}

    def register_tool(self, tool: Tool, category: Optional[str] = None):
        """Register a tool in the registry."""
        if tool.name in self._tools:
            raise ConfigurationError(f"Tool '{tool.name}' is already registered")

        self._tools[tool.name] = tool

        if category:
            if category not in self._categories:
                self._categories[category] = []
            self._categories[category].append(tool.name)

    def register_function(
        self,
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> FunctionTool:
        """Register a function as a tool."""
        tool = FunctionTool(func, name, description)
        self.register_tool(tool, category)
        return tool

    def unregister_tool(self, name: str):
        """Unregister a tool from the registry."""
        if name not in self._tools:
            raise ConfigurationError(f"Tool '{name}' is not registered")

        # Remove from tools
        del self._tools[name]

        # Remove from categories
        for category, tool_names in self._categories.items():
            if name in tool_names:
                tool_names.remove(name)

    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """List all registered tool names, optionally filtered by category."""
        if category is None:
            return list(self._tools.keys())
        else:
            return self._categories.get(category, [])

    def list_categories(self) -> List[str]:
        """List all categories."""
        return list(self._categories.keys())

    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a specific category."""
        tool_names = self._categories.get(category, [])
        return [self._tools[name] for name in tool_names]

    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all registered tools."""
        return self._tools.copy()

    def get_tools_for_agent(self, tool_names: List[str]) -> List[Tool]:
        """Get a list of tools for an agent."""
        tools = []
        for name in tool_names:
            tool = self.get_tool(name)
            if tool is None:
                raise ConfigurationError(f"Tool '{name}' not found in registry")
            tools.append(tool)
        return tools

    def to_langchain_tools(
        self, tool_names: Optional[List[str]] = None
    ) -> List[BaseTool]:
        """Convert tools to LangChain BaseTool format."""
        if tool_names is None:
            tools_to_convert = list(self._tools.values())
        else:
            tools_to_convert = self.get_tools_for_agent(tool_names)

        return [tool.to_langchain_tool() for tool in tools_to_convert]

    def clear(self):
        """Clear all registered tools."""
        self._tools.clear()
        self._categories.clear()

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def __iter__(self):
        return iter(self._tools.values())


# Simple @tool decorator that auto-registers
def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
):
    """
    Simple decorator to mark a function as a tool.
    Auto-registers with global registry for agent discovery.

    Usage:
        @tool
        def my_function(x: int) -> str:
            return f"Result: {x}"

        @tool(name="custom_name", description="Custom description")
        def another_function():
            return "done"
    """

    def decorator(f: Callable) -> Callable:
        # Auto-register with global registry
        registry = get_global_registry()
        registry.register_function(f, name, description)

        # Mark function as a tool for agent discovery
        f._is_broadie_tool = True
        f._tool_name = name or f.__name__
        f._tool_description = description or f.__doc__ or f"Execute {f.__name__}"

        return f

    if func is None:
        # Called with arguments: @tool(name="...", description="...")
        return decorator
    else:
        # Called without arguments: @tool
        return decorator(func)


# Global tool registry instance
_global_registry = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _global_registry


def set_global_registry(registry: ToolRegistry):
    """Set the global tool registry."""
    global _global_registry
    _global_registry = registry


def register_builtin_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """Register all built-in tools with the registry."""
    if registry is None:
        registry = get_global_registry()

    from .builtin import edit_file, ls_files, read_file, write_file, write_todos

    # Register built-in LangChain tools
    registry.register_tool(FunctionTool(write_todos, "write_todos"), "builtin")
    registry.register_tool(FunctionTool(ls_files, "ls"), "builtin")
    registry.register_tool(FunctionTool(read_file, "read_file"), "builtin")
    registry.register_tool(FunctionTool(write_file, "write_file"), "builtin")
    registry.register_tool(FunctionTool(edit_file, "edit_file"), "builtin")

    return registry


def register_integration_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """Register all integration tools with the registry."""
    if registry is None:
        registry = get_global_registry()

    # Import integration tools
    try:
        from .google import (
            create_google_sheet,
            list_drive_folders,
            read_google_drive_file,
            search_google_drive,
            update_google_sheet,
            write_google_drive_file,
        )
        from .slack import (
            create_slack_thread,
            get_slack_user_info,
            list_slack_channels,
            list_slack_users,
            search_slack_messages,
            send_slack_dm,
            send_slack_message,
            upload_slack_file,
        )

        # Register Slack tools
        registry.register_tool(
            FunctionTool(search_slack_messages, "search_slack_messages"), "slack"
        )
        registry.register_tool(
            FunctionTool(send_slack_message, "send_slack_message"), "slack"
        )
        registry.register_tool(FunctionTool(send_slack_dm, "send_slack_dm"), "slack")
        registry.register_tool(
            FunctionTool(list_slack_channels, "list_slack_channels"), "slack"
        )
        registry.register_tool(
            FunctionTool(list_slack_users, "list_slack_users"), "slack"
        )
        registry.register_tool(
            FunctionTool(get_slack_user_info, "get_slack_user_info"), "slack"
        )
        registry.register_tool(
            FunctionTool(create_slack_thread, "create_slack_thread"), "slack"
        )
        registry.register_tool(
            FunctionTool(upload_slack_file, "upload_slack_file"), "slack"
        )

        # Register Google Drive tools
        registry.register_tool(
            FunctionTool(search_google_drive, "search_google_drive"), "google"
        )
        registry.register_tool(
            FunctionTool(read_google_drive_file, "read_google_drive_file"), "google"
        )
        registry.register_tool(
            FunctionTool(write_google_drive_file, "write_google_drive_file"), "google"
        )
        registry.register_tool(
            FunctionTool(create_google_sheet, "create_google_sheet"), "google"
        )
        registry.register_tool(
            FunctionTool(update_google_sheet, "update_google_sheet"), "google"
        )
        registry.register_tool(
            FunctionTool(list_drive_folders, "list_drive_folders"), "google"
        )

    except ImportError as e:
        # Integration tools are optional - only register if dependencies are available
        print(f"Warning: Integration tools not available: {e}")

    return registry


def register_notification_tools(
    registry: Optional[ToolRegistry] = None,
) -> ToolRegistry:
    """Register notification tools with the registry."""
    if registry is None:
        registry = get_global_registry()

    try:
        from .notifications import (
            broadcast_message,
            escalate_issue,
            get_destination_info,
            list_enabled_destinations,
            post_analysis_results,
            send_alert,
            send_notification,
            send_status_update,
            send_to_destination,
            test_notification_destinations,
        )

        # Register notification tools
        registry.register_tool(
            FunctionTool(send_notification, "send_notification"), "notifications"
        )
        registry.register_tool(FunctionTool(send_alert, "send_alert"), "notifications")
        registry.register_tool(
            FunctionTool(escalate_issue, "escalate_issue"), "notifications"
        )
        registry.register_tool(
            FunctionTool(broadcast_message, "broadcast_message"), "notifications"
        )
        registry.register_tool(
            FunctionTool(send_status_update, "send_status_update"), "notifications"
        )
        registry.register_tool(
            FunctionTool(
                test_notification_destinations, "test_notification_destinations"
            ),
            "notifications",
        )
        registry.register_tool(
            FunctionTool(get_destination_info, "get_destination_info"), "notifications"
        )
        registry.register_tool(
            FunctionTool(send_to_destination, "send_to_destination"), "notifications"
        )
        registry.register_tool(
            FunctionTool(post_analysis_results, "post_analysis_results"),
            "notifications",
        )
        registry.register_tool(
            FunctionTool(list_enabled_destinations, "list_enabled_destinations"),
            "notifications",
        )

    except ImportError as e:
        print(f"Warning: Notification tools not available: {e}")

    return registry


# Auto-register all tools when the module is imported
register_builtin_tools()
register_integration_tools()
register_notification_tools()
