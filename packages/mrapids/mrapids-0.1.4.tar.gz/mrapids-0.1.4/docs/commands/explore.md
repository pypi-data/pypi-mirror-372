# mrapids explore

Search for API operations using intelligent keyword matching across operation IDs, paths, summaries, descriptions, and tags.

## Synopsis

```bash
mrapids explore <KEYWORD> [OPTIONS]
```

## Description

The `explore` command provides Google-like search capabilities for OpenAPI specifications, helping developers quickly find the right endpoint without knowing its exact name. It uses fuzzy matching and relevance scoring to surface the most appropriate operations.

## Arguments

### `<KEYWORD>`
The search term or phrase to look for. Use quotes for multi-word searches.

Examples:
- `payment` - Find payment-related operations
- `"reset password"` - Find password reset endpoints
- `user` - Find user management operations

## Options

### `-s, --spec <PATH>`
Path to the OpenAPI specification file. If not provided, the command searches for specs in common locations:
- `specs/api.yaml`
- `specs/api.yml`
- `specs/api.json`
- `api.yaml`
- `openapi.yaml`

### `-l, --limit <NUMBER>`
Maximum number of results to show per relevance category.
- Default: `5`
- Use higher values to see more results

### `--detailed`
Show full descriptions and additional context for each result. Useful when learning a new API.

### `-f, --format <FORMAT>`
Output format for results:
- `pretty` (default): Human-readable with colors and grouping
- `simple`: Plain text, one operation per line
- `json`: Machine-readable JSON format

## Search Algorithm

The explore command searches across multiple fields with weighted relevance:

1. **Operation ID** (100% weight) - Direct matches score highest
2. **Path** (90% weight) - URL path matches
3. **Summary** (70% weight) - Short descriptions
4. **Tags** (60% weight) - API categories
5. **Description** (50% weight) - Detailed descriptions

## Output Formats

### Pretty Format (Default)
Groups results by relevance with visual indicators:
```
🔍 Exploring operations matching: payment

📌 Exact Matches (2)
  • CreatePayment - POST /payments
    Create a new payment transaction
    
🎯 Strong Matches (3)
  • ListPaymentMethods - GET /payment-methods
    Retrieve available payment methods
```

### Simple Format
One operation per line, scriptable:
```
CreatePayment POST /payments
GetPaymentStatus GET /payments/{id}/status
ListPaymentMethods GET /payment-methods
```

### JSON Format
Structured data with metadata:
```json
{
  "keyword": "payment",
  "total_results": 5,
  "results": [
    {
      "operation_id": "CreatePayment",
      "method": "POST",
      "path": "/payments",
      "summary": "Create a new payment",
      "score": 100,
      "matched_fields": ["operation_id", "path"]
    }
  ]
}
```

## Examples

### Basic Search
```bash
# Find user operations
mrapids explore user

# Find authentication endpoints
mrapids explore auth

# Search with phrases
mrapids explore "password reset"
```

### Advanced Usage
```bash
# Show more results
mrapids explore payment --limit 20

# Include full descriptions
mrapids explore subscription --detailed

# Use specific spec file
mrapids explore order --spec ./v2/api.yaml

# Get scriptable output
mrapids explore customer --format simple
```

### Integration Examples
```bash
# Find all POST operations
mrapids explore "" --format json | jq '.results[] | select(.method == "POST")'

# Count operations by keyword
mrapids explore user --format simple | wc -l

# Generate operation list
mrapids explore "" --format json > all-operations.json

# Find and run an operation
op=$(mrapids explore "list users" --format simple | head -1 | awk '{print $1}')
mrapids run "$op"
```

## Use Cases

### 1. Feature Development
```bash
# Building checkout flow
mrapids explore payment
mrapids explore order
mrapids explore shipping
```

### 2. API Learning
```bash
# Understand API structure
mrapids explore "" --detailed --limit 20

# Find authentication flow
mrapids explore auth --detailed
```

### 3. Debugging
```bash
# Find related endpoints
mrapids explore subscription
mrapids explore webhook
```

### 4. Documentation
```bash
# Generate endpoint inventory
mrapids explore "" --format json | \
  jq -r '.results[] | "\(.method) \(.path) - \(.summary)"' > endpoints.txt
```

## Tips

1. **Start broad**: Search for concepts rather than exact names
2. **Use quotes**: For multi-word searches like "create user"
3. **Try variations**: `auth`, `authenticate`, `authorization`
4. **Explore categories**: Search for `list`, `create`, `update`, `delete`
5. **Check related**: Found `GetUser`? Try `mrapids explore user` for all user ops

## Performance

- Small APIs (<100 operations): <10ms
- Medium APIs (100-500 operations): <20ms  
- Large APIs (500+ operations): <50ms

## Exit Codes

- `0`: Success, results found
- `0`: Success, no results found (not an error)
- `1`: Error (invalid spec, file not found, etc.)

## See Also

- `mrapids show` - Display detailed operation information
- `mrapids run` - Execute an operation after finding it
- `mrapids list` - List all operations without search