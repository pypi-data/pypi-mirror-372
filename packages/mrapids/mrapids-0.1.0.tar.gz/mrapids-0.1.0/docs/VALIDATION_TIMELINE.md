# When Do Validation Rules Come Into Play?

## Timeline: From Development to Runtime

### 1. 🛠️ **Build Time** (When compiling MicroRapid)

```rust
// During `cargo build --release`
// Rules are embedded into the binary

const RULES: &str = include_str!("../rules/bundled-rules.yaml");
```

**What happens:**
- Rules are read from YAML files
- Compiled directly into the binary
- Become part of the executable (~200KB)

```bash
# Before build
api-runtime/
├── src/
├── rules/
│   ├── oas2-rules.yaml      # 50KB
│   ├── oas3-rules.yaml      # 60KB
│   ├── oas31-rules.yaml     # 40KB
│   └── security-rules.yaml  # 50KB

# After build
target/release/mrapids        # Single binary with rules inside
```

### 2. 📦 **Distribution Time** (When user downloads)

```bash
# User downloads pre-built binary
$ curl -L https://github.com/mrapids/releases/download/v1.0/mrapids-darwin-arm64 -o mrapids
$ chmod +x mrapids

# Rules are already inside!
$ ls -la mrapids
-rwxr-xr-x  1 user  staff  15M  Dec 20 10:00 mrapids
```

### 3. 🚀 **Execution Time** (When user runs commands)

#### A. During `init` Command
```bash
$ mrapids init my-api --from-url https://api.example.com/openapi.yaml
```

```
Timeline:
0ms    → Command starts
10ms   → Download spec from URL
20ms   → Detect spec version (OAS 3.0.2)
25ms   → Load embedded OAS 3.0 rules from binary
30ms   → Create temporary rules file
35ms   → Run validation engine
250ms  → Show validation results
260ms  → Continue with project setup (if valid)
```

#### B. During `validate` Command
```bash
$ mrapids validate spec api.yaml
```

```
Timeline:
0ms    → Command starts
5ms    → Read spec file
10ms   → Detect version
15ms   → Extract embedded rules for that version
20ms   → Execute validation
200ms  → Display results
```

#### C. During `analyze` Command
```bash
$ mrapids analyze api.yaml
```

```
Timeline:
0ms    → Command starts
5ms    → Read spec
10ms   → Quick validation check (optional)
15ms   → If --validate flag, run full validation
250ms  → Continue with analysis
```

#### D. During `run` Command (NOT validated by default)
```bash
$ mrapids run get-user --id 123
```

```
Timeline (Normal - Fast):
0ms    → Command starts
5ms    → Load cached spec
10ms   → Build request
15ms   → Send HTTP request
65ms   → Display response

Timeline (With --validate flag):
0ms    → Command starts
5ms    → Load spec
10ms   → Extract rules and validate (+240ms)
250ms  → Build request
255ms  → Send HTTP request
305ms  → Display response
```

## 4. 🔄 **Rule Update Cycle**

### Option A: With Each Release
```bash
# MicroRapid v1.1.0 release
- Updated to Spectral v6.11 rules
- Added new OWASP 2023 security rules
- Included OpenAPI 3.1.1 support

# User updates
$ mrapids update
# or
$ brew upgrade mrapids
```

### Option B: Dynamic Rules (Future Enhancement)
```bash
# Check for rule updates
$ mrapids validate update-rules
📥 Downloading latest rules...
✅ Rules updated to version 2024.01.15

# Rules stored locally, not in binary
~/.mrapids/
└── rules/
    ├── version.json
    └── rules.yaml
```

## Visual Timeline

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Build Time    │     │ Distribution │     │   Run Time      │
│                 │     │              │     │                 │
│ Embed rules in  │────▶│ User gets    │────▶│ Rules used for  │
│ binary during   │     │ binary with  │     │ validation at   │
│ compilation     │     │ rules inside │     │ command exec    │
└─────────────────┘     └──────────────┘     └─────────────────┘
      ↑                                              ↑
      │                                              │
   Once per                                     Every time
   release                                    user validates
```

## Practical Examples

### Example 1: Project Setup
```bash
$ mrapids init petstore --from-url https://petstore.io/openapi.json

[Timeline of events:]
T+0ms    : Parse command arguments
T+10ms   : Start downloading spec
T+150ms  : Download complete
T+155ms  : Parse spec, detect "openapi": "3.0.0"
T+160ms  : Load OAS 3.0 rules from binary memory
T+165ms  : Write rules to /tmp/mrapids-rules-xyz.yaml
T+170ms  : Execute validation against spec
T+400ms  : Validation complete
T+405ms  : Display results
T+410ms  : Create project structure (if valid)
```

### Example 2: CI/CD Pipeline
```yaml
# GitHub Actions
- name: Validate API Spec
  run: |
    # Rules come from the mrapids binary
    mrapids validate spec api.yaml --level full
    
[Timeline:]
T+0ms    : GitHub runner starts mrapids
T+5ms    : Read api.yaml
T+10ms   : Detect OpenAPI 3.1.0
T+15ms   : Extract OAS 3.1 + security rules
T+20ms   : Run validation
T+300ms  : Exit with status 0 (success) or 1 (errors)
```

### Example 3: Development Mode
```bash
# Developer with custom rules
$ mrapids validate spec api.yaml --ruleset ./my-rules.yaml

[Timeline:]
T+0ms    : Start command
T+5ms    : Read api.yaml
T+10ms   : Read custom rules (bypass embedded)
T+15ms   : Merge with embedded security rules
T+20ms   : Execute validation
T+250ms  : Show results
```

## Key Points

1. **Rules are embedded at build time** - No network calls needed
2. **Available immediately** - Part of the binary from download
3. **Applied on-demand** - Only when validation is requested
4. **Version-specific** - Correct rules chosen based on spec version
5. **Fast access** - In-memory, no file I/O needed

## Performance Characteristics

```
Rule Loading Performance:
- From embedded binary: ~5ms
- From filesystem cache: ~10ms  
- From network (future): ~200ms

Validation Execution:
- Small spec (10 endpoints): ~50ms
- Medium spec (50 endpoints): ~200ms
- Large spec (200 endpoints): ~500ms
```

## Summary

The validation rules "come to the CLI" at:
1. **Build time** - Embedded in binary
2. **Run time** - Extracted and applied when needed
3. **Never downloaded** - Always available offline
4. **Applied selectively** - Only for commands that need validation

This design ensures validation is always available, fast, and doesn't require internet connectivity!