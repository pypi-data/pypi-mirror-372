"""
Response context management for context-aware formatting and multi-channel responses.

This module handles different response contexts (CLI, Web UI, API, notifications)
and ensures appropriate formatting for each channel while supporting dual/tri
response patterns (direct response + notifications).
"""

import json
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Context variables for tracking response context
_response_context_var: ContextVar[Optional["ResponseContext"]] = ContextVar(
    "response_context", default=None
)


class ResponseChannel(Enum):
    """Supported response channels."""

    CLI = "cli"  # Command line interface (broadie run)
    WEB_UI = "web_ui"  # Web chat interface
    API = "api"  # REST API calls
    WEBSOCKET = "websocket"  # WebSocket connections
    NOTIFICATION = "notification"  # Notification destinations
    A2A = "a2a"  # Agent-to-agent communication


class ResponseFormat(Enum):
    """Supported response formats."""

    PLAIN_TEXT = "plain_text"  # Simple text for CLI
    MARKDOWN = "markdown"  # Markdown for web UI
    JSON = "json"  # JSON for API/webhooks
    SLACK_BLOCKS = "slack_blocks"  # Slack Block Kit format
    HTML = "html"  # HTML for email
    STRUCTURED = "structured"  # Structured data format


@dataclass
class ResponseContext:
    """Context information for response formatting."""

    # Primary response channel
    primary_channel: ResponseChannel

    # Additional notification channels
    notification_channels: List[str] = field(default_factory=list)

    # Formatting preferences
    preferred_format: Optional[ResponseFormat] = None
    supports_rich_formatting: bool = True
    supports_interactive_elements: bool = False

    # User/session context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    conversation_id: Optional[str] = None

    # Agent context
    agent_name: Optional[str] = None

    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set default format based on channel if not specified."""
        if self.preferred_format is None:
            self.preferred_format = self._get_default_format_for_channel()

    def _get_default_format_for_channel(self) -> ResponseFormat:
        """Get default format for the primary channel."""
        format_mapping = {
            ResponseChannel.CLI: ResponseFormat.PLAIN_TEXT,
            ResponseChannel.WEB_UI: ResponseFormat.MARKDOWN,
            ResponseChannel.API: ResponseFormat.JSON,
            ResponseChannel.WEBSOCKET: ResponseFormat.JSON,
            ResponseChannel.NOTIFICATION: ResponseFormat.PLAIN_TEXT,
            ResponseChannel.A2A: ResponseFormat.JSON,
        }
        return format_mapping.get(self.primary_channel, ResponseFormat.PLAIN_TEXT)

    def should_send_notifications(self) -> bool:
        """Check if notifications should be sent."""
        return len(self.notification_channels) > 0

    def clone_for_notification(self, destination_name: str) -> "ResponseContext":
        """Create a copy of context for notification channel."""
        return ResponseContext(
            primary_channel=ResponseChannel.NOTIFICATION,
            notification_channels=[],  # No nested notifications
            preferred_format=self._get_notification_format(destination_name),
            supports_rich_formatting=self._supports_rich_formatting(destination_name),
            supports_interactive_elements=False,  # Notifications don't support interactivity
            user_id=self.user_id,
            session_id=self.session_id,
            conversation_id=self.conversation_id,
            agent_name=self.agent_name,
            metadata=self.metadata.copy(),
        )

    def _get_notification_format(self, destination_name: str) -> ResponseFormat:
        """Get appropriate format for notification destination."""
        # This would ideally look up destination configuration
        # For now, use simple heuristics
        if "slack" in destination_name.lower():
            return ResponseFormat.SLACK_BLOCKS
        elif "email" in destination_name.lower():
            return ResponseFormat.HTML
        elif "webhook" in destination_name.lower():
            return ResponseFormat.JSON
        else:
            return ResponseFormat.PLAIN_TEXT

    def _supports_rich_formatting(self, destination_name: str) -> bool:
        """Check if destination supports rich formatting."""
        rich_destinations = ["slack", "email", "webhook"]
        return any(dest in destination_name.lower() for dest in rich_destinations)


@dataclass
class ResponseContent:
    """Structured response content that can be formatted for different channels."""

    # Core content
    message: str

    # Rich content elements
    title: Optional[str] = None
    summary: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    # Structured elements
    sections: List[Dict[str, Any]] = field(default_factory=list)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    attachments: List[Dict[str, Any]] = field(default_factory=list)

    # Formatting hints
    severity: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def format_for_context(self, context: ResponseContext) -> str:
        """Format content for the given response context."""
        formatter = ResponseFormatter()
        return formatter.format_content(self, context)


class ResponseFormatter:
    """Formats response content for different channels and formats."""

    def format_content(self, content: ResponseContent, context: ResponseContext) -> str:
        """Format content based on the response context."""
        format_method = getattr(self, f"_format_{context.preferred_format.value}", None)
        if format_method:
            return format_method(content, context)
        else:
            return self._format_plain_text(content, context)

    def _format_plain_text(
        self, content: ResponseContent, context: ResponseContext
    ) -> str:
        """Format as plain text for CLI and simple contexts."""
        result = []

        # Add title if present
        if content.title:
            result.append(f"# {content.title}")
            result.append("")

        # Main message
        result.append(content.message)

        # Add sections
        for section in content.sections:
            result.append("")
            if section.get("title"):
                result.append(f"## {section['title']}")
            if section.get("content"):
                result.append(section["content"])

        return "\n".join(result)

    def _format_markdown(
        self, content: ResponseContent, context: ResponseContext
    ) -> str:
        """Format as Markdown for web UI."""
        result = []

        # Add title
        if content.title:
            result.append(f"# {content.title}")
            result.append("")

        # Add summary if different from title
        if content.summary and content.summary != content.title:
            result.append(f"**{content.summary}**")
            result.append("")

        # Main message with markdown formatting
        result.append(content.message)

        # Add sections with proper markdown
        for section in content.sections:
            result.append("")
            if section.get("title"):
                result.append(f"## {section['title']}")
            if section.get("content"):
                result.append(section["content"])

        # Add metadata if present
        if content.metadata and context.supports_rich_formatting:
            result.append("")
            result.append("---")
            result.append("**Metadata:**")
            for key, value in content.metadata.items():
                result.append(f"- **{key}**: {value}")

        return "\n".join(result)

    def _format_json(self, content: ResponseContent, context: ResponseContext) -> str:
        """Format as JSON for API and webhook contexts."""
        response_data = {
            "message": content.message,
            "timestamp": context.metadata.get("timestamp"),
            "agent": context.agent_name,
        }

        # Add optional fields if present
        if content.title:
            response_data["title"] = content.title
        if content.summary:
            response_data["summary"] = content.summary
        if content.severity:
            response_data["severity"] = content.severity
        if content.category:
            response_data["category"] = content.category
        if content.tags:
            response_data["tags"] = content.tags
        if content.sections:
            response_data["sections"] = content.sections
        if content.metadata:
            response_data["metadata"] = content.metadata

        # Add context information
        if context.user_id:
            response_data["user_id"] = context.user_id
        if context.session_id:
            response_data["session_id"] = context.session_id
        if context.conversation_id:
            response_data["conversation_id"] = context.conversation_id

        return json.dumps(response_data, indent=2)

    def _format_slack_blocks(
        self, content: ResponseContent, context: ResponseContext
    ) -> str:
        """Format as Slack Block Kit JSON."""
        blocks = []

        # Title block
        if content.title:
            blocks.append(
                {
                    "type": "header",
                    "text": {"type": "plain_text", "text": content.title},
                }
            )

        # Main message block
        blocks.append(
            {"type": "section", "text": {"type": "mrkdwn", "text": content.message}}
        )

        # Sections as additional blocks
        for section in content.sections:
            if section.get("title") and section.get("content"):
                blocks.append(
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*{section['title']}*\n{section['content']}",
                        },
                    }
                )

        # Context block with metadata
        context_elements = []
        if content.severity:
            context_elements.append(f"Severity: {content.severity}")
        if content.category:
            context_elements.append(f"Category: {content.category}")
        if context.agent_name:
            context_elements.append(f"Agent: {context.agent_name}")

        if context_elements:
            blocks.append(
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": " | ".join(context_elements)}
                    ],
                }
            )

        return json.dumps({"blocks": blocks}, indent=2)

    def _format_html(self, content: ResponseContent, context: ResponseContext) -> str:
        """Format as HTML for email notifications."""
        html_parts = []

        # HTML structure start
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html><head><meta charset='utf-8'></head><body>")

        # Title
        if content.title:
            html_parts.append(f"<h1>{content.title}</h1>")

        # Summary
        if content.summary and content.summary != content.title:
            html_parts.append(f"<p><strong>{content.summary}</strong></p>")

        # Main message
        message_html = content.message.replace("\n", "<br>")
        html_parts.append(f"<p>{message_html}</p>")

        # Sections
        for section in content.sections:
            if section.get("title"):
                html_parts.append(f"<h2>{section['title']}</h2>")
            if section.get("content"):
                section_html = section["content"].replace("\n", "<br>")
                html_parts.append(f"<p>{section_html}</p>")

        # Metadata table
        if content.metadata and context.supports_rich_formatting:
            html_parts.append("<h3>Details</h3>")
            html_parts.append("<table border='1' cellpadding='5'>")
            for key, value in content.metadata.items():
                html_parts.append(
                    f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>"
                )
            html_parts.append("</table>")

        # Footer with agent info
        if context.agent_name:
            html_parts.append(f"<hr><p><small>Sent by {context.agent_name}</small></p>")

        html_parts.append("</body></html>")

        return "\n".join(html_parts)


class ResponseManager:
    """Manages multi-channel responses and notifications."""

    def __init__(self):
        self.formatter = ResponseFormatter()

    async def send_response(
        self, content: Union[str, ResponseContent], context: ResponseContext, agent=None
    ) -> Dict[str, Any]:
        """Send response to primary channel and optional notification channels."""

        # Convert string content to ResponseContent if needed
        if isinstance(content, str):
            content = ResponseContent(message=content)

        results = {}

        # Send primary response
        primary_response = self.formatter.format_content(content, context)
        results["primary"] = {
            "channel": context.primary_channel.value,
            "format": context.preferred_format.value,
            "content": primary_response,
            "success": True,
        }

        # Send notifications if configured and agent is available
        notification_results = []
        if (
            context.should_send_notifications()
            and agent
            and hasattr(agent, "destination_resolver")
        ):
            for destination_name in context.notification_channels:
                try:
                    # Create notification context
                    notification_context = context.clone_for_notification(
                        destination_name
                    )

                    # Format content for notification
                    notification_content = self.formatter.format_content(
                        content, notification_context
                    )

                    # Prepare notification context data
                    notify_context = {}
                    if content.severity:
                        notify_context["severity"] = content.severity
                    if content.category:
                        notify_context["category"] = content.category
                    if content.tags:
                        notify_context["tags"] = content.tags
                    if content.metadata:
                        notify_context["metadata"] = content.metadata
                    if context.user_id:
                        notify_context["user_id"] = context.user_id
                    if context.session_id:
                        notify_context["session_id"] = context.session_id

                    # Send notification
                    result = await agent.destination_resolver.send(
                        notification_content,
                        destination_type=destination_name,
                        context=notify_context,
                    )

                    notification_results.append(
                        {
                            "destination": destination_name,
                            "format": notification_context.preferred_format.value,
                            "success": result.success,
                            "delivery_time": result.delivery_time,
                            "error": (
                                result.error_message if not result.success else None
                            ),
                        }
                    )

                except Exception as e:
                    notification_results.append(
                        {
                            "destination": destination_name,
                            "success": False,
                            "error": str(e),
                        }
                    )

        if notification_results:
            results["notifications"] = notification_results

        return results


# Context management functions
def set_response_context(context: ResponseContext):
    """Set the current response context."""
    _response_context_var.set(context)


def get_response_context() -> Optional[ResponseContext]:
    """Get the current response context."""
    return _response_context_var.get()


def clear_response_context():
    """Clear the current response context."""
    _response_context_var.set(None)


# Convenience functions for creating contexts
def create_cli_context(
    agent_name: Optional[str] = None, notification_channels: List[str] = None
) -> ResponseContext:
    """Create context for CLI interactions."""
    return ResponseContext(
        primary_channel=ResponseChannel.CLI,
        notification_channels=notification_channels or [],
        supports_rich_formatting=False,
        supports_interactive_elements=False,
        agent_name=agent_name,
    )


def create_web_ui_context(
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    notification_channels: List[str] = None,
) -> ResponseContext:
    """Create context for web UI interactions."""
    return ResponseContext(
        primary_channel=ResponseChannel.WEB_UI,
        notification_channels=notification_channels or [],
        supports_rich_formatting=True,
        supports_interactive_elements=True,
        user_id=user_id,
        session_id=session_id,
        conversation_id=conversation_id,
        agent_name=agent_name,
    )


def create_api_context(
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    agent_name: Optional[str] = None,
    notification_channels: List[str] = None,
) -> ResponseContext:
    """Create context for API interactions."""
    return ResponseContext(
        primary_channel=ResponseChannel.API,
        notification_channels=notification_channels or [],
        supports_rich_formatting=False,
        supports_interactive_elements=False,
        user_id=user_id,
        conversation_id=conversation_id,
        agent_name=agent_name,
    )
