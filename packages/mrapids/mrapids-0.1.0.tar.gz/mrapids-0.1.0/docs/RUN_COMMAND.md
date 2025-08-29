# Run Command Guide

The `run` command is the heart of MicroRapid - it executes API operations directly from your OpenAPI spec.

## Quick Start

```bash
# Simple GET request
mrapids run GetBalance --env development

# GET with parameters
mrapids run GetCharges --limit 10 --status succeeded

# POST with data
mrapids run CreateCustomer --data '{"email":"user@example.com"}'
```

## How It Works

```
mrapids run GetBalance --env development
    ↓
1. Find operation "GetBalance" in OpenAPI spec
2. Build HTTP request from operation definition
3. Apply environment config (auth, headers)
4. Execute request and display response
```

## Sending Parameters

### 1. Query Parameters

```bash
# Using common parameters (auto-mapped)
mrapids run GetCharges --limit 10 --status succeeded --env development

# Using generic --param for any parameter
mrapids run GetCharges --param created[gte]=1234567890 --param customer=cus_123

# Using explicit --query
mrapids run GetCharges --query limit=10 --query status=succeeded
```

### 2. Path Parameters

Path parameters are automatically mapped from common flags:

```bash
# --id maps to {id}, {chargeId}, {customerId}, etc.
mrapids run GetChargesCharge --id ch_3Q0PsyFTM8dCq9je0znVgRKq
mrapids run GetCustomersCustomer --id cus_123456

# Smart detection: --id finds the right path parameter
# /v1/charges/{id} → uses --id value
# /v1/customers/{customerId} → uses --id value
```

### 3. Request Body (POST/PUT/PATCH)

#### Option A: Inline JSON
```bash
mrapids run CreateCustomer --data '{"email":"user@example.com","name":"John Doe"}'
```

#### Option B: From File
```bash
# Using @file syntax
mrapids run CreateCustomer --data @customer.json

# Using --file flag
mrapids run CreateCustomer --file customer.json
```

#### Option C: From stdin
```bash
# Pipe from another command
echo '{"email":"user@example.com"}' | mrapids run CreateCustomer --stdin

# From a file
cat customer.json | mrapids run CreateCustomer --stdin
```

#### Option D: Required Fields Only
```bash
# Generate minimal payload with smart examples
mrapids run CreateCustomer --required-only

# This generates a payload with only required fields filled with realistic data
```

### 4. Headers

```bash
# Custom headers
mrapids run GetBalance \
  --header "X-Stripe-Version: 2023-10-16" \
  --header "Idempotency-Key: unique123"

# Auth shortcuts
mrapids run GetBalance --auth "Bearer sk_test_123" 
mrapids run GetBalance --api-key "your-api-key"
```

## Complete Examples

### List resources with filters
```bash
# GET /v1/charges with query parameters
mrapids run GetCharges \
  --limit 20 \
  --param created[gte]=1234567890 \
  --param customer=cus_123 \
  --env development
```

### Create a resource
```bash
# POST /v1/customers with JSON body
mrapids run CreateCustomer \
  --data '{
    "email": "alice@example.com",
    "name": "Alice Smith",
    "metadata": {"user_id": "123"}
  }' \
  --env development
```

### Update a resource
```bash
# POST /v1/customers/{id} with partial update
mrapids run UpdateCustomer \
  --id cus_123456 \
  --data '{"name": "Alice Johnson"}' \
  --env development
```

### Complex request
```bash
# Create subscription with file data, headers, and dry-run
mrapids run CreateSubscription \
  --file subscription.json \
  --header "Idempotency-Key: sub_$(date +%s)" \
  --env production \
  --dry-run  # Test first!
```

## Useful Flags

### Debugging & Testing
```bash
# See request details without sending
mrapids run CreateCustomer --data @customer.json --dry-run

# Show detailed request/response info
mrapids run GetBalance --verbose

# Show as curl command
mrapids run GetBalance --as-curl
```

### Output Control
```bash
# Save response to file
mrapids run GetCharges --save response.json

# Output format
mrapids run GetCharges --output json    # raw JSON
mrapids run GetCharges --output yaml    # YAML format
mrapids run GetCharges --output table   # table for arrays
```

### Advanced Options
```bash
# Custom base URL
mrapids run GetBalance --url https://api.stripe.com

# Timeout
mrapids run LongRunningOperation --timeout 120

# Retry on failure
mrapids run GetBalance --retry 3

# Use request template
mrapids run CreateCustomer --template customer-vip --template-vars tier=gold
```

## Environment Configuration

The `--env` flag loads configuration from workspace files:

```
project/
├── config/
│   ├── development.yaml   # --env development
│   ├── staging.yaml       # --env staging
│   └── production.yaml    # --env production
└── specs/
    └── api.yaml
```

Each environment can configure:
- Authentication (Bearer, API Key, Basic)
- Default headers
- Base URL overrides
- Rate limiting
- Safety checks

## Direct Operation vs Request Files

```bash
# Direct operation (recommended) - always uses latest spec
mrapids run GetBalance --env development

# Using request file - for customized requests
mrapids run requests/examples/get-balance.yaml --env development
```

## Tips

1. **Use `--dry-run`** to preview requests before sending
2. **Use `--verbose`** to debug issues
3. **Use `--required-only`** to quickly test POST operations
4. **Environment configs** handle auth automatically
5. **Common parameters** like `--id`, `--limit` are auto-mapped

## Parameter Mapping Logic

MicroRapid intelligently maps parameters:

1. **Path parameters**: `--id` maps to `{id}`, `{userId}`, `{customerId}`, etc.
2. **Query parameters**: All other parameters go to query string
3. **Body**: Only for POST/PUT/PATCH methods
4. **Headers**: Explicitly set with `--header`

The tool uses the OpenAPI spec to determine where each parameter belongs.