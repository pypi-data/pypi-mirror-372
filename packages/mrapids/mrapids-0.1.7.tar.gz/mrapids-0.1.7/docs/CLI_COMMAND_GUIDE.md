# MicroRapid CLI Command Guide

> **Quick Reference for Developers, DevOps, and QA Engineers**

## 🚀 Quick Start Commands

### For First-Time Users
```bash
# Start a new project from scratch
mrapids init my-api-project

# Or initialize from an existing OpenAPI spec
mrapids init my-api --from-url https://api.example.com/openapi.json

# Analyze what's in your spec
mrapids analyze openapi.yaml

# Run your first API call
mrapids run openapi.yaml --operation getUser --dry-run
```

## 📚 Commands by Use Case

### 🏗️ Project Setup & Configuration

#### `init` - Start a New Project
**When to use**: Starting a new API project or importing existing specs
```bash
# Create from template
mrapids init my-project --template rest

# Import from URL
mrapids init my-project --from-url https://petstore.swagger.io/v2/swagger.json

# Force overwrite existing
mrapids init my-project --force
```
**Output**: Creates project structure with OpenAPI spec, examples, and config files

#### `init-config` - Set Up Environment Configuration
**When to use**: Configuring different environments (dev, staging, prod)
```bash
# Interactive setup
mrapids init-config

# Create specific environment
mrapids init-config --env production --base-url https://api.prod.com

# With authentication
mrapids init-config --env staging --profile staging-key
```
**Output**: Creates `.mrapids/config/[env].yaml` with environment-specific settings

### 🔍 API Discovery & Analysis

#### `analyze` - Generate Examples from Your Spec
**When to use**: Understanding your API structure and generating test data
```bash
# Basic analysis
mrapids analyze openapi.yaml

# Generate examples in specific directory
mrapids analyze openapi.yaml --output ./test-data

# Skip validation for draft specs
mrapids analyze openapi.yaml --skip-validate
```
**Output**: Creates example requests/responses for every operation

#### `list` - Browse Available Operations
**When to use**: Quick overview of what's in your API
```bash
# List all operations
mrapids list operations openapi.yaml

# Filter by method
mrapids list operations openapi.yaml --method GET

# Filter by path pattern
mrapids list operations openapi.yaml --pattern "/users/*"

# List saved requests
mrapids list requests
```
**Output**: Table of operations with IDs, methods, and paths

#### `show` - Get Operation Details
**When to use**: Deep dive into a specific endpoint
```bash
# Show operation details
mrapids show getUserById --spec openapi.yaml

# Include schema information
mrapids show createUser --spec openapi.yaml --verbose

# Output as JSON
mrapids show getOrders --spec openapi.yaml --format json
```
**Output**: Parameters, request body schema, response schemas, and examples

#### `explore` - Search Operations
**When to use**: Finding operations when you don't know exact names
```bash
# Search by keyword
mrapids explore user --spec openapi.yaml

# Case-sensitive search
mrapids explore Order --case-sensitive

# Search in descriptions too
mrapids explore payment --include-descriptions
```
**Output**: Filtered list of matching operations

### 🏃 API Execution & Testing

#### `run` - Execute API Operations
**When to use**: Making actual API calls during development or debugging
```bash
# Dry run (see what would be sent)
mrapids run openapi.yaml --operation getUser --dry-run

# With parameters
mrapids run openapi.yaml --operation getUserById --param userId=123

# With request body
mrapids run openapi.yaml --operation createUser --body user.json

# Using saved request
mrapids run openapi.yaml --request saved-requests/create-user.yaml

# With specific environment
mrapids run openapi.yaml --operation listOrders --env production
```
**Output**: API response with status code and formatted body

#### `test` - Run API Tests
**When to use**: Validating API behavior and contracts
```bash
# Test single operation
mrapids test openapi.yaml --operation getHealth

# Test all operations
mrapids test openapi.yaml --all

# With test data
mrapids test openapi.yaml --operation createUser --data test-user.json

# Validate responses against schema
mrapids test openapi.yaml --operation getUser --validate-response

# Performance test
mrapids test openapi.yaml --operation search --iterations 100 --concurrent 10
```
**Output**: Test results with pass/fail status and timing

#### `setup-tests` - Generate Complete Test Suite
**When to use**: Setting up automated testing for CI/CD
```bash
# Generate test structure
mrapids setup-tests openapi.yaml

# For specific framework
mrapids setup-tests openapi.yaml --framework pytest

# With CI/CD config
mrapids setup-tests openapi.yaml --with-ci github-actions
```
**Output**: Test files, fixtures, and CI configuration

### 🔐 Authentication Management

#### `auth` - Manage Authentication
**When to use**: Setting up API authentication for different environments
```bash
# OAuth flow
mrapids auth login github
mrapids auth login google --scopes "read:user,repo"

# API key setup
mrapids auth add-key production --header "X-API-Key"

# List profiles
mrapids auth list

# Test authentication
mrapids auth test production-oauth

# Remove profile
mrapids auth logout github
```
**Output**: Encrypted auth profiles in `.mrapids/auth/`

### 🛠️ Development Tools

#### `generate` - Code Generation
**When to use**: Creating boilerplate code from specs
```bash
# Generate models
mrapids generate models openapi.yaml --language typescript

# Generate API client
mrapids generate client openapi.yaml --language python --output ./client

# Generate server stubs
mrapids generate server openapi.yaml --framework express
```
**Output**: Generated code files in target language

