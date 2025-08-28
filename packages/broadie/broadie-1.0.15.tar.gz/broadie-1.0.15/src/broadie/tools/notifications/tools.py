"""
Notification tools leveraging the destination system for multi-target messaging.

These tools provide a unified interface for sending notifications, alerts, and
messages through the comprehensive destination system with support for Slack,
email, webhooks, and multi-destination broadcasting.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union

from langchain_core.tools import tool

from broadie.core.destinations.models import SeverityLevel
from broadie.utils.exceptions import ToolError

# Context variables for accessing agent destination resolver
_current_agent_context = None


def set_agent_context(agent):
    """Set the current agent context for notification tools."""
    global _current_agent_context
    _current_agent_context = agent


def get_agent_context():
    """Get the current agent context."""
    return _current_agent_context


def _create_contextual_response_content(
    message: str, **context_data
) -> "ResponseContent":
    """Create ResponseContent with context-aware formatting hints."""
    from broadie.core.response_context import ResponseContent

    return ResponseContent(
        message=message,
        severity=context_data.get("severity"),
        category=context_data.get("category"),
        tags=context_data.get("tags", []),
        metadata=context_data.get("metadata"),
        title=context_data.get("title"),
        summary=context_data.get("summary"),
    )


async def _send_contextual_response(
    content_or_message: Union[str, "ResponseContent"],
    destination_type: str = "primary",
    **context_data,
) -> str:
    """Send a contextual response that formats appropriately for the current context."""
    from broadie.core.response_context import (
        ResponseChannel,
        ResponseContent,
        get_response_context,
    )

    agent = get_agent_context()
    if not agent:
        return "Error: No agent context available"

    # Check if destination is enabled before sending
    if hasattr(agent, "destination_resolver"):
        if not agent.destination_resolver.has_destination(destination_type):
            available_destinations = agent.destination_resolver.list_destinations()
            return f"Destination '{destination_type}' not configured. Available: {', '.join(available_destinations)}"

        # Get destination config to check if it's enabled
        destination_config = agent.destination_resolver.destinations.get_destination(
            destination_type
        )
        if destination_config and not destination_config.enabled:
            return f"Destination '{destination_type}' is disabled in configuration"

    current_context = get_response_context()
    if not current_context:
        # Fallback to basic notification if no context set
        if not hasattr(agent, "destination_resolver"):
            return "Error: Agent does not have destination system configured"

        try:
            result = await agent.destination_resolver.send(
                str(content_or_message),
                destination_type=destination_type,
                context=context_data,
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
            content = _create_contextual_response_content(
                content_or_message, **context_data
            )
        else:
            content = content_or_message

        # Use the response manager for context-aware formatting
        if hasattr(agent, "response_manager"):
            results = await agent.response_manager.send_response(
                content, current_context, agent
            )

            # Format results for tool response
            if current_context.primary_channel == ResponseChannel.CLI:
                # For CLI, show simple success message
                primary_result = results.get("primary", {})
                response_parts = []
                if primary_result.get("success"):
                    response_parts.append("Response delivered to CLI")
                else:
                    response_parts.append("CLI response failed")

                # Show notification results if any
                notifications = results.get("notifications", [])
                if notifications:
                    successful_notifications = sum(
                        1 for n in notifications if n.get("success")
                    )
                    total_notifications = len(notifications)
                    response_parts.append(
                        f"Notifications: {successful_notifications}/{total_notifications} delivered"
                    )

                    for notification in notifications:
                        status = "✅" if notification.get("success") else "❌"
                        response_parts.append(
                            f"  {status} {notification.get('destination')}"
                        )

                return " | ".join(response_parts)

            elif current_context.primary_channel in [
                ResponseChannel.API,
                ResponseChannel.WEB_UI,
            ]:
                # For API/Web UI, return JSON-style summary
                return json.dumps(
                    {
                        "status": "success",
                        "primary_channel": current_context.primary_channel.value,
                        "format": current_context.preferred_format.value,
                        "notifications_sent": len(results.get("notifications", [])),
                        "results": results,
                    },
                    indent=2,
                )

            else:
                # Fallback response
                return f"Response sent via {current_context.primary_channel.value}"

        else:
            # Fallback to basic destination resolver
            result = await agent.destination_resolver.send(
                str(content.message),
                destination_type=destination_type,
                context=context_data,
            )

            return (
                f"Message sent to {result.destination_name}"
                if result.success
                else f"Failed: {result.error_message}"
            )

    except Exception as e:
        return f"Error sending contextual response: {str(e)}"


@tool(
    description="""Send a notification message to the agent's primary destination.
This is the main notification method for routine communications and updates.

Example usage:
- send_notification("Task completed successfully")  
- send_notification("Processing 500 records", category="progress")
- send_notification("User login detected", tags=["security", "auth"])

Supports rich context including severity, tags, categories, and metadata."""
)
async def send_notification(
    message: str,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
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

    if not hasattr(agent, "destination_resolver"):
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
            session_id=session_id,
        )
    except Exception as e:
        raise ToolError(f"Error sending notification: {str(e)}")


@tool(
    description="""Send an alert message to the agent's alerts destination for high-priority issues.
