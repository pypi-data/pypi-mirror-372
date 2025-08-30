# MCP Integration User Guide

## Overview

MicroRapid's MCP (Model Context Protocol) integration enables AI agents to safely execute API operations through a secure, policy-controlled interface. This guide explains the features and how to use them.

## What is MCP?

MCP is a standard protocol that allows AI agents (like Claude, GPT, etc.) to interact with external tools and APIs in a controlled manner. MicroRapid implements an MCP server that acts as a secure gateway between AI agents and your APIs.

## Key Features for Agents

### 1. **Safe API Execution**
- Agents can execute API operations without direct access to credentials
- All operations go through policy enforcement
- Automatic validation of inputs and outputs

### 2. **Policy-Based Access Control**
- Define what operations agents can perform
- Set conditions based on method, path, time, etc.
- Deny access to sensitive endpoints
- Require authentication for specific operations

### 3. **Comprehensive Audit Logging**
- Every agent action is logged with unique IDs
- Track what operations were attempted/executed
- Monitor policy decisions (allow/deny)
- Automatic log rotation and compression

### 4. **Response Redaction**
- Automatic removal of sensitive data from responses
- Redacts: API keys, tokens, passwords, credit cards
- Configurable redaction patterns
- Agents never see actual secrets

### 5. **Auth Profile Management**
- Store credentials securely with environment variables
- Agents reference profiles by name, not actual credentials
- Support for Bearer, Basic, and API Key authentication

## How to Use MCP Integration

### Step 1: Install and Build

```bash
# Clone the repository
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime

# Build the MCP server
cd agent
cargo build --release
```

### Step 2: Configure the Server

Create a configuration file `mcp-server.toml`:

```toml
[server]
host = "127.0.0.1"
port = 8080

[defaults]
spec_path = ".mrapids/api.yaml"
policy_file = ".mrapids/policy.yaml"
env = "production"
auth_profile = "default"

[security]
allow_override_env = false
allow_override_auth = false
redact_patterns = ["password", "secret", "token", "key"]

[audit]
enabled = true
directory = ".mrapids/audit"
level = "detailed"
rotation_size_mb = 100
rotation_time = "daily"
max_files = 30
compress = true
```

### Step 3: Define Access Policies

Create `.mrapids/policy.yaml`:

```yaml
version: "1.0"
metadata:
  name: "agent-policy"
  description: "Policy for AI agent access"

defaults:
  allow_methods: ["GET", "POST"]
  deny_external_refs: true
  require_auth: true
  audit_level: "detailed"

rules:
  # Allow read operations on all endpoints
  - name: "allow-reads"
    pattern: "*"
    allow:
      methods: ["GET"]
      operations: ["list*", "get*", "search*"]
    
  # Deny access to admin endpoints
  - name: "deny-admin"
    pattern: "*/admin/*"
    deny:
      reason: "Admin endpoints are restricted"
  
  # Allow specific write operations
  - name: "allow-safe-writes"
    pattern: "*/comments"
    allow:
      methods: ["POST"]
      conditions:
        - type: "time_window"
          start: "09:00"
          end: "17:00"
```

### Step 4: Set Up Authentication

Create auth profiles in `.mrapids/auth/`:

```toml
# .mrapids/auth/github.toml
[profile]
name = "github"
type = "bearer"
token_env = "GITHUB_TOKEN"
```

```toml
# .mrapids/auth/api-server.toml
[profile]
name = "api-server"
type = "api_key"
header = "X-API-Key"
key_env = "API_SERVER_KEY"
```

Set environment variables:
```bash
export GITHUB_TOKEN="your-github-token"
export API_SERVER_KEY="your-api-key"
```

### Step 5: Add Your API Specification

Place your OpenAPI spec in `.mrapids/api.yaml`:

```yaml
openapi: "3.0.0"
info:
  title: "My API"
  version: "1.0.0"
servers:
  - url: https://api.example.com
paths:
  /users:
    get:
      operationId: listUsers
      summary: List all users
  /users/{id}:
    get:
      operationId: getUser
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
```

### Step 6: Start the MCP Server

```bash
./target/release/mrapids-agent --config mcp-server.toml --config-dir .mrapids
```

Server will start on `http://localhost:8080`

### Step 7: Use with AI Agents

#### Available Tools

The MCP server exposes three main tools via JSON-RPC:

1. **List Operations**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {
    "filter": {
      "method": "GET",
      "tag": "users",
      "pattern": "search"
    }
  },
  "id": 1
}
```

2. **Show Operation Details**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/show",
  "params": {
    "operation_id": "getUser"
  },
  "id": 2
}
```

3. **Run Operation**
```json
{
  "jsonrpc": "2.0",
  "method": "tools/run",
  "params": {
    "operation_id": "getUser",
    "parameters": {
      "id": "123"
    },
    "auth_profile": "github"
  },
  "id": 3
}
```

