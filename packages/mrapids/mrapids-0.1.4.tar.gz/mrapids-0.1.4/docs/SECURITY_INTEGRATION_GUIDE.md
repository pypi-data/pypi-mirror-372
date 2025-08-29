# Security Integration Guide

This guide shows how to integrate the new security features into the MicroRapid CLI to prevent SSRF, local file theft, and insecure configurations.

## 1. HTTP Client Integration

Replace the standard `reqwest::Client` with `SecureHttpClient`:

### Before (Insecure):
```rust
// In src/core/request_runner.rs
let client = Client::new();
let response = client.get(url).send().await?;
```

### After (Secure):
```rust
use crate::core::secure_client::SecureHttpClient;
use crate::security::SecurityConfig;

// Load security config
let security_config = SecurityConfig::load()?;
let secure_client = SecureHttpClient::new(security_config)?;

// Make secure request
let response = secure_client.get(url).await?;
```

## 2. File Operations Integration

Replace direct file operations with sandboxed operations:

### Before (Insecure):
```rust
// Direct file read
let content = fs::read_to_string(path)?;

// Direct file write
fs::write(output_path, content)?;
```

### After (Secure):
```rust
use crate::security::FileSandbox;

// Initialize sandbox
let sandbox = FileSandbox::new(project_root)?;

// Sandboxed file read
let safe_path = sandbox.validate_read_path(path)?;
let content = fs::read_to_string(&safe_path.path)?;

// Sandboxed file write
let safe_output = sandbox.validate_write_path(output_path)?;
fs::write(&safe_output.path, content)?;
```

## 3. Environment Variable Validation

### Before (Insecure):
```rust
let api_key = env::var("API_KEY")?;
let base_url = env::var("BASE_URL")?;
```

### After (Secure):
```rust
use crate::security::{UrlValidator, SecurityError};

// Validate environment variables
fn load_secure_env() -> Result<Config, SecurityError> {
    let validator = UrlValidator::default();
    
    // Validate API key format
    let api_key = env::var("API_KEY")
        .map_err(|_| SecurityError::ConfigError("API_KEY not set".into()))?;
    
    if api_key.contains("://") || api_key.contains("@") {
        return Err(SecurityError::ConfigError("Invalid API key format".into()));
    }
    
    // Validate base URL
    if let Ok(base_url) = env::var("BASE_URL") {
        validator.validate(&base_url)?;
    }
    
    Ok(config)
}
```

## 4. Request Builder Integration

Update the request building logic:

```rust
// In src/core/run_v2.rs or request_runner.rs
pub async fn execute_request(
    spec: &OpenApiSpec,
    operation_id: &str,
    params: &HashMap<String, String>,
) -> Result<Response> {
    // Load security config
    let security_config = SecurityConfig::load()?;
    let secure_client = SecureHttpClient::new(security_config)?;
    
    // Build URL with parameters
    let url = build_url(spec, operation_id, params)?;
    
    // Make secure request
    match method {
        "GET" => secure_client.get(&url).await,
        "POST" => {
            let body = build_body(params)?;
            
            // Validate request size
            secure_client.validate_request_size(body.len())?;
            
            let request = secure_client.post(&url).await?;
            secure_client.execute_with_limits(request.body(body)).await
        }
        _ => Err("Unsupported method".into()),
    }
}
```

## 5. Configuration Loading

Update configuration loading to use secure defaults:

```rust
// In src/core/config.rs
pub fn load_config() -> Result<AppConfig> {
    // Load security config
    let security_config = SecurityConfig::load()
        .unwrap_or_else(|_| SecurityConfig::default());
    
    // Apply secure defaults
    let config = AppConfig {
        timeout: Duration::from_millis(security_config.limits.request_timeout),
        max_redirects: security_config.network.max_redirects,
        verify_tls: security_config.tls.verify,
        ..Default::default()
    };
    
    Ok(config)
}
```

## 6. Update Main Entry Points

### CLI Main (src/main.rs):
```rust
use mrapids::security::SecurityConfig;

fn main() -> Result<()> {
    // Initialize security on startup
    if !Path::new(".mrapids/security.toml").exists() {
        SecurityConfig::save_defaults(&PathBuf::from(".mrapids/security.toml"))?;
        println!("Created default security configuration at .mrapids/security.toml");
    }
    
    // Continue with normal CLI execution
    let cli = Cli::parse();
    // ...
}
```

### Agent Main (agent/src/main.rs):
```rust
use mrapids::security::{SecurityConfig, FileSandbox};

#[tokio::main]
async fn main() -> Result<()> {
    // Load security config
    let security_config = SecurityConfig::load()?;
    
    // Initialize file sandbox
    let project_root = env::current_dir()?;
    let sandbox = FileSandbox::new(project_root)?;
    
    // Pass to MCP server
    let server = McpServer::new(security_config, sandbox);
    // ...
}
```

## 7. Testing Security Features

Add security tests to your test suite:

```rust
#[cfg(test)]
mod security_tests {
    use super::*;
    
    #[test]
    fn test_blocks_ssrf_attempts() {
        let config = SecurityConfig::default();
        let client = SecureHttpClient::new(config).unwrap();
        
        // Should block local URLs
        assert!(client.get("http://localhost/admin").await.is_err());
        assert!(client.get("http://127.0.0.1:22").await.is_err());
        assert!(client.get("http://169.254.169.254/").await.is_err());
    }
    
    #[test]
    fn test_prevents_path_traversal() {
        let sandbox = FileSandbox::new(PathBuf::from(".")).unwrap();
        
        // Should block traversal attempts
        assert!(sandbox.validate_read_path("../../../etc/passwd").is_err());
        assert!(sandbox.validate_read_path("/etc/shadow").is_err());
    }
}
```

## 8. Migration Checklist

- [ ] Replace all `reqwest::Client` with `SecureHttpClient`
- [ ] Wrap all file operations with `FileSandbox`
- [ ] Add URL validation to all user-provided URLs
- [ ] Validate environment variables on startup
- [ ] Add request/response size limits
- [ ] Enable TLS verification by default
- [ ] Add security tests to CI/CD
- [ ] Document security configuration options
- [ ] Add security warnings for dangerous operations

## 9. Security Warnings

Add warnings for potentially dangerous operations:

```rust
// When user disables TLS verification
if !config.tls.verify {
    eprintln!("⚠️  WARNING: TLS verification disabled. This is insecure!");
}

// When accessing private IPs (if allowed via override)
if is_private_ip(&url) {
    eprintln!("⚠️  WARNING: Accessing private IP address");
}

// When file access is outside normal directories
if !is_standard_dir(&path) {
    eprintln!("⚠️  WARNING: Accessing non-standard directory");
}
```

## 10. Gradual Rollout

1. **Phase 1**: Add security module without breaking changes
2. **Phase 2**: Add warnings for insecure operations
3. **Phase 3**: Enable security by default with opt-out
4. **Phase 4**: Remove opt-out, security always enabled