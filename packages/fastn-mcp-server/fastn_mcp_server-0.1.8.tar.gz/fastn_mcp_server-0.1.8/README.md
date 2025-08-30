# FastN MCP Server

[![PyPI version](https://img.shields.io/pypi/v/fastn-mcp-server.svg)](https://pypi.org/project/fastn-mcp-server/)
[![Python versions](https://img.shields.io/pypi/pyversions/fastn-mcp-server.svg)](https://pypi.org/project/fastn-mcp-server/)
[![License](https://img.shields.io/github/license/fastn-ai/mcp-server.svg)](LICENSE)

The Fastn server is a powerful, scalable platform that enables dynamic tool registration and execution based on API definitions. It seamlessly integrates with services like Claude.ai and Cursor.ai, providing a unified server solution for a wide range of tasks. With its robust architecture, Fastn delivers exceptional performance and flexibility for real-time, API-driven operations.

- **Communication tools**: Slack, Gmail, Microsoft Teams
- **Business platforms**: HubSpot, Notion, Salesforce
- **Development tools**: GitHub, GitLab, Jira
- **And many more**

The FastN MCP Server package enables AI systems to:
- Send and retrieve emails
- Create and update contacts in CRM systems
- Post and retrieve messages from Slack
- And perform many other operations across integrated services
## Key Features

- **Zero-configuration tools**: All tools are automatically registered based on your FastN workspace configuration
- **Secure authentication**: API key or tenant-based authentication with your FastN account
- **MCP Protocol support**: Works with any client that supports the MCP protocol
- **Simple command-line interface**: Easy to use with minimal required parameters
- **Clean installation via pipx**: Isolated from your system Python environment

## Getting Started

### 1. Install the package

The recommended way to install the FastN MCP server is using [pipx](https://pypa.github.io/pipx/):

```bash
pipx install fastn-mcp-server
```

Alternatively, you can use pip:

```bash
pip install fastn-mcp-server
```

### 2. Prepare your credentials

Before using this package, you need:

1. A FastN account (sign up at [fastn.ai](https://fastn.ai) if you don't have one)
2. Your FastN API key (available in your account settings) OR tenant ID and auth token
3. Your FastN Space ID (available in your account dashboard)

### 3. Integrate with your AI assistant

First, find the path to your fastn-mcp-server command:

**macOS/Linux:**
```bash
which fastn-mcp-server
```

**Windows:**
```bash
where fastn-mcp-server
```

The configuration JSON is the same for both Claude and Cursor. Replace the path with the actual path from the command above:

#### API Key Authentication (Recommended for individual users)

**macOS/Linux example:**
```json
{
    "mcpServers": {
        "fastn": {
            "command": "/Users/username/.local/bin/fastn-mcp-server",
            "args": [
                "--api_key",
                "YOUR_API_KEY",
                "--space_id",
                "YOUR_WORKSPACE_ID"
            ]
        }
    }
}
```

#### Tenant-Based Authentication (Recommended for organizations)

**macOS/Linux example:**
```json
{
    "mcpServers": {
        "fastn": {
            "command": "/Users/username/.local/bin/fastn-mcp-server",
            "args": [
                "--tenant_id",
                "YOUR_TENANT_ID",
                "--auth_token",
                "YOUR_AUTH_TOKEN",
                "--space_id",
                "YOUR_WORKSPACE_ID"
            ]
        }
    }
}
```

**Windows example:**
```json
{
    "mcpServers": {
        "fastn": {
            "command": "C:\\Users\\username\\AppData\\Local\\Programs\\Python\\Python310\\Scripts\\fastn-mcp-server.exe",
            "args": [
                "--api_key",
                "YOUR_API_KEY",
                "--space_id",
                "YOUR_WORKSPACE_ID"
            ]
        }
    }
}
```

> **Important note for Windows users:** Make sure to use double backslashes (\\\\) in your path, as shown in the example above. Single backslashes will cause errors in JSON.

#### Integration with Claude

1. Open the Claude configuration file:

**Windows:**
```bash
# Using Notepad
notepad "%APPDATA%\Claude\claude_desktop_config.json"

# Using VS Code
code "%APPDATA%\Claude\claude_desktop_config.json"
```

**Mac:**
```bash
# Using TextEdit
open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Using VS Code
code ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

2. Add the configuration JSON shown above.

#### Integration with Cursor

1. Open Cursor settings
2. Click on "MCP" in the settings menu
3. Click on "Add New"
4. Add a name for your server (e.g., "fastn")
5. Select "Command" as the type
6. Use the same configuration as shown above for Claude

That's it! Your AI assistant now has access to all the tools configured in your FastN workspace.

## Manual Usage (Optional)

If you need to run the server directly, use one of the following authentication methods:

### API Key Authentication

```bash
fastn-mcp-server --api_key YOUR_API_KEY --space_id YOUR_SPACE_ID
```

### Tenant-Based Authentication

```bash
fastn-mcp-server --tenant_id YOUR_TENANT_ID --auth_token YOUR_AUTH_TOKEN --space_id YOUR_SPACE_ID
```

### Required Arguments

For API Key Authentication:
- `--api_key`: Your FastN API key for authentication
- `--space_id`: Your FastN Space ID for the target environment

For Tenant-Based Authentication:
- `--tenant_id`: Your FastN tenant ID
- `--auth_token`: Your FastN authentication token
- `--space_id`: Your FastN Space ID for the target environment

### Examples

API Key Authentication:
```bash
fastn-mcp-server --api_key "fastn_key_123..." --space_id "space_456..."
```

Tenant-Based Authentication:
```bash
fastn-mcp-server --tenant_id "tenant_123..." --auth_token "token_456..." --space_id "space_789..."
```

## Security Considerations

- Keep your API key, tenant ID, and auth token secure
- Use environment variables or a secure configuration file for production deployments
- Regularly rotate your API keys and auth tokens for enhanced security

## License

This project is licensed under the terms included in the [LICENSE](LICENSE) file.

## Support

For questions, issues, or feature requests, please visit:
- Documentation: [https://docs.fastn.ai](https://docs.fastn.ai)
- Community: [https://community.fastn.ai](https://community.fastn.ai)
