//! Simple authentication types for HTTP client

use serde::{Deserialize, Serialize};

/// Authentication types
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum AuthType {
    Bearer,
    Basic,
    ApiKey,
}

/// Simple auth profile for HTTP requests
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SimpleAuthProfile {
    pub auth_type: AuthType,
    pub token: Option<String>,
    pub username: Option<String>,
    pub password: Option<String>,
    pub header: Option<String>,
}

impl SimpleAuthProfile {
    /// Create a bearer token auth
    #[allow(dead_code)]
    pub fn bearer(token: String) -> Self {
        Self {
            auth_type: AuthType::Bearer,
            token: Some(token),
            username: None,
            password: None,
            header: None,
        }
    }

    /// Create a basic auth
    #[allow(dead_code)]
    pub fn basic(username: String, password: String) -> Self {
        Self {
            auth_type: AuthType::Basic,
            token: None,
            username: Some(username),
            password: Some(password),
            header: None,
        }
    }

    /// Create an API key auth
    #[allow(dead_code)]
    pub fn api_key(header: String, token: String) -> Self {
        Self {
            auth_type: AuthType::ApiKey,
            token: Some(token),
            username: None,
            password: None,
            header: Some(header),
        }
    }
}
