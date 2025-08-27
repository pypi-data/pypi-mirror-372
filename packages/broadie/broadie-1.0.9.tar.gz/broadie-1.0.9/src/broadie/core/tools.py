"""
Tool system for Broadie agents.
Provides tool registration, management, and execution capabilities.
Integrates with existing LangChain tools and state management.
"""

from typing import Any, Callable, Dict, List, Optional, Union, Annotated
from abc import ABC, abstractmethod
from functools import wraps
import inspect
import asyncio
import uuid
from contextvars import ContextVar
from contextlib import asynccontextmanager

from langchain_core.tools import BaseTool, tool as langchain_tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import InjectedState
from langgraph.types import Command
from pydantic import BaseModel, Field

from broadie.utils.exceptions import ToolError, ConfigurationError
from broadie.core.state import BroadieState, Todo


class ToolMetadata(BaseModel):
    """Metadata for a tool."""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    return_type: Optional[str] = None
    async_capable: bool = False


# Context variables for managing conversation and message IDs
_conversation_id_context: ContextVar[Optional[str]] = ContextVar('conversation_id', default=None)
_message_id_context: ContextVar[Optional[int]] = ContextVar('message_id', default=None)
_agent_id_context: ContextVar[Optional[str]] = ContextVar('agent_id', default=None)


class PersistenceContext:
    """Context manager for managing conversation, message, and agent IDs across tool calls."""
    
    def __init__(
        self, 
        conversation_id: Optional[str] = None,
        message_id: Optional[int] = None,
        agent_id: Optional[str] = None,
        backend = None
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
                        title="New Conversation"
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
            "agent_id": cls.get_current_agent_id()
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
        description: Optional[str] = None
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
                "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any",
                "required": param.default == inspect.Parameter.empty,
            }
            if param.default != inspect.Parameter.empty:
                param_info["default"] = param.default
                
            parameters[param_name] = param_info
        
        return_type = str(sig.return_annotation) if sig.return_annotation != inspect.Parameter.empty else None
        
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters=parameters,
            return_type=return_type,
            async_capable=self.is_async
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
        category: Optional[str] = None
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
    
    def to_langchain_tools(self, tool_names: Optional[List[str]] = None) -> List[BaseTool]:
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
def tool(func: Optional[Callable] = None, *, name: Optional[str] = None, description: Optional[str] = None):
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


# Built-in tools from existing codebase

WRITE_TODOS_DESCRIPTION = """Create and manage a structured task list for your current work session. This helps you track progress, organize complex tasks, and demonstrate thoroughness to the user. Updates the agent's internal todo state."""

READ_FILE_DESCRIPTION = """Read file content from the mock filesystem. Results are returned using cat -n format, with line numbers starting at 1. Use this to examine file contents before making changes."""

EDIT_FILE_DESCRIPTION = """Perform exact string replacements in files. The edit will FAIL if `old_string` is not unique in the file. Use replace_all=True to replace all instances, or provide a more specific string for single replacements."""

WRITE_FILE_DESCRIPTION = """Write content to a file in the mock filesystem. This will overwrite the entire file with the new content. Use edit_file for partial changes."""

LS_FILES_DESCRIPTION = """List all files available in the mock filesystem. Use this to discover what files exist before reading or editing them."""

ADD_TODO_DESCRIPTION = """Add a new todo item to track tasks and persist across sessions. If conversation_id is not provided, uses the current conversation context. Todos help organize work and track progress."""

LIST_TODOS_DESCRIPTION = """List todos with optional filters by conversation, status, or message. Shows todos with status icons (✅ done, ⏳ in_progress, 📌 pending) for easy visual scanning."""

STORE_MEMORY_DESCRIPTION = """Store a memory for an agent that persists across sessions. Memories help agents remember important information, context, and learned patterns."""

RECALL_MEMORIES_DESCRIPTION = """Recall stored memories for an agent. Returns recent memories that can help provide context and continuity across conversations."""

