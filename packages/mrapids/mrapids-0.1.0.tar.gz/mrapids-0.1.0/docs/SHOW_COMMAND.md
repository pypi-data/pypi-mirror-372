# Show Command Guide

The `show` command displays detailed information about API operations, helping you understand what parameters are needed and what responses to expect.

## Quick Start

```bash
# Show operation details
mrapids show GetBalance

# Partial matching works
mrapids show balance

# Show with examples
mrapids show CreateCustomer --examples
```

## Features

### 1. Smart Operation Matching

The command uses fuzzy matching to find operations:

```bash
# These all work for "GetCustomersCustomer":
mrapids show GetCustomersCustomer  # Exact
mrapids show getcustomerscustomer  # Case-insensitive
mrapids show customer              # Partial match
mrapids show get-customer          # With dashes
```

### 2. Comprehensive Operation Details

The output includes everything you need to know:

```
🎯 Operation: GetWebhookEndpoints
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 Summary: List all webhook endpoints

🔧 Details:
  Method:      GET
  Path:        /v1/webhook_endpoints
  Operation ID: GetWebhookEndpoints

🔐 Authentication:
  ✓ Bearer Token (HTTP Bearer)

📥 QUERY PARAMETERS:
  ○ ending_before         string
      → ?ending_before=we_1NtGrtLkdIwHu7ixUpYHsDnU

  ○ expand                array
      → ?expand[]=string

  ✓ limit                 integer    [Pagination]
      → ?limit=10
      Maximum items to return (1-100)
```

### 3. Parameter Categories

Parameters are clearly organized by type:

#### Path Parameters
```
📍 PATH PARAMETERS:
  ✓ id                    string
      → /v1/customers/{id}
      The customer ID
```

#### Query Parameters
```
📥 QUERY PARAMETERS:
  ✓ limit                 integer    [Pagination]
      → ?limit=20
      
  ○ status                string     [Filtering]
      → ?status=active
```

#### Header Parameters
```
📤 HEADER PARAMETERS:
  ○ Stripe-Version        string
      → Stripe-Version: 2023-10-16
```

### 4. Request Body Schema

For POST/PUT/PATCH operations:

```
📦 REQUEST BODY: (application/json)

Required fields:
  • email                 string
    Example: "user@example.com"
    
  • items                 array
    Example: [{"price": "price_1MowQULkdIwHu7ixraBm864M", "quantity": 1}]

Optional fields:
  • name                  string
    Example: "Jenny Rosen"
    
  • metadata              object
    Example: {"order_id": "6735"}
```

### 5. Authentication Display

Shows required authentication from OpenAPI spec:

```
🔐 Authentication:
  ✓ Bearer Token (HTTP Bearer)
  
  OR
  
  ✓ Basic Auth (HTTP Basic)
  Username and password required
```

### 6. Smart Examples

Examples are generated based on field names:

- `email` → `"user@example.com"`
- `phone` → `"+14155551234"`
- `amount` → `2000`
- `currency` → `"usd"`
- `created` → `1640995200`

## Command Options

### --spec
Use a different API specification:
```bash
mrapids show GetUser --spec other-api.yaml
```

### --examples
Show example requests:
```bash
mrapids show CreateCustomer --examples
```

### --format
Output in different formats:
```bash
# Human-readable (default)
mrapids show GetBalance --format pretty

# JSON (for processing)
mrapids show GetBalance --format json | jq '.parameters'

# YAML
mrapids show GetBalance --format yaml
```

## Understanding the Output

### Visual Indicators

- `✓` Required parameter
- `○` Optional parameter
- `[Tag]` Parameter purpose (Pagination, Filtering, etc.)
- `→` Usage example

### Parameter Types

```
string     # Text value
integer    # Whole number
number     # Decimal number
boolean    # true/false
array      # List of values
object     # Nested structure
```

### Usage Examples

Each parameter shows how to use it:

```
Query:  → ?limit=10
Path:   → /v1/customers/{id}
Header: → Authorization: Bearer sk_test_...
Body:   → {"email": "user@example.com"}
```

## Practical Examples

### Exploring an unfamiliar API

```bash
# 1. List all operations
mrapids list operations

# 2. Find payment operations
mrapids explore payment

# 3. Show details for creating a payment
mrapids show CreatePaymentIntent

# 4. Try it out
mrapids run CreatePaymentIntent --required-only --dry-run
```

### Understanding complex operations

```bash
# Show detailed info
mrapids show CreateSubscription

# See the request body structure
mrapids show CreateSubscription --format json | jq '.requestBody.content."application/json".schema'

# Check required fields
mrapids show CreateSubscription | grep -A 1 "Required fields:"
```

### Checking authentication

```bash
# See what auth is needed
mrapids show GetBalance | grep -A 3 "Authentication:"

# Operations that don't need auth
mrapids list operations --format json | jq '.[] | select(.security == null) | .operationId'
```

## Integration with Other Commands

The `show` command works seamlessly with others:

```bash
# Show then run
mrapids show CreateCustomer
mrapids run CreateCustomer --data '{"email":"test@example.com"}'

# Explore, show, run workflow
mrapids explore refund
mrapids show CreateRefund  
mrapids run CreateRefund --id ch_123 --amount 500
```

## Tips

1. **Use partial matching** - Don't type full operation names
2. **Check auth first** - See what credentials are needed
3. **Look for examples** - The `→` arrows show usage
4. **Note required fields** - Marked with `✓`
5. **Understand purposes** - Tags like `[Pagination]` explain parameter use

## Troubleshooting

### Operation not found
```bash
# List all operations to find exact name
mrapids list operations | grep -i customer

# Or use explore
mrapids explore customer
```

### No examples showing
```bash
# Make sure you analyzed the spec first
mrapids analyze

# Or use --examples flag
mrapids show CreateCustomer --examples
```

### Format issues
```bash
# For scripts, use JSON output
mrapids show GetBalance --format json

# For reading, use default pretty format
mrapids show GetBalance
```