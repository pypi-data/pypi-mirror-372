#!/usr/bin/env python3
"""
Simple A2A Registry Server for Broadie Agents

This is a basic implementation of an agent registry server that agents can use
for discovery and heartbeat reporting.

Usage:
    python registry_server.py [--port 8001] [--host 0.0.0.0]

Features:
- Agent registration
- Heartbeat tracking
- Agent discovery
- Basic authentication support
- Agent status monitoring
"""

import argparse
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("registry_server")


class AgentRegistration(BaseModel):
    """Agent registration data."""

    agent_id: str
    agent_name: str
    address: str
    timestamp: int
    status: str = "online"
    capabilities: Optional[Dict] = None
    metadata: Optional[Dict] = None


class AgentHeartbeat(BaseModel):
    """Agent heartbeat data."""

    agent_id: str
    agent_name: Optional[str] = None
    address: Optional[str] = None
    timestamp: int
    status: str = "online"


class RegistryServer:
    """Simple in-memory registry server."""

    def __init__(self, heartbeat_timeout: int = 120):
        self.agents: Dict[str, AgentRegistration] = {}
        self.last_heartbeat: Dict[str, int] = {}
        self.heartbeat_timeout = heartbeat_timeout
        logger.info(
            f"Registry server initialized with heartbeat timeout: {heartbeat_timeout}s"
        )

    def register_agent(self, registration: AgentRegistration) -> bool:
        """Register a new agent or update existing registration."""
        agent_id = registration.agent_id

        # Store agent registration
        self.agents[agent_id] = registration
        self.last_heartbeat[agent_id] = registration.timestamp

        logger.info(
            f"Agent registered: {agent_id} ({registration.agent_name}) at {registration.address}"
        )
        return True

    def update_heartbeat(self, heartbeat: AgentHeartbeat) -> bool:
        """Update agent heartbeat."""
        agent_id = heartbeat.agent_id

        # Update heartbeat timestamp
        self.last_heartbeat[agent_id] = heartbeat.timestamp

        # Update agent info if provided
        if agent_id in self.agents:
            if heartbeat.agent_name:
                self.agents[agent_id].agent_name = heartbeat.agent_name
            if heartbeat.address:
                self.agents[agent_id].address = heartbeat.address
            self.agents[agent_id].status = heartbeat.status
            self.agents[agent_id].timestamp = heartbeat.timestamp
        else:
            # Create minimal registration from heartbeat
            registration = AgentRegistration(
                agent_id=agent_id,
                agent_name=heartbeat.agent_name or agent_id,
                address=heartbeat.address or "unknown",
                timestamp=heartbeat.timestamp,
                status=heartbeat.status,
            )
            self.agents[agent_id] = registration

        logger.debug(f"Heartbeat updated for agent: {agent_id}")
        return True

    def get_active_agents(self) -> List[AgentRegistration]:
        """Get list of active agents (within heartbeat timeout)."""
        current_time = int(time.time())
        active_agents = []

        for agent_id, registration in self.agents.items():
            last_hb = self.last_heartbeat.get(agent_id, 0)
            if current_time - last_hb <= self.heartbeat_timeout:
                active_agents.append(registration)
            else:
                # Mark as inactive
                registration.status = "inactive"

        return active_agents

    def get_agent(self, agent_id: str) -> Optional[AgentRegistration]:
        """Get specific agent registration."""
        return self.agents.get(agent_id)

    def cleanup_inactive_agents(self) -> int:
        """Remove agents that haven't sent heartbeats for too long."""
        current_time = int(time.time())
        inactive_threshold = self.heartbeat_timeout * 3  # 3x heartbeat timeout

        to_remove = []
        for agent_id, last_hb in self.last_heartbeat.items():
            if current_time - last_hb > inactive_threshold:
                to_remove.append(agent_id)

        for agent_id in to_remove:
            self.agents.pop(agent_id, None)
            self.last_heartbeat.pop(agent_id, None)
            logger.info(f"Removed inactive agent: {agent_id}")

        return len(to_remove)


# Global registry instance
registry = RegistryServer()

# Create FastAPI app
app = FastAPI(
    title="Broadie A2A Registry Server",
    description="Agent-to-Agent Registry for Broadie Agents",
    version="1.0.0",
)


def get_api_key(authorization: str = Header(None)) -> Optional[str]:
    """Extract API key from Authorization header."""
    if not authorization:
        return None

    if authorization.startswith("Bearer "):
        return authorization[7:]

    return authorization


