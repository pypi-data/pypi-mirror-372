// Analyze command using proper parsers
// This replaces the old analyze.rs with accurate schema-based generation

use crate::cli::AnalyzeCommand;
use crate::core::examples::{generate_body_example, generate_smart_example};
use crate::core::parser::{parse_spec, ParameterLocation, UnifiedOperation};
use crate::core::validation::{SpecValidator, ValidationLevel};
use crate::utils::security::{validate_file_path, validate_output_path};
use anyhow::Result;
use colored::*;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::collections::HashMap;
use std::fs;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize)]
struct RequestConfig {
    operation: String,
    method: String,
    path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    description: Option<String>,
    #[serde(skip_serializing_if = "HashMap::is_empty")]
    headers: HashMap<String, String>,
    #[serde(skip_serializing_if = "HashMap::is_empty")]
    params: HashMap<String, String>,
    #[serde(skip_serializing_if = "HashMap::is_empty")]
    path_params: HashMap<String, Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    body: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    expect: Option<ExpectConfig>,
}

#[derive(Debug, Serialize, Deserialize)]
struct ExpectConfig {
    status: u16,
    #[serde(skip_serializing_if = "Option::is_none")]
    content_type: Option<String>,
}

pub fn analyze_command(cmd: AnalyzeCommand) -> Result<()> {
    use crate::utils::cleanup;

    println!("{} Analyzing API specification...", "🔍".bright_blue());

    // Use spec from command if provided, otherwise look in default locations
    let spec_file = if let Some(spec) = &cmd.spec {
        spec.clone()
    } else {
        // Try to find spec file in common locations
        let spec_paths = vec![
            Path::new("specs/api.yaml"),
            Path::new("specs/api.json"),
            Path::new("api.yaml"),
            Path::new("api.json"),
            Path::new("openapi.yaml"),
            Path::new("openapi.json"),
            Path::new("swagger.yaml"),
            Path::new("swagger.json"),
        ];

        let spec_path = spec_paths.iter().find(|p| p.exists());

        if spec_path.is_none() {
            println!(
                "{} No API specification found. Provide a spec file or run 'mrapids init' first.",
                "⚠️".yellow()
            );
            println!("  Usage: mrapids analyze <spec-file>");
            return Err(anyhow::anyhow!("No specification file found"));
        }

        spec_path.unwrap().to_path_buf()
    };

    // Check if spec file exists
    if !spec_file.exists() {
        return Err(anyhow::anyhow!(
            "Specification file not found: {}. Run 'mrapids init' first or specify a valid spec file.",
            spec_file.display()
        ));
    }

    // Validate input spec path
    validate_file_path(&spec_file)?;

    // Validate output directory path
    validate_output_path(&cmd.output)?;

    println!(
        "📄 Loading spec from: {}",
        spec_file.display().to_string().cyan()
    );

    // Load spec content
    let content = fs::read_to_string(&spec_file)
        .map_err(|e| anyhow::anyhow!("Cannot read spec file: {}", e))?;

    // Validate the specification before analysis
    if !cmd.skip_validate {
        println!("{} Validating specification...", "🔍".bright_cyan());
        let validator = SpecValidator::new()?;
        let validation_report = validator.validate_content(&content, ValidationLevel::Standard)?;

        if !validation_report.is_valid() {
            println!("\n{} Specification has validation errors:", "❌".red());
            validation_report.display();
            return Err(anyhow::anyhow!(
                "Specification validation failed. Use --skip-validate to bypass validation."
            ));
        } else if validation_report.has_warnings() {
            println!("{} Specification has warnings:", "⚠️".yellow());
            validation_report.display();
        } else {
            println!("{} Specification is valid!", "✅".green());
        }
    }

    // Parse with proper parser
    let spec = parse_spec(&content)?;

    println!(
        "📋 API: {} v{}",
        spec.info.title.bright_yellow(),
        spec.info.version
    );
    if let Some(desc) = &spec.info.description {
        println!("   {}", desc.dimmed());
    }

    // Create output directories
    let requests_dir = cmd.output.join("requests");
    let examples_dir = requests_dir.join("examples");
    let data_dir = cmd.output.join("data");
    let data_examples_dir = data_dir.join("examples");

    // Debug output
    if std::env::var("MRAPIDS_DEBUG").is_ok() {
        eprintln!("Debug: Output dir: {}", cmd.output.display());
        eprintln!("Debug: Requests dir: {}", requests_dir.display());
        eprintln!("Debug: Examples dir: {}", examples_dir.display());
    }

    fs::create_dir_all(&examples_dir).map_err(|e| {
        anyhow::anyhow!(
            "Failed to create examples directory '{}': {}",
            examples_dir.display(),
            e
        )
    })?;
    if !cmd.skip_data {
        fs::create_dir_all(&data_examples_dir).map_err(|e| {
            anyhow::anyhow!(
                "Failed to create data examples directory '{}': {}",
                data_examples_dir.display(),
                e
            )
        })?;
    }

    // Count operations
    let total_operations = spec.operations.len();
    let mut generated_requests = 0;
    let mut generated_data = 0;
    let mut found_matching_operation = false;

    // Process each operation
    for operation in &spec.operations {
        // Skip if filtering by operation and doesn't match
        if let Some(ref filter_op) = cmd.operation {
            if &operation.operation_id != filter_op {
                continue;
            }
            found_matching_operation = true;
        }

        // Generate request config
        let request_config = match generate_request_config(
            operation,
            &spec.base_url,
            &data_examples_dir,
            cmd.skip_data,
        ) {
            Ok(config) => config,
            Err(e) => {
                eprintln!(
                    "Error generating config for operation '{}': {}",
                    operation.operation_id, e
                );
                return Err(e);
            }
        };

        // Determine filename
        let filename = format!("{}.yaml", to_kebab_case(&operation.operation_id));
        let request_file = examples_dir.join(&filename);

        // Debug output
        if std::env::var("MRAPIDS_DEBUG").is_ok() {
            eprintln!("Debug: Operation ID: {}", operation.operation_id);
            eprintln!("Debug: Filename: {}", filename);
            eprintln!("Debug: Request file path: {}", request_file.display());
            eprintln!("Debug: Examples dir exists: {}", examples_dir.exists());
        }

        // Check if file exists and handle force flag
        if request_file.exists() && !cmd.force {
            println!("  ⚠️  Skipping existing: {}", filename.yellow());
            continue;
        }

        // Write request config
        let yaml_content = serde_yaml::to_string(&request_config)?;

        // Add header comment with more details
        let full_content = format!(
            "# Auto-generated from {}\n# Operation: {}\n# Method: {} {}\n{}\n# Generated by MicroRapid with accurate schema parsing\n\n{}",
            spec_file.display(),
            operation.operation_id,
            operation.method,
            operation.path,
            operation.summary.as_ref()
                .map(|s| format!("# Summary: {}\n", s))
                .unwrap_or_default(),
            yaml_content
        );

        fs::write(&request_file, &full_content).map_err(|e| {
            anyhow::anyhow!("Failed to write file '{}': {}", request_file.display(), e)
        })?;
        println!("  ✅ Generated: requests/examples/{}", filename.green());
        generated_requests += 1;

        // Generate data file if needed
        if !cmd.skip_data && needs_body(&operation.method) {
            if let Some(ref body_file) = request_config.body {
                // Generate accurate example JSON data from schema
                let data_content = generate_example_data(operation)?;
                let data_file = cmd.output.join(body_file);

                if !data_file.exists() || cmd.force {
                    // Pretty print JSON with comments
                    let formatted_json = serde_json::to_string_pretty(&data_content)?;
                    let data_with_header = format!(
                        "// Auto-generated example for {}\n// Operation: {}\n// Customize this file as needed\n\n{}",
                        operation.operation_id,
                        operation.summary.as_deref().unwrap_or(""),
                        formatted_json
                    );

                    fs::write(&data_file, data_with_header)?;
                    println!("  ✅ Generated: {}", body_file.green());
                    generated_data += 1;
                }
            }
        }
    }

    // Check if we found the operation when filtering
    if let Some(ref filter_op) = cmd.operation {
        if !found_matching_operation {
            // Try to find similar operations
            let similar_ops: Vec<&str> = spec
                .operations
                .iter()
                .filter(|op| {
                    op.operation_id
                        .to_lowercase()
                        .contains(&filter_op.to_lowercase())
                })
                .take(5)
                .map(|op| op.operation_id.as_str())
                .collect();

            println!("\n{} Operation '{}' not found!", "❌".red(), filter_op);

            if !similar_ops.is_empty() {
                println!("\n{} Did you mean one of these?", "💡".yellow());
                for op in similar_ops {
                    println!("  • {}", op.bright_cyan());
                }
            }

            println!(
                "\n{} Use 'mrapids list operations' to see all available operations",
                "ℹ️".blue()
            );
            return Ok(());
        }
    }

    // Print summary
    println!("\n{} Analysis complete!", "✅".green());
    println!("📊 Summary:");
    println!(
        "  • Total operations: {}",
        total_operations.to_string().bright_yellow()
    );
    println!(
        "  • Request configs generated: {}",
        generated_requests.to_string().bright_green()
    );
    if !cmd.skip_data {
        println!(
            "  • Data files generated: {}",
            generated_data.to_string().bright_green()
        );
    }

    // Print accuracy note
    println!(
        "\n{} Using proper OpenAPI/Swagger parsers for accurate schema-based generation",
        "🎯".bright_cyan()
    );

    // Print next steps
    if generated_requests > 0 {
        println!("\n{} Next steps:", "💡".bright_green());
        println!("  1. Review generated examples in requests/examples/");
        if !cmd.skip_data {
            println!("  2. Customize data files in data/examples/");
        }
        println!("  3. Run requests: mrapids run <request-name>");
        println!("  4. List operations: mrapids list operations");
    }

    // Clean up old backups if enabled
    if cmd.cleanup_backups {
        cleanup::cleanup_analyze_artifacts(&cmd.output, true)?;
    }

    Ok(())
}

