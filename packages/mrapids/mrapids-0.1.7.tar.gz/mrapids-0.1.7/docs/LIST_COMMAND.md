# List Command Guide

The `list` command provides a quick overview of available operations and saved request configurations.

## Quick Start

```bash
# List all operations
mrapids list operations

# List GET operations only
mrapids list operations --method GET

# List operations with "customer" in the name
mrapids list operations --filter customer

# List saved request configs
mrapids list requests
```

## Listing Operations

### Basic Usage

```bash
mrapids list operations
```

Output:
```
📋 API Operations

 #  │ Operation ID           │ Method │ Path                           │ Example
────┼────────────────────────┼────────┼────────────────────────────────┼─────────────────────
 1  │ GetAccount             │ GET    │ /v1/account                    │ mrapids run get-account
 2  │ GetAccounts            │ GET    │ /v1/accounts                   │ mrapids run get-accounts
 3  │ CreateAccount          │ POST   │ /v1/accounts                   │ mrapids run create-account
 4  │ GetAccountsAccount     │ GET    │ /v1/accounts/{account}         │ mrapids run get-accounts-account --id acc_123
 5  │ UpdateAccountsAccount  │ POST   │ /v1/accounts/{account}         │ mrapids run update-accounts-account --id acc_123

Showing 5 of 500 operations
Use filters to narrow results: --method POST --filter customer --tag "Payment Methods"
```

### Filtering

#### By HTTP Method
```bash
# Only GET operations
mrapids list operations --method GET

# Only POST operations  
mrapids list operations --method POST

# DELETE operations
mrapids list operations --method DELETE
```

#### By Text
```bash
# Operations containing "customer"
mrapids list operations --filter customer

# Case-insensitive
mrapids list operations --filter INVOICE

# Multiple words (matches any)
mrapids list operations --filter "payment charge"
```

#### By Tag
```bash
# Operations tagged as "Payment Methods"
mrapids list operations --tag "Payment Methods"

# List available tags first
mrapids list operations --format json | jq -r '.[].tags[]' | sort | uniq
```

#### Combined Filters
```bash
# POST operations with "customer"
mrapids list operations --method POST --filter customer

# GET operations in "Billing" tag
mrapids list operations --method GET --tag Billing
```

### Output Formats

#### Table (Default)
```bash
mrapids list operations
```
- Colored, formatted table
- Shows operation ID, method, path, and example
- Best for human reading

#### Simple
```bash
mrapids list operations --format simple
```
Output:
```
GetAccount GET /v1/account
GetAccounts GET /v1/accounts
CreateAccount POST /v1/accounts
```
- One operation per line
- Good for scripting
- Format: `OperationID METHOD /path`

#### JSON
```bash
mrapids list operations --format json
```
```json
[
  {
    "operation_id": "GetAccount",
    "method": "GET",
    "path": "/v1/account",
    "summary": "Retrieve account details",
    "tags": ["Account"],
    "has_parameters": true,
    "requires_auth": true
  }
]
```
- Full operation details
- Machine-readable
- Includes tags, auth requirements

#### YAML
```bash
mrapids list operations --format yaml
```
```yaml
- operation_id: GetAccount
  method: GET
  path: /v1/account
  summary: Retrieve account details
  tags:
    - Account
```

## Listing Requests

### Basic Usage

```bash
mrapids list requests
```

Shows saved request configurations in `requests/` directory:
```
📁 Saved Request Configurations

 File                              │ Operation          │ Method │ Path
───────────────────────────────────┼────────────────────┼────────┼─────────────────
 create-customer.yaml              │ CreateCustomer     │ POST   │ /v1/customers
 get-balance.yaml                  │ GetBalance         │ GET    │ /v1/balance
 create-payment-intent.yaml        │ CreatePaymentIntent│ POST   │ /v1/payment_intents

Found 3 request configurations
Run with: mrapids run requests/create-customer.yaml
```

### Filtering Requests

```bash
# Filter by filename or content
mrapids list requests --filter customer

# By method
mrapids list requests --method POST
```

## Practical Use Cases

### 1. API Discovery

