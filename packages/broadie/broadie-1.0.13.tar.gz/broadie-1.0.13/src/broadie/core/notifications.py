"""
Notification tools leveraging the destination system for multi-target messaging.

These tools provide a unified interface for sending notifications, alerts, and
messages through the comprehensive destination system with support for Slack, 
email, webhooks, and multi-destination broadcasting.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional, Union
from langchain_core.tools import tool

from broadie.utils.exceptions import ToolError
from broadie.core.destinations.models import SeverityLevel


# Context variables for accessing agent destination resolver
_current_agent_context = None


def set_agent_context(agent):
    """Set the current agent context for notification tools."""
    global _current_agent_context
    _current_agent_context = agent


def get_agent_context():
    """Get the current agent context."""
    return _current_agent_context


def _create_contextual_response_content(message: str, **context_data) -> 'ResponseContent':
    """Create ResponseContent with context-aware formatting hints."""
    from broadie.core.response_context import ResponseContent
    
    return ResponseContent(
        message=message,
        severity=context_data.get('severity'),
        category=context_data.get('category'),
        tags=context_data.get('tags', []),
        metadata=context_data.get('metadata'),
        title=context_data.get('title'),
        summary=context_data.get('summary')
    )


async def _send_contextual_response(
    content_or_message: Union[str, 'ResponseContent'],
    destination_type: str = "primary",
    **context_data
) -> str:
    """Send a contextual response that formats appropriately for the current context."""
    from broadie.core.response_context import (
        get_response_context, ResponseContent, ResponseChannel
    )
    
    agent = get_agent_context()
    if not agent:
        return "Error: No agent context available"
    
    current_context = get_response_context()
    if not current_context:
        # Fallback to basic notification if no context set
        if not hasattr(agent, 'destination_resolver'):
            return "Error: Agent does not have destination system configured"
        
        try:
            result = await agent.destination_resolver.send(
                str(content_or_message), 
                destination_type=destination_type, 
                context=context_data
            )
            
            if result.success:
                return f"Message sent successfully to {result.destination_name} ({result.destination_type})"
            else:
                return f"Failed to send message: {result.error_message}"
        except Exception as e:
            return f"Error sending message: {str(e)}"
    
    # Handle context-aware response with dual/tri channel support
    try:
        # Create ResponseContent if we got a string
        if isinstance(content_or_message, str):
            content = _create_contextual_response_content(content_or_message, **context_data)
        else:
            content = content_or_message
        
        # Use the response manager for context-aware formatting
        if hasattr(agent, 'response_manager'):
            results = await agent.response_manager.send_response(content, current_context, agent)
            
            # Format results for tool response
            if current_context.primary_channel == ResponseChannel.CLI:
                # For CLI, show simple success message
                primary_result = results.get('primary', {})
                response_parts = []
                if primary_result.get('success'):
                    response_parts.append("Response delivered to CLI")
                else:
                    response_parts.append("CLI response failed")
                
                # Show notification results if any
                notifications = results.get('notifications', [])
                if notifications:
                    successful_notifications = sum(1 for n in notifications if n.get('success'))
                    total_notifications = len(notifications)
                    response_parts.append(f"Notifications: {successful_notifications}/{total_notifications} delivered")
                    
                    for notification in notifications:
                        status = "✅" if notification.get('success') else "❌"
                        response_parts.append(f"  {status} {notification.get('destination')}")
                
                return " | ".join(response_parts)
            
            elif current_context.primary_channel in [ResponseChannel.API, ResponseChannel.WEB_UI]:
                # For API/Web UI, return JSON-style summary
                return json.dumps({
                    "status": "success",
                    "primary_channel": current_context.primary_channel.value,
                    "format": current_context.preferred_format.value,
                    "notifications_sent": len(results.get('notifications', [])),
                    "results": results
                }, indent=2)
            
            else:
                # Fallback response
                return f"Response sent via {current_context.primary_channel.value}"
        
        else:
            # Fallback to basic destination resolver
            result = await agent.destination_resolver.send(
                str(content.message), 
                destination_type=destination_type, 
                context=context_data
            )
            
            return f"Message sent to {result.destination_name}" if result.success else f"Failed: {result.error_message}"
            
    except Exception as e:
        return f"Error sending contextual response: {str(e)}"


@tool(description="""Send a notification message to the agent's primary destination.
This is the main notification method for routine communications and updates.

