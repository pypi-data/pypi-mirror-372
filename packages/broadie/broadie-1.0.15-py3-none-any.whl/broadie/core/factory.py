"""
Agent factory for creating Broadie agents with LangGraph integration.
Migrated from graph.py to provide centralized agent creation.
"""

from typing import Any, Callable, Dict, List, Optional, Sequence, Type, TypeVar, Union

from langchain_core.language_models import LanguageModelLike
from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent
from langgraph.types import Checkpointer

from broadie.config.settings import BroadieSettings
from broadie.core.interrupt import ToolInterruptConfig, create_interrupt_hook
from broadie.core.prompts import BASE_AGENT_PROMPT, format_task_description
from broadie.core.state import BroadieState
from broadie.tools import ToolRegistry, get_global_registry
from broadie.tools.builtin import (
    edit_file,
    ls_files,
    read_file,
    write_file,
    write_todos,
)
from broadie.utils.exceptions import AgentError, ConfigurationError

StateSchema = TypeVar("StateSchema", bound=BroadieState)
StateSchemaType = Type[StateSchema]


def _create_task_tool(
        tools: List[BaseTool],
        instructions: str,
        subagents: List[Dict[str, Any]],
        model: LanguageModelLike,
        state_schema: StateSchemaType,
        settings: Optional[BroadieSettings] = None,
):
    """
    Create task delegation tool for sub-agents.

    Args:
        tools: Available tools
        instructions: Main agent instructions
        subagents: Sub-agent configurations
        model: Language model to use
        state_schema: State schema type
        settings: Broadie settings

    Returns:
        Task tool for sub-agent delegation
    """
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import ToolMessage
    from langchain_core.tools import tool
    from langgraph.types import Command

    # Create agents dictionary for sub-agents
    agents = {
        "general-purpose": create_react_agent(
            model, prompt=instructions, tools=tools, checkpointer=False
        )
    }

    # Build tools by name mapping
    tools_by_name = {}
    for tool_ in tools:
        if not isinstance(tool_, BaseTool):
            from langchain_core.tools import tool as langchain_tool

            tool_ = langchain_tool(tool_)
        tools_by_name[tool_.name] = tool_

    # Create sub-agent executors
    for subagent in subagents:
        if "tools" in subagent:
            subagent_tools = [
                tools_by_name[t] for t in subagent["tools"] if t in tools_by_name
            ]
        else:
            subagent_tools = tools

        # Resolve per-subagent model if specified
        if "model_settings" in subagent:
            model_config = subagent["model_settings"]
            sub_model = init_chat_model(**model_config)
        else:
            sub_model = model

        agents[subagent["name"]] = create_react_agent(
            sub_model,
            prompt=subagent["prompt"],
            tools=subagent_tools,
            state_schema=state_schema,
            checkpointer=False,
        )

    # Format other agents description
    other_agents_list = [
        {"name": subagent["name"], "description": subagent["description"]}
        for subagent in subagents
    ]

    task_description = format_task_description(other_agents_list)

    @tool(description=task_description)
    async def task(
            description: str,
            subagent_type: str,
            state: BroadieState,
            tool_call_id: str,
    ):
        """Delegate task to a sub-agent."""
        if subagent_type not in agents:
            allowed_types = list(agents.keys())
            return f"Error: invoked agent of type {subagent_type}, the only allowed types are {allowed_types}"

        sub_agent = agents[subagent_type]

        # Prepare state for sub-agent
        task_state = {**state, "messages": [{"role": "user", "content": description}]}

        try:
            result = await sub_agent.ainvoke(task_state)

            return Command(
                update={
                    "files": result.get("files", state.get("files", {})),
                    "messages": [
                        ToolMessage(
                            (
                                result["messages"][-1].content
                                if result.get("messages")
                                else "Task completed"
                            ),
                            tool_call_id=tool_call_id,
                        )
                    ],
                }
            )
        except Exception as e:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            f"Error in sub-agent {subagent_type}: {str(e)}",
                            tool_call_id=tool_call_id,
                        )
                    ]
                }
            )

    return task


