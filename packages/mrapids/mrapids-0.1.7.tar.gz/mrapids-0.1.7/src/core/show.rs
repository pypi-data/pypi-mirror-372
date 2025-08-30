use crate::cli::{ShowCommand, ShowFormat};
use crate::core::examples::generate_smart_example;
use crate::core::parser::{
    parse_spec, ParameterLocation, SchemaType, UnifiedOperation as Operation,
    UnifiedParameter as Parameter, UnifiedSchema as Schema, UnifiedSpec,
};
use crate::utils::security::validate_file_path;
use anyhow::{Context, Result};
use colored::*;
use std::path::{Path, PathBuf};

pub fn show_command(cmd: ShowCommand) -> Result<()> {
    // Determine spec file path
    let spec_path = cmd.spec.unwrap_or_else(|| {
        // Try common locations
        if Path::new("specs/api.yaml").exists() {
            PathBuf::from("specs/api.yaml")
        } else if Path::new("specs/api.yml").exists() {
            PathBuf::from("specs/api.yml")
        } else if Path::new("specs/api.json").exists() {
            PathBuf::from("specs/api.json")
        } else if Path::new("api.yaml").exists() {
            PathBuf::from("api.yaml")
        } else {
            PathBuf::from("openapi.yaml")
        }
    });

    // Validate spec file path
    validate_file_path(&spec_path)?;

    // Load and parse the spec
    let spec_content = std::fs::read_to_string(&spec_path)
        .with_context(|| format!("Failed to read spec file: {}", spec_path.display()))?;

    let spec = parse_spec(&spec_content)?;

    // Find the operation
    let operation_id = normalize_operation_id(&cmd.operation);
    let operation = find_operation(&spec, &operation_id)?;

    // Display based on format
    match cmd.format {
        ShowFormat::Pretty => {
            display_pretty(operation, &spec, cmd.examples);
            Ok(())
        }
        ShowFormat::Json => display_json(operation),
        ShowFormat::Yaml => display_yaml(operation),
    }
}

/// Find an operation by partial name match - public for use by run command
pub fn find_operation_with_spec<'a>(
    spec: &'a UnifiedSpec,
    operation_id: &str,
) -> Result<&'a Operation> {
    find_operation(spec, operation_id)
}

fn normalize_operation_id(id: &str) -> String {
    // Don't transform IDs with slashes - they're already valid operation IDs
    if id.contains('/') {
        return id.to_string();
    }

    // Convert kebab-case to camelCase if needed
    if id.contains('-') {
        id.split('-')
            .enumerate()
            .map(|(i, part)| {
                if i == 0 {
                    part.to_string()
                } else {
                    let mut chars = part.chars();
                    match chars.next() {
                        None => String::new(),
                        Some(first) => first.to_uppercase().chain(chars).collect(),
                    }
                }
            })
            .collect()
    } else {
        id.to_string()
    }
}

fn find_operation<'a>(
    spec: &'a crate::core::parser::UnifiedSpec,
    operation_id: &str,
) -> Result<&'a Operation> {
    let search_term = operation_id.to_lowercase();

    // Try exact match first (case-insensitive)
    if let Some(op) = spec
        .operations
        .iter()
        .find(|op| op.operation_id.to_lowercase() == search_term)
    {
        return Ok(op);
    }

    // Try converting kebab-case to camelCase
    let camel_case = normalize_operation_id(operation_id).to_lowercase();
    if let Some(op) = spec
        .operations
        .iter()
        .find(|op| op.operation_id.to_lowercase() == camel_case)
    {
        return Ok(op);
    }

    // Find all operations that contain the search term
    let matches: Vec<&Operation> = spec
        .operations
        .iter()
        .filter(|op| op.operation_id.to_lowercase().contains(&search_term))
        .collect();

    match matches.len() {
        0 => {
            // No matches - show available operations
            let available = spec
                .operations
                .iter()
                .map(|op| &op.operation_id)
                .take(10)
                .cloned()
                .collect::<Vec<_>>()
                .join(", ");

            Err(anyhow::anyhow!(
                "No operation matching '{}' found. Available operations: {} {}",
                operation_id,
                available,
                if spec.operations.len() > 10 {
                    "..."
                } else {
                    ""
                }
            ))
        }
        1 => {
            // Single match - use it
            println!(
                "{} Found operation: {}",
                "✓".green(),
                matches[0].operation_id.bright_cyan()
            );
            Ok(matches[0])
        }
        _ => {
            // Multiple matches - show them
            println!(
                "{} Multiple operations match '{}':",
                "?".yellow(),
                operation_id
            );
            for (i, op) in matches.iter().enumerate() {
                println!(
                    "  {} {}",
                    format!("{}.", i + 1).dimmed(),
                    op.operation_id.bright_cyan()
                );
            }
            Err(anyhow::anyhow!(
                "Please be more specific. Found {} operations matching '{}'",
                matches.len(),
                operation_id
            ))
        }
    }
}

