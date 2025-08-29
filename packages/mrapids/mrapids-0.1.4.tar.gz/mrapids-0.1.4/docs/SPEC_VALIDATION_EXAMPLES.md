# Specification Validation Examples

## Current State vs. Proposed State

### Current Implementation
```rust
// Simple format detection
pub fn parse_spec(content: &str) -> Result<UnifiedSpec> {
    if content.contains("\"openapi\"") || content.contains("openapi:") {
        parse_openapi_v3(content)
    } else if content.contains("\"swagger\"") || content.contains("swagger:") {
        parse_swagger_v2(content)
    } else {
        Err(anyhow!("Unknown API specification format"))
    }
}
```

### Proposed Implementation
```rust
use crate::core::validation::{SpecValidator, ValidationLevel, ValidationReport};

pub fn parse_and_validate_spec(content: &str) -> Result<ValidatedSpec> {
    // Step 1: Detect version
    let version = detect_spec_version(content)?;
    
    // Step 2: Parse based on version
    let spec = match version {
        SpecVersion::Swagger2_0 => parse_swagger_v2(content)?,
        SpecVersion::OpenAPI3_0(_) => parse_openapi_v3(content)?,
        SpecVersion::OpenAPI3_1(_) => parse_openapi_v3_1(content)?,
        SpecVersion::Unknown => return Err(anyhow!("Unsupported spec version")),
    };
    
    // Step 3: Validate
    let validator = SpecValidator::new();
    let report = validator.validate(&spec, ValidationLevel::All)?;
    
    if report.has_errors() {
        return Err(anyhow!("Spec validation failed:\n{}", report.format_errors()));
    }
    
    Ok(ValidatedSpec { spec, version, report })
}
```

## Validation Module Structure

### src/core/validation/mod.rs
```rust
pub mod compliance;
pub mod security;
pub mod governance;
pub mod report;

use anyhow::Result;
use std::path::Path;

pub struct SpecValidator {
    compliance: compliance::ComplianceValidator,
    security: security::SecurityValidator,
    governance: governance::GovernanceValidator,
}

#[derive(Debug, Clone, Copy)]
pub enum ValidationLevel {
    Compliance,
    Security,
    Governance,
    All,
}

impl SpecValidator {
    pub fn new() -> Self {
        Self {
            compliance: compliance::ComplianceValidator::new(),
            security: security::SecurityValidator::new(),
            governance: governance::GovernanceValidator::new(),
        }
    }
    
    pub async fn validate_file(
        &self,
        spec_path: &Path,
        level: ValidationLevel,
    ) -> Result<ValidationReport> {
        let mut report = ValidationReport::new();
        
        match level {
            ValidationLevel::Compliance | ValidationLevel::All => {
                let compliance_result = self.compliance.validate(spec_path).await?;
                report.merge(compliance_result);
            }
            ValidationLevel::Security | ValidationLevel::All => {
                let security_result = self.security.validate(spec_path).await?;
                report.merge(security_result);
            }
            ValidationLevel::Governance => {
                // Governance requires two specs for comparison
                return Err(anyhow!("Governance validation requires diff command"));
            }
            _ => {}
        }
        
        Ok(report)
    }
}
```

## Security Rules Configuration

### security-rules.spectral.yaml
```yaml
extends: [[spectral:oas, all]]

rules:
  # Network Security
  require-https-servers:
    description: Server URLs must use HTTPS
    message: "{{path}} - Server URL must use HTTPS, found: {{value}}"
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        match: "^https://"

  no-localhost-servers:
    description: Server URLs must not use localhost
    message: "{{path}} - Server URL contains localhost: {{value}}"
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        notMatch: "(localhost|127\\.0\\.0\\.1|\\[::1\\])"

  no-private-ip-servers:
    description: Server URLs must not use private IPs
    message: "{{path}} - Server URL contains private IP: {{value}}"
    severity: error
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        notMatch: "(192\\.168\\.|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)"

  # Authentication Security
  operation-security-defined:
    description: All operations must define security
    message: "{{path}} - Operation missing security definition"
    severity: error
    given: $.paths[*][get,post,put,patch,delete]
    then:
      field: security
      function: truthy

  global-security-defined:
    description: API must define global security
    message: Global security definition is missing
    severity: warning
    given: $
    then:
      field: security
      function: truthy

  # Schema Security
  no-additional-properties-without-schema:
    description: Objects allowing additionalProperties must define their schema
    message: "{{path}} - additionalProperties needs explicit schema"
    severity: warning
    given: $..schema[?(@.type == 'object' && @.additionalProperties == true)]
    then:
      field: additionalProperties
      function: schema

  # Parameter Security
  required-parameters-have-schema:
    description: Required parameters must have schemas
    message: "{{path}} - Required parameter missing schema"
    severity: error
    given: $..parameters[?(@.required == true)]
    then:
      field: schema
      function: truthy
```

## Integration Examples

