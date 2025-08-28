"""
Broadie CLI for project initialization and management.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

from broadie.cli.scaffold import (
    AVAILABLE_TEMPLATES,
    create_agent_config,
    create_subagent_config,
    scaffold_project,
)
from broadie.core.loader import (
    discover_agent_from_directory,
    load_agent_from_config_or_module,
)


def init_project(template_name: str = "simple"):
    """Initialize a new Broadie project with the specified template."""
    if template_name not in AVAILABLE_TEMPLATES:
        print(f"❌ Unknown template: {template_name}")
        print(f"Available templates: {', '.join(AVAILABLE_TEMPLATES.keys())}")
        return

    template = AVAILABLE_TEMPLATES[template_name]
    print(f"🚀 Initializing Broadie Project ({template.description})...")
    print()

    # Check if files already exist
    existing_files = []
    files_to_create = ["agents", "agent.py", ".env.example", "README.md"]

    for file in files_to_create:
        if Path(file).exists():
            existing_files.append(file)

    if existing_files:
        print("⚠️  The following files already exist:")
        for file in existing_files:
            print(f"   - {file}")

        response = input("\nOverwrite existing files? (y/n): ").strip().lower()
        if response != "y":
            print("❌ Initialization cancelled.")
            return

    print("📁 Creating project structure...")

    try:
        project_path = scaffold_project(template_name)
        agents_dir = project_path / "agents"

        print(f"   ✅ Created {agents_dir}/ with JSON configs")
        print("   ✅ Created agent.py with complete implementation")
        print("   ✅ Created .env.example")
        print("   ✅ Created README.md")

        print("\n🎉 Project initialized successfully!")
        print(f"\n📋 Template: {template_name} - {template.description}")
        print("\n📋 Next steps:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Google API key to .env")
        print("   3. Run: python agent.py")
        print("\n💡 Get your API key at: https://makersuite.google.com/app/apikey")

    except Exception as e:
        print(f"❌ Error creating project: {e}")
        sys.exit(1)


def run_interactive(config_or_agent: Optional[str] = None):
    """
    Run the local agent in an interactive CLI session, with A2A heartbeat and discovery.
    """
    from broadie.a2a.cli import (
        setup_signal_handlers,
        start_background_tasks,
        stop_background_tasks,
    )
    from broadie.config.settings import BroadieSettings

    settings = BroadieSettings()

    # Start A2A background tasks
    host = settings.api_host if settings.api_host != "0.0.0.0" else "localhost"
    agent_address = f"http://{host}:{settings.api_port}"
    controller = start_background_tasks(agent_address)

    # Set up signal handlers for graceful shutdown
    setup_signal_handlers(controller)

    agent = None

    try:
        if config_or_agent:
            agent = load_agent_from_config_or_module(config_or_agent)
        else:
            # Try to discover agent automatically
            agent = discover_agent_from_directory()

    except Exception as e:
        print(f"Error loading agent: {e}")
        if controller:
            stop_background_tasks(controller)
        sys.exit(1)

    # Initialize persistence backend for todo tracking
    import asyncio

    from broadie.persistence import SQLAlchemyBackend

    # Get database URL and convert to async format if needed
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        # Convert to async SQLite URL
        db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif db_url.startswith("postgresql://"):
        # Convert to async PostgreSQL URL
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    backend = SQLAlchemyBackend(db_url)
    # Initialize DB tables
    asyncio.run(backend.initialize())

    # Attach backend to agent for todo display
    agent.backend = backend

    # Run interactive loop
    try:
        print("🤖 Starting agent (press Ctrl+C for graceful shutdown)...")
        agent.run()
    except KeyboardInterrupt:
        print("\n⏹️ Shutdown requested by user")
    except Exception as e:
        print(f"❌ Agent error: {e}")
    finally:
        # Stop background tasks gracefully
        stop_background_tasks(controller)


def serve(config_or_agent: Optional[str] = None, port: Optional[int] = None):
    """
    Serve the A2A HTTP and WebSocket endpoints, with heartbeat and discovery.
    
    Args:
        config_or_agent: Agent config file or module:class reference
        port: Port to serve on (overrides environment variables)
    """
    import uvicorn

    from broadie.a2a.cli import (
        setup_signal_handlers,
        start_background_tasks,
        stop_background_tasks,
    )
    from broadie.api.server import create_app
    from broadie.config.settings import BroadieSettings

    settings = BroadieSettings()
    
    # Override port if provided via CLI argument
    if port is not None:
        settings.api_port = port

    # Start A2A background tasks if enabled
    controller = None
    if settings.is_a2a_enabled():
        # Build agent address for registry
        host = settings.api_host if settings.api_host != "0.0.0.0" else "localhost"
        agent_address = f"http://{host}:{settings.api_port}"
        controller = start_background_tasks(agent_address)

    # Set up signal handlers for graceful shutdown
    setup_signal_handlers(controller)

    agent = None

    try:
        if config_or_agent:
            agent = load_agent_from_config_or_module(config_or_agent)
        else:
            # Try to discover agent automatically
            agent = discover_agent_from_directory()

    except Exception as e:
        print(f"Error loading agent: {e}")
        if controller:
            stop_background_tasks(controller)
        sys.exit(1)

    # Compute a slug ID from agent name (lowercase, alphanumeric + underscores)
    import re

    def slugify(name: str) -> str:
        s = name.strip()
        # Replace non-word characters with underscore
        s = re.sub(r"\W+", "_", s)
        # Collapse multiple underscores
        s = re.sub(r"_+", "_", s)
        # Trim leading/trailing underscores
        s = s.strip("_")
        return s.lower() or "agent"

    agent_id = slugify(agent.name)
    # Persist agent record under slug ID
    import asyncio
    from dataclasses import asdict

    from broadie.persistence import SQLAlchemyBackend

    # Get database URL and convert to async format if needed
    db_url = settings.database_url
    if db_url.startswith("sqlite:///"):
        # Convert to async SQLite URL
        db_url = db_url.replace("sqlite:///", "sqlite+aiosqlite:///")
    elif db_url.startswith("postgresql://"):
        # Convert to async PostgreSQL URL
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    backend = SQLAlchemyBackend(db_url)
    # Initialize DB tables
    asyncio.run(backend.initialize())
    # Store or update agent record (upsert)
    asyncio.run(backend.store_agent(agent_id, agent.name, asdict(agent.config)))
    # Update settings with slug ID
    settings.a2a.agent_id = agent_id
    settings.a2a.agent_name = agent.name

    # Attach backend to agent for CLI todo display
    agent.backend = backend

    # Create the FastAPI app with the loaded agent
    app = create_app(agent, settings)
    # Attach persistence backend for conversation storage
    app.state.backend = backend

    # Start the server
    try:
        # Determine accessible host for URLs
        host = (
            settings.api_host
            if settings.api_host not in ("0.0.0.0", "")
            else "localhost"
        )
        prefix = settings.api_prefix or ""
        base_url = f"http://{host}:{settings.api_port}{prefix}"
        agent_id = getattr(agent, "name", None) or settings.a2a.agent_id or "default"
        # Startup messages
        print(
            f"🚀 Starting server on {settings.api_host}:{settings.api_port} (press Ctrl+C for graceful shutdown)..."
        )
        print(f"📄 Swagger UI: {base_url}/docs")
        print(f"💡 Health Check: {base_url}/health")
        print(f"🖥 Invoke endpoint: POST {base_url}/agents/{agent_id}/invoke")
        print(f"🎨 UI:           {base_url}")
        uvicorn.run(app, host=settings.api_host, port=settings.api_port)
    except KeyboardInterrupt:
        print("\n⏹️ Shutdown requested by user")
    finally:
        if controller:
            stop_background_tasks(controller)


def print_help():
    """Display CLI usage information."""
    print("🤖 Broadie CLI")
    print("Usage: broadie [GLOBAL_OPTS] COMMAND [ARGS]\n")
    print("Global options:")
    print(
        "  --env, -e <file>            - Load environment variables from the specified .env file"
    )
    print(
        "                              (Defaults: loads .env in current directory if present)"
    )
    print()
    print("Commands:")
    print("  init [--template TEMPLATE]  - Create a project scaffold")
    print("  run [config/agent]          - Run agent from JSON config or Python module")
    print("  serve [config/agent]        - Serve HTTP/WebSocket endpoints for A2A")
    print("  create agent <name>         - Create a minimal JSON agent configuration")
    print(
        "  create sub-agent <name>     - Create a minimal JSON sub-agent configuration"
    )
    print("  templates                   - List available project templates")
    print()
    print("Templates:")
    for name, template in AVAILABLE_TEMPLATES.items():
        print(f"  {name:<12} - {template.description}")
    print()
    print("Examples:")
    print("  broadie --env .env.local serve main.json")
    print("  broadie init")
    print("  broadie init --template support")
    print("  broadie run main_agent.json")
    print("  broadie run module.path:AgentClass")
    print("  broadie serve main_agent.json")
    print("  broadie serve module.path:AgentClass")
    print("  broadie create agent support")
    print("  broadie create sub-agent analyzer")


def list_templates():
    """List available project templates."""
    print("📋 Available Broadie Templates:\n")
    for name, template in AVAILABLE_TEMPLATES.items():
        print(f"  {name:<12} - {template.description}")
    print()
    print("Usage: broadie init --template <template_name>")


def _extract_and_load_env(argv):
    """Load default .env and optional --env/-e override.
    Returns modified argv with --env arguments removed.
    """
    # 1) Load default .env in current working directory, if present
    #    Do not override existing environment variables
    try:
        load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
    except Exception:
        # Fail soft if dotenv isn't usable for some reason
        pass

    # 2) Find a global --env or -e flag anywhere and honor it
    new_argv = [argv[0]]
    i = 1
    env_path = None
    while i < len(argv):
        arg = argv[i]
        if arg == "--env" or arg == "-e":
            # accept next token as path (if present and not another flag)
            if i + 1 < len(argv) and not argv[i + 1].startswith("-"):
                env_path = argv[i + 1]
                i += 2
                continue
            else:
                # if no next token, ignore the flag gracefully
                i += 1
                continue
        elif arg.startswith("--env="):
            env_path = arg.split("=", 1)[1]
            i += 1
            continue
        else:
            new_argv.append(arg)
            i += 1

    if env_path:
        try:
            # Expand user (~) and make absolute
            env_file = Path(env_path).expanduser().resolve()
            if env_file.is_file():
                load_dotenv(dotenv_path=env_file, override=True)
                os.environ.setdefault("BROADIE_ENV_FILE", str(env_file))
                # Optional: print a small note for diagnostics
                # print(f"Loaded env from {env_file}")
            else:
                print(f"⚠️  --env file not found: {env_file}")
        except Exception as e:
            print(f"⚠️  Failed to load --env file: {e}")

    return new_argv


def cli():
    """Main CLI entry point."""
    if len(sys.argv) == 1:
        print_help()
        return

    # Load env and strip global --env/-e from argv before dispatching
    sys.argv = _extract_and_load_env(sys.argv)

    cmd = sys.argv[1]

    if cmd == "init":
        # Parse init arguments
        parser = argparse.ArgumentParser(description="Initialize a new Broadie project")
        parser.add_argument(
            "--template",
            "-t",
            default="simple",
            choices=list(AVAILABLE_TEMPLATES.keys()),
            help="Project template to use",
        )

        # Parse remaining args after 'init'
        init_args = parser.parse_args(sys.argv[2:])
        init_project(init_args.template)

    elif cmd == "run":
        if len(sys.argv) > 2:
            config_or_agent = sys.argv[2]
            run_interactive(config_or_agent)
        else:
            run_interactive()

    elif cmd == "serve":
        # Parse serve arguments
        parser = argparse.ArgumentParser(description="Serve HTTP/WebSocket endpoints for A2A")
        parser.add_argument("config_or_agent", nargs="?", help="Agent config file or module:class")
        parser.add_argument("--port", "-p", type=int, help="Port to serve on (overrides environment variables)")
        
        # Parse remaining args after 'serve'
        serve_args = parser.parse_args(sys.argv[2:])
        serve(serve_args.config_or_agent, port=serve_args.port)

    elif cmd == "create":
        if len(sys.argv) > 3:
            entity_type = sys.argv[2]
            entity_name = sys.argv[3]
            if entity_type == "agent":
                config_file = create_agent_config(entity_name)
                print(f"✅ Created agent configuration: {config_file}")
                print(f"📝 Agent name: {entity_name}")
                print(f"🔧 Edit the configuration file to customize the agent")
                print(f"🚀 Run with: broadie run {config_file}")
            elif entity_type == "sub-agent":
                config_file = create_subagent_config(entity_name)
                print(f"✅ Created sub-agent configuration: {config_file}")
                print(f"📝 Sub-agent name: {entity_name}")
                print(f"🔧 Edit the configuration file to customize the sub-agent")
                print(f"📚 Add to main agent's sub_agents array to use it")
            else:
                print(f"Unknown entity type: {entity_type}")
                print("Valid types: agent, sub-agent")
        else:
            print("Usage: broadie create <agent|sub-agent> <name>")

    elif cmd == "templates":
        list_templates()

    else:
        print_help()


if __name__ == "__main__":
    cli()