fn display_pretty(operation: &Operation, spec: &UnifiedSpec, show_examples: bool) {
    // Header
    println!(
        "\n{} {}",
        operation.method.to_uppercase().bright_green().bold(),
        operation.path.bright_cyan()
    );

    // Summary
    if let Some(summary) = &operation.summary {
        println!("{}", summary.dimmed());
    }

    println!("{}", "━".repeat(60).dimmed());

    // Authentication requirements
    if let Some(security_reqs) = &operation.security {
        if !security_reqs.is_empty() {
            println!("\n{}", "AUTHENTICATION:".bright_red().bold());
            for req in security_reqs {
                if let Some(scheme) = spec.security_schemes.get(&req.scheme_name) {
                    match scheme.scheme_type.as_str() {
                        "apiKey" => {
                            let location_str = match scheme.location.as_deref() {
                                Some("header") => "header",
                                Some("query") => "query parameter",
                                Some("cookie") => "cookie",
                                _ => "header",
                            };
                            println!(
                                "  {} API Key required: {} in {}",
                                "►".bright_red(),
                                scheme.name.as_deref().unwrap_or("api_key").bright_yellow(),
                                location_str
                            );
                        }
                        "http" => match scheme.scheme.as_deref() {
                            Some("bearer") => {
                                println!(
                                    "  {} Bearer token required (Authorization: Bearer <token>)",
                                    "►".bright_red()
                                );
                            }
                            Some("basic") => {
                                println!(
                                    "  {} Basic auth required (Authorization: Basic <base64>)",
                                    "►".bright_red()
                                );
                            }
                            _ => {
                                println!(
                                    "  {} HTTP {} authentication required",
                                    "►".bright_red(),
                                    scheme.scheme.as_deref().unwrap_or("unknown")
                                );
                            }
                        },
                        "oauth2" => {
                            println!("  {} OAuth2 authentication required", "►".bright_red());
                            if !req.scopes.is_empty() {
                                println!("    Scopes: {}", req.scopes.join(", ").bright_black());
                            }
                        }
                        _ => {
                            println!(
                                "  {} {} authentication required",
                                "►".bright_red(),
                                req.scheme_name.bright_yellow()
                            );
                        }
                    }
                } else {
                    println!(
                        "  {} {} authentication required",
                        "►".bright_red(),
                        req.scheme_name.bright_yellow()
                    );
                }
            }
        }
    }

    // Path parameters (always required)
    let path_params: Vec<_> = operation
        .parameters
        .iter()
        .filter(|p| p.location == ParameterLocation::Path)
        .collect();

    if !path_params.is_empty() {
        println!("\n{}", "PATH PARAMETERS:".bright_yellow().bold());
        for param in &path_params {
            display_parameter(param, true);
        }
    }

    // Query parameters
    let query_params: Vec<_> = operation
        .parameters
        .iter()
        .filter(|p| p.location == ParameterLocation::Query)
        .collect();

    if !query_params.is_empty() {
        println!("\n{}", "QUERY PARAMETERS:".bright_blue().bold());
        for param in query_params {
            display_parameter_with_usage(param, false);
        }
    }

    // Header parameters (excluding auth headers)
    let header_params: Vec<_> = operation
        .parameters
        .iter()
        .filter(|p| p.location == ParameterLocation::Header)
        .filter(|p| {
            !p.name.eq_ignore_ascii_case("authorization")
                && !p.name.eq_ignore_ascii_case("x-api-key")
        })
        .collect();

    if !header_params.is_empty() {
        println!("\n{}", "HEADER PARAMETERS:".bright_cyan().bold());
        for param in header_params {
            display_parameter(param, param.required);
        }
    }

    // Request body
    if let Some(body) = &operation.request_body {
        println!("\n{}", "REQUEST BODY:".bright_yellow().bold());
        if let Some((content_type, schema)) = body.content.iter().next() {
            println!("  Content-Type: {}", content_type.dimmed());
            display_schema(&schema.schema, "", body.required);
        }
    }

    // Example command
    println!("\n{}", "EXAMPLE:".bright_green().bold());
    let example = generate_example_command(operation);
    println!("  {}", example.cyan());

    // Show response example
    if show_examples {
        println!("\n{}", "EXPECTED RESPONSE:".bright_green().bold());
        for (status, response) in &operation.responses {
            if status.starts_with('2') {
                println!(
                    "  Status: {} {}",
                    status.bright_green(),
                    response.description.dimmed()
                );
                if let Some((content_type, schema)) = response.content.iter().next() {
                    println!("  Content-Type: {}", content_type.dimmed());
                    // Show simplified response schema
                    if let Ok(example) = generate_response_example(&schema.schema) {
                        println!(
                            "  {}",
                            serde_json::to_string_pretty(&example)
                                .unwrap_or_default()
                                .bright_black()
                        );
                    }
                }
                break;
            }
        }
    }
}

