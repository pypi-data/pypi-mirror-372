"""
Destination resolver for managing agent response destinations.

This module provides centralized destination management with support for
environment variable overrides, configuration resolution, and comprehensive
error handling.
"""

import asyncio
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

from .handlers import (
    BaseDestinationHandler,
    EmailDestinationHandler,
    MultiDestinationHandler,
    SlackDestinationHandler,
    WebhookDestinationHandler,
)
from .models import (
    AgentDestinations,
    BroadcastResult,
    DeliveryResult,
    DestinationConfig,
    DestinationType,
    NotificationContext,
    SeverityLevel,
)

logger = logging.getLogger(__name__)


class DestinationResolver:
    """Central system for resolving and managing agent destinations."""

    def __init__(self, agent_name: str, config: Dict[str, Any]):
        """
        Initialize destination resolver.

        Args:
            agent_name: Name of the agent
            config: Agent configuration dictionary
        """
        self.agent_name = agent_name
        self.raw_config = config
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{agent_name}")

        # Resolve destinations from config + environment overrides
        self.destinations = self._resolve_destinations()

        # Initialize handlers for resolved destinations
        self.handlers: Dict[str, BaseDestinationHandler] = {}
        self._initialize_handlers()

    def _resolve_destinations(self) -> AgentDestinations:
        """Resolve destinations from configuration and environment variables."""
        # Extract destinations from agent config
        destinations_config = self.raw_config.get("destinations", {})

        # Apply environment variable overrides
        destinations_config = self._apply_environment_overrides(destinations_config)

        # Apply global defaults
        destinations_config = self._apply_global_defaults(destinations_config)

        # Create and validate AgentDestinations object
        try:
            return AgentDestinations(**destinations_config)
        except Exception as e:
            self.logger.error(f"Failed to parse destinations configuration: {e}")
            # Return empty destinations configuration
            return AgentDestinations()

    def _apply_environment_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to destination configuration."""
        # Environment variable pattern: BROADIE_{AGENT_NAME}_{DESTINATION}_{SETTING}
        agent_prefix = f"BROADIE_{self.agent_name.upper().replace('-', '_')}_"

        # Standard destination names to check
        standard_destinations = [
            "PRIMARY",
            "ESCALATION",
            "NOTIFICATIONS",
            "ALERTS",
            "FALLBACK",
        ]

        for dest_name in standard_destinations:
            dest_key = dest_name.lower()
            env_prefix = f"{agent_prefix}{dest_name}_"

            # Check for destination-specific overrides
            overrides = {}

            # Target override
            target_env = f"{env_prefix}TARGET"
            if os.getenv(target_env):
                overrides["target"] = os.getenv(target_env)

            # Type override
            type_env = f"{env_prefix}TYPE"
            if os.getenv(type_env):
                overrides["type"] = os.getenv(type_env)

            # Enabled override
            enabled_env = f"{env_prefix}ENABLED"
            if os.getenv(enabled_env):
                overrides["enabled"] = os.getenv(enabled_env).lower() == "true"

            # Timeout override
            timeout_env = f"{env_prefix}TIMEOUT"
            if os.getenv(timeout_env):
                try:
                    overrides["timeout"] = int(os.getenv(timeout_env))
                except ValueError:
                    self.logger.warning(f"Invalid timeout value in {timeout_env}")

            # Settings overrides (nested)
            settings_overrides = {}
            for env_var in os.environ:
                if env_var.startswith(f"{env_prefix}SETTINGS_"):
                    setting_key = env_var[len(f"{env_prefix}SETTINGS_") :].lower()
                    settings_overrides[setting_key] = os.getenv(env_var)

            if settings_overrides:
                overrides["settings"] = settings_overrides

            # Apply overrides if any exist
            if overrides:
                if dest_key not in config:
                    config[dest_key] = {}

                # Merge overrides with existing config
                if isinstance(config[dest_key], dict):
                    config[dest_key].update(overrides)

                    # Merge settings specifically
                    if "settings" in overrides and "settings" in config[dest_key]:
                        config[dest_key]["settings"].update(overrides["settings"])
                else:
                    config[dest_key] = overrides

        return config

    def _apply_global_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply global default values from environment variables."""
        # Global defaults
        default_slack_channel = os.getenv("BROADIE_DEFAULT_SLACK_CHANNEL")
        default_email_recipient = os.getenv("BROADIE_DEFAULT_EMAIL_RECIPIENT")
        default_webhook_timeout = os.getenv("BROADIE_DEFAULT_WEBHOOK_TIMEOUT")

        # Apply defaults to destinations that don't have explicit targets
        for dest_name in ["primary", "escalation", "notifications", "alerts"]:
            if dest_name in config and isinstance(config[dest_name], dict):
                dest_config = config[dest_name]

                # Apply default Slack channel if destination type is Slack and no target specified
                if (
                    dest_config.get("type") == "slack"
                    and not dest_config.get("target")
                    and default_slack_channel
                ):
                    dest_config["target"] = default_slack_channel

                # Apply default email if destination type is email and no target specified
                if (
                    dest_config.get("type") == "email"
                    and not dest_config.get("target")
                    and default_email_recipient
                ):
                    dest_config["target"] = default_email_recipient

                # Apply default webhook timeout
                if (
                    dest_config.get("type") == "webhook"
                    and default_webhook_timeout
                    and not dest_config.get("timeout")
                ):
                    try:
                        dest_config["timeout"] = int(default_webhook_timeout)
                    except ValueError:
                        self.logger.warning(
                            f"Invalid default webhook timeout: {default_webhook_timeout}"
                        )

        # If no destinations are configured, set up basic fallback
        if not any(
            dest in config
            for dest in ["primary", "escalation", "notifications", "alerts", "fallback"]
        ):
            if default_slack_channel:
                config["fallback"] = {"type": "slack", "target": default_slack_channel}
            elif default_email_recipient:
                config["fallback"] = {
                    "type": "email",
                    "target": default_email_recipient,
                }

        return config

    def _initialize_handlers(self):
        """Initialize destination handlers for all configured destinations."""
        destination_names = self.destinations.list_destinations()

        for dest_name in destination_names:
            destination_config = self.destinations.get_destination(dest_name)
            if destination_config:
                try:
                    handler = self._create_handler(destination_config)
                    if handler:
                        self.handlers[dest_name] = handler
                        self.logger.debug(
                            f"Initialized {destination_config.type} handler for {dest_name}"
                        )
                except Exception as e:
                    self.logger.error(
                        f"Failed to initialize handler for {dest_name}: {e}"
                    )

    def _create_handler(
        self, config: DestinationConfig
    ) -> Optional[BaseDestinationHandler]:
        """Create appropriate handler for destination configuration."""
        try:
            if config.type == DestinationType.SLACK:
                return SlackDestinationHandler(config)
            elif config.type == DestinationType.EMAIL:
                return EmailDestinationHandler(config)
            elif config.type == DestinationType.WEBHOOK:
                return WebhookDestinationHandler(config)
            elif config.type == DestinationType.MULTI:
                return MultiDestinationHandler(config)
            else:
                self.logger.error(f"Unsupported destination type: {config.type}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create {config.type} handler: {e}")
            return None

    async def send(
        self,
        message: str,
        destination_type: str = "primary",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> DeliveryResult:
        """
        Send message to specified destination.

        Args:
            message: Message to send
            destination_type: Type of destination (primary, escalation, etc.)
            context: Additional context for the message
            **kwargs: Additional parameters for context

        Returns:
            DeliveryResult with delivery status and details
        """
        # Create notification context
        notification_context = self._create_notification_context(context, kwargs)
        
        # Get destination handler
        handler = self.handlers.get(destination_type)

        if not handler:
            # Try fallback if original destination not available
            if destination_type != "fallback" and "fallback" in self.handlers:
                self.logger.warning(
                    f"Destination {destination_type} not available, using fallback"
                )
                handler = self.handlers["fallback"]
            else:
                error_msg = f"No handler available for destination: {destination_type}"
                self.logger.error(error_msg)
                return DeliveryResult(
                    destination_name=destination_type,
                    destination_type="unknown",
                    success=False,
                    error_message=error_msg,
                    delivery_time=0.0,
                    attempts=0,
                )

        # Send message with retry logic
        try:
            return await handler.send_with_retry(message, notification_context)
        except Exception as e:
            self.logger.error(f"Failed to send to {destination_type}: {e}")
            return DeliveryResult(
                destination_name=destination_type,
                destination_type=handler.config.type if handler else "unknown",
                success=False,
                error_message=str(e),
                delivery_time=0.0,
                attempts=1,
            )

    async def broadcast(
        self,
        message: str,
        destination_types: List[str],
        context: Optional[Dict[str, Any]] = None,
    ) -> BroadcastResult:
        """
        Broadcast message to multiple destinations concurrently.

        Args:
            message: Message to broadcast
            destination_types: List of destination types to broadcast to
            context: Additional context for the message

        Returns:
            BroadcastResult with aggregated delivery results
        """
        start_time = time.time()

        # Create notification context
        notification_context = self._create_notification_context(context)

        # Create tasks for concurrent sending
        tasks = []
        for dest_type in destination_types:
            task = asyncio.create_task(
                self.send(message, dest_type, context), name=f"broadcast_{dest_type}"
            )
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # Process results
        delivery_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Task failed with exception
                delivery_results.append(
                    DeliveryResult(
                        destination_name=destination_types[i],
                        destination_type="unknown",
                        success=False,
                        error_message=str(result),
                        delivery_time=0.0,
                        attempts=1,
                    )
                )
            else:
                delivery_results.append(result)

        # Calculate summary statistics
        successful_deliveries = sum(1 for result in delivery_results if result.success)
        failed_deliveries = len(delivery_results) - successful_deliveries
        overall_success = successful_deliveries > 0

        return BroadcastResult(
            message=message,
            destinations=destination_types,
            context=notification_context,
            results=delivery_results,
            successful_deliveries=successful_deliveries,
            failed_deliveries=failed_deliveries,
            overall_success=overall_success,
            total_time=total_time,
        )

    async def test_destinations(self) -> Dict[str, bool]:
        """Test connectivity to all configured destinations."""
        results = {}

        for dest_name, handler in self.handlers.items():
            try:
                results[dest_name] = await handler.test_connection()
            except Exception as e:
                self.logger.error(f"Failed to test {dest_name}: {e}")
                results[dest_name] = False

        return results

    def _create_notification_context(
        self,
        context: Optional[Dict[str, Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
    ) -> NotificationContext:
        """Create notification context from provided data."""
        context_data = context or {}

        # Add kwargs to context
        if kwargs:
            context_data.update(kwargs)

        # Set agent information
        context_data["agent_name"] = self.agent_name

        # Set timestamp if not provided
        if "timestamp" not in context_data:
            context_data["timestamp"] = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC", time.gmtime()
            )

        # Ensure severity is valid if provided
        if "severity" in context_data:
            severity_str = str(context_data["severity"]).lower()
            if severity_str in [s.value for s in SeverityLevel]:
                context_data["severity"] = severity_str
            else:
                self.logger.warning(
                    f"Invalid severity level: {context_data['severity']}"
                )
                del context_data["severity"]

        # Ensure tags is a list
        if "tags" in context_data:
            if isinstance(context_data["tags"], str):
                context_data["tags"] = [
                    tag.strip() for tag in context_data["tags"].split(",")
                ]
            elif not isinstance(context_data["tags"], list):
                context_data["tags"] = [str(context_data["tags"])]

        return NotificationContext(**context_data)

    def get_destination_info(self) -> Dict[str, Any]:
        """Get information about all configured destinations."""
        return {
            "agent_name": self.agent_name,
            "available_destinations": list(self.handlers.keys()),
            "destination_configs": {
                name: handler.get_handler_info()
                for name, handler in self.handlers.items()
            },
            "total_destinations": len(self.handlers),
        }

    def has_destination(self, destination_type: str) -> bool:
        """Check if a destination type is configured."""
        return destination_type in self.handlers

    def list_destinations(self) -> List[str]:
        """List all available destination names."""
        return list(self.handlers.keys())
