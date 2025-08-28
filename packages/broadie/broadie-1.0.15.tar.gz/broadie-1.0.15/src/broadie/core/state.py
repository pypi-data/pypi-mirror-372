"""
State management for Broadie agents.
Defines state schemas and reducers for agent execution.
"""

from typing import Annotated, Any, Dict, List, Literal, Optional

# NotRequired fallback (requires Python 3.11+)
try:
    from typing import NotRequired
except ImportError:
    # Fallback NotRequired for older Python: supports subscription
    class _NotRequiredType:
        def __getitem__(self, item):
            return item

    NotRequired = _NotRequiredType()
from langgraph.prebuilt.chat_agent_executor import AgentState

# TypedDict fallback
try:
    from typing_extensions import TypedDict
except ImportError:

    class TypedDict(dict):
        """Fallback TypedDict base class."""

        pass


from broadie.utils.exceptions import BroadieError


class Todo(TypedDict):
    """Todo item for task tracking."""

    content: str
    status: Literal["pending", "in_progress", "completed"]


def file_reducer(left: Dict[str, str], right: Dict[str, str]) -> Dict[str, str]:
    """
    Reducer function for merging file states.

    Args:
        left: Existing file state
        right: New file state to merge

    Returns:
        Merged file state
    """
    if left is None:
        return right or {}
    elif right is None:
        return left or {}
    else:
        # Merge dictionaries, with right taking precedence
        return {**left, **right}


class BroadieState(AgentState):
    """
    Enhanced state schema for Broadie agents.

    Extends LangGraph's AgentState with additional fields for:
    - Todo/task tracking
    - File system simulation
    - Agent-specific metadata
    """

    # Task management
    todos: NotRequired[list[Todo]]

    # File system simulation for development tools
    files: Annotated[NotRequired[Dict[str, str]], file_reducer]

    # Agent metadata
    agent_metadata: NotRequired[Dict[str, Any]]

    # Memory context
    memory_context: NotRequired[Dict[str, Any]]

    # A2A communication state
    peer_agents: NotRequired[Dict[str, Dict[str, Any]]]


class TaskState(TypedDict):
    """State for task execution within sub-agents."""

    task_id: str
    description: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    result: NotRequired[Any]
    error: NotRequired[str]
    metadata: NotRequired[Dict[str, Any]]


class MemoryState(TypedDict):
    """State for memory operations."""

    memories: NotRequired[Dict[str, Any]]
    search_context: NotRequired[Dict[str, Any]]
    recall_history: NotRequired[list[str]]


class A2AState(TypedDict):
    """State for agent-to-agent communication."""

    peer_registry: NotRequired[Dict[str, Dict[str, Any]]]
    trusted_agents: NotRequired[list[str]]
    communication_log: NotRequired[list[Dict[str, Any]]]


# Type aliases for commonly used state types
DeepAgentState = BroadieState  # Backward compatibility
AgentState = BroadieState  # Alias for clarity


