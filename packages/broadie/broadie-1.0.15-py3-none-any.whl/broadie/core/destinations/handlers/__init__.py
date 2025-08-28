"""
Destination handlers for the Broadie notification system.

This package contains handlers for different types of destinations
including Slack, Email, Webhooks, and Multi-target broadcasting.
"""

from .base import BaseDestinationHandler
from .email import EmailDestinationHandler
from .multi import MultiDestinationHandler
from .slack import SlackDestinationHandler
from .webhook import WebhookDestinationHandler

__all__ = [
    "BaseDestinationHandler",
    "SlackDestinationHandler",
    "EmailDestinationHandler",
    "WebhookDestinationHandler",
    "MultiDestinationHandler",
]
