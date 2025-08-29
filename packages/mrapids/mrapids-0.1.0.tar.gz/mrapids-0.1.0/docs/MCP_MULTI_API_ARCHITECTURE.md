# Multi-API Architecture with MCP Agent

## Visual Overview

### Approach 1: Multiple Agents (Current - Recommended)

```
┌─────────────────────────────────────────────────────┐
│                  Claude Desktop                      │
│  ┌─────────────────────────────────────────────┐   │
│  │            MCP Client Manager                │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ GitHub   │ │ Stripe   │ │ Calendar │   │   │
│  │  │ Client   │ │ Client   │ │ Client   │   │   │
│  │  └─────┬────┘ └─────┬────┘ └─────┬────┘   │   │
│  └────────┼────────────┼────────────┼─────────┘   │
└───────────┼────────────┼────────────┼──────────────┘
            │            │            │
     Port 8080    Port 8081    Port 8082
            │            │            │
┌───────────▼───┐ ┌──────▼───┐ ┌─────▼────┐
│ mrapids-agent │ │  mrapids │ │ mrapids  │
│   (GitHub)    │ │  -agent  │ │  -agent  │
│               │ │ (Stripe) │ │(Calendar)│
├───────────────┤ ├──────────┤ ├──────────┤
│ github/       │ │ stripe/  │ │calendar/ │
│ ├─ api.yaml   │ │├─api.yaml│ │├─api.yaml│
│ ├─ policy.yaml│ │├─policy  │ │├─policy  │
│ └─ auth.toml  │ │└─auth    │ │└─auth    │
└───────┬───────┘ └────┬─────┘ └────┬─────┘
        │              │             │
        ▼              ▼             ▼
   GitHub API    Stripe API    Calendar API
```

### Approach 2: Unified Gateway (Future)

```
┌─────────────────────────────────────────────────────┐
│                  Claude Desktop                      │
│  ┌─────────────────────────────────────────────┐   │
│  │              Single MCP Client               │   │
│  │         "All my APIs in one place"           │   │
│  └──────────────────┬───────────────────────────┘   │
└─────────────────────┼───────────────────────────────┘
                      │
                 Port 8080
                      │
         ┌────────────▼────────────┐
         │    mrapids-agent        │
         │   (Gateway Mode)        │
         ├─────────────────────────┤
         │ • Route by path prefix  │
         │ • Unified auth          │
         │ • Central policy        │
         └────────────┬────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
   /github/*     /stripe/*    /calendar/*
        │             │             │
        ▼             ▼             ▼
   GitHub API    Stripe API    Calendar API
```

## Quick Decision Guide

### How Many APIs Do You Have?

```
1-3 APIs   → Separate agents (simple)
4-10 APIs  → Separate agents with management script
10-20 APIs → Unified gateway or dynamic loading
20+ APIs   → Enterprise patterns (service mesh, API gateway)
```

## Example: 5 API Setup

Let's say you have:
- GitHub (version control)
- Stripe (payments)
- Google Calendar (scheduling)  
- Slack (communication)
- Jira (project management)

### Step 1: Directory Structure
```
~/.mrapids-apis/
├── github/
│   ├── mcp-server.toml
│   ├── github-api.yaml     (143 KB)
│   └── policy.yaml
├── stripe/
│   ├── mcp-server.toml
│   ├── stripe-api.yaml     (523 KB)
│   └── policy.yaml
├── calendar/
│   ├── mcp-server.toml
│   ├── gcal-api.yaml       (89 KB)
│   └── policy.yaml
├── slack/
│   ├── mcp-server.toml
│   ├── slack-api.yaml      (234 KB)
│   └── policy.yaml
└── jira/
    ├── mcp-server.toml
    ├── jira-api.yaml       (412 KB)
    └── policy.yaml
```

