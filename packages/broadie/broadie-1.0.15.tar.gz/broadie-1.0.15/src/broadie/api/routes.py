"""
HTTP routes for Broadie API server.
"""

import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from broadie.config.settings import BroadieSettings

router = APIRouter()


def _clean_text(s: str) -> str:
    s = s or ""
    s = re.sub(r"\s+", " ", s.strip())
    return s


def _generate_title_from_prompt(prompt: str, max_len: int = 60) -> str:
    base = _clean_text(prompt)
    if len(base) <= max_len:
        return base or "New Conversation"
    return base[: max_len - 1].rstrip() + "…"


def _generate_summary(user_msg: str, assistant_msg: str, max_len: int = 180) -> str:
    u = _clean_text(user_msg)
    a = _clean_text(assistant_msg)
    combo = f"Q: {u} • A: {a}" if u and a else (u or a)
    if not combo:
        return None
    if len(combo) <= max_len:
        return combo
    return combo[: max_len - 1].rstrip() + "…"


def get_settings() -> BroadieSettings:
    """Dependency to get application settings."""
    return BroadieSettings()


class InvokeRequest(BaseModel):
    """Schema for invoke request body."""

    message: str
    context: Optional[Dict[str, Any]] = None
    conversation_id: Optional[str] = None
    response_format: Optional[str] = Field(default=None, description="Response format: json, markdown, slack, email, or api")


class TodoCreateRequest(BaseModel):
    """Schema for creating a new todo."""

    description: str
    assigned_to: Optional[str] = None
    source_tool: Optional[str] = None


class TodoUpdateRequest(BaseModel):
    """Schema for updating a todo."""

    status: str
    assigned_to: Optional[str] = None


