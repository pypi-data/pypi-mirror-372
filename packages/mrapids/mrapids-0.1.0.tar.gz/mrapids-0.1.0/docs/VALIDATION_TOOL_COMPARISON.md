# Validation Tool Comparison

## Why Use Proven Validators vs. Custom Implementation

### Current Approach: Custom Parsing
```rust
// Hand-rolled validation (error-prone)
if !spec.paths.is_empty() {
    for (path, item) in &spec.paths {
        // Manual validation logic...
    }
}
```

**Problems:**
- ❌ Incomplete coverage of spec features
- ❌ Maintenance burden as specs evolve
- ❌ Reinventing the wheel
- ❌ Missing edge cases
- ❌ No community-contributed rules

### Proposed Approach: Industry-Standard Tools

## Tool Comparison Matrix

| Feature | Spectral | Redocly CLI | Custom Code | oasdiff |
|---------|----------|-------------|-------------|---------|
| **OAS 2.0 Support** | ✅ Full | ✅ Full | ⚠️ Partial | ✅ Full |
| **OAS 3.0.x Support** | ✅ Full | ✅ Full | ⚠️ Partial | ✅ Full |
| **OAS 3.1 Support** | ✅ Full | ✅ Full | ❌ No | ✅ Full |
| **Custom Rules** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Breaking Changes** | ❌ No | ⚠️ Limited | ❌ No | ✅ Yes |
| **Performance** | ⚡ Fast | ⚡ Fast | ⚡ Fast | ⚡ Fast |
| **Rust Integration** | 🔧 Shell | 🔧 Shell | ✅ Native | 🔧 Shell |
| **Active Development** | ✅ Yes | ✅ Yes | N/A | ✅ Yes |
| **Rule Ecosystem** | 🌟 Huge | 🌟 Large | ❌ None | N/A |

## Spectral Advantages

### 1. Comprehensive Rule Sets
```yaml
# Spectral comes with battle-tested rules
extends:
  - spectral:oas     # OpenAPI rules
  - spectral:asyncapi # AsyncAPI rules
  
# Plus thousands of community rules:
# - Zalando API Guidelines
# - Adidas API Guidelines  
# - Azure API Guidelines
```

### 2. Precise Error Messages
```bash
# Spectral output
api.yaml:23:7 error operation-operationId-unique 
  Operation IDs must be unique. Found: getUserById
  
api.yaml:45:9 warning operation-description
  Operation should have a description
  
✖ 2 problems (1 error, 1 warning)
```

### 3. Extensible Architecture
```javascript
// Custom function example
module.exports = (targetVal) => {
  if (targetVal && targetVal.includes('TODO')) {
    return [{
      message: 'Found TODO in description',
    }];
  }
};
```

## Implementation Complexity Comparison

### Custom Validation (Hundreds of Lines)
```rust
pub fn validate_openapi_document(doc: &OpenAPIDocument) -> Vec<ValidationError> {
    let mut errors = vec![];
    
    // Check info
    if doc.info.title.is_empty() {
        errors.push(ValidationError::new("Missing API title"));
    }
    
    // Check servers
    for server in &doc.servers {
        if !server.url.starts_with("https://") {
            errors.push(ValidationError::new("Server must use HTTPS"));
        }
        // ... dozens more checks ...
    }
    
    // Check paths
    for (path, item) in &doc.paths {
        // Check operations
        if let Some(get) = &item.get {
            validate_operation(get, &mut errors);
        }
        // ... repeat for all methods ...
    }
    
    // ... hundreds more lines ...
}
```

### Spectral Integration (Tens of Lines)
```rust
pub async fn validate_with_spectral(spec_path: &Path) -> Result<ValidationReport> {
    let output = Command::new("spectral")
        .args(&["lint", spec_path.to_str().unwrap()])
        .args(&["--format", "json"])
        .output()
        .await?;
    
    let results: SpectralResults = serde_json::from_slice(&output.stdout)?;
    Ok(ValidationReport::from_spectral(results))
}
```

## Real-World Rule Examples

### Security Rules from Major Companies

#### Zalando's REST Guidelines
```yaml
rules:
  must-use-semantic-versioning:
    description: Version numbers must follow semantic versioning
    given: $.info.version
    then:
      function: pattern
      functionOptions:
        match: "^[0-9]+\\.[0-9]+\\.[0-9]+$"

  must-contain-version-in-uri:
    description: API URLs must contain version
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        match: "/v[0-9]+"
```

#### Adidas API Guidelines
```yaml
rules:
  paths-kebab-case:
    description: Path segments must be kebab-case
    given: $.paths[*]~
    then:
      function: pattern
      functionOptions:
        match: "^(/[a-z0-9]+(-[a-z0-9]+)*)+$"

  must-have-request-id:
    description: All operations must accept X-Request-ID header
    given: $.paths[*][*].parameters[*]
    then:
      - field: name
        function: pattern
        functionOptions:
          match: "^[Xx]-[Rr]equest-[Ii][Dd]$"
```

## Breaking Change Detection with oasdiff

### What oasdiff Catches
```bash
# oasdiff output example
error   [response-property-became-required] at api.yaml
  in `#/paths/~1users~1{id}/get/responses/200/content/application~1json/schema/properties/email`
  response property 'email' became required

error   [request-parameter-removed] at api.yaml  
  in `#/paths/~1users/get/parameters/0`
  removed request parameter 'limit'

warning [endpoint-added] at api.yaml
  in `#/paths/~1users~1profile`
  added endpoint '/users/profile'
```

### Integration Benefits
1. **Automated**: Run in CI/CD pipelines
2. **Comprehensive**: Catches subtle breaking changes
3. **Configurable**: Define what constitutes "breaking"
4. **Language Agnostic**: Works with any OpenAPI spec

## Performance Comparison

### Validation Speed (1000 operations)
- Spectral: ~500ms ⚡
- Redocly: ~600ms ⚡
- Custom Rust: ~100ms ⚡ (but incomplete)
- Full Custom Validation: ~2000ms 🐌

### Development Time
- Spectral Integration: 1-2 days ✅
- Custom Validation: 2-4 weeks ❌
- Maintenance: Spectral (minimal) vs Custom (ongoing)

## Recommended Architecture

```
┌─────────────────┐
│  MicroRapid CLI │
└────────┬────────┘
         │
    ┌────▼────┐
    │ Validate │
    │ Command  │
    └────┬────┘
         │
    ┌────▼────────────────────┐
    │  Validation Orchestrator │
    └────┬──────┬──────┬──────┘
         │      │      │
    ┌────▼───┐ │ ┌────▼────┐
    │Spectral│ │ │ oasdiff │
    │  OAS   │ │ │Breaking │
    │ Rules  │ │ │ Changes │
    └────────┘ │ └─────────┘
          ┌────▼────┐
          │Spectral │
          │Security │
          │ Rules   │
          └─────────┘
```

## Conclusion

Using proven validators like Spectral and oasdiff provides:
- ✅ **Complete** OAS 2.0/3.x validation
- ✅ **Battle-tested** rule sets
- ✅ **Community** contributions
- ✅ **Minimal** maintenance
- ✅ **Professional** error messages
- ✅ **Fast** implementation

The small integration effort pays massive dividends in reliability and maintainability.