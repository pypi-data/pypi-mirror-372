//! HTTP response types with full metadata

use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

/// Complete HTTP response with status, headers, and body
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HttpResponse {
    /// HTTP status code
    pub status_code: u16,

    /// Response headers
    pub headers: HashMap<String, String>,

    /// Response body as JSON (if applicable)
    pub body: Option<Value>,

    /// Raw response body (for non-JSON responses)
    pub raw_body: Option<String>,
}

impl HttpResponse {
    /// Check if the response indicates success
    #[allow(dead_code)]
    pub fn is_success(&self) -> bool {
        self.status_code >= 200 && self.status_code < 300
    }

    /// Check if the response indicates client error
    #[allow(dead_code)]
    pub fn is_client_error(&self) -> bool {
        self.status_code >= 400 && self.status_code < 500
    }

    /// Check if the response indicates server error
    #[allow(dead_code)]
    pub fn is_server_error(&self) -> bool {
        self.status_code >= 500 && self.status_code < 600
    }
}
