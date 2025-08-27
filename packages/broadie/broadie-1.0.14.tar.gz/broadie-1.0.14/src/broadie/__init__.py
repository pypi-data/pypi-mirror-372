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

from .core.agent import Agent, BaseAgent, AgentConfig
from .core.subagent import SubAgent
from .core.tools import Tool, ToolRegistry, tool, get_global_registry
from .core.memory import Memory, MemoryManager
from .core.state import BroadieState, Todo, StateManager
from .core.factory import create_broadie_agent, AgentFactory
from .core.model import get_default_model, ModelManager
from .config.settings import BroadieSettings
from .utils.exceptions import BroadieError, AgentError, ConfigurationError

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