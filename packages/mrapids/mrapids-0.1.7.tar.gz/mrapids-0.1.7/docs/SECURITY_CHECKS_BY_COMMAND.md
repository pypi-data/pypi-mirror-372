# Security Checks by Command

This document shows exactly which commands in both CLIs need security checks and where they would be applied.

## MicroRapid CLI (`mrapids`)

### Commands That Make HTTP Requests (Need URL Validation)

#### 1. `mrapids run` - **HIGH RISK**
```bash
mrapids run petstore.yaml --operation getPet --base-url http://evil.com
```
- **File**: `src/core/run_v2.rs`, `src/core/request_runner.rs`
- **Risk**: User can specify arbitrary base URLs or API endpoints
- **Checks Needed**:
  - ✅ URL validation before making requests
  - ✅ DNS resolution validation
  - ✅ Response size limits
  - ✅ Timeout enforcement

#### 2. `mrapids test` - **HIGH RISK**
```bash
mrapids test api.yaml --all --base-url http://internal.service
```
- **File**: `src/core/runtime.rs`
- **Risk**: Tests operations against provided URLs
- **Checks Needed**: Same as `run` command

#### 3. `mrapids auth` - **MEDIUM RISK**
```bash
mrapids auth oauth2 --provider github --callback-url http://localhost:8080
```
- **File**: `src/core/auth/oauth2.rs`, `src/core/auth/mod.rs`
- **Risk**: OAuth flows involve external URLs
- **Checks Needed**:
  - ✅ Validate OAuth provider URLs
  - ✅ Validate callback URLs

### Commands That Access Files (Need Sandboxing)

#### 1. `mrapids init` - **MEDIUM RISK**
```bash
mrapids init ../../../etc/project
```
- **File**: `src/core/init.rs`
- **Risk**: Creates project structure, writes files
- **Checks Needed**:
  - ✅ Validate project path is safe
  - ✅ Sandbox write operations

#### 2. `mrapids generate` - **HIGH RISK**
```bash
mrapids generate sdk --spec ../../sensitive/api.yaml --output /usr/bin/
```
- **File**: `src/core/generate.rs`, `src/core/sdk_gen/*.rs`
- **Risk**: Reads spec files, writes generated code
- **Checks Needed**:
  - ✅ Sandbox spec file reads
  - ✅ Sandbox output directory writes
  - ✅ Validate file extensions

#### 3. `mrapids analyze` - **MEDIUM RISK**
```bash
mrapids analyze ../../../private/api.yaml
```
- **File**: `src/core/analyze_v2.rs`
- **Risk**: Reads and analyzes spec files
- **Checks Needed**:
  - ✅ Sandbox spec file reads
  - ✅ Validate file paths

#### 4. `mrapids validate` - **MEDIUM RISK**
```bash
mrapids validate ~/Downloads/untrusted.yaml
```
- **File**: `src/core/validate.rs`
- **Risk**: Reads spec files for validation
- **Checks Needed**:
  - ✅ Sandbox file reads
  - ✅ Path validation

#### 5. `mrapids flatten` - **HIGH RISK**
```bash
mrapids flatten spec.yaml --output /etc/flat.yaml
```
- **File**: `src/core/flatten.rs`
- **Risk**: Reads specs with external refs, writes output
- **Checks Needed**:
  - ✅ Sandbox all file operations
  - ✅ Validate external reference URLs

#### 6. `mrapids explore` - **LOW RISK**
```bash
mrapids explore api.yaml
```
- **File**: `src/core/explore.rs`
- **Risk**: Interactive exploration, reads files
- **Checks Needed**:
  - ✅ Sandbox file reads

## MCP Agent CLI (`mrapids-agent`)

### Commands That Need Security

#### 1. `mrapids-agent start` - **CRITICAL RISK**
```bash
mrapids-agent start --spec http://evil.com/api.yaml --port 3000
```
- **File**: `agent/src/commands/start.rs`
- **Risk**: Downloads specs, starts server that processes requests
- **Checks Needed**:
  - ✅ URL validation for spec downloads
  - ✅ Sandbox spec file operations
  - ✅ Runtime request validation

#### 2. MCP Protocol Operations - **CRITICAL RISK**
When the agent is running, it processes these MCP requests:
- `call_tool` with `make_api_call` - Makes HTTP requests to arbitrary URLs
- `call_tool` with `list_operations` - Reads spec files
- `call_tool` with `get_operation_details` - Reads spec files

**Checks Needed**:
- ✅ Validate ALL URLs in API calls
- ✅ Sandbox ALL file operations
- ✅ Enforce request/response limits

## Security Check Matrix

| Command | URL Validation | File Sandboxing | Priority |
|---------|----------------|-----------------|----------|
| **mrapids CLI** |
| `run` | ✅ Required | ✅ Config files | HIGH |
| `test` | ✅ Required | ✅ Spec files | HIGH |
| `generate` | ❌ | ✅ Required | HIGH |
| `init` | ❌ | ✅ Required | MEDIUM |
| `analyze` | ❌ | ✅ Required | MEDIUM |
| `validate` | ❌ | ✅ Required | MEDIUM |
| `flatten` | ✅ External refs | ✅ Required | HIGH |
| `auth` | ✅ OAuth URLs | ✅ Token storage | MEDIUM |
| **mrapids-agent CLI** |
| `start` | ✅ Spec URL | ✅ Spec files | CRITICAL |
| MCP `make_api_call` | ✅ Required | ❌ | CRITICAL |
| MCP `list_operations` | ❌ | ✅ Required | HIGH |

## Integration Points

### For URL Validation:
```rust
// In src/core/request_runner.rs
use crate::core::secure_client::SecureHttpClient;

pub async fn make_request(url: &str, ...) -> Result<Response> {
    // Replace this:
    // let client = reqwest::Client::new();
    
    // With this:
    let client = SecureHttpClient::from_defaults()?;
    let response = client.get(url).await?;
}
```

### For File Sandboxing:
```rust
// In src/core/spec.rs
use crate::security::FileSandbox;

pub fn load_openapi_spec(path: &str) -> Result<OpenApiSpec> {
    // Add sandboxing:
    let sandbox = FileSandbox::new(std::env::current_dir()?)?;
    let safe_path = sandbox.validate_read_path(path)?;
    
    let content = fs::read_to_string(safe_path.path)?;
    // ... parse spec
}
```

### For Agent MCP Calls:
```rust
// In agent/src/mcp/tools.rs (or equivalent)
use mrapids::security::{UrlValidator, SecurityConfig};

async fn handle_make_api_call(params: ApiCallParams) -> Result<ToolResult> {
    // Validate URL before making request
    let validator = UrlValidator::default();
    let validated_url = validator.validate_with_dns(&params.url).await?;
    
    // Make request with SecureHttpClient
    let client = SecureHttpClient::from_defaults()?;
    let response = client.get(&validated_url.url.to_string()).await?;
}
```

## Summary

**Highest Risk Commands** (need immediate protection):
1. `mrapids run` - Makes arbitrary HTTP requests
2. `mrapids test` - Makes arbitrary HTTP requests
3. `mrapids-agent start` - Downloads specs, processes requests
4. MCP `make_api_call` - Makes arbitrary HTTP requests from agent

**File Access Commands** (need sandboxing):
1. `mrapids generate` - Writes to arbitrary paths
2. `mrapids flatten` - Reads/writes files, fetches external refs
3. All commands reading spec files

The security implementation is ready but needs to be integrated into these specific command handlers.