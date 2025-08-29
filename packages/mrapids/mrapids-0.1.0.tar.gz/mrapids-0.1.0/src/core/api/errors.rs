//! Error types for the API module

use schemars::JsonSchema;
use serde_repr::{Deserialize_repr, Serialize_repr};
use thiserror::Error;

/// API error type
#[derive(Error, Debug)]
#[allow(dead_code)]
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

    #[error("Client error: {0}")]
    ClientError(String),

    #[error("Server error: {0}")]
    ServerError(String),

    #[error("Timeout error: {0}")]
    TimeoutError(String),

    #[error("Payload too large: {0}")]
    PayloadTooLarge(String),
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
    ClientError = 4400,
    ServerError = 4500,
    PayloadTooLarge = 4413,

    // Internal errors (5xxx)
    InternalError = 5001,
    ConfigError = 5002,
}

impl From<&ApiError> for ErrorCode {
    fn from(err: &ApiError) -> Self {
        match err {
            ApiError::PolicyDeny(_) => ErrorCode::PolicyDeny,
            ApiError::AuthError(_) => ErrorCode::AuthInvalid,
            ApiError::ValidationError(_) => ErrorCode::InputValidation,
            ApiError::OperationNotFound(_) => ErrorCode::OperationNotFound,
            ApiError::NetworkError(_) => ErrorCode::NetworkError,
            ApiError::InternalError(_) => ErrorCode::InternalError,
            ApiError::ClientError(_) => ErrorCode::ClientError,
            ApiError::ServerError(_) => ErrorCode::ServerError,
            ApiError::TimeoutError(_) => ErrorCode::Timeout,
            ApiError::PayloadTooLarge(_) => ErrorCode::PayloadTooLarge,
        }
    }
}

impl ErrorCode {
    /// Get a human-readable description of the error code
    #[allow(dead_code)]
    pub fn description(&self) -> &'static str {
        match self {
            // Policy errors
            ErrorCode::PolicyDeny => "Operation denied by security policy",
            ErrorCode::PolicyMisconfigured => "Security policy is misconfigured",
            ErrorCode::PolicyNotFound => "Security policy not found",

            // Auth errors
            ErrorCode::AuthMissing => "Authentication credentials missing",
            ErrorCode::AuthExpired => "Authentication credentials expired",
            ErrorCode::AuthInvalid => "Authentication credentials invalid",
            ErrorCode::AuthProfileNotFound => "Authentication profile not found",

            // Validation errors
            ErrorCode::InputValidation => "Input validation failed",
            ErrorCode::SchemaValidation => "Schema validation failed",
            ErrorCode::SpecNotFound => "OpenAPI specification not found",
            ErrorCode::OperationNotFound => "Operation not found in specification",

            // Runtime errors
            ErrorCode::NetworkError => "Network error occurred",
            ErrorCode::Timeout => "Operation timed out",
            ErrorCode::HttpError => "HTTP error occurred",

            // Internal errors
            ErrorCode::InternalError => "Internal error occurred",
            ErrorCode::ConfigError => "Configuration error",

            // Additional HTTP errors
            ErrorCode::ClientError => "Client error occurred",
            ErrorCode::ServerError => "Server error occurred",
            ErrorCode::PayloadTooLarge => "Payload too large",
        }
    }
}
