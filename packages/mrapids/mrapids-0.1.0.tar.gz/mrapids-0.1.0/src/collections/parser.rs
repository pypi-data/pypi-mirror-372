//! Parser for collection YAML files

use super::models::Collection;
use anyhow::{Context, Result};
use std::path::Path;

/// Parse a collection from a YAML file
pub fn parse_collection(path: &Path) -> Result<Collection> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read collection file: {:?}", path))?;

    parse_collection_yaml(&content)
        .with_context(|| format!("Failed to parse collection YAML: {:?}", path))
}

/// Parse collection from YAML string
pub fn parse_collection_yaml(yaml_content: &str) -> Result<Collection> {
    let collection: Collection = serde_yaml::from_str(yaml_content)
        .map_err(|e| anyhow::anyhow!("Invalid collection YAML format: {}", e))?;

    // Basic validation
    if collection.name.is_empty() {
        anyhow::bail!("Collection name cannot be empty");
    }

    if collection.requests.is_empty() {
        anyhow::bail!("Collection must contain at least one request");
    }

    // Check for duplicate request names
    let mut seen_names = std::collections::HashSet::new();
    for request in &collection.requests {
        if !seen_names.insert(&request.name) {
            anyhow::bail!("Duplicate request name: {}", request.name);
        }
    }

    Ok(collection)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_basic_collection() {
        let yaml = r#"
name: test-collection
description: Test collection
requests:
  - name: get_user
    operation: users/get-by-username
    params:
      username: octocat
"#;

        let collection = parse_collection_yaml(yaml).unwrap();
        assert_eq!(collection.name, "test-collection");
        assert_eq!(collection.description, Some("Test collection".to_string()));
        assert_eq!(collection.requests.len(), 1);
        assert_eq!(collection.requests[0].name, "get_user");
        assert_eq!(collection.requests[0].operation, "users/get-by-username");
    }

    #[test]
    fn test_parse_collection_with_variables() {
        let yaml = r#"
name: test-collection
variables:
  username: octocat
  repo: hello-world
requests:
  - name: get_repo
    operation: repos/get
    params:
      owner: "{{username}}"
      repo: "{{repo}}"
"#;

        let collection = parse_collection_yaml(yaml).unwrap();
        assert_eq!(collection.variables.len(), 2);
        assert_eq!(collection.variables["username"], "octocat");
    }

    #[test]
    fn test_duplicate_request_names() {
        let yaml = r#"
name: test-collection
requests:
  - name: request1
    operation: users/get
  - name: request1
    operation: repos/get
"#;

        let result = parse_collection_yaml(yaml);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("Duplicate request name"));
    }

    #[test]
    fn test_empty_collection() {
        let yaml = r#"
name: test-collection
requests: []
"#;

        let result = parse_collection_yaml(yaml);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("at least one request"));
    }
}
