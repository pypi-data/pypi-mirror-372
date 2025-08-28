# ASI1 MCP CLI Configuration

This document describes the configuration format for the ASI1 MCP CLI.

## Configuration File Locations
The configuration file can be placed in one of the following locations:
- `~/.asi1/config.json`
- `$PWD/asi1-mcp-server-config.json`

The CLI will use the first configuration file found in the above order.

## Configuration Format
The configuration is a JSON file with the following structure:

```json
{
  "systemPrompt": "string",
  "llm": {
    "provider": "asi-one",
    "model": "asi1-mini",
    "api_key": "string",
    "temperature": number,
    "base_url": "string"
  },
  "mcpServers": {
    "server_name": {
      "command": "string",
      "args": ["string"],
      "env": {"key": "value"},
      "enabled": boolean,
      "exclude_tools": ["string"],
      "requires_confirmation": ["string"]
    }
  }
}