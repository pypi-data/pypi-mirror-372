"""
Heartbeat: Periodic agent heartbeat to registry for A2A communication.
"""

import asyncio
import logging
import time
from typing import Optional

import httpx

from broadie.config.settings import BroadieSettings

logger = logging.getLogger("broadie.a2a.heartbeat")


class Heartbeat:
    def __init__(
        self,
        settings: BroadieSettings,
        agent_id: str,
        registry_url: str,
        api_key: Optional[str] = None,
        interval: int = 30,
        agent_address: Optional[str] = None,
        agent_name: Optional[str] = None,
    ):
        self.settings = settings
        self.agent_id = agent_id
        self.agent_name = agent_name or settings.a2a.agent_name or agent_id
        self.registry_url = registry_url
        self.api_key = api_key
        self.interval = interval
        self._stop = False
        self._client = httpx.AsyncClient()

        # Build agent address
        if agent_address:
            self.agent_address = agent_address
        else:
            # Construct from settings
            host = settings.api_host if settings.api_host != "0.0.0.0" else "localhost"
            self.agent_address = f"http://{host}:{settings.api_port}"

        self._registered = False

    async def register_agent(self):
        """Register agent with the registry initially."""
        url = f"{self.registry_url.rstrip('/')}/agents/{self.agent_id}/register"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "address": self.agent_address,
            "timestamp": int(time.time()),
            "status": "online",
        }

        try:
            r = await self._client.post(url, headers=headers, json=payload)
            if r.status_code in (200, 201):
                logger.info(f"Agent {self.agent_id} registered at {self.agent_address}")
                self._registered = True
                return True
            else:
                logger.warning(
                    f"Registration failed ({r.status_code}) for {self.agent_id}: {r.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return False

    async def send_heartbeat(self):
        """Send heartbeat with agent address information."""
        url = f"{self.registry_url.rstrip('/')}/agents/{self.agent_id}/heartbeat"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "address": self.agent_address,
            "timestamp": int(time.time()),
            "status": "online",
        }

        try:
            r = await self._client.post(url, headers=headers, json=payload)
            if r.status_code == 200:
                logger.debug(
                    f"Heartbeat sent for agent {self.agent_id} at {self.agent_address}"
                )
            else:
                logger.warning(
                    f"Heartbeat failed ({r.status_code}) for {self.agent_id}: {r.text}"
                )
        except Exception as e:
            logger.error(f"Error sending heartbeat: {e}")

    async def run(self):
        logger.info(
            f"Starting heartbeat for agent {self.agent_id} to {self.registry_url} every {self.interval}s"
        )

        try:
            # Try to register initially
            if not self._registered:
                await self.register_agent()

            while not self._stop:
                await self.send_heartbeat()
                await asyncio.sleep(self.interval)
        except asyncio.CancelledError:
            logger.info(f"Heartbeat cancelled for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Heartbeat error for agent {self.agent_id}: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Clean up resources."""
        try:
            await self._client.aclose()
            logger.debug(f"HTTP client closed for agent {self.agent_id}")
        except Exception as e:
            logger.error(f"Error closing HTTP client: {e}")

    def stop(self):
        """Signal the heartbeat to stop."""
        self._stop = True
