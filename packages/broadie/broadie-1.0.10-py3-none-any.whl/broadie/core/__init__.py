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

from .agent import Agent, BaseAgent, AgentConfig
from .subagent import SubAgent
from .tools import Tool, ToolRegistry, FunctionTool, get_global_registry
from .memory import Memory, MemoryManager
from .state import BroadieState, Todo, StateManager
from .factory import create_broadie_agent, AgentFactory
from .model import get_default_model, ModelManager
from .interrupt import InterruptManager, ToolInterruptConfig
from .prompts import get_agent_prompt, AGENT_PROMPT_TEMPLATES

__all__ = [
    # Core classes
    "Agent",
    "BaseAgent", 
    "AgentConfig",
    "SubAgent",
    
    # Tools
    "Tool", 
    "ToolRegistry",
    "FunctionTool",
    "get_global_registry",
    
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