```bash
# What can I do with customers?
mrapids list operations --filter customer

# What resources can I create?
mrapids list operations --method POST | grep -i create

# What can I delete?
mrapids list operations --method DELETE
```

### 2. Finding Specific Operations

```bash
# Find exact operation
mrapids list operations | grep -i webhook

# Find by path pattern
mrapids list operations --format simple | grep "/v1/customers/"

# Find by tag
mrapids list operations --tag "Core Resources"
```

### 3. Scripting

```bash
# Count operations by method
mrapids list operations --format json | \
  jq -r '.[] | .method' | sort | uniq -c

# List all unique paths
mrapids list operations --format json | \
  jq -r '.[] | .path' | sort | uniq

# Find operations without auth
mrapids list operations --format json | \
  jq '.[] | select(.requires_auth == false)'
```

### 4. Documentation Generation

```bash
# Generate markdown table of operations
echo "| Operation | Method | Path |"
echo "|-----------|--------|------|"
mrapids list operations --format simple | while read -r line; do
  op=$(echo "$line" | cut -d' ' -f1)
  method=$(echo "$line" | cut -d' ' -f2)
  path=$(echo "$line" | cut -d' ' -f3-)
  echo "| $op | $method | $path |"
done
```

## Tips & Tricks

### Quick Operation Lookup

```bash
# Alias for quick searching
alias mfind='mrapids list operations --filter'

# Usage
mfind payment
mfind customer --method POST
```

### Pagination Helpers

```bash
# Find operations that support pagination
mrapids list operations --format json | \
  jq '.[] | select(.has_parameters == true) | select(.path | contains("s}")) | .operation_id' | \
  grep -E "^Get|^List"
```

### API Statistics

```bash
# Total operations
mrapids list operations --format json | jq length

# Operations by method
mrapids list operations --format json | \
  jq -r '.[] | .method' | sort | uniq -c | sort -nr

# Most common tags
mrapids list operations --format json | \
  jq -r '.[] | .tags[]' | sort | uniq -c | sort -nr
```

## Integration with Other Commands

### List → Show → Run Workflow

```bash
# 1. Find operation
mrapids list operations --filter refund

# 2. Get details
mrapids show CreateRefund

# 3. Execute
mrapids run CreateRefund --charge ch_123 --amount 500
```

### Bulk Operations

```bash
# Test all GET operations
mrapids list operations --method GET --format simple | \
  cut -d' ' -f1 | \
  while read -r op; do
    echo "Testing $op..."
    mrapids run "$op" --dry-run
  done
```

## Advanced Filtering

### Using jq for Complex Queries

```bash
# Operations with specific parameter
mrapids list operations --format json | \
  jq '.[] | select(.path | contains("{id}"))'

# POST operations without "Create" in name
mrapids list operations --format json | \
  jq '.[] | select(.method == "POST") | select(.operation_id | contains("Create") | not)'

# Operations in multiple tags
mrapids list operations --format json | \
  jq '.[] | select(.tags | map(. == "Billing" or . == "Payments") | any)'
```

## Output Customization

### For Reports

```bash
# CSV output
echo "Operation,Method,Path,Auth Required" > operations.csv
mrapids list operations --format json | \
  jq -r '.[] | [.operation_id, .method, .path, .requires_auth] | @csv' >> operations.csv
```

### For Documentation

```bash
# Group by tag
mrapids list operations --format json | \
  jq -r 'group_by(.tags[0]) | .[] | "\n## \(.[0].tags[0])\n" + (map("- `\(.operation_id)` - \(.method) \(.path)") | join("\n"))'
```

## Troubleshooting

### No operations found
```bash
# Check spec file location
mrapids list operations --spec ./path/to/api.yaml

# Verify spec is loaded
mrapids analyze
```

### Filters not working
```bash
# Check exact text in operations
mrapids list operations --format json | jq '.[] | .operation_id' | grep -i yourterm

# Try broader search
mrapids list operations --filter pay  # instead of "payment"
```

### Performance with large APIs
```bash
# Use simple format for faster output
mrapids list operations --format simple

# Filter at source
mrapids list operations --method GET --format simple
```