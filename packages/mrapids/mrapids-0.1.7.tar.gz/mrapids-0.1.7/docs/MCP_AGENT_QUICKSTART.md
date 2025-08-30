# MCP Agent Quick Setup Guide

## Installation

> ⚠️ **Current Status**: `mrapids-agent` is in development and not yet published to crates.io.

### Build from Source (Current Method)
```bash
# Clone and build
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime
git checkout Agentic_features
cd agent
cargo build --release

# Add to PATH or copy binary
sudo cp target/release/mrapids-agent /usr/local/bin/
```

### Future Installation (When Published)
```bash
# Install from crates.io (coming soon)
cargo install mrapids-agent

# Or download pre-built binary (coming soon)
curl -L https://github.com/deepwissen/api-runtime/releases/latest/download/mrapids-agent -o /usr/local/bin/mrapids-agent
chmod +x /usr/local/bin/mrapids-agent
```

See [Build Guide](./MCP_AGENT_BUILD_GUIDE.md) for detailed build instructions.

## Quick Start (3 Steps)

### 1. Initialize MCP Agent

```bash
# Create agent configuration in current directory
mrapids-agent init

# This creates:
# .mrapids/
#   ├── mcp-server.toml    # Server configuration
#   ├── policy.yaml        # Default safe policy
#   ├── api.yaml          # Your API spec (example)
#   └── auth/             # Auth profiles directory
```

### 2. Add Your API Spec

```bash
# Option 1: Use existing OpenAPI spec
cp your-api.yaml .mrapids/api.yaml

# Option 2: Download from URL
mrapids-agent init --from-url https://api.example.com/openapi.yaml

# Option 3: Use example API
mrapids-agent init --example github
```

### 3. Start the Agent Server

```bash
# Start with defaults (port 8080)
mrapids-agent start

# Or specify port
mrapids-agent start --port 3000

# Or with custom config
mrapids-agent start --config my-config.toml
```

## Testing the Agent

### Quick Test
```bash
# In another terminal, test the agent
mrapids-agent test

# Or test specific operation
mrapids-agent test --operation listUsers
```

### Manual Test
```bash
# Health check
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"health","params":{},"id":1}'

# List operations
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## Configuration

### Basic Setup (Auto-generated)
```toml
# .mrapids/mcp-server.toml
[server]
host = "127.0.0.1"
port = 8080

[defaults]
spec_path = "api.yaml"
policy_file = "policy.yaml"
```

### Add Authentication
```bash
# Create auth profile
mrapids-agent auth add github --type bearer

# You'll be prompted:
# Enter token environment variable name: GITHUB_TOKEN

# Then set the environment variable
export GITHUB_TOKEN="your-token-here"
```

### Customize Policy
```yaml
# .mrapids/policy.yaml
version: "1.0"
rules:
  # Allow all GET requests (safe default)
  - name: "allow-reads"
    pattern: "*"
    allow:
      methods: ["GET"]
  
  # Add your custom rules here
  - name: "allow-create-comments"
    pattern: "*/comments"
    allow:
      methods: ["POST"]
```

## Common Commands

```bash
# Initialize agent setup
mrapids-agent init

# Start the server
mrapids-agent start

# Run in background
mrapids-agent start --daemon

# Stop daemon
mrapids-agent stop

# Check status
mrapids-agent status

# View logs
mrapids-agent logs

# Test connection
mrapids-agent test

# Manage auth profiles
mrapids-agent auth list
mrapids-agent auth add <name> --type bearer
mrapids-agent auth remove <name>

# Validate configuration
mrapids-agent validate
```

## Examples

### GitHub API Agent
```bash
# Quick setup for GitHub API
mrapids-agent init --example github
export GITHUB_TOKEN="your-github-token"
mrapids-agent start

# Test it
mrapids-agent test --operation getAuthenticatedUser
```

### Custom API Agent
```bash
# Initialize with your API
mrapids-agent init --from-url https://api.mycompany.com/openapi.yaml

# Add authentication
mrapids-agent auth add prod --type api_key
export PROD_API_KEY="your-api-key"

# Start agent
mrapids-agent start
```

### Development Mode
```bash
# Start with verbose logging and hot reload
mrapids-agent start --dev

# This enables:
# - Debug logging
# - Auto-reload on config changes
# - Detailed error messages
```

## Integration

### With Claude Desktop
```json
{
  "mcpServers": {
    "my-api": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8080"]
    }
  }
}
```

### With Python Script
```python
import subprocess
import time

# Start agent
process = subprocess.Popen(['mrapids-agent', 'start'])
time.sleep(2)  # Wait for startup

# Your agent is now running on localhost:8080
# ... use the agent ...

# Stop when done
process.terminate()
```

## Troubleshooting

```bash
# Check if agent is running
mrapids-agent status

# View recent logs
mrapids-agent logs --tail 50

# Test specific operation
mrapids-agent test --operation getUser --params '{"id":"123"}'

# Validate setup
mrapids-agent validate

# Debug mode
mrapids-agent start --debug
```

## Next Steps

1. **Customize Policy**: Edit `.mrapids/policy.yaml` for your security needs
2. **Add Auth**: Set up authentication profiles for your APIs
3. **Monitor Logs**: Check `.mrapids/audit/` for agent activity
4. **Integrate**: Connect your AI agents to `http://localhost:8080`

---

**Note**: This assumes `mrapids-agent` will be distributed as a standalone binary through cargo or GitHub releases, similar to how `mrapids` CLI works.