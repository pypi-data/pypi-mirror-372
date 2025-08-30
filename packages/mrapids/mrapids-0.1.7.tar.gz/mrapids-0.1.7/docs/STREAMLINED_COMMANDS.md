# MicroRapid Streamlined Commands

> Simplified command structure with clear verbs and reduced overlap

## 🎯 Command Groups

### 📁 Projects
Manage projects and configuration

```bash
mrapids init                        # Scaffold a new project
mrapids config                      # View/edit configuration
mrapids cleanup                     # Remove temporary files
```

### 📋 Specs
Work with OpenAPI specifications

```bash
mrapids validate api.yaml           # Validate schema + rules
mrapids flatten api.yaml            # Dereference/flatten spec
mrapids diff old.yaml new.yaml      # Compare specifications
```

### 🔍 Discoverability
Explore and understand your API

```bash
mrapids list operations api.yaml    # List operations/components
mrapids show getUser api.yaml       # Show operation details
mrapids search "user" api.yaml      # Semantic keyword search
```

### 🚀 Execution & Quality
Run and test your API

```bash
mrapids run api.yaml --opId getUser         # Execute an operation
mrapids test api.yaml --all                 # Run tests from spec
mrapids tests init api.yaml                 # Generate test suite
```

### 🛠️ Generation
Generate code and examples

```bash
mrapids gen snippets api.yaml               # Request examples & curl
mrapids gen sdk api.yaml --lang typescript  # Generate SDK
mrapids gen stubs api.yaml --framework express  # Server stubs
mrapids gen fixtures api.yaml               # Sample payloads
```

### 🔐 Auth
Authentication management

```bash
mrapids auth login github           # OAuth login flow
mrapids auth logout github          # Remove credentials
mrapids auth status                 # Show auth profiles
```

## 📚 Detailed Command Reference

### Projects Commands

#### `init` - Scaffold a Project
```bash
# Create new project
mrapids init my-api

# From existing spec
mrapids init my-api --from https://api.example.com/openapi.json

# With template
mrapids init my-api --template rest-api
```

#### `config` - Configuration Management
```bash
# View current config
mrapids config

# Edit specific environment
mrapids config --env production

# Set configuration value
mrapids config set baseUrl https://api.prod.com --env production

# List all environments
mrapids config list
```

#### `cleanup` - Remove Artifacts
```bash
# Clean all temp files
mrapids cleanup

# Selective cleanup
mrapids cleanup --cache --logs

# Keep configuration
mrapids cleanup --all --keep-config

# Preview what will be deleted
mrapids cleanup --dry-run
```

### Specs Commands

#### `validate` - Comprehensive Validation
```bash
# Basic validation
mrapids validate api.yaml

# Strict mode (warnings as errors)
mrapids validate api.yaml --strict

# With linting rules
mrapids validate api.yaml --lint

# Custom rules
mrapids validate api.yaml --rules security.yaml

# Multiple specs
mrapids validate v1.yaml v2.yaml v3.yaml
```

#### `flatten` - Dereference Specifications
```bash
# Flatten all references
mrapids flatten api.yaml

# Save to file
mrapids flatten api.yaml --output flattened.yaml

# Include external refs
mrapids flatten api.yaml --resolve-external

# Include unused schemas
mrapids flatten api.yaml --include-unused
```

#### `diff` - Compare Specifications
```bash
# Basic comparison
mrapids diff v1.yaml v2.yaml

# Only breaking changes
mrapids diff v1.yaml v2.yaml --breaking

# Output formats
mrapids diff v1.yaml v2.yaml --format json
mrapids diff v1.yaml v2.yaml --format markdown

# Ignore descriptions
mrapids diff v1.yaml v2.yaml --ignore-descriptions
```

### Discoverability Commands

#### `list` - List API Components
```bash
# List all operations
mrapids list operations api.yaml

# Filter by method
mrapids list operations api.yaml --filter method=GET

# Filter by path pattern
mrapids list operations api.yaml --filter path=/users/*

# List schemas
mrapids list schemas api.yaml

# JSON output
mrapids list operations api.yaml --output json
```

#### `show` - Display Details
```bash
# Show operation
mrapids show getUser api.yaml

# Show schema
mrapids show User api.yaml --type schema

# Show with examples
mrapids show createUser api.yaml --examples

# Verbose output
mrapids show deleteUser api.yaml --verbose
```

#### `search` - Semantic Search
```bash
# Basic search
mrapids search "user" api.yaml

# Include descriptions
mrapids search "payment" api.yaml --in-descriptions

# Case sensitive
mrapids search "Order" api.yaml --case-sensitive

# Search in specific areas
mrapids search "auth" api.yaml --in operations,schemas
```

### Execution & Quality Commands

#### `run` - Execute Operations
```bash
# By operation ID
mrapids run api.yaml --opId getUser

# By path and method
mrapids run api.yaml --path /users/{id} --method GET

# With parameters
mrapids run api.yaml --opId getUser --param id=123

# With body
mrapids run api.yaml --opId createUser --body user.json

# Dry run
mrapids run api.yaml --opId deleteUser --dry-run

# Environment specific
mrapids run api.yaml --opId getOrders --env production
```

