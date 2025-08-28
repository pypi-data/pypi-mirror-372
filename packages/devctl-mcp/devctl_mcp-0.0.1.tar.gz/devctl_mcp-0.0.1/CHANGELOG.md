# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial DevCtl MCP server implementation
- Process management functionality with start/stop/logs/list operations
- YAML configuration support for defining development processes
- ProcessManager class for handling process lifecycle and logging
- Automatic cleanup and graceful shutdown handling
- MCP tools for process management:
  - `start_process` - Start a named development process
  - `stop_process` - Stop a running process with optional force kill
  - `get_process_logs` - Retrieve process logs with configurable line limits
  - `list_processes` - List all processes and their status
- Example `processes.yaml` configuration with common development scenarios
- GitHub Actions workflow for automated PyPI releases on tags
- Comprehensive README.md with usage examples and setup instructions
- Project documentation and contributing guidelines

### Changed
- Updated project structure to follow MCP server best practices
- Enhanced error handling and logging throughout the application

### Dependencies
- Added `pyyaml>=6.0` for YAML configuration support
- Updated `mcp>=1.0.0` for Model Context Protocol compatibility

## [0.1.0] - TBD

Initial release with core process management functionality.