fn display_parameter(param: &Parameter, required: bool) {
    let req_indicator = if required { "*" } else { " " };
    let type_str = schema_type_string(&param.schema);
    let description = param.description.as_deref().unwrap_or("");
    let example = generate_example_value(&param.name, &param.schema);

    println!(
        "  {} {:<15} {:<10} {} {}",
        req_indicator.bright_red(),
        param.name.bright_white(),
        type_str.dimmed(),
        description.dimmed(),
        format!("(e.g. {})", example).bright_black()
    );
}

fn display_parameter_with_usage(param: &Parameter, required: bool) {
    let req_indicator = if required { "*" } else { " " };
    let type_str = schema_type_string(&param.schema);
    let description = param.description.as_deref().unwrap_or("");
    let example = generate_example_value(&param.name, &param.schema);

    // Determine the purpose based on parameter name
    let purpose = match param.name.to_lowercase().as_str() {
        "limit" | "per_page" | "page_size" => "Pagination",
        "offset" | "page" | "skip" => "Pagination",
        "sort" | "order_by" | "sort_by" => "Sorting",
        "order" | "sort_order" | "direction" => "Sort direction",
        "filter" | "status" | "state" | "type" => "Filtering",
        "search" | "q" | "query" => "Search",
        "fields" | "select" | "include" => "Field selection",
        _ => "",
    };

    // First line: parameter name and type, clearly visible
    print!(
        "  {} {:<20}",
        req_indicator.bright_red(),
        param.name.bright_white().bold()
    );

    // Add type
    print!("{:<15}", type_str.bright_cyan());

    // Add purpose tag if identified
    if !purpose.is_empty() {
        print!("[{}]", purpose.bright_green());
    }
    println!();

    // Second line: usage example (more prominent)
    println!(
        "      → {}",
        format!("?{}={}", param.name, example).bright_yellow()
    );

    // Third line: description (if present, less prominent)
    if !description.is_empty() {
        // Wrap long descriptions
        let desc_lines = wrap_text(description, 70);
        for (i, line) in desc_lines.iter().enumerate() {
            if i == 0 {
                println!("      {}", line.dimmed());
            } else {
                println!("        {}", line.dimmed());
            }
        }
    }

    // Add spacing between parameters
    println!();
}

fn display_schema(schema: &Schema, indent: &str, _required: bool) {
    match &schema.schema_type {
        SchemaType::Object => {
            if let Some(props) = &schema.properties {
                for (name, prop_schema) in props {
                    let is_required = schema
                        .required
                        .as_ref()
                        .map(|r| r.contains(name))
                        .unwrap_or(false);

                    let type_str = schema_type_string(prop_schema);
                    let req_indicator = if is_required { "*" } else { " " };
                    let example = generate_example_value(name, prop_schema);

                    println!(
                        "  {}{} {:<15} {:<10} {}",
                        indent,
                        req_indicator.bright_red(),
                        name.bright_white(),
                        type_str.dimmed(),
                        format!("(e.g. {})", example).bright_black()
                    );

                    // Nested objects
                    if matches!(&prop_schema.schema_type, SchemaType::Object) {
                        display_schema(prop_schema, &format!("{}  ", indent), is_required);
                    }
                }
            }
        }
        _ => {}
    }
}

