# MCP Implementation Guide

## Step-by-Step Implementation Instructions

This guide provides detailed implementation steps for adding MCP support to MicroRapid.

---

## Prerequisites

- Rust 1.75+
- Understanding of MicroRapid architecture
- Familiarity with async Rust
- Basic knowledge of MCP protocol

---

## Phase 1: Core API Layer

### Step 1.1: Create API Module Structure

```bash
# Create new directories
mkdir -p src/core/api
```

### Step 1.2: Define Core Types

Create `src/core/api/types.rs`:

```rust
use serde::{Deserialize, Serialize};
use schemars::JsonSchema;
use std::collections::HashMap;
use std::path::PathBuf;
use serde_json::Value;

/// Request to execute an API operation
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct RunRequest {
    /// Operation ID from OpenAPI spec (e.g., "getUser", "createOrder")
    pub operation_id: String,
    
    /// Parameters for path, query, and header values
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parameters: Option<HashMap<String, Value>>,
    
    /// Request body (for POST, PUT, PATCH)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub body: Option<Value>,
    
    /// Path to OpenAPI spec file (uses default if not specified)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub spec_path: Option<PathBuf>,
    
    /// Environment name (dev, staging, prod)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub env: Option<String>,
    
    /// Auth profile name (not the actual credentials)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub auth_profile: Option<String>,
}

/// Response from API operation execution
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct RunResponse {
    /// Overall status of the operation
    pub status: ResponseStatus,
    
    /// Response data (on success)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub data: Option<Value>,
    
    /// Error details (on failure)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub error: Option<ErrorDetail>,
    
    /// Metadata about the operation
    pub meta: ResponseMeta,
}

/// Operation status
#[derive(Debug, Clone, Copy, Serialize, Deserialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum ResponseStatus {
    Success,
    Error,
    PartialSuccess,
}

/// Detailed error information
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ErrorDetail {
    /// Machine-readable error code
    pub code: u16,
    
    /// Human-readable error message
    pub message: String,
    
    /// Additional error context
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub details: Option<HashMap<String, Value>>,
}

/// Metadata about the operation execution
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ResponseMeta {
    /// Operation ID that was executed
    pub operation_id: String,
    
    /// HTTP method used
    pub method: String,
    
    /// URL that was called
    pub url: String,
    
    /// HTTP status code
    pub status_code: u16,
    
    /// Execution duration in milliseconds
    pub duration_ms: u64,
    
    /// Request ID for tracing
    pub request_id: String,
}
```

### Step 1.3: Implement Error Types

Create `src/core/api/errors.rs`:

```rust
use thiserror::Error;
use serde_repr::{Serialize_repr, Deserialize_repr};
use schemars::JsonSchema;

/// API error type
#[derive(Error, Debug)]
pub enum ApiError {
    #[error("Policy denied operation: {0}")]
    PolicyDeny(String),
    
    #[error("Authentication failed: {0}")]
    AuthError(String),
    
    #[error("Input validation failed: {0}")]
    ValidationError(String),
    
    #[error("Operation not found: {0}")]
    OperationNotFound(String),
    
    #[error("Network error: {0}")]
    NetworkError(String),
    
    #[error("Internal error: {0}")]
    InternalError(String),
}

/// Machine-readable error codes
#[derive(Debug, Clone, Copy, Serialize_repr, Deserialize_repr, JsonSchema)]
#[repr(u16)]
pub enum ErrorCode {
    // Policy errors (1xxx)
    PolicyDeny = 1001,
    PolicyMisconfigured = 1002,
    PolicyNotFound = 1003,
    
    // Auth errors (2xxx)
    AuthMissing = 2001,
    AuthExpired = 2002,
    AuthInvalid = 2003,
    AuthProfileNotFound = 2004,
    
    // Validation errors (3xxx)
    InputValidation = 3001,
    SchemaValidation = 3002,
    SpecNotFound = 3003,
    OperationNotFound = 3004,
    
    // Runtime errors (4xxx)
    NetworkError = 4001,
    Timeout = 4002,
    HttpError = 4100,
    
    // Internal errors (5xxx)
    InternalError = 5001,
    ConfigError = 5002,
}

impl From<ApiError> for ErrorCode {
    fn from(err: ApiError) -> Self {
        match err {
            ApiError::PolicyDeny(_) => ErrorCode::PolicyDeny,
            ApiError::AuthError(_) => ErrorCode::AuthInvalid,
            ApiError::ValidationError(_) => ErrorCode::InputValidation,
            ApiError::OperationNotFound(_) => ErrorCode::OperationNotFound,
            ApiError::NetworkError(_) => ErrorCode::NetworkError,
            ApiError::InternalError(_) => ErrorCode::InternalError,
        }
    }
}
```