@router.get("/api/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@router.get("/api/agents/{agent_id}/")
async def get_agent_info(
    agent_id: str,
    app_request: Request,
    settings: BroadieSettings = Depends(get_settings),
) -> dict:
    """Get agent information and capabilities."""
    # Get the agent from app state
    agent = getattr(app_request.app.state, "agent", None)
    if not agent:
        raise HTTPException(status_code=503, detail="No agent available")

    # Verify agent ID matches (if configured)
    expected_agent_id = settings.a2a.agent_id or agent.name
    if agent_id != expected_agent_id and agent_id != "default":
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Get agent identity and capabilities
    identity = agent.get_identity()

    # Compute canonical agent id
    canonical_id = settings.a2a.agent_id or agent.name

    # Build capabilities response
    capabilities = {
        "id": canonical_id,  # canonical agent id
        "agent_id": agent_id,  # id used in the request path (may be "default")
        "name": agent.name,
        "description": getattr(agent.config, "description", ""),
        "instruction": agent.instruction,
        "model": {
            "provider": agent.config.model_provider,
            "name": agent.config.model_name,
            "settings": agent.config.model_settings,
        },
        "tools": [
            {
                "name": tool_name,
                "description": f"Tool: {tool_name}",  # Could be enhanced with actual tool descriptions
                "type": "function",
            }
            for tool_name in agent.config.tools
        ],
        "sub_agents": [
            {
                "name": sub_name,
                "description": getattr(sub_agent.config, "description", ""),
                "tools": sub_agent.config.tools,
            }
            for sub_name, sub_agent in agent.sub_agents.items()
        ],
        "endpoints": {
            "invoke": f"/api/agents/{canonical_id}/invoke",
            "websocket": f"/api/agents/{canonical_id}/ws",
            "info": f"/api/agents/{canonical_id}/",
        },
        "features": {
            "streaming": True,
            "memory": bool(agent.memory_manager),
            "persistence": bool(getattr(agent, "checkpointer", None)),
            "sub_agents": len(agent.sub_agents) > 0,
        },
        "status": "online",
        "version": "1.0.0",  # Could be made configurable
    }

    return capabilities


@router.post("/api/agents/{agent_id}/invoke")
async def invoke_agent(
    agent_id: str,
    request: InvokeRequest,
    app_request: Request,
    settings: BroadieSettings = Depends(get_settings),
) -> dict:
    """Invoke agent with a message and get response."""
    # Get the agent from app state
    agent = getattr(app_request.app.state, "agent", None)
    if not agent:
        raise HTTPException(status_code=503, detail="No agent available")

    # Verify agent ID matches (if configured)
    expected_agent_id = settings.a2a.agent_id or agent.name
    if agent_id != expected_agent_id and agent_id != "default":
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    # Determine conversation_id for conversation
    conversation_id = request.conversation_id or str(uuid.uuid4())

    # Set API response context with notifications enabled
    from broadie.core.response_context import create_api_context, set_response_context

    notification_channels = []
    if hasattr(agent, "destination_resolver"):
        for dest_name in agent.list_destinations():
            dest_config = agent.destination_resolver.destinations.get_destination(
                dest_name
            )
            if dest_config and dest_config.enabled:
                notification_channels.append(dest_name)

    api_context = create_api_context(
        user_id=request.context.get("user_id") if request.context else None,
        conversation_id=conversation_id,
        agent_name=agent.name,
        notification_channels=notification_channels,
    )
    set_response_context(api_context)

    # Ensure conversation exists with a generated title on first user message
    backend = getattr(app_request.app.state, "backend")
    try:
        existing = await backend.get_conversation(conversation_id)
    except Exception:
        existing = None
    if not existing and hasattr(backend, "create_conversation"):
        try:
            gen_title = _generate_title_from_prompt(request.message)
            await backend.create_conversation(
                conversation_id, agent_id, title=gen_title
            )
        except Exception:
            pass
    # Persist user message
    user_ts = datetime.utcnow().isoformat()
    await backend.store_message(
        conversation_id, agent_id, "user", request.message, user_ts
    )

    try:
        # Invoke the agent with the message (use async version for full schema support)
        response = await agent.ainvoke(
            message=request.message, conversation_id=conversation_id
        )
        # Persist assistant response
        resp_ts = datetime.utcnow().isoformat()
        await backend.store_message(
            conversation_id, agent_id, "assistant", response, resp_ts
        )

        # Apply response format rendering if requested
        formatted_response = response
        response_format_type = "json"  # Default format
        
        if request.response_format and request.response_format.lower() != "json":
            try:
                # Parse the original response as JSON to create envelope
                import json
                if response.strip().startswith('{'):
                    original_data = json.loads(response)
                    
                    # Create envelope for rendering
                    envelope = {
                        "agent": agent.name,
                        "timestamp": resp_ts,
                        "schema": "api_response",
                        "payload": original_data,
                        "metadata": {
                            "conversation_id": conversation_id,
                            "requested_format": request.response_format.lower()
                        }
                    }
                    
                    # Use renderer agent to format response
                    from broadie.core.renderer_agent import create_renderer_agent
                    renderer = create_renderer_agent(parent_agent=agent)
                    formatted_response = await renderer.render_envelope(
                        envelope, request.response_format.lower()
                    )
                    response_format_type = request.response_format.lower()
                    
            except Exception as e:
                # If rendering fails, log warning and return original response
                print(f"Warning: Response format rendering failed: {e}")
                formatted_response = response
                response_format_type = "json"

        # After assistant response, ensure title and summary are set
        try:
            conv_meta = await backend.get_conversation(conversation_id)
        except Exception:
            conv_meta = None
        try:
            # Title: if missing or default, set from first user prompt
            current_title = (
                conv_meta.get("title") if isinstance(conv_meta, dict) else None
            )
            if not current_title or current_title.strip().lower() in {
                "new conversation",
                "",
            }:
                gen_title = _generate_title_from_prompt(request.message)
                if hasattr(backend, "update_conversation_title"):
                    await backend.update_conversation_title(conversation_id, gen_title)
            # Summary: Q/A concise blurb
            if hasattr(backend, "update_conversation_summary"):
                gen_summary = _generate_summary(request.message, str(response))
                await backend.update_conversation_summary(conversation_id, gen_summary)
        except Exception:
            pass

        # Get the message ID for todo association
        messages = await backend.get_messages(conversation_id)
        message_id = None
        if messages:
            # Find the last assistant message (just stored)
            for i, msg in enumerate(messages):
                if msg.get("role") == "assistant" and msg.get("content") == response:
                    message_id = i + 1  # Use 1-based indexing
                    break

        # Get any todos created for this message
        todos = []
        if message_id:
            todos = await backend.get_todos(
                conversation_id=conversation_id, message_id=message_id
            )
        else:
            todos = await backend.get_todos(conversation_id=conversation_id)

        # Return response with conversation_id and todos
        # Response may be formatted based on request.response_format
        return {
            "agent_id": agent_id,
            "response": formatted_response,
            "conversation_id": conversation_id,
            "todos": todos,
            "format": response_format_type,  # Indicate actual response format
            "notifications_enabled": len(notification_channels) > 0,
            "notification_channels": notification_channels,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invoking agent: {str(e)}")


@router.get("/api/conversations")
async def get_conversations(
    app_request: Request,
) -> dict:
    """Get all conversations with metadata."""
    backend = getattr(app_request.app.state, "backend")
    try:
        # Use a very high limit to effectively return all conversations
        conversations = await backend.list_conversations(limit=100)
    except Exception as e:
        print(f"Error fetching conversations: {e}")
        conversations = []

    return {"conversations": conversations}


@router.get("/api/conversations/{conversation_id}/messages")
async def get_messages(
    conversation_id: str,
    app_request: Request,
) -> dict:
    """Get all messages for a specific conversation."""
    backend = getattr(app_request.app.state, "backend")

    messages = await backend.get_messages(conversation_id)
    # Also include conversation metadata for UI synchronization (e.g., agent selection)
    conv = None
    try:
        conv = await backend.get_conversation(conversation_id)
    except Exception:
        conv = None
    agent_id = conv.get("agent_id") if conv else None
    title = conv.get("title") if conv else None
    summary = conv.get("summary") if conv else None
    return {
        "conversation_id": conversation_id,
        "agent_id": agent_id,
        "title": title,
        "summary": summary,
        "messages": messages,
    }


@router.get("/todos")
async def get_todos(
    app_request: Request,
    conversation_id: Optional[str] = None,
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
) -> dict:
    """Get todos with optional filters."""
    backend = getattr(app_request.app.state, "backend")

    todos = await backend.get_todos(
        conversation_id=conversation_id, status=status, assigned_to=assigned_to
    )
    return {"todos": todos}


@router.get("/api/conversations/{conversation_id}/messages/{message_id}/todos")
async def get_message_todos(
    conversation_id: str,
    message_id: int,
    app_request: Request,
) -> dict:
    """Get todos for a specific message."""
    backend = getattr(app_request.app.state, "backend")

    todos = await backend.get_todos(
        conversation_id=conversation_id, message_id=message_id
    )
    return {
        "conversation_id": conversation_id,
        "message_id": message_id,
        "todos": todos,
    }


@router.post("/api/conversations/{conversation_id}/todos")
async def create_todo(
    conversation_id: str,
    request: TodoCreateRequest,
    app_request: Request,
    message_id: Optional[int] = None,
) -> dict:
    """Create a new todo for a conversation."""
    backend = getattr(app_request.app.state, "backend")

    todo_id = await backend.create_todo(
        conversation_id=conversation_id,
        description=request.description,
        message_id=message_id,
        assigned_to=request.assigned_to,
        source_tool=request.source_tool or "api",
    )

    # Get the created todo to return
    todo = await backend.get_todo_by_id(todo_id)
    return {"todo": todo}


@router.patch("/todos/{todo_id}")
async def update_todo(
    todo_id: str,
    request: TodoUpdateRequest,
    app_request: Request,
) -> dict:
    """Update a todo's status or assignment."""
    backend = getattr(app_request.app.state, "backend")

    success = await backend.update_todo_status(
        todo_id=todo_id, status=request.status, assigned_to=request.assigned_to
    )

    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")

    # Get the updated todo to return
    todo = await backend.get_todo_by_id(todo_id)
    return {"todo": todo}
