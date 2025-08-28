"""
Todo management tools for persistent task tracking.
"""

from typing import Any, Dict, List, Optional

from langchain_core.tools import tool as langchain_tool

from broadie.tools.registry import PersistenceContext, Tool, ToolMetadata
from broadie.utils.exceptions import ToolError

ADD_TODO_DESCRIPTION = """Add a new todo item to track tasks and persist across sessions. If conversation_id is not provided, uses the current conversation context. Todos help organize work and track progress."""

LIST_TODOS_DESCRIPTION = """List todos with optional filters by conversation, status, or message. Shows todos with status icons (✅ done, ⏳ in_progress, 📌 pending) for easy visual scanning."""


class TodoManagerTool(Tool):
    """Tool for managing todos with persistence backend."""

    def __init__(self, backend=None):
        super().__init__(
            "todo_manager", "Create and manage todos that persist across sessions"
        )
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
                    raise ToolError(
                        "conversation_id and description are required for add_todo"
                    )

                todo_id = await self.backend.create_todo(
                    conversation_id=conversation_id,
                    description=description,
                    message_id=message_id,
                    assigned_to=assigned_to,
                    source_tool=source_tool,
                )
                return f"Created todo with ID: {todo_id}"

            elif action == "list_todos":
                conversation_id = kwargs.get("conversation_id")
                status = kwargs.get("status")
                message_id = kwargs.get("message_id")

                todos = await self.backend.get_todos(
                    conversation_id=conversation_id,
                    status=status,
                    message_id=message_id,
                )
                return todos

            elif action == "mark_done":
                todo_id = kwargs.get("todo_id")
                if not todo_id:
                    raise ToolError("todo_id is required for mark_done")

                success = await self.backend.update_todo_status(todo_id, "done")
                return (
                    f"Todo {todo_id} marked as done"
                    if success
                    else f"Todo {todo_id} not found"
                )

            elif action == "update_status":
                todo_id = kwargs.get("todo_id")
                status = kwargs.get("status")
                assigned_to = kwargs.get("assigned_to")

                if not todo_id or not status:
                    raise ToolError("todo_id and status are required for update_status")

                success = await self.backend.update_todo_status(
                    todo_id, status, assigned_to
                )
                return (
                    f"Todo {todo_id} updated"
                    if success
                    else f"Todo {todo_id} not found"
                )

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
                    "description": "Action to perform: add_todo, list_todos, mark_done, update_status",
                },
                "conversation_id": {"type": "str", "required": False},
                "description": {"type": "str", "required": False},
                "message_id": {"type": "int", "required": False},
                "todo_id": {"type": "str", "required": False},
                "status": {"type": "str", "required": False},
                "assigned_to": {"type": "str", "required": False},
                "source_tool": {"type": "str", "required": False},
            },
            return_type="Union[str, List[Dict]]",
            async_capable=True,
        )


def create_todo_tools(backend):
    """Create todo management tools with backend dependency injection."""

    @langchain_tool(description=ADD_TODO_DESCRIPTION)
    async def add_todo(
        description: str,
        conversation_id: Optional[str] = None,
        message_id: Optional[int] = None,
        assigned_to: Optional[str] = None,
        source_tool: str = "agent",
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
            source_tool=source_tool,
        )
        return f"Created todo: {description} (ID: {todo_id})"

    @langchain_tool(description=LIST_TODOS_DESCRIPTION)
    async def list_todos(
        conversation_id: Optional[str] = None,
        status: Optional[str] = None,
        message_id: Optional[int] = None,
    ) -> str:
        """List todos with optional filters."""
        todos = await backend.get_todos(
            conversation_id=conversation_id, status=status, message_id=message_id
        )

        if not todos:
            return "No todos found."

        result = f"Found {len(todos)} todos:\n"
        for todo in todos:
            status_icon = (
                "✅"
                if todo["status"] == "done"
                else "⏳" if todo["status"] == "in_progress" else "📌"
            )
            result += (
                f"{status_icon} {todo['description']} (Status: {todo['status']})\n"
            )

        return result.strip()

    @langchain_tool(
        description="Mark a todo as completed by setting its status to 'done'. Provides confirmation of completion."
    )
    async def mark_todo_done(todo_id: str) -> str:
        """Mark a todo as completed."""
        success = await backend.update_todo_status(todo_id, "done")
        if success:
            return f"Marked todo {todo_id} as completed."
        else:
            return f"Todo {todo_id} not found."

    @langchain_tool(
        description="Update todo status (pending, in_progress, done) and optionally reassign to a different agent or person."
    )
    async def update_todo_status(
        todo_id: str, status: str, assigned_to: Optional[str] = None
    ) -> str:
        """Update todo status (pending, in_progress, done) and optionally reassign."""
        if status not in ["pending", "in_progress", "done"]:
            return (
                f"Invalid status: {status}. Must be one of: pending, in_progress, done"
            )

        success = await backend.update_todo_status(todo_id, status, assigned_to)
        if success:
            assign_msg = f" and assigned to {assigned_to}" if assigned_to else ""
            return f"Updated todo {todo_id} to {status}{assign_msg}."
        else:
            return f"Todo {todo_id} not found."

    return [add_todo, list_todos, mark_todo_done, update_todo_status]