Example usage:
- send_notification("Task completed successfully")  
- send_notification("Processing 500 records", category="progress")
- send_notification("User login detected", tags=["security", "auth"])

Supports rich context including severity, tags, categories, and metadata.""")
async def send_notification(
    message: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Send a notification to the primary destination.
    
    Args:
        message: The notification message
        severity: Message severity (info, low, medium, high, critical)
        category: Notification category (status, progress, completion, etc.)
        tags: Tags for categorization (string or list)
        metadata: Additional metadata dictionary
        user_id: Associated user ID
        session_id: Associated session ID
        
    Returns:
        Success message with delivery details
    """
    agent = get_agent_context()
    if not agent:
        return "Error: No agent context available for notifications"
    
    if not hasattr(agent, 'destination_resolver'):
        return "Error: Agent does not have destination system configured"
    
    try:
        return await _send_contextual_response(
            message,
            destination_type="primary",
            severity=severity,
            category=category,
            tags=tags if isinstance(tags, list) else [tags] if tags else [],
            metadata=metadata,
            user_id=user_id,
            session_id=session_id
        )
    except Exception as e:
        raise ToolError(f"Error sending notification: {str(e)}")


@tool(description="""Send an alert message to the agent's alerts destination for high-priority issues.
Automatically sets severity to 'critical' and is designed for urgent notifications.

Example usage:
- send_alert("Database connection failed")
- send_alert("Security breach detected", tags=["security", "urgent"])
- send_alert("System overload - CPU at 95%", category="performance")

Perfect for: system errors, security issues, performance problems, urgent notifications.""")
async def send_alert(
    message: str,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Send an alert to the alerts destination.
    
    Args:
        message: The alert message
        category: Alert category (security, performance, system, etc.)
        tags: Tags for categorization
        metadata: Additional metadata
        user_id: Associated user ID
        session_id: Associated session ID
        
    Returns:
        Success message with delivery details
    """
    agent = get_agent_context()
    if not agent:
        return "Error: No agent context available for alerts"
    
    if not hasattr(agent, 'destination_resolver'):
        return "Error: Agent does not have destination system configured"
    
    try:
        return await _send_contextual_response(
            message,
            destination_type="alerts",
            severity="critical",  # Alerts are always critical
            category=category,
            tags=tags if isinstance(tags, list) else [tags] if tags else [],
            metadata=metadata,
            user_id=user_id,
            session_id=session_id
        )
    except Exception as e:
        raise ToolError(f"Error sending alert: {str(e)}")


@tool(description="""Escalate an issue to the agent's escalation destination for urgent attention.
Sets severity to 'high' and is designed for issues requiring immediate human intervention.

Example usage:
- escalate_issue("Unable to complete user request - requires manual intervention")
- escalate_issue("Payment processing error affecting multiple users", category="business-critical")
- escalate_issue("API rate limit exceeded - service degraded", tags=["api", "performance"])

Perfect for: unresolvable issues, business-critical problems, manual intervention needed.""")
async def escalate_issue(
    message: str,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> str:
    """
    Escalate an issue to the escalation destination.
    
    Args:
        message: The escalation message
        category: Issue category (business-critical, technical, user-facing, etc.)
        tags: Tags for categorization
        metadata: Additional metadata
        user_id: Associated user ID
        session_id: Associated session ID
        
    Returns:
        Success message with delivery details
    """
    agent = get_agent_context()
    if not agent:
        return "Error: No agent context available for escalation"
    
    if not hasattr(agent, 'destination_resolver'):
        return "Error: Agent does not have destination system configured"
    
    try:
        return await _send_contextual_response(
            message,
            destination_type="escalation",
            severity="high",  # Escalations are high priority
            category=category,
            tags=tags if isinstance(tags, list) else [tags] if tags else [],
            metadata=metadata,
            user_id=user_id,
            session_id=session_id
        )
    except Exception as e:
        raise ToolError(f"Error escalating issue: {str(e)}")


@tool(description="""Broadcast a message to multiple destinations simultaneously for wide distribution.
Perfect for important announcements, status updates, or critical information that needs multiple channels.

Example usage:
- broadcast_message("System maintenance completed", ["primary", "notifications"])
- broadcast_message("Critical security update deployed", ["alerts", "escalation", "notifications"])
- broadcast_message("New feature released", ["primary", "notifications"], category="announcement")

All destinations receive the message concurrently with comprehensive delivery reporting.""")
async def broadcast_message(
    message: str,
    destinations: List[str],
    severity: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Broadcast a message to multiple destinations.
    
    Args:
        message: The message to broadcast
        destinations: List of destination names to broadcast to
        severity: Message severity level
        category: Message category
        tags: Tags for categorization
        metadata: Additional metadata
        
    Returns:
        Broadcast results with delivery statistics
    """
    agent = get_agent_context()
    if not agent:
        return "Error: No agent context available for broadcasting"
    
    if not hasattr(agent, 'destination_resolver'):
        return "Error: Agent does not have destination system configured"
    
    if not destinations:
        return "Error: No destinations specified for broadcast"
    
    try:
        context = {}
        if severity:
            context['severity'] = severity
        if category:
            context['category'] = category
        if tags:
            context['tags'] = tags if isinstance(tags, list) else [tags]
        if metadata:
            context['metadata'] = metadata
        
        result = await agent.destination_resolver.broadcast(
            message, 
            destinations, 
            context=context
        )
        
        # Format comprehensive results
        output = f"Broadcast completed to {len(destinations)} destinations:\n"
        output += f"✅ Successful: {result.successful_deliveries}\n"
        output += f"❌ Failed: {result.failed_deliveries}\n"
        output += f"⏱️ Total time: {result.total_time:.2f}s\n\n"
        
        # Individual results
        output += "Individual Results:\n"
        for delivery_result in result.results:
            status = "✅" if delivery_result.success else "❌"
            output += f"{status} {delivery_result.destination_name} ({delivery_result.destination_type})"
            if delivery_result.success:
                output += f" - {delivery_result.delivery_time:.2f}s"
            else:
                output += f" - {delivery_result.error_message}"
            output += "\n"
        
        return output.strip()
        
    except Exception as e:
        raise ToolError(f"Error broadcasting message: {str(e)}")


# Add placeholder implementations for other tools
@tool(description="Send a status update to the notifications destination.")
async def send_status_update(message: str, **kwargs) -> str:
    return await send_notification(message, severity="info", category="status", **kwargs)


@tool(description="Test connectivity to all configured destinations.")
async def test_notification_destinations() -> str:
    agent = get_agent_context()
    if not agent or not hasattr(agent, 'destination_resolver'):
        return "Error: No destination system available"
    
    results = await agent.destination_resolver.test_destinations()
    output = f"Tested {len(results)} destinations:\n"
    for name, success in results.items():
        status = "✅" if success else "❌"
        output += f"{status} {name}\n"
    return output


@tool(description="Get information about all configured destinations.")
async def get_destination_info() -> str:
    agent = get_agent_context()
    if not agent or not hasattr(agent, 'destination_resolver'):
        return "Error: No destination system available"
    
    info = agent.destination_resolver.get_destination_info()
    return f"Agent: {info['agent_name']}\nDestinations: {', '.join(info['available_destinations'])}"


@tool(description="Send message to specific destination.")
async def send_to_destination(destination_name: str, message: str, **kwargs) -> str:
    return await _send_contextual_response(message, destination_type=destination_name, **kwargs)