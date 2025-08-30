# mrapids validate

Validate OpenAPI/Swagger specifications for correctness and best practices.

## Synopsis

```bash
mrapids validate [OPTIONS] <SPEC>
```

## Description

The `validate` command performs comprehensive validation of OpenAPI and Swagger specifications, detecting errors that would cause failures in code generation, API implementation, or runtime execution.

## Arguments

### `<SPEC>`
Path to the OpenAPI/Swagger specification file (YAML or JSON format).

## Options

### `--strict`
Enable strict mode - treats all warnings as errors. Useful for CI/CD pipelines and enforcing quality standards.

### `--lint`
Enable linting mode - performs full validation including best practices, style checks, and documentation completeness.

### `--format <FORMAT>`
Output format for validation results.
- `text` (default): Human-readable output with colors
- `json`: Machine-readable JSON output for automation

## Validation Levels

### 1. **Quick (Default)**
Basic structural validation:
- Version detection (OpenAPI 3.x or Swagger 2.0)
- Required fields (info, title, version)
- Basic structure validation

### 2. **Standard (--strict)**
Comprehensive error checking:
- All quick validations
- Reference integrity ($ref validation)
- Duplicate operation ID detection
- Schema type constraint validation
- Path parameter validation
- Security scheme validation

### 3. **Full (--lint)**
Complete validation with best practices:
- All standard validations
- Missing descriptions and summaries
- Missing examples
- Naming convention checks
- Unused component detection
- Security warnings (HTTP vs HTTPS)
- Documentation completeness

## Examples

### Basic Validation
```bash
# Quick structural validation
mrapids validate api-spec.yaml
```

### Strict Mode
```bash
# Treat warnings as errors
mrapids validate --strict api-spec.yaml
```

### Lint Mode
```bash
# Full validation with best practices
mrapids validate --lint api-spec.yaml
```

### JSON Output
```bash
# Machine-readable output
mrapids validate --strict --format json api-spec.yaml

# Check if valid using jq
mrapids validate --format json spec.yaml | jq '.valid'
```

### CI/CD Integration
```bash
# In a build script
if ! mrapids validate --strict api-spec.yaml; then
    echo "Validation failed"
    exit 1
fi
```

## Common Errors Detected

### Undefined References
```yaml
# Error: Schema 'UserModel' is not defined
schema:
  $ref: '#/components/schemas/UserModel'
```

### Duplicate Operation IDs
```yaml
# Error: Duplicate operationId 'getUsers'
paths:
  /users:
    get:
      operationId: getUsers
  /accounts:
    get:
      operationId: getUsers  # Duplicate!
```

### Type Constraint Violations
```yaml
# Error: String type cannot have numeric constraint 'minimum'
properties:
  name:
    type: string
    minimum: 5  # Invalid!
```

### Missing Path Parameters
```yaml
# Error: Path parameter 'id' is not defined
paths:
  /users/{id}:
    get:
      parameters: []  # Missing 'id' parameter!
```

## Output Format

### Text Output
```
🔍 Validating OpenAPI Specification
📄 Spec: api-spec.yaml
📊 Level: standard (strict mode)

❌ Errors found:
  • Schema 'UserModel' is not defined
    at $.paths./users.get.responses.200.content.application/json.schema.$ref
  • Duplicate operationId 'getUsers'
    at $.paths./users.post

📈 Summary: 2 errors, 0 warnings
```

### JSON Output
```json
{
  "valid": false,
  "version": "OpenAPI 3.0.0",
  "errors": [
    {
      "code": "undefined-schema",
      "message": "Schema 'UserModel' is not defined",
      "path": "$.paths./users.get.responses.200.content.application/json.schema.$ref",
      "severity": "error"
    }
  ],
  "warnings": [],
  "duration_ms": 15
}
```

## Exit Codes

- `0`: Validation successful
- `1`: Validation failed (errors found or warnings in strict mode)

## Performance

Validation is optimized for speed:
- Small specs: ~5-10ms
- Medium specs: ~20-50ms
- Large specs: ~100-200ms

## Best Practices

1. **Use in Development**: Run validation frequently during API design
2. **CI/CD Integration**: Add `--strict` validation to your build pipeline
3. **Pre-commit Hooks**: Validate before committing changes
4. **Team Standards**: Use `--lint` to enforce conventions

## See Also

- `mrapids gen sdk` - Generate SDK after validation
- `mrapids diff` - Compare specifications
- `mrapids resolve` - Resolve all references