#### `test` - Run Tests
```bash
# Test single operation
mrapids test api.yaml --opId getUser

# Test all operations
mrapids test api.yaml --all

# From test file
mrapids test api.yaml --from tests.yaml

# Validate responses
mrapids test api.yaml --all --validate

# Performance test
mrapids test api.yaml --opId search --load 100 --concurrent 10

# Generate report
mrapids test api.yaml --all --report junit.xml
```

#### `tests init` - Initialize Test Suite
```bash
# Basic test generation
mrapids tests init api.yaml

# With specific framework
mrapids tests init api.yaml --framework pytest

# Include CI/CD config
mrapids tests init api.yaml --with-ci github-actions

# Custom output directory
mrapids tests init api.yaml --output ./tests
```

### Generation Commands

#### `gen snippets` - Generate Examples
```bash
# All examples
mrapids gen snippets api.yaml

# Specific operation
mrapids gen snippets api.yaml --opId createUser

# Output formats
mrapids gen snippets api.yaml --format curl
mrapids gen snippets api.yaml --format httpie
mrapids gen snippets api.yaml --format fetch

# Custom output
mrapids gen snippets api.yaml --output ./examples
```

#### `gen sdk` - Generate SDKs
```bash
# Single language
mrapids gen sdk api.yaml --lang typescript

# Multiple languages
mrapids gen sdk api.yaml --lang typescript,python,go

# With package info
mrapids gen sdk api.yaml --lang python --package myapi-client

# Include docs
mrapids gen sdk api.yaml --lang typescript --with-docs

# Custom templates
mrapids gen sdk api.yaml --lang java --template ./my-templates
```

#### `gen stubs` - Generate Server Stubs
```bash
# Express.js
mrapids gen stubs api.yaml --framework express

# FastAPI
mrapids gen stubs api.yaml --framework fastapi

# Spring Boot
mrapids gen stubs api.yaml --framework spring

# With tests
mrapids gen stubs api.yaml --framework express --with-tests
```

#### `gen fixtures` - Generate Test Data
```bash
# All fixtures
mrapids gen fixtures api.yaml

# Specific schemas
mrapids gen fixtures api.yaml --schema User,Order

# Number of samples
mrapids gen fixtures api.yaml --count 10

# Deterministic output
mrapids gen fixtures api.yaml --seed 42

# Output format
mrapids gen fixtures api.yaml --format json
mrapids gen fixtures api.yaml --format yaml
```

### Auth Commands

#### `auth login` - Authenticate
```bash
# OAuth providers
mrapids auth login github
mrapids auth login google --scopes "read:user,repo"

# API key
mrapids auth login api-key --name prod-key

# Custom OAuth
mrapids auth login custom --auth-url https://auth.example.com
```

#### `auth logout` - Remove Credentials
```bash
# Specific profile
mrapids auth logout github

# All profiles
mrapids auth logout --all

# Force logout
mrapids auth logout github --force
```

#### `auth status` - Show Auth Status
```bash
# All profiles
mrapids auth status

# Specific profile
mrapids auth status github

# Test authentication
mrapids auth status github --test

# JSON output
mrapids auth status --output json
```

## 🎯 Common Workflows

### Developer Workflow
```bash
# Start project
mrapids init my-api
mrapids validate api.yaml --strict

# Explore API
mrapids list operations api.yaml
mrapids search "user" api.yaml
mrapids show createUser api.yaml

# Generate and test
mrapids gen snippets api.yaml --opId createUser
mrapids run api.yaml --opId createUser --dry-run
mrapids test api.yaml --opId createUser
```

### CI/CD Pipeline
```bash
# Validation stage
mrapids validate api.yaml --strict --lint

# Test stage  
mrapids test api.yaml --all --validate

# Breaking change detection
mrapids diff prod.yaml staging.yaml --breaking

# Cleanup
mrapids cleanup --all
```

### SDK Generation
```bash
# Validate first
mrapids validate api.yaml

# Generate for multiple languages
mrapids gen sdk api.yaml --lang typescript,python,go

# Test generated SDKs
cd sdk-typescript && npm test
cd sdk-python && pytest
```

## 💡 Key Improvements

1. **Clearer Verbs**: Each command has a distinct purpose
2. **Logical Grouping**: Commands organized by workflow
3. **Consistent Patterns**: 
   - `--opId` for operation ID
   - `--output` for output format
   - `--format` for file format
   - `--env` for environment
4. **Subcommands**: Complex commands use subcommands (e.g., `auth login`, `gen sdk`)
5. **Reduced Overlap**: No more confusion between similar commands

## 🚀 Migration from Old Commands

| Old Command | New Command |
|-------------|-------------|
| `init-config` | `config` |
| `analyze` | `gen snippets` |
| `explore` | `search` |
| `setup-tests` | `tests init` |
| `sdk` | `gen sdk` |
| `generate` | `gen stubs` or `gen sdk` |
| `resolve` | `flatten` (removed - same functionality) |

---

*Simplified. Streamlined. Powerful.*