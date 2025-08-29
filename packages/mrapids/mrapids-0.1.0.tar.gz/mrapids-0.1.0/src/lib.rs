//! MicroRapid library for programmatic access

pub mod cli;
pub mod collections;
pub mod core;
pub mod utils;

// Make parser public for the agent
pub use crate::core::parser;

// Python bindings module
#[cfg(feature = "python")]
pub mod python_lib;

// WASM bindings module
#[cfg(feature = "wasm")]
pub mod wasm_lib;