### Step 1.4: Create API Implementation

Create `src/core/api/run.rs`:

```rust
use super::types::*;
use super::errors::*;
use crate::core::parser::UnifiedSpec;
use crate::core::request_runner::execute_operation;
use std::time::Instant;
use uuid::Uuid;

/// Execute an API operation
pub async fn run_operation(
    request: RunRequest,
    spec: &UnifiedSpec,
    auth: Option<crate::core::auth::AuthProfile>,
) -> Result<RunResponse, ApiError> {
    let start = Instant::now();
    let request_id = Uuid::new_v4().to_string();
    
    // Find the operation
    let operation = spec.operations
        .iter()
        .find(|op| op.operation_id == request.operation_id)
        .ok_or_else(|| ApiError::OperationNotFound(request.operation_id.clone()))?;
    
    // Build the full URL
    let base_url = if let Some(env) = &request.env {
        // Load environment-specific base URL
        load_base_url_for_env(env, &spec.base_url)?
    } else {
        spec.base_url.clone()
    };
    
    let url = format!("{}{}", base_url, operation.path);
    
    // Execute the operation
    match execute_operation(
        operation,
        request.parameters,
        request.body,
        auth,
    ).await {
        Ok(response_data) => {
            Ok(RunResponse {
                status: ResponseStatus::Success,
                data: Some(response_data),
                error: None,
                meta: ResponseMeta {
                    operation_id: request.operation_id,
                    method: operation.method.clone(),
                    url,
                    status_code: 200, // TODO: Get from actual response
                    duration_ms: start.elapsed().as_millis() as u64,
                    request_id,
                },
            })
        }
        Err(e) => {
            let error_code = ErrorCode::from(&e);
            Ok(RunResponse {
                status: ResponseStatus::Error,
                data: None,
                error: Some(ErrorDetail {
                    code: error_code as u16,
                    message: e.to_string(),
                    details: None,
                }),
                meta: ResponseMeta {
                    operation_id: request.operation_id,
                    method: operation.method.clone(),
                    url,
                    status_code: 0,
                    duration_ms: start.elapsed().as_millis() as u64,
                    request_id,
                },
            })
        }
    }
}

fn load_base_url_for_env(env: &str, default: &str) -> Result<String, ApiError> {
    // TODO: Load from config
    Ok(default.to_string())
}
```

### Step 1.5: Add List and Show Operations

Create `src/core/api/list.rs`:

```rust
use super::types::*;
use super::errors::*;
use crate::core::parser::UnifiedSpec;
use serde::{Serialize, Deserialize};
use schemars::JsonSchema;

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListRequest {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub filter: Option<ListFilter>,
    
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub spec_path: Option<PathBuf>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListFilter {
    pub method: Option<String>,
    pub tag: Option<String>,
    pub pattern: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListResponse {
    pub operations: Vec<OperationSummary>,
    pub total: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct OperationSummary {
    pub operation_id: String,
    pub method: String,
    pub path: String,
    pub summary: Option<String>,
    pub tags: Vec<String>,
}

pub async fn list_operations(
    request: ListRequest,
    spec: &UnifiedSpec,
) -> Result<ListResponse, ApiError> {
    let mut operations: Vec<OperationSummary> = spec.operations
        .iter()
        .filter(|op| {
            // Apply filters
            if let Some(filter) = &request.filter {
                if let Some(method) = &filter.method {
                    if op.method.to_lowercase() != method.to_lowercase() {
                        return false;
                    }
                }
                // Add more filter logic
            }
            true
        })
        .map(|op| OperationSummary {
            operation_id: op.operation_id.clone(),
            method: op.method.clone(),
            path: op.path.clone(),
            summary: op.summary.clone(),
            tags: vec![], // TODO: Extract from operation
        })
        .collect();
    
    let total = operations.len();
    
    Ok(ListResponse {
        operations,
        total,
    })
}
```

