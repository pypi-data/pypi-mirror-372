"""
Multi-destination notification tools.

Provides unified notification system with context-aware delivery:
- Primary notifications and alerts
- Multi-destination broadcasting
- Escalation and status updates
- Destination management and testing
"""

from .tools import (
    broadcast_message,
    escalate_issue,
    get_agent_context,
    get_destination_info,
    list_enabled_destinations,
    post_analysis_results,
    send_alert,
    send_notification,
    send_status_update,
    send_to_destination,
    set_agent_context,
    test_notification_destinations,
)

__all__ = [
    "send_notification",
    "send_alert",
    "escalate_issue",
    "broadcast_message",
    "send_status_update",
    "test_notification_destinations",
    "get_destination_info",
    "send_to_destination",
    "post_analysis_results",
    "list_enabled_destinations",
    "set_agent_context",
    "get_agent_context",
]
