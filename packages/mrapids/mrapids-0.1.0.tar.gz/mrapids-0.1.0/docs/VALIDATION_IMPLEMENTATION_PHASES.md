# Validation Implementation Phases

## When Rules Enter the MicroRapid Ecosystem

### Phase 1: Development Time (Creating MicroRapid)

```bash
# 1. Research and collect rules
$ git clone https://github.com/stoplightio/spectral
$ curl -O https://owasp.org/api-security/rules.yaml
$ wget https://zalando.github.io/restful-api-guidelines/rules.yaml

# 2. Create bundled ruleset
$ cat > rules/mrapids-bundled.yaml << EOF
extends: [[spectral:oas, all]]
rules:
  # From OWASP
  require-https: ...
  # From Zalando  
  use-kebab-case: ...
  # MicroRapid specific
  operation-id-required: ...
EOF

# 3. Compile into binary
$ cargo build --release
# Rules are now INSIDE the binary
```

### Phase 2: User Installation Time

```bash
# User installs MicroRapid
$ brew install mrapids
# or
$ curl -L https://install.mrapids.com | sh

# Check what's included
$ mrapids --version
MicroRapid CLI v1.0.0
Built with validation rules v2024.01.15
- OAS 2.0 support ✓
- OAS 3.0.x support ✓
- OAS 3.1.x support ✓
- Security rules (OWASP 2023) ✓
```

### Phase 3: User Execution Time

#### Scenario A: First Time Project Setup
```bash
$ mrapids init my-api --from-url https://api.example.com/spec.yaml

┌─ T+0ms ────────────────────────────────────┐
│ User runs init command                      │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+10ms ───────────────────────────────────┐
│ Download spec from URL                      │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+200ms ──────────────────────────────────┐
│ Detect spec version: "openapi: 3.0.2"       │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+205ms ──────────────────────────────────┐
│ Load OAS 3.0 rules from EMBEDDED BINARY    │
│ (No network call, no file read)            │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+210ms ──────────────────────────────────┐
│ Execute validation with loaded rules        │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+450ms ──────────────────────────────────┐
│ Show results and continue/abort            │
└─────────────────────────────────────────────┘
```

#### Scenario B: Explicit Validation
```bash
$ mrapids validate spec api.yaml

┌─ T+0ms ────────────────────────────────────┐
│ Read api.yaml from disk                     │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+5ms ────────────────────────────────────┐
│ Parse and detect: "swagger: 2.0"           │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+10ms ───────────────────────────────────┐
│ Extract Swagger 2.0 rules from binary      │
│                                            │
│ // Pseudo-code inside mrapids:             │
│ match version {                            │
│   "2.0" => EMBEDDED_SWAGGER2_RULES,       │
│   "3.0.x" => EMBEDDED_OAS3_RULES,         │
│   "3.1.x" => EMBEDDED_OAS31_RULES         │
│ }                                          │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+15ms ───────────────────────────────────┐
│ Run validation engine with rules           │
└─────────────────────────────────────────────┘
                    ↓
┌─ T+200ms ──────────────────────────────────┐
│ Display validation results                  │
└─────────────────────────────────────────────┘
```

## Implementation Stages

### Stage 1: Basic Embedded Rules (Week 1)
```rust
// Hardcode basic rules in Rust
pub fn validate_basic(spec: &Value) -> Vec<ValidationError> {
    let mut errors = vec![];
    
    // Basic checks
    if spec.get("info").is_none() {
        errors.push(ValidationError::new("Missing info section"));
    }
    
    // Security check
    if let Some(servers) = spec.get("servers").and_then(|s| s.as_array()) {
        for server in servers {
            if let Some(url) = server.get("url").and_then(|u| u.as_str()) {
                if url.starts_with("http://") {
                    errors.push(ValidationError::new("Use HTTPS instead of HTTP"));
                }
            }
        }
    }
    
    errors
}
```

### Stage 2: Rule Engine Integration (Week 2)
```rust
// Embed Spectral rules
const OAS3_RULES: &str = include_str!("../rules/oas3.spectral.yaml");

pub async fn validate_with_spectral(spec_path: &Path) -> Result<ValidationReport> {
    // Write rules to temp file
    let rules_file = write_temp_rules(OAS3_RULES)?;
    
    // Shell out to Spectral
    let output = Command::new("spectral")
        .args(&["lint", spec_path.to_str().unwrap()])
        .args(&["--ruleset", rules_file.to_str().unwrap()])
        .output()
        .await?;
    
    parse_spectral_output(output)
}
```

### Stage 3: Native Rust Validation (Week 3-4)
```rust
// Pure Rust implementation (no external dependencies)
use jsonschema::{JSONSchema, Draft};

pub fn validate_native(spec: &Value, version: &SpecVersion) -> ValidationResult {
    let schema = match version {
        SpecVersion::OpenAPI3_0(_) => OAS30_SCHEMA,
        SpecVersion::OpenAPI3_1(_) => OAS31_SCHEMA,
        _ => OAS2_SCHEMA,
    };
    
    let compiled = JSONSchema::compile(schema)
        .expect("Schema compilation failed");
        
    compiled.validate(spec)
        .map_err(|e| ValidationError::from(e))
}
```

## Memory Flow Diagram

```
┌──────────────────────────────────────┐
│         MicroRapid Binary            │
│                                      │
│  ┌────────────────────────────────┐  │
│  │    Executable Code             │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │    Embedded Rules (200KB)      │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │ OAS 2.0 Rules (50KB)     │  │  │
│  │  ├──────────────────────────┤  │  │
│  │  │ OAS 3.0.x Rules (60KB)   │  │  │
│  │  ├──────────────────────────┤  │  │
│  │  │ OAS 3.1 Rules (40KB)     │  │  │
│  │  ├──────────────────────────┤  │  │
│  │  │ Security Rules (50KB)    │  │  │
│  │  └──────────────────────────┘  │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
                ↓ At runtime
         Rules loaded into
         memory instantly
```

## Cost Analysis

### Traditional Approach (Network-based)
```
Every validation:
- Network request: 50-200ms
- Download rules: 100ms
- Parse rules: 20ms
- Total: 170-320ms overhead

Plus:
- Requires internet
- Can fail if service down
- Security concerns
```

### MicroRapid Approach (Embedded)
```
Every validation:
- Load from binary: 5ms
- Parse rules: 0ms (pre-parsed)
- Total: 5ms overhead

Plus:
- Works offline
- Never fails
- Secure by default
```

## Summary

**When do rules come to the CLI?**

1. **At build time** - Rules are embedded into the binary
2. **At install time** - User gets everything in one download
3. **At runtime** - Rules are instantly available in memory
4. **Never downloaded** - No network dependency

This is why MicroRapid can validate specs:
- ⚡ Fast (5ms to load rules)
- 🔒 Secure (no external dependencies)
- 🌐 Offline (everything bundled)
- 🎯 Version-aware (right rules for each spec version)