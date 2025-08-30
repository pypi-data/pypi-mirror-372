//! Validator for collections

use super::models::Collection;
use crate::core::parser::UnifiedSpec;
use std::collections::HashSet;

/// Validation result with warnings and errors
#[derive(Debug, Default)]
pub struct ValidationResult {
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
}

impl ValidationResult {
    pub fn is_valid(&self) -> bool {
        self.errors.is_empty()
    }

    pub fn add_error(&mut self, error: String) {
        self.errors.push(error);
    }

    pub fn add_warning(&mut self, warning: String) {
        self.warnings.push(warning);
    }
}

/// Validate a collection against an API spec
pub fn validate_collection(
    collection: &Collection,
    spec: Option<&UnifiedSpec>,
) -> ValidationResult {
    let mut result = ValidationResult::default();

    // Validate collection structure
    validate_structure(collection, &mut result);

    // Validate against API spec if provided
    if let Some(spec) = spec {
        validate_against_spec(collection, spec, &mut result);
    }

    // Validate variable usage
    validate_variables(collection, &mut result);

    result
}

fn validate_structure(collection: &Collection, result: &mut ValidationResult) {
    // Check collection name
    if collection.name.is_empty() {
        result.add_error("Collection name cannot be empty".to_string());
    }

    // Check for empty requests
    if collection.requests.is_empty() {
        result.add_error("Collection must contain at least one request".to_string());
    }

    // Check for duplicate request names
    let mut seen_names = HashSet::new();
    for request in &collection.requests {
        if !seen_names.insert(&request.name) {
            result.add_error(format!("Duplicate request name: {}", request.name));
        }

        // Validate request
        if request.name.is_empty() {
            result.add_error("Request name cannot be empty".to_string());
        }

        if request.operation.is_empty() {
            result.add_error(format!(
                "Operation cannot be empty for request '{}'",
                request.name
            ));
        }
    }
}

fn validate_against_spec(
    collection: &Collection,
    spec: &UnifiedSpec,
    result: &mut ValidationResult,
) {
    // Get all available operations
    let available_ops: HashSet<&str> = spec
        .operations
        .iter()
        .map(|op| op.operation_id.as_str())
        .collect();

    // Check each request
    for request in &collection.requests {
        if !available_ops.contains(request.operation.as_str()) {
            result.add_error(format!(
                "Unknown operation '{}' in request '{}'",
                request.operation, request.name
            ));

            // Suggest similar operations
            let similar = find_similar_operations(&request.operation, &available_ops);
            if !similar.is_empty() {
                result.add_warning(format!("Did you mean one of: {}?", similar.join(", ")));
            }
        }
    }
}

fn validate_variables(collection: &Collection, result: &mut ValidationResult) {
    // Collect all variables used in templates
    let mut used_vars = HashSet::new();
    let mut saved_vars = HashSet::new();

    for request in &collection.requests {
        // Check save_as
        if let Some(save_as) = &request.save_as {
            if saved_vars.contains(save_as) {
                result.add_warning(format!("Variable '{}' is saved multiple times", save_as));
            }
            saved_vars.insert(save_as.clone());
        }

        // Extract variables from params
        if let Some(params) = &request.params {
            for value in params.values() {
                extract_template_vars(value, &mut used_vars);
            }
        }

        // Extract variables from body
        if let Some(body) = &request.body {
            extract_template_vars(body, &mut used_vars);
        }
    }

    // Check if all used variables are defined
    for var in &used_vars {
        // Skip saved response variables
        if var.contains('.') {
            let prefix = var.split('.').next().unwrap();
            if saved_vars.contains(prefix) {
                continue;
            }
        }

        // Check if variable is defined in collection
        if !collection.variables.contains_key(var) && !saved_vars.contains(var) {
            result.add_warning(format!(
                "Variable '{}' is used but not defined in collection",
                var
            ));
        }
    }
}

fn extract_template_vars(value: &serde_json::Value, vars: &mut HashSet<String>) {
    match value {
        serde_json::Value::String(s) => {
            // Simple regex to find {{variable}} patterns
            let re = regex::Regex::new(r"\{\{([^}]+)\}\}").unwrap();
            for cap in re.captures_iter(s) {
                if let Some(var) = cap.get(1) {
                    vars.insert(var.as_str().trim().to_string());
                }
            }
        }
        serde_json::Value::Object(map) => {
            for v in map.values() {
                extract_template_vars(v, vars);
            }
        }
        serde_json::Value::Array(arr) => {
            for v in arr {
                extract_template_vars(v, vars);
            }
        }
        _ => {}
    }
}

fn find_similar_operations(target: &str, available: &HashSet<&str>) -> Vec<String> {
    let mut similar = Vec::new();

    for op in available {
        // Simple similarity check - could be improved
        if op.contains(&target) || target.contains(op) {
            similar.push(op.to_string());
        }
    }

    similar.sort();
    similar.truncate(3);
    similar
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::collections::models::CollectionRequest;

    #[test]
    fn test_validate_empty_collection() {
        let collection = Collection {
            name: "test".to_string(),
            description: None,
            requests: vec![],
            variables: Default::default(),
            auth_profile: None,
        };

        let result = validate_collection(&collection, None);
        assert!(!result.is_valid());
        assert!(result
            .errors
            .iter()
            .any(|e| e.contains("at least one request")));
    }

    #[test]
    fn test_validate_duplicate_names() {
        let collection = Collection {
            name: "test".to_string(),
            description: None,
            requests: vec![
                CollectionRequest {
                    name: "req1".to_string(),
                    operation: "op1".to_string(),
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
                },
                CollectionRequest {
                    name: "req1".to_string(),
                    operation: "op2".to_string(),
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
                },
            ],
            variables: Default::default(),
            auth_profile: None,
        };

        let result = validate_collection(&collection, None);
        assert!(!result.is_valid());
        assert!(result
            .errors
            .iter()
            .any(|e| e.contains("Duplicate request name")));
    }
}
