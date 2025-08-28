"""
Core models for the Broadie destinations system.

This module defines the data structures used for configuring and managing
agent response destinations including validation, serialization, and
type safety.
"""

import re
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, validator


class DestinationType(str, Enum):
    """Supported destination types."""

    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"
    MULTI = "multi"
    TEAMS = "teams"


class SeverityLevel(str, Enum):
    """Message severity levels for conditional routing."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DestinationConfig(BaseModel):
    """Configuration for a single destination."""

    type: DestinationType = Field(..., description="Type of destination")
    target: Union[str, List[str], List[Dict[str, Any]]] = Field(
        ..., description="Target identifier (channel, email, URL, etc.)"
    )
    settings: Dict[str, Any] = Field(
        default_factory=dict, description="Destination-specific settings"
    )
    enabled: bool = Field(
        default=True, description="Whether this destination is enabled"
    )
    conditions: Optional[Dict[str, Any]] = Field(
        default=None, description="Conditional routing rules"
    )

    # Retry and timeout settings
    timeout: int = Field(
        default=30, ge=1, le=300, description="Request timeout in seconds"
    )
    retry_attempts: int = Field(
        default=3, ge=1, le=10, description="Number of retry attempts"
    )
    retry_backoff: float = Field(
        default=2.0, ge=1.0, le=10.0, description="Exponential backoff multiplier"
    )

    @validator("target")
    def validate_target(cls, v, values):
        """Validate target based on destination type."""
        dest_type = values.get("type")

        if dest_type == DestinationType.SLACK:
            if isinstance(v, str):
                if not (v.startswith("#") or v.startswith("@") or "@" in v):
                    raise ValueError(
                        "Slack target must be a channel (#channel) or user (@user or email)"
                    )

        elif dest_type == DestinationType.EMAIL:
            if isinstance(v, str):
                email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(email_pattern, v):
                    raise ValueError("Email target must be a valid email address")

        elif dest_type == DestinationType.WEBHOOK:
            if isinstance(v, str):
                if not v.startswith(("http://", "https://")):
                    raise ValueError("Webhook target must be a valid HTTP/HTTPS URL")

        elif dest_type == DestinationType.MULTI:
            # For multi destinations, target can be a list of dictionaries
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        # Validate that each dictionary has required fields
                        if "type" not in item or "target" not in item:
                            raise ValueError(
                                "Multi-destination items must have 'type' and 'target' fields"
                            )

        return v

    @validator("conditions")
    def validate_conditions(cls, v):
        """Validate conditional routing rules."""
        if v is None:
            return v

        # Validate severity conditions
        if "severity" in v:
            severity_rule = v["severity"]
            if isinstance(severity_rule, str):
                # Support patterns like ">=high", "==critical", "medium"
                if severity_rule.startswith((">=", "<=", "==", ">", "<")):
                    operator = (
                        severity_rule[:2]
                        if severity_rule.startswith((">=", "<=", "=="))
                        else severity_rule[0]
                    )
                    level = severity_rule[len(operator) :]
                    if level not in [s.value for s in SeverityLevel]:
                        raise ValueError(f"Invalid severity level: {level}")
                elif severity_rule not in [s.value for s in SeverityLevel]:
                    raise ValueError(f"Invalid severity condition: {severity_rule}")

        # Validate tag conditions
        if "tags" in v:
            tags = v["tags"]
            if not isinstance(tags, list) or not all(
                isinstance(tag, str) for tag in tags
            ):
                raise ValueError("Tags condition must be a list of strings")

        return v

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
        extra = "forbid"  # Prevent additional fields


class AgentDestinations(BaseModel):
    """Complete destination configuration for an agent."""

    # Standard destination types
    primary: Optional[DestinationConfig] = Field(
        default=None, description="Primary response destination"
    )
    escalation: Optional[DestinationConfig] = Field(
        default=None, description="Escalation destination"
    )
    notifications: Optional[DestinationConfig] = Field(
        default=None, description="General notifications"
    )
    alerts: Optional[DestinationConfig] = Field(
        default=None, description="Alert-specific destination"
    )
    fallback: Optional[DestinationConfig] = Field(
        default=None, description="Fallback when others fail"
    )

    # Custom named destinations
    custom: Dict[str, DestinationConfig] = Field(
        default_factory=dict, description="Custom destination configurations"
    )

    # Global settings
    default_timeout: int = Field(
        default=30, ge=1, le=300, description="Default timeout for all destinations"
    )
    retry_attempts: int = Field(
        default=3, ge=1, le=10, description="Default retry attempts"
    )
    enable_fallback: bool = Field(
        default=True, description="Enable automatic fallback on failures"
    )

    def get_destination(self, name: str) -> Optional[DestinationConfig]:
        """Get a destination by name, checking both standard and custom destinations."""
        # Check standard destinations first
        standard_destinations = {
            "primary": self.primary,
            "escalation": self.escalation,
            "notifications": self.notifications,
            "alerts": self.alerts,
            "fallback": self.fallback,
        }

        if name in standard_destinations:
            return standard_destinations[name]

        # Check custom destinations
        return self.custom.get(name)

    def list_destinations(self) -> List[str]:
        """List all available destination names."""
        destinations = []

        # Add enabled standard destinations
        for name, config in [
            ("primary", self.primary),
            ("escalation", self.escalation),
            ("notifications", self.notifications),
            ("alerts", self.alerts),
            ("fallback", self.fallback),
        ]:
            if config and config.enabled:
                destinations.append(name)

        # Add enabled custom destinations
        for name, config in self.custom.items():
            if config.enabled:
                destinations.append(name)

        return destinations

    class Config:
        """Pydantic configuration."""

        extra = "forbid"


class NotificationContext(BaseModel):
    """Context information for notifications and conditional routing."""

    # Message metadata
    severity: Optional[SeverityLevel] = Field(
        default=None, description="Message severity level"
    )
    tags: List[str] = Field(
        default_factory=list, description="Message tags for routing"
    )
    category: Optional[str] = Field(default=None, description="Message category")

    # Agent context
    agent_name: str = Field(..., description="Name of the sending agent")
    agent_type: Optional[str] = Field(
        default=None, description="Type/role of the agent"
    )

    # Additional metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional context metadata"
    )
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")

    # Request context
    thread_id: Optional[str] = Field(default=None, description="Conversation thread ID")
    user_id: Optional[str] = Field(default=None, description="User ID if applicable")
    session_id: Optional[str] = Field(
        default=None, description="Session ID if applicable"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class DeliveryResult(BaseModel):
    """Result of delivering a message to a single destination."""

    destination_name: str = Field(..., description="Name of the destination")
    destination_type: DestinationType = Field(..., description="Type of destination")
    success: bool = Field(..., description="Whether delivery was successful")

    # Response details
    response_data: Optional[Dict[str, Any]] = Field(
        default=None, description="Response data from destination"
    )
    error_message: Optional[str] = Field(
        default=None, description="Error message if delivery failed"
    )
    error_code: Optional[str] = Field(
        default=None, description="Error code if applicable"
    )

    # Timing information
    delivery_time: Optional[float] = Field(
        default=None, description="Time taken for delivery in seconds"
    )
    attempts: int = Field(default=1, description="Number of delivery attempts made")

    # Status information
    status_code: Optional[int] = Field(
        default=None, description="HTTP status code for webhook destinations"
    )

    class Config:
        """Pydantic configuration."""

        use_enum_values = True


class BroadcastResult(BaseModel):
    """Result of broadcasting a message to multiple destinations."""

    message: str = Field(..., description="The message that was broadcast")
    destinations: List[str] = Field(..., description="List of destination names")
    context: NotificationContext = Field(
        ..., description="Context used for the broadcast"
    )

    # Results
    results: List[DeliveryResult] = Field(
        ..., description="Individual delivery results"
    )
    successful_deliveries: int = Field(
        ..., description="Number of successful deliveries"
    )
    failed_deliveries: int = Field(..., description="Number of failed deliveries")

    # Overall status
    overall_success: bool = Field(
        ..., description="Whether at least one delivery succeeded"
    )
    total_time: Optional[float] = Field(
        default=None, description="Total time for all deliveries"
    )

    def get_successful_destinations(self) -> List[str]:
        """Get list of destinations that were successfully delivered to."""
        return [result.destination_name for result in self.results if result.success]

    def get_failed_destinations(self) -> List[str]:
        """Get list of destinations that failed delivery."""
        return [
            result.destination_name for result in self.results if not result.success
        ]

    def get_errors(self) -> Dict[str, str]:
        """Get mapping of destination names to error messages for failed deliveries."""
        return {
            result.destination_name: result.error_message or "Unknown error"
            for result in self.results
            if not result.success and result.error_message
        }

    class Config:
        """Pydantic configuration."""

        use_enum_values = True
