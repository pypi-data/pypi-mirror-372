# OpenAPI Specification Validation Implementation Plan

## Overview

Implement comprehensive OpenAPI specification validation using proven tools and a multi-level validation approach to ensure spec compliance, security, and governance.

## 1. Support Matrix Declaration

### Supported Versions
- **OpenAPI 2.0** (fka Swagger 2.0)
- **OpenAPI 3.0.x** (3.0.0, 3.0.1, 3.0.2, 3.0.3)
- **OpenAPI 3.1.x** (3.1.0)

### Version Detection Strategy
```rust
pub enum SpecVersion {
    Swagger2_0,
    OpenAPI3_0(String), // Store exact version
    OpenAPI3_1(String), // Store exact version
    Unknown,
}

pub fn detect_spec_version(content: &Value) -> Result<SpecVersion> {
    if let Some(swagger) = content.get("swagger").and_then(|v| v.as_str()) {
        if swagger == "2.0" {
            return Ok(SpecVersion::Swagger2_0);
        }
    }
    
    if let Some(openapi) = content.get("openapi").and_then(|v| v.as_str()) {
        if openapi.starts_with("3.0.") {
            return Ok(SpecVersion::OpenAPI3_0(openapi.to_string()));
        }
        if openapi.starts_with("3.1.") {
            return Ok(SpecVersion::OpenAPI3_1(openapi.to_string()));
        }
    }
    
    Err(anyhow!("Unknown spec format. Expected 'swagger: \"2.0\"' or 'openapi: \"3.x.y\"'"))
}
```

## 2. Validation Tool Integration

### Primary Tools
1. **Spectral** (via spectral-rs or shell integration)
   - OAS compliance validation
   - Custom security rules
   - Extensible ruleset system

2. **oasdiff** (for breaking change detection)
   - API compatibility checks
   - Governance enforcement

### Alternative Options
- **Redocly CLI** (if Spectral integration proves difficult)
- **openapi-validator** crate (Rust native)

## 3. Multi-Level Validation Architecture

### Level A: Canonical/OAS Compliance
```rust
pub struct ComplianceValidator {
    spectral_path: PathBuf,
    ruleset: RuleSet,
}

impl ComplianceValidator {
    pub async fn validate(&self, spec_path: &Path) -> Result<ValidationReport> {
        // Run Spectral with OAS ruleset
        let output = Command::new(&self.spectral_path)
            .args(&["lint", spec_path.to_str().unwrap()])
            .args(&["--ruleset", "@stoplight/spectral-oas"])
            .output()
            .await?;
        
        parse_spectral_output(output)
    }
}
```

### Level B: Security Linting
```yaml
# security-rules.yaml for Spectral
extends: [[spectral:oas, all]]

rules:
  no-http-servers:
    description: "Server URLs must use HTTPS"
    given: "$.servers[*].url"
    then:
      function: pattern
      functionOptions:
        match: "^https://"
    severity: error

  operation-security-defined:
    description: "All operations must define security"
    given: "$.paths[*][*]"
    then:
      field: security
      function: truthy
    severity: error

  no-private-ip-servers:
    description: "Server URLs must not use private IPs"
    given: "$.servers[*].url"
    then:
      function: pattern
      functionOptions:
        notMatch: "(localhost|127\\.0\\.0\\.1|192\\.168\\.|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)"
    severity: error
```

### Level C: Governance/Breaking Changes
```rust
pub struct GovernanceValidator {
    oasdiff_path: PathBuf,
}

impl GovernanceValidator {
    pub async fn check_breaking_changes(
        &self,
        old_spec: &Path,
        new_spec: &Path,
    ) -> Result<BreakingChangeReport> {
        let output = Command::new(&self.oasdiff_path)
            .args(&["breaking", old_spec.to_str().unwrap(), new_spec.to_str().unwrap()])
            .output()
            .await?;
        
        parse_oasdiff_output(output)
    }
}
```

## 4. JSON Schema Version Handling

### OAS 3.1 Specific Handling
```rust
pub struct JsonSchemaValidator {
    version: SpecVersion,
}

impl JsonSchemaValidator {
    pub fn validate_schema(&self, schema: &Value) -> Result<()> {
        match &self.version {
            SpecVersion::OpenAPI3_1(_) => {
                // OAS 3.1 uses JSON Schema 2020-12
                self.validate_json_schema_2020_12(schema)
            }
            _ => {
                // OAS 2.0 and 3.0.x use JSON Schema Draft 4 subset
                self.validate_json_schema_draft4_subset(schema)
            }
        }
    }
}
```

