# Quick Start: Spectral Integration

## Step 1: Install Spectral

```bash
# Via npm (most common)
npm install -g @stoplight/spectral-cli

# Via yarn
yarn global add @stoplight/spectral-cli

# Via brew (macOS)
brew install stoplight/tap/spectral

# Verify installation
spectral --version
```

## Step 2: Create Basic Integration

### src/core/validation/spectral.rs
```rust
use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::path::Path;
use std::process::Command;

#[derive(Debug, Deserialize, Serialize)]
pub struct SpectralResult {
    pub code: String,
    pub message: String,
    pub path: Vec<String>,
    pub severity: u8, // 0=error, 1=warning, 2=info, 3=hint
    pub source: String,
    pub range: SpectralRange,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct SpectralRange {
    pub start: Position,
    pub end: Position,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct Position {
    pub line: u32,
    pub character: u32,
}

pub struct SpectralValidator {
    spectral_path: String,
    ruleset_path: Option<String>,
}

impl SpectralValidator {
    pub fn new() -> Result<Self> {
        // Find spectral executable
        let spectral_path = which::which("spectral")
            .context("Spectral CLI not found. Install with: npm install -g @stoplight/spectral-cli")?
            .to_string_lossy()
            .to_string();
        
        Ok(Self {
            spectral_path,
            ruleset_path: None,
        })
    }
    
    pub fn with_ruleset(mut self, ruleset: &str) -> Self {
        self.ruleset_path = Some(ruleset.to_string());
        self
    }
    
    pub fn validate(&self, spec_path: &Path) -> Result<Vec<SpectralResult>> {
        let mut cmd = Command::new(&self.spectral_path);
        cmd.arg("lint");
        cmd.arg(spec_path);
        cmd.arg("--format").arg("json");
        
        if let Some(ruleset) = &self.ruleset_path {
            cmd.arg("--ruleset").arg(ruleset);
        }
        
        let output = cmd.output()
            .context("Failed to run Spectral")?;
        
        if output.stdout.is_empty() {
            // No issues found
            return Ok(vec![]);
        }
        
        // Parse JSON output
        let results: Vec<SpectralResult> = serde_json::from_slice(&output.stdout)
            .context("Failed to parse Spectral output")?;
        
        Ok(results)
    }
}
```

## Step 3: Create Security Ruleset

### .spectral.yaml
```yaml
extends: [[spectral:oas, all]]

rules:
  # Security Rules
  servers-use-https:
    description: Server URLs must use HTTPS
    given: $.servers[*].url
    severity: error
    then:
      function: pattern
      functionOptions:
        match: "^https://"
    message: "Server URL must use HTTPS: {{value}}"

  no-http-basic:
    description: HTTP Basic auth should not be used
    given: $.components.securitySchemes[*][?(@.type == 'http' && @.scheme == 'basic')]
    severity: warning
    message: "HTTP Basic auth is not recommended. Use OAuth2 or API keys."

  operation-security:
    description: Operations must declare security requirements
    given: $.paths[*][*]
    severity: error
    then:
      - field: security
        function: truthy
    message: "Operation must declare security requirements"

  # API Design Rules  
  operation-id-required:
    description: Every operation must have an operationId
    given: $.paths[*][*]
    severity: error
    then:
      field: operationId
      function: truthy
    message: "Operation must have an operationId"

  operation-id-kebab-case:
    description: Operation IDs must be kebab-case
    given: $.paths[*][*].operationId
    severity: warning
    then:
      function: pattern
      functionOptions:
        match: "^[a-z]+(-[a-z]+)*$"
    message: "Operation ID should be kebab-case: {{value}}"

  # Documentation Rules
  api-description:
    description: API must have a description
    given: $.info
    severity: warning
    then:
      field: description
      function: truthy
    message: "API should have a description"

  operation-description:
    description: Operations should have descriptions
    given: $.paths[*][*]
    severity: info
    then:
      field: description
      function: truthy
    message: "Operation should have a description"
```

## Step 4: Integrate with CLI

### Update validate command
```rust
use crate::cli::ValidateCommand;
use crate::core::validation::spectral::SpectralValidator;

pub fn validate_command(cmd: ValidateCommand) -> Result<()> {
    println!("🔍 Validating {} specification...", cmd.spec.display());
    
    // Create validator
    let validator = SpectralValidator::new()?;
    let validator = if let Some(ruleset) = cmd.ruleset {
        validator.with_ruleset(&ruleset)
    } else {
        validator
    };
    
    // Run validation
    let results = validator.validate(&cmd.spec)?;
    
    // Process results
    let errors: Vec<_> = results.iter().filter(|r| r.severity == 0).collect();
    let warnings: Vec<_> = results.iter().filter(|r| r.severity == 1).collect();
    
    if errors.is_empty() && warnings.is_empty() {
        println!("✅ Specification is valid!");
        return Ok(());
    }
    
    // Display errors
    if !errors.is_empty() {
        println!("\n❌ Errors found:");
        for error in errors {
            println!("  {} {}", "•".red(), error.message);
            println!("    at {}", format_path(&error.path).dimmed());
        }
    }
    
    // Display warnings
    if !warnings.is_empty() {
        println!("\n⚠️  Warnings found:");
        for warning in warnings {
            println!("  {} {}", "•".yellow(), warning.message);
            println!("    at {}", format_path(&warning.path).dimmed());
        }
    }
    
    if !errors.is_empty() {
        Err(anyhow!("{} errors, {} warnings found", errors.len(), warnings.len()))
    } else {
        Ok(())
    }
}

fn format_path(path: &[String]) -> String {
    path.join(" > ")
}
```

## Step 5: Add to Project Init

```rust
// In init.rs
pub fn init_project(cmd: InitCommand) -> Result<()> {
    // ... existing code ...
    
    // After downloading/loading spec
    if !cmd.skip_validation {
        println!("🔍 Validating specification...");
        
        let validator = SpectralValidator::new()?;
        let results = validator.validate(&spec_path)?;
        
        let errors = results.iter().filter(|r| r.severity == 0).count();
        if errors > 0 {
            eprintln!("❌ Specification has {} errors. Fix them or use --skip-validation", errors);
            return Err(anyhow!("Invalid specification"));
        }
        
        println!("✅ Specification validated successfully!");
    }
    
    // ... continue with project creation ...
}
```

## Step 6: Test the Integration

### Create test spec with issues
```yaml
# test-bad-spec.yaml
openapi: "3.0.0"
info:
  title: Test API
  version: "1.0"
servers:
  - url: http://api.example.com  # Should be HTTPS
paths:
  /users:
    get:  # Missing operationId and security
      responses:
        200:
          description: Success
```

### Run validation
```bash
# Test with built-in rules
mrapids validate spec test-bad-spec.yaml

# Expected output:
❌ Errors found:
  • Server URL must use HTTPS: http://api.example.com
    at servers > 0 > url
  • Operation must have an operationId
    at paths > /users > get
  • Operation must declare security requirements
    at paths > /users > get
```

## Benefits of This Approach

1. **Immediate Value**: Basic validation working in hours, not weeks
2. **Extensible**: Easy to add more rules as needed
3. **Community Rules**: Can use rulesets from Zalando, Adidas, etc.
4. **CI/CD Ready**: JSON output perfect for automation
5. **User Friendly**: Clear error messages with exact locations

## Next Steps

1. Add more sophisticated rules
2. Create MicroRapid-specific ruleset
3. Integrate with other commands (analyze, generate)
4. Add caching for performance
5. Bundle Spectral with MicroRapid distribution