def create_broadie_agent(
        tools: Sequence[Union[BaseTool, Callable, Dict[str, Any]]],
        instructions: str,
        model: Optional[Union[str, LanguageModelLike]] = None,
        subagents: Optional[List[Dict[str, Any]]] = None,
        state_schema: Optional[StateSchemaType] = None,
        interrupt_config: Optional[ToolInterruptConfig] = None,
        config_schema: Optional[Type[Any]] = None,
        checkpointer: Optional[Checkpointer] = None,
        post_model_hook: Optional[Callable] = None,
        settings: Optional[BroadieSettings] = None,
        tool_registry: Optional[ToolRegistry] = None,
        backend=None,  # Add backend parameter
) -> Any:
    """
    Create a Broadie agent with enhanced capabilities.

    This agent includes built-in tools for todo management and file operations,
    plus any additional tools and sub-agents specified.

    Args:
        backend:
        tools: Additional tools the agent should have access to
        instructions: System instructions for the agent
        model: Language model to use (defaults to configured model)
        subagents: List of sub-agent configurations
        state_schema: State schema (defaults to BroadieState)
        interrupt_config: Tool interrupt configurations
        config_schema: Configuration schema
        checkpointer: State checkpointer for persistence
        post_model_hook: Custom post-processing hook
        settings: Broadie settings
        tool_registry: Tool registry to use

    Returns:
        Configured LangGraph agent

    Raises:
        AgentError: If agent creation fails
        ConfigurationError: If configuration is invalid
    """

    try:
        # Initialize defaults
        settings = settings or BroadieSettings()
        tool_registry = tool_registry or get_global_registry()
        state_schema = state_schema or BroadieState
        subagents = subagents or []

        # Build complete instruction prompt
        prompt = f"{instructions}\n\n{BASE_AGENT_PROMPT}"

        # Get built-in tools
        builtin_tools = [write_todos, write_file, read_file, ls_files, edit_file]

        # Add backend-dependent tools if backend is available
        if backend:
            from broadie.tools import (
                create_conversation_tools,
                create_memory_tools,
                create_todo_tools,
            )

            todo_tools = create_todo_tools(backend)
            memory_tools = create_memory_tools(backend)
            conversation_tools = create_conversation_tools(backend)
            builtin_tools.extend(todo_tools)
            builtin_tools.extend(memory_tools)
            builtin_tools.extend(conversation_tools)

        # Initialize model if needed
        if model is None:
            from broadie.core.model import get_default_model

            model = get_default_model()
        elif isinstance(model, str):
            from langchain.chat_models import init_chat_model

            model = init_chat_model(model)

        # Convert tools to BaseTool instances
        processed_tools = []
        for tool in tools:
            if isinstance(tool, str):
                # Get tool from registry
                registered_tool = tool_registry.get_tool(tool)
                if registered_tool is None:
                    raise ConfigurationError(f"Tool '{tool}' not found in registry")
                processed_tools.append(registered_tool.to_langchain_tool())
            elif isinstance(tool, BaseTool):
                processed_tools.append(tool)
            elif callable(tool):
                from langchain_core.tools import tool as langchain_tool

                processed_tools.append(langchain_tool(tool))
            elif isinstance(tool, dict):
                # Handle tool dict representation
                if "name" in tool and "function" in tool:
                    from langchain_core.tools import tool as langchain_tool

                    processed_tools.append(
                        langchain_tool(name=tool["name"])(tool["function"])
                    )
            else:
                raise ConfigurationError(f"Invalid tool type: {type(tool)}")

        # Create task delegation tool if there are sub-agents
        if subagents:
            task_tool = _create_task_tool(
                builtin_tools + processed_tools,
                instructions,
                subagents,
                model,
                state_schema,
                settings,
            )
            all_tools = builtin_tools + processed_tools + [task_tool]
        else:
            all_tools = builtin_tools + processed_tools

        # Handle post-model hooks and interrupts
        if post_model_hook and interrupt_config:
            raise ValueError(
                "Cannot specify both post_model_hook and interrupt_config together. "
                "Use either interrupt_config for tool interrupts or post_model_hook for custom post-processing."
            )
        elif post_model_hook is not None:
            selected_post_model_hook = post_model_hook
        elif interrupt_config is not None:
            selected_post_model_hook = create_interrupt_hook(interrupt_config)
        else:
            selected_post_model_hook = None

        # Create the agent
        agent = create_react_agent(
            model,
            prompt=prompt,
            tools=all_tools,
            state_schema=state_schema,
            post_model_hook=selected_post_model_hook,
            config_schema=config_schema,
            checkpointer=checkpointer,
        )

        return agent

    except Exception as e:
        raise AgentError(f"Failed to create Broadie agent: {str(e)}") from e