Automatically sets severity to 'critical' and is designed for urgent notifications.

Example usage:
- send_alert("Database connection failed")
- send_alert("Security breach detected", tags=["security", "urgent"])
- send_alert("System overload - CPU at 95%", category="performance")

Perfect for: system errors, security issues, performance problems, urgent notifications."""
)
async def send_alert(
    message: str,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
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

    if not hasattr(agent, "destination_resolver"):
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
            session_id=session_id,
        )
    except Exception as e:
        raise ToolError(f"Error sending alert: {str(e)}")


@tool(
    description="""Escalate an issue to the agent's escalation destination for urgent attention.
Sets severity to 'high' and is designed for issues requiring immediate human intervention.

Example usage:
- escalate_issue("Unable to complete user request - requires manual intervention")
- escalate_issue("Payment processing error affecting multiple users", category="business-critical")
- escalate_issue("API rate limit exceeded - service degraded", tags=["api", "performance"])

Perfect for: unresolvable issues, business-critical problems, manual intervention needed."""
)
async def escalate_issue(
    message: str,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
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

    if not hasattr(agent, "destination_resolver"):
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
            session_id=session_id,
        )
    except Exception as e:
        raise ToolError(f"Error escalating issue: {str(e)}")


@tool(
    description="""Broadcast a message to multiple destinations simultaneously for wide distribution.
Perfect for important announcements, status updates, or critical information that needs multiple channels.

Example usage:
- broadcast_message("System maintenance completed", ["primary", "notifications"])
- broadcast_message("Critical security update deployed", ["alerts", "escalation", "notifications"])
- broadcast_message("New feature released", ["primary", "notifications"], category="announcement")

All destinations receive the message concurrently with comprehensive delivery reporting."""
)
async def broadcast_message(
    message: str,
    destinations: List[str],
    severity: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[Union[str, List[str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
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

    if not hasattr(agent, "destination_resolver"):
        return "Error: Agent does not have destination system configured"

    if not destinations:
        return "Error: No destinations specified for broadcast"

    try:
        context = {}
        if severity:
            context["severity"] = severity
        if category:
            context["category"] = category
        if tags:
            context["tags"] = tags if isinstance(tags, list) else [tags]
        if metadata:
            context["metadata"] = metadata

        result = await agent.destination_resolver.broadcast(
            message, destinations, context=context
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
    return await send_notification(
        message, severity="info", category="status", **kwargs
    )


@tool(description="Test connectivity to all configured destinations.")
async def test_notification_destinations() -> str:
    agent = get_agent_context()
    if not agent or not hasattr(agent, "destination_resolver"):
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
    if not agent or not hasattr(agent, "destination_resolver"):
        return "Error: No destination system available"

    info = agent.destination_resolver.get_destination_info()
    return f"Agent: {info['agent_name']}\nDestinations: {', '.join(info['available_destinations'])}"


@tool(description="Send message to specific destination.")
async def send_to_destination(destination_name: str, message: str, **kwargs) -> str:
    return await _send_contextual_response(
        message, destination_type=destination_name, **kwargs
    )


@tool(
    description="""Post analysis results to the agent's primary destination (typically configured Slack channel).
This is the main tool for posting final results, analysis, or outputs to the designated channel.

Example usage:
- post_analysis_results("Phishing analysis complete: Risk Score 85/100")
- post_analysis_results("Task completed successfully", category="completion")

