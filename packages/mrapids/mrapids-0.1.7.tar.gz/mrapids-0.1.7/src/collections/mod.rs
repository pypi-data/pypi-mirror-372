//! Collections module for grouping and executing multiple API requests
//!
//! This module provides functionality to:
//! - Define collections of API requests in YAML format
//! - Execute collections with various options
//! - Save and analyze results
//! - Use variables and dependencies between requests

pub mod condition;
pub mod context;
pub mod dependency;
pub mod executor;
pub mod models;
pub mod parser;
pub mod reporter;
pub mod testing;
pub mod validator;

#[cfg(test)]
mod tests;

pub use context::ExecutionContext;
pub use executor::{CollectionExecutor, ExecutionOptions};
pub use models::{Collection, CollectionRequest};
pub use parser::parse_collection;
pub use reporter::{ConsoleReporter, Reporter};
pub use validator::validate_collection;

use anyhow::Result;
use std::path::{Path, PathBuf};

/// List all available collections in the collections directory
pub fn list_collections(collections_dir: &Path) -> Result<Vec<PathBuf>> {
    let mut collections = Vec::new();

    if !collections_dir.exists() {
        return Ok(collections);
    }

    for entry in std::fs::read_dir(collections_dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_file() {
            if let Some(ext) = path.extension() {
                if ext == "yaml" || ext == "yml" {
                    collections.push(path);
                }
            }
        }
    }

    collections.sort();
    Ok(collections)
}

/// Find a collection by name in the collections directory
pub fn find_collection(collections_dir: &Path, name: &str) -> Result<PathBuf> {
    // Try exact match with common extensions
    for ext in &["yaml", "yml"] {
        let path = collections_dir.join(format!("{}.{}", name, ext));
        if path.exists() {
            return Ok(path);
        }
    }

    // Try without extension if already included
    let path = collections_dir.join(name);
    if path.exists() && path.is_file() {
        return Ok(path);
    }

    anyhow::bail!("Collection '{}' not found in {:?}", name, collections_dir)
}
