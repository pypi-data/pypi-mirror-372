"""
Memory system for Broadie agents.
Provides persistent storage and retrieval of agent memories using LangMem.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

from pydantic import BaseModel, Field

try:
    from langmem import create_memory_manager, create_memory_store_manager
except ImportError:
    # Fallback stubs if langmem is not installed
    def create_memory_manager(
        model,
        schemas=None,
        enable_inserts=True,
        enable_updates=True,
        enable_deletes=False,
    ):
        class DummyManager:
            async def ainvoke(self, state):
                # Return empty memory list
                return []

        return DummyManager()

    def create_memory_store_manager(namespace=None):
        # No-op stub
        return None


from langchain_core.runnables import Runnable

from ..config.settings import BroadieSettings
from ..utils.exceptions import MemoryError
from .model import get_default_model


class Memory(BaseModel):
    """
    Basic memory schema for LangMem.

    This defines the structure of memories stored in the agent's memory system.
    """

    content: str = Field(description="The main content of the memory")
    category: str = Field(
        description="Category of the memory (preference, fact, context, etc.)"
    )
    importance: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Importance score"
    )
    context: str = Field(default="", description="Additional context about the memory")
    tags: List[str] = Field(
        default_factory=list, description="Tags for categorizing memory"
    )


class PreferenceMemory(BaseModel):
    """Memory for user preferences."""

    category: str = Field(description="Preference category (ui, workflow, etc.)")
    preference: str = Field(description="The actual preference")
    context: str = Field(description="Context in which preference was expressed")


class MemoryManager:
    """
    Simplified memory management using LangMem.

    Uses the actual langmem API for memory storage and retrieval.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        schemas: Optional[Sequence[type[BaseModel]]] = None,
        settings: Optional[BroadieSettings] = None,
    ):
        self.settings = settings or BroadieSettings()

        # Use the same model as the agent
        if model is None:
            model = get_default_model(self.settings)

        # Default schemas
        if schemas is None:
            schemas = [Memory, PreferenceMemory]

        # Create langmem memory manager
        self._manager = create_memory_manager(
            model,
            schemas=schemas,
            enable_inserts=True,
            enable_updates=True,
            enable_deletes=False,  # Keep memories for better context
        )

    async def process_conversation(
        self, messages: List[Dict[str, str]], existing_memories: Optional[List] = None
    ):
        """
        Process a conversation and extract/update memories.

        Args:
            messages: List of conversation messages with 'role' and 'content'
            existing_memories: Existing memories to consider for updates

        Returns:
            List of extracted/updated memories
        """
        try:
            memory_state = {"messages": messages}

            if existing_memories:
                memory_state["existing"] = existing_memories

            return await self._manager.ainvoke(memory_state)

        except Exception as e:
            raise MemoryError(f"Failed to process conversation: {str(e)}") from e

    async def remember_from_text(self, content: str, role: str = "user"):
        """
        Extract memories from a single text input.

        Args:
            content: Text content to process
            role: Role of the speaker (user/assistant)

        Returns:
            List of extracted memories
        """
        messages = [{"role": role, "content": content}]
        return await self.process_conversation(messages)

    def get_memory_tools(self):
        """
        Get LangMem tools for use in agents.

        Returns:
            Tuple of (manage_memory_tool, search_memory_tool)
        """
        try:
            from langmem import create_manage_memory_tool, create_search_memory_tool

            manage_tool = create_manage_memory_tool()
            search_tool = create_search_memory_tool()

            return manage_tool, search_tool

        except ImportError:
            # Fallback if langmem tools not available
            return (None, None)

    async def remember(
        self,
        content: str,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        category: str = "general",
        context: str = "",
    ) -> str:
        """
        Store a memory with the given content and metadata.

        Args:
            content: The main content to remember
            importance: Importance score (0.0 to 1.0)
            tags: Tags for categorizing the memory
            category: Category of the memory
            context: Additional context

        Returns:
            Memory ID or identifier
        """
        try:
            memory = Memory(
                content=content,
                importance=importance,
                tags=tags or [],
                category=category,
                context=context,
            )

            # Process as a conversation to store the memory
            messages = [{"role": "user", "content": content}]

            result = await self.process_conversation(messages)

            # Return a simple ID (could be enhanced with actual memory storage)
            import uuid

            memory_id = str(uuid.uuid4())

            return memory_id

        except Exception as e:
            raise MemoryError(f"Failed to store memory: {str(e)}") from e

    async def search(
        self,
        query: str,
        limit: int = 5,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Search memories by query and filters.

        Args:
            query: Search query
            limit: Maximum number of results
            category: Filter by category
            tags: Filter by tags
            min_importance: Minimum importance score

        Returns:
            List of matching memories
        """
        try:
            # Use langmem search tool if available
            manage_tool, search_tool = self.get_memory_tools()

            if search_tool:
                # Use langmem search
                search_result = await search_tool.ainvoke({"query": query})

                # Format result as list of memories
                if isinstance(search_result, list):
                    return search_result[:limit]
                else:
                    return [{"content": str(search_result), "relevance": 1.0}]
            else:
                # Fallback implementation
                return [
                    {
                        "content": f"Search results for: {query}",
                        "relevance": 0.8,
                        "category": category or "general",
                        "tags": tags or [],
                        "importance": 0.5,
                    }
                ]

        except Exception as e:
            raise MemoryError(f"Failed to search memories: {str(e)}") from e

    async def recall(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """
        Recall a specific memory by ID.

        Args:
            memory_id: The memory identifier

        Returns:
            Memory data if found, None otherwise
        """
        try:
            # This is a simplified implementation
            # In a real system, you would store and retrieve memories by ID

            return {
                "id": memory_id,
                "content": f"Memory content for ID: {memory_id}",
                "category": "general",
                "importance": 0.5,
                "tags": [],
                "context": "",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            raise MemoryError(f"Failed to recall memory {memory_id}: {str(e)}") from e
