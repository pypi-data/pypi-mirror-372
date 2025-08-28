# 🌟 Noctis - Your Complete AI Development Team in a Box

> **Transform your development workflow with 10 specialized AI agents, powerful tools, and enterprise-grade features - all in one comprehensive framework.**

[![PyPI version](https://badge.fury.io/py/noctis-ai.svg)](https://badge.fury.io/py/noctis-ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI downloads](https://img.shields.io/pypi/dm/noctis-ai.svg)](https://pypi.org/project/noctis-ai/)

## 🚀 What is Noctis?

**Noctis** is a revolutionary AI agent framework that gives you instant access to 10 specialized AI developers, each an expert in their domain. Think of it as having a senior developer, security expert, performance engineer, and more - all available 24/7 through a simple Python import.

**Stop struggling with complex AI setups. Start building with Noctis.**

## ✨ Why Developers Love Noctis

### 🎯 **Instant Expertise**
- **Zero learning curve** - Get expert-level assistance in seconds
- **Domain-specific knowledge** - Each agent is trained for specific development tasks
- **Production-ready** - Built with enterprise-grade error handling and validation

### 🚀 **10 Specialized Agents, One Framework**

| Agent | Superpower | Use Case |
|-------|------------|----------|
| **🔍 Code Reviewer** | Spot bugs, security issues, and quality problems instantly | Code reviews, quality assurance, team collaboration |
| **🐛 Debugger** | Troubleshoot complex errors with AI-powered analysis | Error resolution, system debugging, performance issues |
| **📚 Documentation Writer** | Create crystal-clear docs that developers actually read | API documentation, READMEs, user guides, technical specs |
| **🛡️ Security Auditor** | Find vulnerabilities before hackers do | Security reviews, penetration testing, compliance audits |
| **⚡ Performance Optimizer** | Make your code run faster than ever | Performance tuning, bottleneck identification, optimization |
| **🧪 Testing Specialist** | Build bulletproof testing strategies | Test planning, test case creation, coverage analysis |
| **🏗️ Architect** | Design scalable systems like a senior architect | System design, architecture planning, technology selection |
| **🔄 DevOps Engineer** | Streamline your CI/CD and infrastructure | Pipeline design, deployment automation, infrastructure setup |
| **⚙️ Code Generator** | Generate production-ready code from specs | Boilerplate code, API implementations, CRUD operations |
| **🔧 Refactoring Specialist** | Transform legacy code into clean, maintainable code | Technical debt reduction, code modernization, best practices |

### 💡 **Real-World Impact**

```python
# Before Noctis: Hours of debugging, research, and trial-and-error
# After Noctis: Expert guidance in seconds

from noctis import CodeReviewAgent, SecurityAgent, PerformanceAgent

# Get instant code review
reviewer = CodeReviewAgent()
issues = reviewer.ask("Review this code for security and quality issues")

# Security audit in seconds
security = SecurityAgent()
vulnerabilities = security.ask("Find security flaws in this authentication code")

# Performance optimization
optimizer = PerformanceAgent()
improvements = optimizer.ask("How can I make this algorithm 10x faster?")
```

## 🚀 Get Started in 30 Seconds

### 1. **Install Noctis**
```bash
pip install noctis-ai
```

### 2. **Set Your API Key**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 3. **Start Building**
```python
from noctis import CodeReviewAgent

# Create your first AI agent
agent = CodeReviewAgent()

# Get expert code review
response = agent.ask("Review this Python function for best practices")
print(response)
```

## 🎯 Perfect For

- **🚀 Startup Teams** - Get enterprise-level expertise without the cost
- **👥 Solo Developers** - Have a team of experts at your fingertips
- **🏢 Enterprise Teams** - Standardize development practices across teams
- **🎓 Learning Developers** - Learn from AI experts in real-time
- **🔧 DevOps Engineers** - Automate and optimize your infrastructure
- **🛡️ Security Teams** - Proactive vulnerability detection and remediation

## 🛠️ Complete Feature Overview

### **🧠 Core Agent Framework**

#### **Base Noctis Class**
```python
from noctis import Noctis
from noctis.memory.sqlite import SQLiteMemory

# Create a custom agent with memory
agent = Noctis(
    model="gpt-4",
    memory=SQLiteMemory("my_project.db"),
    tools=["web.search", "web.fetch"]
)

# Basic interaction
response = agent.ask("What are the best practices for Python error handling?")

# Chat mode (alias for ask)
response = agent.chat("Can you elaborate on the second point?")

# Advanced reasoning with thought process
answer, thoughts = agent.think(
    "How should I design a microservices architecture?",
    max_steps=5,
    return_thoughts=True
)
```

#### **Predefined Agent System**
```python
from noctis import (
    CodeReviewAgent, DebuggingAgent, DocumentationAgent,
    SecurityAgent, PerformanceAgent, TestingAgent,
    ArchitectureAgent, DevOpsAgent, CodeGenerationAgent,
    RefactoringAgent, PredefinedAgent
)

# Factory function for dynamic agent creation
agent = create_agent("code_reviewer", model="gpt-4")

# List all available agent types
available_agents = get_available_agents()
agent_types = list_agent_types()

# Create custom agents by extending PredefinedAgent
class CustomAgent(PredefinedAgent):
    def _setup_agent(self):
        system_prompt = """You are a specialized agent for [your domain]..."""
        # Custom setup logic
```

### **🔌 Multi-Model Support**

#### **OpenAI Models**
```python
from noctis.models.openai_adapter import OpenAIAdapter

# Use any OpenAI model
agent = CodeReviewAgent("gpt-4")
agent = CodeReviewAgent("gpt-4o-mini")
agent = CodeReviewAgent("gpt-3.5-turbo")

# Custom OpenAI adapter
openai_adapter = OpenAIAdapter("gpt-4", api_key="your-key")
agent = CodeReviewAgent(openai_adapter)
```

#### **Local Models with Ollama**
```python
from noctis.models.ollama_adapter import OllamaAdapter

# Use local Ollama models
ollama_adapter = OllamaAdapter(
    base_url="http://localhost:11434",
    model="llama2"
)
agent = CodeReviewAgent(ollama_adapter)

# Different Ollama models
agent = CodeReviewAgent(OllamaAdapter(model="codellama"))
agent = CodeReviewAgent(OllamaAdapter(model="mistral"))
agent = CodeReviewAgent(OllamaAdapter(model="neural-chat"))
```

#### **Mock Adapter for Testing**
```python
from noctis.models.openai_adapter import MockAdapter

# Use mock adapter for testing
mock_adapter = MockAdapter("test-model")
agent = CodeReviewAgent(mock_adapter)
```

### **🧠 Advanced Memory System**

#### **SQLite Memory with Full Features**
```python
from noctis.memory.sqlite import SQLiteMemory

# Create memory with custom database
memory = SQLiteMemory("project_specific.db")

# Add messages to memory
memory.add("user", "What are Python best practices?")
memory.add("assistant", "Here are the key Python best practices...")

# Retrieve memory
all_messages = memory.get_all()  # List of (role, content) tuples
recent_messages = memory.get_recent(10)  # Last 10 messages as dicts

# Clear memory when needed
memory.clear()

# Automatic memory management in agents
agent = CodeReviewAgent()
agent.agent.memory = memory  # Use custom memory
```

#### **Memory Persistence Features**
- **Automatic storage** - All conversations automatically saved
- **Context awareness** - Agents remember previous interactions
- **Database isolation** - Separate memory per project/agent
- **Timestamp tracking** - Full conversation history with timestamps
- **Memory optimization** - Efficient retrieval of recent context

### **🛠️ Built-in Tools & Extensions**

#### **Web Tools**
```python
from noctis.tools import run_tool, get_registry

# Web search with multiple providers
search_results = run_tool("web.search", {
    "query": "Python async best practices",
    "num_results": 10,
    "provider": "ddg"  # or "bing"
})

# Fetch single URL content
content = run_tool("web.fetch", {
    "url": "https://example.com",
    "timeout": 15,
    "snippet_chars": 500
})

# Fetch multiple URLs in parallel
urls = ["https://site1.com", "https://site2.com", "https://site3.com"]
results = run_tool("web.fetch_many", {
    "urls": urls,
    "max_workers": 5,
    "snippet_chars": 300
})

# Search and fetch combined
combined = run_tool("web.search_fetch", {
    "query": "Python performance optimization",
    "num_results": 5,
    "snippet_chars": 400,
    "max_paragraphs": 3
})
```

#### **Agent Management Tools**
```python
# Create new agents dynamically
new_agent = run_tool("agent.create", {
    "name": "DataAnalysisAgent",
    "goal": "Analyze data and provide insights",
    "constraints": ["Use only statistical methods", "Provide visualizations"],
    "tools": ["web.search", "web.fetch"],
    "memory": {}
})

# Execute agent actions
results = run_tool("agent.run", {
    "agent": new_agent,
    "query": "Analyze the latest Python performance benchmarks"
})
```

#### **Tool Framework & Extensions**
```python
from noctis.tools import tool

# Create custom tools
@tool(
    name="file.analyze",
    schema={
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "analysis_type": {"type": "string", "enum": ["complexity", "style", "security"]}
        },
        "required": ["file_path"]
    },
    description="Analyze Python files for various metrics"
)
def analyze_file(file_path: str, analysis_type: str = "complexity"):
    # Your custom tool implementation
    return {"file": file_path, "analysis": "results"}

# Use your custom tool
results = run_tool("file.analyze", {
    "file_path": "main.py",
    "analysis_type": "security"
})
```

### **📱 Command Line Interface (CLI)**

#### **Full CLI Capabilities**
```bash
# List all available agents
noctis --list

# Interactive mode with any agent
noctis code_reviewer
noctis security_auditor
noctis performance_optimizer

# Single query mode
noctis debugger -q "Help me fix this Python error"
noctis documentation_writer -q "Write a README for my project"

# Model selection
noctis code_reviewer -m gpt-4
noctis security_auditor -m gpt-4o-mini

# Force interactive mode
noctis performance_optimizer -i

# Help and usage
noctis --help
```

#### **CLI Features**
- **Interactive sessions** - Chat with agents like team members
- **Single query mode** - Quick answers without full sessions
- **Model flexibility** - Switch between different AI models
- **Agent validation** - Automatic validation of agent types
- **Help system** - Built-in usage tips and examples
- **Error handling** - Graceful error handling and user feedback

### **🔧 Advanced Configuration**

#### **Environment Variables**
```bash
# OpenAI Configuration
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_BASE_URL="https://api.openai.com/v1"  # Optional custom endpoint

# Ollama Configuration
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_MODEL="llama2"  # Default model

# Noctis Configuration
export NOCTIS_DEFAULT_MODEL="gpt-4o-mini"
export NOCTIS_MEMORY_PATH="./noctis_memory.db"
```

#### **Custom Model Adapters**
```python
from noctis.models.openai_adapter import ModelAdapterBase

class CustomOpenAIAdapter(ModelAdapterBase):
    def __init__(self, model: str, custom_config: dict):
        self.model = model
        self.config = custom_config
    
    def send(self, messages: List[Dict[str, str]]) -> str:
        # Custom implementation
        return "Custom response"

# Use custom adapter
custom_adapter = CustomOpenAIAdapter("custom-model", {"key": "value"})
agent = CodeReviewAgent(custom_adapter)
```

### **🧪 Testing & Quality Assurance**

#### **Built-in Testing Support**
```python
# Test agent creation
from noctis import create_agent

def test_agent_creation():
    agent = create_agent("code_reviewer")
    assert agent is not None
    assert hasattr(agent, 'ask')

# Test memory system
from noctis.memory.sqlite import SQLiteMemory

def test_memory():
    memory = SQLiteMemory(":memory:")  # In-memory database for testing
    memory.add("user", "test message")
    recent = memory.get_recent(1)
    assert len(recent) == 1
    assert recent[0]["content"] == "test message"
```

#### **Testing Features**
- **Mock adapters** - Test without API calls
- **In-memory databases** - Isolated testing environments
- **Agent validation** - Ensure agents work correctly
- **Memory testing** - Verify persistence and retrieval
- **Tool testing** - Validate custom tool functionality

### **📊 Performance & Reliability Features**

#### **Built-in Optimizations**
- **Connection pooling** - Efficient database connections
- **Caching** - LRU cache for web search results
- **Parallel processing** - Concurrent URL fetching
- **Memory management** - Efficient SQLite operations
- **Error handling** - Comprehensive error recovery

#### **Scalability Features**
- **Multiple agents** - Run multiple agents simultaneously
- **Memory isolation** - Separate databases per project
- **Tool registry** - Centralized tool management
- **Model switching** - Easy model changes without restart
- **Session management** - Persistent conversations

### **🔒 Security & Privacy**

#### **Security Features**
- **API key management** - Secure environment variable handling
- **Input validation** - JSON schema validation for tools
- **Error sanitization** - Safe error message handling
- **Memory isolation** - Separate databases prevent data leakage
- **Local model support** - Use Ollama for privacy-sensitive applications

#### **Privacy Options**
- **Local processing** - Run with Ollama models locally
- **Data isolation** - Separate memory per project
- **No external logging** - Conversations stay on your system
- **Custom endpoints** - Use your own API endpoints

### **🚀 Advanced Usage Patterns**

#### **Multi-Agent Workflows**
```python
from noctis import (
    CodeReviewAgent, SecurityAgent, PerformanceAgent,
    DocumentationAgent, TestingAgent
)

def comprehensive_code_analysis(code: str):
    # Create specialized agents
    reviewer = CodeReviewAgent()
    security = SecurityAgent()
    performance = PerformanceAgent()
    docs = DocumentationAgent()
    tester = TestingAgent()
    
    # Parallel analysis
    results = {
        "review": reviewer.ask(f"Review this code: {code}"),
        "security": security.ask(f"Security audit: {code}"),
        "performance": performance.ask(f"Performance analysis: {code}"),
        "documentation": docs.ask(f"Generate documentation for: {code}"),
        "testing": tester.ask(f"Create test strategy for: {code}")
    }
    
    return results
```

#### **Custom Agent Architectures**
```python
from noctis import PredefinedAgent, Noctis
from noctis.memory.sqlite import SQLiteMemory

class DataScienceAgent(PredefinedAgent):
    def _setup_agent(self):
        system_prompt = """You are a data science expert specializing in:
        - Statistical analysis and hypothesis testing
        - Machine learning model selection and evaluation
        - Data visualization and interpretation
        - Python libraries: pandas, numpy, scikit-learn, matplotlib
        
        Provide practical, implementable advice with code examples."""
        
        self.agent = Noctis(
            model=self.model,
            memory=SQLiteMemory("datascience_memory.db")
        )
        
        # Override system prompt
        self.agent._messages = lambda text: [
            {"role": "system", "content": system_prompt},
            *self.agent.memory.get_recent(10),
            {"role": "user", "content": text}
        ]

# Use custom agent
ds_agent = DataScienceAgent("gpt-4")
analysis = ds_agent.ask("How should I approach this classification problem?")
```

#### **Memory Management Strategies**
```python
from noctis.memory.sqlite import SQLiteMemory

# Project-specific memory
project_memory = SQLiteMemory("my_project.db")
agent = CodeReviewAgent()
agent.agent.memory = project_memory

# Session-based memory
session_memory = SQLiteMemory("session_123.db")
session_agent = CodeReviewAgent()
session_agent.agent.memory = session_memory

# Shared memory across agents
shared_memory = SQLiteMemory("team_shared.db")
reviewer = CodeReviewAgent()
reviewer.agent.memory = shared_memory
security = SecurityAgent()
security.agent.memory = shared_memory
```

## 📱 CLI Usage Examples

```bash
# Quick code review
noctis code_reviewer -q "Review this Python function for best practices"

# Interactive security audit
noctis security_auditor -i

# Performance optimization with specific model
noctis performance_optimizer -m gpt-4 -q "How can I optimize this algorithm?"

# Documentation writing session
noctis documentation_writer

# Testing strategy development
noctis testing_specialist -q "Create a testing strategy for my Flask API"
```

## 🧪 Testing & Quality

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_predefined_agents.py

# Run with coverage
python -m pytest --cov=noctis tests/

# Run specific test functions
python -m pytest tests/test_predefined_agents.py::test_code_review_agent
```

## 🤝 Community & Support

- **📖 Documentation** - Comprehensive guides and examples
- **🐛 Issue Tracking** - Report bugs and request features
- **💬 Discussions** - Join the community conversation
- **⭐ Star the Repo** - Show your support for Noctis
- **🔧 Contributing** - Add new agents, tools, and features

## 🚀 Roadmap

- **🔌 Plugin System** - Extend agents with custom tools
- **🌐 Web Interface** - Browser-based agent interactions
- **📊 Analytics Dashboard** - Track agent usage and performance
- **🔒 Enterprise Features** - SSO, audit logs, and compliance tools
- **🤖 Agent Orchestration** - Multi-agent coordination and workflows
- **📱 Mobile Support** - Mobile-optimized interfaces
- **🌍 Multi-language Support** - Support for non-English languages

## 📄 License

MIT License - Use Noctis in your personal and commercial projects freely.

## 🙏 Acknowledgments

Built with ❤️ by the developer community, powered by OpenAI and Ollama.

---

## 🎯 Ready to Transform Your Development Workflow?

**Get started with Noctis today and experience the future of AI-powered development.**

```bash
pip install noctis-ai
```

**Join thousands of developers who are already building faster, smarter, and more securely with Noctis.**

[⭐ Star on GitHub](https://github.com/Dhiaelhak-Rached/Noctis) | [📖 Documentation](https://github.com/Dhiaelhak-Rached/Noctis#readme) | [🐛 Report Issues](https://github.com/Dhiaelhak-Rached/Noctis/issues)

---

**Happy coding with Noctis! 🚀✨**
