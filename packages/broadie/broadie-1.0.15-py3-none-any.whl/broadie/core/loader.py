"""
Agent loading utilities for Broadie.

Provides utilities to load agents from JSON configuration files or
Python module:class references.
"""

import importlib
import os
import sys
from pathlib import Path
from typing import Union

from broadie.core.agent import Agent


def load_agent_from_config_or_module(config_or_agent: str) -> Agent:
    """
    Load an agent from either a JSON config file or a Python module:class reference.

    Args:
        config_or_agent: Either a path to JSON config file or "module.path:AgentClass"

    Returns:
        Loaded Agent instance

    Raises:
        ImportError: If module or class cannot be loaded
        FileNotFoundError: If JSON config file doesn't exist

    Examples:
        # Load from JSON config
        agent = load_agent_from_config_or_module("agents/my_agent.json")

        # Load from Python class
        agent = load_agent_from_config_or_module("my_module:MyAgent")
    """
    if ":" in config_or_agent:
        # Format: module.path:AgentClass
        return _load_agent_from_module(config_or_agent)
    else:
        # Assume it's a JSON config file
        return _load_agent_from_json(config_or_agent)


def _load_agent_from_module(module_class_ref: str) -> Agent:
    """Load agent from Python module:class reference."""
    module_path, class_name = module_class_ref.split(":", 1)

    # Add current directory to path
    sys.path.insert(0, os.getcwd())

    try:
        module = importlib.import_module(module_path)
        obj = getattr(module, class_name)
        # If it's already an Agent instance, return it directly
        if isinstance(obj, Agent):
            return obj
        # If it's callable (Agent subclass or factory), call it
        if callable(obj):
            instance = obj()
            if isinstance(instance, Agent):
                return instance
            else:
                raise ImportError(
                    f"Callable '{class_name}' from module '{module_path}' did not return an Agent instance"
                )
        # Otherwise, invalid object
        raise ImportError(
            f"Object '{class_name}' in module '{module_path}' is not callable or an Agent instance"
        )
    except (ImportError, AttributeError) as e:
        raise ImportError(
            f"Could not load agent '{class_name}' from module '{module_path}': {e}"
        ) from e


def _load_agent_from_json(config_path: str) -> Agent:
    """Load agent from JSON configuration file."""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    # Load agent from JSON config
    agent = Agent(config_file)
    return agent


def discover_agent_from_directory(directory: Path = None) -> Agent:
    """
    Discover and load an agent from a directory.

    Looks for common patterns:
    1. agent.py with create_agents_from_json() or create_agents_in_code()
    2. main.json, main_agent.json, or first .json file in agents/

    Args:
        directory: Directory to search (defaults to current directory)

    Returns:
        Loaded Agent instance

    Raises:
        ImportError: If no suitable agent can be found
    """
    if directory is None:
        directory = Path.cwd()

    # Try loading from agent.py
    agent_py = directory / "agent.py"
    if agent_py.exists():
        try:
            sys.path.insert(0, str(directory))
            agent_mod = importlib.import_module("agent")

            # Try different creation functions
            creation_functions = [
                "create_agents_from_json",
                "create_agents_in_code",
                "create_agent",
                "main",
            ]

            for func_name in creation_functions:
                if hasattr(agent_mod, func_name):
                    func = getattr(agent_mod, func_name)
                    if callable(func):
                        agent = func()
                        if isinstance(agent, Agent):
                            return agent

        except Exception as e:
            # Continue to try JSON files
            pass

    # Try loading from JSON configs
    agents_dir = directory / "agents"
    if agents_dir.exists():
        # Look for common config names
        common_names = ["main.json", "main_agent.json", "agent.json"]

        for name in common_names:
            config_file = agents_dir / name
            if config_file.exists():
                return _load_agent_from_json(str(config_file))

        # Try the first .json file
        json_files = list(agents_dir.glob("*.json"))
        if json_files:
            return _load_agent_from_json(str(json_files[0]))

    # Try JSON files in root directory
    root_configs = ["main.json", "agent.json", "config.json"]
    for name in root_configs:
        config_file = directory / name
        if config_file.exists():
            return _load_agent_from_json(str(config_file))

    raise ImportError(
        f"No agent found in {directory}. "
        "Expected agent.py with creation function or JSON config file."
    )
