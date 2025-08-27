<!-- ABOUT.md: Detailed project overview and documentation -->
# About Broadie

Broadie is a batteries‐included, Python-based multi-agent framework for building, orchestrating, and persisting intelligent agents. It provides all the essential components out of the box—models, tools, memory, persistence, CLI utilities, REST and WebSocket endpoints, and secure agent-to-agent (A2A) communications—so you can focus on the unique logic of your AI applications.

Inspired by [DeepAgents](https://github.com/langchain-ai/deepagents) but extended with robust A2A capabilities and production-ready REST APIs, Broadie accelerates development of autonomous agents that collaborate, learn, and evolve over time.

## Table of Contents
1. [Key Features](#key-features)
2. [Intended Purpose](#intended-purpose)
3. [High-Level Architecture](#high-level-architecture)
4. [Core Components](#core-components)
5. [Getting Started](#getting-started)
6. [Usage Patterns](#usage-patterns)
7. [Extensibility and Customization](#extensibility-and-customization)
8. [A2A and API Endpoints](#a2a-and-api-endpoints)
9. [Inspiration & Related Projects](#inspiration--related-projects)
10. [Contributing](#contributing)

## Key Features
- **Multi-Agent Orchestration**: Define main agents with specialized sub-agents to delegate tasks.
- **Custom Tool Registry**: Easily register and discover custom functions as agent tools.
- **Persistent Memory**: Semantic memory storage (SQLite, PostgreSQL, vector stores) with recall and search.
- **Secure A2A Communication**: Agent-to-agent discovery, identity verification, and function invocation.
- **REST & WebSocket APIs**: FastAPI-powered endpoints for programmatic and real-time agent interactions.
- **CLI Interface**: `broadie init`, `broadie run`, `broadie serve`, `broadie create agent`, `broadie create sub-agent` to scaffold and manage agents.
- **Notifications**: Slack integration for alerts, summaries, and external notifications.
- **Plug-and-Play Models**: Built-in support for Google Generative AI (Gemini) and Vertex AI with fallback to LangChain adapters.

## Intended Purpose
Broadie is designed for developers and organizations that need:
- Rapid prototyping and deployment of conversational or task-oriented agents.
- Persistent context and memory across sessions.
- Secure collaboration between distributed agents.
- Production-grade API endpoints to integrate agents into existing systems.

Whether you’re automating customer support, incident response, data analysis, or cross-system orchestration, Broadie provides a solid foundation so you can build, scale, and manage AI agents in one cohesive framework.

## High-Level Architecture

```
  +--------------------+      +----------------------+      +------------------+
  |      Client        | <--> |   FastAPI Server     | <--> |  Broadie Agents  |
  +--------------------+      +----------------------+      +------------------+
               ^                           |                        |
               |                           v                        v
     WebSocket / REST                A2A Registry            Persistence Layer
                                        (optional)            (SQLite, PostgreSQL,
                                                               Vector Store)
```

- **Agents**: Core logic built on LangGraph/React Agents, orchestrating prompts, tools, and memory.
- **A2A Registry**: Optional service for peer discovery and trust-based communication.
- **Persistence Layer**: Memory and state stored persistently for long-term context.
- **API Server**: FastAPI application exposing agent capabilities via HTTP and WebSocket.
- **CLI**: Command-line interface for scaffolding, running, and validating agents.

## Core Components
1. **core**: `Agent`, `SubAgent`, `ToolRegistry`, `MemoryManager`, state and prompts abstractions.
2. **config**: JSON-based and environment variable configuration management.
3. **persistence**: SQLite and PostgreSQL backends, vector store integration.
4. **api**: FastAPI server modules (`routes.py`, `server.py`, `websocket.py`).
5. **a2a**: Agent-to-agent modules for heartbeat, discovery, and registry clients.
6. **cli**: Console entry points (`broadie run`, `serve`, `validate`, `ask`).
7. **notifications**: Slack integration for posting messages.
8. **templates**: Python and JSON templates for common agent patterns (customer support, security, teams, etc.).
9. **utils**: Logging, schema validation, exception classes.

## Getting Started
Refer to [README.md](./README.md) for full installation and quick start instructions. In brief:
```bash
git clone https://github.com/your-org/broadie.git
cd broadie
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -e .[dev]
cp .env.example .env       # configure API keys and DB settings
```

## Usage Patterns
### JSON-Driven Agents
Define a minimal JSON file (`agent.json`) specifying `name`, `description`, `instruction`, and `model`.
```json
{
  "name": "my_agent",
  "description": "Helps with X",
  "instruction": "You are an AI assistant.",
  "model": { "provider": "google", "name": "gemini-2.0-flash" }
}
```
Run locally:
```bash
broadie run agent.json
```

### Programmatic Agents
Subclass `Agent` or `SubAgent`, implement `build_config()`, and invoke directly:
```python
from broadie import Agent, SubAgent, tool

@tool(name="echo", description="Echo input back")
def echo(text: str) -> str:
    return text

class EchoAgent(Agent):
    def build_config(self):
        return {"name": "echo_agent", "instruction": "Echoer"}

agent = EchoAgent()
print(agent.invoke("Hello"))
```

## Extensibility and Customization
- **Tools**: Decorate Python functions with `@tool` to register custom actions.
- **Models**: Swap or configure language models via `model_settings` in JSON or programmatic configs.
- **Memory**: Leverage memory APIs to store, search, and recall persistent data.
- **Sub-Agents**: Decompose complex tasks by defining multiple `SubAgent` classes.

## A2A and API Endpoints
- **Agent-to-Agent**: Secure peer discovery, heartbeat, and function invocation via `broadie.a2a` modules.
- **REST API**: Expose agents at `/agents/{id}/invoke`, health checks, and metadata endpoints.
- **WebSocket**: Real-time chat interface under `/ws` for interactive applications.

## Inspiration & Related Projects
- **DeepAgents** by LangChain: foundational project for multi-agent patterns.
- **Broadie** builds upon this with:
  - First-class A2A communications and discovery.
  - Production-ready REST and WebSocket APIs.
  - Batteries-included persistence, CLI, and notifications.

## Contributing
We welcome issues, feature requests, and pull requests. See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---
© Broad Institute • MIT License