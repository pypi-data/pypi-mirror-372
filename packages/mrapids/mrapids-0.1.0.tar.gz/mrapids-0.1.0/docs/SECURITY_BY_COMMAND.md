# Security Implementation by Command

## Summary Table

| Command | URL Validation | File Read | File Write | Delete | Security Level |
|---------|---------------|-----------|------------|--------|----------------|
| `init` | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | **HIGH** |
| `run` | ✅ Yes | ✅ Yes | ❌ No | ❌ No | **HIGH** |
| `test` | ✅ Yes | ✅ Yes | ❌ No | ❌ No | **HIGH** |
| `auth` | ✅ Yes | ❌ No | ❌ No | ❌ No | **HIGH** |
| `flatten` | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No | **HIGH** |
| `generate` | ❌ No | ✅ Yes | ✅ Yes | ❌ No | **MEDIUM** |
| `analyze` | ❌ No | ✅ Yes | ✅ Yes | ❌ No | **MEDIUM** |
| `cleanup` | ❌ No | ❌ No | ❌ No | ✅ Yes | **MEDIUM** |
| `list` | ❌ No | ✅ Yes | ❌ No | ❌ No | **LOW** |
| `show` | ❌ No | ✅ Yes | ❌ No | ❌ No | **LOW** |

## Detailed Security by Command

### `init` Command
```rust
// URL validation for --from-url
validate_url(&url)?

// File path validation for --from-file
validate_file_path(&path)?

// Project path validation
if path.starts_with("/etc") || path.starts_with("/usr") {
    return Err("Cannot create project in system directory")
}
```

### `run` Command
```rust
// In run_v2.rs
validate_request_url(&base_url)?

// In request_runner.rs
validate_request_url(&base_url)?
```

### `test` Command
```rust
// In runtime.rs
validate_url(base_url)?
```

### `auth` Command
```rust
// OAuth URL validation
validate_url(&config.auth_url)?
validate_url(&config.token_url)?
```

### `flatten` Command
```rust
// External reference validation
validate_url(url)?
validate_file_path(&path)?
validate_output_path(&output_path)?
```

### `generate` Command
```rust
// Input/output validation
validate_file_path(&cmd.spec)?
validate_output_path(&cmd.output)?
```

### `analyze` Command
```rust
// Spec and output validation
validate_file_path(&cmd.spec)?
validate_output_path(&cmd.output)?
```

### `cleanup` Command
```rust
// Deletion validation
validate_delete_path(base_path)?
validate_delete_path(&path)? // For each file/dir
```

### `list` Command
```rust
// Spec file validation
validate_file_path(spec_file)?
```

### `show` Command
```rust
// Spec file validation
validate_file_path(&spec_path)?
```

## Agent MCP Security

### `run_operation` Function
```rust
// Base URL validation
validate_url(&base_url)?

// Request URL validation
validate_url(url)?
```

## Security Functions

### URL Validation
- Blocks localhost, private IPs, metadata endpoints
- Only allows HTTP/HTTPS schemes
- Prevents SSRF attacks

### File Path Validation
- Blocks path traversal (.., ~)
- Prevents access to sensitive files
- Platform-specific protections

### Output Path Validation
- All file path checks plus:
- Prevents writes to system directories
- Protects critical system paths

### Delete Path Validation
- All output path checks plus:
- Prevents deletion of root directories
- Extra protection for critical paths