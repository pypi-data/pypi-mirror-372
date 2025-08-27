"""
Broadie Destinations System

This module provides a comprehensive notification and response routing system
for Broadie agents, supporting multi-target broadcasting, webhooks, and 
environment-based configuration management.
"""

from .models import (
    DestinationConfig,
    AgentDestinations,
    NotificationContext,
    DeliveryResult,
    BroadcastResult
)
from .resolver import DestinationResolver
from .handlers.base import BaseDestinationHandler

__all__ = [
    'DestinationConfig',
    'AgentDestinations', 
    'NotificationContext',
    'DeliveryResult',
    'BroadcastResult',
    'DestinationResolver',
    'BaseDestinationHandler'
]