GENERATE_TITLE_DESCRIPTION = """Generate an appropriate title for a conversation based on its content. Automatically analyzes conversation messages and creates a descriptive title for better organization. Called automatically for new conversations."""

CREATE_CONVERSATION_DESCRIPTION = """Create a new conversation thread with a specific title and agent. Use this to start new conversation contexts that can be referenced later."""

LIST_CONVERSATIONS_DESCRIPTION = """List recent conversations with optional agent filter. Shows conversation titles, IDs, and message counts for easy navigation and context switching."""


@langchain_tool(description=WRITE_TODOS_DESCRIPTION)
def write_todos(
    todos: List[Todo], 
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Write/update todo list in agent state."""
    return Command(
        update={
            "todos": todos,
            "messages": [
                ToolMessage(f"Updated todo list to {len(todos)} items", tool_call_id=tool_call_id)
            ],
        }
    )


@langchain_tool(description=LS_FILES_DESCRIPTION)
def ls_files(state: Annotated[BroadieState, InjectedState]) -> List[str]:
    """List all files in the mock filesystem."""
    return list(state.get("files", {}).keys())


@langchain_tool(description=READ_FILE_DESCRIPTION)
def read_file(
    file_path: str,
    state: Annotated[BroadieState, InjectedState],
    offset: int = 0,
    limit: int = 2000,
) -> str:
    """Read file content from mock filesystem."""
    mock_filesystem = state.get("files", {})
    if file_path not in mock_filesystem:
        return f"Error: File '{file_path}' not found"

    content = mock_filesystem[file_path]

    if not content or content.strip() == "":
        return "System reminder: File exists but has empty contents"

    lines = content.splitlines()
    start_idx = offset
    end_idx = min(start_idx + limit, len(lines))

    if start_idx >= len(lines):
        return f"Error: Line offset {offset} exceeds file length ({len(lines)} lines)"

    result_lines = []
    for i in range(start_idx, end_idx):
        line_content = lines[i]
        if len(line_content) > 2000:
            line_content = line_content[:2000]
        
        line_number = i + 1
        result_lines.append(f"{line_number:6d}\t{line_content}")

    return "\n".join(result_lines)


@langchain_tool(description=WRITE_FILE_DESCRIPTION)
def write_file(
    file_path: str,
    content: str,
    state: Annotated[BroadieState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
) -> Command:
    """Write content to a file in the mock filesystem."""
    files = state.get("files", {})
    files[file_path] = content
    return Command(
        update={
            "files": files,
            "messages": [
                ToolMessage(f"Updated file {file_path}", tool_call_id=tool_call_id)
            ],
        }
    )


@langchain_tool(description=EDIT_FILE_DESCRIPTION)
def edit_file(
    file_path: str,
    old_string: str,
    new_string: str,
    state: Annotated[BroadieState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
    replace_all: bool = False,
) -> Command:
    """Edit file by replacing old_string with new_string."""
    mock_filesystem = state.get("files", {})
    
    if file_path not in mock_filesystem:
        return Command(
            update={
                "messages": [
                    ToolMessage(f"Error: File '{file_path}' not found", tool_call_id=tool_call_id)
                ]
            }
        )

    content = mock_filesystem[file_path]

    if old_string not in content:
        return Command(
            update={
                "messages": [
                    ToolMessage(f"Error: String not found in file: '{old_string}'", tool_call_id=tool_call_id)
                ]
            }
        )

    if not replace_all:
        occurrences = content.count(old_string)
        if occurrences > 1:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"Error: String '{old_string}' appears {occurrences} times in file. "
                            "Use replace_all=True to replace all instances, or provide a more specific string.",
                            tool_call_id=tool_call_id
                        )
                    ]
                }
            )

    if replace_all:
        new_content = content.replace(old_string, new_string)
        replacement_count = content.count(old_string)
        result_msg = f"Successfully replaced {replacement_count} instance(s) of the string in '{file_path}'"
    else:
        new_content = content.replace(old_string, new_string, 1)
        result_msg = f"Successfully replaced string in '{file_path}'"

    mock_filesystem[file_path] = new_content
    return Command(
        update={
            "files": mock_filesystem,
            "messages": [ToolMessage(result_msg, tool_call_id=tool_call_id)],
        }
    )


# Todo Manager Tool for persistence
class TodoManagerTool(Tool):
    """Tool for managing todos with persistence backend."""
    
    def __init__(self, backend=None):
        super().__init__("todo_manager", "Create and manage todos that persist across sessions")
        self.backend = backend
    
    async def execute(self, action: str, **kwargs) -> Any:
        """Execute todo management actions."""
        if not self.backend:
            raise ToolError("No persistence backend available for todo management")
        
        try:
            if action == "add_todo":
                conversation_id = kwargs.get("conversation_id")
                description = kwargs.get("description")
                message_id = kwargs.get("message_id")
                assigned_to = kwargs.get("assigned_to")
                source_tool = kwargs.get("source_tool", "todo_manager")
                
                if not conversation_id or not description:
                    raise ToolError("conversation_id and description are required for add_todo")
                
                todo_id = await self.backend.create_todo(
                    conversation_id=conversation_id,
                    description=description,
                    message_id=message_id,
                    assigned_to=assigned_to,
                    source_tool=source_tool
                )
                return f"Created todo with ID: {todo_id}"
            
            elif action == "list_todos":
                conversation_id = kwargs.get("conversation_id")
                status = kwargs.get("status")
                message_id = kwargs.get("message_id")
                
                todos = await self.backend.get_todos(
                    conversation_id=conversation_id,
                    status=status,
                    message_id=message_id
                )
                return todos
            
            elif action == "mark_done":
                todo_id = kwargs.get("todo_id")
                if not todo_id:
                    raise ToolError("todo_id is required for mark_done")
                
                success = await self.backend.update_todo_status(todo_id, "done")
                return f"Todo {todo_id} marked as done" if success else f"Todo {todo_id} not found"
            
            elif action == "update_status":
                todo_id = kwargs.get("todo_id")
                status = kwargs.get("status")
                assigned_to = kwargs.get("assigned_to")
                
                if not todo_id or not status:
                    raise ToolError("todo_id and status are required for update_status")
                
                success = await self.backend.update_todo_status(todo_id, status, assigned_to)
                return f"Todo {todo_id} updated" if success else f"Todo {todo_id} not found"
            
            else:
                raise ToolError(f"Unknown action: {action}")
                
        except Exception as e:
            raise ToolError(f"Error in todo_manager: {str(e)}")
    
    def _generate_metadata(self) -> ToolMetadata:
        """Generate metadata for todo manager tool."""
        return ToolMetadata(
            name=self.name,
            description=self.description,
            parameters={
                "action": {
                    "type": "str",
                    "required": True,
                    "description": "Action to perform: add_todo, list_todos, mark_done, update_status"
                },
                "conversation_id": {"type": "str", "required": False},
                "description": {"type": "str", "required": False},
                "message_id": {"type": "int", "required": False},
                "todo_id": {"type": "str", "required": False},
                "status": {"type": "str", "required": False},
                "assigned_to": {"type": "str", "required": False},
                "source_tool": {"type": "str", "required": False}
            },
            return_type="Union[str, List[Dict]]",
            async_capable=True
        )


def create_todo_tools(backend):
    """Create todo management tools with backend dependency injection."""
    
    @langchain_tool(description=ADD_TODO_DESCRIPTION)
    async def add_todo(
        description: str,
        conversation_id: Optional[str] = None,
        message_id: Optional[int] = None,
        assigned_to: Optional[str] = None,
        source_tool: str = "agent"
    ) -> str:
        """Add a new todo item to track tasks. If conversation_id is not provided, uses current context."""
        # Use context if conversation_id not provided
        if not conversation_id:
            conversation_id = PersistenceContext.get_current_conversation_id()
            
        if not conversation_id:
            return "Error: No conversation context available. Please provide conversation_id."
        
        # Use context for message_id if not provided
        if not message_id:
            message_id = PersistenceContext.get_current_message_id()
        
        todo_id = await backend.create_todo(
            conversation_id=conversation_id,
            description=description,
            message_id=message_id,
            assigned_to=assigned_to,
            source_tool=source_tool
        )
        return f"Created todo: {description} (ID: {todo_id})"

    @langchain_tool(description=LIST_TODOS_DESCRIPTION) 
    async def list_todos(
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        message_id: Optional[int] = None
    ) -> str:
        """List todos with optional filters."""
        todos = await backend.get_todos(
            conversation_id=conversation_id,
            status=status,
            message_id=message_id
        )
        
        if not todos:
            return "No todos found."
        
        result = f"Found {len(todos)} todos:\n"
        for todo in todos:
            status_icon = "✅" if todo["status"] == "done" else "⏳" if todo["status"] == "in_progress" else "📌"
            result += f"{status_icon} {todo['description']} (Status: {todo['status']})\n"
        
        return result.strip()

    @langchain_tool(description="Mark a todo as completed by setting its status to 'done'. Provides confirmation of completion.")
    async def mark_todo_done(todo_id: str) -> str:
        """Mark a todo as completed."""
        success = await backend.update_todo_status(todo_id, "done")
        if success:
            return f"Marked todo {todo_id} as completed."
        else:
            return f"Todo {todo_id} not found."
    
    @langchain_tool(description="Update todo status (pending, in_progress, done) and optionally reassign to a different agent or person.")
    async def update_todo_status(
        todo_id: str, 
        status: str,
        assigned_to: Optional[str] = None
    ) -> str:
        """Update todo status (pending, in_progress, done) and optionally reassign."""
        if status not in ["pending", "in_progress", "done"]:
            return f"Invalid status: {status}. Must be one of: pending, in_progress, done"
        
        success = await backend.update_todo_status(todo_id, status, assigned_to)
        if success:
            assign_msg = f" and assigned to {assigned_to}" if assigned_to else ""
            return f"Updated todo {todo_id} to {status}{assign_msg}."
        else:
            return f"Todo {todo_id} not found."
    
    return [add_todo, list_todos, mark_todo_done, update_todo_status]


def create_memory_tools(backend):
    """Create memory management tools with backend dependency injection."""
    
    @langchain_tool(description=STORE_MEMORY_DESCRIPTION)
    async def store_memory(
        content: str,
        agent_id: str,
        memory_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a memory for an agent."""
        import uuid
        if not memory_id:
            memory_id = str(uuid.uuid4())
        
        success = await backend.store_memory(
            memory_id=memory_id,
            agent_id=agent_id,
            content=content,
            metadata=metadata
        )
        
        if success:
            return f"Stored memory: {content} (ID: {memory_id})"
        else:
            return f"Failed to store memory"
    
    @langchain_tool(description=RECALL_MEMORIES_DESCRIPTION)
    async def recall_memories(
        agent_id: str,
        limit: int = 10
    ) -> str:
        """Recall stored memories for an agent."""
        memories = await backend.get_memories(agent_id)
        
        if not memories:
            return "No memories found for this agent."
        
        # Limit results
        limited_memories = memories[-limit:] if len(memories) > limit else memories
        
        result = f"Found {len(limited_memories)} recent memories:\n"
        for i, memory in enumerate(limited_memories, 1):
            result += f"{i}. {memory['content']}\n"
        
        return result.strip()
    
    return [store_memory, recall_memories]


def create_conversation_tools(backend):
    """Create conversation management tools with backend dependency injection."""
    
    @langchain_tool(description=GENERATE_TITLE_DESCRIPTION)
    async def generate_conversation_title(
        conversation_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        recent_messages: Optional[str] = None
    ) -> str:
        """Generate an appropriate title for a conversation based on its content.
        
        This tool analyzes the conversation content and creates a descriptive title.
        It's automatically called for new conversations to provide meaningful organization.
        If conversation_id or agent_id are not provided, uses current context.
        """
        try:
            # Use context if parameters not provided
            if not conversation_id:
                conversation_id = PersistenceContext.get_current_conversation_id()
            if not agent_id:
                agent_id = PersistenceContext.get_current_agent_id()
            
            if not conversation_id:
                return "Error: No conversation context available. Please provide conversation_id."
            if not agent_id:
                return "Error: No agent context available. Please provide agent_id."
            
            # Check if conversation exists
            conversation = await backend.get_conversation(conversation_id)
            if not conversation:
                # Create new conversation if it doesn't exist
                await backend.create_conversation(
                    conversation_id=conversation_id,
                    agent_id=agent_id,
                    title="New Conversation"
                )
            
            # Get recent messages if not provided
            if not recent_messages:
                messages = await backend.get_messages(conversation_id)
                if messages:
                    # Take first few messages to generate title
                    recent_messages = "\n".join([
                        f"{msg['role']}: {msg['content'][:100]}" 
                        for msg in messages[:3]
                    ])
            
            if not recent_messages:
                return "Created new conversation with default title"
            
            # Generate title based on content (simple heuristic for now)
            # In a real implementation, this could use the LLM to generate titles
            title = _generate_title_from_content(recent_messages)
            
            # Update conversation title
            success = await backend.update_conversation_title(conversation_id, title)
            if success:
                return f"Generated title: '{title}' for conversation {conversation_id}"
            else:
                return f"Failed to update title for conversation {conversation_id}"
                
        except Exception as e:
            return f"Error generating title: {str(e)}"
    
    @langchain_tool(description=CREATE_CONVERSATION_DESCRIPTION)
    async def create_conversation(
        conversation_id: str,
        agent_id: str,
        title: str = "New Conversation"
    ) -> str:
        """Create a new conversation thread."""
        try:
            success = await backend.create_conversation(
                conversation_id=conversation_id,
                agent_id=agent_id,
                title=title
            )
            if success:
                return f"Created conversation '{title}' with ID: {conversation_id}"
            else:
                return f"Failed to create conversation {conversation_id}"
        except Exception as e:
            return f"Error creating conversation: {str(e)}"
    
    @langchain_tool(description=LIST_CONVERSATIONS_DESCRIPTION)
    async def list_conversations(
        agent_id: Optional[str] = None,
        limit: int = 20
    ) -> str:
        """List recent conversations with optional agent filter."""
        try:
            conversations = await backend.list_conversations(agent_id=agent_id, limit=limit)
            
            if not conversations:
                return "No conversations found."
            
            result = f"Found {len(conversations)} conversations:\n"
            for conv in conversations:
                result += f"• {conv['title']} (ID: {conv['id']}, Messages: {conv.get('message_count', 0)})\n"
            
            return result.strip()
        except Exception as e:
            return f"Error listing conversations: {str(e)}"
    
    return [generate_conversation_title, create_conversation, list_conversations]


def _generate_title_from_content(content: str) -> str:
    """Generate a conversation title from content using simple heuristics."""
    import re
    
    # Extract first meaningful sentence or phrase
    lines = content.split('\n')
    for line in lines:
        # Skip role prefixes and get actual content
        if ':' in line:
            content_part = line.split(':', 1)[1].strip()
        else:
            content_part = line.strip()
        
        if len(content_part) > 10:  # Meaningful content
            # Clean and truncate
            title = re.sub(r'[^\w\s-]', '', content_part)[:50]
            title = ' '.join(title.split())  # Normalize whitespace
            
            if title:
                return title.title()
    
    # Fallback titles based on keywords
    content_lower = content.lower()
    if 'error' in content_lower or 'bug' in content_lower:
        return "Debugging Session"
    elif 'implement' in content_lower or 'create' in content_lower:
        return "Implementation Task" 
    elif 'help' in content_lower or 'how' in content_lower:
        return "Help Request"
    elif 'test' in content_lower:
        return "Testing Discussion"
    else:
        return "General Discussion"


# Global tool registry instance
_global_registry = ToolRegistry()


def get_global_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _global_registry


def set_global_registry(registry: ToolRegistry):
    """Set the global tool registry."""
    global _global_registry
    _global_registry = registry


# Register built-in tools
def register_builtin_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """Register all built-in tools with the registry."""
    if registry is None:
        registry = get_global_registry()
    
    # Create tool instances for built-in LangChain tools
    registry.register_tool(FunctionTool(write_todos, "write_todos", WRITE_TODOS_DESCRIPTION), "builtin")
    registry.register_tool(FunctionTool(ls_files, "ls", LS_FILES_DESCRIPTION), "builtin") 
    registry.register_tool(FunctionTool(read_file, "read_file", READ_FILE_DESCRIPTION), "builtin")
    registry.register_tool(FunctionTool(write_file, "write_file", WRITE_FILE_DESCRIPTION), "builtin")
    registry.register_tool(FunctionTool(edit_file, "edit_file", EDIT_FILE_DESCRIPTION), "builtin")
    
    return registry


def register_integration_tools(registry: Optional[ToolRegistry] = None) -> ToolRegistry:
    """Register all integration tools with the registry."""
    if registry is None:
        registry = get_global_registry()
    
    # Import integration tools
    try:
        from broadie.core.integrations import (
            # Google Drive tools
            search_google_drive,
            read_google_drive_file,
            write_google_drive_file,
            create_google_sheet,
            update_google_sheet,
            list_drive_folders,
            # Slack tools
            search_slack_messages,
            send_slack_message,
            send_slack_dm,
            list_slack_channels,
            list_slack_users,
            get_slack_user_info,
            create_slack_thread,
            upload_slack_file,
        )
        
        # Register Google Drive tools
        registry.register_tool(FunctionTool(search_google_drive, "search_google_drive"), "google_drive")
        registry.register_tool(FunctionTool(read_google_drive_file, "read_google_drive_file"), "google_drive")
        registry.register_tool(FunctionTool(write_google_drive_file, "write_google_drive_file"), "google_drive")
        registry.register_tool(FunctionTool(create_google_sheet, "create_google_sheet"), "google_drive")
        registry.register_tool(FunctionTool(update_google_sheet, "update_google_sheet"), "google_drive")
        registry.register_tool(FunctionTool(list_drive_folders, "list_drive_folders"), "google_drive")
        
        # Register Slack tools
        registry.register_tool(FunctionTool(search_slack_messages, "search_slack_messages"), "slack")
        registry.register_tool(FunctionTool(send_slack_message, "send_slack_message"), "slack")
        registry.register_tool(FunctionTool(send_slack_dm, "send_slack_dm"), "slack")
        registry.register_tool(FunctionTool(list_slack_channels, "list_slack_channels"), "slack")
        registry.register_tool(FunctionTool(list_slack_users, "list_slack_users"), "slack")
        registry.register_tool(FunctionTool(get_slack_user_info, "get_slack_user_info"), "slack")
        registry.register_tool(FunctionTool(create_slack_thread, "create_slack_thread"), "slack")
        registry.register_tool(FunctionTool(upload_slack_file, "upload_slack_file"), "slack")
        
    except ImportError as e:
        # Integration tools are optional - only register if dependencies are available
        print(f"Warning: Integration tools not available: {e}")
    
    return registry


# Auto-register built-in tools
register_builtin_tools()

# Auto-register integration tools  
register_integration_tools()