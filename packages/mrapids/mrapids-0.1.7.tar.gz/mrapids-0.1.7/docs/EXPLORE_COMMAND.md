# Explore Command Guide

The `explore` command helps you discover API operations by searching through operation IDs, paths, and descriptions.

## Quick Start

```bash
# Search for payment-related operations
mrapids explore payment

# Search for customer operations
mrapids explore customer

# Case-insensitive search
mrapids explore INVOICE
```

## How It Works

The explore command searches through:
1. **Operation IDs** - e.g., `GetPaymentIntent`
2. **URL paths** - e.g., `/v1/payment_intents`
3. **Descriptions** - e.g., "Create a payment for a customer"
4. **Summaries** - Brief operation descriptions

Results are ranked by relevance and grouped for easy scanning.

## Search Examples

### Basic Search

```bash
mrapids explore payment
```

Output:
```
🔍 Exploring operations matching: payment

📌 OPERATION ID MATCHES:
  • GetPaymentIntents          GET    /v1/payment_intents
  • CreatePaymentIntent        POST   /v1/payment_intents
  • GetPaymentIntentsIntent    GET    /v1/payment_intents/{intent}
  • UpdatePaymentIntentsIntent POST   /v1/payment_intents/{intent}
  • GetPaymentMethods          GET    /v1/payment_methods

💡 PATH MATCHES:
  • GetPaymentLinks            GET    /v1/payment_links
  • PostPaymentLinksLink       POST   /v1/payment_links/{payment_link}

📝 DESCRIPTION MATCHES:
  • CaptureCharge              POST   /v1/charges/{charge}/capture
    "Capture a previously created charge"
```

### Detailed Search

```bash
mrapids explore subscription --detailed
```

Shows full descriptions for each match:
```
📝 DESCRIPTION MATCHES:
  • CreateSubscription         POST   /v1/subscriptions
    "Creates a new subscription for an existing customer. When you 
    create a subscription, the customer is signed up for a recurring 
    billing cycle."
```

### Limited Results

```bash
# Show only top 3 results per category
mrapids explore user --limit 3
```

## Command Options

### --spec / -s
Search in a different API spec:
```bash
mrapids explore payment --spec other-api.yaml
```

### --limit / -l
Control number of results per category:
```bash
# Show more results (default is 5)
mrapids explore customer --limit 10

# Show just top result per category
mrapids explore invoice --limit 1
```

### --detailed
Include full descriptions in output:
```bash
mrapids explore refund --detailed
```

### --format / -f
Change output format:

#### Pretty (default)
```bash
mrapids explore charge
```
Grouped, colored output for human reading

#### Simple
```bash
mrapids explore charge --format simple
```
Output:
```
GetCharges: List all charges
GetChargesCharge: Retrieve a charge
UpdateChargesCharge: Update a charge
CaptureChargesCharge: Capture a charge
```

#### JSON
```bash
mrapids explore charge --format json
```
```json
[
  {
    "operation_id": "GetCharges",
    "method": "GET",
    "path": "/v1/charges",
    "summary": "List all charges",
    "score": 100,
    "match_type": "operation_id"
  }
]
```

## Search Strategies

### 1. Broad to Specific

Start with general terms, then narrow down:
```bash
# Start broad
mrapids explore payment

# Find specific operation
mrapids explore "payment intent"

# Or use partial operation ID
mrapids explore createpayment
```

### 2. Use Domain Terms

Search using business domain language:
```bash
# E-commerce
mrapids explore order
mrapids explore cart
mrapids explore checkout

# SaaS
mrapids explore subscription
mrapids explore billing
mrapids explore usage

# Finance
mrapids explore invoice
mrapids explore refund
mrapids explore payout
```

### 3. HTTP Method Patterns

Common patterns to search for:
```bash
# CRUD operations
mrapids explore create
mrapids explore update
mrapids explore delete
mrapids explore list

# Actions
mrapids explore cancel
mrapids explore confirm
mrapids explore capture
```

## Practical Workflows

### Discovering Features

```bash
# What can I do with customers?
mrapids explore customer --limit 10

# Are there any webhook operations?
mrapids explore webhook

# How do I handle refunds?
mrapids explore refund --detailed
```

### Finding Exact Operations

```bash
# Step 1: Explore
mrapids explore subscription

# Step 2: Show details
mrapids show CreateSubscription

# Step 3: Run
mrapids run CreateSubscription --required-only --dry-run
```

### API Learning

```bash
# Understand payment flow
mrapids explore payment --detailed | less

# Find all list operations
mrapids explore list --format simple | grep "^Get"

# Find operations that might not need auth
mrapids explore public
mrapids explore health
mrapids explore status
```

## Combining with Other Commands

### Explore → List → Show → Run

```bash
# 1. Explore area of interest
mrapids explore invoice

# 2. List all invoice operations
mrapids list operations --filter invoice

# 3. Show specific operation
mrapids show CreateInvoice

# 4. Execute
mrapids run CreateInvoice --dry-run
```

### Script-Friendly Workflows

```bash
# Find all payment operations and save
mrapids explore payment --format json > payment-ops.json

# Process with jq
cat payment-ops.json | jq '.[] | select(.method == "POST") | .operation_id'

# Loop through results
mrapids explore refund --format simple | while read -r line; do
  op=$(echo "$line" | cut -d: -f1)
  echo "Checking $op..."
  mrapids show "$op" --format json | jq '.method'
done
```

## Tips

1. **Use simple terms** - "payment" not "payments"
2. **Try variations** - "auth", "authenticate", "authorization"
3. **Check descriptions** - `--detailed` reveals more matches
4. **Increase limits** - Default 5 might miss operations
5. **Use JSON for scripts** - Easier to parse than pretty output

## Advanced Usage

### Finding Patterns

```bash
# All operations with IDs in path
mrapids explore "{id}" --limit 20

# Operations that might be idempotent
mrapids explore idempotency

# Batch operations
mrapids explore batch
mrapids explore bulk
```

### Category-Specific Searches

```bash
# Pagination parameters
mrapids explore limit
mrapids explore page
mrapids explore cursor

# Filtering
mrapids explore filter
mrapids explore status
mrapids explore date

# Sorting
mrapids explore sort
mrapids explore order
```

### Discovering API Structure

```bash
# Find resource types
for resource in customer payment subscription invoice order; do
  echo "=== $resource ==="
  mrapids explore $resource --format simple | wc -l
done

# Find common prefixes
mrapids list operations --format json | \
  jq -r '.[].operation_id' | \
  cut -d_ -f1 | \
  sort | uniq -c | sort -nr
```

## Troubleshooting

### No results found
```bash
# Try simpler terms
mrapids explore pay     # instead of "payment"

# Try related terms  
mrapids explore charge  # instead of "payment"

# Check available operations
mrapids list operations | grep -i yourterm
```

### Too many results
```bash
# Be more specific
mrapids explore "create payment"

# Use operation ID patterns
mrapids explore "^Create"  # Operations starting with Create

# Limit results
mrapids explore payment --limit 3
```

### Understanding matches
```bash
# Use detailed mode to see why something matched
mrapids explore transfer --detailed

# Check JSON for match scores
mrapids explore transfer --format json | jq '.[] | {operation_id, score, match_type}'
```