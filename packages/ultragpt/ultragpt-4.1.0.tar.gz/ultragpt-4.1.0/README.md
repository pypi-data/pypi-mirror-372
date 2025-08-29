# 🤖 UltraGPT

**A powerful and modular library for advanced AI-based reasoning and step pipelines with multi-provider support**

[![Python](https://img.shields.io/badge/python-3.6+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.rst)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com)
[![Anthropic](https://img.shields.io/badge/Anthropic-Claude-purple.svg)](https://anthropic.com)

## 🌟 Features

- **🔄 Multi-Provider Support:** Use OpenAI and Anthropic Claude models seamlessly
- **📝 Steps Pipeline:** Break down complex tasks into manageable steps
- **🧠 Reasoning Pipeline:** Advanced multi-iteration reasoning capabilities
- **🛠️ Tool Integration:** Web search, calculator, math operations, and custom tools
- **🎯 Structured Output:** Get structured responses using Pydantic schemas
- **🔧 Tool Calling:** Execute custom tools with validated parameters
- **📊 Token Management:** Comprehensive token tracking across providers

## 📦 Installation

```bash
pip install ultragpt

# For environment variable support (optional)
pip install python-dotenv
```

**Note:** Starting with version 4.0.0, Anthropic Claude support is included by default!

## 🚀 Quick Start

### Basic Usage (OpenAI)
```python
from ultragpt import UltraGPT

# Initialize with OpenAI (default)
ultragpt = UltraGPT(api_key="your-openai-api-key")

# Simple chat
response, tokens, details = ultragpt.chat([
    {"role": "user", "content": "Write a story about an elephant."}
])
print("Response:", response)
print("Tokens used:", tokens)
```

### Multi-Provider Support
```python
from ultragpt import UltraGPT

# OpenAI (default)
ultragpt_openai = UltraGPT(api_key="your-openai-api-key")

# Claude
ultragpt_claude = UltraGPT(
    api_key="your-anthropic-api-key", 
    provider="anthropic"
)

# Both work the same way!
response, tokens, details = ultragpt_claude.chat([
    {"role": "user", "content": "Hello Claude!"}
])
```

### Provider:Model Format
```python
# Use provider:model format for specific models
ultragpt = UltraGPT(
    api_key="your-openai-api-key",
    claude_api_key="your-anthropic-api-key"  # For Claude models
)

# OpenAI models
response = ultragpt.chat([
    {"role": "user", "content": "Hello!"}
], model="openai:gpt-4o")

# Claude models  
response = ultragpt.chat([
    {"role": "user", "content": "Hello!"}
], model="claude:claude-3-sonnet-20240229")
```

## 🌐 Web Search & Tools

### Google Search Integration
```python
from ultragpt import UltraGPT

ultragpt = UltraGPT(
    api_key="your-openai-api-key",
    google_api_key="your-google-api-key",
    search_engine_id="your-search-engine-id"
)

# Web search with scraping
response = ultragpt.chat([
    {"role": "user", "content": "What are the latest AI trends?"}
], tools=["web-search"], tools_config={
    "web-search": {
        "max_results": 3,
        "enable_scraping": True,
        "max_scrape_length": 2000
    }
})
```

### Built-in Tools
```python
# Use multiple tools
response = ultragpt.chat([
    {"role": "user", "content": "Calculate 15% of 200 and check if 17 is prime"}
], tools=["calculator", "math-operations"])
```

## 🔧 Custom Tool Calling

### Define Custom Tools
```python
from pydantic import BaseModel
from ultragpt.schemas import UserTool

class EmailParams(BaseModel):
    recipient: str
    subject: str
    body: str

email_tool = UserTool(
    name="send_email",
    description="Send an email to a recipient",
    parameters_schema=EmailParams,
    usage_guide="Use when user wants to send an email",
    when_to_use="When user asks to send an email"
)

# Use custom tools
response, tokens = ultragpt.tool_call(
    messages=[{"role": "user", "content": "Send email to john@example.com about meeting"}],
    user_tools=[email_tool]
)
```

## 🧠 Advanced Pipelines

### Steps Pipeline
```python
response = ultragpt.chat([
    {"role": "user", "content": "Plan a trip to Japan for 2 weeks"}
], steps_pipeline=True, steps_model="gpt-4o-mini")  # Use cheaper model for steps
```

### Reasoning Pipeline
```python
response = ultragpt.chat([
    {"role": "user", "content": "Solve this complex problem: ..."}
], reasoning_pipeline=True, reasoning_iterations=5)
```

### Mixed Provider Pipelines
```python
# Use OpenAI for main response, Claude for reasoning
response = ultragpt.chat([
    {"role": "user", "content": "Complex analysis task"}
], 
model="openai:gpt-4o",  # Main model
reasoning_model="claude:claude-3-sonnet-20240229",  # Reasoning model
reasoning_pipeline=True
)
```

## 📊 Structured Output

### Using Pydantic Schemas
```python
from pydantic import BaseModel

class AnalysisResult(BaseModel):
    sentiment: str
    confidence: float
    keywords: list[str]

# Get structured output (works with both providers)
result = ultragpt.chat_with_schema(
    messages=[{"role": "user", "content": "Analyze: 'I love this product!'"}],
    schema=AnalysisResult
)
print(result.sentiment)  # "positive"
print(result.confidence)  # 0.95
```

## 🔄 History Management

```python
# Enable conversation history tracking
ultragpt = UltraGPT(
    api_key="your-api-key",
    track_history=True,
    max_history=50  # Keep last 50 messages
)

# Continue conversations naturally
response1 = ultragpt.chat([{"role": "user", "content": "My name is Alice"}])
response2 = ultragpt.chat([{"role": "user", "content": "What's my name?"}])
# Response2 will remember Alice from response1
```

## ⚙️ Configuration Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `api_key` | str | Required | OpenAI API key |
| `claude_api_key` | str | None | Anthropic API key (for Claude models) |
| `provider` | str | "openai" | Default provider ("openai" or "anthropic") |
| `model` | str | Auto-selected | Default model for provider |
| `temperature` | float | 0.7 | Output randomness (0-2) |
| `reasoning_iterations` | int | 3 | Number of reasoning steps |
| `tools` | list | [] | Enabled tools |
| `verbose` | bool | False | Enable detailed logging |
| `track_history` | bool | False | Enable conversation history |
| `max_history` | int | 100 | Maximum messages to keep |

## 🛠️ Available Tools

### Web Search
- **Google Custom Search** with result scraping
- Configurable result limits and scraping depth
- Error handling and rate limiting

### Calculator
- Mathematical expression evaluation
- Complex calculations with step-by-step solutions
- Support for scientific functions

### Math Operations
- Range checking and validation
- Statistical analysis and outlier detection
- Prime number checking and factorization
- Sequence analysis (arithmetic/geometric patterns)
- Percentage calculations and ratios

## 🌍 Environment Variables

Create a `.env` file for easy configuration:

```env
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GOOGLE_SEARCH_API_KEY=your-google-api-key
SEARCH_ENGINE_ID=your-search-engine-id
```

```python
from dotenv import load_dotenv
import os

load_dotenv()

ultragpt = UltraGPT(
    api_key=os.getenv("OPENAI_API_KEY"),
    claude_api_key=os.getenv("ANTHROPIC_API_KEY"),
    google_api_key=os.getenv("GOOGLE_SEARCH_API_KEY"),
    search_engine_id=os.getenv("SEARCH_ENGINE_ID")
)
```

## 📋 Requirements

- Python 3.6+
- OpenAI API key (for OpenAI models)
- Anthropic API key (for Claude models)
- Google Custom Search API (for web search tool)

**Built-in Dependencies:**
- `anthropic==0.60.0` - Claude API support (included by default)
- `openai>=1.59.3` - OpenAI API support
- `pydantic>=2.10.4` - Data validation and schemas

## 🚀 Examples

Check out the `examples/` directory for comprehensive usage examples:
- `example_tool_call.py` - Custom tool calling
- `example_claude_support.py` - Claude-specific features
- `example_multi_provider.py` - Multi-provider usage
- `example_history_control.py` - Conversation history

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Add tests if applicable
5. Commit your changes (`git commit -am 'Add new feature'`)
6. Push to the branch (`git push origin feature/improvement`)
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE.rst](LICENSE.rst) file for details.

## 👥 Author

**Ranit Bhowmick**
- Email: bhowmickranitking@duck.com
- GitHub: [@Kawai-Senpai](https://github.com/Kawai-Senpai)

## 🔗 Links

- [Documentation](docs/)
- [Examples](examples/)
- [Tests](tests/)
- [PyPI Package](https://pypi.org/project/ultragpt/)

---

<div align="center">
Made with ❤️ by Ranit Bhowmick
</div>