#### `sdk` - Generate Full SDK
**When to use**: Creating client libraries for API consumers
```bash
# TypeScript SDK
mrapids sdk openapi.yaml --language typescript --package-name @mycompany/api

# Python SDK with docs
mrapids sdk openapi.yaml --language python --with-docs

# Multiple languages
mrapids sdk openapi.yaml --language typescript,python,go,rust

# With custom templates
mrapids sdk openapi.yaml --template ./my-templates --language java
```
**Output**: Complete SDK with package files, docs, and examples

#### `validate` - Validate OpenAPI Spec
**When to use**: Ensuring spec correctness before deployment
```bash
# Basic validation
mrapids validate openapi.yaml

# Strict mode (warnings as errors)
mrapids validate openapi.yaml --strict

# With custom rules
mrapids validate openapi.yaml --rules security-rules.yaml

# Multiple specs
mrapids validate api-v1.yaml api-v2.yaml --format json
```
**Output**: Validation report with errors and warnings

### 📋 API Maintenance

#### `diff` - Compare API Versions
**When to use**: Finding breaking changes between versions
```bash
# Compare two specs
mrapids diff api-v1.yaml api-v2.yaml

# Only breaking changes
mrapids diff api-old.yaml api-new.yaml --breaking-only

# Ignore certain changes
mrapids diff api-v1.yaml api-v2.yaml --ignore-descriptions

# Output as JSON
mrapids diff api-v1.yaml api-v2.yaml --format json
```
**Output**: List of changes categorized by severity

#### `flatten` - Simplify Complex Specs
**When to use**: Creating a single-file spec from multi-file refs
```bash
# Flatten all $ref
mrapids flatten openapi.yaml --output openapi-flat.yaml

# Keep internal refs
mrapids flatten openapi.yaml --external-only

# Validate after flattening
mrapids flatten openapi.yaml --validate
```
**Output**: Single OpenAPI file with all references resolved

#### `resolve` - Resolve References
**When to use**: Debugging reference issues or preparing for tools that don't support $ref
```bash
# Resolve and show
mrapids resolve openapi.yaml

# Resolve specific path
mrapids resolve openapi.yaml --path "#/components/schemas/User"

# Save resolved spec
mrapids resolve openapi.yaml --output resolved.yaml
```
**Output**: Spec with all references replaced by actual content

#### `cleanup` - Clean Temporary Files
**When to use**: Cleaning up after testing or when switching projects
```bash
# Clean test artifacts
mrapids cleanup

# Clean specific types
mrapids cleanup --cache --temp --logs

# Clean everything except config
mrapids cleanup --all --keep-config

# Dry run
mrapids cleanup --dry-run
```
**Output**: List of removed files and freed space

## 🎯 Common Workflows

### For Developers
```bash
# Morning routine
mrapids validate openapi.yaml
mrapids diff openapi.yaml openapi-prod.yaml
mrapids test openapi.yaml --operation healthCheck

# Adding new endpoint
mrapids analyze openapi.yaml
mrapids run openapi.yaml --operation newEndpoint --dry-run
mrapids generate client openapi.yaml --language typescript

# Debugging
mrapids show failingOperation --spec openapi.yaml --verbose
mrapids run openapi.yaml --operation failingOperation --curl-output
```

### For DevOps
```bash
# CI/CD Pipeline
mrapids validate openapi.yaml --strict
mrapids test openapi.yaml --all --env staging
mrapids diff openapi-previous.yaml openapi.yaml --breaking-only

# Environment setup
mrapids init-config --env production --no-interactive
mrapids auth add-key production --from-env API_KEY
mrapids test openapi.yaml --env production --operation health

# Monitoring
mrapids run openapi.yaml --operation metrics --format json | jq .
```

### For QA Engineers
```bash
# Test suite setup
mrapids setup-tests openapi.yaml --framework pytest
mrapids analyze openapi.yaml --output test-data/

# Contract testing
mrapids validate openapi.yaml
mrapids test openapi.yaml --all --validate-response

# Regression testing
mrapids diff api-v1.yaml api-v2.yaml > breaking-changes.txt
mrapids test api-v2.yaml --from-file regression-tests.yaml

# Load testing
mrapids test openapi.yaml --operation search \
  --iterations 1000 --concurrent 50 --duration 5m
```

## 💡 Pro Tips

### 1. **Use Aliases for Common Commands**
```bash
alias mr='mrapids'
alias mrt='mrapids test'
alias mrr='mrapids run'
```

### 2. **Chain Commands for Workflows**
```bash
# Validate, test, and deploy
mrapids validate api.yaml && \
mrapids test api.yaml --all && \
echo "Ready to deploy!"
```

### 3. **Use Environment Variables**
```bash
export MRAPIDS_SPEC=./openapi.yaml
export MRAPIDS_ENV=staging
mrapids run --operation getUser  # Uses env vars
```

### 4. **Output Formats for Automation**
```bash
# JSON for parsing
mrapids list operations api.yaml --format json | jq '.operations[].id'

# CSV for reports
mrapids diff v1.yaml v2.yaml --format csv > changes.csv
```

### 5. **Dry Run Everything First**
```bash
# Always safe
mrapids run api.yaml --operation deleteUser --dry-run
mrapids cleanup --dry-run
```

## 🆘 Getting Help

```bash
# General help
mrapids --help
mrapids help

# Command-specific help
mrapids run --help
mrapids test --help

# Show version
mrapids --version
```

## 🔗 See Also

- [API Documentation](./API_REFERENCE.md)
- [Configuration Guide](./CONFIGURATION.md)
- [CI/CD Integration](./CI_CD_GUIDE.md)
- [Troubleshooting](./TROUBLESHOOTING.md)

---

*Remember: MicroRapid executes your OpenAPI specs directly - no conversion needed! Your spec IS your test.*