# MCP Integration Testing Guide

## Prerequisites

1. Build the project:
```bash
cd /Users/neetagundala/Projects/microrapid_runtime/api-runtime
cargo build --release
```

2. Build the MCP server:
```bash
cd agent
cargo build --release
```

## 1. Testing the MCP Server

### Start the Server

```bash
# Generate example configuration
./target/release/mrapids-agent --generate-config > test-mcp-server.toml

# Create test directory structure
mkdir -p test-mcp
cd test-mcp
mkdir -p .mrapids/auth

# Start the server with example config
../target/release/mrapids-agent --config ../test-mcp-server.toml --config-dir .mrapids
```

The server will create example files in `.mrapids/` including:
- `policy.yaml` - Default safety policy
- `auth/` - Example auth profiles
- `api.yaml` - Example OpenAPI spec

### Test JSON-RPC Endpoints

1. **Health Check**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "health",
    "params": {},
    "id": 1
  }'
```

Expected response:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "healthy",
    "version": "0.1.0",
    "service": "mrapids-agent"
  },
  "id": 1
}
```

2. **List Operations**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {
      "filter": {
        "method": "GET"
      }
    },
    "id": 2
  }'
```

3. **Show Operation Details**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/show",
    "params": {
      "operation_id": "health"
    },
    "id": 3
  }'
```

## 2. Testing with Real APIs

### Setup GitHub API Example

1. Create a GitHub API spec:
```bash
cat > .mrapids/github-api.yaml << 'EOF'
openapi: "3.0.0"
info:
  title: GitHub API
  version: "1.0.0"
servers:
  - url: https://api.github.com
paths:
  /user:
    get:
      operationId: getAuthenticatedUser
      summary: Get the authenticated user
      security:
        - bearerAuth: []
      responses:
        200:
          description: User details
  /users/{username}:
    get:
      operationId: getUser
      summary: Get a user by username
      parameters:
        - name: username
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: User details
  /repos/{owner}/{repo}:
    get:
      operationId: getRepository
      summary: Get repository information
      parameters:
        - name: owner
          in: path
          required: true
          schema:
            type: string
        - name: repo
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: Repository details
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
EOF
```

2. Create auth profile for GitHub:
```bash
cat > .mrapids/auth/github.toml << 'EOF'
[profile]
name = "github"
type = "bearer"
token_env = "GITHUB_TOKEN"
EOF
```

3. Update server config to use GitHub API:
```toml
# In test-mcp-server.toml, update:
[defaults]
spec_path = ".mrapids/github-api.yaml"
auth_profile = "github"
```

4. Set GitHub token (read-only):
```bash
export GITHUB_TOKEN="your-github-token"
```

5. Test GitHub API operations:
```bash
# List GitHub operations
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 4
  }'

# Get repository info
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/run",
    "params": {
      "operation_id": "getRepository",
      "parameters": {
        "owner": "anthropics",
        "repo": "anthropic-sdk-python"
      }
    },
    "id": 5
  }'
```

## 3. Testing Policy Engine

### Create Test Policy

```bash
cat > .mrapids/test-policy.yaml << 'EOF'
version: "1.0"
metadata:
  name: "test-policy"
  description: "Policy for testing"

defaults:
  allow_methods: ["GET"]
  deny_external_refs: true
  require_auth: false
  audit_level: "detailed"

rules:
  - name: "allow-public-reads"
    description: "Allow read operations on public endpoints"
    pattern: "*/users/*"
    allow:
      methods: ["GET"]
      
  - name: "deny-private-endpoints"
    description: "Deny access to private endpoints"
    pattern: "*/admin/*"
    deny:
      reason: "Admin endpoints are not accessible to agents"
      
  - name: "require-auth-for-user"
    description: "Require auth for authenticated user endpoint"
    pattern: "*/user"
    conditions:
      - type: "has_auth"
        value: "true"
    allow:
      methods: ["GET"]
EOF
```

Update server to use test policy and restart.

### Test Policy Enforcement

1. **Test allowed operation**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/run",
    "params": {
      "operation_id": "getUser",
      "parameters": {
        "username": "octocat"
      }
    },
    "id": 6
  }'
```

2. **Test denied operation** (if you add an admin endpoint):
Should return error code 1001 (PolicyDeny).

## 4. Testing Audit Logging

Check audit logs:
```bash
# Logs are in the audit directory
ls -la .mrapids/audit/

# View recent audit entries
tail -f .mrapids/audit/mcp-audit-*.log | jq .
```

Each log entry contains:
- Unique ID
- Timestamp
- Operation details
- Policy decision
- Response (if detailed audit level)

## 5. Testing Response Redaction

1. Create a test endpoint that returns sensitive data:
```yaml
/test/secrets:
  get:
    operationId: getSecrets
    responses:
      200:
        description: Test response with secrets
        content:
          application/json:
            example:
              api_key: "sk-1234567890abcdef"
              token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              password: "super-secret-password"
              safe_data: "this is safe"
```

2. Call the endpoint and verify redaction:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/run",
    "params": {
      "operation_id": "getSecrets"
    },
    "id": 7
  }'
```

Response should show:
```json
{
  "api_key": "[REDACTED:API_KEY]",
  "token": "[REDACTED:JWT]",
  "password": "[REDACTED:PASSWORD]",
  "safe_data": "this is safe"
}
```

## 6. Integration Testing with Python

```python
import requests
import json

class MCPClient:
    def __init__(self, url="http://localhost:8080"):
        self.url = url
        self.id_counter = 1
        
    def call(self, method, params=None):
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.id_counter
        }
        self.id_counter += 1
        
        response = requests.post(self.url, json=payload)
        return response.json()

# Test the client
client = MCPClient()

# List operations
result = client.call("tools/list", {"filter": {"method": "GET"}})
print("Operations:", json.dumps(result, indent=2))

# Show operation details
result = client.call("tools/show", {"operation_id": "getUser"})
print("Operation details:", json.dumps(result, indent=2))

# Execute operation
result = client.call("tools/run", {
    "operation_id": "getUser",
    "parameters": {"username": "octocat"}
})
print("Execution result:", json.dumps(result, indent=2))
```

## 7. Performance Testing

```bash
# Install Apache Bench
# macOS: already installed
# Linux: apt-get install apache2-utils

# Test concurrent requests
ab -n 1000 -c 10 -p request.json -T application/json http://localhost:8080/
```

Where `request.json` contains:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 1
}
```

## 8. Security Testing

1. **Test SQL injection attempts**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/run",
    "params": {
      "operation_id": "getUser",
      "parameters": {
        "username": "octocat'; DROP TABLE users;--"
      }
    },
    "id": 8
  }'
```

2. **Test path traversal**:
```bash
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/run",
    "params": {
      "operation_id": "../../etc/passwd"
    },
    "id": 9
  }'
```

## 9. Unit Tests

Run the existing unit tests:
```bash
# Run all tests
cargo test

# Run with output
cargo test -- --nocapture

# Run specific test modules
cargo test policy::
cargo test api::
cargo test audit::
```

## 10. Debugging Tips

1. **Enable debug logging**:
```bash
RUST_LOG=debug ./target/release/mrapids-agent --config test-mcp-server.toml
```

2. **Check server state**:
- Audit logs show all operations
- Server logs show policy decisions
- Use `--generate-config` to see all config options

3. **Common issues**:
- Missing auth token: Set environment variables
- Policy denials: Check policy rules and audit logs
- Connection refused: Ensure server is running on correct port

This comprehensive testing approach covers unit tests, integration tests, security tests, and performance tests for the MCP integration.