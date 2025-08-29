# Remaining Security Work

## Summary of Security Status

### ✅ Already Secured (2/17 commands)
1. **`init`** - URL validation, file path checks, system directory protection
2. **`run`** - URL validation in both execution paths

### ❌ Need Security (15/17 commands)

## Priority 1: Commands Making HTTP Requests (CRITICAL)

### 1. `test` Command - CRITICAL
- **Location**: `src/core/runtime.rs` → `execute_operation()`
- **Risk**: Makes HTTP requests without validation
- **Fix**: Add same URL validation as `run` command
```rust
// In execute_operation() before client.get(&url):
validate_request_url(&base_url)?;
```

### 2. `auth` Command - CRITICAL  
- **Location**: `src/core/auth/oauth2.rs`
- **Risk**: OAuth flows to arbitrary URLs
- **Fix**: Validate provider URLs and callbacks

### 3. `flatten` Command - CRITICAL
- **Location**: `src/core/flatten.rs`
- **Risk**: Downloads external $ref URLs
- **Fix**: Validate all external reference URLs

## Priority 2: File Write Commands (HIGH)

### 4. `generate` Command
- **Location**: `src/core/generate.rs`
- **Risk**: Writes files to arbitrary paths
- **Fix**: Validate output directory isn't system path

### 5. `cleanup` Command
- **Location**: `src/utils/cleanup.rs`
- **Risk**: Deletes files/directories
- **Fix**: Strict path validation, no system dirs

### 6. `setup-tests` Command
- **Location**: `src/core/setup_tests.rs`
- **Risk**: Writes test files anywhere
- **Fix**: Sandbox output paths

## Priority 3: File Read Commands (MEDIUM)

### 7. `analyze` Command
- **Location**: `src/core/analyze_v2.rs`
- **Risk**: Reads specs from anywhere
- **Fix**: Path validation like `init --from-file`

### 8-15. Other Read-Only Commands
- `list`, `show`, `validate`, `diff`, `explore`, `resolve`, `sdk`, `init-config`
- All read spec files without path validation
- Apply same file path checks as `init`

## Quick Implementation Plan

### Step 1: Create Reusable Functions
```rust
// In a new src/utils/security.rs file:

pub fn validate_url(url: &str) -> Result<()> {
    let url_lower = url.to_lowercase();
    if url_lower.contains("localhost") || 
       url_lower.contains("169.254") ||
       url_lower.contains("192.168") {
        return Err(anyhow!("Dangerous URL blocked"));
    }
    Ok(())
}

pub fn validate_file_path(path: &Path) -> Result<()> {
    let path_str = path.to_string_lossy();
    if path_str.contains("..") || 
       path_str.starts_with("/etc") ||
       path_str.starts_with("/usr") {
        return Err(anyhow!("Invalid file path"));
    }
    Ok(())
}

pub fn validate_output_path(path: &Path) -> Result<()> {
    validate_file_path(path)?;
    // Additional checks for write operations
    let path_str = path.to_string_lossy();
    if path_str.starts_with("/bin") ||
       path_str.starts_with("/sbin") ||
       path_str.starts_with("/lib") {
        return Err(anyhow!("Cannot write to system directories"));
    }
    Ok(())
}
```

### Step 2: Apply to Each Command

1. **For HTTP commands**: Add `validate_url()` before requests
2. **For file reads**: Add `validate_file_path()` before reading
3. **For file writes**: Add `validate_output_path()` before writing

### Step 3: Test Each Command
```bash
# Test URL validation
mrapids test api.yaml --base-url http://169.254.169.254
mrapids auth oauth2 --provider malicious --callback http://localhost

# Test file path validation  
mrapids analyze /etc/passwd
mrapids generate sdk --spec ~/.ssh/id_rsa --output /usr/bin/

# Test output validation
mrapids setup-tests api.yaml --output /etc/
mrapids cleanup --path /usr --force
```

## Estimated Effort

- **1 hour**: Create reusable security functions
- **2 hours**: Apply to all 15 remaining commands
- **1 hour**: Test all commands
- **Total**: ~4 hours to fully secure the CLI

## Impact

Once complete:
- ✅ No SSRF attacks possible
- ✅ No arbitrary file access
- ✅ No system file modifications
- ✅ Safe for use in CI/CD pipelines
- ✅ Safe for use with untrusted specs