"""
Renderer components for converting agent envelopes to destination-specific formats.
Builds on existing notification tools while providing specialized rendering capabilities.
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from broadie.core.destinations.models import DestinationType

logger = logging.getLogger(__name__)


class BaseRenderer(ABC):
    """Base class for all renderer components."""
    
    def __init__(self, destination_type: DestinationType):
        self.destination_type = destination_type
    
    @abstractmethod
    def render(self, envelope: Dict[str, Any]) -> Any:
        """Render envelope for specific destination type."""
        pass
    
    def get_renderer_info(self) -> Dict[str, Any]:
        """Get information about this renderer."""
        return {
            "type": self.__class__.__name__,
            "destination_type": self.destination_type.value if hasattr(self.destination_type, 'value') else str(self.destination_type)
        }


class SlackRenderer(BaseRenderer):
    """Renderer for Slack destinations using existing slack tools."""
    
    def __init__(self):
        super().__init__(DestinationType.SLACK)
    
    def render(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Render envelope as Slack Block Kit JSON."""
        try:
            # Try to import slack tools to reuse their formatting logic
            # If not available, fall back to our own implementation
            # from broadie.tools.slack.tools import format_slack_blocks
            
            payload = envelope.get("payload", {})
            agent_name = envelope.get("agent", "Agent")
            timestamp = envelope.get("timestamp", "")
            metadata = envelope.get("metadata", {})
            
            # Create Block Kit structure based on payload content
            blocks = []
            
            # Header block with agent name and status
            tier_label = metadata.get("tier_label", "INFO")
            status_emoji = self._get_status_emoji(tier_label)
            header_text = f"{status_emoji} {agent_name} Response ({tier_label})"
            
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text
                }
            })
            
            # Process payload into readable format
            if "raw_output" in payload:
                # Simple raw output
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{payload['raw_output']}```"
                    }
                })
            else:
                # Structured payload - format each field
                for key, value in payload.items():
                    if isinstance(value, (dict, list)):
                        formatted_value = f"```{json.dumps(value, indent=2)}```"
                    else:
                        formatted_value = str(value)
                    
                    blocks.append({
                        "type": "section",
                        "text": {
                            "type": "mrkdwn", 
                            "text": f"*{key.replace('_', ' ').title()}:*\n{formatted_value}"
                        }
                    })
            
            # Add timestamp context
            if timestamp:
                blocks.append({
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"🕒 Generated at {timestamp}"
                        }
                    ]
                })
            
            return {"blocks": blocks}
            
        except Exception as e:
            logger.error(f"SlackRenderer failed: {e}")
            # Fallback to generic slack rendering
            return SlackGenericRenderer().render(envelope)
    
    def _get_status_emoji(self, tier_label: str) -> str:
        """Get appropriate emoji for tier label."""
        emoji_map = {
            "CRITICAL": ":rotating_light:",
            "HIGH": ":warning:",
            "MEDIUM": ":large_yellow_circle:",
            "LOW": ":information_source:",
            "INFORMATIONAL": ":white_check_mark:"
        }
        return emoji_map.get(tier_label.upper(), ":speech_balloon:")


class EmailRenderer(BaseRenderer):
    """Renderer for email destinations using existing email tools."""
    
    def __init__(self):
        super().__init__(DestinationType.EMAIL)
    
    def render(self, envelope: Dict[str, Any]) -> Dict[str, str]:
        """Render envelope as email content (HTML and text)."""
        payload = envelope.get("payload", {})
        agent_name = envelope.get("agent", "Agent")
        timestamp = envelope.get("timestamp", "")
        metadata = envelope.get("metadata", {})
        
        # Create subject line
        tier_label = metadata.get("tier_label", "INFO")
        subject = f"[{tier_label}] {agent_name} Response"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body>
            <h2>{agent_name} Response</h2>
            <p><strong>Status:</strong> {tier_label}</p>
            <p><strong>Generated:</strong> {timestamp}</p>
            <hr>
        """
        
        # Add payload content
        if "raw_output" in payload:
            html_content += f"<pre>{payload['raw_output']}</pre>"
        else:
            for key, value in payload.items():
                html_content += f"<h3>{key.replace('_', ' ').title()}</h3>"
                if isinstance(value, (dict, list)):
                    html_content += f"<pre>{json.dumps(value, indent=2)}</pre>"
                else:
                    html_content += f"<p>{value}</p>"
        
        html_content += """
        </body>
        </html>
        """
        
        # Create text content
        text_content = f"{agent_name} Response\n"
        text_content += f"Status: {tier_label}\n"
        text_content += f"Generated: {timestamp}\n"
        text_content += "-" * 50 + "\n\n"
        
        if "raw_output" in payload:
            text_content += payload["raw_output"]
        else:
            for key, value in payload.items():
                text_content += f"{key.replace('_', ' ').title()}:\n"
                if isinstance(value, (dict, list)):
                    text_content += json.dumps(value, indent=2) + "\n\n"
                else:
                    text_content += f"{value}\n\n"
        
        return {
            "subject": subject,
            "html": html_content,
            "text": text_content
        }


class MarkdownRenderer(BaseRenderer):
    """Renderer for web/markdown contexts."""
    
    def __init__(self):
        super().__init__("markdown")
    
    def render(self, envelope: Dict[str, Any]) -> str:
        """Render envelope as Markdown."""
        payload = envelope.get("payload", {})
        agent_name = envelope.get("agent", "Agent")
        timestamp = envelope.get("timestamp", "")
        metadata = envelope.get("metadata", {})
        
        # Create markdown content
        tier_label = metadata.get("tier_label", "INFO")
        markdown = f"# {agent_name} Response\n\n"
        markdown += f"**Status:** {tier_label}  \n"
        markdown += f"**Generated:** {timestamp}\n\n"
        markdown += "---\n\n"
        
        # Add payload content
        if "raw_output" in payload:
            markdown += f"```\n{payload['raw_output']}\n```\n"
        else:
            for key, value in payload.items():
                markdown += f"## {key.replace('_', ' ').title()}\n\n"
                if isinstance(value, (dict, list)):
                    markdown += f"```json\n{json.dumps(value, indent=2)}\n```\n\n"
                else:
                    markdown += f"{value}\n\n"
        
        return markdown


# Generic fallback renderers
class SlackGenericRenderer:
    """Generic fallback renderer for Slack."""
    
    def render(self, envelope: Dict[str, Any]) -> Dict[str, Any]:
        """Render envelope as generic Slack blocks."""
        agent_name = envelope.get("agent", "Agent")
        code_content = json.dumps(envelope, ensure_ascii=False, indent=2)
        
        return {
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"📋 {agent_name} Result"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"```{code_content}```"
                    }
                }
            ]
        }


class EmailGenericRenderer:
    """Generic fallback renderer for Email."""
    
    def render(self, envelope: Dict[str, Any]) -> Dict[str, str]:
        """Render envelope as generic email."""
        agent_name = envelope.get("agent", "Agent")
        content = json.dumps(envelope, ensure_ascii=False, indent=2)
        
        return {
            "subject": f"{agent_name} Response",
            "html": f"<h2>{agent_name} Result</h2><pre>{content}</pre>",
            "text": f"{agent_name} Result\n\n{content}"
        }


class MarkdownGenericRenderer:
    """Generic fallback renderer for Markdown."""
    
    def render(self, envelope: Dict[str, Any]) -> str:
        """Render envelope as generic markdown."""
        agent_name = envelope.get("agent", "Agent")
        content = json.dumps(envelope, ensure_ascii=False, indent=2)
        return f"# {agent_name} Result\n\n```json\n{content}\n```"


class RendererFactory:
    """Factory for creating appropriate renderers."""
    
    _renderers = {
        DestinationType.SLACK: SlackRenderer,
        DestinationType.EMAIL: EmailRenderer,
        "markdown": MarkdownRenderer,
        "api": lambda: None  # API returns raw envelope
    }
    
    _fallback_renderers = {
        DestinationType.SLACK: SlackGenericRenderer,
        DestinationType.EMAIL: EmailGenericRenderer,
        "markdown": MarkdownGenericRenderer,
    }
    
    @classmethod
    def create_renderer(cls, destination_type: str) -> Optional[BaseRenderer]:
        """Create appropriate renderer for destination type."""
        renderer_class = cls._renderers.get(destination_type)
        if renderer_class and renderer_class is not None:
            return renderer_class()
        return None
    
    @classmethod
    def create_fallback_renderer(cls, destination_type: str):
        """Create fallback renderer for destination type."""
        fallback_class = cls._fallback_renderers.get(destination_type)
        if fallback_class:
            return fallback_class()
        return MarkdownGenericRenderer()  # Ultimate fallback