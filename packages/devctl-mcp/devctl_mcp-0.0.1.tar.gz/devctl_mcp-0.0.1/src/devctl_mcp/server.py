#!/usr/bin/env python3
"""
DevCtl MCP Server - Process Management for Development

This MCP server provides process management capabilities:
- Start/stop development processes
- Retrieve process logs
- List process status
- Automatic cleanup on session end
"""

import asyncio
import atexit
import logging
import signal
from typing import Any

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from ._version import version
from .process_manager import ProcessManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("devctl-mcp")

# Create the server instance and process manager
server = Server("devctl-mcp")
process_manager = ProcessManager()


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="start_process",
            description="Start a named development process",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the process to start",
                    }
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="stop_process",
            description="Stop a running process",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the process to stop",
                    },
                    "force": {
                        "type": "boolean",
                        "description": "Force kill the process (default: false)",
                        "default": False,
                    }
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="get_process_logs",
            description="Get logs from a process",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the process",
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Number of recent log lines to retrieve (default: all)",
                        "minimum": 1,
                    }
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="list_processes",
            description="List all processes and their status",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls."""
    if name == "start_process":
        if not arguments or "name" not in arguments:
            raise ValueError("Missing required argument: name")

        process_name = arguments["name"]
        success, message = await process_manager.start_process(process_name)
        
        return [
            types.TextContent(
                type="text",
                text=message,
            )
        ]

    elif name == "stop_process":
        if not arguments or "name" not in arguments:
            raise ValueError("Missing required argument: name")

        process_name = arguments["name"]
        force = arguments.get("force", False)
        success, message = await process_manager.stop_process(process_name, force)
        
        return [
            types.TextContent(
                type="text",
                text=message,
            )
        ]

    elif name == "get_process_logs":
        if not arguments or "name" not in arguments:
            raise ValueError("Missing required argument: name")

        process_name = arguments["name"]
        lines = arguments.get("lines")
        success, message, log_lines = await process_manager.get_process_logs(process_name, lines)
        
        if not success:
            return [types.TextContent(type="text", text=message)]
            
        log_text = "\n".join(log_lines) if log_lines else "No logs available"
        return [
            types.TextContent(
                type="text", 
                text=f"{message}\n\n{log_text}",
            )
        ]

    elif name == "list_processes":
        processes = process_manager.list_processes()
        
        if not processes:
            return [types.TextContent(type="text", text="No processes defined")]
            
        lines = ["Process Status:"]
        for proc in processes:
            status_line = f"• {proc['name']}: {proc['status']}"
            if proc['pid']:
                status_line += f" (PID: {proc['pid']})"
            if proc['uptime']:
                uptime_str = f"{proc['uptime']:.1f}s"
                status_line += f" - Uptime: {uptime_str}"
            status_line += f" - Command: {proc['cmd']} {' '.join(proc['args'])}"
            lines.append(status_line)
            
        return [
            types.TextContent(
                type="text",
                text="\n".join(lines),
            )
        ]

    else:
        raise ValueError(f"Unknown tool: {name}")


async def run():
    """Run the MCP server."""
    # Initialize process manager
    await process_manager.initialize()
    
    # Set up cleanup on server shutdown
    def cleanup():
        asyncio.create_task(process_manager.shutdown())
    
    try:
        # Run the server using stdio transport
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="devctl-mcp",
                    server_version=version,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    finally:
        # Ensure cleanup happens when server shuts down
        await process_manager.shutdown()


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
