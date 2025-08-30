# `mrapids init` Command Security Analysis

## Overview

The `init` command has several security risks that need to be addressed:

```bash
# Usage examples that pose risks:
mrapids init my-project --from-url http://evil.com/malicious-spec.yaml
mrapids init ../../../sensitive-location --force
mrapids init /etc/systemd/system --template rest
```

## Security Risks Identified

### 1. **URL Downloads (HIGH RISK)**

The command can download schemas from arbitrary URLs:

```rust
// In src/core/init.rs
fn download_schema(url: &str) -> Result<Option<(String, bool)>> {
    let client = Client::new();  // ❌ No URL validation!
    let response = client.get(url)
        .send()?;
}
```

**Risks:**
- SSRF attacks: `--from-url http://169.254.169.254/latest/meta-data`
- Internal service access: `--from-url http://internal-db:5432`
- Malicious redirects to private IPs
- Large file DoS: Downloading gigabyte-sized "schemas"

### 2. **Directory Traversal (MEDIUM RISK)**

The command creates directories based on user input:

```rust
let project_path = Path::new(&cmd.name);  // ❌ No path validation!
fs::create_dir_all(project_path)?;
```

**Risks:**
- Creating projects in system directories: `init /usr/local/bin/backdoor`
- Overwriting sensitive locations with `--force`
- Path traversal: `init ../../../etc/my-project`

### 3. **File Write Operations (MEDIUM RISK)**

The command writes multiple files without sandboxing:

```rust
fs::write(base.join("mrapids.yaml"), config)?;
fs::write(base.join("specs/api.yaml"), spec)?;
fs::write(base.join("config/.env.example"), env)?;
```

**Risks:**
- Writing outside intended directories
- Overwriting existing files with `--force`
- No file extension validation

### 4. **Local File Reads (LOW-MEDIUM RISK)**

With `--from-file` option:

```rust
fn load_local_schema(file_path: &str) -> Result<Option<(String, bool)>> {
    let content = fs::read_to_string(file_path)?;  // ❌ No path validation!
}
```

**Risks:**
- Reading sensitive files: `--from-file /etc/passwd`
- Information disclosure through error messages

## Required Security Measures

### 1. URL Validation for Downloads

```rust
use crate::security::UrlValidator;

fn download_schema(url: &str) -> Result<Option<(String, bool)>> {
    // Validate URL before downloading
    let validator = UrlValidator::default();
    let validated = validator.validate_with_dns(url).await?;
    
    // Use secure client with size limits
    let secure_client = SecureHttpClient::from_defaults()?;
    let response = secure_client.get(url).await?;
    
    // Check content-length before reading
    if let Some(size) = response.content_length() {
        if size > 10_485_760 { // 10MB limit for schemas
            return Err(anyhow!("Schema too large: {} bytes", size));
        }
    }
}
```

### 2. Project Path Sandboxing

```rust
use crate::security::FileSandbox;

pub fn init_project(cmd: InitCommand) -> Result<()> {
    // Validate project name/path
    let sandbox = FileSandbox::new(std::env::current_dir()?)?;
    
    // Ensure project path is safe
    let safe_project_path = if cmd.name.contains('/') || cmd.name.contains('\\') {
        // User provided a path, validate it
        sandbox.validate_write_path(&cmd.name)?
    } else {
        // Just a name, safe to use
        SafePath { path: PathBuf::from(&cmd.name) }
    };
    
    // Prevent system directories
    let forbidden_paths = ["/etc", "/usr", "/bin", "/sbin", "/var", "/opt"];
    let canonical = safe_project_path.path.canonicalize()?;
    for forbidden in &forbidden_paths {
        if canonical.starts_with(forbidden) {
            return Err(anyhow!("Cannot create project in system directory"));
        }
    }
}
```

### 3. File Operation Sandboxing

```rust
// Instead of direct fs::write
fn write_project_file(base: &Path, relative_path: &str, content: &str) -> Result<()> {
    let sandbox = FileSandbox::new(base.to_path_buf())?;
    let safe_path = sandbox.validate_write_path(relative_path)?;
    fs::write(safe_path.path, content)?;
    Ok(())
}

// Use it for all file writes
write_project_file(&project_path, "mrapids.yaml", config)?;
write_project_file(&project_path, "specs/api.yaml", spec)?;
```

### 4. Schema File Validation

```rust
fn load_local_schema(file_path: &str) -> Result<Option<(String, bool)>> {
    let sandbox = FileSandbox::new(std::env::current_dir()?)?;
    let safe_path = sandbox.validate_read_path(file_path)?;
    
    // Check file size before reading
    let metadata = fs::metadata(&safe_path.path)?;
    if metadata.len() > 10_485_760 { // 10MB limit
        return Err(anyhow!("Schema file too large"));
    }
    
    let content = fs::read_to_string(safe_path.path)?;
    Ok(Some((content, file_path.ends_with(".json"))))
}
```

## Attack Scenarios Prevented

With security measures in place:

```bash
# SSRF attempt - BLOCKED
mrapids init my-api --from-url http://169.254.169.254/latest/
❌ Error: Blocked IP address: 169.254.169.254

# Path traversal - BLOCKED  
mrapids init ../../../etc/systemd/system/backdoor
❌ Error: Path traversal attempt detected

# System directory write - BLOCKED
mrapids init /usr/local/bin/evil --force
❌ Error: Cannot create project in system directory

# Sensitive file read - BLOCKED
mrapids init my-api --from-file /etc/shadow
❌ Error: File access denied: /etc/shadow

# Large file DoS - BLOCKED
mrapids init my-api --from-url http://evil.com/10gb.yaml
❌ Error: Schema too large: 10737418240 bytes
```

## Priority

**MEDIUM-HIGH**: While not as critical as `run` or `test` commands that make arbitrary API calls, `init` can:
- Download from arbitrary URLs (SSRF risk)
- Write files to arbitrary locations (potential backdoor creation)
- Read local files (information disclosure)

The command should be secured before the others because it's often the first command users run, and compromising project initialization could affect all subsequent operations.