@app.get("/")
async def root():
    """Root endpoint with basic server info."""
    return {
        "service": "Broadie A2A Registry Server",
        "version": "1.0.0",
        "status": "online",
        "timestamp": int(time.time()),
        "active_agents": len(registry.get_active_agents()),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": int(time.time())}


@app.post("/agents/{agent_id}/register")
async def register_agent(
    agent_id: str,
    registration: AgentRegistration,
    api_key: Optional[str] = Depends(get_api_key),
):
    """Register a new agent."""
    # Validate agent_id matches
    if agent_id != registration.agent_id:
        raise HTTPException(status_code=400, detail="Agent ID mismatch")

    # TODO: Add API key validation if needed
    # if api_key != expected_api_key:
    #     raise HTTPException(status_code=401, detail="Invalid API key")

    success = registry.register_agent(registration)
    if success:
        return {
            "message": f"Agent {agent_id} registered successfully",
            "timestamp": int(time.time()),
        }
    else:
        raise HTTPException(status_code=500, detail="Registration failed")


@app.post("/agents/{agent_id}/heartbeat")
async def agent_heartbeat(
    agent_id: str,
    heartbeat: AgentHeartbeat,
    api_key: Optional[str] = Depends(get_api_key),
):
    """Update agent heartbeat."""
    # Validate agent_id matches
    if agent_id != heartbeat.agent_id:
        raise HTTPException(status_code=400, detail="Agent ID mismatch")

    success = registry.update_heartbeat(heartbeat)
    if success:
        return {
            "message": f"Heartbeat updated for {agent_id}",
            "timestamp": int(time.time()),
        }
    else:
        raise HTTPException(status_code=500, detail="Heartbeat update failed")


@app.get("/agents")
async def list_agents(
    active_only: bool = True, api_key: Optional[str] = Depends(get_api_key)
):
    """List all agents or only active agents."""
    if active_only:
        agents = registry.get_active_agents()
    else:
        agents = list(registry.agents.values())

    return {
        "agents": [agent.model_dump() for agent in agents],
        "total": len(agents),
        "timestamp": int(time.time()),
    }


@app.get("/agents/{agent_id}")
async def get_agent_info(agent_id: str, api_key: Optional[str] = Depends(get_api_key)):
    """Get information about a specific agent."""
    agent = registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")

    # Check if agent is active
    current_time = int(time.time())
    last_hb = registry.last_heartbeat.get(agent_id, 0)
    is_active = current_time - last_hb <= registry.heartbeat_timeout

    agent_data = agent.model_dump()
    agent_data["is_active"] = is_active
    agent_data["last_heartbeat"] = last_hb
    agent_data["seconds_since_heartbeat"] = current_time - last_hb

    return agent_data


@app.delete("/agents/{agent_id}")
async def unregister_agent(
    agent_id: str, api_key: Optional[str] = Depends(get_api_key)
):
    """Unregister an agent."""
    if agent_id in registry.agents:
        del registry.agents[agent_id]
        registry.last_heartbeat.pop(agent_id, None)
        logger.info(f"Agent unregistered: {agent_id}")
        return {"message": f"Agent {agent_id} unregistered successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")


@app.get("/stats")
async def get_stats():
    """Get registry statistics."""
    active_agents = registry.get_active_agents()
    total_agents = len(registry.agents)

    return {
        "total_agents": total_agents,
        "active_agents": len(active_agents),
        "inactive_agents": total_agents - len(active_agents),
        "heartbeat_timeout": registry.heartbeat_timeout,
        "timestamp": int(time.time()),
    }


@app.post("/admin/cleanup")
async def cleanup_inactive():
    """Admin endpoint to cleanup inactive agents."""
    removed = registry.cleanup_inactive_agents()
    return {
        "message": f"Cleaned up {removed} inactive agents",
        "removed_count": removed,
        "timestamp": int(time.time()),
    }


async def periodic_cleanup():
    """Periodic cleanup of inactive agents."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            removed = registry.cleanup_inactive_agents()
            if removed > 0:
                logger.info(f"Periodic cleanup removed {removed} inactive agents")
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")


@app.on_event("startup")
async def startup_event():
    """Start background tasks."""
    asyncio.create_task(periodic_cleanup())
    logger.info("Registry server startup complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Broadie A2A Registry Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument(
        "--timeout", type=int, default=120, help="Heartbeat timeout in seconds"
    )
    parser.add_argument("--log-level", default="INFO", help="Log level")

    args = parser.parse_args()

    # Update log level
    logging.getLogger().setLevel(getattr(logging, args.log_level.upper()))

    # Update registry timeout
    registry.heartbeat_timeout = args.timeout

    logger.info(f"Starting Broadie A2A Registry Server on {args.host}:{args.port}")
    logger.info(f"Heartbeat timeout: {args.timeout} seconds")

    # Run the server
    uvicorn.run(app, host=args.host, port=args.port, log_level=args.log_level.lower())


if __name__ == "__main__":
    main()
