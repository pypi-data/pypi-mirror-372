"""
Core module for Broadie agents and related abstractions.

This module contains the fundamental building blocks:
- Agent: Main agent class with LangGraph integration
- SubAgent: Specialized agents for specific tasks
- Tool: Function definitions and registry
- Memory: Persistent memory and vector storage
- State: Agent state management and schemas
- Factory: Agent creation utilities
- Model: Language model management
"""

from .agent import Agent, AgentConfig, BaseAgent
from .factory import AgentFactory, create_broadie_agent
from .interrupt import InterruptManager, ToolInterruptConfig

# Tools are now in the tools package
from .memory import Memory, MemoryManager
from .model import ModelManager, get_default_model
from .prompts import AGENT_PROMPT_TEMPLATES, get_agent_prompt
from .state import BroadieState, StateManager, Todo
from .subagent import SubAgent

__all__ = [
    # Core classes
    "Agent",
    "BaseAgent",
    "AgentConfig",
    "SubAgent",
    # Memory
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
    # Interrupts
    "InterruptManager",
    "ToolInterruptConfig",
    # Prompts
    "get_agent_prompt",
    "AGENT_PROMPT_TEMPLATES",
]
