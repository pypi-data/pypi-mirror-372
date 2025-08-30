//! Core API module for programmatic access to MicroRapid functionality
//!
//! This module provides a clean API surface for both CLI and MCP server usage,
//! with no interactive prompts or I/O operations.

#![allow(unused_imports)]

pub mod errors;
pub mod list;
pub mod run;
pub mod show;
pub mod types;

// Re-export main types and functions
pub use errors::*;
pub use list::{list_operations, ListFilter, ListRequest, ListResponse, OperationSummary};
pub use run::run_operation;
pub use show::{show_operation, ShowRequest, ShowResponse};
pub use types::*;
