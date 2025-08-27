"""
Destination handlers for the Broadie notification system.

This package contains handlers for different types of destinations
including Slack, Email, Webhooks, and Multi-target broadcasting.
"""

from .base import BaseDestinationHandler
from .slack import SlackDestinationHandler
from .email import EmailDestinationHandler
from .webhook import WebhookDestinationHandler
from .multi import MultiDestinationHandler

__all__ = [
    'BaseDestinationHandler',
    'SlackDestinationHandler', 
    'EmailDestinationHandler',
    'WebhookDestinationHandler',
    'MultiDestinationHandler'
]