## Example: AI Agent Workflow

### 1. Agent Discovers Available Operations

```python
# Agent asks: "What user operations are available?"
response = mcp_client.call("tools/list", {
    "filter": {"pattern": "user"}
})
# Returns: listUsers, getUser, createUser, updateUser, deleteUser
```

### 2. Agent Gets Operation Details

```python
# Agent asks: "How do I get a specific user?"
response = mcp_client.call("tools/show", {
    "operation_id": "getUser"
})
# Returns: Parameters needed, response schema, etc.
```

### 3. Agent Executes Operation

```python
# Agent executes: "Get user with ID 123"
response = mcp_client.call("tools/run", {
    "operation_id": "getUser",
    "parameters": {"id": "123"}
})
# Returns: User data (with sensitive fields redacted)
```

## Security Features in Action

### Policy Enforcement Example

If an agent tries to access a restricted endpoint:

```python
# Agent tries: "Delete all users"
response = mcp_client.call("tools/run", {
    "operation_id": "deleteAllUsers"
})

# Response:
{
  "error": {
    "code": 1001,
    "message": "Admin endpoints are restricted",
    "data": {
      "rule": "deny-admin",
      "operation": "deleteAllUsers"
    }
  }
}
```

### Response Redaction Example

When sensitive data is returned:

```python
# Original API response:
{
  "user": {
    "id": "123",
    "name": "John Doe",
    "api_key": "sk-1234567890abcdef",
    "password_hash": "$2b$10$...",
    "email": "john@example.com"
  }
}

# Redacted response to agent:
{
  "user": {
    "id": "123",
    "name": "John Doe",
    "api_key": "[REDACTED:API_KEY]",
    "password_hash": "[REDACTED:PASSWORD]",
    "email": "john@example.com"
  }
}
```

### Audit Log Example

Every operation creates an audit entry:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-20T10:30:00Z",
  "agent_id": "mcp-agent",
  "operation": {
    "operation_id": "getUser",
    "method": "GET",
    "url": "https://api.example.com/users/123",
    "auth_profile": "github",
    "parameters": {"id": "123"}
  },
  "policy": {
    "decision": "allow",
    "rule": "allow-reads"
  },
  "response": {
    "status": "success",
    "status_code": 200,
    "duration_ms": 145
  }
}
```

## Integration with AI Frameworks

### Claude Desktop (via MCP)

1. Add to Claude's config:
```json
{
  "mcpServers": {
    "mrapids": {
      "command": "mrapids-agent",
      "args": ["--config", "mcp-server.toml"]
    }
  }
}
```

2. Claude can then use commands like:
- "List all available API operations"
- "Show me how to create a user"
- "Get the user with ID 123"

### Custom AI Integration

```python
import openai
import requests

class MRapidsAgent:
    def __init__(self, mcp_url="http://localhost:8080"):
        self.mcp_url = mcp_url
        
    def execute_operation(self, operation_id, params=None):
        response = requests.post(self.mcp_url, json={
            "jsonrpc": "2.0",
            "method": "tools/run",
            "params": {
                "operation_id": operation_id,
                "parameters": params or {}
            },
            "id": 1
        })
        return response.json()
    
# Use with OpenAI
agent = MRapidsAgent()
result = agent.execute_operation("getUser", {"id": "123"})
```

## Best Practices

### 1. **Principle of Least Privilege**
- Only allow operations that agents actually need
- Use specific patterns, not wildcards
- Deny by default, allow by exception

### 2. **Monitor Audit Logs**
- Regularly review agent activities
- Set up alerts for denied operations
- Track usage patterns

### 3. **Test Policies**
- Use the policy test framework
- Verify both allows and denies work correctly
- Test edge cases and time conditions

### 4. **Secure Credentials**
- Never expose actual credentials to agents
- Use environment variables for secrets
- Rotate credentials regularly

### 5. **Response Safety**
- Configure redaction patterns for your API
- Test that sensitive data is properly redacted
- Consider what agents should/shouldn't see

## Troubleshooting

### Agent Can't Connect
```bash
# Check server is running
curl http://localhost:8080 -d '{"jsonrpc":"2.0","method":"health","id":1}'

# Check logs
tail -f .mrapids/audit/mcp-audit-current.log
```

### Operation Denied
- Check audit logs for the denial reason
- Review policy rules with `mrapids validate-policy`
- Ensure time conditions are met

### Missing Auth
- Verify environment variables are set
- Check auth profile exists in `.mrapids/auth/`
- Ensure profile name matches in request

## Summary

MicroRapid's MCP integration provides:
- **Safe API access** for AI agents
- **Policy-based control** over operations
- **Complete audit trail** of all activities
- **Automatic security** through redaction
- **Simple integration** via JSON-RPC

This enables AI agents to interact with your APIs while maintaining security, compliance, and control over what they can access and execute.