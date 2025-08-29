# Demo Hello MCP Server Documentation

## Overview

A simple demonstration MCP server that provides greeting tools

## Quick Start

Deploy this template:

```bash
mcpp deploy demo
```

## Configuration Options

| Property | Type | Environment Variable | Default | Description |
|----------|------|---------------------|---------|-------------|
| `hello_from` | string | `MCP_HELLO_FROM` | `MCP Platform` | Name or message to include in greetings |
| `log_level` | string | `MCP_LOG_LEVEL` | `info` | Logging level for the server |

### Usage Examples

```bash
# Deploy with configuration
mcpp deploy demo --show-config

# Using environment variables
mcpp deploy demo --env MCP_HELLO_FROM=value

# Using CLI configuration
mcpp deploy {template_id} --config {first_prop}=value

# Using nested configuration
mcpp deploy {template_id} --config category__property=value
```## Development

### Local Testing

```bash
cd templates/demo
pytest tests/
```

## Support

For support, please open an issue in the main repository.
