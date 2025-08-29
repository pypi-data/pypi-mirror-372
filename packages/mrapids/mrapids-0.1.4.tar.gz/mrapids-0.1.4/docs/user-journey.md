# MicroRapid User Journey

## Overview

MicroRapid transforms OpenAPI specifications into executable API calls with minimal friction. This document walks through the complete user journey from initialization to API execution.

## Quick Start: Zero to API Call

```bash
# 1. Initialize project with an API spec
mrapids init my-api --from-url https://api.example.com/openapi.json

# 2. Configure your environment
cd my-api
mrapids init-config --env development --api stripe

# 3. Analyze the API to generate requests
mrapids analyze specs/api.yaml

# 4. Execute your first API call
mrapids run list-customers
```

## Detailed User Journey

### Step 1: Project Initialization

Initialize a new MicroRapid project with your API specification:

```bash
mrapids init my-stripe-api --from-url https://api.stripe.com/spec.json
```

This creates a well-organized project structure:

```
my-stripe-api/
├── specs/api.yaml         # Your API specification (auto-converted to YAML)
├── config/                # Environment configurations
│   └── .env.example       # Template for API keys
├── requests/              # Request configurations (generated)
├── data/                  # Request payloads (generated)
├── tests/                 # Test cases
└── docs/                  # Documentation
```

### Step 2: Environment Configuration

Set up your API credentials for different environments:

```bash
# Create environment-specific configuration
mrapids init-config --env development --api stripe

# Add your API key
echo "STRIPE_TEST_KEY=sk_test_xxx" > config/.env
```

Each environment gets its own configuration file:
- `config/development.yaml` - Development settings
- `config/staging.yaml` - Staging settings  
- `config/production.yaml` - Production settings (with safety features)

### Step 3: API Analysis

Analyze your OpenAPI spec to generate executable request configurations:

```bash
mrapids analyze specs/api.yaml
```

This generates:
- **Request configs** in `requests/` - One YAML file per operation
- **Example payloads** in `data/` - JSON templates for POST/PUT requests

### Step 4: Understanding the Contract

Before running an API, understand what's required:

```bash
# List all available operations
mrapids list operations

# Show contract details for a specific operation
mrapids show create-customer
```

Output shows:
- Required vs optional fields
- Field types and constraints
- Example values
- Expected responses

### Step 5: Executing API Calls

Multiple ways to run APIs based on complexity:

#### Simple GET Request
```bash
mrapids run get-customer --id cus_123
```

#### POST with Inline Data
```bash
mrapids run create-customer \
  --email test@example.com \
  --name "Test Customer"
```

#### Complex Request with File
```bash
# Edit the generated data file first
vim data/examples/create-customer.json

# Run with the data file
mrapids run create-customer
```

#### Environment-Based Execution
```bash
# Uses config from config/development.yaml
mrapids run stripe:customers --env development
```

## Common Workflows

### Testing a New API

1. **Explore available operations:**
   ```bash
   mrapids list operations | grep customer
   ```

2. **Understand the contract:**
   ```bash
   mrapids show create-customer
   ```

3. **Test with minimal data:**
   ```bash
   mrapids run create-customer --required-only
   ```

4. **Save successful test:**
   ```bash
   mrapids run create-customer --save-as tests/customer-test.yaml
   ```

### Debugging Failed Requests

```bash
# Dry run to see what would be sent
mrapids run create-customer --dry-run

# Verbose mode for debugging
mrapids run create-customer --verbose

# Validate against schema before sending
mrapids validate create-customer
```

### CI/CD Integration

```bash
# Run all tests
mrapids test --all

# Run specific test suite
mrapids test tests/customers/*.yaml

# Generate test report
mrapids test --format junit > test-results.xml
```

## Best Practices

1. **Start Simple**: Use `--required-only` flag to test with minimal data
2. **Save Success**: Save working requests as test cases
3. **Use Environments**: Separate dev/staging/prod configurations
4. **Version Control**: Commit your `requests/` and `tests/` directories
5. **Validate First**: Use `--dry-run` to check before sending

## Troubleshooting

### "String" in Generated Data Files
The current version generates placeholder data. Replace with real values:

```json
// Generated (not useful)
{
  "email": "string",
  "name": "string"
}

// Replace with:
{
  "email": "test@example.com",
  "name": "Test Customer"
}
```

### Authentication Errors
Ensure your environment variables are set:

```bash
# Check current environment
mrapids config --show

# Test with a simple authenticated request
mrapids run get-account --env development
```

## Next Steps

- Read the [Value Proposition](./value-proposition.md) to understand MicroRapid's unique benefits
- See [Examples](./examples/) for common API patterns
- Check [API Reference](./api-reference.md) for all commands