"""
Conversation management tools for agent conversation handling.
"""

from typing import Optional

from langchain_core.tools import tool as langchain_tool

from broadie.tools.registry import PersistenceContext

GENERATE_TITLE_DESCRIPTION = """Generate an appropriate title for a conversation based on its content. Automatically analyzes conversation messages and creates a descriptive title for better organization. Called automatically for new conversations."""

CREATE_CONVERSATION_DESCRIPTION = """Create a new conversation thread with a specific title and agent. Use this to start new conversation contexts that can be referenced later."""

LIST_CONVERSATIONS_DESCRIPTION = """List recent conversations with optional agent filter. Shows conversation titles, IDs, and message counts for easy navigation and context switching."""


def create_conversation_tools(backend):
    """Create conversation management tools with backend dependency injection."""

    @langchain_tool(description=GENERATE_TITLE_DESCRIPTION)
    async def generate_conversation_title(
        conversation_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        recent_messages: Optional[str] = None,
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
                    title="New Conversation",
                )

            # Get recent messages if not provided
            if not recent_messages:
                messages = await backend.get_messages(conversation_id)
                if messages:
                    # Take first few messages to generate title
                    recent_messages = "\n".join(
                        [
                            f"{msg['role']}: {msg['content'][:100]}"
                            for msg in messages[:3]
                        ]
                    )

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
        conversation_id: str, agent_id: str, title: str = "New Conversation"
    ) -> str:
        """Create a new conversation thread."""
        try:
            success = await backend.create_conversation(
                conversation_id=conversation_id, agent_id=agent_id, title=title
            )
            if success:
                return f"Created conversation '{title}' with ID: {conversation_id}"
            else:
                return f"Failed to create conversation {conversation_id}"
        except Exception as e:
            return f"Error creating conversation: {str(e)}"

    @langchain_tool(description=LIST_CONVERSATIONS_DESCRIPTION)
    async def list_conversations(
        agent_id: Optional[str] = None, limit: int = 20
    ) -> str:
        """List recent conversations with optional agent filter."""
        try:
            conversations = await backend.list_conversations(
                agent_id=agent_id, limit=limit
            )

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
    lines = content.split("\n")
    for line in lines:
        # Skip role prefixes and get actual content
        if ":" in line:
            content_part = line.split(":", 1)[1].strip()
        else:
            content_part = line.strip()

        if len(content_part) > 10:  # Meaningful content
            # Clean and truncate
            title = re.sub(r"[^\w\s-]", "", content_part)[:50]
            title = " ".join(title.split())  # Normalize whitespace

            if title:
                return title.title()

    # Fallback titles based on keywords
    content_lower = content.lower()
    if "error" in content_lower or "bug" in content_lower:
        return "Debugging Session"
    elif "implement" in content_lower or "create" in content_lower:
        return "Implementation Task"
    elif "help" in content_lower or "how" in content_lower:
        return "Help Request"
    elif "test" in content_lower:
        return "Testing Discussion"
    else:
        return "General Discussion"