### Step 2: Claude Config (Simplified)
```json
{
  "mcpServers": {
    "github": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8080", "--config-dir", "~/.mrapids-apis/github"]
    },
    "stripe": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8081", "--config-dir", "~/.mrapids-apis/stripe"]
    },
    "calendar": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8082", "--config-dir", "~/.mrapids-apis/calendar"]
    },
    "slack": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8083", "--config-dir", "~/.mrapids-apis/slack"]
    },
    "jira": {
      "command": "mrapids-agent",
      "args": ["start", "--port", "8084", "--config-dir", "~/.mrapids-apis/jira"]
    }
  }
}
```

### Step 3: Usage in Claude

```
You: "Create a GitHub issue about the Stripe payment bug"

Claude: I'll help you create a GitHub issue about the Stripe payment bug. Let me:
1. First check your Stripe account for recent payment errors
2. Then create a detailed GitHub issue

[Claude uses stripe agent to get error details]
[Claude uses github agent to create issue]

You: "Schedule a meeting about this issue"

Claude: I'll schedule a meeting about the payment bug issue.

[Claude uses calendar agent to find available slots]
[Claude uses slack agent to notify team]
```

## Management Tips

### 1. Port Management
```bash
# Reserve port ranges
GitHub:   8080-8089
Stripe:   8090-8099  
Calendar: 8100-8109
Slack:    8110-8119
Jira:     8120-8129
```

### 2. Process Management
```bash
# Start all
~/.mrapids-apis/start-all.sh

# Status check
ps aux | grep mrapids-agent | grep -v grep | wc -l
# Should show 5 processes

# Resource usage
htop -p $(pgrep -d, mrapids-agent)
```

### 3. Debugging
```bash
# Check individual agent
curl http://localhost:8080/health

# View logs
tail -f ~/.mrapids-apis/*/audit/current.log

# Test specific API
mrapids-agent test --port 8081 --operation listCustomers
```

## Advanced Patterns

### Pattern 1: API Categories
Group related APIs:
```
~/.mrapids-apis/
├── development/     (GitHub, GitLab, Jira)
├── financial/       (Stripe, PayPal, QuickBooks)
├── communication/   (Slack, Discord, Email)
└── productivity/    (Calendar, Todoist, Notion)
```

### Pattern 2: Environment Separation
```
~/.mrapids-apis/
├── production/
│   ├── github-prod/
│   └── stripe-prod/
└── development/
    ├── github-dev/
    └── stripe-dev/
```

### Pattern 3: Shared Policies
```
~/.mrapids-apis/
├── _shared/
│   ├── base-policy.yaml
│   └── common-rules.yaml
├── github/
│   └── policy.yaml  # includes: ../_shared/base-policy.yaml
└── stripe/
    └── policy.yaml  # includes: ../_shared/base-policy.yaml
```

## Performance Considerations

### Resource Usage (Typical)
```
Per Agent:
- Memory: 20-50 MB
- CPU: 0.1-0.5%
- Startup: 200-500ms

5 Agents Total:
- Memory: ~200 MB
- CPU: ~1%
- Ports: 5
```

### Optimization Tips
1. **Lazy Loading**: Start agents on-demand
2. **Shared Cache**: Use Redis for common data
3. **Connection Pooling**: Reuse HTTP connections
4. **Rate Limiting**: Implement per-API limits

## Future: Smart API Router

Imagine asking Claude without specifying which API:

```
You: "Show my recent payments"
Claude: [Automatically uses Stripe API]

You: "What issues are assigned to me?"
Claude: [Automatically uses Jira API]

You: "Schedule a meeting next week"
Claude: [Automatically uses Calendar API]
```

This would require:
- API capability registry
- Intent classification
- Smart routing logic

## Summary

For multiple APIs:
- **Current Best**: Run separate agents (simple, isolated)
- **Future Vision**: Unified gateway with smart routing
- **Key Principle**: Each API has its own spec, policy, and auth
- **Claude Benefit**: Natural language access to all your APIs