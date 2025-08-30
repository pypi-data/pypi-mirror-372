# Analyze Command Guide

The `analyze` command examines your OpenAPI specification and generates example request configurations and data files.

## Quick Start

```bash
# Analyze default spec (specs/api.yaml)
mrapids analyze

# Analyze and generate all examples
mrapids analyze --all

# Analyze specific operation
mrapids analyze --operation CreateCustomer
```

## What It Does

1. **Parses** your OpenAPI/Swagger specification
2. **Validates** the spec structure
3. **Generates** example request configs in `requests/examples/`
4. **Creates** sample data files in `data/`
5. **Reports** statistics about your API

## Generated Files

### Request Configurations
`requests/examples/{operation-id}.yaml`

```yaml
# Auto-generated from specs/api.yaml
operation: CreateCustomer
method: POST
path: /v1/customers
description: Create a new customer
headers:
  Content-Type: application/json
  Accept: application/json
body: data/create-customer.json
expect:
  status: 200
```

### Data Files
`data/{operation-id}.json`

```json
{
  "email": "user@example.com",
  "name": "Jenny Rosen",
  "description": "Premium customer",
  "metadata": {
    "order_id": "order_123"
  }
}
```

## Command Options

### --operation / -o
Analyze specific operation only:
```bash
mrapids analyze --operation CreatePaymentIntent
mrapids analyze -o GetCustomer
```

### --output / -d
Custom output directory:
```bash
mrapids analyze --output ./generated
mrapids analyze -d /tmp/api-examples
```

### --all
Generate examples for all operations:
```bash
mrapids analyze --all
```
Without this flag, analyze shows statistics only.

### --skip-data
Skip generating data files:
```bash
mrapids analyze --all --skip-data
```
Useful when you only want request configs.

### --force / -f
Overwrite existing files:
```bash
mrapids analyze --all --force
```

### --cleanup-backups
Clean up backup directories (default: true):
```bash
mrapids analyze --all --cleanup-backups=false
```

## Examples

### Basic Analysis

```bash
mrapids analyze
```

Output:
```
🔍 Analyzing API specification...
📊 API: Stripe API (v1)
📁 Base URL: https://api.stripe.com

📈 Statistics:
  Total operations: 500
  GET:    250 operations
  POST:   200 operations  
  DELETE: 50 operations

✅ Ready to generate examples. Use --all or --operation <name>
```

### Generate All Examples

```bash
mrapids analyze --all
```

Output:
```
🔍 Analyzing API specification...
✨ Generating examples...

  ✅ Generated: requests/examples/get-balance.yaml
  ✅ Generated: requests/examples/create-customer.yaml
  ✅ Generated: requests/examples/update-customer.yaml
  ... 

📊 Summary:
  Generated 500 request examples
  Created 200 data files
  Skipped 0 (already exist)

Next steps:
  1. Review generated examples in requests/examples/
  2. Run an example: mrapids run requests/examples/create-customer.yaml
  3. Or use direct: mrapids run CreateCustomer
```

### Selective Generation

```bash
# Single operation
mrapids analyze --operation CreateSubscription

# Multiple operations
for op in CreateCustomer CreateSubscription CreateInvoice; do
  mrapids analyze --operation $op
done

# Pattern matching
mrapids list operations --filter payment --format simple | \
  cut -d' ' -f1 | \
  xargs -I {} mrapids analyze --operation {}
```

## Smart Example Generation

The analyzer generates realistic examples based on field names:

| Field Name | Generated Example |
|------------|------------------|
| `email` | `"user@example.com"` |
| `phone` | `"+14155551234"` |
| `name` | `"Jenny Rosen"` |
| `amount` | `2000` |
| `currency` | `"usd"` |
| `created` | `1640995200` |
| `url` | `"https://example.com/webhook"` |
| `description` | `"Premium subscription"` |

## Working with Generated Files

### Request Configurations

Execute directly:
```bash
mrapids run requests/examples/create-customer.yaml
```

Customize before running:
```bash
# Edit the generated file
vim requests/examples/create-customer.yaml

# Add custom headers, change data, etc.
mrapids run requests/examples/create-customer.yaml --env production
```

