"""
Scaffolding utilities for Broadie CLI project initialization.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional


class ProjectTemplate:
    """Base class for project templates."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def create_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Return agent configurations for this template."""
        raise NotImplementedError

    def create_agent_py(self) -> str:
        """Return agent.py code for this template."""
        raise NotImplementedError

    def create_readme(self) -> str:
        """Return README.md content for this template."""
        raise NotImplementedError

    def get_tools_code(self) -> str:
        """Return custom tools code for this template."""
        return ""


class GenericTemplate(ProjectTemplate):
    """Generic multi-agent template."""

    def __init__(self):
        super().__init__(
            name="generic", description="A generic multi-agent system template"
        )

    def create_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Create generic agent configurations."""
        return {
            "main_agent.json": {
                "name": "main_agent",
                "description": "A helpful AI assistant",
                "instruction": "You are a helpful AI assistant. You can assist users with various tasks and questions. When you need specialized help, you can delegate to your sub-agents.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.2, "max_tokens": 8000},
            },
            "specialist.json": {
                "name": "specialist",
                "description": "A specialized assistant for complex tasks",
                "instruction": "You are a specialized assistant that handles complex tasks delegated by the main agent. You have access to advanced tools and capabilities.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.1, "max_tokens": 4000},
            },
        }

    def get_tools_code(self) -> str:
        """Return generic tools code."""
        return '''# Generic tools for demonstration
@tool
def get_current_time() -> str:
    """Get the current date and time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def search_web(query: str) -> str:
    """Simulate a web search."""
    # Simulate web search results
    results = {
        "weather": "Today's weather: Sunny, 22°C with light winds.",
        "news": "Latest news: Technology stocks rise 3% in morning trading.",
        "sports": "Sports update: Local team wins championship game 3-2.",
        "recipes": "Popular recipe: Easy pasta with tomato sauce and basil."
    }
    
    for key, result in results.items():
        if key.lower() in query.lower():
            return f"🔍 Search result for '{query}':\\n{result}"
    
    return f"🔍 Search result for '{query}': No specific results found. Try a different search term."

@tool
def analyze_data(data_description: str) -> str:
    """Analyze data and provide insights."""
    return f"📊 Data Analysis for '{data_description}':\\n- Pattern identified: Upward trend\\n- Recommendation: Monitor for next 24 hours\\n- Confidence: 85%"

@tool
def generate_report(report_type: str) -> str:
    """Generate a formatted report."""
    import uuid
    report_id = str(uuid.uuid4())[:8]
    return f"📄 {report_type.title()} Report #{report_id}\\n- Generated: {datetime.now().strftime('%Y-%m-%d')}\\n- Status: Complete\\n- Available for download"'''

    def create_agent_py(self) -> str:
        """Create generic agent.py implementation."""
        return f'''"""
Generic Multi-Agent System
A complete example showing Agent with SubAgent using build_config approach.
"""

from broadie import Agent, SubAgent, tool
from broadie.core.agent import AgentConfig
from datetime import datetime

{self.get_tools_code()}

class SpecialistSubAgent(SubAgent):
    """Specialized sub-agent using build_config approach."""
    
    def build_config(self):
        return AgentConfig(
            name="specialist",
            description="A specialized assistant for complex tasks",
            instruction="You are a specialized assistant that handles complex tasks delegated by the main agent. You have access to advanced tools and capabilities.",
            tools=["analyze_data", "generate_report"]
        )

class MainAgent(Agent):
    """Main agent using build_config approach."""
    
    def build_config(self):
        return AgentConfig(
            name="main_agent",
            description="A helpful AI assistant",
            instruction="You are a helpful AI assistant. You can assist users with various tasks and questions. When you need specialized help, you can delegate to your sub-agents.",
            tools=["get_current_time", "search_web"]
        )

# Create the agent system
specialist = SpecialistSubAgent()
main_agent = MainAgent(subagents=[specialist])

