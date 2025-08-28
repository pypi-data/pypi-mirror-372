# pCloudy-MCP

## 🔌 What is MCP?

**MCP (Modular Context Protocol)** is an open standard that simplifies how applications interact with large language models (LLMs). It's like a **USB-C port for AI** — a single, consistent way to connect tools and data sources to your LLMs.

MCP allows you to:

* 🔌 Plug LLMs into existing tools and APIs with ease
* 🔄 Switch between different LLM vendors with minimal effort
* 🔐 Keep data secure by executing within your infrastructure
* ⚙️ Build composable, modular workflows for real-world use cases

📖 [Learn more about MCP →](https://modelcontextprotocol.io/introduction)

---

## 📱 About pCloudy-MCP

`pCloudy-MCP` serves as an MCP server that interacts with the pCloudy Device Cloud to:

* 📊 Manage test cases via natural language
* 📲 Execute manual or scripted tests on Android/iOS devices
* 🤖 Automate test steps using QPilot, an LLM-compatible AI testing agent

---

## 🧠 Why Use It?

### ✅ Test from Anywhere

Easily control real devices using natural prompts — whether you're in a terminal, IDE, Claude, Cursor, or any other AI tool.

### ✅ Reduce Context Switching

Trigger device actions, upload builds, or run flows directly from your development or chat environment — no more jumping between tools.

---

## 🧪 Examples

### Manual Testing (Natural Language)

Use plain English to test your apps across real devices:

```
Upload the APK to the cloud
Install the app on a Pixel 6
Resign and upload the iOS build
```

### 🤖 QPilot Automation

Run intelligent automation steps with natural language:

```
Book another iOS device and run the following:
  - Enter username 'user@gmail.com'
  - Enter password 'pass'
  - Click on login
```

---

## ✅ How to Use

### 🔧 Prerequisites

1. Sign up for pCloudy account
   👉 [pCloudy Sign Up](https://device.pcloudy.com/signup)

2. Install **Python ≥ 3.10** on your machine

3. Install [**uv**](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer)

---

### ⚙️ Configuration (MCP-compatible tools)

To launch the pCloudy MCP server, use this configuration:

1. For claude **claude_desktop_config.json**

```json
{
  "mcpServers": {
    "pCloudy": {
      "command": "uvx",
      "args": ["pcloudy-mcp"],
      "env": {
        "PCLOUDY_USERNAME": "<your_pcloudy_username>",
        "PCLOUDY_API_KEY": "<your_pcloudy_api_key>",
        "PCLOUDY_CLOUD_URL": "<your_pcloudy_cloud_url>"
      }
    }
  }
}
```
1. For cursor **mcp.json**

```json
{
  "mcpServers": {
    "pCloudy": {
      "command": "uvx",
      "args": ["pcloudy-mcp"],
      "env": {
        "PCLOUDY_USERNAME": "<your_pcloudy_username>",
        "PCLOUDY_API_KEY": "<your_pcloudy_api_key>",
        "PCLOUDY_CLOUD_URL": "<your_pcloudy_cloud_url>"
      }
    }
  }
}
```

Replace the values with your actual credentials and endpoint.

---

## 💠 Development

To work with this repo locally:

```bash
git clone https://github.com/Smart-Software-Testing-Solutions-Opkey/pcloudy-mcp-server.git

cd pcloudy-mcp-server

uv pip install .[dev]
```

Use the following `poethepoet` tasks:

```bash
poe format         # black + isort
poe lint-check     # ruff linter
poe typecheck      # mypy type checks
poe check-server   # check server is working or not
```

---



## 📁 Project Structure

```
src/
└── pcloudy_mcp/
    ├── main.py          # CLI entry point
    ├── server.py        # FastMCP app factory
    ├── api/             # API logic (auth, booking, etc.)
    ├── utils/           # Configuration 
	|── tools/           # Tools setup
	├── logger/          # logging
    ├── Constants/       # constants
	├── errors/          # Handle Errors and Exceptions
	└── validation/      # Env Validation
```


## 👥 Contributors

Maintained by the pCloudy team.