fn generate_request_config(
    operation: &UnifiedOperation,
    _base_url: &str,
    _data_dir: &Path,
    skip_data: bool,
) -> Result<RequestConfig> {
    let mut config = RequestConfig {
        operation: operation.operation_id.clone(),
        method: operation.method.clone(),
        path: operation.path.clone(),
        description: operation.summary.clone(),
        headers: HashMap::new(),
        params: HashMap::new(),
        path_params: HashMap::new(),
        body: None,
        expect: None,
    };

    // Add appropriate headers based on request body
    if let Some(request_body) = &operation.request_body {
        // Use the first content type (usually application/json)
        if let Some((content_type, _)) = request_body.content.iter().next() {
            config
                .headers
                .insert("Content-Type".to_string(), content_type.clone());
        }
    }
    config
        .headers
        .insert("Accept".to_string(), "application/json".to_string());

    // Extract parameters with accurate examples from schema
    for param in &operation.parameters {
        let example_value = if let Some(example) = &param.example {
            example.clone()
        } else {
            generate_smart_example(&param.name, &param.schema)
        };

        match param.location {
            ParameterLocation::Path => {
                config.path_params.insert(param.name.clone(), example_value);
            }
            ParameterLocation::Query => {
                config
                    .params
                    .insert(param.name.clone(), example_value.to_string());
            }
            ParameterLocation::Header => {
                if param.name != "Accept" && param.name != "Content-Type" {
                    config
                        .headers
                        .insert(param.name.clone(), example_value.to_string());
                }
            }
            ParameterLocation::Cookie => {
                // Cookies could be added to headers if needed
            }
        }
    }

    // Set body file if needed
    if needs_body(&operation.method) && !skip_data {
        let data_filename = format!(
            "data/examples/{}.json",
            to_kebab_case(&operation.operation_id)
        );
        config.body = Some(data_filename);
    }

    // Set expected response (look for success responses)
    for (status_code, response) in &operation.responses {
        if status_code.starts_with('2') {
            // Success response
            let status: u16 = status_code.parse().unwrap_or(200);
            let content_type = response.content.keys().next().cloned();

            config.expect = Some(ExpectConfig {
                status,
                content_type,
            });
            break;
        }
    }

    // Default to 200 if no success response defined
    if config.expect.is_none() {
        config.expect = Some(ExpectConfig {
            status: 200,
            content_type: Some("application/json".to_string()),
        });
    }

    Ok(config)
}

