# Validate Command - Quick Reference

## 🚀 Quick Start

```bash
# Basic validation
mrapids validate api.yaml

# Strict mode (CI/CD ready)
mrapids validate --strict api.yaml

# Full lint mode (best practices)
mrapids validate --lint api.yaml
```

## 📊 Validation Levels

| Level | Flag | Use Case | Checks |
|-------|------|----------|--------|
| **Quick** | (default) | Development | Basic structure |
| **Standard** | `--strict` | CI/CD | All errors |
| **Full** | `--lint` | Quality | Errors + warnings |

## ❌ Errors Detected (Block Execution)

### 1. Undefined References
```yaml
$ref: '#/components/schemas/NonExistent'  # ❌ Doesn't exist
```

### 2. Duplicate Operation IDs
```yaml
paths:
  /users:
    get:
      operationId: getItems  # ❌ Duplicate!
  /products:
    get:
      operationId: getItems  # ❌ Same ID!
```

### 3. Type Constraint Violations
```yaml
age:
  type: string
  minimum: 0  # ❌ Numeric constraint on string!
```

### 4. Missing Path Parameters
```yaml
/users/{id}:  # ❌ {id} not defined in parameters
  get:
    parameters: []
```

## ⚠️ Warnings (Best Practices)

- Missing descriptions
- Missing examples
- Naming conventions
- Unused schemas
- HTTP vs HTTPS
- Missing security

## 🎯 Common Use Cases

### CI/CD Pipeline
```yaml
# GitHub Actions
- run: mrapids validate --strict api.yaml
```

### Pre-commit Hook
```bash
#!/bin/bash
mrapids validate --lint api.yaml || exit 1
```

### Automated Testing
```bash
mrapids validate --format json api.yaml | jq -e '.valid'
```

## 📤 Output Formats

### Text (Default)
```
❌ Errors found:
  • Schema 'User' is not defined
    at $.paths./users.get.responses.200

📈 Summary: 1 error, 0 warnings
```

### JSON (`--format json`)
```json
{
  "valid": false,
  "errors": [{
    "code": "undefined-schema",
    "message": "Schema 'User' is not defined",
    "path": "$.paths./users.get.responses.200"
  }]
}
```

## 🎮 Keyboard Shortcuts

| Task | Command |
|------|---------|
| Quick check | `mrapids validate api.yaml` |
| Pre-commit | `mrapids validate --strict api.yaml` |
| Full review | `mrapids validate --lint api.yaml` |
| CI/CD check | `mrapids validate --strict --format json api.yaml` |

## 💡 Pro Tips

1. **Start Simple**: Use basic validation during development
2. **Enforce Standards**: Use `--strict` in CI/CD
3. **Quality Gate**: Require `--lint` for releases
4. **Automate**: Add to pre-commit hooks
5. **Monitor**: Track validation metrics over time

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Schema not found" | Check spelling and `$ref` path |
| "Duplicate ID" | Rename operations uniquely |
| "Type mismatch" | Fix constraint/type combination |
| "Path param missing" | Add parameter definition |

## 📚 Related Commands

- `mrapids gen sdk` - Generate SDK after validation
- `mrapids diff` - Compare API versions
- `mrapids resolve` - Resolve all references

## 🚦 Exit Codes

- `0` - Validation passed
- `1` - Errors found (or warnings with --strict)