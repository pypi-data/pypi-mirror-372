# Security Analysis: All MicroRapid Commands

## Command Risk Matrix

| Command | HTTP Requests | File Read | File Write | Risk Level | Security Status |
|---------|--------------|-----------|------------|------------|-----------------|
| `init` | ✅ Yes (--from-url) | ✅ Yes (--from-file) | ✅ Yes | **HIGH** | ✅ SECURED |
| `run` | ✅ Yes | ✅ Yes (specs) | ❌ No | **HIGH** | ✅ SECURED |
| `test` | ✅ Yes | ✅ Yes (specs) | ✅ Yes (results) | **HIGH** | ❌ NOT SECURED |
| `analyze` | ❌ No | ✅ Yes (specs) | ✅ Yes (backup) | **MEDIUM** | ❌ NOT SECURED |
| `generate` | ❌ No | ✅ Yes (specs) | ✅ Yes (code) | **MEDIUM-HIGH** | ❌ NOT SECURED |
| `setup-tests` | ❌ No | ✅ Yes (specs) | ✅ Yes (tests) | **MEDIUM** | ❌ NOT SECURED |
| `list` | ❌ No | ✅ Yes (specs) | ❌ No | **LOW** | ❌ NOT SECURED |
| `show` | ❌ No | ✅ Yes (specs) | ❌ No | **LOW** | ❌ NOT SECURED |
| `cleanup` | ❌ No | ❌ No | ✅ Yes (delete) | **MEDIUM** | ❌ NOT SECURED |
| `init-config` | ❌ No | ❌ No | ✅ Yes (config) | **LOW** | ❌ NOT SECURED |
| `auth` | ✅ Yes (OAuth) | ✅ Yes (tokens) | ✅ Yes (tokens) | **HIGH** | ❌ NOT SECURED |
| `explore` | ❌ No | ✅ Yes (specs) | ❌ No | **LOW** | ❌ NOT SECURED |
| `flatten` | ✅ Yes ($ref URLs) | ✅ Yes (specs) | ✅ Yes (output) | **HIGH** | ❌ NOT SECURED |
| `validate` | ❌ No | ✅ Yes (specs) | ❌ No | **LOW** | ❌ NOT SECURED |
| `sdk` | ❌ No | ✅ Yes (specs) | ✅ Yes (SDK) | **MEDIUM** | ❌ NOT SECURED |
| `diff` | ❌ No | ✅ Yes (2 specs) | ❌ No | **LOW** | ❌ NOT SECURED |
| `resolve` | ✅ Yes? ($ref) | ✅ Yes (specs) | ✅ Yes (output) | **MEDIUM-HIGH** | ❌ NOT SECURED |

## Detailed Security Analysis

### 1. `test` Command - **HIGH RISK** ❌
```bash
mrapids test api.yaml --all --base-url http://internal-service
```
**Risks:**
- Makes HTTP requests to test operations (same as `run`)
- Could access internal services
- Could be used to scan internal networks

**Required Security:**
- Same URL validation as `run` command
- Validate base URLs and overrides

### 2. `analyze` Command - **MEDIUM RISK** ❌
```bash
mrapids analyze ../../../sensitive/api.yaml --backup
```
**Risks:**
- Reads spec files from arbitrary paths
- Creates backup directories
- Path traversal vulnerability

**Required Security:**
- File path sandboxing for input specs
- Validate backup directory paths

### 3. `generate` Command - **MEDIUM-HIGH RISK** ❌
```bash
mrapids generate sdk --spec /etc/passwd --output /usr/local/bin/
```
**Risks:**
- Reads spec files from arbitrary paths
- Writes generated code to arbitrary locations
- Could overwrite system files

**Required Security:**
- Sandbox spec file reads
- Sandbox output directory writes
- Validate file extensions

### 4. `setup-tests` Command - **MEDIUM RISK** ❌
```bash
mrapids setup-tests ../../private/api.yaml --output /tmp/tests
```
**Risks:**
- Reads spec files
- Writes test files to arbitrary locations
- Could expose sensitive API details

**Required Security:**
- File path validation for specs
- Output directory sandboxing

### 5. `cleanup` Command - **MEDIUM RISK** ❌
```bash
mrapids cleanup --path /etc --force
```
**Risks:**
- Deletes files/directories
- Could delete system files if misconfigured
- Path traversal risk

**Required Security:**
- Strict path validation
- Prevent system directory access
- Confirm dangerous operations

### 6. `auth` Command - **HIGH RISK** ❌
```bash
mrapids auth oauth2 --provider evil --callback-url http://attacker.com
```
**Risks:**
- Makes OAuth requests to external providers
- Stores tokens locally
- SSRF via OAuth redirects

**Required Security:**
- Validate OAuth provider URLs
- Validate callback URLs
- Secure token storage

### 7. `flatten` Command - **HIGH RISK** ❌
```bash
mrapids flatten spec.yaml --output flat.yaml
```
**Risks:**
- Downloads external $ref URLs
- Could access internal schemas
- SSRF via $ref resolution

**Required Security:**
- Validate all $ref URLs
- Block internal/metadata URLs
- Sandbox file operations

### 8. `resolve` Command - **MEDIUM-HIGH RISK** ❌
```bash
mrapids resolve spec.yaml --output resolved.yaml
```
**Risks:**
- Similar to flatten - resolves $refs
- Downloads external references
- File write operations

**Required Security:**
- URL validation for external $refs
- File sandboxing

### 9. `list` Command - **LOW RISK** ❌
```bash
mrapids list operations --spec ../../../etc/passwd
```
**Risks:**
- Reads spec files
- Information disclosure
- Path traversal

**Required Security:**
- Basic file path validation
- Sandbox spec reads

### 10. `show` Command - **LOW RISK** ❌
```bash
mrapids show operation --spec ~/.aws/credentials
```
**Risks:**
- Reads spec files
- Could expose sensitive data
- Path traversal

**Required Security:**
- File path validation
- Prevent sensitive file access

## Priority Order for Security Integration

### 🚨 CRITICAL (Do First):
1. **`test`** - Makes HTTP requests like `run`
2. **`auth`** - OAuth flows with external URLs
3. **`flatten`** - Downloads external $ref URLs

### ⚠️ HIGH (Do Next):
4. **`generate`** - Arbitrary file writes
5. **`resolve`** - External $ref resolution
6. **`analyze`** - File reads and backups

### 🟡 MEDIUM (Do After):
7. **`setup-tests`** - File writes
8. **`cleanup`** - File deletion
9. **`sdk`** - Code generation

### 🟢 LOW (Do Last):
10. **`list`** - Read only
11. **`show`** - Read only
12. **`validate`** - Read only
13. **`diff`** - Read only
14. **`explore`** - Interactive read
15. **`init-config`** - Limited writes

## Quick Wins

Commands that need the SAME security as already implemented:

1. **`test`** → Copy security from `run` command
2. **`flatten`/`resolve`** → Copy URL validation from `run`
3. **`analyze`/`generate`/etc** → Copy file validation from `init`

## Security Code to Reuse

```rust
// For HTTP commands (test, auth, flatten):
validate_request_url(&url)?;

// For file read commands (analyze, generate, list, show):
if path.contains("..") || path.starts_with("/etc") {
    return Err(anyhow!("Invalid file path"));
}

// For file write commands (generate, setup-tests):
if output.starts_with("/usr") || output.starts_with("/etc") {
    return Err(anyhow!("Cannot write to system directories"));
}
```