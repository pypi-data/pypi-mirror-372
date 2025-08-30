# Init-Config Command Guide

The `init-config` command creates environment-specific configuration files with authentication, headers, and API settings.

## Quick Start

```bash
# Create development config
mrapids init-config

# Create production config with safety checks
mrapids init-config --env production

# Pre-configured for Stripe API
mrapids init-config --env production --api stripe
```

## What It Creates

```
config/
├── development.yaml    # Environment config
├── .env               # Environment variables (git-ignored)
└── .env.example       # Template for version control
```

## Basic Usage

### Default Development Config

```bash
mrapids init-config
```

Creates `config/development.yaml`:
```yaml
name: development

defaults:
  timeout: 30
  retry:
    enabled: true
    max_attempts: 3
    backoff: exponential

headers:
  User-Agent: "MicroRapid/1.0 (Development)"
  X-Environment: "development"

# Authentication section with examples for:
# - Bearer token
# - Basic auth  
# - API key
# - OAuth2
```

### Production Config

```bash
mrapids init-config --env production
```

Adds production-specific features:
```yaml
safety:
  require_confirmation: true    # Confirm destructive operations
  audit_log: true              # Log all requests
  dry_run_default: false

rate_limit:
  requests_per_second: 10
  burst: 20

monitoring:
  trace_id_header: X-Trace-ID
  log_requests: true
  log_responses: false         # Don't log sensitive data
```

## Pre-Configured APIs

### Stripe
```bash
mrapids init-config --env development --api stripe
```

Creates config with:
```yaml
apis:
  stripe:
    base_url: https://api.stripe.com/v1
    auth:
      type: bearer
      token: ${STRIPE_TEST_KEY}
    content_type: application/x-www-form-urlencoded
    timeout: 30
```

### GitHub
```bash
mrapids init-config --env production --api github
```

```yaml
apis:
  github:
    base_url: https://api.github.com
    auth:
      type: bearer
      token: ${GITHUB_TOKEN}
    headers:
      Accept: application/vnd.github.v3+json
```

### OpenAI
```bash
mrapids init-config --api openai
```

```yaml
apis:
  openai:
    base_url: https://api.openai.com/v1
    auth:
      type: bearer
      token: ${OPENAI_API_KEY}
    timeout: 60
```

### Custom API
```bash
mrapids init-config --api myapi
```

Creates generic template:
```yaml
apis:
  myapi:
    base_url: ${MYAPI_BASE_URL}
    auth:
      type: bearer
      token: ${MYAPI_API_KEY}
    content_type: application/json
```

## Command Options

### --env / -e
Environment name (affects defaults and safety settings):
```bash
mrapids init-config --env staging
mrapids init-config --env production
mrapids init-config --env test
```

### --api / -a
Pre-configure for specific API:
```bash
mrapids init-config --api stripe
mrapids init-config --api github
mrapids init-config --api openai
mrapids init-config --api custom-name
```

### --output / -o
Custom output path:
```bash
# Different directory
mrapids init-config --output ~/configs/prod.yaml --env production

# Different filename
mrapids init-config --output config/prod-stripe.yaml --env production --api stripe
```

### --force / -f
Overwrite existing config:
```bash
mrapids init-config --env development --force
```

## Environment Variables

### Created .env File

```bash
# Development environment
STRIPE_TEST_KEY=sk_test_...
GITHUB_TOKEN=ghp_...
API_USERNAME=your_username
API_PASSWORD=your_password
```

### .env.example Template

```bash
# Stripe Test Key (development/staging)
STRIPE_TEST_KEY=sk_test_...

# GitHub Personal Access Token
GITHUB_TOKEN=ghp_... or ghs_...

# Add more environment variables as needed
```

## Configuration Sections

### 1. Defaults
Global settings for all requests:
```yaml
defaults:
  timeout: 30                  # Request timeout in seconds
  output: pretty               # Output format
  retry:
    enabled: true
    max_attempts: 3
    backoff: exponential       # exponential, linear, constant
```

### 2. Headers
Applied to all requests:
```yaml
headers:
  User-Agent: "MicroRapid/1.0"
  X-Environment: "development"
  X-Request-ID: "${REQUEST_ID:auto}"
```

### 3. Authentication
Global auth (can be overridden per API):

#### Bearer Token
```yaml
auth:
  type: bearer
  token: ${API_TOKEN}
```

#### Basic Auth
```yaml
auth:
  type: basic
  username: ${API_USERNAME}
  password: ${API_PASSWORD}
```

#### API Key
```yaml
auth:
  type: api_key
  header: X-API-Key
  key: ${API_KEY}
```

