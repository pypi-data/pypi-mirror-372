# Integrating MCP Agent with Claude

This guide shows how to connect your `mrapids-agent` with Claude Desktop and other AI assistants.

## Prerequisites

1. Install `mrapids-agent`:
```bash
# Future: via cargo
cargo install mrapids-agent

# Or download binary
curl -L https://github.com/deepwissen/api-runtime/releases/latest/download/mrapids-agent -o /usr/local/bin/mrapids-agent
chmod +x /usr/local/bin/mrapids-agent
```

2. Set up your agent:
```bash
# Initialize configuration
mrapids-agent init

# Add your API spec
cp your-api.yaml .mrapids/api.yaml

# Start the agent
mrapids-agent start
```

## Claude Desktop Integration

### Step 1: Locate Claude's Configuration

Claude Desktop stores its configuration in:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Step 2: Configure MCP Server

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mrapids": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8080"],
      "env": {
        "GITHUB_TOKEN": "your-github-token",
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### Step 3: Multiple API Configuration

For multiple APIs, create separate configurations:

```json
{
  "mcpServers": {
    "github-api": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8080", "--config-dir", "~/.mrapids-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxx"
      }
    },
    "stripe-api": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8081", "--config-dir", "~/.mrapids-stripe"],
      "env": {
        "STRIPE_API_KEY": "sk_test_xxxxxxxxxxxx"
      }
    },
    "internal-api": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8082", "--config-dir", "~/.mrapids-internal"],
      "env": {
        "INTERNAL_API_KEY": "xxxxxxxxxxxx"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

After updating the configuration:
1. Quit Claude Desktop completely
2. Start Claude Desktop again
3. The MCP servers will start automatically

### Step 5: Using in Claude

Once configured, you can use natural language commands:

```
You: "List all my GitHub repositories"
Claude: I'll search for your GitHub repositories using the GitHub API.
[Uses mrapids-agent to execute the searchRepositories operation]

You: "Show me the issues in anthropics/anthropic-sdk-python"
Claude: I'll get the issues for that repository.
[Uses mrapids-agent to execute the listIssues operation]

You: "What's my Stripe account balance?"
Claude: I'll check your Stripe account balance.
[Uses mrapids-agent to execute the getBalance operation]
```

## How It Works

### 1. Claude Starts MCP Servers
When Claude Desktop starts, it:
- Reads the MCP configuration
- Starts each configured `mrapids-agent` process
- Establishes JSON-RPC connections

### 2. Claude Discovers Tools
Claude queries each MCP server:
```json
// Claude sends:
{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}

// mrapids-agent responds:
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "listRepositories",
        "description": "Search GitHub repositories",
        "parameters": {...}
      },
      // ... more operations
    ]
  },
  "id": 1
}
```

### 3. Claude Executes Operations
When you ask Claude to do something:
```json
// Claude sends:
{
  "jsonrpc": "2.0",
  "method": "tools/run",
  "params": {
    "operation_id": "searchRepositories",
    "parameters": {
      "q": "user:anthropics",
      "sort": "stars"
    }
  },
  "id": 2
}

// mrapids-agent responds with results
```

## Advanced Configuration

### Custom Policies per API

Create different policies for different APIs:

```bash
# GitHub - more permissive
cat > ~/.mrapids-github/policy.yaml << EOF
version: "1.0"
rules:
  - name: "allow-github-reads"
    pattern: "*"
    allow:
      methods: ["GET", "POST"]
      operations: ["*"]
EOF

# Stripe - read-only
cat > ~/.mrapids-stripe/policy.yaml << EOF
version: "1.0"
rules:
  - name: "stripe-readonly"
    pattern: "*"
    allow:
      methods: ["GET"]
    deny:
      methods: ["POST", "PUT", "DELETE"]
      reason: "Only read operations allowed for Stripe"
EOF
```

### Environment-Specific Configurations

Use different configurations for different environments:

```json
{
  "mcpServers": {
    "api-dev": {
      "command": "mrapids-agent",
      "args": ["start", "--config", "~/.mrapids/dev-config.toml"],
      "env": {
        "API_ENV": "development",
        "API_KEY": "dev-key"
      }
    },
    "api-prod": {
      "command": "mrapids-agent",
      "args": ["start", "--config", "~/.mrapids/prod-config.toml"],
      "env": {
        "API_ENV": "production",
        "API_KEY": "prod-key"
      }
    }
  }
}
```

### Debugging Integration

Enable debug logging to troubleshoot:

```json
{
  "mcpServers": {
    "mrapids-debug": {
      "command": "mrapids-agent",
      "args": ["start", "--debug", "--port", "8080"],
      "env": {
        "RUST_LOG": "debug"
      }
    }
  }
}
```

View logs:
```bash
# Check agent logs
mrapids-agent logs --tail 50

