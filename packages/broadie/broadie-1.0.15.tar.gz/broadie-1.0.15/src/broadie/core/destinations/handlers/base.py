"""
Base destination handler class.

This module defines the abstract interface that all destination handlers
must implement, providing consistent error handling, retry logic, and
formatting capabilities.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..models import DeliveryResult, DestinationConfig, NotificationContext

logger = logging.getLogger(__name__)


class BaseDestinationHandler(ABC):
    """Abstract base class for all destination handlers."""

    def __init__(self, config: DestinationConfig):
        """Initialize the handler with destination configuration."""
        self.config = config
        self.logger = logging.getLogger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    @abstractmethod
    async def send_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """
        Send a message to the destination.

        Args:
            message: The message to send
            context: Context information for the message

        Returns:
            Dict containing response data from the destination

        Raises:
            Exception: If the message cannot be sent
        """
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Test connectivity to the destination.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        pass

    @abstractmethod
    def format_message(self, message: str, context: NotificationContext) -> Any:
        """
        Format message for the specific destination type.

        Args:
            message: Raw message text
            context: Context information

        Returns:
            Formatted message appropriate for the destination
        """
        pass

    async def send_with_retry(
        self, message: str, context: NotificationContext
    ) -> DeliveryResult:
        """
        Send message with retry logic and comprehensive error handling.

        Args:
            message: Message to send
            context: Notification context

        Returns:
            DeliveryResult with success/failure information
        """
        start_time = time.time()
        last_error = None
        attempts = 0

        # Check if destination is enabled
        if not self.config.enabled:
            return DeliveryResult(
                destination_name=getattr(context, "destination_name", "unknown"),
                destination_type=self.config.type,
                success=False,
                error_message="Destination is disabled",
                error_code="DISABLED",
                delivery_time=0.0,
                attempts=0,
            )

        # Evaluate conditions if present
        if not self._check_conditions(context):
            return DeliveryResult(
                destination_name=getattr(context, "destination_name", "unknown"),
                destination_type=self.config.type,
                success=False,
                error_message="Message conditions not met",
                error_code="CONDITIONS_NOT_MET",
                delivery_time=0.0,
                attempts=0,
            )

        # Attempt delivery with retries
        for attempt in range(self.config.retry_attempts):
            attempts = attempt + 1

            try:
                self.logger.debug(
                    f"Sending message to {self.config.type} destination (attempt {attempts}/{self.config.retry_attempts})"
                )

                # Send the message
                response_data = await asyncio.wait_for(
                    self.send_message(message, context), timeout=self.config.timeout
                )

                delivery_time = time.time() - start_time

                self.logger.info(
                    f"Successfully sent message to {self.config.type} destination in {delivery_time:.2f}s"
                )

                return DeliveryResult(
                    destination_name=getattr(context, "destination_name", "unknown"),
                    destination_type=self.config.type,
                    success=True,
                    response_data=response_data,
                    delivery_time=delivery_time,
                    attempts=attempts,
                )

            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.config.timeout}s"
                self.logger.warning(f"Timeout on attempt {attempts}: {last_error}")

            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Error on attempt {attempts}: {last_error}")

                # For certain errors, don't retry
                if self._is_non_retryable_error(e):
                    self.logger.error(f"Non-retryable error: {last_error}")
                    break

            # Wait before retry (exponential backoff)
            if attempt < self.config.retry_attempts - 1:
                backoff_time = self.config.retry_backoff**attempt
                self.logger.debug(f"Waiting {backoff_time}s before retry")
                await asyncio.sleep(backoff_time)

        delivery_time = time.time() - start_time

        self.logger.error(
            f"Failed to send message to {self.config.type} destination after {attempts} attempts: {last_error}"
        )

        return DeliveryResult(
            destination_name=getattr(context, "destination_name", "unknown"),
            destination_type=self.config.type,
            success=False,
            error_message=last_error,
            delivery_time=delivery_time,
            attempts=attempts,
        )

    def _check_conditions(self, context: NotificationContext) -> bool:
        """
        Check if message meets destination conditions.

        Args:
            context: Notification context to evaluate

        Returns:
            bool: True if conditions are met or no conditions exist
        """
        if not self.config.conditions:
            return True

        conditions = self.config.conditions

        # Check severity conditions
        if "severity" in conditions and context.severity:
            severity_rule = conditions["severity"]
            if not self._evaluate_severity_condition(severity_rule, context.severity):
                self.logger.debug(
                    f"Severity condition not met: {severity_rule} vs {context.severity}"
                )
                return False

        # Check tag conditions
        if "tags" in conditions:
            required_tags = conditions["tags"]
            if not self._evaluate_tag_condition(required_tags, context.tags):
                self.logger.debug(
                    f"Tag condition not met: required {required_tags}, got {context.tags}"
                )
                return False

        # Check custom conditions
        for condition_key, condition_value in conditions.items():
            if condition_key not in ["severity", "tags"]:
                if not self._evaluate_custom_condition(
                    condition_key, condition_value, context
                ):
                    self.logger.debug(
                        f"Custom condition not met: {condition_key}={condition_value}"
                    )
                    return False

        return True

    def _evaluate_severity_condition(self, rule: str, actual_severity: str) -> bool:
        """Evaluate severity-based conditions."""
        severity_levels = {"low": 1, "medium": 2, "high": 3, "critical": 4}

        if rule.startswith(">="):
            required_level = severity_levels.get(rule[2:], 0)
            actual_level = severity_levels.get(actual_severity, 0)
            return actual_level >= required_level
        elif rule.startswith("<="):
            required_level = severity_levels.get(rule[2:], 0)
            actual_level = severity_levels.get(actual_severity, 0)
            return actual_level <= required_level
        elif rule.startswith("=="):
            return rule[2:] == actual_severity
        elif rule.startswith(">"):
            required_level = severity_levels.get(rule[1:], 0)
            actual_level = severity_levels.get(actual_severity, 0)
            return actual_level > required_level
        elif rule.startswith("<"):
            required_level = severity_levels.get(rule[1:], 0)
            actual_level = severity_levels.get(actual_severity, 0)
            return actual_level < required_level
        else:
            # Direct equality
            return rule == actual_severity

    def _evaluate_tag_condition(self, required_tags: list, actual_tags: list) -> bool:
        """Evaluate tag-based conditions (all required tags must be present)."""
        return all(tag in actual_tags for tag in required_tags)

    def _evaluate_custom_condition(
        self, key: str, value: Any, context: NotificationContext
    ) -> bool:
        """Evaluate custom conditions against context metadata."""
        metadata_value = context.metadata.get(key)
        if metadata_value is None:
            return False
        return metadata_value == value

    def _is_non_retryable_error(self, error: Exception) -> bool:
        """
        Determine if an error should not be retried.

        Args:
            error: The exception that occurred

        Returns:
            bool: True if error should not be retried
        """
        # Common non-retryable error patterns
        error_message = str(error).lower()

        non_retryable_patterns = [
            "unauthorized",
            "forbidden",
            "not found",
            "bad request",
            "invalid",
            "malformed",
            "authentication failed",
            "permission denied",
        ]

        return any(pattern in error_message for pattern in non_retryable_patterns)

    def get_handler_info(self) -> Dict[str, Any]:
        """Get information about this handler."""
        return {
            "type": self.config.type,
            "target": self.config.target,
            "enabled": self.config.enabled,
            "timeout": self.config.timeout,
            "retry_attempts": self.config.retry_attempts,
            "has_conditions": bool(self.config.conditions),
        }
