# Validation Opt-In Design

## Philosophy: Fast by Default, Safe When Needed

### Default Behavior (Fast Path)

```bash
# No validation - Maximum speed
mrapids run get-user --id 123        # ~70ms
mrapids test get-user --params '{}'  # ~80ms
mrapids-agent start                   # Validates once at startup
```

### Opt-In Validation (Safe Path)

```bash
# User explicitly requests validation
mrapids run get-user --id 123 --validate     # ~370ms
mrapids test --all --validate                # ~400ms per test
mrapids-agent start --validate-always         # Validates every request
```

## Implementation Pattern

### 1. Add Optional Flag to Commands

```rust
// In cli/mod.rs
#[derive(Parser)]
pub struct RunCommand {
    // ... existing fields ...
    
    /// Validate spec before execution (slower but safer)
    #[arg(long, default_value = "false")]
    pub validate: bool,
    
    /// Validation level when --validate is used
    #[arg(long, value_enum, default_value = "quick")]
    pub validate_level: ValidationLevel,
}

#[derive(ValueEnum, Clone, Copy)]
pub enum ValidationLevel {
    Quick,    // ~50ms - Structure only
    Standard, // ~200ms - OAS compliance  
    Full,     // ~500ms - All rules
}
```

### 2. Conditional Validation Logic

```rust
// In run command implementation
pub async fn execute_run_command(cmd: RunCommand) -> Result<()> {
    let spec = load_spec(&cmd.spec)?;
    
    // Only validate if explicitly requested
    if cmd.validate {
        let start = Instant::now();
        println!("🔍 Validating specification (--validate flag)...");
        
        match cmd.validate_level {
            ValidationLevel::Quick => quick_validate(&spec)?,
            ValidationLevel::Standard => standard_validate(&spec).await?,
            ValidationLevel::Full => full_validate(&spec).await?,
        }
        
        println!("✅ Validated in {}ms", start.elapsed().as_millis());
    }
    
    // Continue with normal execution
    execute_operation(&spec, &cmd).await
}
```

### 3. Environment Variable Override

```bash
# For users who always want validation
export MRAPIDS_ALWAYS_VALIDATE=true
export MRAPIDS_VALIDATE_LEVEL=standard

# Now all commands validate by default
mrapids run get-user  # Will validate
```

```rust
pub fn should_validate(cmd_flag: bool) -> bool {
    // Command flag takes precedence
    if cmd_flag {
        return true;
    }
    
    // Check environment variable
    std::env::var("MRAPIDS_ALWAYS_VALIDATE")
        .map(|v| v.to_lowercase() == "true")
        .unwrap_or(false)
}
```

### 4. Configuration File Support

```yaml
# .mrapids/config.yaml
validation:
  init: true        # Always validate on init
  analyze: true     # Always validate on analyze
  generate: true    # Always validate on generate
  run: false        # Never validate on run (unless --validate)
  test: false       # Never validate on test
  default_level: standard
```

### 5. Smart Caching for Repeated Runs

```rust
use std::sync::OnceLock;

static VALIDATION_CACHE: OnceLock<Mutex<ValidationCache>> = OnceLock::new();

pub struct ValidationCache {
    entries: HashMap<PathBuf, CachedValidation>,
}

struct CachedValidation {
    file_hash: String,
    validated_at: Instant,
    result: ValidationResult,
}

impl ValidationCache {
    pub fn validate_with_cache(
        &mut self,
        spec_path: &Path,
        level: ValidationLevel,
    ) -> Result<ValidationResult> {
        let current_hash = calculate_file_hash(spec_path)?;
        
        // Check cache
        if let Some(cached) = self.entries.get(spec_path) {
            if cached.file_hash == current_hash &&
               cached.validated_at.elapsed() < Duration::from_secs(3600) {
                println!("⚡ Using cached validation result");
                return Ok(cached.result.clone());
            }
        }
        
        // Validate and cache
        let result = perform_validation(spec_path, level)?;
        self.entries.insert(spec_path.to_owned(), CachedValidation {
            file_hash: current_hash,
            validated_at: Instant::now(),
            result: result.clone(),
        });
        
        Ok(result)
    }
}
```

## Use Case Examples

### Development Workflow
```bash
# During development - validate after changes
$ vim api.yaml
$ mrapids validate spec api.yaml     # Full validation
$ mrapids run get-user --id 123      # Fast execution

# Before commit - validate everything
$ mrapids validate spec api.yaml --level full
$ git commit -m "Updated API spec"
```

### Production Deployment
```bash
# CI/CD Pipeline - Always validate
- name: Validate API Spec
  run: mrapids validate spec api.yaml --level full

# Production runtime - Skip validation for speed
$ mrapids run get-user --id $USER_ID  # No validation
```

### Debugging Issues
```bash
# Something's not working? Add validation
$ mrapids run create-order --data @order.json
Error: 400 Bad Request

# Debug with validation
$ mrapids run create-order --data @order.json --validate --validate-level full
🔍 Validating specification...
❌ Validation error: Operation 'create-order' missing required 'security' field
```

### Agent Configuration
```bash
# Development agent - validate everything
mrapids-agent start --validate-always --validate-level full

# Production agent - validate once
mrapids-agent start  # Only validates at startup

# Debug mode - selective validation
mrapids-agent start --validate-operations "create-*,update-*"
```

## Best Practices

### 1. Document the Performance Trade-off
```bash
$ mrapids run --help
OPTIONS:
  --validate    Validate spec before execution (~300ms overhead)
```

### 2. Show Validation Time
```bash
$ mrapids run get-user --validate
🔍 Validating specification...
✅ Validated in 287ms
🚀 Executing request...
```

### 3. Provide Shortcuts
```bash
# Alias for validated runs
alias mrapids-safe='mrapids --validate'

# Now users can choose
mrapids run get-user         # Fast
mrapids-safe run get-user    # Validated
```

## Summary

This opt-in approach provides:
- ⚡ **Fast by default**: No performance penalty unless requested
- 🛡️ **Safe when needed**: Full validation available on demand
- 🎯 **User control**: Explicit flags and configuration options
- 📊 **Visibility**: Clear feedback about validation overhead
- 🔧 **Flexibility**: Different validation levels for different needs

The key principle: **Don't force users to pay for validation they don't need, but make it easy when they do!**