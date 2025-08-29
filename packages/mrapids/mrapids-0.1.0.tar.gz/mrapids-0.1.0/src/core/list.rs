use crate::cli::{ListCommand, ListFormat, ListResource};
use crate::core::parser::parse_spec;
use crate::utils::security::validate_file_path;
use anyhow::Result;
use colored::*;
use serde_json::json;
use std::fs;
use std::path::Path;

pub fn list_command(cmd: ListCommand) -> Result<()> {
    match cmd.resource {
        ListResource::Operations => list_operations(&cmd)?,
        ListResource::Requests => list_requests(&cmd)?,
        ListResource::All => {
            list_operations(&cmd)?;
            println!();
            list_requests(&cmd)?;
        }
    }

    Ok(())
}

fn list_operations(cmd: &ListCommand) -> Result<()> {
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
            println!("  Usage: mrapids list operations <spec-file>");
            return Ok(());
        }

        spec_path.unwrap().to_path_buf()
    };

    let spec_file = &spec_file;

    // Validate spec file path
    validate_file_path(spec_file)?;

    // Load and parse the spec
    let content = fs::read_to_string(spec_file)?;
    let spec = parse_spec(&content)?;

    // Collect operations
    let mut operations = Vec::new();
    let mut index = 1;

    for operation in &spec.operations {
        // Apply filters
        if let Some(ref filter_method) = cmd.method {
            if operation.method.to_uppercase() != filter_method.to_uppercase() {
                continue;
            }
        }

        if let Some(ref filter_text) = cmd.filter {
            let search_text = filter_text.to_lowercase();
            let matches = operation.operation_id.to_lowercase().contains(&search_text)
                || operation.path.to_lowercase().contains(&search_text)
                || operation
                    .summary
                    .as_ref()
                    .map(|s| s.to_lowercase().contains(&search_text))
                    .unwrap_or(false);

            if !matches {
                continue;
            }
        }

        // Tag filtering not supported in simplified model
        if cmd.tag.is_some() {
            // Skip tag filtering for now
        }

        operations.push((
            index,
            operation.operation_id.clone(),
            operation.method.to_uppercase(),
            operation.path.clone(),
            operation.summary.clone().unwrap_or_default(),
            has_example(&Some(operation.operation_id.clone())),
        ));
        index += 1;
    }

    // Display results based on format
    match cmd.format {
        ListFormat::Table => display_operations_table(&operations, &spec),
        ListFormat::Simple => display_operations_simple(&operations),
        ListFormat::Json => display_operations_json(&operations),
        ListFormat::Yaml => display_operations_yaml(&operations),
    }

    Ok(())
}

