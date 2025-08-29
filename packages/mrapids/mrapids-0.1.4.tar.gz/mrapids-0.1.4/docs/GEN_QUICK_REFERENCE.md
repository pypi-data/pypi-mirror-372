# MicroRapid `gen` Command Quick Reference

## Command Overview

```bash
mrapids gen <subcommand> [options]
```

## Subcommands at a Glance

| Command | Purpose | Replaces |
|---------|---------|----------|
| `gen snippets` | Generate example requests/responses | `analyze` |
| `gen sdk` | Generate client libraries | `sdk` |
| `gen stubs` | Generate server boilerplate | `generate` |
| `gen fixtures` | Generate test data *(coming soon)* | *(new)* |

## Quick Examples

### Generate Everything
```bash
# Generate all examples
mrapids gen snippets

# Generate TypeScript SDK
mrapids gen sdk -l typescript

# Generate Express.js server
mrapids gen stubs --framework express
```

### Common Workflows

#### 1. API Testing Workflow
```bash
# Generate examples
mrapids gen snippets

# Test an endpoint
mrapids run create-user

# Generate cURL commands
mrapids gen snippets --format curl
```

#### 2. SDK Development
```bash
# TypeScript SDK with custom name
mrapids gen sdk -l typescript --package @mycompany/api-client

# Python SDK
mrapids gen sdk -l python -o ./python-sdk

# Go SDK
mrapids gen sdk -l go --package github.com/mycompany/api-go
```

#### 3. Server Implementation
```bash
# Express.js with validation
mrapids gen stubs --framework express --with-validation

# FastAPI with tests
mrapids gen stubs --framework fastapi --with-tests

# Custom output
mrapids gen stubs -o ./backend
```

## Options Reference

### `gen snippets`
```bash
-o, --output <DIR>           # Output directory (default: ./examples)
--operation <ID>             # Specific operation only
--format <FORMAT>            # json, yaml, curl, httpie, all
--curl                       # Include cURL examples
--httpie                     # Include HTTPie examples
```

### `gen sdk`
```bash
-l, --language <LANG>        # typescript, python, go, rust
-o, --output <DIR>           # Output directory
--package <NAME>             # Package/module name
--docs <BOOL>                # Include documentation (default: true)
--examples <BOOL>            # Include examples (default: true)
```

### `gen stubs`
```bash
-f, --framework <NAME>       # express, fastapi, gin, etc.
-o, --output <DIR>           # Output directory
--with-tests                 # Include test stubs
--with-validation            # Include validation middleware
```

### `gen fixtures` *(planned)*
```bash
-o, --output <DIR>           # Output directory
--count <N>                  # Records per schema (default: 10)
--schema <NAME>              # Specific schemas only
--format <TYPE>              # json, yaml, csv, sql
--seed <N>                   # Random seed
```

## Output Structure

### Snippets Output
```
examples/
├── requests/
│   └── examples/
│       ├── get-users.yaml
│       ├── create-user.yaml
│       └── update-user.yaml
└── data/
    └── examples/
        ├── create-user.json
        └── update-user.json
```

### SDK Output
```
sdk-typescript/
├── src/
│   ├── client.ts
│   ├── models.ts
│   ├── types.ts
│   └── index.ts
├── package.json
├── tsconfig.json
└── README.md
```

### Stubs Output
```
generated/
├── src/
│   ├── routes/
│   ├── handlers/
│   ├── models/
│   ├── middleware/
│   └── app.ts
├── tests/
└── package.json
```

## Language/Framework Support

### SDK Languages
- **TypeScript** - Fetch API, full types, tree-shakeable
- **Python** - httpx, type hints, async/sync
- **Go** - net/http, context support
- **Rust** - *(coming soon)*

### Server Frameworks
- **Express.js** - Node.js/TypeScript
- **FastAPI** - Python async
- **Gin** - Go
- More coming soon...

## Pro Tips

### 1. Regenerate After API Changes
```bash
# Validate first
mrapids validate specs/api.yaml

# Then regenerate all
mrapids gen snippets && mrapids gen sdk -l typescript
```

### 2. Use in CI/CD
```yaml
# GitHub Actions example
- name: Generate API artifacts
  run: |
    mrapids gen snippets
    mrapids gen sdk -l typescript -o ./sdk
    mrapids gen stubs --framework express -o ./server
```

### 3. Custom Templates
```bash
# Use custom output directories
mrapids gen snippets -o ./test-data
mrapids gen sdk -l python -o ./clients/python
mrapids gen stubs -o ./backend/generated
```

### 4. Specific Operations
```bash
# Generate only what you need
mrapids gen snippets --operation createUser
mrapids gen snippets --operation updateUser
```

### 5. Multiple Formats
```bash
# Generate all formats at once
mrapids gen snippets --format all

# Or specific combinations
mrapids gen snippets --curl --httpie
```

## Common Patterns

### Full Stack Development
```bash
# 1. Backend
mrapids gen stubs --framework express --with-validation

# 2. Frontend SDKs
mrapids gen sdk -l typescript -o ./frontend/src/api

# 3. Mobile SDKs  
mrapids gen sdk -l swift -o ./ios/API
mrapids gen sdk -l kotlin -o ./android/api

# 4. Testing
mrapids gen snippets --format all
mrapids gen fixtures --count 1000
```

### Microservices
```bash
# For each service
for service in users orders payments; do
  mrapids gen stubs specs/$service.yaml -o ./services/$service
  mrapids gen sdk specs/$service.yaml -l go -o ./services/$service/client
done
```

### Documentation
```bash
# Generate all examples for docs
mrapids gen snippets --format all -o ./docs/examples

# Generate SDK examples
mrapids gen sdk -l typescript --examples true
mrapids gen sdk -l python --examples true
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No API specification found" | Specify path: `mrapids gen snippets specs/api.yaml` |
| "Operation not found" | Check with: `mrapids list operations` |
| "Invalid specification" | Validate: `mrapids validate specs/api.yaml` |
| Generated code errors | Ensure spec is valid and complete |

## See Also
- [Full Gen Command Guide](./GEN_COMMAND_GUIDE.md)
- [OpenAPI Best Practices](./OPENAPI_BEST_PRACTICES.md)
- [MicroRapid CLI Reference](./CLI_REFERENCE.md)