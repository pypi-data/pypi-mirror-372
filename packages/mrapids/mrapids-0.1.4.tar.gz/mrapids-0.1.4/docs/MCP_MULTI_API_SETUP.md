# Managing Multiple APIs with MCP Agent

When you have many API specs (Stripe, GitHub, Calendar, Internal APIs, etc.), here are the best approaches:

## Approach 1: Separate Agents (Recommended for 2-10 APIs)

Each API gets its own agent instance on different ports:

### Directory Structure
```
~/.mrapids-apis/
├── github/
│   ├── mcp-server.toml
│   ├── api.yaml
│   └── policy.yaml
├── stripe/
│   ├── mcp-server.toml
│   ├── api.yaml
│   └── policy.yaml
├── calendar/
│   ├── mcp-server.toml
│   ├── api.yaml
│   └── policy.yaml
└── internal/
    ├── mcp-server.toml
    ├── api.yaml
    └── policy.yaml
```

### Claude Configuration
```json
{
  "mcpServers": {
    "github": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8080", "--config-dir", "~/.mrapids-apis/github"],
      "env": { "GITHUB_TOKEN": "${GITHUB_TOKEN}" }
    },
    "stripe": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8081", "--config-dir", "~/.mrapids-apis/stripe"],
      "env": { "STRIPE_API_KEY": "${STRIPE_API_KEY}" }
    },
    "calendar": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8082", "--config-dir", "~/.mrapids-apis/calendar"],
      "env": { "CALENDAR_API_KEY": "${CALENDAR_API_KEY}" }
    },
    "internal": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8083", "--config-dir", "~/.mrapids-apis/internal"],
      "env": { "INTERNAL_API_KEY": "${INTERNAL_API_KEY}" }
    }
  }
}
```

**Pros**: 
- Isolated policies per API
- Independent scaling
- Clear separation

**Cons**:
- Multiple processes
- More ports to manage

## Approach 2: Unified Spec (Future Feature)

Combine multiple OpenAPI specs into one mega-spec:

### Directory Structure
```
~/.mrapids-unified/
├── mcp-server.toml
├── unified-api.yaml    # Combined spec
├── policy.yaml         # Unified policies
└── specs/              # Original specs
    ├── github.yaml
    ├── stripe.yaml
    ├── calendar.yaml
    └── internal.yaml
```

### Generate Unified Spec
```bash
# Future command
mrapids-agent merge-specs \
  --input specs/*.yaml \
  --output unified-api.yaml \
  --prefix-operations
```

### Result in unified-api.yaml
```yaml
openapi: "3.0.0"
info:
  title: "Unified API Gateway"
paths:
  # GitHub paths
  /github/repos/{owner}/{repo}:
    get:
      operationId: github_getRepository
      
  # Stripe paths  
  /stripe/customers/{id}:
    get:
      operationId: stripe_getCustomer
      
  # Calendar paths
  /calendar/events:
    get:
      operationId: calendar_listEvents
```

### Claude Configuration
```json
{
  "mcpServers": {
    "unified-apis": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8080", "--config-dir", "~/.mrapids-unified"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}",
        "STRIPE_API_KEY": "${STRIPE_API_KEY}",
        "CALENDAR_API_KEY": "${CALENDAR_API_KEY}"
      }
    }
  }
}
```

## Approach 3: Dynamic API Loading (Enterprise)

For many APIs, use dynamic configuration:

### Directory Structure
```
~/.mrapids-dynamic/
├── mcp-server.toml
├── apis/
│   ├── github/
│   │   ├── spec.yaml
│   │   ├── policy.yaml
│   │   └── auth.toml
│   ├── stripe/
│   │   ├── spec.yaml
│   │   ├── policy.yaml
│   │   └── auth.toml
│   └── .../
└── registry.yaml
```

### Registry Configuration
```yaml
# registry.yaml
apis:
  - id: github
    name: "GitHub API"
    spec: apis/github/spec.yaml
    policy: apis/github/policy.yaml
    auth: apis/github/auth.toml
    tags: ["vcs", "development"]
    
  - id: stripe  
    name: "Stripe API"
    spec: apis/stripe/spec.yaml
    policy: apis/stripe/policy.yaml
    auth: apis/stripe/auth.toml
    tags: ["payment", "billing"]
    
  - id: calendar
    name: "Calendar API"
    spec: apis/calendar/spec.yaml
    policy: apis/calendar/policy.yaml
    auth: apis/calendar/auth.toml
    tags: ["productivity", "scheduling"]
```

### Enhanced MCP Server Config
```toml
# mcp-server.toml
[server]
mode = "dynamic"
registry = "registry.yaml"

[discovery]
enable_search = true
enable_tags = true
```

## Approach 4: API Gateway Pattern

Use MicroRapid as an API gateway with namespace routing:

### Setup Script
```bash
#!/bin/bash
# setup-multi-api.sh

# Create base directory
mkdir -p ~/.mrapids-gateway

# Create gateway configuration
cat > ~/.mrapids-gateway/gateway.yaml << EOF
version: "1.0"
routes:
  - prefix: /github
    spec: specs/github.yaml
    auth: github
    
  - prefix: /stripe
    spec: specs/stripe.yaml
    auth: stripe
    
  - prefix: /calendar
    spec: specs/calendar.yaml
    auth: calendar
EOF

# Start gateway agent
mrapids-agent start --mode gateway --config ~/.mrapids-gateway
```

## Best Practices for Multiple APIs

### 1. Naming Conventions
```
Operation IDs: {api}_{operation}
- github_listRepos
- stripe_createCustomer
- calendar_getEvents
```

### 2. Unified Policy Structure
```yaml
# policy.yaml
rules:
  # Global rules
  - name: "deny-all-deletes"
    pattern: "*"
    deny:
      methods: ["DELETE"]
      
  # API-specific rules
  - name: "github-readonly"
    pattern: "/github/*"
    allow:
      methods: ["GET"]
      
  - name: "stripe-limited"
    pattern: "/stripe/*"
    allow:
      operations: ["stripe_listCustomers", "stripe_getCustomer"]
```

### 3. Centralized Auth Management
```bash
# Create auth profile manager
~/.mrapids-auth/
├── profiles/
│   ├── github.toml
│   ├── stripe.toml
│   └── calendar.toml
└── vault.encrypted  # Future: encrypted storage
```

### 4. Batch Operations Script
```bash
#!/bin/bash
# manage-all-agents.sh

APIS="github stripe calendar internal"
BASE_PORT=8080

case "$1" in
  start)
    for api in $APIS; do
      echo "Starting $api agent on port $BASE_PORT"
      mrapids-agent start \
        --port $BASE_PORT \
        --config-dir ~/.mrapids-apis/$api \
        --daemon
      ((BASE_PORT++))
    done
    ;;
    
  stop)
    for api in $APIS; do
      mrapids-agent stop --config-dir ~/.mrapids-apis/$api
    done
    ;;
    
  status)
    for api in $APIS; do
      echo -n "$api: "
      mrapids-agent status --config-dir ~/.mrapids-apis/$api
    done
    ;;
esac
```

## Scaling Considerations

### For 2-5 APIs
- Use separate agents (Approach 1)
- Simple and isolated
- Easy to debug

### For 5-20 APIs  
- Consider unified spec (Approach 2)
- Or use dynamic loading (Approach 3)
- Better resource usage

### For 20+ APIs
- Implement gateway pattern (Approach 4)
- Consider service mesh
- Add caching layer

## Example: Complete Setup for 5 APIs

```bash
#!/bin/bash
# setup-my-apis.sh

# Create directory structure
mkdir -p ~/.mrapids-apis/{github,stripe,calendar,slack,jira}

# Initialize each API
for api in github stripe calendar slack jira; do
  cd ~/.mrapids-apis/$api
  
  # Download or copy spec
  case $api in
    github)
      curl -o api.yaml https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.yaml
      ;;
    stripe)
      curl -o api.yaml https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.yaml
      ;;
    *)
      echo "Add your $api spec to ~/.mrapids-apis/$api/api.yaml"
      ;;
  esac
  
  # Create config
  cat > mcp-server.toml << EOF
[server]
name = "$api"

[defaults]
spec_path = "api.yaml"
policy_file = "policy.yaml"
auth_profile = "$api"
EOF

  # Create policy
  cat > policy.yaml << EOF
version: "1.0"
metadata:
  api: "$api"
  
rules:
  - name: "allow-${api}-reads"
    pattern: "*"
    allow:
      methods: ["GET"]
EOF
done

# Create unified Claude config
cat > ~/claude-mcp-config.json << EOF
{
  "mcpServers": {
EOF

PORT=8080
for api in github stripe calendar slack jira; do
  cat >> ~/claude-mcp-config.json << EOF
    "$api": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "$PORT", "--config-dir", "$HOME/.mrapids-apis/$api"],
      "env": {
        "$(echo $api | tr '[:lower:]' '[:upper:]')_TOKEN": "\${$(echo $api | tr '[:lower:]' '[:upper:]')_TOKEN}"
      }
    },
EOF
  ((PORT++))
done

# Close JSON
echo '  }' >> ~/claude-mcp-config.json
echo '}' >> ~/claude-mcp-config.json

echo "Setup complete! Copy ~/claude-mcp-config.json to Claude's config location"
```

## Future Enhancements

1. **API Discovery Service**
   ```bash
   mrapids-agent discover --scan ~/.apis/
   ```

2. **Unified Dashboard**
   ```bash
   mrapids-agent dashboard --port 9000
   ```

3. **Smart Routing**
   - Auto-detect which API to use based on request
   - Load balance between similar APIs

4. **API Composition**
   - Combine multiple API calls
   - Create virtual endpoints

This gives users flexibility to scale from a few APIs to dozens, with appropriate patterns for each scale.