#### OAuth2
```yaml
auth:
  type: oauth2
  client_id: ${CLIENT_ID}
  client_secret: ${CLIENT_SECRET}
  token_url: https://oauth.provider.com/token
```

### 4. Safety (Production)
```yaml
safety:
  require_confirmation: true    # Confirm DELETE, PUT, PATCH
  audit_log: true              # Log all operations
  dry_run_default: false
```

### 5. Rate Limiting
```yaml
rate_limit:
  requests_per_second: 10
  burst: 20                    # Allow bursts up to 20
```

### 6. Monitoring
```yaml
monitoring:
  trace_id_header: X-Trace-ID
  log_requests: true
  log_responses: false         # Careful with sensitive data
```

### 7. API-Specific Overrides
```yaml
apis:
  stripe:
    base_url: https://api.stripe.com/v1
    auth:
      type: bearer
      token: ${STRIPE_KEY}
    
  internal:
    base_url: https://api.internal.com
    auth:
      type: basic
      username: ${INTERNAL_USER}
      password: ${INTERNAL_PASS}
    headers:
      X-Internal-Version: "2.0"
```

## Usage Examples

### Multi-Environment Setup

```bash
# Create configs for each environment
mrapids init-config --env development --api stripe
mrapids init-config --env staging --api stripe
mrapids init-config --env production --api stripe --force

# Use different environments
mrapids run GetBalance --env development
mrapids run GetBalance --env staging
mrapids run GetBalance --env production
```

### Project Organization

```
project/
├── config/
│   ├── development.yaml
│   ├── staging.yaml
│   ├── production.yaml
│   ├── .env              # Local secrets (git-ignored)
│   └── .env.example      # Template for team
├── specs/
│   └── api.yaml
└── .gitignore            # Contains: config/.env
```

### Team Collaboration

1. Create configs:
```bash
mrapids init-config --env development
mrapids init-config --env staging
mrapids init-config --env production
```

2. Commit templates:
```bash
git add config/*.yaml config/.env.example
git commit -m "Add environment configs"
```

3. Team members copy and fill:
```bash
cp config/.env.example config/.env
# Edit .env with real values
```

## Advanced Configuration

### Multiple APIs per Environment

```yaml
name: development

# Global defaults
defaults:
  timeout: 30

# Different APIs with different auth
apis:
  stripe:
    base_url: https://api.stripe.com/v1
    auth:
      type: bearer
      token: ${STRIPE_TEST_KEY}
  
  github:
    base_url: https://api.github.com
    auth:
      type: bearer
      token: ${GITHUB_TOKEN}
  
  internal:
    base_url: http://localhost:8080
    auth:
      type: api_key
      header: X-API-Key
      key: ${INTERNAL_API_KEY}
```

### Environment-Specific Features

```yaml
# Development - verbose, no limits
name: development
defaults:
  timeout: 60
monitoring:
  log_requests: true
  log_responses: true

# Production - strict, monitored
name: production
safety:
  require_confirmation: true
rate_limit:
  requests_per_second: 10
monitoring:
  log_requests: true
  log_responses: false
```

### Dynamic Values

```yaml
headers:
  # Auto-generated request ID
  X-Request-ID: "${REQUEST_ID:auto}"
  
  # Timestamp
  X-Timestamp: "${TIMESTAMP:now}"
  
  # With defaults
  X-Client-Version: "${CLIENT_VERSION:1.0.0}"
```

## Best Practices

### 1. Security
- Never commit `.env` files
- Use environment-specific keys
- Rotate keys regularly
- Use read-only keys in development

### 2. Organization
```bash
# Clear naming
config/dev-stripe.yaml
config/prod-stripe.yaml
config/test-integration.yaml
```

### 3. Environment Variables
```bash
# Prefix by environment
STRIPE_TEST_KEY=sk_test_...
STRIPE_LIVE_KEY=sk_live_...

# Or by purpose
DEV_STRIPE_KEY=sk_test_...
PROD_STRIPE_KEY=sk_live_...
```

## Troubleshooting

### Config not found
```bash
# Check current directory
pwd
ls config/

# Specify path explicitly
mrapids run GetBalance --env development --config ./config/dev.yaml
```

### Environment variables not loading
```bash
# Check .env file exists
ls -la config/.env

# Debug mode
MRAPIDS_DEBUG=1 mrapids run GetBalance --env development

# Manual export
export STRIPE_TEST_KEY=sk_test_...
mrapids run GetBalance --env development
```

### Wrong config loaded
```bash
# Be explicit about environment
mrapids run GetBalance --env production

# Check which config is loaded
mrapids run GetBalance --env development --verbose
```