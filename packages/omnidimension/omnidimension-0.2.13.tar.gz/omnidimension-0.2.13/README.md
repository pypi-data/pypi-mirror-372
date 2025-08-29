
# OmniDimension Python SDK

*Build and ship AI voice agents from a single prompt.*

OmniDimension lets you **build, test, and deploy** reliable voice AI assistants by simply describing them in plain text. The platform offers **rigorous simulation testing** and **real-time observability**, making it easy to debug and monitor agents in production.

👉 [Try the Web UI](https://www.omnidim.io/) — You can also build and test voice agents visually using our no-code interface.

---

## 🚀 Features

- **Prompt-based creation:** Define voice agents with natural language.
- **Drag-and-drop editor:** Chat or visually edit flows, voices, models, and more.
- **Prebuilt templates:** Use plug-and-play agent templates for common use cases.
- **Testing & monitoring:** Simulate edge cases and debug live calls.
- **Knowledge Base support:** Upload and attach documents (PDFs) for factual grounding.
- **Integrations:** Connect to external APIs, CRMs, or tools like Cal.com.
- **Phone agents:** Assign numbers and initiate real voice calls via the SDK.

---

## 📦 Installation

### Basic SDK

```bash
pip install omnidimension
````

### With MCP Server Support

```bash
pip install omnidimension[mcp]
```

> Requires Python 3.9+

---

## 🔐 Authentication

First, obtain your API key from the OmniDimension dashboard. Store it in your environment variables:

### Linux/macOS

```bash
export OMNIDIM_API_KEY="your_api_key_here"
```

### Windows (CMD)

```cmd
set OMNIDIM_API_KEY=your_api_key_here
```

### In Python

```python
import os
from omnidimension import Client

api_key = os.environ.get("OMNIDIM_API_KEY")
client = Client(api_key)
```

---

## ✨ SDK Usage

```python
from omnidimension import Client

# Initialize the client with your API key
client = Client(api_key="your_api_key")

# List agents
agents = client.agent.list()
print(agents)
```

---

## 🛰️ MCP Server Usage

You can run the MCP server in several ways:

### 1. Using the Python module:

```bash
python -m omnidimension.mcp_server --api-key your_api_key
```

### 2. Using the CLI entry point:

```bash
omnidim-mcp-server --api-key your_api_key
```

### 3. Using the compatibility module (for MCP clients):

```bash
python -m omnidim_mcp_server --api-key your_api_key
```

You can also set the API key using the environment variable:

```bash
export OMNIDIM_API_KEY=your_api_key
python -m omnidimension.mcp_server
```

---

## ⚙️ MCP Client Configuration

To use OmniDimension with MCP clients like Claude Desktop, save the following configuration to a file named `omnidim_mcp.json`:

```json
{
  "mcpServers": {
    "omnidim-mcp-server": {
      "command": "python3",
      "args": [
        "-m",
        "omnidim_mcp_server"
      ],
      "env": {
        "OMNIDIM_API_KEY": "<your_omnidim_api_key>"
      }
    }
  }
}
```

---

## 📚 Knowledge Base

```python
files = client.knowledge_base.list()
print(files)

file_ids = [123]
agent_id = 456
response = client.knowledge_base.attach(file_ids, agent_id)
print(response)
```

---

## 🔌 Integrations

```python
response = client.integrations.create_custom_api_integration(
    name="WeatherAPI",
    url="https://api.example.com/weather",
    method="GET"
)
print(response)

client.integrations.add_integration_to_agent(agent_id=123, integration_id=789)
```

---

## ☎️ Phone Number Management

```python
numbers = client.phone_number.list(page=1, page_size=10)
print(numbers)

client.phone_number.attach(phone_number_id=321, agent_id=123)
```

---

## 📁 Recommended Project Structure

```
/docs/
  ├── agents/
  ├── calling/
  ├── integrations/
  ├── knowledge_base/
  └── phone_numbers/

/examples/         # Sample Python scripts
/cookbook/         # Ready-made project use cases
```

---


## 🌐 Learn More

Visit [omnidim.io](https://www.omnidim.io/) to explore the full platform, UI builder, and templates.

