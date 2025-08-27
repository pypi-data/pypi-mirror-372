# Broadie

A powerful multi-agent framework developed by the Broad Institute for building intelligent, collaborative AI systems with persistence, API integration, and agent-to-agent communication.

## What is Broadie?

Broadie enables you to create sophisticated AI agent systems that can work together, remember conversations, integrate with external services, and communicate with other agents. Whether you're building a simple chatbot or a complex multi-agent workflow, Broadie provides the infrastructure you need.

**Key Features:**
- **Two Usage Modes**: JSON configuration for quick setup or programmatic Python API for advanced customization
- **Agent Collaboration**: Main agents coordinate with specialized sub-agents
- **Persistent Memory**: Agents remember conversations and learn from interactions
- **Tool Integration**: Built-in tools for file operations, Google Drive, Slack, and more
- **Web Interface**: Chat with your agents through a web browser
- **Agent Communication**: Secure peer-to-peer agent discovery and function calls
- **Multiple AI Models**: Support for Google Gemini, Vertex AI, and more

---

## 🚀 Quick Start (5 minutes)

### Step 1: Install Broadie

```bash
pip install broadie
```

**System Requirements:** Python 3.9–3.12 (Python 3.11 recommended)

### Step 2: Get Your Google API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Create an API key
3. Set it as an environment variable:

**macOS/Linux:**
```bash
export GOOGLE_API_KEY="your_google_api_key"
```

**Windows PowerShell:**
```powershell
$env:GOOGLE_API_KEY = "your_google_api_key"
```

### Step 3: Create Your First Agent

Create a file called `my_agent.json`:

```json
{
  "name": "helpful_assistant",
  "description": "A helpful AI assistant", 
  "instruction": "You are a helpful AI assistant that can answer questions and help with tasks."
}
```

### Step 4: Start Chatting

```bash
broadie serve my_agent.json
```

Open your browser to: **http://localhost:8000/**

🎉 **That's it!** You now have a working AI agent with a web interface.

---

## 📖 Usage Guide

There are two ways to use Broadie, depending on your needs:

### Option 1: JSON Configuration (Recommended for Beginners)

**Best for:** Quick prototypes, simple agents, getting started  
**Limitations:** Cannot add custom tools or complex logic

Create agents using simple JSON files:

```json
{
  "name": "helpful_assistant",
  "description": "A helpful AI assistant",
  "instruction": "You are a helpful AI assistant that can answer questions and help with tasks."
}
```

**Commands:**
```bash
# Chat in terminal
broadie run my_agent.json

# Start web interface  
broadie serve my_agent.json
```

### Option 2: Python API (Advanced)

**Best for:** Production systems, custom tools, complex workflows  
**Advantages:** Full customization, custom tools, advanced logic

Create agents programmatically with custom capabilities:

```python
from broadie import Agent, SubAgent, tool

# Define custom tools that your agents can use
@tool(name="analyze_data", description="Analyze data and return insights")
def analyze_data(data: str) -> str:
    # Your custom analysis logic here
    return f"Analysis complete: {data} shows positive trends"

# Create a specialized sub-agent
class AnalystAgent(SubAgent):
    def build_config(self):
        return {
            "name": "data_analyst",
            "description": "Specializes in data analysis",
            "instruction": "You are a data analysis expert."
        }

# Create the main coordination agent
class ResearchCoordinator(Agent):
    def build_config(self):
        return {
            "name": "research_coordinator", 
            "description": "Coordinates research tasks",
            "instruction": "You coordinate research tasks and delegate to specialists.",
            "sub_agents": [AnalystAgent()]
        }

# Use your agent
async def main():
    agent = ResearchCoordinator()
    response = await agent.process_message("Analyze our Q4 sales data")
    print(response)
```

---

## ⚙️ Configuration

### Basic Setup (.env file)

Create a `.env` file in your project directory:

```bash
# Required: Google API Key
GOOGLE_API_KEY=your_google_api_key

# Optional: Advanced settings
A2A_ENABLED=true
DB_DRIVER=sqlite
SLACK_BOT_TOKEN=xoxb-your-slack-token
GOOGLE_DRIVE_CREDENTIALS_PATH=/path/to/credentials.json
```

### Advanced Google Cloud Setup

For production or advanced use cases:

1. **Create Google Cloud Project**: Visit [Google Cloud Console](https://console.cloud.google.com/)
2. **Enable Vertex AI API**: In "APIs & Services" → "Library" 
3. **Set additional variables**:

```bash
export GOOGLE_CLOUD_PROJECT_ID="your-project-id"
export GOOGLE_CLOUD_REGION="us-central1"
```

---

## 🛠️ Built-in Tools

Broadie agents automatically have access to powerful built-in tools:

### File Operations
- Read, write, and edit files
- List directories and search content

### Google Drive Integration *(when configured)*
- Search documents and spreadsheets  
- Read and write Google Docs
- Create and update Google Sheets

### Slack Integration *(when configured)*
- Send messages to channels
- Search message history
- Upload files and create threads

### Task Management
- Create and manage todo lists
- Track progress across conversations

---

## 🖥️ Commands & API

### CLI Commands
```bash
# Create new project from template
broadie init my_project

# Chat with agent in terminal
broadie run agent.json

# Start web interface
broadie serve agent.json

# Generate agent configs
broadie create agent customer_support

# List all templates
broadie templates
```

### Web Interface
When you run `broadie serve`, you get:
- **Chat UI**: `http://localhost:8000/` - Web interface for chatting
- **REST API**: `POST /agents/{id}/invoke` - Programmatic access  
- **WebSocket**: `/ws` - Real-time communication
- **Health Check**: `GET /health` - Service monitoring

---

## 🏗️ Advanced Features

### Multi-Agent Communication
Agents can work together in complex workflows:

```python
# Agent A can invoke functions on Agent B
result = await coordinator_agent.invoke_peer_agent(
    "analyst_agent_id", 
    "analyze_sales_data",
    {"data": sales_data, "period": "Q4"}
)
```

### Project Templates
Jump-start with built-in templates:

```bash
# Customer support system
broadie init --template support my_support_system

# Data integration specialist  
broadie init --template integration my_data_agent

# Generic multi-agent system
broadie init --template generic my_system
```

### Example Use Cases

**Customer Support:** Multi-agent system with specialized support, escalation, and knowledge base agents

**Data Analysis:** Pipeline with ingestion, analysis, and reporting agents working together

**Content Creation:** Research, writing, and editing agents coordinating content workflows

---

## 📚 Learn More

### Documentation & Support
- **Documentation**: [docs.broadie.ai](https://docs.broadie.ai)
- **GitHub Issues**: [Report bugs & request features](https://github.com/broadinstitute/broadie/issues)
- **Community**: [GitHub Discussions](https://github.com/broadinstitute/broadie/discussions)

### Contributing
We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Developed by the [Broad Institute](https://www.broadinstitute.org/)**

*Empowering researchers and developers with intelligent agent systems*

</div>