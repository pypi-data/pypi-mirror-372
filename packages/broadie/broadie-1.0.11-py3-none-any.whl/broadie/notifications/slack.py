"""
Slack notification integration for Broadie agents.
"""

import json
import asyncio
from typing import Optional, Dict, Any, List
from datetime import datetime
import aiohttp

from broadie.config.settings import BroadieSettings
from broadie.utils.exceptions import NotificationError
from broadie.utils.logging import get_logger

logger = get_logger(__name__)


class SlackNotifier:
    """
    Slack notification client for sending alerts, summaries, and messages.
    
    Supports both Bot Token API and Webhook URL methods.
    """
    
    def __init__(self, settings: Optional[BroadieSettings] = None):
        self.settings = settings or BroadieSettings()
        self.bot_token = self.settings.slack_bot_token
        self.webhook_url = self.settings.slack_webhook_url
        self.default_channel = self.settings.slack_channel
        
        if not self.bot_token and not self.webhook_url:
            logger.warning("No Slack bot token or webhook URL configured. Notifications will be disabled.")
    
    async def send_message(
        self,
        message: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Send a message to Slack.
        
        Args:
            message: The message text
            channel: Channel to send to (defaults to configured channel)
            username: Bot username (for webhook mode)
            icon_emoji: Bot icon emoji (for webhook mode)
            attachments: Message attachments (legacy format)
            blocks: Rich message blocks (modern format)
            
        Returns:
            True if message was sent successfully
        """
        if not self.bot_token and not self.webhook_url:
            logger.warning("No Slack configuration available")
            return False
        
        channel = channel or self.default_channel
        if not channel:
            logger.error("No Slack channel specified")
            return False
        
        try:
            if self.bot_token:
                return await self._send_via_bot_token(
                    message=message,
                    channel=channel,
                    attachments=attachments,
                    blocks=blocks
                )
            else:
                return await self._send_via_webhook(
                    message=message,
                    channel=channel,
                    username=username,
                    icon_emoji=icon_emoji,
                    attachments=attachments,
                    blocks=blocks
                )
        except Exception as e:
            logger.error(f"Failed to send Slack message: {e}")
            raise NotificationError(f"Slack notification failed: {e}") from e
    
    async def _send_via_bot_token(
        self,
        message: str,
        channel: str,
        attachments: Optional[List[Dict[str, Any]]] = None,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send message using Slack Bot Token API."""
        url = "https://slack.com/api/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {self.bot_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel,
            "text": message
        }
        
        if attachments:
            payload["attachments"] = attachments
        if blocks:
            payload["blocks"] = blocks
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("ok"):
                        logger.info(f"Slack message sent to {channel}")
                        return True
                    else:
                        logger.error(f"Slack API error: {result.get('error', 'Unknown error')}")
                        return False
                else:
                    logger.error(f"Slack API request failed with status {response.status}")
                    return False
    
    async def _send_via_webhook(
        self,
        message: str,
        channel: str,
        username: Optional[str] = None,
        icon_emoji: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        blocks: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send message using Slack Webhook URL."""
        payload = {
            "text": message,
            "channel": channel
        }
        
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if attachments:
            payload["attachments"] = attachments
        if blocks:
            payload["blocks"] = blocks
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.webhook_url, json=payload) as response:
                if response.status == 200:
                    logger.info(f"Slack webhook message sent to {channel}")
                    return True
                else:
                    logger.error(f"Slack webhook request failed with status {response.status}")
                    return False
    
    async def send_alert(
        self,
        title: str,
        message: str,
        level: str = "info",
        channel: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> bool:
        """
        Send a formatted alert message.
        
        Args:
            title: Alert title
            message: Alert message
            level: Alert level (info, warning, error, critical)
            channel: Channel to send to
            agent_name: Name of the agent sending the alert
            
        Returns:
            True if alert was sent successfully
        """
        # Color mapping for alert levels
        color_map = {
            "info": "#36a64f",      # Green
            "warning": "#ff9500",   # Orange  
            "error": "#ff0000",     # Red
            "critical": "#8b0000"   # Dark red
        }
        
        color = color_map.get(level.lower(), "#36a64f")
        
        # Create rich attachment
        attachment = {
            "color": color,
            "title": title,
            "text": message,
            "footer": f"Broadie Agent{f' - {agent_name}' if agent_name else ''}",
            "ts": int(datetime.now().timestamp())
        }
        
        alert_message = f"🚨 *{level.upper()}*: {title}"
        
        return await self.send_message(
            message=alert_message,
            channel=channel,
            attachments=[attachment]
        )
    
    async def send_summary(
        self,
        title: str,
        summary_data: Dict[str, Any],
        channel: Optional[str] = None,
        agent_name: Optional[str] = None
    ) -> bool:
        """
        Send a formatted summary message.
        
        Args:
            title: Summary title
            summary_data: Dictionary of summary data
            channel: Channel to send to
            agent_name: Name of the agent sending the summary
            
        Returns:
            True if summary was sent successfully
        """
        # Format summary data
        fields = []
        for key, value in summary_data.items():
            fields.append({
                "title": key.replace("_", " ").title(),
                "value": str(value),
                "short": len(str(value)) < 20
            })
        
        attachment = {
            "color": "#36a64f",
            "title": title,
            "fields": fields,
            "footer": f"Broadie Agent{f' - {agent_name}' if agent_name else ''}",
            "ts": int(datetime.now().timestamp())
        }
        
        summary_message = f"📊 *Summary*: {title}"
        
        return await self.send_message(
            message=summary_message,
            channel=channel,
            attachments=[attachment]
        )
    
    async def send_agent_status(
        self,
        agent_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        channel: Optional[str] = None
    ) -> bool:
        """
        Send agent status update.
        
        Args:
            agent_name: Name of the agent
            status: Status message (e.g., "online", "offline", "busy")
            details: Optional status details
            channel: Channel to send to
            
        Returns:
            True if status was sent successfully
        """
        status_icons = {
            "online": "🟢",
            "offline": "🔴", 
            "busy": "🟡",
            "error": "❌",
            "warning": "⚠️"
        }
        
        icon = status_icons.get(status.lower(), "ℹ️")
        message = f"{icon} Agent **{agent_name}** is now *{status}*"
        
        if details:
            fields = []
            for key, value in details.items():
                fields.append({
                    "title": key.replace("_", " ").title(),
                    "value": str(value),
                    "short": True
                })
            
            attachment = {
                "color": "#36a64f" if status == "online" else "#ff9500",
                "fields": fields,
                "footer": f"Broadie Agent - {agent_name}",
                "ts": int(datetime.now().timestamp())
            }
            
            return await self.send_message(
                message=message,
                channel=channel,
                attachments=[attachment]
            )
        else:
            return await self.send_message(message, channel)
    
    def is_configured(self) -> bool:
        """Check if Slack notifications are properly configured."""
        return bool(self.bot_token or self.webhook_url)


# Convenience functions for easy usage
_global_notifier: Optional[SlackNotifier] = None

def get_slack_notifier() -> SlackNotifier:
    """Get the global Slack notifier instance."""
    global _global_notifier
    if _global_notifier is None:
        _global_notifier = SlackNotifier()
    return _global_notifier

async def notify_slack(
    message: str,
    channel: Optional[str] = None,
    level: str = "info"
) -> bool:
    """
    Quick function to send a Slack notification.
    
    Args:
        message: Message to send
        channel: Channel to send to
        level: Message level (for formatting)
        
    Returns:
        True if message was sent successfully
    """
    notifier = get_slack_notifier()
    if not notifier.is_configured():
        logger.warning("Slack notifications not configured")
        return False
    
    if level in ["warning", "error", "critical"]:
        return await notifier.send_alert(
            title=f"{level.title()} Notification",
            message=message,
            level=level,
            channel=channel
        )
    else:
        return await notifier.send_message(message, channel)

async def notify_agent_status(
    agent_name: str,
    status: str,
    details: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Quick function to send agent status update.
    
    Args:
        agent_name: Name of the agent
        status: Status message
        details: Optional status details
        
    Returns:
        True if status was sent successfully
    """
    notifier = get_slack_notifier()
    if not notifier.is_configured():
        return False
    
    return await notifier.send_agent_status(agent_name, status, details)