### Data Files

Use generated data:
```bash
# As-is
mrapids run CreateCustomer --file data/create-customer.json

# Modified
cp data/create-customer.json my-customer.json
# Edit my-customer.json
mrapids run CreateCustomer --file my-customer.json
```

## Advanced Usage

### Incremental Generation

```bash
# First, analyze to see what's available
mrapids analyze

# Generate examples for new operations only
mrapids analyze --all

# Force regenerate specific operation
mrapids analyze --operation UpdateCustomer --force
```

### Custom Templates

```bash
# Generate with custom output structure
mrapids analyze --all --output ./custom-examples

# Organize by method
for method in GET POST PUT DELETE; do
  mkdir -p examples/$method
  mrapids list operations --method $method --format simple | \
    cut -d' ' -f1 | \
    xargs -I {} mrapids analyze --operation {} --output examples/$method
done
```

### CI/CD Integration

```bash
#!/bin/bash
# ci-check-examples.sh

# Analyze and check if examples are up to date
mrapids analyze --all --output /tmp/examples

# Compare with committed examples
diff -r requests/examples /tmp/examples/requests/examples
if [ $? -ne 0 ]; then
  echo "Examples are out of date. Run: mrapids analyze --all"
  exit 1
fi
```

## Understanding the Output

### Request Configuration Structure

```yaml
# Auto-generated header
# Shows source and operation details

operation: CreatePaymentIntent    # OpenAPI operation ID
method: POST                     # HTTP method
path: /v1/payment_intents       # URL path
description: Create a payment   # From OpenAPI summary

headers:                        # Required headers
  Content-Type: application/json
  Accept: application/json

params:                         # Query parameters
  expand: ["latest_charge"]

body: data/create-payment-intent.json  # Request body reference

expect:                         # Expected response
  status: 200
  content_type: application/json
```

### Data File Structure

```json
{
  // Required fields with smart examples
  "amount": 2000,
  "currency": "usd",
  
  // Optional fields with realistic data
  "description": "Premium subscription",
  "metadata": {
    "order_id": "order_123"
  },
  
  // Arrays with example items
  "payment_method_types": ["card"]
}
```

## Tips & Best Practices

### 1. Initial Setup
```bash
# Full analysis after init
mrapids init api.yaml my-project
cd my-project
mrapids analyze --all
```

### 2. Keeping Examples Updated
```bash
# After API spec changes
git pull
mrapids analyze --all --force
git add requests/examples data/
git commit -m "Update examples for new API version"
```

### 3. Testing Workflows
```bash
# Generate examples for testing
mrapids analyze --operation CreateCustomer
mrapids run requests/examples/create-customer.yaml --dry-run
# Modify if needed
mrapids run requests/examples/create-customer.yaml --env test
```

### 4. Documentation
```bash
# Generate examples for docs
mrapids analyze --all --output docs/examples
# Include in documentation
```

## Troubleshooting

### No operations found
```bash
# Check spec location
ls specs/
mrapids analyze --spec ./path/to/openapi.yaml

# Validate spec
mrapids validate api.yaml
```

### Examples not generating
```bash
# Check permissions
ls -la requests/examples/

# Force regeneration
mrapids analyze --operation SomeOperation --force

# Check for errors in spec
mrapids analyze --operation SomeOperation --verbose
```

### Data files missing
```bash
# Some operations might not have request bodies
mrapids show OperationName

# Check if skipped
mrapids analyze --operation OperationName
# Look for "No request body" message
```

### Large APIs
```bash
# Generate in batches
mrapids list operations --format simple | \
  head -50 | \
  cut -d' ' -f1 | \
  xargs -I {} mrapids analyze --operation {}
```

## Integration with Other Commands

### Analyze → List → Run
```bash
# 1. Analyze API
mrapids analyze

# 2. List what was generated
mrapids list requests

# 3. Run examples
mrapids run requests/examples/get-balance.yaml
```

### Analyze → Show → Customize
```bash
# 1. Analyze operation
mrapids analyze --operation CreateSubscription

# 2. Understand it better
mrapids show CreateSubscription

# 3. Customize generated example
vim requests/examples/create-subscription.yaml
```