class StateManager:
    """
    Manager for agent state operations.

    Provides utilities for state manipulation, validation, and persistence.
    """

    @staticmethod
    def create_initial_state() -> BroadieState:
        """Create initial state for a new agent session."""
        return BroadieState(
            messages=[],
            todos=[],
            files={},
            agent_metadata={},
            memory_context={},
            peer_agents={},
        )

    @staticmethod
    def add_todo(
        state: BroadieState, content: str, status: str = "pending"
    ) -> BroadieState:
        """Add a new todo item to the state."""
        if status not in ["pending", "in_progress", "completed"]:
            raise BroadieError(f"Invalid todo status: {status}")

        todo = Todo(content=content, status=status)

        if "todos" not in state:
            state["todos"] = []

        state["todos"].append(todo)
        return state

    @staticmethod
    def update_todo_status(
        state: BroadieState, todo_index: int, status: str
    ) -> BroadieState:
        """Update the status of a todo item."""
        if status not in ["pending", "in_progress", "completed"]:
            raise BroadieError(f"Invalid todo status: {status}")

        if "todos" not in state or todo_index >= len(state["todos"]):
            raise BroadieError(f"Todo index {todo_index} not found")

        state["todos"][todo_index]["status"] = status
        return state

    @staticmethod
    def add_file(state: BroadieState, file_path: str, content: str) -> BroadieState:
        """Add or update a file in the state."""
        if "files" not in state:
            state["files"] = {}

        state["files"][file_path] = content
        return state

    @staticmethod
    def get_file(state: BroadieState, file_path: str) -> str:
        """Get file content from state."""
        files = state.get("files", {})
        if file_path not in files:
            raise BroadieError(f"File '{file_path}' not found in state")

        return files[file_path]

    @staticmethod
    def list_files(state: BroadieState) -> list[str]:
        """List all files in the state."""
        return list(state.get("files", {}).keys())

    @staticmethod
    def update_agent_metadata(
        state: BroadieState, key: str, value: Any
    ) -> BroadieState:
        """Update agent metadata."""
        if "agent_metadata" not in state:
            state["agent_metadata"] = {}

        state["agent_metadata"][key] = value
        return state

    @staticmethod
    def get_agent_metadata(state: BroadieState, key: str, default: Any = None) -> Any:
        """Get agent metadata value."""
        metadata = state.get("agent_metadata", {})
        return metadata.get(key, default)

    @staticmethod
    def add_peer_agent(
        state: BroadieState, agent_id: str, agent_info: Dict[str, Any]
    ) -> BroadieState:
        """Add a peer agent to the registry."""
        if "peer_agents" not in state:
            state["peer_agents"] = {}

        state["peer_agents"][agent_id] = agent_info
        return state

    @staticmethod
    def get_peer_agents(state: BroadieState) -> Dict[str, Dict[str, Any]]:
        """Get all peer agents."""
        return state.get("peer_agents", {})

    @staticmethod
    def validate_state(state: BroadieState) -> bool:
        """Validate state structure."""
        required_fields = ["messages"]

        for field in required_fields:
            if field not in state:
                raise BroadieError(f"Missing required state field: {field}")

        # Validate todos if present
        if "todos" in state:
            for i, todo in enumerate(state["todos"]):
                if "content" not in todo or "status" not in todo:
                    raise BroadieError(f"Invalid todo at index {i}")

                if todo["status"] not in ["pending", "in_progress", "completed"]:
                    raise BroadieError(
                        f"Invalid todo status at index {i}: {todo['status']}"
                    )

        return True

    @staticmethod
    def serialize_state(state: BroadieState) -> Dict[str, Any]:
        """Serialize state for storage."""
        # Convert state to plain dictionary for serialization
        serialized = {}

        for key, value in state.items():
            if hasattr(value, "model_dump"):
                # Handle Pydantic models
                serialized[key] = value.model_dump()
            elif hasattr(value, "__dict__"):
                # Handle objects with __dict__
                serialized[key] = value.__dict__
            else:
                # Handle primitive types
                serialized[key] = value

        return serialized

    @staticmethod
    def deserialize_state(data: Dict[str, Any]) -> BroadieState:
        """Deserialize state from storage."""
        # Create state from dictionary
        state = BroadieState(**data)
        return state


class DatabaseStateManager(StateManager):
    """
    State manager that persists state operations to database.

    Extends StateManager to automatically persist todos, messages, and memories
    to the database backend.
    """

    def __init__(self, backend=None):
        self.backend = backend

    async def add_todo_persistent(
        self,
        state: BroadieState,
        thread_id: str,
        content: str,
        message_id: Optional[int] = None,
        status: str = "pending",
        assigned_to: Optional[str] = None,
        source_tool: str = "agent",
    ) -> BroadieState:
        """Add todo to state and persist to database."""
        # Add to state
        state = self.add_todo(state, content, status)

        # Persist to database if backend available
        if self.backend:
            try:
                await self.backend.create_todo(
                    thread_id=thread_id,
                    description=content,
                    message_id=message_id,
                    assigned_to=assigned_to,
                    source_tool=source_tool,
                    status=status,
                )
            except Exception:
                # Don't break state flow if persistence fails
                pass

        return state

    async def store_message_with_todos(
        self,
        conversation_id: str,
        agent_id: str,
        role: str,
        content: str,
        timestamp: str,
        todos: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[int]:
        """Store message and associated todos to database."""
        if not self.backend:
            return None

        try:
            message_id = await self.backend.store_message_with_metadata(
                conversation_id=conversation_id,
                agent_id=agent_id,
                role=role,
                content=content,
                timestamp=timestamp,
                todos_created=todos,
            )
            return message_id
        except Exception:
            # Fallback to regular message storage
            try:
                await self.backend.store_message(
                    conversation_id, agent_id, role, content, timestamp
                )
            except Exception:
                pass
            return None

    async def load_persistent_state(
        self, thread_id: str, initial_state: Optional[BroadieState] = None
    ) -> BroadieState:
        """Load state from database including messages and todos."""
        state = initial_state or self.create_initial_state()

        if not self.backend:
            return state

        try:
            # Load messages for context (latest 10)
            messages = await self.backend.get_messages(thread_id)
            if messages:
                # Convert to LangGraph message format
                state["messages"] = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in messages[-10:]  # Last 10 messages
                ]

            # Load todos
            todos = await self.backend.get_todos(thread_id=thread_id)
            if todos:
                # Convert to state format
                state["todos"] = [
                    {
                        "content": todo["description"],
                        "status": todo["status"],
                        "id": todo["id"],
                        "assigned_to": todo.get("assigned_to"),
                        "created_at": todo.get("created_at"),
                    }
                    for todo in todos
                ]

        except Exception:
            # Don't fail if loading fails - just use empty state
            pass

        return state
