"""
Core Agent implementation integrating existing functionality.
Enhanced with LangGraph, memory, and state management capabilities.
"""

import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

# Click for interactive chat UI (always present)
import click
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.store.memory import InMemoryStore

# LangMem tools (assume langmem is always installed)
from langmem import (
    create_manage_memory_tool,
    create_memory_store_manager,
    create_search_memory_tool,
)

from broadie.config.settings import BroadieSettings
from broadie.core.destinations import DestinationResolver
from broadie.core.factory import create_broadie_agent
from broadie.core.memory import MemoryManager
from broadie.core.response_context import (
    ResponseChannel,
    ResponseContent,
    ResponseContext,
    ResponseManager,
    create_api_context,
    create_cli_context,
    create_web_ui_context,
    get_response_context,
    set_response_context,
)
from broadie.core.state import DatabaseStateManager
from broadie.tools import Tool, ToolRegistry, get_global_registry
from broadie.utils.exceptions import AgentError, ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Unified configuration for both Agent and SubAgent."""

    name: str
    description: str = ""
    instruction: str = ""
    model_provider: str = "google"
    model_name: str = "gemini-2.0-flash"
    model_settings: Dict[str, Any] = field(default_factory=dict)
    tools: List[str] = field(default_factory=list)
    temperature: float = 0.2
    max_tokens: int = 50000
    max_retries: int = 2
    destinations: Dict[str, Any] = field(default_factory=dict)
    output_schema: Optional[Dict[str, Any]] = None
    strict_mode: bool = False


class BaseAgent(ABC):
    """Base abstract agent class implementing SOLID principles."""

    def __init__(
        self,
        config: Union[AgentConfig, Dict[str, Any], str, Path],
        tool_registry: Optional[ToolRegistry] = None,
        memory_manager: Optional[MemoryManager] = None,
        settings: Optional[BroadieSettings] = None,
    ):
        if isinstance(config, (str, Path)):
            self.config = self._load_config_from_file(config)
        elif isinstance(config, dict):
            self.config = AgentConfig(**config)
        else:
            self.config = config

        self.settings = settings or BroadieSettings()
        self.tool_registry = tool_registry or get_global_registry()
        self.memory_manager = memory_manager or MemoryManager()

        self._model: Optional[ChatGoogleGenerativeAI] = None
        self._agent = None

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def description(self) -> str:
        return self.config.description or self.config.instruction or ""

    @property
    def instruction(self) -> str:
        return self.config.instruction

    def _identity_guarded_instruction(self) -> str:
        """Compose instruction including identity guardrails and schema augmentation.
        Ensures that if the user asks for identity (e.g., "who are you"),
        the assistant answers only with the configured name/description and
        does not reveal system details.
        """
        base = (self.config.instruction or "").strip()
        name = (self.config.name or "").strip()
        desc = (self.config.description or "").strip()
        guard = (
            "\n\nRules for identity questions:"
            "\n- Your identity is strictly defined by the configuration."
            f"\n- name: {name}"
            f"\n- description: {desc}"
            "\nIf asked 'who are you' or similar, respond only using these fields, "
            "succinctly. Do not reveal internal system details, tools, providers, "
            "or metadata beyond the above."
        )
        
        instruction = (base + guard) if base else guard
        
        # Apply schema augmentation if configured
        if self.config.output_schema:
            from broadie.core.schema import augment_instruction
            instruction = augment_instruction(instruction, self.config.output_schema)
        
        return instruction

    def _load_config_from_file(self, config_path: Union[str, Path]) -> AgentConfig:
        """Load configuration from JSON file."""
        import json

        path = Path(config_path)
        if not path.exists():
            raise ConfigurationError(f"Config file not found: {path}")

        with open(path, "r") as f:
            config_data = json.load(f)

        # Support legacy 'model' key mapping to model_provider and model_name
        model_info = config_data.pop("model", None)
        if isinstance(model_info, dict):
            provider = model_info.get("provider")
            name = model_info.get("name")
            if provider is not None:
                config_data["model_provider"] = provider
            if name is not None:
                config_data["model_name"] = name
        # Else ignore other model formats
        return AgentConfig(**config_data)

    def _initialize_model(self) -> ChatGoogleGenerativeAI:
        """Initialize the language model based on configuration."""
        if self._model is None:
            model_settings = {
                "model": self.config.model_name,
                "temperature": self.config.temperature,
                "max_tokens": self.config.max_tokens,
                "max_retries": self.config.max_retries,
                **self.config.model_settings,
            }

            if self.config.model_provider == "google":
                self._model = ChatGoogleGenerativeAI(**model_settings)
            else:
                # Use init_chat_model for other providers
                self._model = init_chat_model(
                    model=self.config.model_name,
                    model_provider=self.config.model_provider,
                    **model_settings,
                )

        return self._model

    def _get_tools(self) -> List[Tool]:
        """Get tools for this agent."""
        tools = []

        # Always include built-in tools
        builtin_tools = self.tool_registry.get_tools_by_category("builtin")
        tools.extend(builtin_tools)

        # Always include integration tools if available
        try:
            google_tools = self.tool_registry.get_tools_by_category("google_drive")
            tools.extend(google_tools)
        except Exception as e:
            pass  # Integration tools are optional

        try:
            slack_tools = self.tool_registry.get_tools_by_category("slack")
            tools.extend(slack_tools)
        except Exception as e:
            pass  # Integration tools are optional

        # Always include notification tools if available
        try:
            notification_tools = self.tool_registry.get_tools_by_category(
                "notifications"
            )
            tools.extend(notification_tools)
        except Exception as e:
            pass  # Notification tools are optional

        # Add any explicitly configured tools
        if self.config.tools:
            for tool_name in self.config.tools:
                tool = self.tool_registry.get_tool(tool_name)
                if tool is None:
                    raise ConfigurationError(
                        f"Tool '{tool_name}' not found in registry"
                    )
                # Avoid duplicates
                if tool not in tools:
                    tools.append(tool)

        return tools

    def _initialize_agent(self):
        """Initialize the LangGraph agent."""
        if self._agent is None:
            model = self._initialize_model()
            # Convert tools to LangChain BaseTool objects
            registry_tools = self._get_tools()
            langchain_tools = [tool.to_langchain_tool() for tool in registry_tools]
            prompt_text = self._identity_guarded_instruction()

            self._agent = create_react_agent(
                model, tools=langchain_tools, prompt=prompt_text, checkpointer=False
            )

        return self._agent

    @abstractmethod
    async def process_message(self, message: str) -> str:
        """Process a message and return a response."""
        pass

    async def invoke(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Invoke the agent with a message."""
        try:
            agent = self._initialize_agent()

            state = {
                "messages": [HumanMessage(content=message)],
                "files": context.get("files", {}) if context else {},
            }

            result = await agent.ainvoke(state)

            return {
                "response": (
                    result["messages"][-1].content if result["messages"] else ""
                ),
                "files": result.get("files", {}),
                "messages": result.get("messages", []),
            }

        except Exception as e:
            raise AgentError(f"Error invoking agent '{self.name}': {str(e)}") from e

    def get_identity(self) -> Dict[str, Any]:
        """Get agent identity for A2A communication."""
        return {
            "name": self.config.name,
            "instruction": self.config.instruction,
            "tools": self.config.tools,
            "model": {
                "provider": self.config.model_provider,
                "name": self.config.model_name,
            },
        }


