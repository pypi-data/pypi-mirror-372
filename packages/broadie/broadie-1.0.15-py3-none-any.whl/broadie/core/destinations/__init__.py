"""
Broadie Destinations System

This module provides a comprehensive notification and response routing system
for Broadie agents, supporting multi-target broadcasting, webhooks, and
environment-based configuration management.
"""

from .handlers.base import BaseDestinationHandler
from .models import (
    AgentDestinations,
    BroadcastResult,
    DeliveryResult,
    DestinationConfig,
    NotificationContext,
)
from .resolver import DestinationResolver

__all__ = [
    "DestinationConfig",
    "AgentDestinations",
    "NotificationContext",
    "DeliveryResult",
    "BroadcastResult",
    "DestinationResolver",
    "BaseDestinationHandler",
]
