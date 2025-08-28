"""
Broadie - A powerful multi-agent framework with persistence, API server, and agent-to-agent communication.

This package provides:
- Agent and SubAgent classes for building intelligent agents
- Persistent storage backends (SQLite, PostgreSQL, Vector stores)
- REST API and WebSocket server
- Agent-to-agent communication and discovery
- CLI tools for managing agents
- Notification integrations
- LangGraph integration with state management
- Memory management with semantic search
"""

from .config.settings import BroadieSettings
from .core.agent import Agent, AgentConfig, BaseAgent, agent, subagent
from .core.factory import AgentFactory, create_broadie_agent
from .core.memory import Memory, MemoryManager
from .core.model import ModelManager, get_default_model
from .core.state import BroadieState, StateManager, Todo
from .core.subagent import SubAgent
from .tools import Tool, ToolRegistry, get_global_registry, tool
from .utils.exceptions import AgentError, BroadieError, ConfigurationError

__version__ = "1.0.6"
__author__ = "Broad Institute"
__email__ = "broadie@broadinstitute.org"

__all__ = [
    # Core agent classes
    "Agent",
    "BaseAgent",
    "AgentConfig",
    "SubAgent",
    # Convenience functions
    "agent",
    "subagent",
    # Tools system
    "Tool",
    "ToolRegistry",
    "tool",
    "get_global_registry",
    # Memory system
    "Memory",
    "MemoryManager",
    # State management
    "BroadieState",
    "Todo",
    "StateManager",
    # Agent creation
    "create_broadie_agent",
    "AgentFactory",
    # Model management
    "get_default_model",
    "ModelManager",
    # Configuration
    "BroadieSettings",
    # Exceptions
    "BroadieError",
    "AgentError",
    "ConfigurationError",
]