fn list_requests(cmd: &ListCommand) -> Result<()> {
    let requests_dir = Path::new("requests");

    if !requests_dir.exists() {
        println!(
            "{} No saved requests found. Run 'mrapids analyze' to generate examples.",
            "📋".cyan()
        );
        return Ok(());
    }

    // Collect request files
    let mut requests = Vec::new();

    // Check main requests directory
    if let Ok(entries) = fs::read_dir(requests_dir) {
        for entry in entries.flatten() {
            if let Some(ext) = entry.path().extension() {
                if ext == "yaml" || ext == "yml" {
                    if let Ok(content) = fs::read_to_string(entry.path()) {
                        if let Ok(config) = serde_yaml::from_str::<serde_yaml::Value>(&content) {
                            let name = entry
                                .file_name()
                                .to_string_lossy()
                                .replace(".yaml", "")
                                .replace(".yml", "");
                            let method =
                                config.get("method").and_then(|v| v.as_str()).unwrap_or("?");
                            let path = config.get("path").and_then(|v| v.as_str()).unwrap_or("?");
                            let description = config
                                .get("description")
                                .and_then(|v| v.as_str())
                                .unwrap_or("");

                            // Apply filters
                            if let Some(ref filter_method) = cmd.method {
                                if method != filter_method.to_uppercase() {
                                    continue;
                                }
                            }

                            if let Some(ref filter_text) = cmd.filter {
                                let search_text = filter_text.to_lowercase();
                                if !name.to_lowercase().contains(&search_text)
                                    && !path.to_lowercase().contains(&search_text)
                                    && !description.to_lowercase().contains(&search_text)
                                {
                                    continue;
                                }
                            }

                            requests.push((
                                name,
                                method.to_string(),
                                path.to_string(),
                                description.to_string(),
                            ));
                        }
                    }
                }
            }
        }
    }

    // Check examples directory
    let examples_dir = requests_dir.join("examples");
    if examples_dir.exists() {
        if let Ok(entries) = fs::read_dir(examples_dir) {
            for entry in entries.flatten() {
                if let Some(ext) = entry.path().extension() {
                    if ext == "yaml" || ext == "yml" {
                        if let Ok(content) = fs::read_to_string(entry.path()) {
                            if let Ok(config) = serde_yaml::from_str::<serde_yaml::Value>(&content)
                            {
                                let name = format!(
                                    "examples/{}",
                                    entry
                                        .file_name()
                                        .to_string_lossy()
                                        .replace(".yaml", "")
                                        .replace(".yml", "")
                                );
                                let method =
                                    config.get("method").and_then(|v| v.as_str()).unwrap_or("?");
                                let path =
                                    config.get("path").and_then(|v| v.as_str()).unwrap_or("?");
                                let description = config
                                    .get("description")
                                    .and_then(|v| v.as_str())
                                    .unwrap_or("");

                                // Apply filters
                                if let Some(ref filter_method) = cmd.method {
                                    if method != filter_method.to_uppercase() {
                                        continue;
                                    }
                                }

                                if let Some(ref filter_text) = cmd.filter {
                                    let search_text = filter_text.to_lowercase();
                                    if !name.to_lowercase().contains(&search_text)
                                        && !path.to_lowercase().contains(&search_text)
                                        && !description.to_lowercase().contains(&search_text)
                                    {
                                        continue;
                                    }
                                }

                                requests.push((
                                    name,
                                    method.to_string(),
                                    path.to_string(),
                                    description.to_string(),
                                ));
                            }
                        }
                    }
                }
            }
        }
    }

    // Display results
    match cmd.format {
        ListFormat::Table => display_requests_table(&requests),
        ListFormat::Simple => display_requests_simple(&requests),
        ListFormat::Json => display_requests_json(&requests),
        ListFormat::Yaml => display_requests_yaml(&requests),
    }

    Ok(())
}

fn display_operations_table(
    operations: &[(usize, String, String, String, String, bool)],
    spec: &crate::core::parser::UnifiedSpec,
) {
    if operations.is_empty() {
        println!("{} No operations found matching criteria", "📋".cyan());
        return;
    }

    let title = format!(
        "{} - Available Operations ({} total)",
        spec.info.title,
        operations.len()
    );

    // Calculate column widths
    let max_op_len = operations
        .iter()
        .map(|(_, op, _, _, _, _)| op.len())
        .max()
        .unwrap_or(20)
        .min(30);
    let max_path_len = operations
        .iter()
        .map(|(_, _, _, path, _, _)| path.len())
        .max()
        .unwrap_or(20)
        .min(40);

    // Print table
    println!("┌{:─<72}┐", "");
    println!("│ {:^70} │", title.bright_yellow());
    println!(
        "├{:─<4}┬{:─<width_op$}┬{:─<8}┬{:─<width_path$}┬{:─<10}┤",
        "",
        "",
        "",
        "",
        "",
        width_op = max_op_len + 2,
        width_path = max_path_len + 2
    );
    println!(
        "│ {} │ {:^width_op$} │ {:^8} │ {:^width_path$} │ {:^10} │",
        "#".bright_cyan(),
        "Operation ID".bright_cyan(),
        "Method".bright_cyan(),
        "Path".bright_cyan(),
        "Example".bright_cyan(),
        width_op = max_op_len,
        width_path = max_path_len
    );
    println!(
        "├{:─<4}┼{:─<width_op$}┼{:─<8}┼{:─<width_path$}┼{:─<10}┤",
        "",
        "",
        "",
        "",
        "",
        width_op = max_op_len + 2,
        width_path = max_path_len + 2
    );

    for (idx, op_id, method, path, _desc, has_ex) in operations {
        let method_colored = match method.as_str() {
            "GET" => method.green(),
            "POST" => method.yellow(),
            "PUT" => method.blue(),
            "DELETE" => method.red(),
            "PATCH" => method.magenta(),
            _ => method.normal(),
        };

        let example_mark = if *has_ex { "✓".green() } else { "-".dimmed() };

        println!(
            "│ {:>2} │ {:<width_op$} │ {:^8} │ {:<width_path$} │ {:^10} │",
            idx,
            op_id,
            method_colored,
            path,
            example_mark,
            width_op = max_op_len,
            width_path = max_path_len
        );
    }

    println!(
        "└{:─<4}┴{:─<width_op$}┴{:─<8}┴{:─<width_path$}┴{:─<10}┘",
        "",
        "",
        "",
        "",
        "",
        width_op = max_op_len + 2,
        width_path = max_path_len + 2
    );

    println!("\n{} Usage:", "💡".bright_yellow());
    println!("  mrapids run <operation-id>         # Run by operation ID");
    println!("  mrapids run-op <number>            # Run by number from list");
    println!("  mrapids analyze --operation <id>   # Generate example for specific operation");
}