---

## Phase 2: Policy Engine

### Step 2.1: Define Policy Model

Create `src/core/policy/model.rs`:

```rust
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Policy configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicySet {
    pub version: String,
    pub defaults: PolicyDefaults,
    pub rules: Vec<PolicyRule>,
}

/// Default policy settings
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyDefaults {
    pub allow_methods: Vec<String>,
    pub deny_external_refs: bool,
    pub require_auth: bool,
}

/// Individual policy rule
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyRule {
    pub name: String,
    pub description: Option<String>,
    pub pattern: String,
    pub conditions: Option<Vec<PolicyCondition>>,
    pub allow: Option<PolicyAction>,
    pub deny: Option<PolicyAction>,
    pub audit: Option<AuditConfig>,
}

/// Policy condition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyCondition {
    pub auth_profile: Option<String>,
    pub time_window: Option<String>,
    pub source_ip: Option<String>,
}

/// Policy action
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyAction {
    pub operations: Option<Vec<String>>,
    pub methods: Option<Vec<String>>,
    pub all: Option<bool>,
}

/// Audit configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuditConfig {
    pub level: String,
}
```

### Step 2.2: Implement Policy Engine

Create `src/core/policy/engine.rs`:

```rust
use super::model::*;
use crate::core::api::types::RunRequest;
use glob::Pattern;

pub struct PolicyEngine {
    policy: PolicySet,
}

impl PolicyEngine {
    pub fn new(policy: PolicySet) -> Self {
        Self { policy }
    }
    
    pub fn evaluate(&self, request: &RunRequest, url: &str) -> PolicyDecision {
        // Check each rule
        for rule in &self.policy.rules {
            if self.matches_pattern(&rule.pattern, url) {
                // Check conditions
                if let Some(conditions) = &rule.conditions {
                    if !self.check_conditions(conditions, request) {
                        continue;
                    }
                }
                
                // Check deny first
                if let Some(deny) = &rule.deny {
                    if self.matches_action(deny, request) {
                        return PolicyDecision::Deny {
                            rule: rule.name.clone(),
                            reason: format!("Denied by rule: {}", rule.name),
                        };
                    }
                }
                
                // Check allow
                if let Some(allow) = &rule.allow {
                    if self.matches_action(allow, request) {
                        return PolicyDecision::Allow {
                            rule: rule.name.clone(),
                        };
                    }
                }
            }
        }
        
        // Default decision based on defaults
        PolicyDecision::Deny {
            rule: "default".to_string(),
            reason: "No matching allow rule".to_string(),
        }
    }
    
    fn matches_pattern(&self, pattern: &str, url: &str) -> bool {
        Pattern::new(pattern)
            .map(|p| p.matches(url))
            .unwrap_or(false)
    }
    
    fn check_conditions(&self, conditions: &[PolicyCondition], request: &RunRequest) -> bool {
        // TODO: Implement condition checking
        true
    }
    
    fn matches_action(&self, action: &PolicyAction, request: &RunRequest) -> bool {
        if let Some(true) = action.all {
            return true;
        }
        
        // TODO: Check specific operations and methods
        true
    }
}

#[derive(Debug, Clone)]
pub enum PolicyDecision {
    Allow { rule: String },
    Deny { rule: String, reason: String },
}
```

---

## Phase 3: MCP Server

### Step 3.1: Create MCP Server Crate

```bash
# Create agent directory
mkdir -p agent/src/tools
cd agent

# Create Cargo.toml
cat > Cargo.toml << 'EOF'
[package]
name = "mrapids-agent"
version = "0.1.0"
edition = "2021"

[dependencies]
mrapids = { path = ".." }
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }
serde_json = "1"
mcp-server = "0.1"  # MCP server library
toml = "0.8"
tracing = "0.1"
tracing-subscriber = "0.3"

[[bin]]
name = "mrapids-agent"
path = "src/main.rs"
EOF
```

### Step 3.2: Implement MCP Server

Create `agent/src/main.rs`:

