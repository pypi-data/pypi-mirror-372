use crate::core::validation::types::{Severity, ValidationError, ValidationResult};
/// Validation rules for operations
use serde_json::Value;
use std::collections::{HashMap, HashSet};

/// Validate operations for duplicates and path parameters
pub fn validate_operations(spec: &Value) -> ValidationResult {
    let mut result = ValidationResult::new();
    let mut operation_ids = HashMap::new();

    if let Some(paths) = spec.get("paths").and_then(|p| p.as_object()) {
        for (path, path_item) in paths {
            if let Some(path_obj) = path_item.as_object() {
                // Extract path parameters
                let path_params = extract_path_parameters(path);

                for (method, operation) in path_obj {
                    // Skip non-operation fields
                    if ["parameters", "servers", "$ref", "summary", "description"]
                        .contains(&method.as_str())
                    {
                        continue;
                    }

                    if let Some(op) = operation.as_object() {
                        let op_path = format!("$.paths.{}.{}", path, method);

                        // Check duplicate operation IDs
                        if let Some(op_id) = op.get("operationId").and_then(|id| id.as_str()) {
                            if let Some(existing_path) = operation_ids.get(op_id) {
                                result.errors.push(
                                    ValidationError::new(
                                        "duplicate-operation-id",
                                        format!(
                                            "Duplicate operationId '{}' (also defined at {})",
                                            op_id, existing_path
                                        ),
                                    )
                                    .with_path(&op_path),
                                );
                            } else {
                                operation_ids.insert(op_id.to_string(), op_path.clone());
                            }
                        }

                        // Validate path parameters
                        validate_path_parameters(op, &path_params, &op_path, &mut result);
                    }
                }
            }
        }
    }

    result
}

fn extract_path_parameters(path: &str) -> HashSet<String> {
    let mut params = HashSet::new();
    let mut chars = path.chars();
    let mut in_param = false;
    let mut current_param = String::new();

    while let Some(ch) = chars.next() {
        if ch == '{' {
            in_param = true;
            current_param.clear();
        } else if ch == '}' && in_param {
            if !current_param.is_empty() {
                params.insert(current_param.clone());
            }
            in_param = false;
        } else if in_param {
            current_param.push(ch);
        }
    }

    params
}

fn validate_path_parameters(
    operation: &serde_json::Map<String, Value>,
    path_params: &HashSet<String>,
    op_path: &str,
    result: &mut ValidationResult,
) {
    let mut defined_params = HashSet::new();

    // Collect parameters from operation
    if let Some(params) = operation.get("parameters").and_then(|p| p.as_array()) {
        for (i, param) in params.iter().enumerate() {
            if let Some(param_obj) = param.as_object() {
                if param_obj.get("in").and_then(|v| v.as_str()) == Some("path") {
                    if let Some(name) = param_obj.get("name").and_then(|n| n.as_str()) {
                        defined_params.insert(name.to_string());

                        // Check if parameter is required
                        let required = param_obj
                            .get("required")
                            .and_then(|r| r.as_bool())
                            .unwrap_or(false);

                        if !required {
                            result.errors.push(
                                ValidationError::new(
                                    "path-param-not-required",
                                    format!("Path parameter '{}' must be required", name),
                                )
                                .with_path(&format!("{}.parameters[{}]", op_path, i)),
                            );
                        }
                    }
                }
            }
        }
    }

    // Check for missing path parameters
    for path_param in path_params {
        if !defined_params.contains(path_param) {
            result.errors.push(
                ValidationError::new(
                    "missing-path-parameter",
                    format!(
                        "Path parameter '{}' is not defined in operation parameters",
                        path_param
                    ),
                )
                .with_path(op_path),
            );
        }
    }

    // Check for extra path parameters
    for defined_param in &defined_params {
        if !path_params.contains(defined_param) {
            result.warnings.push(
                ValidationError::new(
                    "unused-path-parameter",
                    format!(
                        "Path parameter '{}' is defined but not used in path",
                        defined_param
                    ),
                )
                .with_path(op_path)
                .with_severity(Severity::Warning),
            );
        }
    }
}
