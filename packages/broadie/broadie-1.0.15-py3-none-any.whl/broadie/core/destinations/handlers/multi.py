"""
Multi-destination handler for broadcasting messages.

This handler manages sending messages to multiple destinations concurrently
with comprehensive error handling and result aggregation.
"""

import asyncio
import time
from typing import Any, Dict, List, Union

from ..models import DeliveryResult, DestinationConfig, NotificationContext
from .base import BaseDestinationHandler
from .email import EmailDestinationHandler
from .slack import SlackDestinationHandler
from .webhook import WebhookDestinationHandler


class MultiDestinationHandler(BaseDestinationHandler):
    """Handler for broadcasting to multiple destinations."""

    def __init__(self, config: DestinationConfig):
        super().__init__(config)
        self.target_handlers = []
        self._initialize_target_handlers()

    def _initialize_target_handlers(self):
        """Initialize handlers for each target destination."""
        targets = (
            self.config.target
            if isinstance(self.config.target, list)
            else [self.config.target]
        )

        for i, target in enumerate(targets):
            if isinstance(target, dict):
                # Target is a full destination configuration
                target_config = DestinationConfig(**target)
                handler = self._create_handler_for_config(target_config)
                if handler:
                    self.target_handlers.append((f"target_{i}", handler))
            elif isinstance(target, str):
                # Target is a string, infer type and create basic config
                target_config = self._infer_destination_config(target, i)
                handler = self._create_handler_for_config(target_config)
                if handler:
                    self.target_handlers.append((f"target_{i}", handler))

    def _create_handler_for_config(
        self, config: DestinationConfig
    ) -> BaseDestinationHandler:
        """Create appropriate handler for destination configuration."""
        try:
            if config.type == "slack":
                return SlackDestinationHandler(config)
            elif config.type == "email":
                return EmailDestinationHandler(config)
            elif config.type == "webhook":
                return WebhookDestinationHandler(config)
            else:
                self.logger.error(f"Unsupported destination type: {config.type}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to create handler for {config.type}: {e}")
            return None

    def _infer_destination_config(self, target: str, index: int) -> DestinationConfig:
        """Infer destination configuration from target string."""
        settings = self.config.settings.get("targets", [{}])
        target_settings = settings[index] if index < len(settings) else {}

        # Infer type from target string
        if (
            target.startswith("#")
            or target.startswith("@")
            or "slack" in target.lower()
        ):
            dest_type = "slack"
        elif "@" in target and "." in target:  # Email pattern
            dest_type = "email"
        elif target.startswith("http"):
            dest_type = "webhook"
        else:
            dest_type = "slack"  # Default fallback

        return DestinationConfig(
            type=dest_type,
            target=target,
            settings=target_settings,
            timeout=self.config.timeout,
            retry_attempts=self.config.retry_attempts,
        )

    async def send_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """Send message to all target destinations concurrently."""
        if not self.target_handlers:
            raise Exception("No valid target handlers configured")

        start_time = time.time()

        # Create tasks for concurrent execution
        tasks = []
        for target_name, handler in self.target_handlers:
            # Create a copy of context with destination name
            target_context = NotificationContext(**context.dict())
            target_context.destination_name = target_name

            task = asyncio.create_task(
                self._send_to_target(target_name, handler, message, target_context),
                name=f"send_{target_name}",
            )
            tasks.append(task)

        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        total_time = time.time() - start_time

        # Process results
        delivery_results = []
        successful_deliveries = 0
        failed_deliveries = 0

        for i, (target_name, handler) in enumerate(self.target_handlers):
            result = results[i]

            if isinstance(result, Exception):
                # Task failed with exception
                delivery_results.append(
                    DeliveryResult(
                        destination_name=target_name,
                        destination_type=handler.config.type,
                        success=False,
                        error_message=str(result),
                        delivery_time=0.0,
                        attempts=1,
                    )
                )
                failed_deliveries += 1
            else:
                # Task completed (could be success or failure)
                delivery_results.append(result)
                if result.success:
                    successful_deliveries += 1
                else:
                    failed_deliveries += 1

        # Determine overall success
        overall_success = successful_deliveries > 0

        return {
            "status": "success" if overall_success else "failed",
            "total_targets": len(self.target_handlers),
            "successful_deliveries": successful_deliveries,
            "failed_deliveries": failed_deliveries,
            "delivery_results": [result.dict() for result in delivery_results],
            "total_time": total_time,
            "overall_success": overall_success,
        }

    async def _send_to_target(
        self,
        target_name: str,
        handler: BaseDestinationHandler,
        message: str,
        context: NotificationContext,
    ) -> DeliveryResult:
        """Send message to a single target with error handling."""
        try:
            return await handler.send_with_retry(message, context)
        except Exception as e:
            self.logger.error(f"Failed to send to {target_name}: {e}")
            return DeliveryResult(
                destination_name=target_name,
                destination_type=handler.config.type,
                success=False,
                error_message=str(e),
                delivery_time=0.0,
                attempts=1,
            )

    async def test_connection(self) -> bool:
        """Test connectivity to all target destinations."""
        if not self.target_handlers:
            return False

        # Test all targets concurrently
        tasks = [handler.test_connection() for _, handler in self.target_handlers]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Return True if at least one target is reachable
        successful_connections = sum(
            1 for result in results if not isinstance(result, Exception) and result
        )

        self.logger.debug(
            f"Multi-destination test: {successful_connections}/{len(self.target_handlers)} targets reachable"
        )
        return successful_connections > 0

    def format_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """Format message for multi-destination (delegation to individual handlers)."""
        return {
            "message": message,
            "context": context.dict(),
            "target_count": len(self.target_handlers),
            "note": "Message formatting is handled by individual target handlers",
        }

    def get_target_info(self) -> List[Dict[str, Any]]:
        """Get information about all target handlers."""
        return [
            {"name": target_name, "handler_info": handler.get_handler_info()}
            for target_name, handler in self.target_handlers
        ]

    def get_handler_info(self) -> Dict[str, Any]:
        """Get multi-destination handler information."""
        info = super().get_handler_info()
        info.update(
            {
                "total_targets": len(self.target_handlers),
                "target_types": [
                    handler.config.type for _, handler in self.target_handlers
                ],
                "supports_concurrent_delivery": True,
                "partial_failure_handling": True,
                "targets": self.get_target_info(),
            }
        )
        return info