if __name__ == "__main__":
    print("🎯 Generic Multi-Agent System")
    print("=" * 50)
    
    print(f"✅ Agent: {{main_agent.name}}")
    print(f"📝 Description: {{main_agent.description}}")
    print(f"🛠️ Tools: {{', '.join(main_agent.config.tools)}}")
    print(f"🤖 Sub-agents: {{list(main_agent.sub_agents.keys())}}")
    
    print("\\n🚀 Starting interactive agent session...")
    print("Try asking:")
    print("  - 'What time is it?'") 
    print("  - 'Search for weather information'")
    print("  - 'Analyze sales data from last quarter'")
    print("  - 'Generate a monthly report' (uses specialist)")
    print("\\nType 'quit' to exit\\n")
    
    # Start the agent
    main_agent.run()
'''

    def create_readme(self) -> str:
        """Create generic README content."""
        return '''# Generic Multi-Agent System

A complete Broadie multi-agent system featuring a main agent with specialized sub-agents.

## 🚀 Quick Start

### 1. Set up your environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 2. Run the agent system
```bash
python agent.py
```

## 🏗️ Project Structure

```
├── agents/                    # Agent configurations
│   ├── main_agent.json       # Main agent config
│   └── specialist.json       # Specialist sub-agent config
├── agent.py                  # Complete implementation
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🤖 Agents Overview

### Main Agent
- **Role**: General-purpose assistant
- **Capabilities**: Time queries, web search simulation
- **Tools**: `get_current_time`, `search_web`

### Specialist Sub-Agent  
- **Role**: Handles complex analytical tasks
- **Capabilities**: Data analysis, report generation
- **Tools**: `analyze_data`, `generate_report`

## 💬 Example Interactions

Try these prompts when running the agent:

**Basic Tasks:**
- "What time is it?"
- "Search for weather information" 
- "Search for news updates"

**Advanced Tasks (delegated to specialist):**
- "Analyze sales data from last quarter"
- "Generate a monthly performance report"

## 🛠️ Customization

### Adding New Tools
Add custom tools in `agent.py`:

```python
@tool
def your_custom_tool(param: str) -> str:
    """Your tool description."""
    return f"Result for {param}"
```

### Modifying Agent Behavior
Edit the JSON configs in `agents/` or modify the build_config() methods in `agent.py`.

### Environment Configuration
All settings are configurable via `.env`:
- Model selection (`DEFAULT_GEMINI_MODEL`)
- API keys (`GOOGLE_API_KEY`)
- Logging levels (`LOG_LEVEL`)
- A2A communication settings

## 📚 Learn More

- [Broadie Documentation](https://docs.broadie.ai)
- [Agent Configuration Guide](https://docs.broadie.ai/agents)
- [Tool Development](https://docs.broadie.ai/tools)

## 🔧 Troubleshooting

**"No module named 'broadie'"**
```bash
pip install broadie
```

**"API key not found"** 
- Make sure you've set `GOOGLE_API_KEY` in your `.env` file
- Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Agent not responding**
- Check your internet connection
- Verify your API key is valid
- Check the console for error messages
'''


class SimpleTemplate(ProjectTemplate):
    """Simple agent template - the default template."""

    def __init__(self):
        super().__init__(name="simple", description="A simple single agent example")

    def create_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Create simple agent configuration."""
        return {
            "simple_agent.json": {
                "name": "simple_agent",
                "description": "A simple helpful AI assistant",
                "instruction": "You are a simple, helpful AI assistant. Answer questions clearly and concisely. Be friendly and professional.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.7, "max_tokens": 4000},
            }
        }

    def get_tools_code(self) -> str:
        """Return simple tools code."""
        return '''@tool
def hello_world(name: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {name}! Nice to meet you!"

@tool  
def get_current_time() -> str:
    """Get the current date and time."""
    return f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"'''

    def create_agent_py(self) -> str:
        """Create simple agent.py implementation."""
        return f'''"""
Simple Agent Example
A basic Broadie agent to get you started.
"""

from broadie import Agent, tool
from broadie.core.agent import AgentConfig
from datetime import datetime
import json

{self.get_tools_code()}

class SimpleAgent(Agent):
    """A simple agent using build_config approach."""
    
    def build_config(self):
        return AgentConfig(
            name="simple_agent",
            description="A simple helpful AI assistant", 
            instruction="You are a simple, helpful AI assistant. Answer questions clearly and concisely. Be friendly and professional.",
            tools=["hello_world", "get_current_time"]
        )

# Create agent instance
simple_agent = SimpleAgent()

if __name__ == "__main__":
    print("🤖 Simple Agent")
    print("=" * 30)
    
    print(f"✅ Agent: {{simple_agent.name}}")
    print(f"📝 Description: {{simple_agent.description}}")
    print(f"🛠️ Available tools: {{', '.join(simple_agent.config.tools)}}")
    
    print("\\n🚀 Starting agent...")
    print("Try asking:")
    print("  - 'Hello there!'")
    print("  - 'What time is it?'") 
    print("  - 'Tell me a joke'")
    print("\\nType 'quit' to exit\\n")
    
    # Start the agent
    simple_agent.run()
'''

    def create_readme(self) -> str:
        """Create simple README content."""
        return '''# Simple Agent

A basic Broadie agent to help you get started.

## 🚀 Quick Start

### 1. Set up your environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google API key  
# Get your key from: https://makersuite.google.com/app/apikey
```

