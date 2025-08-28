# agentsphere-mcp-server

## Introduction

**agent-sphere** is a cloud-based secure isolated sandbox infrastructure that provides AI with a stable, fast, and secure runtime environment.

**agentsphere-mcp-server** is an MCP Server designed for AI to connect and operate agent-sphere sandboxes.

**Official Website**: https://www.agentsphere.run/home



## MCP Tools Description

This MCP Server provides the following 4 tools for AI usage:

### 1. exec_command
**Function**: Execute Linux system commands in the sandbox

**Parameters**:
- `cmd` (string): The command to execute

**Return Value**: Execution result containing stdout, stderr, and success fields


### 2. get_preview_link
**Function**: Get the access URL for web services in the sandbox

**Parameters**:
- `port` (int): Port number

**Return Value**: Result containing the accessible URL


### 3. upload_files_to_sandbox
**Function**: Upload local files or folders to a specified directory in the sandbox

**Parameters**:
- `local_path` (string): Absolute path of local file or folder
- `target_path` (string, optional): Target directory path in the sandbox, defaults to `/user_uploaded_files/`

**Return Value**: Result containing the list of successfully uploaded files or error information


### 4. find_file_path
**Function**: Search for files or directories by name and return their absolute paths

**Parameters**:
- `filename` (string): The filename to search for (supports wildcards like *.py, project*, etc.)
- `search_path` (string, optional): Starting search path or shortcut option
  - Specific paths: e.g., "/Users/username/Desktop/Projects"
  - Shortcut options: "desktop" (default), "documents", "downloads", "home"

**Return Value**: Search results containing a list of found files/directories with complete paths, types, sizes, and modification times


## Usage

### MCP Server Configuration

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

**Note**:
- Replace `your_api_key_here` with your AgentSphere API key
- Please ensure uv is installed (uv is a modern Python dependency and project manager: https://docs.astral.sh/uv/getting-started/installation/)
- Please ensure network connectivity. Users in mainland China are recommended to enable global proxy to ensure proper functionality