## 5. Safe External Reference Handling

### Reference Validator
```rust
pub struct ReferenceValidator {
    allowed_domains: Vec<String>,
    max_depth: usize,
}

impl ReferenceValidator {
    pub fn validate_reference(&self, ref_url: &str) -> Result<()> {
        // Use existing security validation
        validate_url(ref_url)?;
        
        // Check against allowlist
        let url = Url::parse(ref_url)?;
        if let Some(host) = url.host_str() {
            if !self.allowed_domains.iter().any(|d| host.ends_with(d)) {
                return Err(anyhow!("External reference not in allowlist: {}", host));
            }
        }
        
        Ok(())
    }
}
```

## 6. Tool Version Management

### Cargo.toml Dependencies
```toml
[dependencies]
spectral-rs = "=0.5.0"  # Pin exact version
oasdiff = "=1.2.0"      # Pin exact version

[dev-dependencies]
# For testing against known spec versions
openapi-test-specs = "=1.0.0"
```

### Version Tracking Script
```bash
#!/bin/bash
# check-tool-updates.sh

echo "Checking for validation tool updates..."

# Check Spectral
CURRENT_SPECTRAL=$(grep "spectral-rs" Cargo.toml | grep -o '"[^"]*"')
LATEST_SPECTRAL=$(cargo search spectral-rs --limit 1 | grep -o "= \"[^\"]*\"")

if [ "$CURRENT_SPECTRAL" != "$LATEST_SPECTRAL" ]; then
    echo "Spectral update available: $CURRENT_SPECTRAL -> $LATEST_SPECTRAL"
fi

# Similar for other tools...
```

## Implementation Steps

### Phase 1: Core Validation (Week 1)
1. Add version detection to parser
2. Integrate Spectral for OAS compliance
3. Implement basic validation command

### Phase 2: Security Rules (Week 2)
1. Create custom Spectral ruleset
2. Add security validation level
3. Integrate with existing security module

### Phase 3: Governance (Week 3)
1. Integrate oasdiff for breaking changes
2. Add diff validation to CI/CD
3. Create governance reports

### Phase 4: Polish (Week 4)
1. Improve error messages
2. Add validation caching
3. Create comprehensive tests

## CLI Integration

### New Commands
```bash
# Validate a spec
mrapids validate spec api.yaml --level all

# Check for breaking changes
mrapids validate diff old-api.yaml new-api.yaml

# Validate with custom rules
mrapids validate spec api.yaml --ruleset ./my-rules.yaml
```

### Integration with Existing Commands
```rust
// In init command
pub fn init_project(cmd: InitCommand) -> Result<()> {
    // ... download/load spec ...
    
    // Validate before proceeding
    let validator = SpecValidator::new();
    validator.validate_all_levels(&spec_path)?;
    
    // ... continue with project creation ...
}
```

## Testing Strategy

### Test Cases
1. Valid specs for each version (2.0, 3.0.x, 3.1.x)
2. Invalid specs with various errors
3. Security rule violations
4. Breaking change scenarios
5. External reference handling

### Example Test
```rust
#[test]
fn test_validates_oas_3_1_correctly() {
    let spec = r#"
    openapi: "3.1.0"
    info:
      title: Test API
      version: "1.0.0"
    paths:
      /test:
        get:
          operationId: getTest
          responses:
            '200':
              description: OK
    "#;
    
    let validator = SpecValidator::new();
    let result = validator.validate(spec);
    
    assert!(result.is_ok());
    assert_eq!(result.unwrap().version, SpecVersion::OpenAPI3_1("3.1.0".to_string()));
}
```

## Benefits

1. **Reliability**: Catch spec errors before they cause runtime issues
2. **Security**: Enforce security best practices automatically
3. **Governance**: Prevent breaking changes from slipping through
4. **Developer Experience**: Clear, actionable error messages
5. **Standards Compliance**: Ensure specs follow official standards

## Conclusion

This implementation plan provides a robust, multi-layered validation system that leverages proven tools while maintaining MicroRapid's ease of use. The phased approach allows for incremental delivery while building toward a comprehensive solution.