# Validate Command Documentation

## Overview

The `mrapids validate` command is a comprehensive OpenAPI/Swagger specification validator that ensures your API definitions are correct, complete, and follow best practices before using them for code generation or implementation.

## Value Proposition

### 🛡️ **Prevent Downstream Failures**
Catch specification errors early in the development cycle, preventing:
- SDK generation crashes
- Runtime errors in generated code
- API implementation inconsistencies
- Integration failures with third-party tools

### 💰 **Cost Savings**
- **Reduce debugging time** by catching errors before code generation
- **Prevent production issues** caused by malformed specifications
- **Minimize rework** by ensuring specifications are correct from the start
- **Save developer hours** with clear, actionable error messages

### 🚀 **Accelerate Development**
- **Instant feedback** on specification quality
- **Automated checks** replace manual review processes
- **CI/CD integration** with JSON output format
- **Progressive validation levels** from quick checks to comprehensive linting

### 📊 **Quality Assurance**
- **Enforce standards** across teams and projects
- **Maintain consistency** in API design
- **Document best practices** through lint rules
- **Track specification quality** over time

## Purpose

The validate command serves multiple critical purposes in the API development lifecycle:

### 1. **Specification Correctness**
Ensures that OpenAPI/Swagger specifications are syntactically and semantically correct according to the official standards (OpenAPI 3.x and Swagger 2.0).

### 2. **Reference Integrity**
Verifies that all internal references ($ref) point to existing definitions, preventing "undefined reference" errors during code generation.

### 3. **Operation Uniqueness**
Detects duplicate operation IDs that would cause naming conflicts in generated SDKs and client libraries.

### 4. **Type Safety**
Validates that schema types and their constraints are compatible, preventing type mismatches that lead to runtime errors.

### 5. **Path Parameter Validation**
Ensures all path parameters are properly defined and marked as required, preventing routing and validation issues.

### 6. **Best Practices Enforcement**
Promotes API design best practices through optional linting rules that check for:
- Missing descriptions and examples
- Naming convention consistency
- Security considerations
- Documentation completeness

## Features

### 🔍 **Multi-Level Validation**

#### Quick Mode (Default)
- Basic structural validation
- OpenAPI/Swagger version detection
- Required fields presence

#### Standard Mode (`--strict`)
- All quick mode checks
- Reference validation
- Duplicate detection
- Type constraint validation
- Path parameter validation

#### Full Mode (`--lint`)
- All standard mode checks
- Security best practices
- Documentation completeness
- Naming conventions
- Unused component detection

### 🎯 **Comprehensive Error Detection**

| Error Type | Description | Impact if Undetected |
|------------|-------------|---------------------|
| **Undefined References** | `$ref` points to non-existent schema/response/parameter | SDK generation crashes |
| **Duplicate Operation IDs** | Multiple operations share the same ID | Naming conflicts in generated code |
| **Type Constraint Violations** | Invalid combinations like string with numeric constraints | Runtime type errors |
| **Missing Path Parameters** | Path parameters in URL not defined in operation | 404 errors, routing failures |
| **Invalid Security Schemes** | References to undefined security definitions | Authentication/authorization failures |

### 📋 **Output Formats**

#### Text Format (Default)
Human-readable output with:
- Colored error/warning indicators
- File paths for easy navigation
- Grouped errors by severity
- Summary statistics

#### JSON Format (`--format json`)
Machine-readable output for:
- CI/CD pipeline integration
- Automated quality gates
- Programmatic analysis
- Metrics collection

## Usage Examples

### Basic Validation
```bash
# Quick structural check
mrapids validate api-spec.yaml
```

### Strict Validation
```bash
# Comprehensive error checking
mrapids validate --strict api-spec.yaml

# Treats warnings as errors - perfect for CI/CD
```

### Lint Mode
```bash
# Full validation with best practices
mrapids validate --lint api-spec.yaml

# Catches style issues, missing docs, unused schemas
```

