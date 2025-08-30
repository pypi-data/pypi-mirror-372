# Security Hardening Plan for MicroRapid CLI

## Overview
This document outlines the security measures to prevent SSRF, local file theft, and insecure configurations in the MicroRapid CLI.

## 1. SSRF (Server-Side Request Forgery) Prevention

### URL Validation Module
```rust
// src/security/url_validator.rs
pub struct UrlValidator {
    blocked_cidrs: Vec<IpNetwork>,
    allowed_schemes: HashSet<String>,
    allowed_ports: HashSet<u16>,
    max_redirects: u8,
}

impl UrlValidator {
    pub fn validate(&self, url: &str) -> Result<ValidatedUrl, SecurityError> {
        // 1. Parse and validate URL structure
        // 2. Check scheme (only https/http)
        // 3. Resolve DNS and check IP
        // 4. Verify not in blocked CIDR ranges
        // 5. Check port allowlist
        // 6. Return validated URL
    }
}
```

### Blocked CIDR Ranges
- `127.0.0.0/8` - Localhost
- `10.0.0.0/8` - Private network
- `172.16.0.0/12` - Private network
- `192.168.0.0/16` - Private network
- `169.254.0.0/16` - Link-local
- `::1/128` - IPv6 localhost
- `fc00::/7` - IPv6 private
- `169.254.169.254/32` - AWS metadata

### DNS Resolution Protection
```rust
pub async fn safe_dns_resolve(hostname: &str) -> Result<IpAddr, SecurityError> {
    // Resolve hostname
    let ips = lookup_host(hostname).await?;
    
    // Check each resolved IP
    for ip in ips {
        if is_private_ip(&ip) || is_metadata_endpoint(&ip) {
            return Err(SecurityError::DangerousIP(ip));
        }
    }
    
    Ok(ips[0])
}
```

### Redirect Chain Validation
```rust
pub struct RedirectGuard {
    max_redirects: u8,
    seen_urls: HashSet<String>,
}

impl RedirectGuard {
    pub fn check_redirect(&mut self, url: &str) -> Result<(), SecurityError> {
        // Validate each redirect
        // Prevent redirect loops
        // Block redirects to internal IPs
    }
}
```

## 2. Local File Theft Prevention

### File Access Sandbox
```rust
pub struct FileSandbox {
    allowed_dirs: Vec<PathBuf>,
    project_root: PathBuf,
}

impl FileSandbox {
    pub fn validate_path(&self, path: &Path) -> Result<PathBuf, SecurityError> {
        // Canonicalize path
        let canonical = path.canonicalize()?;
        
        // Check if within allowed directories
        for allowed in &self.allowed_dirs {
            if canonical.starts_with(allowed) {
                return Ok(canonical);
            }
        }
        
        Err(SecurityError::PathTraversal)
    }
}
```

### Path Traversal Prevention
```rust
pub fn safe_join(base: &Path, untrusted: &str) -> Result<PathBuf, SecurityError> {
    // Strip dangerous patterns
    let cleaned = untrusted
        .replace("..", "")
        .replace("~", "")
        .replace("//", "/");
    
    let joined = base.join(cleaned);
    let canonical = joined.canonicalize()?;
    
    // Verify still under base
    if !canonical.starts_with(base) {
        return Err(SecurityError::PathTraversal);
    }
    
    Ok(canonical)
}
```

### File Operation Restrictions
```rust
pub enum AllowedFileOp {
    ReadConfig,
    WriteGenerated,
    ReadOpenAPI,
}

pub fn check_file_permission(
    path: &Path, 
    operation: AllowedFileOp
) -> Result<(), SecurityError> {
    match operation {
        AllowedFileOp::ReadConfig => {
            // Only .yaml, .json, .toml in project
        },
        AllowedFileOp::WriteGenerated => {
            // Only in designated output dirs
        },
        AllowedFileOp::ReadOpenAPI => {
            // Only OpenAPI spec files
        }
    }
}
```

## 3. Secure Default Configurations

### Configuration Schema
```rust
#[derive(Deserialize, Validate)]
pub struct SecureConfig {
    #[validate(url)]
    api_base_url: Option<String>,
    
    #[validate(range(min = 1000, max = 300000))]
    timeout_ms: u64,
    
    #[validate(range(min = 0, max = 5))]
    max_retries: u8,
    
    #[serde(default = "secure_defaults::tls_verify")]
    tls_verify: bool,
    
    #[serde(default = "secure_defaults::max_response_size")]
    max_response_bytes: usize,
}

mod secure_defaults {
    pub fn tls_verify() -> bool { true }
    pub fn max_response_size() -> usize { 10_485_760 } // 10MB
}
```

