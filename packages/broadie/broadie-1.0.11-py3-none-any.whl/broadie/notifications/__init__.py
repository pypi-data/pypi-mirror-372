"""
Notification system for Broadie agents.
Supports Slack integration for alerts, summaries, and external notifications.
"""

from .slack import SlackNotifier

__all__ = ['SlackNotifier']