class AgentFactory:
    """
    Factory class for creating different types of Broadie agents.

    Provides convenient methods for creating pre-configured agent types
    and custom agent configurations.
    """

    def __init__(
            self,
            settings: Optional[BroadieSettings] = None,
            tool_registry: Optional[ToolRegistry] = None,
    ):
        self.settings = settings or BroadieSettings()
        self.tool_registry = tool_registry or get_global_registry()

    def create_agent(
            self,
            agent_type: str = "general",
            name: str = "broadie_agent",
            instructions: Optional[str] = None,
            tools: Optional[List[Union[str, BaseTool, Callable]]] = None,
            subagents: Optional[List[Dict[str, Any]]] = None,
            **kwargs,
    ) -> Any:
        """
        Create an agent of specified type.

        Args:
            agent_type: Type of agent (general, security, customer_support)
            name: Agent name
            instructions: Custom instructions (overrides type default)
            tools: Additional tools beyond built-ins
            subagents: Sub-agent configurations
            **kwargs: Additional arguments for create_broadie_agent

        Returns:
            Configured agent
        """

        # Get default instructions for agent type
        from broadie.core.prompts import AGENT_PROMPT_TEMPLATES

        if agent_type in AGENT_PROMPT_TEMPLATES:
            default_instructions = AGENT_PROMPT_TEMPLATES[agent_type]["instruction"]
            default_tools = AGENT_PROMPT_TEMPLATES[agent_type].get("tools", [])
        else:
            default_instructions = AGENT_PROMPT_TEMPLATES["general"]["instruction"]
            default_tools = []

        # Use provided instructions or defaults
        final_instructions = instructions or default_instructions

        # Combine default and provided tools
        final_tools = list(tools or [])
        final_tools.extend(default_tools)

        return create_broadie_agent(
            tools=final_tools,
            instructions=final_instructions,
            subagents=subagents,
            settings=self.settings,
            tool_registry=self.tool_registry,
            **kwargs,
        )

    def create_security_agent(
            self,
            name: str = "security_agent",
            additional_tools: Optional[List[str]] = None,
            **kwargs,
    ) -> Any:
        """Create a security-focused agent."""
        tools = ["analyze_threat", "recommend_mitigation", "generate_security_report"]
        if additional_tools:
            tools.extend(additional_tools)

        return self.create_agent(
            agent_type="security", name=name, tools=tools, **kwargs
        )

    def create_support_agent(
            self,
            name: str = "support_agent",
            additional_tools: Optional[List[str]] = None,
            **kwargs,
    ) -> Any:
        """Create a customer support agent."""
        tools = ["lookup_customer", "create_ticket", "escalate_issue"]
        if additional_tools:
            tools.extend(additional_tools)

        return self.create_agent(
            agent_type="customer_support", name=name, tools=tools, **kwargs
        )

    def create_general_agent(
            self, name: str = "general_agent", tools: Optional[List[str]] = None, **kwargs
    ) -> Any:
        """Create a general-purpose agent."""
        return self.create_agent(
            agent_type="general", name=name, tools=tools or [], **kwargs
        )


# Convenience functions
def create_agent_from_config(
        config: Dict[str, Any],
        settings: Optional[BroadieSettings] = None,
        tool_registry: Optional[ToolRegistry] = None,
) -> Any:
    """
    Create agent from configuration dictionary.

    Args:
        config: Agent configuration
        settings: Broadie settings
        tool_registry: Tool registry

    Returns:
        Configured agent
    """
    factory = AgentFactory(settings, tool_registry)

    return create_broadie_agent(
        tools=config.get("tools", []),
        instructions=config.get("instruction", ""),
        subagents=config.get("subagents", []),
        settings=settings,
        tool_registry=tool_registry,
    )