```rust
use mcp_server::{Server, Tool};
use std::sync::Arc;
use tokio::sync::RwLock;

mod config;
mod tools;
mod auth;
mod audit;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt::init();
    
    // Load configuration
    let config = config::load_config("mcp-server.toml")?;
    
    // Create shared state
    let state = Arc::new(RwLock::new(ServerState {
        config,
        policy_engine: create_policy_engine()?,
    }));
    
    // Create MCP server
    let mut server = Server::new();
    
    // Register tools
    server.register_tool(tools::list::create_tool(state.clone()));
    server.register_tool(tools::show::create_tool(state.clone()));
    server.register_tool(tools::run::create_tool(state.clone()));
    
    // Start server
    let addr = "127.0.0.1:3333";
    tracing::info!("Starting MCP server on {}", addr);
    server.listen(addr).await?;
    
    Ok(())
}

struct ServerState {
    config: config::Config,
    policy_engine: mrapids::core::policy::PolicyEngine,
}

fn create_policy_engine() -> Result<PolicyEngine, Box<dyn std::error::Error>> {
    // Load policy from file
    let policy_content = std::fs::read_to_string("policy.yaml")?;
    let policy: PolicySet = serde_yaml::from_str(&policy_content)?;
    Ok(PolicyEngine::new(policy))
}
```

### Step 3.3: Implement Run Tool

Create `agent/src/tools/run.rs`:

```rust
use mcp_server::{Tool, ToolInput, ToolOutput};
use mrapids::core::api::{run_operation, RunRequest, RunResponse};
use std::sync::Arc;
use tokio::sync::RwLock;

pub fn create_tool(state: Arc<RwLock<ServerState>>) -> Tool {
    Tool::new("run")
        .description("Execute an API operation")
        .input_schema(serde_json::from_str(include_str!("../../../schemas/tools/run-tool.json")).unwrap())
        .handler(move |input: ToolInput| {
            let state = state.clone();
            async move {
                // Parse input
                let request: RunRequest = serde_json::from_value(input.parameters)?;
                
                // Get state
                let state = state.read().await;
                
                // Check policy
                let decision = state.policy_engine.evaluate(&request, ""); // TODO: Get URL
                match decision {
                    PolicyDecision::Deny { reason, .. } => {
                        return Ok(ToolOutput::error(1001, &reason));
                    }
                    PolicyDecision::Allow { .. } => {}
                }
                
                // Load auth profile
                let auth = if let Some(profile_name) = &request.auth_profile {
                    Some(auth::load_profile(profile_name).await?)
                } else {
                    None
                };
                
                // Execute operation
                let response = run_operation(request, spec, auth).await?;
                
                // Redact sensitive data
                let response = redact::redact_response(response);
                
                // Audit
                audit::log_operation(&request, &response).await?;
                
                // Return response
                Ok(ToolOutput::success(serde_json::to_value(response)?))
            }
        })
}
```

---

## Phase 4: Testing

### Step 4.1: Unit Tests

Create `src/core/api/tests.rs`:

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_run_operation_success() {
        let request = RunRequest {
            operation_id: "getUser".to_string(),
            parameters: Some(HashMap::from([
                ("userId".to_string(), json!("123"))
            ])),
            body: None,
            spec_path: None,
            env: None,
            auth_profile: None,
        };
        
        let spec = create_test_spec();
        let response = run_operation(request, &spec, None).await.unwrap();
        
        assert_eq!(response.status, ResponseStatus::Success);
        assert!(response.data.is_some());
    }
    
    #[test]
    fn test_policy_evaluation() {
        let policy = PolicySet {
            version: "1.0".to_string(),
            defaults: PolicyDefaults {
                allow_methods: vec!["GET".to_string()],
                deny_external_refs: true,
                require_auth: true,
            },
            rules: vec![
                PolicyRule {
                    name: "readonly".to_string(),
                    pattern: "*".to_string(),
                    allow: Some(PolicyAction {
                        methods: Some(vec!["GET".to_string()]),
                        ..Default::default()
                    }),
                    ..Default::default()
                }
            ],
        };
        
        let engine = PolicyEngine::new(policy);
        let request = RunRequest {
            operation_id: "getUser".to_string(),
            ..Default::default()
        };
        
        match engine.evaluate(&request, "https://api.example.com/users/123") {
            PolicyDecision::Allow { .. } => {}
            _ => panic!("Expected allow decision"),
        }
    }
}
```

### Step 4.2: Integration Tests

Create `tests/mcp_integration.rs`:

```rust
use mcp_client::Client;

