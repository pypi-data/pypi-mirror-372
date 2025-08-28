"""
SubAgent implementation for specialized tasks.
Extends the base agent with simpler configuration and focused functionality.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from broadie.utils.exceptions import ConfigurationError

from .agent import AgentConfig, BaseAgent


class SubAgent(BaseAgent):
    """
    Specialized agent for specific tasks within a parent agent.

    SubAgents have the same API as Agent, but cannot declare subagents.
    Both Agent and SubAgent support: name, instruction, tools, etc.
    """

    def build_config(self) -> Union[AgentConfig, Dict[str, Any], Path]:
        """
        Return the configuration for this sub-agent when instantiated without parameters.
        Should return an AgentConfig instance, a dict, or a path to a JSON config file.
        """
        raise NotImplementedError("build_config() must be implemented by subclasses")

    def __init__(
        self,
        config: Optional[Union[AgentConfig, Dict[str, Any], Path]] = None,
        *,
        parent_agent: Optional["Agent"] = None,
        **kwargs,
    ):
        # Require configuration via config param or build_config()
        if config is not None:
            if isinstance(config, (str, Path)):
                agent_config = self._load_config_from_file(config)
            elif isinstance(config, dict):
                agent_config = AgentConfig(**config)
            else:
                agent_config = config
        else:
            try:
                config_data = self.build_config()
            except Exception:
                raise ConfigurationError(
                    "SubAgent must be configured via the 'config' parameter or build_config() method; name-based init is not supported"
                )
            if isinstance(config_data, (str, Path)):
                agent_config = self._load_config_from_file(config_data)
            elif isinstance(config_data, dict):
                agent_config = AgentConfig(**config_data)
            else:
                agent_config = config_data
        super().__init__(agent_config, **kwargs)
        self.parent_agent = parent_agent
        self.config: AgentConfig = agent_config  # Type hint for better IDE support

        # Auto-discover tools from global registry if no explicit tools
        if not self.config.tools:
            self._auto_discover_tools()

    def _auto_discover_tools(self):
        """Auto-discover tools decorated with @tool in the current module context."""
        import inspect
        import sys

        # Get the calling module (where SubAgent is instantiated)
        frame = inspect.currentframe()
        try:
            # Go up the call stack to find the module where SubAgent() was called
            caller_frame = frame.f_back.f_back  # Skip __init__ frame
            if caller_frame:
                caller_globals = caller_frame.f_globals

                # Look for functions decorated with @tool
                discovered_tools = []
                for name, obj in caller_globals.items():
                    if (
                        callable(obj)
                        and hasattr(obj, "_is_broadie_tool")
                        and obj._is_broadie_tool
                    ):
                        discovered_tools.append(obj._tool_name)

                # Add discovered tools to config if not already specified
                if not self.config.tools:
                    self.config.tools = discovered_tools
                else:
                    # Merge with existing tools
                    all_tools = list(self.config.tools) + discovered_tools
                    self.config.tools = list(
                        dict.fromkeys(all_tools)
                    )  # Remove duplicates
        finally:
            del frame

    @property
    def prompt(self) -> str:
        """Get the instruction for this sub-agent (alias for consistency)."""
        return self.config.instruction

    def _load_config_from_file(self, config_path: Union[str, Path]) -> AgentConfig:
        """Load SubAgent configuration from JSON file."""
        import json

        path = Path(config_path)
        if not path.exists():
            raise ConfigurationError(f"Config file not found: {path}")

        with open(path, "r") as f:
            config_data = json.load(f)

        return AgentConfig(**config_data)

    def _initialize_agent(self):
        """Initialize the LangGraph agent with prompt instead of instruction."""
        if self._agent is None:
            from langgraph.prebuilt import create_react_agent

            model = self._initialize_model()
            tools = self._get_tools()

            # Use prompt for sub-agents, fallback to instruction
            agent_prompt = self.prompt or self.config.instruction

            self._agent = create_react_agent(
                model, tools=tools, prompt=agent_prompt, checkpointer=False
            )

        return self._agent

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a message using this sub-agent."""
        result = await self.invoke(message, context)
        return result.get("response", "")

    def get_identity(self) -> Dict[str, Any]:
        """Get sub-agent identity."""
        identity = super().get_identity()
        identity.update(
            {
                "type": "sub_agent",
                "prompt": self.prompt,
                "parent_agent": getattr(self.config, "parent_agent", None)
                or (self.parent_agent.name if self.parent_agent else None),
            }
        )
        return identity

    def set_parent_agent(self, parent_agent: "Agent"):
        """Set the parent agent for this sub-agent."""
        self.parent_agent = parent_agent
        # Store parent reference (config doesn't have parent_agent field anymore)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any], **kwargs) -> "SubAgent":
        """Create a SubAgent from a dictionary configuration."""
        from .agent import AgentConfig

        data = config_dict.copy()

        # Remove type and parent_agent fields if present
        data.pop("type", None)
        data.pop("parent_agent", None)

        # Ensure model field is properly structured
        if "model_provider" not in data and "model" in data:
            model_info = data.pop("model")
            if isinstance(model_info, dict):
                data["model_provider"] = model_info.get("provider", "google")
                data["model_name"] = model_info.get("name", "gemini-2.0-flash")

        return cls(AgentConfig(**data), **kwargs)

    @classmethod
    def from_file(cls, config_path: Union[str, Path], **kwargs) -> "SubAgent":
        """Create a SubAgent from a JSON configuration file."""
        return cls(config_path, **kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Convert SubAgent configuration to dictionary."""
        from dataclasses import asdict

        result = asdict(self.config)
        # Add type information for proper deserialization
        result["type"] = "sub_agent"
        if self.parent_agent:
            result["parent_agent"] = self.parent_agent.name
        return result

    def clone(self, **overrides) -> "SubAgent":
        """Create a clone of this sub-agent with optional overrides."""
        from dataclasses import asdict

        config_dict = asdict(self.config)
        config_dict.update(overrides)

        # Remove any non-config fields
        config_dict.pop("type", None)
        config_dict.pop("parent_agent", None)

        return SubAgent(
            AgentConfig(**config_dict),
            parent_agent=self.parent_agent,
            tool_registry=self.tool_registry,
            memory_manager=self.memory_manager,
            settings=self.settings,
        )
