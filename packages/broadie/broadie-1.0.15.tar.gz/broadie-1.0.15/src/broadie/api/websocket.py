"""
WebSocket routes for Broadie API server.
"""

import asyncio
import json
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

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


def _generate_summary(
    user_msg: str, assistant_msg: str, max_len: int = 180
) -> Optional[str]:
    u = _clean_text(user_msg)
    a = _clean_text(assistant_msg)
    combo = f"Q: {u} • A: {a}" if u and a else (u or a)
    if not combo:
        return None
    if len(combo) <= max_len:
        return combo
    return combo[: max_len - 1].rstrip() + "…"


@router.websocket("/api/agents/{agent_id}/ws")
async def agent_ws(websocket: WebSocket, agent_id: str) -> None:
    """WebSocket endpoint for real-time chat/streaming responses.
    - Generates a conversation_id when none is provided
    - Persists user and assistant messages to backend
    - Streams chunks when available
    """
    await websocket.accept()

    # Get agent and settings from app state
    agent = getattr(websocket.app.state, "agent", None)
    settings = getattr(websocket.app.state, "settings", None)
    backend = getattr(websocket.app.state, "backend", None)

    if not agent:
        await websocket.send_json({"error": "No agent available"})
        await websocket.close()
        return

    # Verify agent ID if configured
    if settings and settings.a2a.agent_id:
        expected_agent_id = settings.a2a.agent_id
        if agent_id != expected_agent_id and agent_id != "default":
            await websocket.send_json({"error": f"Agent '{agent_id}' not found"})
            await websocket.close()
            return

    try:
        while True:
            # Wait for message from client
            data = await websocket.receive_text()

            # Parse JSON or raw string
            try:
                message_data = json.loads(data)
                if isinstance(message_data, dict):
                    message = message_data.get("message", "")
                    conversation_id = message_data.get(
                        "conversation_id"
                    ) or message_data.get("thread_id")
                    user_id = message_data.get("user_id")
                    session_id = message_data.get("session_id")
                else:
                    message = str(message_data)
                    conversation_id = None
                    user_id = None
                    session_id = None
            except json.JSONDecodeError:
                message = data
                conversation_id = None
                user_id = None
                session_id = None

            if not message:
                await websocket.send_json({"error": "Empty message"})
                continue

            # Ensure conversation id exists
            if not conversation_id:
                conversation_id = str(uuid.uuid4())
                # Optionally create a conversation record if backend supports it
                if backend and hasattr(backend, "create_conversation"):
                    try:
                        gen_title = _generate_title_from_prompt(message)
                        await backend.create_conversation(
                            conversation_id, agent_id, title=gen_title
                        )
                    except Exception:
                        pass

            # Set WebSocket response context with notifications enabled
            from broadie.core.response_context import (
                create_web_ui_context,
                set_response_context,
            )

            notification_channels = []
            if hasattr(agent, "destination_resolver"):
                for dest_name in agent.list_destinations():
                    dest_config = (
                        agent.destination_resolver.destinations.get_destination(
                            dest_name
                        )
                    )
                    if dest_config and dest_config.enabled:
                        notification_channels.append(dest_name)

            websocket_context = create_web_ui_context(
                user_id=user_id,
                session_id=session_id,
                conversation_id=conversation_id,
                agent_name=agent.name,
                notification_channels=notification_channels,
            )
            set_response_context(websocket_context)

            # Persist user message
            if backend and hasattr(backend, "store_message"):
                try:
                    await backend.store_message(
                        conversation_id,
                        agent_id,
                        "user",
                        message,
                        datetime.utcnow().isoformat(),
                    )
                except Exception:
                    pass

            # Acknowledge processing with context info
            await websocket.send_json(
                {
                    "type": "ack",
                    "message": "Processing...",
                    "notifications_enabled": len(notification_channels) > 0,
                    "format": "markdown",  # Web UI supports markdown
                }
            )

            try:
                response_text = ""
                # Stream response from agent if available
                if hasattr(agent, "stream"):
                    try:
                        for chunk in agent.stream(message, conversation_id):
                            if "messages" in chunk and chunk["messages"]:
                                last_message = chunk["messages"][-1]
                                raw_content = (
                                    last_message.content
                                    if hasattr(last_message, "content")
                                    else str(last_message)
                                )
                                try:
                                    content = (
                                        raw_content
                                        if isinstance(
                                            raw_content, (str, int, float, bool)
                                        )
                                        else json.dumps(raw_content, default=str)
                                    )
                                except Exception:
                                    content = str(raw_content)
                                content = str(content)
                                await websocket.send_json(
                                    {"type": "chunk", "content": content}
                                )
                                response_text += content
                    except Exception as stream_error:
                        # Fallback to regular invoke if streaming fails
                        print(
                            f"Streaming failed, falling back to invoke: {stream_error}"
                        )
                        resp = agent.invoke(message, conversation_id)
                        response_text = str(resp)
                        await websocket.send_json(
                            {
                                "type": "response",
                                "content": response_text,
                                "conversation_id": conversation_id,
                                "thread_id": conversation_id,
                            }
                        )
                else:
                    # Regular invoke path
                    resp = agent.invoke(message, conversation_id)
                    response_text = str(resp)
                    await websocket.send_json(
                        {
                            "type": "response",
                            "content": response_text,
                            "conversation_id": conversation_id,
                            "thread_id": conversation_id,
                        }
                    )

                # Persist assistant response
                if backend and hasattr(backend, "store_message") and response_text:
                    try:
                        await backend.store_message(
                            conversation_id,
                            agent_id,
                            "assistant",
                            response_text,
                            datetime.utcnow().isoformat(),
                        )
                    except Exception:
                        pass

                # After assistant response, ensure title and summary are set
                if backend:
                    try:
                        conv_meta = None
                        if hasattr(backend, "get_conversation"):
                            conv_meta = await backend.get_conversation(conversation_id)
                        # Title: if missing or default, set from first user prompt
                        current_title = (
                            conv_meta.get("title")
                            if isinstance(conv_meta, dict)
                            else None
                        )
                        if (not current_title) or (
                            current_title.strip().lower() in {"new conversation", ""}
                        ):
                            gen_title = _generate_title_from_prompt(message)
                            if hasattr(backend, "update_conversation_title"):
                                await backend.update_conversation_title(
                                    conversation_id, gen_title
                                )
                        # Summary: concise Q/A blurb
                        if hasattr(backend, "update_conversation_summary"):
                            gen_summary = _generate_summary(message, response_text)
                            await backend.update_conversation_summary(
                                conversation_id, gen_summary
                            )
                    except Exception:
                        pass

                # Fetch todos (if any) for this conversation
                todos = []
                if backend and hasattr(backend, "get_todos"):
                    try:
                        todos = await backend.get_todos(conversation_id=conversation_id)
                    except Exception:
                        todos = []

                # Completion signal with ids to allow UI to lock and refresh
                await websocket.send_json(
                    {
                        "type": "complete",
                        "conversation_id": conversation_id,
                        "thread_id": conversation_id,
                        "todos": todos,
                    }
                )
            except Exception as e:
                await websocket.send_json(
                    {"type": "error", "error": f"Error processing message: {str(e)}"}
                )
    except WebSocketDisconnect:
        print(f"WebSocket client disconnected for agent {agent_id}")
    except Exception as e:
        print(f"WebSocket error for agent {agent_id}: {e}")
        await websocket.close()
