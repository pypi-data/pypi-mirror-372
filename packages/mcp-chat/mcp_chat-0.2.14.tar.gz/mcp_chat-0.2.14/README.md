# Simple MCP Client to Explore MCP Servers [![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/hideya/langchain-mcp-tools-py/blob/main/LICENSE) [![pypi version](https://img.shields.io/pypi/v/mcp-chat.svg)](https://pypi.org/project/mcp-chat/)


**Quickly test and explore MCP servers from the command line!**

A simple, text-based CLI client for [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) servers built with LangChain and Python.  
Suitable for testing MCP servers, exploring their capabilities, and prototyping integrations.

Internally it uses [LangChain ReAct Agent](https://langchain-ai.github.io/langgraph/reference/agents/) and
a utility function `convert_mcp_to_langchain_tools()` from [`langchain_mcp_tools`](https://pypi.org/project/langchain-mcp-tools/).  

A TypeScript equivalent of this utility is available [here](https://www.npmjs.com/package/@h1deya/mcp-try-cli)

## Prerequisites

- Python 3.11+
- [optional] [`uv` (`uvx`)](https://docs.astral.sh/uv/getting-started/installation/)
  installed to run Python package-based MCP servers
- [optional] [npm 7+ (`npx`)](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
  to run Node.js package-based MCP servers
- LLM API key(s) from
  [OpenAI](https://platform.openai.com/api-keys),
  [Anthropic](https://console.anthropic.com/settings/keys),
  [Google AI Studio (for GenAI/Gemini)](https://aistudio.google.com/apikey),
  [xAI](https://console.x.ai/),
  [Cerebras](https://cloud.cerebras.ai),
  and/or
  [Groq](https://console.groq.com/keys),
  as needed

## Quick Start

- Install `mcp-chat` tool.
  This can take up to a few minutes to complete:
  ```bash
  pip install mcp-chat
  ```

- Configure LLM and MCP Servers settings via the configuration file, `llm_mcp_config.json5`
  ```bash
  code llm_mcp_config.json5
  ```

  The following is a simple configuration for quick testing:
  ```json5
  {
    "llm": {
      "provider": "openai",       "model": "gpt-5-mini",
      // "provider": "anthropic",    "model": "claude-3-5-haiku-latest",
      // "provider": "google_genai", "model": "gemini-2.5-flash",
      // "provider": "xai",          "model": "grok-3-mini",
      // "provider": "cerebras",     "model": "gpt-oss-120b",
      // "provider": "groq",         "model": "openai/gpt-oss-20b",
    },

    "mcp_servers": {
      "us-weather": {  // US weather only
        "command": "npx", 
        "args": ["-y", "@h1deya/mcp-server-weather"]
      },
    },

    "example_queries": [
      "Tell me how LLMs work in a few sentences",
      "Are there any weather alerts in California?",
    ],
  }
  ```

- Set up API keys
  ```bash
  echo "ANTHROPIC_API_KEY=sk-ant-...                                       
  OPENAI_API_KEY=sk-proj-...
  GOOGLE_API_KEY=AI...
  XAI_API_KEY=xai-...
  CEREBRAS_API_KEY=csk-...
  GROQ_API_KEY=gsk_..." > .env
  
  code .env
  ```

- Run the tool
  ```bash
  mcp-chat
  ```
  By default, it reads the configuration file, `llm_mcp_config.json5`, from the current directory.  
  Then, it applies the environment variables specified in the `.env` file,
  as well as the ones that are already defined.

## Building from Source

See [README_DEV.md](https://github.com/hideya/mcp-client-langchain-py/blob/main/README_DEV.md) for details.

## Features

- **Easy setup**: Works out of the box with popular MCP servers
- **Flexible configuration**: JSON5 config with environment variable support
- **Multiple LLM/API providers**: OpenAI, Anthropic, Google (GenAI), xAI, Ceberas, Groq
- **Command & URL servers**: Support for both local and remote MCP servers
- **Local MCP Server logging**: Save stdio MCP server logs with customizable log directory
- **Interactive testing**: Example queries for the convenience of repeated testing

## Limitations

- **Tool Return Types**: Currently, only text results of tool calls are supported.
It uses LangChain's `response_format: 'content'` (the default) internally, which only supports text strings.
While MCP tools can return multiple content types (text, images, etc.), this library currently filters and uses only text content.
- **MCP Features**: Only MCP [Tools](https://modelcontextprotocol.io/docs/concepts/tools) are supported. Other MCP features like Resources, Prompts, and Sampling are not implemented.

## Usage

### Basic Usage

```bash
mcp-chat
```

By default, it reads the configuration file, `llm_mcp_config.json5`, from the current directory.  
Then, it applies the environment variables specified in the `.env` file,
as well as the ones that are already defined.  
It outputs local MCP server logs to the current directory.

### With Options

```bash
# Specify the config file to use
mcp-chat --config my-config.json5

# Store local (stdio) MCP server logs in specific directory
mcp-chat --log-dir ./logs

# Enable verbose logging
mcp-chat --verbose

# Show help
mcp-chat --help
```

## Supported Model/API Providers

- **OpenAI**: `gpt-5-mini`, `gpt-4.1-nano`, etc.
- **Anthropic**: `claude-sonnet-4-0`, `claude-3-5-haiku-latest`, etc.
- **Google (GenAI)**: `gemini-2.5-flash`, `gemini-2.5-pro`, etc.
- **xAI**: `grok-3-mini`, `grok-4`, etc.
- **Cerebras**: `gpt-oss-120b`, etc.
- **Groq**: `openai/gpt-oss-20b`, `openai/gpt-oss-120b`, etc.

## Configuration

Create a `llm_mcp_config.json5` file:

- [The configuration file format](https://github.com/hideya/mcp-client-langchain-py/blob/main/llm_mcp_config.json5)
  for MCP servers follows the same structure as
  [Claude for Desktop](https://modelcontextprotocol.io/quickstart/user),
  with one difference: the key name `mcpServers` has been changed
  to `mcp_servers` to follow the snake_case convention
  commonly used in JSON configuration files.
- The file format is [JSON5](https://json5.org/),
  where comments and trailing commas are allowed.
- The format is further extended to replace `${...}` notations
  with the values of corresponding environment variables.
- Keep all the credentials and private info in the `.env` file
  and refer to them with `${...}` notation as needed

```json5
{
  "llm": {
    "provider": "openai",
    "model": "gpt-4.1-nano",
    // model: "gpt-5-mini",
  },

  // "llm": {
  //   "provider": "anthropic",
  //   "model": "claude-3-5-haiku-latest",
  //   // "model": "claude-sonnet-4-0",
  // },

  // "llm": {
  //   "provider": "google_genai",
  //   "model": "gemini-2.5-flash",
  //   // "model": "gemini-2.5-pro",
  // },

  // "llm": {
  //   "provider": "xai",
  //   "model": "grok-3-mini",
  //   // "model": "grok-4",
  // },

  // "llm": {
  //   "provider": "cerebras",
  //   "model": "gpt-oss-120b",
  // },

  // "llm": {
  //   "provider": "groq",
  //   "model": "openai/gpt-oss-20b",
  //   // "model": "openai/gpt-oss-120b",
  // },

  "example_queries": [
    "Tell me how LLMs work in a few sentences",
    "Are there any weather alerts in California?",
    "Read the news headlines on bbc.com",
  ],

  "mcp_servers": {
    // Local MCP server that uses `npx`
    "weather": {
      "command": "npx", 
      "args": [ "-y", "@h1deya/mcp-server-weather" ]
    },

    // Another local server that uses `uvx`
    "fetch": {
      "command": "uvx",
      "args": [ "mcp-server-fetch" ]
    },

    "brave-search": {
      "command": "npx",
      "args": [ "-y", "@modelcontextprotocol/server-brave-search" ],
      "env": { "BRAVE_API_KEY": "${BRAVE_API_KEY}" }
    },

    // Remote MCP server via URL
    // Auto-detection: tries Streamable HTTP first, falls back to SSE
    "remote-mcp-server": {
      "url": "https://api.example.com/..."
    },

    // Server with authentication
    "github": {
      "type": "http",  // recommended to specify the protocol explicitly when authentication is used
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Environment Variables

Create a `.env` file for API keys:

```bash
OPENAI_API_KEY=sk-ant-...
ANTHROPIC_API_KEY=sk-proj-...
GOOGLE_API_KEY=AI...
XAI_API_KEY=xai-...
CEREBRAS_API_KEY=csk-...
GROQ_API_KEY=gsk_...

# Other services as needed
GITHUB_PERSONAL_ACCESS_TOKEN=github_pat_...
BRAVE_API_KEY=BSA...
```

## Popular MCP Servers to Try

There are quite a few useful MCP servers already available:

- [MCP Server Listing on the Official Site](https://github.com/modelcontextprotocol/servers?tab=readme-ov-file#model-context-protocol-servers)

## Troubleshooting

- Make sure your configuration and .env files are correct, especially the spelling of the API keys
- Check the local MCP server logs
- Use `--verbose` flag to view the detailed logs
- Refer to [Debugging Section in MCP documentation](https://modelcontextprotocol.io/docs/tools/debugging)

## Change Log

Can be found [here](https://github.com/hideya/mcp-client-langchain-py/blob/main/CHANGELOG.md)

## License

MIT License - see [LICENSE](https://github.com/hideya/mcp-client-langchain-py/blob/main/LICENSE) file for details.

## Contributing

Issues and pull requests welcome! This tool aims to make MCP server testing as simple as possible.