### Init Command with Validation
```rust
pub fn init_project(cmd: InitCommand) -> Result<()> {
    println!("🚀 {} Project", "Initializing".bright_cyan());
    
    let spec_content = if let Some(url) = cmd.from_url {
        println!("📥 Downloading spec from: {}", url.cyan());
        download_spec(&url)?
    } else if let Some(file) = cmd.from_file {
        println!("📄 Loading spec from: {}", file.display());
        fs::read_to_string(&file)?
    } else {
        return Err(anyhow!("No spec source provided"));
    };
    
    // NEW: Validate spec before proceeding
    println!("🔍 Validating OpenAPI specification...");
    let validator = SpecValidator::new();
    let temp_file = write_temp_spec(&spec_content)?;
    
    let validation_report = validator
        .validate_file(&temp_file, ValidationLevel::All)
        .await?;
    
    if validation_report.has_errors() {
        eprintln!("{}", "❌ Specification validation failed:".red());
        for error in validation_report.errors() {
            eprintln!("  - {}: {}", error.severity.to_string().red(), error.message);
            if let Some(path) = &error.path {
                eprintln!("    at {}", path.dimmed());
            }
        }
        return Err(anyhow!("Please fix spec errors before initializing project"));
    }
    
    if validation_report.has_warnings() {
        println!("{}", "⚠️  Specification warnings:".yellow());
        for warning in validation_report.warnings() {
            println!("  - {}", warning.message.yellow());
        }
    }
    
    println!("{} Specification is valid!", "✅".green());
    
    // Continue with project setup...
}
```

### Validate Command Implementation
```rust
pub fn validate_command(cmd: ValidateCommand) -> Result<()> {
    println!("🔍 {} Specification", "Validating".bright_cyan());
    
    let validator = SpecValidator::new();
    let runtime = tokio::runtime::Runtime::new()?;
    
    let report = runtime.block_on(async {
        validator.validate_file(&cmd.spec, cmd.level).await
    })?;
    
    // Display results
    if report.is_valid() {
        println!("{} Specification is valid!", "✅".green());
        println!("\n📊 Validation Summary:");
        println!("  Version: {}", report.spec_version.bright_blue());
        println!("  Compliance: {}", "PASSED".green());
        if cmd.level == ValidationLevel::Security || cmd.level == ValidationLevel::All {
            println!("  Security: {}", "PASSED".green());
        }
    } else {
        println!("{} Validation failed!", "❌".red());
        
        if !report.errors().is_empty() {
            println!("\n🚨 Errors:");
            for error in report.errors() {
                println!("  {} {}", "•".red(), error.message);
                if let Some(path) = &error.path {
                    println!("    at {}", path.dimmed());
                }
            }
        }
        
        if !report.warnings().is_empty() {
            println!("\n⚠️  Warnings:");
            for warning in report.warnings() {
                println!("  {} {}", "•".yellow(), warning.message);
                if let Some(path) = &warning.path {
                    println!("    at {}", path.dimmed());
                }
            }
        }
        
        return Err(anyhow!("Validation failed with {} errors, {} warnings", 
            report.error_count(), report.warning_count()));
    }
    
    // Output format options
    match cmd.output_format {
        OutputFormat::Json => {
            println!("\n{}", serde_json::to_string_pretty(&report)?);
        }
        OutputFormat::Yaml => {
            println!("\n{}", serde_yaml::to_string(&report)?);
        }
        _ => {} // Already displayed above
    }
    
    Ok(())
}
```

## Breaking Change Detection

### Diff Command with oasdiff
```rust
pub async fn diff_command(cmd: DiffCommand) -> Result<()> {
    println!("🔄 {} API Changes", "Analyzing".bright_cyan());
    
    let validator = GovernanceValidator::new();
    let report = validator
        .check_breaking_changes(&cmd.old_spec, &cmd.new_spec)
        .await?;
    
    if report.has_breaking_changes() {
        println!("{} Breaking changes detected!", "⚠️".red());
        
        for change in report.breaking_changes() {
            println!("\n{} {}", "•".red(), change.description.red());
            println!("  Type: {}", change.change_type.yellow());
            println!("  Path: {}", change.path.dimmed());
            
            if let Some(old) = &change.old_value {
                println!("  Old: {}", old);
            }
            if let Some(new) = &change.new_value {
                println!("  New: {}", new);
            }
        }
        
        if !cmd.allow_breaking {
            return Err(anyhow!("Breaking changes detected. Use --allow-breaking to proceed"));
        }
    } else {
        println!("{} No breaking changes detected", "✅".green());
    }
    
    // Show non-breaking changes
    if !report.non_breaking_changes().is_empty() {
        println!("\n📝 Non-breaking changes:");
        for change in report.non_breaking_changes() {
            println!("  {} {}", "•".green(), change.description);
        }
    }
    
    Ok(())
}
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: API Validation

on:
  pull_request:
    paths:
      - 'specs/**/*.yaml'
      - 'specs/**/*.json'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install MicroRapid
        run: |
          curl -sSL https://install.microrapid.com | sh
          
      - name: Validate Specs
        run: |
          for spec in specs/**/*.{yaml,json}; do
            echo "Validating $spec..."
            mrapids validate spec "$spec" --level all
          done
          
      - name: Check Breaking Changes
        if: github.event_name == 'pull_request'
        run: |
          # Get the base branch spec
          git checkout ${{ github.base_ref }}
          cp specs/api.yaml /tmp/base-api.yaml
          
          # Get the PR spec
          git checkout ${{ github.head_ref }}
          
          # Check for breaking changes
          mrapids validate diff /tmp/base-api.yaml specs/api.yaml
```

## Benefits Summary

1. **Early Error Detection**: Catch spec issues before runtime
2. **Security by Default**: Enforce HTTPS, auth requirements automatically
3. **API Governance**: Prevent accidental breaking changes
4. **Better Developer Experience**: Clear, actionable error messages
5. **Standards Compliance**: Ensure specs follow official OpenAPI standards
6. **Tool Ecosystem**: Leverage battle-tested validation tools