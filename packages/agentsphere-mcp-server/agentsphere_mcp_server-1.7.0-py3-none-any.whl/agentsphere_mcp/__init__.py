"""AgentSphere STDIO MCP Server

an MCP Server designed for AI to connect and operate agent-sphere sandboxes.

- MCP Tools Description

This MCP Server provides the following 4 tools for AI usage:
1. exec_command: execute Linux system commands in the sandbox
2. get_preview_link: get the access URL for web services in the sandbox
3. upload_files_to_sandbox: upload local files or folders to a specified directory in the sandbox
4. find_file_path: search for files or directories by name and return their absolute paths

- Usage: MCP Server Configuration

To configure this server in Efflux, Cursor, or other MCP clients, add the following configuration to your MCP configuration file:

```json
{
  "mcpServers": {
    "agentsphere": {
      "command": "uvx",
      "args": ["agentsphere-mcp-server"],
      "env": {
        "AGENTSPHERE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```
"""

__version__ = "1.7.0"
