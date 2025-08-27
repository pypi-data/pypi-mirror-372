"""
Slack destination handler.

This handler integrates with the existing Slack tools to send notifications
to Slack channels and users with support for rich formatting, threads, and mentions.
"""

from typing import Dict, Any, Optional, List
import json
from ..models import DestinationConfig, NotificationContext
from .base import BaseDestinationHandler
from ...integrations.slack import _get_slack_client, send_slack_message, send_slack_dm


class SlackDestinationHandler(BaseDestinationHandler):
    """Handler for Slack destinations."""
    
    async def send_message(self, message: str, context: NotificationContext) -> Dict[str, Any]:
        """Send message to Slack channel or user."""
        target = self.config.target
        settings = self.config.settings
        
        # Format the message
        formatted_message = self.format_message(message, context)
        
        try:
            # Determine if this is a DM or channel message
            if target.startswith('@') or '@' in target:
                # Direct message
                username = target.lstrip('@')
                result = send_slack_dm(
                    username=username,
                    text=formatted_message['text'],
                    blocks=formatted_message.get('blocks')
                )
            else:
                # Channel message
                channel = target.lstrip('#')
                result = send_slack_message(
                    channel=channel,
                    text=formatted_message['text'],
                    thread_ts=settings.get('thread_ts'),
                    mention_users=settings.get('mention_users', []),
                    mention_channel=settings.get('mention_channel', False),
                    blocks=formatted_message.get('blocks')
                )
            
            return {
                'status': 'success',
                'result': result,
                'target': target,
                'formatted_message': formatted_message
            }
            
        except Exception as e:
            # Re-raise for retry logic in base handler
            raise Exception(f"Failed to send Slack message to {target}: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test Slack connection."""
        try:
            client = _get_slack_client()
            auth_result = client.auth_test()
            return auth_result.get('ok', False)
        except Exception:
            return False
    
    def format_message(self, message: str, context: NotificationContext) -> Dict[str, Any]:
        """Format message for Slack with optional rich formatting."""
        settings = self.config.settings
        
        # Basic formatting
        formatted = {'text': message}
        
        # Add context information if enabled
        if settings.get('include_context', False):
            context_info = []
            
            if context.severity:
                severity_emoji = self._get_severity_emoji(context.severity)
                context_info.append(f"{severity_emoji} *Severity:* {context.severity}")
            
            if context.tags:
                context_info.append(f"*Tags:* {', '.join(context.tags)}")
            
            if context.agent_name:
                context_info.append(f"*Agent:* {context.agent_name}")
                
            if context_info:
                formatted['text'] = f"{message}\n\n_" + " | ".join(context_info) + "_"
        
        # Rich formatting with blocks
        if settings.get('format') == 'rich' or settings.get('use_blocks', False):
            formatted['blocks'] = self._create_rich_blocks(message, context, settings)
        
        # Add emoji reactions if specified
        if settings.get('add_reactions'):
            formatted['reactions'] = settings['add_reactions']
        
        return formatted
    
    def _create_rich_blocks(self, message: str, context: NotificationContext, settings: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create Slack Block Kit blocks for rich formatting."""
        blocks = []
        
        # Header block with severity indicator
        if context.severity:
            severity_emoji = self._get_severity_emoji(context.severity)
            header_text = f"{severity_emoji} {context.severity.upper()} Alert"
            
            blocks.append({
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": header_text
                }
            })
        
        # Main message block
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message
            }
        })
        
        # Context block with metadata
        context_elements = []
        
        if context.agent_name:
            context_elements.append({
                "type": "mrkdwn",
                "text": f"*Agent:* {context.agent_name}"
            })
        
        if context.tags:
            context_elements.append({
                "type": "mrkdwn", 
                "text": f"*Tags:* {', '.join(context.tags)}"
            })
        
        if context.timestamp:
            context_elements.append({
                "type": "mrkdwn",
                "text": f"*Time:* {context.timestamp}"
            })
        
        if context_elements:
            blocks.append({
                "type": "context",
                "elements": context_elements
            })
        
        # Add action buttons if specified
        if settings.get('actions'):
            action_elements = []
            for action in settings['actions']:
                action_elements.append({
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": action['text']
                    },
                    "value": action.get('value', action['text']),
                    "action_id": action.get('action_id', f"action_{action['text'].lower()}")
                })
            
            if action_elements:
                blocks.append({
                    "type": "actions",
                    "elements": action_elements
                })
        
        # Add divider if there are multiple blocks
        if len(blocks) > 1:
            blocks.insert(-1, {"type": "divider"})
        
        return blocks
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get appropriate emoji for severity level."""
        severity_emojis = {
            'low': '🔵',
            'medium': '🟡', 
            'high': '🟠',
            'critical': '🔴'
        }
        return severity_emojis.get(severity.lower(), '⚪')
    
    def get_handler_info(self) -> Dict[str, Any]:
        """Get Slack-specific handler information."""
        info = super().get_handler_info()
        info.update({
            'supports_threads': True,
            'supports_mentions': True,
            'supports_rich_formatting': True,
            'supports_blocks': True,
            'target_type': 'dm' if (self.config.target.startswith('@') or '@' in self.config.target) else 'channel'
        })
        return info