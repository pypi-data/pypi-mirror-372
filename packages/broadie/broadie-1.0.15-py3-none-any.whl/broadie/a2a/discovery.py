"""
A2A Peer discovery: fetch and cache peer /.well-known/agent.json for function discovery.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from functools import lru_cache, wraps
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger("broadie.a2a.discovery")


@dataclass
class AgentIdentity:
    agent_id: str
    agent_name: str
    capabilities: dict


@dataclass
class PeerAgent:
    agent_id: str
    agent_name: str
    url: str
    capabilities: dict
    identity: Optional[AgentIdentity] = None
    agent_json: dict = field(default_factory=dict)


class DiscoveryClient:
    def __init__(self):
        self.http_client = httpx.AsyncClient()
        self.cache: Dict[str, PeerAgent] = {}

    async def fetch_agent_json(self, url: str) -> Optional[dict]:

        full_url = url.rstrip("/") + "/.well-known/agent.json"
        try:
            resp = await self.http_client.get(full_url, timeout=4.0)
            if resp.status_code == 200:
                return resp.json()
            logger.warning(f"Non-200 response from {full_url}: {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to fetch {full_url}: {e}")
        return None

    async def discover_peer(self, url: str) -> Optional[PeerAgent]:
        # Try cache
        if url in self.cache:
            return self.cache[url]
        agent_json = await self.fetch_agent_json(url)
        if not agent_json:
            return None
        try:
            identity = AgentIdentity(
                agent_id=agent_json["agent_id"],
                agent_name=agent_json["agent_name"],
                capabilities=agent_json.get("capabilities", {}),
            )
            peer = PeerAgent(
                agent_id=identity.agent_id,
                agent_name=identity.agent_name,
                url=url,
                capabilities=agent_json.get("capabilities", {}),
                identity=identity,
                agent_json=agent_json,
            )
            self.cache[url] = peer
            return peer
        except Exception as e:
            logger.error(f"Malformed agent.json from {url}: {e}")
        return None

    async def get_peers_from_registry(
        self, registry_url: str, *, api_key: Optional[str] = None
    ) -> List[PeerAgent]:
        # Assume registry exposes /agents/peers returning a list of {agent_id, agent_name, url}
        try:
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            url = registry_url.rstrip("/") + "/agents/peers"
            resp = await self.http_client.get(url, headers=headers)
            if resp.status_code != 200:
                logger.warning(f"Failed to get peers from registry: {resp.status_code}")
                return []
            data = resp.json()
            peers = []
            for peer_info in data.get("peers", []):
                url = peer_info.get("url")
                if url:
                    peer = await self.discover_peer(url)
                    if peer:
                        peers.append(peer)
            return peers
        except Exception as e:
            logger.error(f"Error in get_peers_from_registry: {e}")
            return []

    def get_cached_peer(self, url: str) -> Optional[PeerAgent]:
        return self.cache.get(url)

    def clear_cache(self):
        self.cache.clear()


# Utility: Limit trust to only trusted agent_ids


def ensure_trusted(agent_id: str, trusted_agents: List[str]):
    if trusted_agents and agent_id not in trusted_agents:
        raise PermissionError(f"Untrusted agent: {agent_id}")


# Basic fallback/error testing
async def test_discovery():
    # Example peer (local agent):
    d = DiscoveryClient()
    # Should not error if downstream is missing
    result = await d.fetch_agent_json("http://localhost:9999")
    assert result is None
    print("Discovery peer failed as expected.")


if __name__ == "__main__":
    asyncio.run(test_discovery())