fn schema_type_string(schema: &Schema) -> String {
    match &schema.schema_type {
        SchemaType::String => {
            if let Some(format) = &schema.format {
                format!("string({})", format)
            } else if let Some(enums) = &schema.enum_values {
                format!(
                    "enum[{}]",
                    enums
                        .iter()
                        .map(|v| v.to_string())
                        .collect::<Vec<_>>()
                        .join("|")
                )
            } else {
                "string".to_string()
            }
        }
        SchemaType::Number => "number".to_string(),
        SchemaType::Integer => "integer".to_string(),
        SchemaType::Boolean => "boolean".to_string(),
        SchemaType::Array => {
            if let Some(items) = &schema.items {
                format!("{}[]", schema_type_string(items))
            } else {
                "array".to_string()
            }
        }
        SchemaType::Object => "object".to_string(),
        SchemaType::Unknown => "unknown".to_string(),
    }
}

fn generate_example_value(field_name: &str, schema: &Schema) -> String {
    // Use our smart example generation
    let value = generate_smart_example(field_name, schema);

    // Convert JSON value to string representation
    match value {
        serde_json::Value::String(s) => s,
        serde_json::Value::Number(n) => n.to_string(),
        serde_json::Value::Bool(b) => b.to_string(),
        serde_json::Value::Null => "null".to_string(),
        serde_json::Value::Array(_) => value.to_string(),
        serde_json::Value::Object(_) => value.to_string(),
    }
}

fn generate_example_command(operation: &Operation) -> String {
    let mut cmd = format!("mrapids run {}", operation.operation_id);

    // Add required parameters using --param syntax
    for param in &operation.parameters {
        if param.required && param.location == ParameterLocation::Path {
            let example = generate_example_value(&param.name, &param.schema);
            cmd.push_str(&format!(" --param {}={}", param.name, example));
        }
    }

    // Add example body parameters if POST/PUT/PATCH
    if matches!(operation.method.as_str(), "post" | "put" | "patch") {
        if let Some(body) = &operation.request_body {
            if body.required {
                // Show a couple of required fields as examples
                if let Some((_, schema)) = body.content.iter().next() {
                    if let Some(props) = &schema.schema.properties {
                        let required_fields: Vec<_> = schema
                            .schema
                            .required
                            .as_ref()
                            .map(|r| r.iter().take(2).collect())
                            .unwrap_or_default();

                        for field in required_fields {
                            if let Some(field_schema) = props.get(field) {
                                let example = generate_example_value(field, field_schema);
                                cmd.push_str(&format!(" --{} {}", field, example));
                            }
                        }
                    }
                }
            }
        }
    }

    cmd
}

fn generate_response_example(schema: &Schema) -> Result<serde_json::Value> {
    use serde_json::json;

    match &schema.schema_type {
        SchemaType::Object => {
            let mut obj = serde_json::Map::new();
            if let Some(props) = &schema.properties {
                for (name, prop_schema) in props.iter().take(5) {
                    // Limit to first 5 properties
                    let value = generate_response_example(prop_schema)?;
                    obj.insert(name.clone(), value);
                }
            }
            Ok(json!(obj))
        }
        SchemaType::Array => {
            if let Some(items) = &schema.items {
                let item = generate_response_example(items)?;
                Ok(json!([item]))
            } else {
                Ok(json!([]))
            }
        }
        SchemaType::String => Ok(json!(generate_example_value("field", schema))),
        SchemaType::Integer => Ok(json!(123)),
        SchemaType::Number => Ok(json!(123.45)),
        SchemaType::Boolean => Ok(json!(true)),
        SchemaType::Unknown => Ok(json!(null)),
    }
}

fn display_json(operation: &Operation) -> Result<()> {
    use serde_json::json;

    // Build a JSON representation manually
    let mut params_json = vec![];
    for param in &operation.parameters {
        params_json.push(json!({
            "name": param.name,
            "location": match param.location {
                ParameterLocation::Path => "path",
                ParameterLocation::Query => "query",
                ParameterLocation::Header => "header",
                ParameterLocation::Cookie => "cookie",
            },
            "required": param.required,
            "type": param.schema.schema_type.to_string(),
            "description": param.description,
            "example": generate_example_value(&param.name, &param.schema),
        }));
    }

    // Build request body JSON if present
    let request_body_json = if let Some(rb) = &operation.request_body {
        let mut content_json = serde_json::Map::new();
        for (content_type, media_type) in &rb.content {
            let schema_json = schema_to_json(&media_type.schema);
            content_json.insert(
                content_type.clone(),
                json!({
                    "schema": schema_json,
                    "example": media_type.example.clone(),
                }),
            );
        }
        Some(json!({
            "required": rb.required,
            "content": content_json,
        }))
    } else {
        None
    };

    // Build security requirements
    let security_json = if let Some(sec_reqs) = &operation.security {
        let reqs: Vec<_> = sec_reqs
            .iter()
            .map(|req| {
                json!({
                    "scheme": req.scheme_name,
                    "scopes": req.scopes,
                })
            })
            .collect();
        Some(reqs)
    } else {
        None
    };

    // Build final JSON
    let output = json!({
        "operation_id": operation.operation_id,
        "method": operation.method,
        "path": operation.path,
        "summary": operation.summary,
        "description": operation.description,
        "parameters": params_json,
        "request_body": request_body_json,
        "security": security_json,
    });

    println!("{}", serde_json::to_string_pretty(&output)?);
    Ok(())
}

