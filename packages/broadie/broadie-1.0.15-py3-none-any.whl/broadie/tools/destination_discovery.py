"""
Streamlined destination discovery and tool management for agents.

This module analyzes agent configuration to automatically determine:
- Which destinations are enabled and their targets
- What notification tools should be available 
- How to route different message types
- Channel/target validation and recommendations
"""

from typing import Dict, List, Optional, Set, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class DestinationDiscovery:
    """Discovers and manages destination configuration for agents."""
    
    def __init__(self, agent_config: Dict[str, Any]):
        """
        Initialize destination discovery from agent config.
        
        Args:
            agent_config: Full agent configuration including destinations
        """
        self.agent_name = agent_config.get("name", "unknown")
        self.destinations_config = agent_config.get("destinations", {})
        
        # Analyze configuration
        self._enabled_destinations = self._discover_enabled_destinations()
        self._available_targets = self._discover_targets()
        self._recommended_tools = self._determine_recommended_tools()
    
    def _discover_enabled_destinations(self) -> Dict[str, Dict[str, Any]]:
        """Discover which destinations are enabled."""
        enabled = {}
        
        for dest_name, dest_config in self.destinations_config.items():
            if dest_config.get("enabled", False):
                enabled[dest_name] = dest_config
                logger.info(f"Agent {self.agent_name}: Discovered enabled destination '{dest_name}' -> {dest_config.get('target')}")
        
        return enabled
    
    def _discover_targets(self) -> Dict[str, List[str]]:
        """Discover all available targets grouped by destination type."""
        targets = {}
        
        for dest_name, dest_config in self._enabled_destinations.items():
            dest_type = dest_config.get("type", "unknown")
            target = dest_config.get("target")
            
            if dest_type not in targets:
                targets[dest_type] = []
            
            # Handle multi-target destinations
            if dest_type == "multi" and isinstance(target, list):
                for multi_target in target:
                    if isinstance(multi_target, dict):
                        multi_type = multi_target.get("type", "unknown") 
                        multi_target_val = multi_target.get("target")
                        if multi_target_val:
                            if multi_type not in targets:
                                targets[multi_type] = []
                            targets[multi_type].append(multi_target_val)
            else:
                if target:
                    targets[dest_type].append(target)
        
        return targets
    
    def _determine_recommended_tools(self) -> Set[str]:
        """Determine which notification tools should be available based on config."""
        tools = set()
        
        # Always include basic notification tools if any destination is enabled
        if self._enabled_destinations:
            tools.update([
                "send_notification",
                "list_enabled_destinations", 
                "get_destination_info"
            ])
        
        # Add destination-specific tools based on enabled destinations
        for dest_name, dest_config in self._enabled_destinations.items():
            dest_type = dest_config.get("type")
            
            if dest_type == "slack":
                tools.update([
                    "send_slack_message",
                    "send_slack_dm", 
                    "list_slack_channels",
                    "post_analysis_results"  # Common for analysis agents
                ])
            elif dest_type == "multi":
                # Multi destinations often need broadcasting
                tools.add("broadcast_message")
                # Check component types
                target = dest_config.get("target", [])
                if isinstance(target, list):
                    for component in target:
                        if isinstance(component, dict) and component.get("type") == "slack":
                            tools.update([
                                "send_slack_message",
                                "post_analysis_results"
                            ])
        
        # Add escalation/alert tools based on enabled destinations
        if "alerts" in self._enabled_destinations:
            tools.add("send_alert")
        
        if "escalation" in self._enabled_destinations:
            tools.add("escalate_issue")
        
        return tools
    
    def get_discovery_summary(self) -> Dict[str, Any]:
        """Get comprehensive discovery summary."""
        return {
            "agent_name": self.agent_name,
            "enabled_destinations": list(self._enabled_destinations.keys()),
            "available_targets": self._available_targets,
            "recommended_tools": sorted(list(self._recommended_tools)),
            "destination_details": self._enabled_destinations,
            "primary_target": self.get_primary_target(),
            "supports_alerts": "alerts" in self._enabled_destinations,
            "supports_escalation": "escalation" in self._enabled_destinations,
            "multi_destination_support": any(
                dest.get("type") == "multi" 
                for dest in self._enabled_destinations.values()
            )
        }
    
    def get_primary_target(self) -> Optional[str]:
        """Get the primary target for notifications."""
        primary_config = self._enabled_destinations.get("primary")
        if primary_config:
            return primary_config.get("target")
        return None
    
    def get_enabled_channels(self) -> List[str]:
        """Get list of all enabled Slack channels."""
        channels = []
        
        for dest_config in self._enabled_destinations.values():
            target = dest_config.get("target")
            dest_type = dest_config.get("type")
            
            if dest_type == "slack" and target:
                # Normalize channel name (remove # if present)
                channel = target.lstrip("#")
                if channel not in channels:
                    channels.append(channel)
            elif dest_type == "multi" and isinstance(target, list):
                for component in target:
                    if isinstance(component, dict) and component.get("type") == "slack":
                        comp_target = component.get("target", "").lstrip("#")
                        if comp_target and comp_target not in channels:
                            channels.append(comp_target)
        
        return channels
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate destination configuration and provide recommendations."""
        issues = []
        recommendations = []
        warnings = []
        
        # Check if any destinations are enabled
        if not self._enabled_destinations:
            issues.append("No destinations are enabled - agent cannot send notifications")
            recommendations.append("Enable at least the 'primary' destination")
        
        # Validate Slack channel names
        for dest_name, dest_config in self._enabled_destinations.items():
            target = dest_config.get("target")
            dest_type = dest_config.get("type")
            
            if dest_type == "slack" and target:
                if not target.startswith("#"):
                    warnings.append(f"Slack target '{target}' in '{dest_name}' should start with #")
        
        # Check for recommended destinations for security agents
        if "phish" in self.agent_name.lower() or "security" in self.agent_name.lower():
            if "alerts" not in self._enabled_destinations:
                recommendations.append("Security agents should consider enabling 'alerts' destination")
            if "escalation" not in self._enabled_destinations:
                recommendations.append("Security agents should consider enabling 'escalation' destination")
        
        # Check for disabled but configured destinations
        disabled_destinations = []
        for dest_name, dest_config in self.destinations_config.items():
            if not dest_config.get("enabled", False):
                disabled_destinations.append(dest_name)
        
        if disabled_destinations:
            warnings.append(f"Disabled destinations available: {', '.join(disabled_destinations)}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings, 
            "recommendations": recommendations,
            "disabled_destinations": disabled_destinations
        }
    
    def get_routing_guide(self) -> Dict[str, str]:
        """Get guidance on which destination to use for different message types."""
        guide = {}
        
        if "primary" in self._enabled_destinations:
            guide["general_notifications"] = "primary"
            guide["analysis_results"] = "primary"
            guide["status_updates"] = "primary"
        
        if "alerts" in self._enabled_destinations:
            guide["security_alerts"] = "alerts"
            guide["system_alerts"] = "alerts"
            guide["urgent_notifications"] = "alerts"
        
        if "escalation" in self._enabled_destinations:
            guide["critical_issues"] = "escalation"
            guide["manual_intervention_needed"] = "escalation"
            guide["business_critical_problems"] = "escalation"
        
        if "notifications" in self._enabled_destinations:
            guide["broadcast_announcements"] = "notifications"
            guide["team_wide_updates"] = "notifications"
        
        return guide


def discover_agent_destinations(agent_config: Dict[str, Any]) -> DestinationDiscovery:
    """
    Convenience function to create destination discovery from agent config.
    
    Args:
        agent_config: Agent configuration dictionary
        
    Returns:
        DestinationDiscovery instance with analysis results
    """
    return DestinationDiscovery(agent_config)


def get_recommended_notification_tools(agent_config: Dict[str, Any]) -> List[str]:
    """
    Get list of recommended notification tools based on agent configuration.
    
    Args:
        agent_config: Agent configuration dictionary
        
    Returns:
        List of recommended tool names
    """
    discovery = discover_agent_destinations(agent_config)
    return sorted(list(discovery._recommended_tools))


def validate_agent_destinations(agent_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate agent destination configuration.
    
    Args:
        agent_config: Agent configuration dictionary
        
    Returns:
        Validation results with issues, warnings, and recommendations
    """
    discovery = discover_agent_destinations(agent_config)
    return discovery.validate_configuration()