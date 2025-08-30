# Validation Command Matrix

## Quick Reference: Where to Apply Validation

| Command | Apply Validation? | When? | Performance Impact | Rationale |
|---------|------------------|-------|-------------------|-----------|
| **init** | ✅ YES | On spec import | +200-500ms | One-time setup, prevents bad specs |
| **validate** | ✅ YES | Always | +200-500ms | Primary purpose of command |
| **analyze** | ✅ YES | Before analysis | +200-500ms | Ensures valid examples |
| **generate** | ✅ YES | Before generation | +200-500ms | Prevents invalid SDK code |
| **flatten** | ✅ YES | After flattening | +200-500ms | Ensures output is valid |
| **run** | ❌ NO | Never | 0ms | Would kill performance |
| **test** | ❌ NO | Never | 0ms | Tests must be fast |
| **show** | ❌ NO | Never | 0ms | Quick lookup operation |
| **list** | ❌ NO | Never | 0ms | Simple read operation |
| **auth** | ❌ NO | Never | 0ms | Not spec-related |
| **cleanup** | ❌ NO | Never | 0ms | Not spec-related |

## Agent CLI Validation Strategy

### Agent Startup
```bash
# Validate once during agent initialization
mrapids-agent start --spec api.yaml

[Agent Starting]
🔍 Validating API specification... (one-time)
✅ Specification valid
🚀 Agent ready for MCP requests
```

### Agent Runtime
```bash
# NO validation during tool calls
MCP Request -> Agent -> Execute -> Response
     |          |         |          |
   ~10ms      ~5ms      ~50ms     ~10ms
   
# Total: ~75ms (without validation)
# With validation: ~575ms (unacceptable!)
```

## Performance Comparison

### Without Validation (Current)
```
mrapids run get-user --id 123
├─ Parse command: 2ms
├─ Load spec: 10ms  
├─ Build request: 5ms
├─ HTTP call: 50ms
└─ Total: ~67ms ⚡
```

### With Validation (Bad Idea)
```
mrapids run get-user --id 123
├─ Parse command: 2ms
├─ Load spec: 10ms
├─ VALIDATE SPEC: 300ms ❌
├─ Build request: 5ms  
├─ HTTP call: 50ms
└─ Total: ~367ms 🐌 (5x slower!)
```

## Practical Examples

### Good: Validate at Design Time
```bash
# When importing a new API spec
$ mrapids init petstore --from-url https://petstore.swagger.io/v2/swagger.json
🔍 Validating specification...
✅ OpenAPI 2.0 specification valid
📁 Creating project structure...

# When analyzing to generate examples  
$ mrapids analyze api.yaml
🔍 Validating specification...
✅ Specification valid
📊 Analyzing 24 operations...
```

### Bad: Validate at Runtime
```bash
# DON'T DO THIS - Would make every API call slow
$ mrapids run get-pet --id 1
❌ Validating specification... (300ms wasted!)
🚀 Executing request...
```

## Caching Strategy for Edge Cases

If you absolutely need some validation at runtime:

```rust
// Lightweight runtime checks (5-10ms max)
pub struct QuickValidator {
    spec_hash: String,
    last_validated: Instant,
}

impl QuickValidator {
    pub fn is_probably_valid(&self, spec: &Value) -> bool {
        // Super fast checks only
        spec.get("paths").is_some() &&
        spec.get("info").is_some() &&
        (spec.get("openapi").is_some() || spec.get("swagger").is_some())
    }
}
```

## Validation in CI/CD

```yaml
# .github/workflows/api-validation.yml
name: API Validation
on:
  push:
    paths: ['specs/**/*.yaml']

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Full validation in CI - latency doesn't matter here
      - name: Validate API Specs
        run: |
          mrapids validate spec specs/api.yaml --level full
          mrapids validate diff ${{ github.base_ref }} specs/api.yaml
```

## Summary by Use Case

### 🏗️ Development Time (Validate Everything)
- Importing specs
- Generating code/docs
- Analyzing APIs
- **Goal**: Catch errors early

### ⚡ Runtime (Skip Validation)  
- Making API calls
- Running tests
- Agent operations
- **Goal**: Maximum performance

### 🔍 Dedicated Validation
- CI/CD pipelines
- Pre-commit hooks
- Manual checks
- **Goal**: Ensure quality

The key insight: **Validate once, run many times!**