use super::errors::CoreError;
use openapiv3::{OpenAPI, Operation};
use std::fs;
use std::path::Path;

pub fn load_openapi_spec(path: &Path) -> Result<OpenAPI, CoreError> {
    // Check if file exists
    if !path.exists() {
        let parent = path.parent().unwrap_or(Path::new("."));
        let available = fs::read_dir(parent)
            .map(|entries| {
                entries
                    .filter_map(|e| e.ok())
                    .filter_map(|e| e.file_name().to_str().map(String::from))
                    .filter(|name| {
                        name.ends_with(".yaml") || name.ends_with(".yml") || name.ends_with(".json")
                    })
                    .collect()
            })
            .unwrap_or_default();

        return Err(CoreError::SpecNotFound {
            path: path.to_path_buf(),
            available,
        });
    }

    // Read file content
    let content = fs::read_to_string(path).map_err(|e| CoreError::SpecParseFailed {
        reason: format!("Cannot read file: {}", e),
    })?;

    // Parse based on extension
    let spec = if path.extension().and_then(|s| s.to_str()) == Some("json") {
        serde_json::from_str(&content).map_err(|e| CoreError::SpecParseFailed {
            reason: format!("Invalid JSON: {}", e),
        })?
    } else {
        serde_yaml::from_str(&content).map_err(|e| CoreError::SpecParseFailed {
            reason: format!("Invalid YAML: {}", e),
        })?
    };

    Ok(spec)
}

pub fn find_operation<'a>(
    spec: &'a OpenAPI,
    operation_id: &str,
) -> Result<&'a Operation, CoreError> {
    // Search through all paths for the operation
    for (_path, path_item) in &spec.paths.paths {
        let path_item = match path_item {
            openapiv3::ReferenceOr::Item(item) => item,
            _ => continue,
        };

        // Check each HTTP method
        let operations = [
            (&path_item.get, "GET"),
            (&path_item.post, "POST"),
            (&path_item.put, "PUT"),
            (&path_item.delete, "DELETE"),
            (&path_item.patch, "PATCH"),
        ];

        for (op, _method) in operations {
            let Some(operation) = op else { continue };
            if operation.operation_id.as_deref() == Some(operation_id) {
                return Ok(operation);
            }
        }
    }

    // Operation not found - list available ones
    let available = list_operations(spec);
    Err(CoreError::OperationNotFound {
        operation: operation_id.to_string(),
        available,
    })
}

pub fn list_operations(spec: &OpenAPI) -> Vec<String> {
    let mut operations = Vec::new();

    for (_path, path_item) in &spec.paths.paths {
        let path_item = match path_item {
            openapiv3::ReferenceOr::Item(item) => item,
            _ => continue,
        };

        let ops = [
            &path_item.get,
            &path_item.post,
            &path_item.put,
            &path_item.delete,
            &path_item.patch,
        ];

        for op in ops.into_iter().flatten() {
            if let Some(id) = &op.operation_id {
                operations.push(id.clone());
            }
        }
    }

    operations
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_load_valid_openapi_spec() {
        let path = PathBuf::from("examples/petstore.yaml");
        let result = load_openapi_spec(&path);
        assert!(result.is_ok());

        let spec = result.unwrap();
        assert_eq!(spec.info.title, "Pet Store API");
        assert_eq!(spec.info.version, "1.0.0");
    }

    #[test]
    fn test_load_nonexistent_file() {
        let path = PathBuf::from("nonexistent.yaml");
        let result = load_openapi_spec(&path);
        assert!(result.is_err());

        match result.unwrap_err() {
            CoreError::SpecNotFound { .. } => (),
            _ => panic!("Expected SpecNotFound error"),
        }
    }

    #[test]
    fn test_find_operation_exists() {
        let path = PathBuf::from("examples/petstore.yaml");
        let spec = load_openapi_spec(&path).unwrap();

        let result = find_operation(&spec, "getPetById");
        assert!(result.is_ok());

        let operation = result.unwrap();
        assert_eq!(operation.operation_id.as_deref(), Some("getPetById"));
    }

    #[test]
    fn test_find_operation_not_exists() {
        let path = PathBuf::from("examples/petstore.yaml");
        let spec = load_openapi_spec(&path).unwrap();

        let result = find_operation(&spec, "nonexistentOperation");
        assert!(result.is_err());

        match result.unwrap_err() {
            CoreError::OperationNotFound { available, .. } => {
                assert!(available.contains(&"getPetById".to_string()));
            }
            _ => panic!("Expected OperationNotFound error"),
        }
    }

    #[test]
    fn test_list_operations() {
        let path = PathBuf::from("examples/petstore.yaml");
        let spec = load_openapi_spec(&path).unwrap();

        let operations = list_operations(&spec);
        assert!(operations.contains(&"getPetById".to_string()));
        assert!(operations.contains(&"addPet".to_string()));
        assert!(operations.contains(&"findPetsByStatus".to_string()));
    }
}