Uses the agent's primary destination configuration and respects enabled/disabled settings."""
)
async def post_analysis_results(
    message: str,
    title: Optional[str] = None,
    category: Optional[str] = "analysis",
    severity: Optional[str] = "info",
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Post analysis results to the agent's primary destination.

    Args:
        message: The main result/analysis message
        title: Optional title for the analysis
        category: Category of the analysis (defaults to "analysis")
        severity: Severity level (info, low, medium, high, critical)
        tags: Optional tags for categorization
        metadata: Additional metadata to include

    Returns:
        Success message with delivery details
    """
    # Merge optional title into the message to avoid passing unsupported kwargs to tools
    combined_message = f"{title}\n\n{message}" if title else message
    return await _send_contextual_response(
        combined_message,
        destination_type="primary",
        category=category,
        severity=severity,
        tags=tags or [],
        metadata=metadata,
    )


@tool(
    description="""Get comprehensive destination discovery and configuration analysis for this agent.
Shows enabled channels, available tools, routing guidance, and configuration validation.

Perfect for understanding agent capabilities and troubleshooting notification issues."""
)
async def list_enabled_destinations() -> str:
    """Get comprehensive destination analysis and recommendations."""
    agent = get_agent_context()
    if not agent or not hasattr(agent, "destination_resolver"):
        return "No destination system configured"

    # Import here to avoid circular imports
    from ..destination_discovery import discover_agent_destinations
    
    # Get agent configuration for analysis
    agent_config = {
        "name": agent.name,
        "destinations": agent.config.destinations if hasattr(agent.config, 'destinations') else {}
    }
    
    discovery = discover_agent_destinations(agent_config)
    summary = discovery.get_discovery_summary()
    validation = discovery.validate_configuration()
    routing_guide = discovery.get_routing_guide()
    
    # Format comprehensive output
    result = f"🤖 Agent: {summary['agent_name']}\n"
    result += "=" * 50 + "\n\n"
    
    # Enabled destinations
    result += f"📡 ENABLED DESTINATIONS ({len(summary['enabled_destinations'])}):\n"
    if summary['enabled_destinations']:
        for dest_name in summary['enabled_destinations']:
            dest_details = summary['destination_details'][dest_name]
            target = dest_details.get('target', 'No target')
            dest_type = dest_details.get('type', 'unknown')
            result += f"  ✅ {dest_name}: {dest_type} -> {target}\n"
        
        # Primary target highlight
        if summary['primary_target']:
            result += f"\n🎯 Primary Target: {summary['primary_target']}\n"
    else:
        result += "  ❌ No destinations enabled\n"
    
    # Available channels
    channels = discovery.get_enabled_channels()
    if channels:
        result += f"\n📢 SLACK CHANNELS ({len(channels)}):\n"
        for channel in channels:
            result += f"  • #{channel}\n"
    
    # Recommended tools
    if summary['recommended_tools']:
        result += f"\n🛠️ RECOMMENDED TOOLS ({len(summary['recommended_tools'])}):\n"
        for tool in summary['recommended_tools'][:8]:  # Show first 8
            result += f"  • {tool}\n"
        if len(summary['recommended_tools']) > 8:
            result += f"  ... and {len(summary['recommended_tools']) - 8} more\n"
    
    # Routing guidance
    if routing_guide:
        result += "\n🗺️ MESSAGE ROUTING GUIDE:\n"
        for message_type, destination in routing_guide.items():
            result += f"  • {message_type.replace('_', ' ').title()}: → {destination}\n"
    
    # Validation results
    if not validation['valid'] or validation['warnings'] or validation['recommendations']:
        result += "\n⚠️ CONFIGURATION ANALYSIS:\n"
        
        for issue in validation['issues']:
            result += f"  ❌ Issue: {issue}\n"
        
        for warning in validation['warnings']:
            result += f"  ⚠️ Warning: {warning}\n"
        
        for rec in validation['recommendations']:
            result += f"  💡 Recommendation: {rec}\n"
        
        if validation['disabled_destinations']:
            result += f"  🔒 Disabled but available: {', '.join(validation['disabled_destinations'])}\n"
    
    # Capabilities summary
    capabilities = []
    if summary['supports_alerts']:
        capabilities.append("🚨 Alerts")
    if summary['supports_escalation']:
        capabilities.append("⬆️ Escalation")
    if summary['multi_destination_support']:
        capabilities.append("📡 Broadcasting")
    
    if capabilities:
        result += f"\n✨ CAPABILITIES: {' | '.join(capabilities)}\n"
    
    return result.strip()


@tool(
    description="""Discover and validate agent destination configuration with actionable recommendations.
Analyzes the agent's notification setup and provides guidance on optimal tool usage.

Returns validation results and setup recommendations."""
)
async def discover_agent_destinations() -> str:
    """Analyze agent configuration and provide destination discovery insights."""
    agent = get_agent_context()
    if not agent:
        return "No agent context available"
    
    # Import here to avoid circular imports
    from ..destination_discovery import discover_agent_destinations
    
    # Get agent configuration for analysis
    agent_config = {
        "name": agent.name,
        "destinations": agent.config.destinations if hasattr(agent.config, 'destinations') else {}
    }
    
    discovery = discover_agent_destinations(agent_config)
    summary = discovery.get_discovery_summary()
    
    result = f"🔍 DESTINATION DISCOVERY: {summary['agent_name']}\n"
    result += "=" * 50 + "\n\n"
    
    # Quick stats
    result += f"📊 CONFIGURATION OVERVIEW:\n"
    result += f"  • Enabled destinations: {len(summary['enabled_destinations'])}\n"
    result += f"  • Available targets: {sum(len(targets) for targets in summary['available_targets'].values())}\n"
    result += f"  • Recommended tools: {len(summary['recommended_tools'])}\n"
    result += f"  • Primary target: {summary['primary_target'] or 'Not configured'}\n\n"
    
    # Target breakdown
    if summary['available_targets']:
        result += "🎯 TARGET BREAKDOWN:\n"
        for target_type, targets in summary['available_targets'].items():
            result += f"  • {target_type}: {', '.join(targets)}\n"
        result += "\n"
    
    # Tool recommendations with reasoning
    result += f"🛠️ TOOL RECOMMENDATIONS:\n"
    tool_categories = {
        'Core': ['send_notification', 'get_destination_info', 'list_enabled_destinations'],
        'Slack': ['send_slack_message', 'post_analysis_results', 'send_slack_dm'],
        'Alerts': ['send_alert', 'escalate_issue'],
        'Broadcasting': ['broadcast_message']
    }
    
    recommended = set(summary['recommended_tools'])
    for category, tools in tool_categories.items():
        category_tools = [tool for tool in tools if tool in recommended]
        if category_tools:
            result += f"  📂 {category}: {', '.join(category_tools)}\n"
    
    return result.strip()
