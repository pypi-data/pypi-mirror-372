# Stash MCP Server

[![PyPI version](https://badge.fury.io/py/stash-mcp.svg)](https://badge.fury.io/py/stash-mcp)
[![Python versions](https://img.shields.io/pypi/pyversions/stash-mcp.svg)](https://pypi.org/project/stash-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Model Context Protocol (MCP) server for Stash issue analysis. This server enables AI assistants to interact with your Stash instance to analyze issues, find similar content, and identify subject matter experts.

## Features

- **Issue Analysis**: Get detailed analysis for specific issues including similar content discovery
- **Task Management**: List and manage tasks assigned to the authenticated user
- **Secure Authentication**: Uses MCP tokens for secure API access

## Configuration

The server requires the following environment variables:

- `STASH_API_BASE`: Base URL for your Stash API
- `STASH_MCP_TOKEN`: Your Stash MCP authentication token

You can get these environment variables from your [Stash account](https://usestash.com).

### With Copilot, Cursor, or Claude Code

Add this to your IDE MCP configuration file:

```json
{
  "mcpServers": {
    "stash": {
      "command": "uvx",
      "args": ["stash-mcp"],
      "env": {
        "STASH_API_BASE": "stash-api-base-url",
        "STASH_MCP_TOKEN": "your-mcp-token-here"
      }
    }
  }
}
```

### Available Tools

#### `list_my_tasks`

Lists all tasks assigned to the authenticated user, grouped by categories.

#### `get_issue_analysis`

Get detailed analysis for a specific issue including:

- Similar issues
- Related documents
- Relevant code files
- Subject matter experts

## Requirements

- Python 3.10 or higher
- Valid [Stash account](https://usestash.com) with MCP access
- Network access to your Stash instance

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions, See [Stash Documentation](https://docs.usestash.com/mcp/stash-mcp).
