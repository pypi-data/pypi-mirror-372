# Explore Command Documentation

## Overview

The `mrapids explore` command is an intelligent API operation search tool that helps developers quickly find the right endpoint in large API specifications. It uses smart fuzzy matching and relevance scoring to surface the most relevant operations based on your search query.

## Value Proposition

### 🔍 **Find Operations Instantly**
- **Save Time**: No more scrolling through hundreds of endpoints
- **Reduce Errors**: Find the exact operation you need, not a similar one
- **Improve Productivity**: Spend less time searching, more time building

### 💡 **Smart Search Capabilities**
- **Multi-field Search**: Searches across operation IDs, paths, summaries, descriptions, and tags
- **Fuzzy Matching**: Handles typos and partial matches
- **Relevance Scoring**: Most relevant results appear first
- **Contextual Results**: Shows why each result matched

### 🚀 **Developer Experience**
- **Zero Learning Curve**: Just type what you're looking for
- **Multiple Output Formats**: Human-readable, scriptable, or JSON
- **Works Offline**: No internet connection required
- **Lightning Fast**: Results in milliseconds

## Purpose

The explore command addresses common pain points in API development:

### 1. **Large API Navigation**
Modern APIs can have hundreds of endpoints. Finding the right one shouldn't require:
- Opening the spec in an editor
- Using Ctrl+F repeatedly
- Remembering exact operation names
- Browsing through Swagger UI

### 2. **Discovery During Development**
When building applications, developers need to:
- Find operations for specific features
- Discover related endpoints
- Understand API capabilities
- Locate operations by concept, not exact name

### 3. **Onboarding New Team Members**
New developers can explore the API naturally:
- Search by business concepts
- Discover API patterns
- Learn endpoint naming conventions
- Find examples quickly

## Features

### 🎯 **Intelligent Matching**

The explore command uses a sophisticated scoring algorithm:

1. **Exact Matches** (Score: 100)
   - Operation ID exact match
   - Path exact match

2. **Strong Matches** (Score: 80-90)
   - Operation ID contains keyword
   - Path segment matches

3. **Good Matches** (Score: 60-70)
   - Summary contains keyword
   - Tag matches

4. **Relevant Matches** (Score: 40-50)
   - Description contains keyword
   - Parameter names match

### 📊 **Output Formats**

#### Pretty Format (Default)
```
🔍 Exploring operations matching: payment

📌 Exact Matches (2)
  • CreatePayment - POST /payments
    Create a new payment transaction
    
  • GetPaymentStatus - GET /payments/{id}/status
    Check payment processing status

🎯 Strong Matches (3)
  • ListPaymentMethods - GET /payment-methods
    Retrieve available payment methods
    
  • UpdatePaymentMethod - PUT /payment-methods/{id}
    Update customer payment method
```

#### Simple Format
```
CreatePayment POST /payments
GetPaymentStatus GET /payments/{id}/status
ListPaymentMethods GET /payment-methods
UpdatePaymentMethod PUT /payment-methods/{id}
```

#### JSON Format
```json
{
  "keyword": "payment",
  "total_results": 5,
  "results": [
    {
      "operation_id": "CreatePayment",
      "method": "POST",
      "path": "/payments",
      "summary": "Create a new payment transaction",
      "score": 100,
      "matched_fields": ["operation_id", "path"]
    }
  ]
}
```

## Real-World Use Cases

### Use Case 1: Feature Development
**Scenario**: Building a checkout flow

```bash
# Find all payment-related operations
mrapids explore payment

# Find order operations
mrapids explore order

# Find shipping operations
mrapids explore shipping
```

**Value**: Quickly discover all endpoints needed for the feature

### Use Case 2: Debugging
**Scenario**: Customer reports issue with subscription

```bash
# Find subscription endpoints
mrapids explore subscription --detailed

# Look for webhook operations
mrapids explore webhook

# Find customer-related operations
mrapids explore customer
```

**Value**: Rapidly locate relevant endpoints for investigation

### Use Case 3: API Integration
**Scenario**: Third-party integration

```bash
# Discover authentication endpoints
mrapids explore auth

# Find rate limit information
mrapids explore "rate limit" --detailed

# Explore available webhooks
mrapids explore webhook --format json | jq '.results[].path'
```

**Value**: Understand API capabilities without documentation

## Usage Examples

### Basic Search
```bash
# Search for user operations
mrapids explore user

# Search for authentication
mrapids explore auth

# Search for specific features
mrapids explore "reset password"
```

### Advanced Search
```bash
# Show more results
mrapids explore payment --limit 20

# Include descriptions for context
mrapids explore subscription --detailed

# Use specific spec file
mrapids explore customer --spec ./v2/api.yaml

# Get scriptable output
mrapids explore order --format simple | grep POST
```

### Integration Examples
```bash
# Find all POST operations
mrapids explore "" --format json | jq '.results[] | select(.method == "POST")'

# List all operations with "create" in name
mrapids explore create --format simple | awk '{print $1}'

# Generate operation list for documentation
mrapids explore "" --format json > operations.json
```

## Search Algorithm

The explore command uses a multi-stage search process:

1. **Tokenization**
   - Splits search query into tokens
   - Handles camelCase and snake_case
   - Recognizes common API terms

2. **Field Weighting**
   - Operation ID: 100% weight
   - Path: 90% weight
   - Summary: 70% weight
   - Tags: 60% weight
   - Description: 50% weight

3. **Fuzzy Matching**
   - Handles typos (paymnt → payment)
   - Partial matches (pay → payment)
   - Case insensitive

4. **Result Grouping**
   - Groups by relevance score
   - Sorts within groups
   - Limits results per group

## Performance

The explore command is optimized for speed:
- **Small APIs (<100 operations)**: <10ms
- **Medium APIs (100-500 operations)**: <20ms
- **Large APIs (500+ operations)**: <50ms

## Best Practices

### 1. **Start Broad, Then Narrow**
```bash
# Start with concept
mrapids explore payment

# Then get specific
mrapids explore "payment refund"
```

### 2. **Use Detailed Mode for Learning**
```bash
# When learning a new API
mrapids explore user --detailed --limit 10
```

### 3. **Combine with Other Commands**
```bash
# Explore, then show details
mrapids explore subscription --format simple
mrapids show CancelSubscription

# Explore, then run
mrapids explore "list users" --format simple
mrapids run ListUsers --limit 10
```

### 4. **Script Integration**
```bash
# Find and test all GET operations
for op in $(mrapids explore "" --format json | jq -r '.results[] | select(.method == "GET") | .operation_id'); do
    echo "Testing $op"
    mrapids run "$op" --dry-run
done
```

## Tips and Tricks

1. **Use Quotes for Phrases**
   ```bash
   mrapids explore "reset password"
   ```

2. **Explore by HTTP Method**
   ```bash
   mrapids explore GET --format simple | grep "/users"
   ```

3. **Find Deprecated Operations**
   ```bash
   mrapids explore deprecated --detailed
   ```

4. **Discover API Patterns**
   ```bash
   # Find all list operations
   mrapids explore list
   
   # Find all delete operations
   mrapids explore delete
   ```

## Future Enhancements

Planned improvements include:
- Regular expression support
- Search history
- Saved searches
- Operation categories
- API version awareness
- Search suggestions
- Natural language queries

## Conclusion

The `mrapids explore` command transforms how developers interact with API specifications. Instead of treating specs as static documents, it makes them searchable, discoverable, and accessible. This leads to faster development, fewer errors, and a better developer experience overall.