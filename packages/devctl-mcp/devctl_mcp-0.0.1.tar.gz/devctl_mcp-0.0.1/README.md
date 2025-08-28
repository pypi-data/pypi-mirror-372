# DevCtl MCP

A Model Context Protocol (MCP) server for managing development processes. Start, stop, and monitor your development servers, background tasks, and other processes directly through Claude or other MCP-compatible clients.

## Features

- 🚀 **Start/Stop Processes**: Launch and terminate development processes by name
- 📊 **Process Monitoring**: View real-time status and uptime for all processes
- 📝 **Log Management**: Retrieve and view process logs with configurable line limits
- ⚙️ **YAML Configuration**: Define processes with commands, arguments, working directories, and environment variables
- 🔄 **Automatic Cleanup**: Graceful shutdown of all processes when the server terminates
- 🛡️ **Process Groups**: Proper signal handling for clean process termination

## Installation

```bash
pip install devctl-mcp
```

## Configuration

Create a `processes.yaml` file in your project root to define your development processes:

```yaml
processes:
  # Example Go API server
  go_api:
    cmd: go
    args:
      - run
      - ./cmd/server
    working_directory: ~/projects/my-api
    env:
      PORT: "8080"
      GO_ENV: "development"
  
  # Example Python web server
  web_server:
    cmd: python
    args:
      - -m
      - flask
      - run
    working_directory: /path/to/your/flask/project
    env:
      FLASK_APP: app.py
      FLASK_ENV: development
      FLASK_DEBUG: "1"
  
  # Example Node.js development server
  frontend:
    cmd: npm
    args:
      - run
      - dev
    working_directory: /path/to/your/frontend
    env:
      NODE_ENV: development
```

## MCP Client Setup

### Claude Desktop

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "devctl": {
      "command": "devctl-mcp"
    }
  }
}
```

### Other MCP Clients

The server runs via stdio transport and can be used with any MCP-compatible client:

```bash
devctl-mcp
```

## Available Tools

The MCP server provides the following tools:

### `start_process`
Start a named development process.

**Parameters:**
- `name` (required): The name of the process to start

### `stop_process`
Stop a running process.

**Parameters:**
- `name` (required): The name of the process to stop
- `force` (optional): Force kill the process (default: false)

### `get_process_logs`
Retrieve logs from a process.

**Parameters:**
- `name` (required): The name of the process
- `lines` (optional): Number of recent log lines to retrieve

### `list_processes`
List all defined processes and their current status.

**Parameters:** None

## Usage Examples

Once configured, you can interact with your processes through Claude:

```
"Start my web server"
"Stop the API server"
"Show me the logs for the frontend process"
"List all my development processes"
"Restart the database with force kill"
```

## Process Configuration Reference

Each process in `processes.yaml` supports:

- **`cmd`** (required): The command to execute
- **`args`** (optional): List of command arguments
- **`working_directory`** (optional): Working directory for the process
- **`env`** (optional): Environment variables as key-value pairs

## Development

### Setup

```bash
git clone https://github.com/opentrace/devctl-mcp.git
cd devctl-mcp
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Building

```bash
python -m build
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.