### 2. Run your agent
```bash
python agent.py
```

## 🏗️ Project Structure

```
├── agents/
│   └── simple_agent.json    # Agent configuration
├── agent.py                # Agent implementation  
├── .env.example           # Environment variables
└── README.md             # This file
```

## 🤖 What This Agent Does

- **Role**: General-purpose assistant
- **Capabilities**: Greetings, time queries, general conversation
- **Tools**: `hello_world`, `get_current_time`

## 💬 Example Interactions

Try these prompts:
- "Hello there!"
- "What time is it?"
- "Tell me about yourself"

## 🛠️ Customization

### Adding New Tools
Add custom tools in `agent.py`:

```python
@tool
def your_custom_tool(param: str) -> str:
    """Your tool description."""
    return f"Result for {param}"
```

Then add it to your agent's tools list in the `build_config()` method.

### Modifying Behavior
Edit the agent configuration in `agents/simple_agent.json` or modify the `build_config()` method directly in `agent.py`.

## 📚 Learn More

- [Broadie Documentation](https://docs.broadie.ai)
- [Agent Configuration Guide](https://docs.broadie.ai/agents)
- [Tool Development](https://docs.broadie.ai/tools)

## 🔧 Troubleshooting

**"No module named 'broadie'"**
```bash
pip install broadie
```

**"API key not found"**
- Make sure you've set `GOOGLE_API_KEY` in your `.env` file
- Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)
'''


class IntegrationTemplate(ProjectTemplate):
    """API integration template with sub-agent."""

    def __init__(self):
        super().__init__(
            name="integration", description="API integration specialist with sub-agent"
        )

    def create_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Create integration agent configurations."""
        return {
            "integration_agent.json": {
                "name": "integration_agent",
                "description": "API integration main agent",
                "instruction": "You are an API integration specialist. You help users integrate with various APIs, debug connection issues, and provide integration guidance. You can delegate complex tasks to your sub-agent.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.3, "max_tokens": 6000},
            },
            "integration_specialist.json": {
                "name": "integration_specialist",
                "description": "API integration sub-agent specialist",
                "instruction": "You are a specialized API integration assistant. You handle complex integration tasks, analyze API responses, and provide detailed technical solutions.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.2, "max_tokens": 4000},
            },
        }

    def get_tools_code(self) -> str:
        """Return integration tools code."""
        return '''@tool
def test_api_connection(url: str, method: str = "GET") -> str:
    """Test API connection and return status."""
    try:
        import requests
        response = requests.request(method, url, timeout=10)
        return f"✅ API Connection Test:\\nURL: {url}\\nMethod: {method}\\nStatus: {response.status_code}\\nResponse Time: {response.elapsed.total_seconds():.2f}s"
    except Exception as e:
        return f"❌ API Connection Failed:\\nURL: {url}\\nError: {str(e)}"

@tool
def parse_api_response(response_data: str) -> str:
    """Parse and analyze API response data."""
    try:
        import json
        data = json.loads(response_data)
        return f"📊 API Response Analysis:\\nType: {type(data).__name__}\\nKeys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}\\nSize: {len(data) if hasattr(data, '__len__') else 'N/A'}"
    except Exception as e:
        return f"⚠️ Response Parsing Error: {str(e)}"

@tool
def generate_integration_code(api_name: str, endpoint: str) -> str:
    """Generate sample integration code for an API."""
    api_func_name = api_name.lower().replace(' ', '_')
    code = f"""# {api_name} Integration Example
import requests
import json

def call_{api_func_name}_api():
    \"\"\"Call the {api_name} API endpoint.\"\"\"
    
    url = "{endpoint}"
    headers = {{
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
    }}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        print(f"Success: {{data}}")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Error: {{e}}")
        return None

# Example usage
if __name__ == "__main__":
    result = call_{api_func_name}_api()
"""
    return f"💻 Generated Integration Code:\\n```python\\n{code}\\n```"

@tool  
def analyze_api_documentation(api_docs: str) -> str:
    """Analyze API documentation and provide integration insights."""
    insights = []
    
    if "authentication" in api_docs.lower():
        insights.append("🔐 Authentication required")
    if "rate limit" in api_docs.lower():
        insights.append("⏱️ Rate limiting present")
    if "webhook" in api_docs.lower():
        insights.append("🔗 Webhook support available")
    if "pagination" in api_docs.lower():
        insights.append("📄 Pagination supported")
    
    return f"📚 API Documentation Analysis:\\n" + "\\n".join(insights) if insights else "📚 Basic API documentation provided"

@tool
def debug_integration_issue(error_description: str) -> str:
    """Debug common API integration issues."""
    solutions = {
        "401": "Authentication issue - check API key and authorization headers",
        "403": "Permission issue - verify API key has required permissions", 
        "404": "Endpoint not found - check URL and API version",
        "429": "Rate limit exceeded - implement backoff strategy",
        "500": "Server error - check API status and retry later",
        "timeout": "Connection timeout - increase timeout or check network",
        "ssl": "SSL certificate issue - verify certificate or use verify=False for testing"
    }
    
    for error_type, solution in solutions.items():
        if error_type in error_description.lower():
            return f"🔧 Debug Suggestion:\\n{solution}"
    
    return "🔧 Debug Suggestion: Check API documentation, verify credentials, and test with a simple HTTP client first"'''

    def create_agent_py(self) -> str:
        """Create integration agent.py implementation."""
        return f'''"""
API Integration Specialist
A Broadie agent system for API integration assistance with specialized sub-agent.
"""

from broadie import Agent, SubAgent, tool
from broadie.core.agent import AgentConfig
import json

{self.get_tools_code()}

class IntegrationSpecialistSubAgent(SubAgent):
    """Specialized API integration sub-agent."""
    
    def build_config(self):
        return AgentConfig(
            name="integration_specialist",
            description="API integration sub-agent specialist",
            instruction="You are a specialized API integration assistant. You handle complex integration tasks, analyze API responses, and provide detailed technical solutions.",
            tools=["analyze_api_documentation", "debug_integration_issue", "generate_integration_code"]
        )

class IntegrationAgent(Agent):
    """Main integration agent."""
    
    def build_config(self):
        return AgentConfig(
            name="integration_agent",
            description="API integration main agent", 
            instruction="You are an API integration specialist. You help users integrate with various APIs, debug connection issues, and provide integration guidance. You can delegate complex tasks to your sub-agent.",
            tools=["test_api_connection", "parse_api_response"]
        )

# Create the integration system
integration_specialist = IntegrationSpecialistSubAgent()
integration_agent = IntegrationAgent(subagents=[integration_specialist])

if __name__ == "__main__":
    print("🔌 API Integration Specialist")
    print("=" * 40)
    
    print(f"✅ Agent: {{integration_agent.name}}")
    print(f"📝 Description: {{integration_agent.description}}")
    print(f"🛠️ Tools: {{', '.join(integration_agent.config.tools)}}")
    print(f"🤖 Sub-agents: {{list(integration_agent.sub_agents.keys())}}")
    
    print("\\n🚀 Starting integration assistant...")
    print("Try asking:")
    print("  - 'Test connection to https://api.example.com'")
    print("  - 'Help me debug a 401 authentication error'")
    print("  - 'Generate code to integrate with the GitHub API'")
    print("  - 'Analyze this API documentation: [paste docs]'")
    print("\\nType 'quit' to exit\\n")
    
    # Start the agent
    integration_agent.run()
'''

    def create_readme(self) -> str:
        """Create integration README content."""
        return '''# API Integration Specialist

A Broadie multi-agent system specialized in API integration assistance, featuring a main agent with a technical specialist sub-agent.

## 🚀 Quick Start

### 1. Set up your environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 2. Run the integration assistant
```bash
python agent.py
```

## 🏗️ Project Structure

```
├── agents/
│   ├── integration_agent.json      # Main agent config
│   └── integration_specialist.json # Specialist sub-agent config  
├── agent.py                       # Complete implementation
├── .env.example                  # Environment variables
└── README.md                    # This file
```

## 🤖 Agents Overview

### Main Agent: Integration Agent
- **Role**: API integration guidance and basic testing
- **Capabilities**: API connection testing, response parsing
- **Tools**: `test_api_connection`, `parse_api_response`

### Sub-Agent: Integration Specialist  
- **Role**: Complex integration analysis and code generation
- **Capabilities**: Documentation analysis, issue debugging, code generation
- **Tools**: `analyze_api_documentation`, `debug_integration_issue`, `generate_integration_code`

## 💬 Example Interactions

Try these prompts when running the agent:

**Basic Testing:**
- "Test connection to https://api.github.com"
- "Parse this API response: {'users': [{'name': 'John'}]}"

**Advanced Analysis:**
- "Help me debug a 401 authentication error with the Stripe API"
- "Generate Python code to integrate with the Slack API"
- "Analyze this API documentation and provide integration insights"

**Complex Tasks (handled by specialist):**
- "I'm getting SSL certificate errors when calling the API"
- "Generate a complete integration example for a REST API with authentication"

## 🛠️ Customization

### Adding New Tools
Add custom tools in `agent.py`:

```python
@tool
def your_integration_tool(param: str) -> str:
    """Your tool description."""
    return f"Integration result for {param}"
```

### Modifying Agent Behavior
Edit the JSON configs in `agents/` or modify the `build_config()` methods in `agent.py`.

### Environment Configuration
All settings are configurable via `.env`:
- Model selection (`DEFAULT_GEMINI_MODEL`)
- API keys (`GOOGLE_API_KEY`) 
- Logging levels (`LOG_LEVEL`)

## 📚 Learn More

- [Broadie Documentation](https://docs.broadie.ai)
- [Agent Configuration Guide](https://docs.broadie.ai/agents)
- [Tool Development](https://docs.broadie.ai/tools)

## 🔧 Troubleshooting

**"No module named 'broadie'"**
```bash
pip install broadie
```

**"API key not found"**
- Make sure you've set `GOOGLE_API_KEY` in your `.env` file
- Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Agent not responding**
- Check your internet connection
- Verify your API key is valid
- Check the console for error messages
'''


class SupportTemplate(ProjectTemplate):
    """Customer support template."""

    def __init__(self):
        super().__init__(
            name="support", description="Customer support multi-agent system"
        )

    def create_agents_config(self) -> Dict[str, Dict[str, Any]]:
        """Create support agent configurations."""
        return {
            "support.json": {
                "name": "support",
                "description": "A helpful customer support agent",
                "instruction": "You are a helpful customer support agent. You handle customer inquiries, resolve issues, and provide excellent service. You can escalate complex issues to specialists when needed.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.3, "max_tokens": 8000},
            },
            "customer_support.json": {
                "name": "customer_support",
                "description": "A specialized customer support specialist",
                "instruction": "You are a specialized customer support specialist. You handle escalated customer issues with empathy and technical expertise. Focus on finding solutions and ensuring customer satisfaction.",
                "model": {"provider": "google", "name": "gemini-2.0-flash"},
                "model_settings": {"temperature": 0.2, "max_tokens": 4000},
            },
        }

    def get_tools_code(self) -> str:
        """Return support tools code."""
        return '''# Custom tools for customer support
@tool
def lookup_customer(customer_id: str) -> str:
    """Look up customer information by ID."""
    # Simulate customer lookup
    customers = {
        "12345": "John Doe - Premium Customer, Account Active, Last Contact: 2024-01-15",
        "67890": "Jane Smith - Standard Customer, Account Active, Last Contact: 2024-01-10", 
        "11111": "Bob Johnson - VIP Customer, Account Active, Priority Support"
    }
    return customers.get(customer_id, f"Customer {customer_id} not found")

@tool
def create_ticket(issue_description: str, priority: str = "medium") -> str:
    """Create a support ticket for the issue."""
    import uuid
    ticket_id = str(uuid.uuid4())[:8]
    return f"✅ Support ticket #{ticket_id} created\\nIssue: {issue_description}\\nPriority: {priority}\\nStatus: Open"

@tool
def search_knowledge_base(query: str) -> str:
    """Search the knowledge base for solutions."""
    # Simulate knowledge base search
    kb_articles = {
        "password reset": "To reset password: Go to Settings > Security > Reset Password. Enter email and follow instructions.",
        "billing issue": "For billing issues: Check Account > Billing History. Contact billing@company.com for disputes.",
        "technical support": "Technical issues: Try clearing cache/cookies first. Check system status at status.company.com",
        "account locked": "Account locked: Wait 15 minutes or contact support. Multiple failed login attempts trigger auto-lock."
    }
    
    for key, article in kb_articles.items():
        if key.lower() in query.lower():
            return f"📚 Knowledge Base Article:\\n{article}"
    
    return "No relevant articles found. Consider creating a support ticket."

@tool  
def escalate_issue(ticket_id: str, reason: str) -> str:
    """Escalate an issue to specialized support."""
    return f"🔺 Ticket {ticket_id} escalated to specialist support\\nReason: {reason}\\nETA: 2-4 hours"

@tool
def access_technical_docs(topic: str) -> str:
    """Access technical documentation for complex issues."""
    docs = {
        "api integration": "API Integration Guide: Use REST endpoints at api.company.com/v1/. Authentication via Bearer tokens.",
        "system architecture": "System Architecture: Microservices on AWS, Redis cache, PostgreSQL database.",
        "troubleshooting": "Troubleshooting Guide: Check logs, verify connectivity, restart services if needed."
    }
    return docs.get(topic.lower(), f"No technical docs found for: {topic}")

@tool
def create_follow_up(customer_id: str, notes: str) -> str:
    """Create a follow-up task for the customer.""" 
    return f"📋 Follow-up scheduled for customer {customer_id}\\nNotes: {notes}\\nDue: Tomorrow 9 AM"'''

    def create_agent_py(self) -> str:
        """Create support agent.py implementation."""
        return f'''"""
Customer Support Agent System
A complete example showing Agent with SubAgent for customer support.
"""

from broadie import Agent, SubAgent, tool
from broadie.core.agent import AgentConfig

{self.get_tools_code()}

class CustomerSupportSubAgent(SubAgent):
    """Specialized customer support sub-agent using build_config approach."""
    
    def build_config(self):
        return AgentConfig(
            name="customer_support",
            description="A specialized customer support specialist",
            instruction="You are a specialized customer support specialist. You handle escalated customer issues with empathy and technical expertise. Focus on finding solutions and ensuring customer satisfaction.",
            tools=["escalate_issue", "access_technical_docs", "create_follow_up"]
        )

class SupportAgent(Agent):
    """Main support agent using build_config approach."""
    
    def build_config(self):
        return AgentConfig(
            name="support",
            description="A helpful customer support agent",
            instruction="You are a helpful customer support agent. You handle customer inquiries, resolve issues, and provide excellent service. You can escalate complex issues to specialists when needed.",
            tools=["lookup_customer", "create_ticket", "search_knowledge_base"]
        )

# Create the support agent system
specialist = CustomerSupportSubAgent()
support_agent = SupportAgent(subagents=[specialist])

if __name__ == "__main__":
    print("🎯 Customer Support Agent System")
    print("=" * 50)
    
    print(f"✅ Agent: {{support_agent.name}}")
    print(f"📝 Description: {{support_agent.description}}")
    print(f"🛠️ Tools: {{', '.join(support_agent.config.tools)}}")
    print(f"🤖 Sub-agents: {{list(support_agent.sub_agents.keys())}}")
    
    print("\\n🚀 Starting interactive support session...")
    print("Try asking:")
    print("  - 'Look up customer 12345'") 
    print("  - 'I need help with password reset'")
    print("  - 'Create a ticket for billing issue'")
    print("  - 'This is a complex technical problem' (will escalate)")
    print("\\nType 'quit' to exit\\n")
    
    # Start the agent
    support_agent.run()
'''

    def create_readme(self) -> str:
        """Create support README content."""
        return '''# Customer Support Agent System

A complete Broadie multi-agent system for customer support, featuring a main support agent with a specialized escalation sub-agent.

## 🚀 Quick Start

### 1. Set up your environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your Google API key
# Get your key from: https://makersuite.google.com/app/apikey
```

### 2. Run the support system
```bash
python agent.py
```

## 🏗️ Project Structure

```
├── agents/                    # Agent configurations
│   ├── support.json          # Main support agent config
│   └── customer_support.json # Escalation specialist config
├── agent.py                  # Complete implementation
├── .env.example             # Environment variables template
└── README.md                # This file
```

## 🤖 Agents Overview

### Main Agent: Support
- **Role**: Front-line customer support
- **Capabilities**: Customer lookup, ticket creation, knowledge base search
- **Tools**: `lookup_customer`, `create_ticket`, `search_knowledge_base`

### Sub-Agent: Customer Support Specialist  
- **Role**: Handles escalated complex issues
- **Capabilities**: Technical documentation access, issue escalation, follow-ups
- **Tools**: `escalate_issue`, `access_technical_docs`, `create_follow_up`

## 💬 Example Interactions

Try these prompts when running the agent:

**Basic Support:**
- "Look up customer 12345"
- "I need help with password reset" 
- "Create a ticket for a billing issue"

**Escalation Scenarios:**
- "This is a complex technical problem that needs specialist attention"
- "I need access to technical documentation for API integration"

**Follow-up Actions:**
- "Schedule a follow-up for customer 67890"
- "Escalate ticket ABC123 due to system complexity"

## 🛠️ Customization

### Adding New Tools
Add custom tools in `agent.py`:

```python
@tool
def your_custom_tool(param: str) -> str:
    """Your tool description."""
    return f"Result for {param}"
```

### Modifying Agent Behavior
Edit the JSON configs in `agents/` or modify the instructions directly in `agent.py`.

### Environment Configuration
All settings are configurable via `.env`:
- Model selection (`DEFAULT_GEMINI_MODEL`)
- API keys (`GOOGLE_API_KEY`)
- Logging levels (`LOG_LEVEL`)
- A2A communication settings

## 📚 Learn More

- [Broadie Documentation](https://docs.broadie.ai)
- [Agent Configuration Guide](https://docs.broadie.ai/agents)
- [Tool Development](https://docs.broadie.ai/tools)

## 🔧 Troubleshooting

**"No module named 'broadie'"**
```bash
pip install broadie
```

**"API key not found"** 
- Make sure you've set `GOOGLE_API_KEY` in your `.env` file
- Get your key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**Agent not responding**
- Check your internet connection
- Verify your API key is valid
- Check the console for error messages
'''


# Template registry
AVAILABLE_TEMPLATES = {
    "simple": SimpleTemplate(),
    "integration": IntegrationTemplate(),
    "generic": GenericTemplate(),
    "support": SupportTemplate(),
}


def create_env_example(template_name: str = "simple") -> str:
    """Create .env.example file content."""
    template = AVAILABLE_TEMPLATES.get(template_name, SimpleTemplate())

    if template_name == "support":
        agent_id = "support-agent-001"
        agent_name = "Customer Support Agent"
    else:
        agent_id = "main-agent-001"
        agent_name = "Main Agent"

    return f"""# Broadie Configuration
# Copy this file to .env and add your actual values

# Google AI API Key (required)
# Get your key from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-google-api-key-here

# Model Configuration  
DEFAULT_GEMINI_MODEL=gemini-2.0-flash
GOOGLE_GENAI_USE_VERTEXAI=false

# Logging
LOG_LEVEL=INFO
DEBUG=false

# Agent-to-Agent Communication (optional)
A2A_ENABLED=true
A2A_AGENT_ID={agent_id}
A2A_AGENT_NAME={agent_name}
A2A_TRUSTED_AGENTS=
A2A_REGISTRY_URL=

# Slack Notifications (optional)
SLACK_BOT_TOKEN=
SLACK_CHANNEL=
SLACK_WEBHOOK_URL=

# Database (optional - defaults to SQLite)
# DATABASE_URL=sqlite:///data/broadie.db
DB_DRIVER=sqlite
DB_NAME=broadie.db
"""


def scaffold_project(
    template_name: str = "simple", project_path: Optional[Path] = None
) -> Path:
    """
    Scaffold a new Broadie project using the specified template.

    Args:
        template_name: Name of the template to use
        project_path: Path to create the project (defaults to current directory)

    Returns:
        Path to the created project
    """
    if project_path is None:
        project_path = Path.cwd()

    template = AVAILABLE_TEMPLATES.get(template_name)
    if not template:
        raise ValueError(
            f"Unknown template: {template_name}. Available: {list(AVAILABLE_TEMPLATES.keys())}"
        )

    # Create agents directory and configs
    agents_dir = project_path / "agents"
    agents_dir.mkdir(exist_ok=True)

    agent_configs = template.create_agents_config()
    for filename, config in agent_configs.items():
        with open(agents_dir / filename, "w") as f:
            json.dump(config, f, indent=2)

    # Create agent.py
    with open(project_path / "agent.py", "w") as f:
        f.write(template.create_agent_py())

    # Create .env.example
    with open(project_path / ".env.example", "w") as f:
        f.write(create_env_example(template_name))

    # Create README.md
    with open(project_path / "README.md", "w") as f:
        f.write(template.create_readme())

    return project_path


def create_agent_config(agent_name: str, agents_dir: Optional[Path] = None) -> Path:
    """Create a minimal JSON agent configuration."""
    if agents_dir is None:
        agents_dir = Path("agents")

    agents_dir.mkdir(exist_ok=True)

    agent_config = {
        "name": agent_name,
        "description": f"A helpful {agent_name} agent",
        "instruction": f"You are {agent_name}, a helpful AI assistant. Provide clear, accurate, and helpful responses to user queries.",
        "model": {"provider": "google", "name": "gemini-2.0-flash"},
        "model_settings": {"temperature": 0.2, "max_tokens": 8000},
    }

    config_file = agents_dir / f"{agent_name}.json"
    with open(config_file, "w") as f:
        json.dump(agent_config, f, indent=2)

    return config_file


def create_subagent_config(
    subagent_name: str, agents_dir: Optional[Path] = None
) -> Path:
    """Create a minimal JSON sub-agent configuration."""
    if agents_dir is None:
        agents_dir = Path("agents")

    agents_dir.mkdir(exist_ok=True)

    subagent_config = {
        "name": subagent_name,
        "description": f"A specialized {subagent_name} sub-agent",
        "instruction": f"You are {subagent_name}, a specialized AI assistant. You handle specific tasks delegated to you by the main agent.",
        "model": {"provider": "google", "name": "gemini-2.0-flash"},
        "model_settings": {"temperature": 0.2, "max_tokens": 4000},
    }

    config_file = agents_dir / f"{subagent_name}.json"
    with open(config_file, "w") as f:
        json.dump(subagent_config, f, indent=2)

    return config_file
