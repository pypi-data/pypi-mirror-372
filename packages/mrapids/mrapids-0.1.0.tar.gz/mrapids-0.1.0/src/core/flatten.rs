use crate::cli::{FlattenCommand, FlattenFormat};
use crate::core::external_refs::flatten_spec;
use crate::core::parser::{parse_openapi_v3, OpenAPIDocument, ReferenceOr, SpecResolver};
use crate::utils::security::{validate_file_path, validate_output_path};
use anyhow::{Context, Result};
use colored::*;
use serde_json::Value;
use std::fs;
use std::path::Path;

pub async fn flatten_command(cmd: FlattenCommand) -> Result<()> {
    println!("🔧 {} Flatten", "MicroRapid".bright_cyan());
    println!(
        "📄 Loading spec from: {}",
        cmd.spec.display().to_string().cyan()
    );

    // Validate input file path
    validate_file_path(&cmd.spec).context("Invalid input spec path")?;

    // Load and parse the spec
    let content = fs::read_to_string(&cmd.spec)
        .map_err(|e| anyhow::anyhow!("Cannot read spec file: {}", e))?;

    // Parse as raw YAML/JSON first to preserve structure
    let raw_value: serde_yaml::Value =
        serde_yaml::from_str(&content).context("Failed to parse spec as YAML")?;

    // Convert to JSON Value for manipulation
    let mut json_value: Value =
        serde_json::to_value(&raw_value).context("Failed to convert YAML to JSON")?;

    // Check if we should use external reference support
    if cmd.resolve_external {
        println!("🔍 Resolving external references...");

        // Use async runtime to handle external references
        let base_path = cmd.spec.parent().unwrap_or(Path::new("."));
        flatten_spec(&mut json_value, base_path, cmd.allow_insecure).await?;

        // Remove components section if not including unused
        if !cmd.include_unused {
            if let Some(obj) = json_value.as_object_mut() {
                obj.remove("components");
                obj.remove("definitions"); // For Swagger 2.0
            }
        }
    } else {
        // Use the existing local-only flattening
        // Check if it's OpenAPI or Swagger
        let is_openapi = json_value.get("openapi").is_some();

        let components = if is_openapi {
            // Parse as OpenAPI to get components
            let _openapi_result = parse_openapi_v3(&content)?;
            // We need to re-parse to get the actual OpenAPIDocument structure
            let openapi: OpenAPIDocument = serde_json::from_value(json_value.clone())
                .or_else(|_| serde_yaml::from_str(&content))
                .context("Failed to parse as OpenAPI document")?;
            openapi.components
        } else {
            // For Swagger 2.0, there are no components
            None
        };

        // Create resolver
        let mut resolver = SpecResolver::new(components);

        // Flatten the spec by resolving all references
        flatten_value(&mut json_value, &mut resolver, &mut Vec::new())?;

        // Remove components section if not including unused
        if !cmd.include_unused {
            if let Some(obj) = json_value.as_object_mut() {
                obj.remove("components");
            }
        }
    }

    // Output the flattened spec
    let output_content = match cmd.format {
        FlattenFormat::Yaml => {
            serde_yaml::to_string(&json_value).context("Failed to serialize to YAML")?
        }
        FlattenFormat::Json => {
            serde_json::to_string_pretty(&json_value).context("Failed to serialize to JSON")?
        }
    };

    if let Some(output_path) = cmd.output {
        // Validate output path
        validate_output_path(&output_path).context("Invalid output path")?;

        fs::write(&output_path, output_content)?;
        println!(
            "✅ Flattened spec written to: {}",
            output_path.display().to_string().green()
        );
    } else {
        println!("{}", output_content);
    }

    Ok(())
}

/// Recursively flatten a JSON value by resolving all $ref references
fn flatten_value(
    value: &mut Value,
    resolver: &mut SpecResolver,
    path: &mut Vec<String>,
) -> Result<()> {
    match value {
        Value::Object(map) => {
            // Check if this is a reference object
            if let Some(Value::String(ref_str)) = map.get("$ref") {
                let ref_str = ref_str.clone();

                // Resolve the reference
                let resolved = resolve_reference(&ref_str, resolver)?;

                // Replace the reference with the resolved value
                *value = resolved;

                // Continue flattening the resolved value
                flatten_value(value, resolver, path)?;
            } else {
                // Recursively flatten all values in the object
                for (key, val) in map.iter_mut() {
                    path.push(key.clone());
                    flatten_value(val, resolver, path)?;
                    path.pop();
                }
            }
        }
        Value::Array(arr) => {
            // Recursively flatten all values in the array
            for (i, val) in arr.iter_mut().enumerate() {
                path.push(format!("[{}]", i));
                flatten_value(val, resolver, path)?;
                path.pop();
            }
        }
        _ => {
            // Primitive values don't need flattening
        }
    }

    Ok(())
}

/// Resolve a reference string to its actual value
fn resolve_reference(reference: &str, resolver: &mut SpecResolver) -> Result<Value> {
    // Parse the reference path
    if let Some(path) = reference.strip_prefix("#/components/") {
        let parts: Vec<&str> = path.split('/').collect();
        if parts.len() != 2 {
            return Err(anyhow::anyhow!("Invalid reference format: {}", reference));
        }

        let component_type = parts[0];
        let _component_name = parts[1];

        // Resolve based on component type
        match component_type {
            "parameters" => {
                let param_ref = ReferenceOr::Reference {
                    reference: reference.to_string(),
                };
                let param = resolver.resolve_parameter(&param_ref)?;
                serde_json::to_value(param).context("Failed to serialize parameter")
            }
            "schemas" => {
                let schema_ref = ReferenceOr::Reference {
                    reference: reference.to_string(),
                };
                let schema = resolver.resolve_schema(&schema_ref)?;
                serde_json::to_value(schema).context("Failed to serialize schema")
            }
            "responses" => {
                let response_ref = ReferenceOr::Reference {
                    reference: reference.to_string(),
                };
                let response = resolver.resolve_response(&response_ref)?;
                serde_json::to_value(response).context("Failed to serialize response")
            }
            "requestBodies" => {
                let rb_ref = ReferenceOr::Reference {
                    reference: reference.to_string(),
                };
                let request_body = resolver.resolve_request_body(&rb_ref)?;
                serde_json::to_value(request_body).context("Failed to serialize request body")
            }
            _ => Err(anyhow::anyhow!(
                "Unsupported component type: {}",
                component_type
            )),
        }
    } else {
        Err(anyhow::anyhow!(
            "Only local references (#/components/...) are currently supported"
        ))
    }
}