#[tokio::test]
async fn test_mcp_workflow() {
    // Start test server
    let server = start_test_server().await;
    
    // Create MCP client
    let client = Client::connect("http://localhost:3333").await.unwrap();
    
    // List operations
    let list_result = client.call("list", json!({})).await.unwrap();
    assert!(list_result["operations"].is_array());
    
    // Show operation
    let show_result = client.call("show", json!({
        "operation_id": "getUser"
    })).await.unwrap();
    assert!(show_result["parameters"].is_object());
    
    // Run operation
    let run_result = client.call("run", json!({
        "operation_id": "getUser",
        "parameters": {
            "userId": "123"
        }
    })).await.unwrap();
    assert_eq!(run_result["status"], "success");
}
```

---

## Phase 5: Documentation

### Step 5.1: Generate JSON Schemas

```bash
# Add build script to generate schemas
cat > build.rs << 'EOF'
use schemars::schema_for;
use std::fs;

fn main() {
    // Generate schemas for types
    let schemas = vec![
        ("RunRequest", schema_for!(mrapids::core::api::RunRequest)),
        ("RunResponse", schema_for!(mrapids::core::api::RunResponse)),
        // Add more types
    ];
    
    for (name, schema) in schemas {
        let json = serde_json::to_string_pretty(&schema).unwrap();
        fs::write(format!("schemas/types/{}.json", name), json).unwrap();
    }
}
EOF
```

### Step 5.2: Create Examples

Create `examples/.mrapids/policy.yaml`:

```yaml
version: "1.0"
metadata:
  name: "example-policy"
  description: "Example policy for agent access"

defaults:
  allow_methods: ["GET", "HEAD"]
  deny_external_refs: true
  require_auth: true

rules:
  - name: "public-readonly"
    pattern: "api.public.com/*"
    allow:
      methods: ["GET"]
      operations: ["list*", "get*", "search*"]
      
  - name: "internal-full"
    pattern: "*.internal.com/*"
    conditions:
      - auth_profile: "internal-agent"
    allow:
      methods: ["GET", "POST", "PUT", "DELETE"]
```

---

## Deployment

### Docker Setup

Create `agent/Dockerfile`:

```dockerfile
FROM rust:1.75 as builder
WORKDIR /app
COPY . .
RUN cargo build --release --bin mrapids-agent

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates
COPY --from=builder /app/target/release/mrapids-agent /usr/local/bin/
COPY examples/.mrapids /etc/mrapids
CMD ["mrapids-agent", "--config", "/etc/mrapids/mcp-server.toml"]
```

### Systemd Service

Create `/etc/systemd/system/mrapids-agent.service`:

```ini
[Unit]
Description=MicroRapid MCP Agent Server
After=network.target

[Service]
Type=simple
User=mrapids
ExecStart=/usr/local/bin/mrapids-agent --config /etc/mrapids/mcp-server.toml
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

---

## Monitoring

### Prometheus Metrics

Add to `agent/src/metrics.rs`:

```rust
use prometheus::{Counter, Histogram, Registry};

lazy_static! {
    static ref REQUEST_COUNTER: Counter = Counter::new(
        "mrapids_agent_requests_total",
        "Total number of MCP requests"
    ).unwrap();
    
    static ref REQUEST_DURATION: Histogram = Histogram::new(
        "mrapids_agent_request_duration_seconds",
        "Request duration in seconds"
    ).unwrap();
}
```

---

## Troubleshooting

### Common Issues

1. **Policy Denials**
   - Check audit logs: `tail -f logs/audit.jsonl`
   - Test policy: `mrapids-agent policy test`

2. **Auth Failures**
   - Verify profile exists: `mrapids auth list`
   - Check token expiry: `mrapids auth show <profile>`

3. **Schema Validation**
   - Validate request: `mrapids-agent validate request.json`
   - Check schema: `cat schemas/types/RunRequest.json`

---

## Next Steps

1. Complete implementation of all phases
2. Add comprehensive tests
3. Security audit
4. Performance benchmarking
5. Documentation review
6. Beta testing with partners
7. Production release

---

**Remember**: Each phase builds on the previous one. Don't skip steps!