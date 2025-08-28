# agentsphere-mcp-server

## 简介

**agent-sphere** 是一个云端安全隔离的沙箱基础设施，为 AI 提供一个稳定、快速、安全的运行环境。

**agentsphere-mcp-server** 是用于给 AI 连接和操作 agent-sphere 沙箱的 MCP Server。

**官网**: https://www.agentsphere.run/home



## MCP 工具说明

本 MCP Server 提供以下 4 个工具供 AI 使用：

### 1. exec_command
**功能**: 在 sandbox 中执行 Linux 系统命令

**参数**:
- `cmd` (string): 要执行的命令

**返回值**: 包含 stdout、stderr 和 success 字段的执行结果


### 2. get_preview_link
**功能**: 获取 sandbox 中 web 服务的访问 URL

**参数**:
- `port` (int): 端口号

**返回值**: 包含可访问 URL 的结果


### 3. upload_files_to_sandbox
**功能**: 将用户本地文件或文件夹上传到沙箱中的指定目录

**参数**:
- `local_path` (string): 本地文件或文件夹的绝对路径
- `target_path` (string, 可选): 沙箱中的目标目录路径，默认为 `/user_uploaded_files/`

**返回值**: 包含成功上传的文件列表或错误信息的结果


### 4. find_file_path
**功能**: 根据名称搜索文件或目录的绝对路径

**参数**:
- `filename` (string): 要搜索的文件名（支持通配符，如 *.py, project* 等）
- `search_path` (string, 可选): 搜索起始路径或快捷选项
  - 具体路径：如 "/Users/username/Desktop/Projects"
  - 快捷选项："desktop"（默认）、"documents"、"downloads"、"home"

**返回值**: 包含找到的文件/目录列表的搜索结果，每个结果包含完整路径、类型、大小、修改时间等信息


## 使用方法

### MCP Server 配置

在 Efflux, Cursor 或其他 MCP 客户端中配置此服务器，请将以下配置添加到您的 MCP 配置文件中：

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

**注意**：
- 将 `your_api_key_here` 替换为您的 AgentSphere API 密钥
- uv 已安装（uv, 一个目前主流的 python 依赖和项目管理器: https://docs.astral.sh/uv/getting-started/installation/）
- 确保网络畅通，大陆用户建议开启全局代理以确保正常使用


