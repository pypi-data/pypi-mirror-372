//! Core types for the API module

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::path::PathBuf;

/// Request to execute an API operation
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema, Default)]
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
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize, JsonSchema)]
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

    /// Timestamp of the request
    pub timestamp: chrono::DateTime<chrono::Utc>,

    /// Response headers
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub headers: Option<HashMap<String, String>>,
}