fn schema_to_json(schema: &Schema) -> serde_json::Value {
    use serde_json::json;

    let mut json_schema = json!({
        "type": schema.schema_type.to_string(),
    });

    if let Some(obj) = json_schema.as_object_mut() {
        if let Some(desc) = &schema.description {
            obj.insert("description".to_string(), json!(desc));
        }

        if let Some(format) = &schema.format {
            obj.insert("format".to_string(), json!(format));
        }

        if let Some(example) = &schema.example {
            obj.insert("example".to_string(), example.clone());
        }

        if let Some(default) = &schema.default {
            obj.insert("default".to_string(), default.clone());
        }

        if let Some(min) = schema.minimum {
            obj.insert("minimum".to_string(), json!(min));
        }

        if let Some(max) = schema.maximum {
            obj.insert("maximum".to_string(), json!(max));
        }

        if let Some(props) = &schema.properties {
            let mut props_json = serde_json::Map::new();
            for (name, prop_schema) in props {
                props_json.insert(name.clone(), schema_to_json(prop_schema));
            }
            obj.insert("properties".to_string(), json!(props_json));
        }

        if let Some(required) = &schema.required {
            obj.insert("required".to_string(), json!(required));
        }

        if let Some(items) = &schema.items {
            obj.insert("items".to_string(), schema_to_json(items));
        }
    }

    json_schema
}

fn display_yaml(operation: &Operation) -> Result<()> {
    // Convert to JSON first, then to YAML
    use serde_json::json;

    // Build the same structure as JSON
    let mut params_json = vec![];
    for param in &operation.parameters {
        params_json.push(json!({
            "name": param.name,
            "location": match param.location {
                ParameterLocation::Path => "path",
                ParameterLocation::Query => "query",
                ParameterLocation::Header => "header",
                ParameterLocation::Cookie => "cookie",
            },
            "required": param.required,
            "type": param.schema.schema_type.to_string(),
            "description": param.description,
            "example": generate_example_value(&param.name, &param.schema),
        }));
    }

    let request_body_json = if let Some(rb) = &operation.request_body {
        let mut content_json = serde_json::Map::new();
        for (content_type, media_type) in &rb.content {
            let schema_json = schema_to_json(&media_type.schema);
            content_json.insert(
                content_type.clone(),
                json!({
                    "schema": schema_json,
                    "example": media_type.example.clone(),
                }),
            );
        }
        Some(json!({
            "required": rb.required,
            "content": content_json,
        }))
    } else {
        None
    };

    let security_json = if let Some(sec_reqs) = &operation.security {
        let reqs: Vec<_> = sec_reqs
            .iter()
            .map(|req| {
                json!({
                    "scheme": req.scheme_name,
                    "scopes": req.scopes,
                })
            })
            .collect();
        Some(reqs)
    } else {
        None
    };

    let output = json!({
        "operation_id": operation.operation_id,
        "method": operation.method,
        "path": operation.path,
        "summary": operation.summary,
        "description": operation.description,
        "parameters": params_json,
        "request_body": request_body_json,
        "security": security_json,
    });

    println!("{}", serde_yaml::to_string(&output)?);
    Ok(())
}

fn wrap_text(text: &str, max_width: usize) -> Vec<String> {
    let words: Vec<&str> = text.split_whitespace().collect();
    let mut lines = Vec::new();
    let mut current_line = String::new();

    for word in words {
        if current_line.is_empty() {
            current_line.push_str(word);
        } else if current_line.len() + word.len() + 1 <= max_width {
            current_line.push(' ');
            current_line.push_str(word);
        } else {
            lines.push(current_line);
            current_line = word.to_string();
        }
    }

    if !current_line.is_empty() {
        lines.push(current_line);
    }

    lines
}