### CI/CD Integration
```bash
# JSON output for automated pipelines
mrapids validate --strict --format json api-spec.yaml

# Parse results programmatically
mrapids validate --lint --format json spec.yaml | jq '.valid'
```

## Real-World Scenarios

### Scenario 1: Pre-Deployment Validation
```bash
# In your CI/CD pipeline
if ! mrapids validate --strict api-spec.yaml; then
  echo "API specification has errors. Deployment blocked."
  exit 1
fi
```

### Scenario 2: Code Review Automation
```bash
# In a pre-commit hook
mrapids validate --lint modified-spec.yaml --format json > validation.json
if [ $(jq '.errors | length' validation.json) -gt 0 ]; then
  echo "Please fix specification errors before committing"
  exit 1
fi
```

### Scenario 3: SDK Generation Safety
```bash
# Validate before generating SDKs
mrapids validate --strict api-spec.yaml && \
mrapids gen sdk -s api-spec.yaml -o ./sdks --language typescript
```

## Common Issues Detected

### 1. Bad References
```yaml
# ❌ Will cause SDK generation to fail
schema:
  $ref: '#/components/schemas/UserModel'  # UserModel doesn't exist!
```

### 2. Duplicate Operation IDs
```yaml
# ❌ Creates naming conflicts
paths:
  /users:
    get:
      operationId: getUsers
  /accounts:
    get:
      operationId: getUsers  # Duplicate!
```

### 3. Type Mismatches
```yaml
# ❌ Runtime errors in generated code
properties:
  age:
    type: string
    minimum: 0  # Numeric constraint on string!
```

### 4. Missing Path Parameters
```yaml
# ❌ 404 errors in production
paths:
  /users/{userId}:  # userId in path
    get:
      parameters: []  # But not defined!
```

## Best Practices

### 1. **Progressive Validation**
Start with basic validation during development, then increase strictness:
```bash
# During development
mrapids validate spec.yaml

# Before PR/commit
mrapids validate --strict spec.yaml

# Before release
mrapids validate --lint spec.yaml
```

### 2. **CI/CD Integration**
Add validation to your pipeline:
```yaml
# GitHub Actions example
- name: Validate API Spec
  run: |
    mrapids validate --strict --format json api-spec.yaml > results.json
    echo "::set-output name=valid::$(jq '.valid' results.json)"
```

### 3. **Team Standards**
Use `--lint` mode to enforce team conventions:
- Require descriptions for all operations
- Enforce camelCase for operation IDs
- Mandate examples for request/response bodies
- Ensure security schemes are defined

## Validation Rules Reference

### Error Level Rules (Block Execution)
- Missing required fields (title, version, paths)
- Invalid references
- Duplicate operation IDs
- Type constraint violations
- Missing/invalid path parameters
- Circular references
- Invalid schema types

### Warning Level Rules (Best Practices)
- Missing descriptions
- Missing examples
- Inconsistent naming conventions
- Unused components
- HTTP instead of HTTPS
- Missing security definitions
- Incomplete documentation

## Return Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed |
| 1 | Validation failed (errors found) |
| 1 | Warnings found (in strict mode) |

## Performance

The validate command is optimized for speed:
- **Small specs (<100 operations)**: ~5-10ms
- **Medium specs (100-500 operations)**: ~20-50ms
- **Large specs (500+ operations)**: ~100-200ms

## Future Enhancements

Planned improvements include:
- Custom validation rules via plugins
- Performance profiling for large specs
- Auto-fix suggestions for common issues
- Integration with popular API design tools
- Historical validation tracking
- Team-specific rule configurations

## Conclusion

The `mrapids validate` command is an essential tool in the modern API development workflow. By catching errors early and enforcing best practices, it saves development time, prevents production issues, and ensures high-quality API specifications that generate reliable code.

Use it early, use it often, and make it a required step in your API development process.