### Environment Variable Validation
```rust
pub fn load_env_config() -> Result<EnvConfig, SecurityError> {
    // Validate API keys format
    if let Some(key) = env::var("MRAPIDS_API_KEY").ok() {
        validate_api_key_format(&key)?;
    }
    
    // Validate URLs
    if let Some(url) = env::var("MRAPIDS_BASE_URL").ok() {
        UrlValidator::default().validate(&url)?;
    }
    
    // No secrets in URLs
    check_no_secrets_in_env()?;
    
    Ok(config)
}
```

### Request Limits
```rust
pub struct RequestLimits {
    pub max_body_size: usize,      // 10MB default
    pub max_header_size: usize,    // 8KB default
    pub timeout: Duration,         // 30s default
    pub max_redirects: u8,         // 5 default
}

impl Default for RequestLimits {
    fn default() -> Self {
        Self {
            max_body_size: 10 * 1024 * 1024,
            max_header_size: 8 * 1024,
            timeout: Duration::from_secs(30),
            max_redirects: 5,
        }
    }
}
```

## 4. Implementation Checklist

### Phase 1: URL Validation
- [ ] Implement UrlValidator with CIDR blocking
- [ ] Add DNS resolution checks
- [ ] Create redirect chain validator
- [ ] Add unit tests for all edge cases

### Phase 2: File Sandboxing
- [ ] Implement FileSandbox with path validation
- [ ] Add path traversal prevention
- [ ] Create file operation permission system
- [ ] Test with symbolic links and hard links

### Phase 3: Secure Defaults
- [ ] Create secure configuration schema
- [ ] Add environment variable validation
- [ ] Implement request size/timeout limits
- [ ] Add configuration validation on startup

### Phase 4: Integration
- [ ] Integrate validators into HTTP client
- [ ] Add security checks to file operations
- [ ] Create security audit logging
- [ ] Add security tests to CI/CD

## 5. Security Configuration File

Create `.mrapids/security.toml`:
```toml
[network]
# Schemes allowed for API calls
allowed_schemes = ["https", "http"]

# Ports allowed for connections
allowed_ports = [80, 443, 8080, 8443]

# Maximum redirects to follow
max_redirects = 5

# Blocked IP ranges (CIDR notation)
blocked_cidrs = [
    "127.0.0.0/8",
    "10.0.0.0/8",
    "172.16.0.0/12",
    "192.168.0.0/16",
    "169.254.0.0/16",
    "::1/128",
    "fc00::/7"
]

[files]
# Directories where files can be read
allowed_read_dirs = [".", "./config", "./specs"]

# Directories where files can be written
allowed_write_dirs = ["./output", "./generated", "./.mrapids"]

# File extensions allowed for reading
allowed_extensions = [".yaml", ".yml", ".json", ".toml"]

[limits]
# Maximum response size (bytes)
max_response_size = 10485760  # 10MB

# Request timeout (milliseconds)
request_timeout = 30000  # 30s

# Maximum request body size
max_request_size = 1048576  # 1MB

[tls]
# Verify TLS certificates
verify = true

# Minimum TLS version
min_version = "1.2"
```

## 6. Example Usage

```rust
// Before making any HTTP request
let validator = UrlValidator::from_config(&security_config);
let validated_url = validator.validate(&user_provided_url)?;

// Before any file operation
let sandbox = FileSandbox::from_config(&security_config);
let safe_path = sandbox.validate_path(&user_provided_path)?;

// Load config with validation
let config = SecureConfig::load()?;
```

## 7. Testing Strategy

### SSRF Tests
```rust
#[test]
fn test_blocks_localhost() {
    assert!(validator.validate("http://localhost/api").is_err());
    assert!(validator.validate("http://127.0.0.1/api").is_err());
    assert!(validator.validate("http://[::1]/api").is_err());
}

#[test]
fn test_blocks_private_ips() {
    assert!(validator.validate("http://10.0.0.1/api").is_err());
    assert!(validator.validate("http://192.168.1.1/api").is_err());
    assert!(validator.validate("http://172.16.0.1/api").is_err());
}

#[test]
fn test_blocks_metadata_endpoints() {
    assert!(validator.validate("http://169.254.169.254/").is_err());
    assert!(validator.validate("http://metadata.google.internal/").is_err());
}
```

### Path Traversal Tests
```rust
#[test]
fn test_blocks_path_traversal() {
    assert!(sandbox.validate_path("../../../etc/passwd").is_err());
    assert!(sandbox.validate_path("/etc/passwd").is_err());
    assert!(sandbox.validate_path("~/.ssh/id_rsa").is_err());
}
```

## 8. Security Headers for HTTP Client

```rust
pub fn secure_http_client() -> Client {
    Client::builder()
        .user_agent("MicroRapid/1.0")
        .default_headers(headers)
        .timeout(Duration::from_secs(30))
        .redirect(Policy::limited(5))
        .danger_accept_invalid_certs(false)
        .build()
        .unwrap()
}
```