# Check Claude's console (Developer Tools)
# macOS: View > Developer > Developer Tools
```

## Other AI Integration Examples

### OpenAI GPTs

Create a custom GPT with action:

```yaml
openapi: "3.1.0"
info:
  title: MCP Agent Bridge
  version: "1.0.0"
servers:
  - url: http://localhost:8080
paths:
  /tools/list:
    post:
      operationId: listTools
      requestBody:
        content:
          application/json:
            schema:
              type: object
  /tools/run:
    post:
      operationId: runTool
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                operation_id:
                  type: string
                parameters:
                  type: object
```

### LangChain Integration

```python
from langchain.tools import Tool
from langchain.agents import initialize_agent
import requests

class MRapidsTools:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
    
    def list_operations(self, query=""):
        response = requests.post(f"{self.base_url}/tools/list", json={
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {"filter": {"pattern": query}},
            "id": 1
        })
        return response.json()
    
    def run_operation(self, operation_id, params=None):
        response = requests.post(f"{self.base_url}/tools/run", json={
            "jsonrpc": "2.0",
            "method": "tools/run",
            "params": {
                "operation_id": operation_id,
                "parameters": params or {}
            },
            "id": 1
        })
        return response.json()

# Create tools
mrapids = MRapidsTools()
tools = [
    Tool(
        name="list_api_operations",
        func=lambda q: mrapids.list_operations(q),
        description="List available API operations"
    ),
    Tool(
        name="execute_api_operation",
        func=lambda op: mrapids.run_operation(op),
        description="Execute an API operation"
    )
]

# Initialize agent
agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
```

### Copilot Integration

For GitHub Copilot or similar:

```typescript
// .copilot/mrapids-context.ts
import { exec } from 'child_process';

export class MRapidsContext {
  async getAPIOperations(): Promise<any> {
    return new Promise((resolve, reject) => {
      exec('mrapids-agent test --operation list', (error, stdout) => {
        if (error) reject(error);
        else resolve(JSON.parse(stdout));
      });
    });
  }
  
  async executeOperation(operationId: string, params: any): Promise<any> {
    const cmd = `mrapids-agent test --operation ${operationId} --params '${JSON.stringify(params)}'`;
    return new Promise((resolve, reject) => {
      exec(cmd, (error, stdout) => {
        if (error) reject(error);
        else resolve(JSON.parse(stdout));
      });
    });
  }
}
```

## Best Practices

### 1. Security
- Use separate auth profiles for each API
- Never commit tokens to configuration files
- Use environment variables for secrets
- Implement strict policies for production APIs

### 2. Performance
- Run agents on different ports for multiple APIs
- Use connection pooling in the agent configuration
- Enable caching for read-heavy operations

### 3. Monitoring
- Check audit logs regularly: `ls ~/.mrapids/audit/`
- Set up alerts for policy violations
- Monitor agent resource usage

### 4. Testing
Before giving Claude access:
```bash
# Test the agent manually
mrapids-agent test --operation listUsers

# Verify policies work
mrapids-agent test --operation deleteUser --params '{"id":"123"}'
# Should be denied by policy
```

## Troubleshooting

### Claude Can't Connect
1. Check agent is running: `mrapids-agent status`
2. Verify port is correct in configuration
3. Check firewall settings
4. Look for errors in: `mrapids-agent logs`

### Operations Not Showing
1. Verify API spec is loaded: `mrapids-agent validate`
2. Check for spec parsing errors
3. Ensure operations have unique IDs

### Authentication Failures
1. Verify environment variables are set
2. Check auth profile configuration
3. Test with curl first
4. Review audit logs for details

### Policy Denials
1. Check policy rules: `cat ~/.mrapids/policy.yaml`
2. Review audit logs for denial reasons
3. Test with more permissive policy
4. Add specific allow rules as needed

## Summary

The integration allows Claude to:
- Discover available API operations automatically
- Execute operations safely through policy control
- Work with multiple APIs simultaneously
- Maintain security through auth profiles
- Provide audit trails of all actions

This creates a powerful combination where Claude's language understanding meets your API capabilities through a secure, controlled interface.