fn display_operations_simple(operations: &[(usize, String, String, String, String, bool)]) {
    for (idx, op_id, method, path, desc, _) in operations {
        println!(
            "{:>3}. {} {} {} {}",
            idx,
            method.bright_cyan(),
            path.yellow(),
            format!("[{}]", op_id).dimmed(),
            if !desc.is_empty() {
                format!("- {}", desc).dimmed()
            } else {
                "".normal()
            }
        );
    }
}

fn display_operations_json(operations: &[(usize, String, String, String, String, bool)]) {
    let json_ops: Vec<_> = operations
        .iter()
        .map(|(idx, op_id, method, path, desc, has_ex)| {
            json!({
                "index": idx,
                "operationId": op_id,
                "method": method,
                "path": path,
                "description": desc,
                "hasExample": has_ex
            })
        })
        .collect();

    println!("{}", serde_json::to_string_pretty(&json_ops).unwrap());
}

fn display_operations_yaml(operations: &[(usize, String, String, String, String, bool)]) {
    let yaml_ops: Vec<_> = operations
        .iter()
        .map(|(idx, op_id, method, path, desc, has_ex)| {
            json!({
                "index": idx,
                "operationId": op_id,
                "method": method,
                "path": path,
                "description": desc,
                "hasExample": has_ex
            })
        })
        .collect();

    println!("{}", serde_yaml::to_string(&yaml_ops).unwrap());
}

fn display_requests_table(requests: &[(String, String, String, String)]) {
    if requests.is_empty() {
        println!("{} No saved requests found", "📋".cyan());
        return;
    }

    println!("┌{:─<72}┐", "");
    println!(
        "│ {:^70} │",
        format!("Saved Requests ({} total)", requests.len()).bright_yellow()
    );
    println!("├{:─<25}┬{:─<8}┬{:─<35}┤", "", "", "");
    println!(
        "│ {:^23} │ {:^8} │ {:^33} │",
        "Name".bright_cyan(),
        "Method".bright_cyan(),
        "Path".bright_cyan()
    );
    println!("├{:─<25}┼{:─<8}┼{:─<35}┤", "", "", "");

    for (name, method, path, _desc) in requests {
        let method_colored = match method.as_str() {
            "GET" => method.green(),
            "POST" => method.yellow(),
            "PUT" => method.blue(),
            "DELETE" => method.red(),
            "PATCH" => method.magenta(),
            _ => method.normal(),
        };

        println!("│ {:<23} │ {:^8} │ {:<33} │", name, method_colored, path);
    }

    println!("└{:─<25}┴{:─<8}┴{:─<35}┘", "", "", "");

    println!("\n{} Usage:", "💡".bright_yellow());
    println!("  mrapids run <request-name>     # Run saved request");
    println!("  mrapids run <name> --data file # Use different data file");
}

fn display_requests_simple(requests: &[(String, String, String, String)]) {
    for (name, method, path, desc) in requests {
        println!(
            "{} {} {} {}",
            name.yellow(),
            method.bright_cyan(),
            path,
            if !desc.is_empty() {
                format!("- {}", desc).dimmed()
            } else {
                "".normal()
            }
        );
    }
}

fn display_requests_json(requests: &[(String, String, String, String)]) {
    let json_reqs: Vec<_> = requests
        .iter()
        .map(|(name, method, path, desc)| {
            json!({
                "name": name,
                "method": method,
                "path": path,
                "description": desc
            })
        })
        .collect();

    println!("{}", serde_json::to_string_pretty(&json_reqs).unwrap());
}

fn display_requests_yaml(requests: &[(String, String, String, String)]) {
    let yaml_reqs: Vec<_> = requests
        .iter()
        .map(|(name, method, path, desc)| {
            json!({
                "name": name,
                "method": method,
                "path": path,
                "description": desc
            })
        })
        .collect();

    println!("{}", serde_yaml::to_string(&yaml_reqs).unwrap());
}

fn has_example(op_id: &Option<String>) -> bool {
    if let Some(id) = op_id {
        let example_file =
            Path::new("requests/examples").join(format!("{}.yaml", to_kebab_case(id)));
        example_file.exists()
    } else {
        false
    }
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
