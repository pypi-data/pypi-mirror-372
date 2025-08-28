"""
Memory management tools for persistent agent memory.
"""

from typing import Any, Dict, Optional

from langchain_core.tools import tool as langchain_tool

STORE_MEMORY_DESCRIPTION = """Store a memory for an agent that persists across sessions. Memories help agents remember important information, context, and learned patterns."""

RECALL_MEMORIES_DESCRIPTION = """Recall stored memories for an agent. Returns recent memories that can help provide context and continuity across conversations."""


def create_memory_tools(backend):
    """Create memory management tools with backend dependency injection."""

    @langchain_tool(description=STORE_MEMORY_DESCRIPTION)
    async def store_memory(
        content: str,
        agent_id: str,
        memory_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a memory for an agent."""
        import uuid

        if not memory_id:
            memory_id = str(uuid.uuid4())

        success = await backend.store_memory(
            memory_id=memory_id, agent_id=agent_id, content=content, metadata=metadata
        )

        if success:
            return f"Stored memory: {content} (ID: {memory_id})"
        else:
            return f"Failed to store memory"

    @langchain_tool(description=RECALL_MEMORIES_DESCRIPTION)
    async def recall_memories(agent_id: str, limit: int = 10) -> str:
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
