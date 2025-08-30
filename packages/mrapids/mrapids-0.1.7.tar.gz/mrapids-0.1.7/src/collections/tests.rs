//! Tests for collections module

#[cfg(test)]
mod tests {
    use super::super::*;
    use tempfile::TempDir;

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

        let collection = parser::parse_collection_yaml(yaml).unwrap();
        assert_eq!(collection.name, "test-collection");
        assert_eq!(collection.description, Some("Test collection".to_string()));
        assert_eq!(collection.requests.len(), 1);
        assert_eq!(collection.requests[0].name, "get_user");
    }

    #[test]
    fn test_list_collections() {
        let temp_dir = TempDir::new().unwrap();
        let collections_dir = temp_dir.path();

        // Create test collection files
        std::fs::write(
            collections_dir.join("test1.yaml"),
            "name: test1\nrequests: []",
        )
        .unwrap();
        std::fs::write(
            collections_dir.join("test2.yml"),
            "name: test2\nrequests: []",
        )
        .unwrap();
        std::fs::write(collections_dir.join("not-yaml.txt"), "not a yaml file").unwrap();

        let collections = list_collections(collections_dir).unwrap();
        assert_eq!(collections.len(), 2);

        // Should only include .yaml and .yml files
        let names: Vec<String> = collections
            .iter()
            .filter_map(|p| p.file_stem())
            .map(|s| s.to_string_lossy().to_string())
            .collect();

        assert!(names.contains(&"test1".to_string()));
        assert!(names.contains(&"test2".to_string()));
    }

    #[test]
    fn test_find_collection() {
        let temp_dir = TempDir::new().unwrap();
        let collections_dir = temp_dir.path();

        // Create test collection
        std::fs::write(
            collections_dir.join("test-collection.yaml"),
            "name: test\nrequests: []",
        )
        .unwrap();

        // Test finding with and without extension
        let found = find_collection(collections_dir, "test-collection").unwrap();
        assert_eq!(found.file_name().unwrap(), "test-collection.yaml");

        let found2 = find_collection(collections_dir, "test-collection.yaml").unwrap();
        assert_eq!(found2.file_name().unwrap(), "test-collection.yaml");

        // Test not found
        assert!(find_collection(collections_dir, "non-existent").is_err());
    }

    #[test]
    fn test_variable_resolution() {
        let mut context = context::ExecutionContext::new();
        context.set_variable("username".to_string(), serde_json::json!("octocat"));
        context.set_variable("repo".to_string(), serde_json::json!("hello-world"));

        let template = "{{username}}/{{repo}}";
        let resolved = context.resolve_string(template).unwrap();
        assert_eq!(resolved, "octocat/hello-world");
    }

    #[test]
    fn test_collection_validation() {
        let collection = models::Collection {
            name: "test".to_string(),
            description: None,
            requests: vec![models::CollectionRequest {
                name: "req1".to_string(),
                operation: "users/get".to_string(),
                params: None,
                body: None,
                save_as: None,
                expect: None,
                depends_on: None,
                if_condition: None,
                skip: None,
                run_always: false,
                critical: false,
                retry: None,
            }],
            variables: Default::default(),
            auth_profile: None,
        };

        let result = validator::validate_collection(&collection, None);
        assert!(result.is_valid());
        assert!(result.errors.is_empty());
    }
}