class Agent(BaseAgent):
    """
    Main Agent implementation with enhanced capabilities.

    Integrates functionality from base_agents.py with LangGraph execution,
    memory management, and state persistence.

    Usage:
        @tool
        def my_function():
            return "result"

        agent = Agent("my_agent", "You are helpful")
        # Automatically discovers @tool decorated functions
    """

    def build_config(self) -> Union[AgentConfig, Dict[str, Any], Path]:
        """
        Return the configuration for this agent when instantiated without parameters.
        Should return an AgentConfig instance, a dict, or a path to a JSON config file.
        """
        raise NotImplementedError("build_config() must be implemented by subclasses")

    def __init__(
        self,
        config: Optional[Union[AgentConfig, Dict[str, Any], Path]] = None,
        *,
        name: Optional[str] = None,
        instruction: Optional[str] = None,
        tools: Optional[List[str]] = None,
        subagents: Optional[List[Union["SubAgent", Dict[str, Any]]]] = None,
        memory_namespace: Optional[str] = None,
        **kwargs,
    ):
        # Handle explicit parameters vs config or via build_config
        if config is not None:
            if isinstance(config, (str, Path)):
                agent_config = self._load_config_from_file(config)
            elif isinstance(config, dict):
                agent_config = AgentConfig(**config)
            else:
                agent_config = config
        else:
            # Delegate to subclass-provided configuration
            try:
                config_data = self.build_config()
            except Exception as e:
                raise ConfigurationError(
                    "Agent must be configured via the 'config' parameter or build_config() method; name-based init is not supported"
                ) from e
            if isinstance(config_data, (str, Path)):
                agent_config = self._load_config_from_file(config_data)
            elif isinstance(config_data, dict):
                agent_config = AgentConfig(**config_data)
            else:
                agent_config = config_data
        super().__init__(agent_config, **kwargs)

        # Merge description/instruction for compatibility
        if not self.config.instruction and getattr(self.config, "description", None):
            self.config.instruction = self.config.description
        if not self.config.description and getattr(self.config, "instruction", None):
            self.config.description = self.config.instruction

        # Override tools if explicitly provided
        if tools is not None:
            self.config.tools = tools

        # Auto-discover tools from global registry if no explicit tools
        if not self.config.tools:
            self._auto_discover_tools()

        # Sub-agents management
        self.sub_agents: Dict[str, "SubAgent"] = {}
        if subagents:
            for sub_agent in subagents:
                if isinstance(sub_agent, dict):
                    # Convert dict to SubAgent
                    from .subagent import SubAgent

                    sub_agent = SubAgent(sub_agent)
                self.add_sub_agent(sub_agent)

        # Memory and persistence setup
        self.memory_namespace = memory_namespace or f"agent_{self.name}"
        self.store = InMemoryStore()
        self.checkpointer = MemorySaver()

        # Build enhanced tools list with memory tools (will be rebuilt dynamically)
        self._enhanced_tools = None

        # Create LangGraph agent
        self._langgraph_agent = None

        # Initialize destination resolver for notifications
        # Pass the destinations configuration dict to the resolver
        destinations_config = (
            {"destinations": self.config.destinations}
            if self.config.destinations
            else {}
        )
        self.destination_resolver = DestinationResolver(self.name, destinations_config)

        # Initialize response manager for context-aware responses
        self.response_manager = ResponseManager()

    def _auto_discover_tools(self):
        """Auto-discover tools decorated with @tool in the current module context."""
        import inspect

        # Get the calling module (where Agent is instantiated)
        frame = inspect.currentframe()
        try:
            # Go up the call stack to find the module where Agent() was called
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

    def _build_enhanced_tools(self) -> List[BaseTool]:
        """Build comprehensive tools list including memory tools."""
        tools = []

        # Set agent context for notification tools
        try:
            from broadie.tools.notifications import set_agent_context

            set_agent_context(self)
        except ImportError:
            pass  # Notification tools not available

        # Get all tools (including built-ins and integrations automatically)
        agent_tools = self._get_tools()
        for tool in agent_tools:
            tools.append(tool.to_langchain_tool())

        # Ensure a memory store exists for this agent's namespace
        try:
            create_memory_store_manager(namespace=(self.memory_namespace,))
        except Exception:
            pass
        # Attach memory management and search tools
        tools.extend(
            [
                create_manage_memory_tool(namespace=(self.memory_namespace,)),
                create_search_memory_tool(namespace=(self.memory_namespace,)),
            ]
        )

        return tools

    @property
    def enhanced_tools(self) -> List[BaseTool]:
        """Get enhanced tools list, building it if necessary."""
        if self._enhanced_tools is None:
            self._enhanced_tools = self._build_enhanced_tools()
        return self._enhanced_tools

    def _create_langgraph_agent(self):
        """Create the LangGraph agent with full configuration."""
        if self._langgraph_agent is None:
            # Prepare sub-agents for task delegation
            subagents_config = [
                sub_agent.to_dict() for sub_agent in self.sub_agents.values()
            ]

            self._langgraph_agent = create_broadie_agent(
                tools=self.enhanced_tools,
                instructions=self._identity_guarded_instruction(),
                model=self._initialize_model(),
                subagents=subagents_config,
                checkpointer=self.checkpointer,
                settings=self.settings,
                tool_registry=self.tool_registry,
                backend=getattr(self, "backend", None),
            )

        return self._langgraph_agent

    def add_sub_agent(self, sub_agent: "SubAgent"):
        """Add a sub-agent to this agent."""
        self.sub_agents[sub_agent.name] = sub_agent
        sub_agent.set_parent_agent(self)
        # Reset LangGraph agent to include new sub-agent
        self._langgraph_agent = None

    def remove_sub_agent(self, name: str):
        """Remove a sub-agent by name."""
        if name in self.sub_agents:
            del self.sub_agents[name]
            # Reset LangGraph agent to exclude removed sub-agent
            self._langgraph_agent = None

    def get_sub_agent(self, name: str) -> Optional["SubAgent"]:
        """Get a sub-agent by name."""
        return self.sub_agents.get(name)

    def run(self, initial_message: Optional[str] = None):
        """Run the agent in an interactive loop."""
        conversation_id = str(uuid.uuid4())
        config = {
            "configurable": {"thread_id": conversation_id}
        }  # LangGraph still uses thread_id internally

        # Set CLI response context with enabled notifications only
        notification_channels = []
        if hasattr(self, "destination_resolver"):
            for dest_name in self.list_destinations():
                dest_config = self.destination_resolver.destinations.get_destination(
                    dest_name
                )
                if dest_config and dest_config.enabled:
                    notification_channels.append(dest_name)
        cli_context = create_cli_context(
            agent_name=self.name, notification_channels=notification_channels
        )
        set_response_context(cli_context)

        # Welcome banner
        click.secho(f"{self.name} Started! Type 'quit' to exit.", fg="green", bold=True)
        click.secho("-" * 50)
        if self.instruction:
            click.secho(f"Instruction: {self.instruction}", fg="yellow")
        click.secho(f"Conversation ID: {conversation_id}", fg="blue")
        if notification_channels:
            click.secho(
                f"Notifications enabled for: {', '.join(notification_channels)}",
                fg="cyan",
            )
        click.secho("-" * 50)
        if initial_message:
            click.secho(f"System: {initial_message}", fg="magenta")

        agent = self._create_langgraph_agent()

        # Main REPL loop
        while True:
            try:
                user_input = click.prompt(
                    click.style("You", fg="blue", bold=True), prompt_suffix=": "
                ).strip()
                if user_input.lower() in ("quit", "exit", "q"):
                    click.secho("Goodbye!", fg="green")
                    break
                if not user_input:
                    continue

                # Update context with conversation details
                cli_context.conversation_id = conversation_id
                cli_context.metadata["timestamp"] = datetime.utcnow().isoformat()

                # Store user message
                user_ts = datetime.utcnow().isoformat()
                asyncio.run(
                    self.backend.store_message(
                        conversation_id, "user", "user", user_input, user_ts
                    )
                )

                click.secho(f"{self.name}:", fg="green", bold=True, nl=False)
                click.echo(" ", nl=False)  # Add space after agent name
                response_text = ""
                assistant_started = False

                for chunk in agent.stream(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config=config,
                    stream_mode="values",
                ):
                    messages = chunk.get("messages", [])
                    if messages:
                        last_msg = messages[-1]

                        # Check message type/role to filter out user echo
                        msg_type = getattr(last_msg, "type", "")
                        msg_role = getattr(
                            last_msg, "__class__", type(last_msg)
                        ).__name__
                        content = getattr(last_msg, "content", "")

                        # Skip user messages - only show AI/assistant responses
                        is_assistant_msg = (
                            msg_type == "ai"
                            or "AI" in msg_role
                            or "Assistant" in msg_role
                            or (
                                content and content != user_input
                            )  # Skip if it's echoing user input
                        )

                        if is_assistant_msg and content:
                            # Only add new content (incremental streaming)
                            if len(content) > len(response_text):
                                new_text = content[len(response_text) :]
                                if new_text.strip():  # Only display non-empty content
                                    click.secho(new_text, fg="white", nl=False)
                                response_text = content

                click.echo()  # New line after response

                # Handle dual response: CLI display + optional notifications
                # Notifications are handled automatically by notification tools if agent uses them

                # Store the assistant response in database
                # Create state manager for persistence
                state_manager = DatabaseStateManager(self.backend)

                # Store the message (run async in sync context)
                resp_ts = datetime.utcnow().isoformat()
                message_id = asyncio.run(
                    state_manager.store_message_with_todos(
                        conversation_id=conversation_id,
                        agent_id=self.name,
                        role="assistant",
                        content=response_text,
                        timestamp=resp_ts,
                    )
                )

                # Get recent todos for display
                recent_todos = asyncio.run(
                    self.backend.get_todos(conversation_id=conversation_id)
                )
                if recent_todos:
                    click.echo()
                    click.secho("📋 Todos:", fg="yellow", bold=True)
                    for todo in recent_todos[-3:]:  # Show last 3 todos
                        status_icon = (
                            "✅"
                            if todo["status"] == "done"
                            else "⏳" if todo["status"] == "in_progress" else "📌"
                        )
                        todo_color = (
                            "green"
                            if todo["status"] == "done"
                            else "yellow" if todo["status"] == "in_progress" else "cyan"
                        )
                        click.secho(
                            f"  {status_icon} {todo['description']}", fg=todo_color
                        )
                    if len(recent_todos) > 3:
                        click.secho(f"  ... and {len(recent_todos) - 3} more", fg="dim")

            except KeyboardInterrupt:
                click.secho("Goodbye!", fg="green")
                break
            except Exception as e:
                click.secho(f"Error: {e}", fg="red")
                continue

    def invoke(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Invoke the agent with a single message."""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        # LangGraph still uses thread_id internally for checkpointing
        config = {"configurable": {"thread_id": conversation_id}}
        agent = self._create_langgraph_agent()

        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )

            # Extract response content
            messages = response.get("messages", [])
            raw_response = ""
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    raw_response = last_message.content
                else:
                    raw_response = str(last_message)
            else:
                raw_response = "No response generated"

            # Apply schema processing if configured
            if self.config.output_schema or any(self.destination_resolver.list_destinations()):
                return self._process_schema_response_sync(raw_response, conversation_id)
            else:
                # Return raw response for non-schema agents
                return raw_response

        except Exception as e:
            raise AgentError(f"Error invoking agent '{self.name}': {str(e)}") from e

    async def ainvoke(self, message: str, conversation_id: Optional[str] = None) -> str:
        """Async version of invoke for use in async contexts like FastAPI."""
        if conversation_id is None:
            conversation_id = str(uuid.uuid4())

        # LangGraph still uses thread_id internally for checkpointing
        config = {"configurable": {"thread_id": conversation_id}}
        agent = self._create_langgraph_agent()

        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )

            # Extract response content
            messages = response.get("messages", [])
            raw_response = ""
            if messages:
                last_message = messages[-1]
                if hasattr(last_message, "content"):
                    raw_response = last_message.content
                else:
                    raw_response = str(last_message)
            else:
                raw_response = "No response generated"

            # Apply schema processing if configured
            if self.config.output_schema or any(self.destination_resolver.list_destinations()):
                return await self._process_schema_response(raw_response, conversation_id)
            else:
                # Return raw response for non-schema agents
                return raw_response

        except Exception as e:
            raise AgentError(f"Error invoking agent '{self.name}': {str(e)}") from e
    
    def _process_schema_response_sync(self, raw_response: str, conversation_id: str) -> str:
        """Process response through schema validation and rendering pipeline (synchronous version)."""
        try:
            from broadie.core.schema import SchemaManager, build_envelope, extract_json_from_response
            import json
            
            # Extract JSON from response
            payload = extract_json_from_response(raw_response)
            
            # Validate against schema if configured
            schema_manager = SchemaManager(self.config.output_schema)
            validated_payload = schema_manager.validate(payload, self.config.strict_mode)
            
            # Build envelope
            envelope = build_envelope(
                agent_name=self.name,
                schema_name=schema_manager.schema_name,
                payload=validated_payload,
                metadata={
                    "conversation_id": conversation_id,
                    "should_send": True,
                    "tier_label": "INFORMATIONAL"
                }
            )
            
            # For sync version, we'll skip the async dispatch for now
            # This ensures compatibility with both sync and async contexts
            enabled_destinations = [d for d in self.destination_resolver.list_destinations() 
                                  if self.destination_resolver.has_destination(d)]
            
            if enabled_destinations:
                logger.info(f"Schema processing complete. Destinations configured: {enabled_destinations}")
                # TODO: Implement sync dispatch or defer to async version
                
            # Return envelope as JSON for API consumers
            return json.dumps(envelope, indent=2)
            
        except Exception as e:
            logger.error(f"Schema processing failed: {e}")
            # Fallback to raw response
            return raw_response

    async def _process_schema_response(self, raw_response: str, conversation_id: str) -> str:
        """Process response through schema validation and rendering pipeline (async version)."""
        try:
            from broadie.core.schema import SchemaManager, build_envelope, extract_json_from_response
            from broadie.core.dispatch import EnvelopeDispatcher
            from broadie.core.renderer_agent import create_renderer_agent
            
            # Extract JSON from response
            payload = extract_json_from_response(raw_response)
            
            # Validate against schema if configured
            schema_manager = SchemaManager(self.config.output_schema)
            validated_payload = schema_manager.validate(payload, self.config.strict_mode)
            
            # Build envelope
            envelope = build_envelope(
                agent_name=self.name,
                schema_name=schema_manager.schema_name,
                payload=validated_payload,
                metadata={
                    "conversation_id": conversation_id,
                    "should_send": True,
                    "tier_label": "INFORMATIONAL"
                }
            )
            
            # Dispatch to destinations if any are configured
            enabled_destinations = [d for d in self.destination_resolver.list_destinations() 
                                  if self.destination_resolver.has_destination(d)]
            
            if enabled_destinations:
                # Create renderer agent as sub-agent
                renderer_agent = create_renderer_agent(parent_agent=self)
                self.add_sub_agent(renderer_agent)
                
                # Create dispatcher and dispatch
                dispatcher = EnvelopeDispatcher(self.destination_resolver, renderer_agent)
                dispatch_result = await dispatcher.dispatch(envelope)
                
                logger.info(f"Dispatched to {dispatch_result['successful_dispatches']}/{dispatch_result['total_destinations']} destinations")
            
            # Return envelope as JSON for API consumers
            import json
            return json.dumps(envelope, indent=2)
            
        except Exception as e:
            logger.error(f"Schema processing failed: {e}")
            # Fallback to raw response
            return raw_response

    def stream(self, message: str, thread_id: Optional[str] = None):
        """Stream responses from the agent."""
        if thread_id is None:
            thread_id = str(uuid.uuid4())

        config = {"configurable": {"thread_id": thread_id}}
        agent = self._create_langgraph_agent()

        try:
            for chunk in agent.stream(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
                stream_mode="values",
            ):
                yield chunk
        except Exception as e:
            raise AgentError(
                f"Error streaming from agent '{self.name}': {str(e)}"
            ) from e

    async def process_message(
        self, message: str, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Process a message using the main agent."""
        thread_id = context.get("thread_id") if context else None
        return self.invoke(message, thread_id)

    async def delegate_to_sub_agent(
        self,
        sub_agent_name: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Delegate a task to a specific sub-agent."""
        sub_agent = self.get_sub_agent(sub_agent_name)
        if sub_agent is None:
            raise AgentError(f"Sub-agent '{sub_agent_name}' not found")

        return await sub_agent.process_message(message, context)

    def list_sub_agents(self) -> List[str]:
        """List all sub-agent names."""
        return list(self.sub_agents.keys())

    def get_identity(self) -> Dict[str, Any]:
        """Get agent identity including sub-agents."""
        identity = super().get_identity()
        identity["sub_agents"] = [
            sub_agent.get_identity() for sub_agent in self.sub_agents.values()
        ]
        identity["memory_namespace"] = self.memory_namespace
        identity["has_persistence"] = bool(self.checkpointer)
        return identity

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        from dataclasses import asdict

        result = asdict(self.config)
        # Add agent-specific fields
        result.update(
            {
                "type": "agent",
                "sub_agents": [
                    sub_agent.to_dict() for sub_agent in self.sub_agents.values()
                ],
                "memory_namespace": self.memory_namespace,
            }
        )
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any], **kwargs) -> "Agent":
        """Create agent from dictionary representation."""
        config_data = data.copy()
        sub_agents_data = config_data.pop("sub_agents", [])
        memory_namespace = config_data.pop("memory_namespace", None)
        # Remove type field if present
        config_data.pop("type", None)

        # Ensure model field is properly structured
        if "model_provider" not in config_data and "model" in config_data:
            model_info = config_data.pop("model")
            if isinstance(model_info, dict):
                config_data["model_provider"] = model_info.get("provider", "google")
                config_data["model_name"] = model_info.get("name", "gemini-2.0-flash")

        # Create sub-agents
        from .subagent import SubAgent

        sub_agents = [SubAgent.from_dict(sa_data) for sa_data in sub_agents_data]

        return cls(
            config=AgentConfig(**config_data),
            subagents=sub_agents,
            memory_namespace=memory_namespace,
            **kwargs,
        )

    # Notification methods using the destination system
    async def respond(
        self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Send a response message to the primary destination."""
        from broadie.core.destinations.models import DeliveryResult

        return await self.destination_resolver.send(
            message, destination_type="primary", context=context, **kwargs
        )

    async def escalate(
        self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Send an escalation message to the escalation destination."""
        from broadie.core.destinations.models import DeliveryResult

        return await self.destination_resolver.send(
            message,
            destination_type="escalation",
            context=context,
            severity="high",
            **kwargs,
        )

    async def notify(
        self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Send a notification message to the notifications destination."""
        from broadie.core.destinations.models import DeliveryResult

        return await self.destination_resolver.send(
            message, destination_type="notifications", context=context, **kwargs
        )

    async def alert(
        self, message: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ):
        """Send an alert message to the alerts destination."""
        from broadie.core.destinations.models import DeliveryResult

        return await self.destination_resolver.send(
            message,
            destination_type="alerts",
            context=context,
            severity="critical",
            **kwargs,
        )

    async def broadcast(
        self,
        message: str,
        destinations: List[str],
        context: Optional[Dict[str, Any]] = None,
    ):
        """Broadcast a message to multiple destinations concurrently."""
        from broadie.core.destinations.models import BroadcastResult

        return await self.destination_resolver.broadcast(
            message, destinations, context=context
        )

    async def test_destinations(self) -> Dict[str, bool]:
        """Test connectivity to all configured destinations."""
        return await self.destination_resolver.test_destinations()

    def get_destination_info(self) -> Dict[str, Any]:
        """Get information about all configured destinations."""
        return self.destination_resolver.get_destination_info()

    def has_destination(self, destination_type: str) -> bool:
        """Check if a destination type is configured."""
        return self.destination_resolver.has_destination(destination_type)

    def list_destinations(self) -> List[str]:
        """List all available destination names."""
        return self.destination_resolver.list_destinations()


# Convenience functions for easy agent creation
def agent(
    name: str,
    instruction: str = None,
    tools: List[Union[str, Callable]] = None,
    sub_agents: List[Union[Dict, "SubAgent"]] = None,
    **kwargs,
) -> Agent:
    """
    Create an agent with minimal configuration.

    Args:
        name: Agent name
        instruction: System instruction (optional, uses default if not provided)
        tools: List of tool names or functions
        sub_agents: List of sub-agent configs or SubAgent instances
        **kwargs: Additional configuration options

    Returns:
        Configured Agent

    Example:
        agent = agent("my_agent", "You are helpful", tools=["analyze_data"])
    """
    # Auto-register function tools
    tool_names = []
    if tools:
        registry = get_global_registry()
        for tool in tools:
            if callable(tool):
                # Auto-register the function
                tool_instance = registry.register_function(tool)
                tool_names.append(tool_instance.name)
            else:
                tool_names.append(str(tool))

    # Convert sub-agent dicts to SubAgent instances
    processed_sub_agents = []
    if sub_agents:
        for sa in sub_agents:
            if isinstance(sa, dict):
                processed_sub_agents.append(subagent(**sa))
            else:
                processed_sub_agents.append(sa)

    config = AgentConfig(
        name=name,
        instruction=instruction or f"You are {name}, a helpful AI assistant.",
        tools=tool_names,
        **kwargs,
    )

    return Agent(config, sub_agents=processed_sub_agents)


def subagent(
    name: str,
    description: str = "",
    prompt: str = None,
    tools: List[Union[str, Callable]] = None,
    **kwargs,
) -> "SubAgent":
    """
    Create a sub-agent with minimal configuration.

    Args:
        name: Sub-agent name
        description: Description for task delegation
        prompt: System prompt (optional, uses default if not provided)
        tools: List of tool names or functions
        **kwargs: Additional configuration options

    Returns:
        Configured SubAgent

    Example:
        sa = subagent("analyzer", "Analyzes data", tools=[analyze_func])
    """
    # Import here to avoid circular import
    from .subagent import SubAgent

    # Auto-register function tools
    tool_names = []
    if tools:
        registry = get_global_registry()
        for tool in tools:
            if callable(tool):
                # Auto-register the function
                tool_instance = registry.register_function(tool)
                tool_names.append(tool_instance.name)
            else:
                tool_names.append(str(tool))

    config = AgentConfig(
        name=name,
        description=description,
        instruction=prompt or f"You are {name}, a specialized assistant. {description}",
        tools=tool_names,
        **kwargs,
    )

    return SubAgent(config)
