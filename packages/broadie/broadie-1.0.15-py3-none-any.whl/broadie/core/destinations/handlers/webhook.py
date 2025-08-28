"""
Webhook destination handler.

This handler provides HTTP webhook capabilities with support for
custom headers, authentication, and comprehensive error handling.
"""

import json
import os
from typing import Any, Dict, Optional

import httpx

from ..models import DestinationConfig, NotificationContext
from .base import BaseDestinationHandler


class WebhookDestinationHandler(BaseDestinationHandler):
    """Handler for webhook destinations."""

    async def send_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """Send message to webhook endpoint."""
        url = self.config.target
        settings = self.config.settings

        # Format the message
        payload = self.format_message(message, context)

        # Prepare headers
        headers = self._prepare_headers(settings)

        # HTTP method
        method = settings.get("method", "POST").upper()

        try:
            async with httpx.AsyncClient(
                timeout=httpx.Timeout(self.config.timeout),
                follow_redirects=settings.get("follow_redirects", True),
            ) as client:

                # Make the request
                response = await client.request(
                    method=method,
                    url=url,
                    json=payload if method in ["POST", "PUT", "PATCH"] else None,
                    params=payload if method == "GET" else None,
                    headers=headers,
                )

                # Check for HTTP errors
                response.raise_for_status()

                # Parse response
                response_data = {}
                try:
                    if response.content:
                        response_data = response.json()
                except (json.JSONDecodeError, ValueError):
                    response_data = {"response_text": response.text}

                return {
                    "status": "success",
                    "url": url,
                    "method": method,
                    "status_code": response.status_code,
                    "response_data": response_data,
                    "payload": payload,
                }

        except httpx.HTTPStatusError as e:
            error_detail = f"HTTP {e.response.status_code}: {e.response.text}"
            raise Exception(
                f"Webhook request failed with status {e.response.status_code}: {error_detail}"
            )

        except httpx.TimeoutException:
            raise Exception(
                f"Webhook request to {url} timed out after {self.config.timeout}s"
            )

        except httpx.ConnectError:
            raise Exception(f"Failed to connect to webhook URL: {url}")

        except Exception as e:
            raise Exception(f"Webhook request failed: {str(e)}")

    async def test_connection(self) -> bool:
        """Test webhook endpoint connectivity."""
        try:
            url = self.config.target
            settings = self.config.settings

            # Use HEAD request for testing, or GET if specified
            test_method = settings.get("test_method", "HEAD")

            async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
                response = await client.request(
                    method=test_method, url=url, headers=self._prepare_headers(settings)
                )

                # Accept any 2xx or 3xx status, or specific allowed status codes
                allowed_status_codes = settings.get(
                    "test_allowed_status", [200, 201, 202, 204, 301, 302, 404, 405]
                )
                return response.status_code in allowed_status_codes

        except Exception:
            return False

    def format_message(
        self, message: str, context: NotificationContext
    ) -> Dict[str, Any]:
        """Format message for webhook payload."""
        settings = self.config.settings

        # Base payload structure
        payload = {
            "message": message,
            "timestamp": context.timestamp,
            "agent": {"name": context.agent_name, "type": context.agent_type},
        }

        # Add context information
        if context.severity:
            payload["severity"] = context.severity

        if context.tags:
            payload["tags"] = context.tags

        if context.category:
            payload["category"] = context.category

        # Add thread/session information
        if context.thread_id:
            payload["thread_id"] = context.thread_id

        if context.session_id:
            payload["session_id"] = context.session_id

        if context.user_id:
            payload["user_id"] = context.user_id

        # Add metadata
        if context.metadata:
            payload["metadata"] = context.metadata

        # Custom payload transformation
        if settings.get("payload_template"):
            payload = self._apply_payload_template(
                payload, settings["payload_template"]
            )

        # Add custom fields from settings
        if settings.get("custom_fields"):
            payload.update(settings["custom_fields"])

        # Wrap payload if specified
        if settings.get("payload_wrapper"):
            wrapper_key = settings["payload_wrapper"]
            payload = {wrapper_key: payload}

        return payload

    def _prepare_headers(self, settings: Dict[str, Any]) -> Dict[str, str]:
        """Prepare HTTP headers with environment variable substitution."""
        headers = {"Content-Type": "application/json"}

        # Add custom headers
        if settings.get("headers"):
            for key, value in settings["headers"].items():
                # Support environment variable substitution
                if (
                    isinstance(value, str)
                    and value.startswith("${")
                    and value.endswith("}")
                ):
                    env_var = value[2:-1]
                    env_value = os.getenv(env_var)
                    if env_value:
                        headers[key] = env_value
                    else:
                        self.logger.warning(
                            f"Environment variable {env_var} not found for header {key}"
                        )
                else:
                    headers[key] = str(value)

        # Add User-Agent
        if "User-Agent" not in headers:
            headers["User-Agent"] = "Broadie-Agent/1.0"

        return headers

    def _apply_payload_template(
        self, payload: Dict[str, Any], template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply payload template transformation."""

        def substitute_values(template_item, payload_data):
            """Recursively substitute template values."""
            if isinstance(template_item, dict):
                return {
                    k: substitute_values(v, payload_data)
                    for k, v in template_item.items()
                }
            elif isinstance(template_item, list):
                return [substitute_values(item, payload_data) for item in template_item]
            elif isinstance(template_item, str):
                # Support simple substitution like ${field} or ${metadata.key}
                if template_item.startswith("${") and template_item.endswith("}"):
                    field_path = template_item[2:-1]
                    return self._get_nested_value(payload_data, field_path)
                return template_item
            else:
                return template_item

        return substitute_values(template, payload)

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation."""
        try:
            keys = path.split(".")
            value = data
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    def get_handler_info(self) -> Dict[str, Any]:
        """Get webhook-specific handler information."""
        info = super().get_handler_info()
        settings = self.config.settings

        info.update(
            {
                "url": self.config.target,
                "method": settings.get("method", "POST"),
                "supports_custom_headers": True,
                "supports_auth_tokens": True,
                "supports_payload_templates": True,
                "follow_redirects": settings.get("follow_redirects", True),
                "has_custom_headers": bool(settings.get("headers")),
                "has_auth_header": any(
                    key.lower() in ["authorization", "x-api-key", "x-auth-token"]
                    for key in settings.get("headers", {}).keys()
                ),
            }
        )

        return info
