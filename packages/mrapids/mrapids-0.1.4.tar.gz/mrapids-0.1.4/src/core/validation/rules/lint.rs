use crate::core::validation::types::{Severity, ValidationError, ValidationResult};
/// Linting rules for best practices and style
use serde_json::Value;
use std::collections::HashSet;

/// Validate best practices and style issues
pub fn validate_best_practices(spec: &Value) -> ValidationResult {
    let mut result = ValidationResult::new();

    // Check for missing descriptions
    check_missing_descriptions(spec, &mut result);

    // Check for missing examples
    check_missing_examples(spec, &mut result);

    // Check naming conventions
    check_naming_conventions(spec, &mut result);

    // Check for unused components
    check_unused_components(spec, &mut result);

    result
}

fn check_missing_descriptions(spec: &Value, result: &mut ValidationResult) {
    // Check info description
    if let Some(info) = spec.get("info") {
        if info.get("description").is_none() {
            result.warnings.push(
                ValidationError::new(
                    "missing-info-description",
                    "Info section should have a description",
                )
                .with_path("$.info")
                .with_severity(Severity::Warning),
            );
        }
    }

    // Check operation descriptions
    if let Some(paths) = spec.get("paths").and_then(|p| p.as_object()) {
        for (path, path_item) in paths {
            if let Some(path_obj) = path_item.as_object() {
                for (method, operation) in path_obj {
                    if ["parameters", "servers", "$ref", "summary", "description"]
                        .contains(&method.as_str())
                    {
                        continue;
                    }

                    if let Some(op) = operation.as_object() {
                        let op_path = format!("$.paths.{}.{}", path, method);

                        if op.get("description").is_none() && op.get("summary").is_none() {
                            result.warnings.push(
                                ValidationError::new(
                                    "missing-operation-description",
                                    "Operation should have a description or summary",
                                )
                                .with_path(&op_path)
                                .with_severity(Severity::Warning),
                            );
                        }

                        // Check parameter descriptions
                        if let Some(params) = op.get("parameters").and_then(|p| p.as_array()) {
                            for (i, param) in params.iter().enumerate() {
                                if let Some(param_obj) = param.as_object() {
                                    if param_obj.get("description").is_none() {
                                        result.warnings.push(
                                            ValidationError::new(
                                                "missing-parameter-description",
                                                format!(
                                                    "Parameter '{}' should have a description",
                                                    param_obj
                                                        .get("name")
                                                        .and_then(|n| n.as_str())
                                                        .unwrap_or("unknown")
                                                ),
                                            )
                                            .with_path(&format!("{}.parameters[{}]", op_path, i))
                                            .with_severity(Severity::Warning),
                                        );
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

fn check_missing_examples(spec: &Value, result: &mut ValidationResult) {
    if let Some(paths) = spec.get("paths").and_then(|p| p.as_object()) {
        for (path, path_item) in paths {
            if let Some(path_obj) = path_item.as_object() {
                for (method, operation) in path_obj {
                    if ["parameters", "servers", "$ref", "summary", "description"]
                        .contains(&method.as_str())
                    {
                        continue;
                    }

                    if let Some(op) = operation.as_object() {
                        let op_path = format!("$.paths.{}.{}", path, method);

                        // Check for request body examples
                        if let Some(request_body) =
                            op.get("requestBody").and_then(|r| r.as_object())
                        {
                            if let Some(content) =
                                request_body.get("content").and_then(|c| c.as_object())
                            {
                                for (media_type, media) in content {
                                    if media.get("example").is_none()
                                        && media.get("examples").is_none()
                                    {
                                        result.warnings.push(
                                            ValidationError::new(
                                                "missing-request-example",
                                                format!(
                                                    "Request body for {} should have an example",
                                                    media_type
                                                ),
                                            )
                                            .with_path(&format!(
                                                "{}.requestBody.content.{}",
                                                op_path, media_type
                                            ))
                                            .with_severity(Severity::Warning),
                                        );
                                    }
                                }
                            }
                        }

                        // Check for response examples
                        if let Some(responses) = op.get("responses").and_then(|r| r.as_object()) {
                            for (status, response) in responses {
                                if let Some(content) =
                                    response.get("content").and_then(|c| c.as_object())
                                {
                                    for (media_type, media) in content {
                                        if media.get("example").is_none()
                                            && media.get("examples").is_none()
                                        {
                                            result.warnings.push(
                                                ValidationError::new(
                                                    "missing-response-example",
                                                    format!(
                                                        "Response {} for {} should have an example",
                                                        status, media_type
                                                    ),
                                                )
                                                .with_path(&format!(
                                                    "{}.responses.{}.content.{}",
                                                    op_path, status, media_type
                                                ))
                                                .with_severity(Severity::Warning),
                                            );
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

fn check_naming_conventions(spec: &Value, result: &mut ValidationResult) {
    // Check operation IDs for camelCase
    if let Some(paths) = spec.get("paths").and_then(|p| p.as_object()) {
        for (path, path_item) in paths {
            if let Some(path_obj) = path_item.as_object() {
                for (method, operation) in path_obj {
                    if ["parameters", "servers", "$ref", "summary", "description"]
                        .contains(&method.as_str())
                    {
                        continue;
                    }

                    if let Some(op) = operation.as_object() {
                        if let Some(op_id) = op.get("operationId").and_then(|id| id.as_str()) {
                            if !is_camel_case(op_id) && !is_snake_case(op_id) {
                                result.warnings.push(
                                    ValidationError::new(
                                        "inconsistent-operation-id",
                                        format!(
                                            "Operation ID '{}' should use camelCase or snake_case",
                                            op_id
                                        ),
                                    )
                                    .with_path(&format!("$.paths.{}.{}.operationId", path, method))
                                    .with_severity(Severity::Warning),
                                );
                            }
                        }
                    }
                }
            }
        }
    }

    // Check schema names for PascalCase
    if let Some(schemas) = spec
        .get("components")
        .and_then(|c| c.get("schemas"))
        .and_then(|s| s.as_object())
    {
        for (name, _) in schemas {
            if !is_pascal_case(name) {
                result.warnings.push(
                    ValidationError::new(
                        "schema-naming-convention",
                        format!("Schema name '{}' should use PascalCase", name),
                    )
                    .with_path(&format!("$.components.schemas.{}", name))
                    .with_severity(Severity::Warning),
                );
            }
        }
    }
}

fn check_unused_components(spec: &Value, result: &mut ValidationResult) {
    use std::collections::HashSet;

    // Collect all references
    let mut used_refs = HashSet::new();
    collect_refs(spec, &mut used_refs);

    // Check unused schemas
    if let Some(schemas) = spec
        .get("components")
        .and_then(|c| c.get("schemas"))
        .and_then(|s| s.as_object())
    {
        for (name, _) in schemas {
            let ref_path = format!("#/components/schemas/{}", name);
            if !used_refs.contains(&ref_path) {
                result.warnings.push(
                    ValidationError::new(
                        "unused-schema",
                        format!("Schema '{}' is defined but never used", name),
                    )
                    .with_path(&format!("$.components.schemas.{}", name))
                    .with_severity(Severity::Warning),
                );
            }
        }
    }
}

fn collect_refs(value: &Value, refs: &mut HashSet<String>) {
    match value {
        Value::Object(map) => {
            for (key, val) in map {
                if key == "$ref" {
                    if let Some(ref_str) = val.as_str() {
                        refs.insert(ref_str.to_string());
                    }
                } else {
                    collect_refs(val, refs);
                }
            }
        }
        Value::Array(arr) => {
            for val in arr {
                collect_refs(val, refs);
            }
        }
        _ => {}
    }
}

fn is_camel_case(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }

    let chars: Vec<char> = s.chars().collect();

    // First character should be lowercase
    if !chars[0].is_lowercase() {
        return false;
    }

    // No underscores or hyphens
    if s.contains('_') || s.contains('-') {
        return false;
    }

    true
}

fn is_snake_case(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }

    // All lowercase with underscores
    s.chars()
        .all(|c| c.is_lowercase() || c.is_numeric() || c == '_')
}

fn is_pascal_case(s: &str) -> bool {
    if s.is_empty() {
        return false;
    }

    let chars: Vec<char> = s.chars().collect();

    // First character should be uppercase
    if !chars[0].is_uppercase() {
        return false;
    }

    // No underscores or hyphens
    if s.contains('_') || s.contains('-') {
        return false;
    }

    true
}
