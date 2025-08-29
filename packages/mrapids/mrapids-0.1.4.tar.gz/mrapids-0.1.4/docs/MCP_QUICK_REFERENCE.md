# MCP Integration Quick Reference

## 🚀 What's Implemented for Agents

### Core Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Safe API Execution** | Agents execute operations through MCP server | No direct API access needed |
| **Policy Engine** | Rule-based access control with patterns | Control what agents can do |
| **Audit Logging** | Complete trail of all agent actions | Track and monitor usage |
| **Response Redaction** | Automatic removal of sensitive data | Agents never see secrets |
| **Auth Profiles** | Named credential references | Secure credential management |

### Available Tools for Agents

#### 1. List Operations
```bash
# Find available operations
POST /tools/list
{
  "filter": {
    "method": "GET",     # Optional: filter by HTTP method
    "pattern": "user"    # Optional: search pattern
  }
}
```

#### 2. Show Operation Details  
```bash
# Get operation schema and parameters
POST /tools/show
{
  "operation_id": "getUser"
}
```

#### 3. Run Operation
```bash
# Execute an API operation
POST /tools/run
{
  "operation_id": "getUser",
  "parameters": {"id": "123"},
  "auth_profile": "github"    # Optional: auth profile to use
}
```

## 🛡️ Security Features

### Policy Rules
```yaml
rules:
  - name: "allow-reads"
    pattern: "*/users/*"
    allow:
      methods: ["GET"]
      
  - name: "deny-admin"
    pattern: "*/admin/*"
    deny:
      reason: "Admin access restricted"
```

### Response Redaction
- Auto-redacts: API keys, JWTs, passwords, credit cards
- Custom patterns via config
- Example: `"api_key": "sk-123..."` → `"api_key": "[REDACTED:API_KEY]"`

### Audit Entry
```json
{
  "id": "unique-uuid",
  "timestamp": "2024-01-20T10:30:00Z",
  "agent_id": "mcp-agent",
  "operation": {
    "operation_id": "getUser",
    "url": "https://api.example.com/users/123"
  },
  "policy": {
    "decision": "allow",
    "rule": "allow-reads"
  }
}
```

## 🎯 Use Cases

### 1. **Customer Support Bot**
- List customer orders
- View order details
- Update order status
- Cannot: Delete orders, access admin panel

### 2. **Documentation Assistant**
- Explore API endpoints
- Show operation schemas
- Test GET endpoints
- Cannot: Modify data, access private APIs

### 3. **Development Helper**
- Generate API examples
- Test endpoint availability
- Validate response formats
- Cannot: Access production data, modify configs

### 4. **Analytics Agent**
- Fetch metrics data
- Aggregate statistics
- Generate reports
- Cannot: Access PII, modify data

## 🔧 Quick Setup

```bash
# 1. Build
cd agent && cargo build --release

# 2. Configure
cat > mcp-server.toml << EOF
[server]
host = "127.0.0.1"
port = 8080

[defaults]
spec_path = "api.yaml"
policy_file = "policy.yaml"
EOF

# 3. Create Policy
cat > policy.yaml << EOF
version: "1.0"
rules:
  - name: "allow-safe-reads"
    pattern: "*"
    allow:
      methods: ["GET"]
EOF

# 4. Run
./target/release/mrapids-agent --config mcp-server.toml

# 5. Test
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

## 📊 Architecture

```
┌─────────────┐     JSON-RPC      ┌──────────────┐
│  AI Agent   │ ◄──────────────► │  MCP Server  │
└─────────────┘                   └──────┬───────┘
                                         │
                                         ▼
                              ┌────────────────────┐
                              │   Policy Engine    │
                              └────────┬───────────┘
                                      │
                              ┌───────▼────────┐
                              │  Audit Logger  │
                              └───────┬────────┘
                                     │
                              ┌──────▼───────┐
                              │   Redactor   │
                              └──────┬───────┘
                                     │
                              ┌──────▼───────┐
                              │  Target API  │
                              └──────────────┘
```

## 🔑 Key Benefits

1. **Security First**: Agents never see credentials or sensitive data
2. **Full Control**: Define exactly what agents can/cannot do
3. **Complete Visibility**: Every action is logged and auditable
4. **Easy Integration**: Standard JSON-RPC protocol
5. **Flexible Policies**: Time-based, method-based, pattern-based rules

## 📝 Error Codes

| Code | Meaning | Example |
|------|---------|---------|
| 1001 | Policy Deny | "Admin endpoints are restricted" |
| 2001 | Auth Missing | "Authentication required" |
| 3001 | Invalid Input | "Missing required parameter" |
| 4001 | Execution Failed | "API returned error" |
| 5001 | Internal Error | "Audit logging failed" |

## 🚦 Status

✅ **Implemented**
- Core MCP server with JSON-RPC
- Policy engine with pattern matching
- Audit logging with rotation
- Response redaction
- Auth profile management
- Three tools: list, show, run

🚧 **Future Enhancements**
- WebSocket support for streaming
- Rate limiting per agent
- Caching for read operations
- Batch operations support
- Webhook notifications