use crate::core::validation::types::{ValidationError, ValidationResult};
/// Validation rules for reference checking
use serde_json::Value;
use std::collections::HashSet;

/// Validate all references in the specification
pub fn validate_references(spec: &Value) -> ValidationResult {
    let mut result = ValidationResult::new();
    let mut resolver = ReferenceResolver::new(spec);

    // Collect all defined components
    resolver.collect_definitions();

    // Find and validate all references
    find_and_validate_refs(spec, &resolver, &mut result, "$");

    result
}

struct ReferenceResolver<'a> {
    spec: &'a Value,
    schemas: HashSet<String>,
    responses: HashSet<String>,
    parameters: HashSet<String>,
    request_bodies: HashSet<String>,
    security_schemes: HashSet<String>,
}

impl<'a> ReferenceResolver<'a> {
    fn new(spec: &'a Value) -> Self {
        Self {
            spec,
            schemas: HashSet::new(),
            responses: HashSet::new(),
            parameters: HashSet::new(),
            request_bodies: HashSet::new(),
            security_schemes: HashSet::new(),
        }
    }

    fn collect_definitions(&mut self) {
        // OpenAPI 3.x components
        if let Some(components) = self.spec.get("components").and_then(|c| c.as_object()) {
            if let Some(schemas) = components.get("schemas").and_then(|s| s.as_object()) {
                self.schemas.extend(schemas.keys().cloned());
            }
            if let Some(responses) = components.get("responses").and_then(|r| r.as_object()) {
                self.responses.extend(responses.keys().cloned());
            }
            if let Some(params) = components.get("parameters").and_then(|p| p.as_object()) {
                self.parameters.extend(params.keys().cloned());
            }
            if let Some(bodies) = components.get("requestBodies").and_then(|b| b.as_object()) {
                self.request_bodies.extend(bodies.keys().cloned());
            }
            if let Some(schemes) = components
                .get("securitySchemes")
                .and_then(|s| s.as_object())
            {
                self.security_schemes.extend(schemes.keys().cloned());
            }
        }

        // Swagger 2.0 definitions
        if let Some(definitions) = self.spec.get("definitions").and_then(|d| d.as_object()) {
            self.schemas.extend(definitions.keys().cloned());
        }
        if let Some(responses) = self.spec.get("responses").and_then(|r| r.as_object()) {
            self.responses.extend(responses.keys().cloned());
        }
        if let Some(params) = self.spec.get("parameters").and_then(|p| p.as_object()) {
            self.parameters.extend(params.keys().cloned());
        }
    }

    fn validate_reference(&self, reference: &str) -> Option<ValidationError> {
        if !reference.starts_with('#') {
            // External reference - skip for now
            return None;
        }

        let parts: Vec<&str> = reference.split('/').collect();
        if parts.len() < 3 {
            return Some(ValidationError::new(
                "invalid-reference-format",
                format!("Invalid reference format: {}", reference),
            ));
        }

        match (parts.get(1), parts.get(2), parts.get(3)) {
            (Some(&"components"), Some(&"schemas"), Some(name))
            | (Some(&"definitions"), Some(name), _) => {
                if !self.schemas.contains(*name) {
                    return Some(ValidationError::new(
                        "undefined-schema",
                        format!("Schema '{}' is not defined", name),
                    ));
                }
            }
            (Some(&"components"), Some(&"responses"), Some(name))
            | (Some(&"responses"), Some(name), _) => {
                if !self.responses.contains(*name) {
                    return Some(ValidationError::new(
                        "undefined-response",
                        format!("Response '{}' is not defined", name),
                    ));
                }
            }
            (Some(&"components"), Some(&"parameters"), Some(name))
            | (Some(&"parameters"), Some(name), _) => {
                if !self.parameters.contains(*name) {
                    return Some(ValidationError::new(
                        "undefined-parameter",
                        format!("Parameter '{}' is not defined", name),
                    ));
                }
            }
            (Some(&"components"), Some(&"requestBodies"), Some(name)) => {
                if !self.request_bodies.contains(*name) {
                    return Some(ValidationError::new(
                        "undefined-request-body",
                        format!("Request body '{}' is not defined", name),
                    ));
                }
            }
            (Some(&"components"), Some(&"securitySchemes"), Some(name)) => {
                if !self.security_schemes.contains(*name) {
                    return Some(ValidationError::new(
                        "undefined-security-scheme",
                        format!("Security scheme '{}' is not defined", name),
                    ));
                }
            }
            _ => {
                // Other reference types - could add more validation
            }
        }

        None
    }
}

fn find_and_validate_refs(
    value: &Value,
    resolver: &ReferenceResolver,
    result: &mut ValidationResult,
    path: &str,
) {
    match value {
        Value::Object(map) => {
            for (key, val) in map {
                let new_path = if path == "$" {
                    format!("$.{}", key)
                } else {
                    format!("{}.{}", path, key)
                };

                if key == "$ref" {
                    if let Some(ref_str) = val.as_str() {
                        if let Some(error) = resolver.validate_reference(ref_str) {
                            result.errors.push(error.with_path(&new_path));
                        }
                    }
                } else {
                    find_and_validate_refs(val, resolver, result, &new_path);
                }
            }
        }
        Value::Array(arr) => {
            for (i, val) in arr.iter().enumerate() {
                let new_path = format!("{}[{}]", path, i);
                find_and_validate_refs(val, resolver, result, &new_path);
            }
        }
        _ => {}
    }
}
