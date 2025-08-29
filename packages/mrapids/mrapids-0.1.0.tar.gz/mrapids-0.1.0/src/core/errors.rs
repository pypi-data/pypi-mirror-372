use std::path::PathBuf;
use thiserror::Error;

#[derive(Error, Debug)]
#[allow(dead_code)]
pub enum CoreError {
    #[error("Cannot find spec file '{path}'. Files in directory: {available:?}")]
    SpecNotFound {
        path: PathBuf,
        available: Vec<String>,
    },

    #[error("Failed to parse spec: {reason}")]
    SpecParseFailed { reason: String },

    #[error("Operation '{operation}' not found. Available operations: {available:?}")]
    OperationNotFound {
        operation: String,
        available: Vec<String>,
    },

    #[error("HTTP request failed: {reason}")]
    RequestFailed { reason: String },

    #[error("Invalid input data: {reason}")]
    InvalidInput { reason: String },

    #[error("Response validation failed: {reason}")]
    ValidationFailed { reason: String },
}
