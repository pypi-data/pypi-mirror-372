# Reference Handling Quick Start Guide

## What's New?

MicroRapid now fully supports OpenAPI specifications with `$ref` references! This means you can work with complex, real-world API specs from GitHub, Stripe, OpenAI, and more.

## Quick Examples

### 1. Working with GitHub's API

```bash
# Download GitHub's OpenAPI spec
curl -o github-api.yaml https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.yaml

# Generate a curl script with all endpoints
mrapids setup-tests github-api.yaml --format curl -o github-api.sh

# Validate the specification
mrapids validate github-api.yaml

# Create a flattened version (all refs resolved)
mrapids flatten github-api.yaml -o github-flat.yaml
```

### 2. Your API with References

Before (this would fail):
```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      parameters:
        - $ref: '#/components/parameters/limitParam'
        - $ref: '#/components/parameters/pageParam'
      responses:
        '200':
          $ref: '#/components/responses/UserListResponse'
components:
  parameters:
    limitParam:
      name: limit
      in: query
      schema:
        type: integer
        default: 10
    pageParam:
      name: page
      in: query
      schema:
        type: integer
        default: 1
  responses:
    UserListResponse:
      description: List of users
      content:
        application/json:
          schema:
            type: array
            items:
              $ref: '#/components/schemas/User'
```

Now it works perfectly with all commands! ✅

## New Commands

### `mrapids flatten`

Resolve all references in your spec:

```bash
# Basic usage - outputs to stdout
mrapids flatten api.yaml

# Save to file
mrapids flatten api.yaml -o resolved-api.yaml

# Output as JSON
mrapids flatten api.yaml -f json

# Keep unused components
mrapids flatten api.yaml --include-unused
```

**Use cases:**
- Debugging reference issues
- Creating standalone spec files
- Preparing specs for tools that don't support references
- Inspecting what references resolve to

### `mrapids validate`

Comprehensive validation with reference checking:

```bash
# Basic validation
mrapids validate api.yaml

# Strict mode - warnings become errors
mrapids validate api.yaml --strict

# Machine-readable output
mrapids validate api.yaml -f json

# Use in CI/CD
if mrapids validate api.yaml --strict -f json > /dev/null; then
  echo "✅ API spec is valid"
else
  echo "❌ API spec has issues"
  exit 1
fi
```

**What it checks:**
- ✓ All references resolve correctly
- ✓ Required fields are present
- ✓ No duplicate parameter names
- ✓ Path parameters match URL templates
- ✓ Valid parameter locations
- ✓ At least one response defined
- ✓ Unused components (warnings)

## Common Reference Patterns

### 1. Shared Parameters

```yaml
paths:
  /users:
    get:
      parameters:
        - $ref: '#/components/parameters/limitParam'
        - $ref: '#/components/parameters/offsetParam'
  /posts:
    get:
      parameters:
        - $ref: '#/components/parameters/limitParam'
        - $ref: '#/components/parameters/offsetParam'
```

### 2. Common Responses

```yaml
paths:
  /users/{id}:
    get:
      responses:
        '404':
          $ref: '#/components/responses/NotFound'
        '401':
          $ref: '#/components/responses/Unauthorized'
```

### 3. Reusable Schemas

```yaml
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        profile:
          $ref: '#/components/schemas/UserProfile'
    UserProfile:
      type: object
      properties:
        name:
          type: string
        email:
          type: string
```

## Working with Large Specs

For large API specs like GitHub's (700+ operations):

```bash
# First, analyze what's available
mrapids list github-api.yaml | head -20

# Search for specific operations
mrapids explore github-api.yaml "pull request"

# Generate examples for specific operations
mrapids analyze github-api.yaml --operation "pulls/create"

# Setup Tests just what you need
mrapids setup-tests github-api.yaml --format npm
# Then use: npm run api:pulls/create
```

## Troubleshooting

### "missing field 'name'" Error

**Old behavior**: Parser would fail
**New behavior**: References are properly resolved

### Validation Warnings

```bash
# See what's unused in your spec
mrapids validate api.yaml

# Example output:
⚠️  Warnings: Found 3 warning(s):
   • components.parameters.sortParam - Parameter is defined but never used
   • components.schemas.Error - Schema is defined but never used
```

### Complex Reference Chains

If you have references pointing to other references:

```yaml
# This works now!
parameters:
  - $ref: '#/components/parameters/CommonParam'
components:
  parameters:
    CommonParam:
      $ref: '#/components/parameters/BaseParam'
    BaseParam:
      name: filter
      in: query
```

## Performance Tips

1. **Caching**: The parser caches resolved references - repeated operations are fast
2. **Large Specs**: All commands work efficiently even with 8MB+ specs
3. **Validation**: Use JSON output in CI/CD for faster parsing

## Integration Examples

### CI/CD Pipeline

```yaml
# .github/workflows/api-validation.yml
- name: Validate API Spec
  run: |
    npm install -g mrapids
    mrapids validate api/openapi.yaml --strict
    
- name: Generate SDK
  run: |
    mrapids flatten api/openapi.yaml -o api/resolved.yaml
    mrapids generate api/resolved.yaml --target typescript
```

### Pre-commit Hook

```bash
#!/bin/sh
# .git/hooks/pre-commit

# Validate any changed OpenAPI specs
for file in $(git diff --cached --name-only | grep -E '\.(yaml|yml|json)$'); do
  if grep -q "openapi:" "$file" 2>/dev/null; then
    echo "Validating $file..."
    mrapids validate "$file" --strict || exit 1
  fi
done
```

### Docker Integration

```dockerfile
FROM node:18-alpine
RUN npm install -g mrapids

# Validate and prepare spec
COPY api.yaml .
RUN mrapids validate api.yaml --strict
RUN mrapids flatten api.yaml -o resolved.yaml

# Use resolved spec for code generation
RUN mrapids generate resolved.yaml --target typescript
```

## Best Practices

1. **Always Validate**: Run `mrapids validate` before committing
2. **Use References**: DRY principle - reuse common components
3. **Document References**: Add descriptions to shared components
4. **Flatten for Distribution**: When sharing specs with external tools
5. **Cache Specs Locally**: Download remote specs for faster development

## What's Next?

The reference-aware parser sets the foundation for:
- 🔄 Circular reference detection (coming soon)
- 🌐 External file references (planned)
- 📊 Reference usage analytics
- 🔍 Smart reference refactoring

Happy API development! 🚀