"""
A2A Registry Client: agent registration, peer list fetching, and tracking heartbeats.
"""

import logging
from typing import Dict, List, Optional

import httpx

from broadie.config.settings import BroadieSettings

logger = logging.getLogger("broadie.a2a.registry_client")


class RegistryClient:
    def __init__(
        self,
        settings: BroadieSettings,
        agent_id: str,
        agent_name: str,
        registry_url: str,
        api_key: Optional[str] = None,
    ):
        self.settings = settings
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.registry_url = registry_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.AsyncClient()

    async def register(self, metadata: Optional[dict] = None):
        url = f"{self.registry_url}/agents/register"
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload = {"agent_id": self.agent_id, "agent_name": self.agent_name}
        if metadata:
            payload.update(metadata)
        try:
            resp = await self._client.post(url, json=payload, headers=headers)
            if resp.status_code == 200:
                logger.info(f"Agent {self.agent_id} registered with registry.")
                return resp.json()
            else:
                logger.warning(
                    f"Failed to register agent: {resp.status_code}: {resp.text}"
                )
                return None
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return None

    async def get_peers(self) -> List[Dict]:
        url = f"{self.registry_url}/agents/peers"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            resp = await self._client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json().get("peers", [])
            else:
                logger.warning(
                    f"Failed to fetch peers from registry: {resp.status_code}: {resp.text}"
                )
                return []
        except Exception as e:
            logger.error(f"Error fetching peers: {e}")
            return []

    async def get_peer_heartbeat(self, peer_id: str) -> Optional[dict]:
        url = f"{self.registry_url}/agents/{peer_id}/heartbeat"
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        try:
            resp = await self._client.get(url, headers=headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning(
                    f"Failed to fetch heartbeat for {peer_id}: {resp.status_code}"
                )
        except Exception as e:
            logger.error(f"Error fetching heartbeat for {peer_id}: {e}")
        return None