fn generate_example_data(operation: &UnifiedOperation) -> Result<Value> {
    // Generate accurate example JSON based on request body schema
    if let Some(request_body) = &operation.request_body {
        // Get the first content type (preferably application/json)
        let media_type = request_body
            .content
            .get("application/json")
            .or_else(|| request_body.content.values().next());

        if let Some(media) = media_type {
            // Use provided example or generate from schema
            if let Some(example) = &media.example {
                return Ok(example.clone());
            } else {
                return Ok(generate_body_example(&media.schema));
            }
        }
    }

    // Fallback for operations without defined request body
    Ok(json!({
        "note": "No request body schema found in specification",
        "hint": "Add your request data here"
    }))
}

fn needs_body(method: &str) -> bool {
    matches!(method.to_uppercase().as_str(), "POST" | "PUT" | "PATCH")
}

fn to_kebab_case(s: &str) -> String {
    let mut result = String::new();
    let mut prev_is_lower = false;

    for ch in s.chars() {
        if ch == '/' || ch == '\\' {
            // Replace path separators with hyphens
            result.push('-');
            prev_is_lower = false;
        } else if ch == ' ' || ch == '_' {
            // Replace spaces and underscores with hyphens
            result.push('-');
            prev_is_lower = false;
        } else if ch.is_uppercase() && prev_is_lower {
            result.push('-');
            result.push(ch.to_lowercase().next().unwrap());
            prev_is_lower = false;
        } else if ch.is_alphanumeric() {
            result.push(ch.to_lowercase().next().unwrap());
            prev_is_lower = ch.is_lowercase();
        }
        // Skip other special characters
    }

    // Remove multiple consecutive hyphens and trim
    let cleaned = result
        .split('-')
        .filter(|s| !s.is_empty())
        .collect::<Vec<_>>()
        .join("-");

    cleaned
}
