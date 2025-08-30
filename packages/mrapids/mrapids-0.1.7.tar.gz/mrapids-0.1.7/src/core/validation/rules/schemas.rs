use crate::core::validation::types::{Severity, ValidationError, ValidationResult};
/// Validation rules for schemas
use serde_json::Value;

/// Validate schema definitions for type violations
pub fn validate_schemas(spec: &Value) -> ValidationResult {
    let mut result = ValidationResult::new();

    // Check OpenAPI 3.x components
    if let Some(schemas) = spec
        .get("components")
        .and_then(|c| c.get("schemas"))
        .and_then(|s| s.as_object())
    {
        for (name, schema) in schemas {
            validate_schema_definition(
                schema,
                &format!("$.components.schemas.{}", name),
                &mut result,
            );
        }
    }

    // Check Swagger 2.0 definitions
    if let Some(definitions) = spec.get("definitions").and_then(|d| d.as_object()) {
        for (name, schema) in definitions {
            validate_schema_definition(schema, &format!("$.definitions.{}", name), &mut result);
        }
    }

    // Check inline schemas in operations
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

                        // Check request body schemas
                        if let Some(request_body) =
                            op.get("requestBody").and_then(|r| r.as_object())
                        {
                            if let Some(content) =
                                request_body.get("content").and_then(|c| c.as_object())
                            {
                                for (media_type, media) in content {
                                    if let Some(schema) = media.get("schema") {
                                        validate_schema_definition(
                                            schema,
                                            &format!(
                                                "{}.requestBody.content.{}.schema",
                                                op_path, media_type
                                            ),
                                            &mut result,
                                        );
                                    }
                                }
                            }
                        }

                        // Check response schemas
                        if let Some(responses) = op.get("responses").and_then(|r| r.as_object()) {
                            for (status, response) in responses {
                                if let Some(content) =
                                    response.get("content").and_then(|c| c.as_object())
                                {
                                    for (media_type, media) in content {
                                        if let Some(schema) = media.get("schema") {
                                            validate_schema_definition(
                                                schema,
                                                &format!(
                                                    "{}.responses.{}.content.{}.schema",
                                                    op_path, status, media_type
                                                ),
                                                &mut result,
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

    result
}

fn validate_schema_definition(schema: &Value, path: &str, result: &mut ValidationResult) {
    if let Some(schema_obj) = schema.as_object() {
        // Check for type violations
        if let Some(type_val) = schema_obj.get("type").and_then(|t| t.as_str()) {
            validate_type_constraints(type_val, schema_obj, path, result);
        }

        // Recursively validate nested schemas
        if let Some(properties) = schema_obj.get("properties").and_then(|p| p.as_object()) {
            for (prop_name, prop_schema) in properties {
                validate_schema_definition(
                    prop_schema,
                    &format!("{}.properties.{}", path, prop_name),
                    result,
                );
            }
        }

        if let Some(items) = schema_obj.get("items") {
            validate_schema_definition(items, &format!("{}.items", path), result);
        }

        if let Some(all_of) = schema_obj.get("allOf").and_then(|a| a.as_array()) {
            for (i, sub_schema) in all_of.iter().enumerate() {
                validate_schema_definition(sub_schema, &format!("{}.allOf[{}]", path, i), result);
            }
        }

        if let Some(one_of) = schema_obj.get("oneOf").and_then(|o| o.as_array()) {
            for (i, sub_schema) in one_of.iter().enumerate() {
                validate_schema_definition(sub_schema, &format!("{}.oneOf[{}]", path, i), result);
            }
        }

        if let Some(any_of) = schema_obj.get("anyOf").and_then(|a| a.as_array()) {
            for (i, sub_schema) in any_of.iter().enumerate() {
                validate_schema_definition(sub_schema, &format!("{}.anyOf[{}]", path, i), result);
            }
        }
    }
}

fn validate_type_constraints(
    type_val: &str,
    schema: &serde_json::Map<String, Value>,
    path: &str,
    result: &mut ValidationResult,
) {
    let numeric_constraints = [
        "minimum",
        "maximum",
        "exclusiveMinimum",
        "exclusiveMaximum",
        "multipleOf",
    ];
    let string_constraints = ["minLength", "maxLength", "pattern"];
    let array_constraints = ["minItems", "maxItems", "uniqueItems"];
    let _object_constraints = ["minProperties", "maxProperties"];

    match type_val {
        "string" => {
            // Check for numeric constraints on string type
            for constraint in &numeric_constraints {
                if schema.contains_key(*constraint) {
                    result.errors.push(
                        ValidationError::new(
                            "invalid-type-constraint",
                            format!(
                                "String type cannot have numeric constraint '{}'",
                                constraint
                            ),
                        )
                        .with_path(path),
                    );
                }
            }

            // Check for invalid format
            if let Some(format) = schema.get("format").and_then(|f| f.as_str()) {
                let valid_string_formats = [
                    "date",
                    "date-time",
                    "password",
                    "byte",
                    "binary",
                    "email",
                    "hostname",
                    "ipv4",
                    "ipv6",
                    "uri",
                    "uri-reference",
                    "uuid",
                ];
                if !valid_string_formats.contains(&format) && !format.starts_with("x-") {
                    result.warnings.push(
                        ValidationError::new(
                            "unknown-string-format",
                            format!("Unknown string format '{}'", format),
                        )
                        .with_path(path)
                        .with_severity(Severity::Warning),
                    );
                }
            }
        }
        "integer" | "number" => {
            // Check for string constraints on numeric type
            for constraint in &string_constraints {
                if schema.contains_key(*constraint) {
                    result.errors.push(
                        ValidationError::new(
                            "invalid-type-constraint",
                            format!(
                                "Numeric type cannot have string constraint '{}'",
                                constraint
                            ),
                        )
                        .with_path(path),
                    );
                }
            }

            // Check for invalid format combinations
            if let Some(format) = schema.get("format").and_then(|f| f.as_str()) {
                if type_val == "integer"
                    && ["email", "date", "date-time", "password", "byte", "binary"]
                        .contains(&format)
                {
                    result.errors.push(
                        ValidationError::new(
                            "invalid-format-for-type",
                            format!("Format '{}' is not valid for integer type", format),
                        )
                        .with_path(path),
                    );
                }
            }
        }
        "boolean" => {
            // Booleans shouldn't have any constraints
            for constraint in numeric_constraints
                .iter()
                .chain(string_constraints.iter())
                .chain(array_constraints.iter())
            {
                if schema.contains_key(*constraint) {
                    result.errors.push(
                        ValidationError::new(
                            "invalid-type-constraint",
                            format!("Boolean type cannot have constraint '{}'", constraint),
                        )
                        .with_path(path),
                    );
                }
            }
        }
        "array" => {
            // Check for non-array constraints
            for constraint in numeric_constraints.iter().chain(string_constraints.iter()) {
                if schema.contains_key(*constraint) {
                    result.errors.push(
                        ValidationError::new(
                            "invalid-type-constraint",
                            format!("Array type cannot have constraint '{}'", constraint),
                        )
                        .with_path(path),
                    );
                }
            }

            // Arrays must have items
            if !schema.contains_key("items") {
                result.warnings.push(
                    ValidationError::new(
                        "array-without-items",
                        "Array type should define 'items' schema",
                    )
                    .with_path(path)
                    .with_severity(Severity::Warning),
                );
            }
        }
        "object" => {
            // Check for non-object constraints
            for constraint in numeric_constraints
                .iter()
                .chain(string_constraints.iter())
                .chain(array_constraints.iter())
            {
                if schema.contains_key(*constraint) {
                    result.errors.push(
                        ValidationError::new(
                            "invalid-type-constraint",
                            format!("Object type cannot have constraint '{}'", constraint),
                        )
                        .with_path(path),
                    );
                }
            }
        }
        _ => {
            // Unknown type
            result.errors.push(
                ValidationError::new(
                    "unknown-type",
                    format!("Unknown schema type '{}'", type_val),
                )
                .with_path(path),
            );
        }
    }
}
