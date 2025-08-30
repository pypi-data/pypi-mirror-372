// Simplified run command implementation
// Supports: direct operations, request configs, templates, and complex files

use crate::cli::RunCommand;
use crate::core::config;
use crate::core::examples::generate_smart_example;
use anyhow::Result;
use colored::*;
use serde_json::{json, Value};
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

/// Execute the simplified run command
pub fn execute(cmd: RunCommand) -> Result<()> {
    // Determine what type of operation this is
    let operation_path = PathBuf::from(&cmd.operation);

    // Check if it's a file path (request config, template, or spec)
    if operation_path.exists() {
        execute_from_file(&operation_path, &cmd)
    } else if cmd.template.is_some() {
        // Using a template
        execute_from_template(&cmd)
    } else {
        // Direct operation name (e.g., GetCharges, CreateCustomer)
        execute_direct_operation(&cmd)
    }
}

/// Execute a direct operation by name
fn execute_direct_operation(cmd: &RunCommand) -> Result<()> {
    println!("⚡ Executing operation: {}", cmd.operation.bright_cyan());

    // Find the API spec in the project
    let spec_path = find_api_spec()?;
    println!(
        "📋 Using spec: {}",
        spec_path.display().to_string().dimmed()
    );

    // Load and parse the spec
    let spec_content = fs::read_to_string(&spec_path)?;
    let spec = crate::core::parser::parse_spec(&spec_content)?;

    // Use partial matching to find the operation
    let operation = crate::core::show::find_operation_with_spec(&spec, &cmd.operation)?;

    // Build the request
    let mut request = build_request_from_operation(operation, cmd, &spec.base_url)?;

    // Apply environment settings (pass spec path for relative config lookup)
    apply_environment(&mut request, &cmd.env, Some(&spec_path))?;

    // Execute the request
    execute_request(&request, cmd)
}

/// Execute from a file (request config, spec, etc.)
fn execute_from_file(path: &Path, cmd: &RunCommand) -> Result<()> {
    // Check if it's a request config
    if crate::core::request_runner::is_request_config(path) {
        println!(
            "📄 Loading request config from: {}",
            path.display().to_string().cyan()
        );
        let mut config = crate::core::request_runner::load_request_config(path)?;

        // Override with command line options
        if let Some(url) = &cmd.url {
            config.base_url = Some(url.clone());
        }

        // Handle data override
        let data = if let Some(file) = &cmd.file {
            Some(format!("@{}", file.display()))
        } else {
            cmd.data.clone()
        };

        return crate::core::request_runner::execute_request_config(
            config,
            cmd.url.clone(),
            data,
            &cmd.output,
        );
    }

    // Otherwise treat as API spec (backward compatibility)
    println!(
        "📄 Loading spec from: {}",
        path.display().to_string().cyan()
    );

    // This is the old behavior - we can keep it for backward compatibility
    // but encourage users to use the new direct operation approach
    Err(anyhow::anyhow!(
        "Direct spec execution is deprecated. Use:\n\
         mrapids run <operation-name> [options]\n\
         Example: mrapids run get-user --id 123"
    ))
}

/// Execute from a template
fn execute_from_template(cmd: &RunCommand) -> Result<()> {
    let template_name = cmd.template.as_ref().unwrap();
    println!("📋 Loading template: {}", template_name.bright_cyan());

    // Find template file
    let template_path = find_template(template_name)?;
    let template_content = fs::read_to_string(&template_path)?;

    // Parse template variables
    let mut vars = HashMap::new();
    for var in &cmd.template_vars {
        if let Some((key, value)) = var.split_once('=') {
            vars.insert(key.to_string(), value.to_string());
        }
    }

    // Apply common parameters as variables too
    if let Some(id) = &cmd.id {
        vars.insert("ID".to_string(), id.clone());
    }
    if let Some(name) = &cmd.name {
        vars.insert("NAME".to_string(), name.clone());
    }

    // Substitute variables in template
    let processed = substitute_variables(&template_content, &vars)?;

    // Parse and execute the processed template
    let config: crate::core::request_runner::RequestConfig = serde_yaml::from_str(&processed)?;

    crate::core::request_runner::execute_request_config(
        config,
        cmd.url.clone(),
        cmd.data.clone(),
        &cmd.output,
    )
}

/// Build a request from an operation and command options
fn build_request_from_operation(
    operation: &crate::core::parser::UnifiedOperation,
    cmd: &RunCommand,
    base_url: &str,
) -> Result<Request> {
    if cmd.verbose {
        println!(
            "\n  Building request for operation: {}",
            operation.operation_id
        );
        println!("  Operation path: {}", operation.path);
        println!("  Command params: {:?}", cmd.params);
    }

    let mut request = Request {
        method: operation.method.clone(),
        path: operation.path.clone(),
        base_url: base_url.to_string(),
        headers: HashMap::new(),
        query_params: HashMap::new(),
        path_params: HashMap::new(),
        body: None,
    };

    // Add common parameters
    if let Some(id) = &cmd.id {
        // Smart detection: map to appropriate path parameter
        // Look for any parameter containing "id" or "Id"
        if operation.path.contains("{id}") {
            request.path_params.insert("id".to_string(), json!(id));
        } else if operation.path.contains("{petId}") {
            request.path_params.insert("petId".to_string(), json!(id));
        } else if operation.path.contains("{userId}") {
            request.path_params.insert("userId".to_string(), json!(id));
        } else if operation.path.contains("{productId}") {
            request
                .path_params
                .insert("productId".to_string(), json!(id));
        } else if operation.path.contains("{orderId}") {
            request.path_params.insert("orderId".to_string(), json!(id));
        } else if operation.path.contains("{customerId}") {
            request
                .path_params
                .insert("customerId".to_string(), json!(id));
        } else {
            // Check for any path param ending with "id" or "Id"
            let id_pattern = regex::Regex::new(r"\{(\w*[iI]d)\}").unwrap();
            if let Some(captures) = id_pattern.captures(&operation.path) {
                if let Some(param_name) = captures.get(1) {
                    request
                        .path_params
                        .insert(param_name.as_str().to_string(), json!(id));
                }
            } else {
                // Fallback to query parameter
                request.query_params.insert("id".to_string(), id.clone());
            }
        }
    }

    // Add other common parameters
    if let Some(name) = &cmd.name {
        request
            .query_params
            .insert("name".to_string(), name.clone());
    }
    if let Some(status) = &cmd.status {
        request
            .query_params
            .insert("status".to_string(), status.clone());
    }
    if let Some(limit) = &cmd.limit {
        request
            .query_params
            .insert("limit".to_string(), limit.to_string());
    }
    if let Some(offset) = &cmd.offset {
        request
            .query_params
            .insert("offset".to_string(), offset.to_string());
    }
    if let Some(sort) = &cmd.sort {
        request
            .query_params
            .insert("sort".to_string(), sort.clone());
    }

    // Add generic parameters - smart detection of path vs query params
    if cmd.verbose {
        println!("  Processing {} generic parameters", cmd.params.len());
    }
    for param in &cmd.params {
        if let Some((key, value)) = param.split_once('=') {
            // Check if this parameter is in the path
            let path_param_pattern = format!("{{{}}}", key);
            if cmd.verbose {
                println!(
                    "  Checking if '{}' is in path '{}' (pattern: '{}')",
                    key, operation.path, path_param_pattern
                );
            }
            if operation.path.contains(&path_param_pattern) {
                // It's a path parameter
                request.path_params.insert(key.to_string(), json!(value));
                if cmd.verbose {
                    println!("  Adding path parameter: {} = {}", key, value);
                }
            } else {
                // Check if it's defined as a path parameter in the operation
                let is_path_param = operation.parameters.iter().any(|p| {
                    p.name == key && p.location == crate::core::parser::ParameterLocation::Path
                });

                if is_path_param {
                    request.path_params.insert(key.to_string(), json!(value));
                    if cmd.verbose {
                        println!("  Adding path parameter (from spec): {} = {}", key, value);
                    }
                } else {
                    // Default to query parameter - smart decode if URL-encoded
                    let decoded_value = smart_decode_param(value);
                    request
                        .query_params
                        .insert(key.to_string(), decoded_value.clone());
                    if cmd.verbose {
                        println!("  Adding query parameter: {} = {}", key, decoded_value);
                        if decoded_value != value {
                            println!("    (decoded from: {})", value);
                        }
                    }
                }
            }
        }
    }

    // Add query parameters
    for param in &cmd.query_params {
        if let Some((key, value)) = param.split_once('=') {
            let decoded_value = smart_decode_param(value);
            request.query_params.insert(key.to_string(), decoded_value);
        }
    }

    // Add headers
    request
        .headers
        .insert("Accept".to_string(), "application/json".to_string());
    request
        .headers
        .insert("User-Agent".to_string(), "MicroRapid/0.1.0".to_string());

    for header in &cmd.headers {
        if let Some((key, value)) = header.split_once(':') {
            request
                .headers
                .insert(key.trim().to_string(), value.trim().to_string());
        }
    }

    // Add auth headers
    if let Some(auth) = &cmd.auth {
        request
            .headers
            .insert("Authorization".to_string(), auth.clone());
    } else if let Some(api_key) = &cmd.api_key {
        request
            .headers
            .insert("X-API-Key".to_string(), api_key.clone());
    } else if let Some(profile) = &cmd.auth_profile {
        // Use OAuth profile
        apply_oauth_profile_auth(&mut request, profile)?;
    }

    // Handle body data
    if needs_body(&operation.method) {
        request.body = if let Some(file) = &cmd.file {
            // Load from file
            let content = fs::read_to_string(file)?;
            Some(content)
        } else if let Some(data) = &cmd.data {
            // Use provided data
            if data.starts_with('@') {
                // Load from file
                let file_path = &data[1..];
                let content = fs::read_to_string(file_path)?;
                Some(content)
            } else {
                Some(data.clone())
            }
        } else if cmd.stdin {
            // Read from stdin
            use std::io::Read;
            let mut buffer = String::new();
            std::io::stdin().read_to_string(&mut buffer)?;
            Some(buffer)
        } else if cmd.required_only {
            // Generate minimal payload with only required fields
            generate_required_only_body(operation)?
        } else {
            // Try to load default example
            load_default_example(&operation.operation_id).ok()
        };

        if request.body.is_some() {
            request
                .headers
                .insert("Content-Type".to_string(), "application/json".to_string());
        }
    }

    Ok(request)
}

/// Internal request structure
struct Request {
    method: String,
    path: String,
    base_url: String,
    headers: HashMap<String, String>,
    query_params: HashMap<String, String>,
    path_params: HashMap<String, Value>,
    body: Option<String>,
}

/// Execute the built request
fn execute_request(request: &Request, cmd: &RunCommand) -> Result<()> {
    // Validate URL for security and enforce HTTPS
    use crate::utils::request_warnings::RequestAnalyzer;
    use crate::utils::security::enforce_https;
    let full_url = format!("{}{}", request.base_url, request.path);
    enforce_https(&full_url, cmd.allow_insecure)?;

    // Analyze request for security warnings
    let mut analyzer = RequestAnalyzer::new(cmd.no_warnings);

    // Analyze headers
    let headers_vec: Vec<(String, String)> = request
        .headers
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    analyzer.analyze_headers(&headers_vec);

    // Analyze query parameters
    let query_params_vec: Vec<(String, String)> = request
        .query_params
        .iter()
        .map(|(k, v)| (k.clone(), v.clone()))
        .collect();
    analyzer.analyze_url_params(&query_params_vec);

    // Analyze path parameters
    let path_params_vec: Vec<(String, String)> = request
        .path_params
        .iter()
        .filter_map(|(k, v)| {
            if let Value::String(s) = v {
                Some((k.clone(), s.clone()))
            } else {
                Some((k.clone(), v.to_string()))
            }
        })
        .collect();
    analyzer.analyze_url_params(&path_params_vec);

    // Analyze body if present
    if let Some(body) = &request.body {
        analyzer.analyze_json_body(body);
    }

    // Display warnings
    analyzer.display_warnings();

    // Show verbose info if requested
    if cmd.verbose {
        println!("\n{} Request Details:", "📋".bright_blue());
        println!("  Method: {}", request.method.bright_green());
        println!("  Path: {}", request.path.bright_cyan());
        println!("  Base URL: {}", request.base_url.dimmed());
        if !request.headers.is_empty() {
            println!("  Headers:");
            for (key, value) in &request.headers {
                // Mask sensitive header values
                let display_value = match key.to_lowercase().as_str() {
                    "authorization" => {
                        if value.starts_with("Bearer ") {
                            format!("Bearer {}...", &value[7..14.min(value.len())]).bright_black()
                        } else if value.starts_with("Basic ") {
                            "Basic [MASKED]".bright_black()
                        } else {
                            "[MASKED]".bright_black()
                        }
                    }
                    "x-api-key" | "api-key" | "apikey" => {
                        format!("{}...", &value[..7.min(value.len())]).bright_black()
                    }
                    _ => value.normal(),
                };
                println!("    {}: {}", key.yellow(), display_value);
            }
        }
        if !request.query_params.is_empty() {
            println!("  Query Parameters:");
            for (key, value) in &request.query_params {
                println!("    {}: {}", key.yellow(), value);
            }
        }
        if let Some(body) = &request.body {
            println!("  Body: {}", body.dimmed());
        }
        println!(); // Add spacing
    }

    // Show as curl if requested
    if cmd.as_curl {
        print_as_curl(request)?;
        if cmd.dry_run {
            return Ok(());
        }
    }

    // Dry run - don't actually send
    if cmd.dry_run {
        println!("\n{} Dry run complete (request not sent)", "✅".green());
        return Ok(());
    }

    // Build URL with path params substituted
    let mut url_path = request.path.clone();
    for (param_name, param_value) in &request.path_params {
        let placeholder = format!("{{{}}}", param_name);
        let value_str = match param_value {
            Value::String(s) => s.clone(),
            Value::Number(n) => n.to_string(),
            _ => param_value.to_string(),
        };
        url_path = url_path.replace(&placeholder, &value_str);
    }

    let full_url = format!("{}{}", request.base_url.trim_end_matches('/'), url_path);

    println!("🌐 Request URL: {}", full_url.bright_blue());
    println!("🚀 Sending request...");

    // Execute with retries if specified
    let mut attempts = 0;
    let max_attempts = cmd.retry + 1;

    loop {
        attempts += 1;

        // Create HTTP client and request
        let client = reqwest::blocking::Client::builder()
            .timeout(std::time::Duration::from_secs(cmd.timeout as u64))
            .build()?;

        let mut http_request = match request.method.to_uppercase().as_str() {
            "GET" => client.get(&full_url),
            "POST" => client.post(&full_url),
            "PUT" => client.put(&full_url),
            "DELETE" => client.delete(&full_url),
            "PATCH" => client.patch(&full_url),
            _ => return Err(anyhow::anyhow!("Unsupported method: {}", request.method)),
        };

        // Add headers
        for (key, value) in &request.headers {
            http_request = http_request.header(key, value);
        }

        // Add query params
        if !request.query_params.is_empty() {
            http_request = http_request.query(&request.query_params);
        }

        // Add body
        if let Some(body) = &request.body {
            http_request = http_request.body(body.clone());
        }

        // Send request
        match http_request.send() {
            Ok(response) => {
                // Display response
                display_response(response, &cmd.output, cmd.save.as_deref())?;
                break;
            }
            Err(e) => {
                if attempts < max_attempts {
                    println!(
                        "⚠️  Request failed: {}. Retrying ({}/{})...",
                        e, attempts, max_attempts
                    );
                    std::thread::sleep(std::time::Duration::from_secs(2));
                } else {
                    return Err(anyhow::anyhow!(
                        "Request failed after {} attempts: {}",
                        max_attempts,
                        e
                    ));
                }
            }
        }
    }

    Ok(())
}

/// Display the response
fn display_response(
    response: reqwest::blocking::Response,
    format: &str,
    save_path: Option<&Path>,
) -> Result<()> {
    let status = response.status();
    let headers = response.headers().clone();

    // Show status
    if status.is_success() {
        println!(
            "✅ Status: {} {}",
            status.as_u16().to_string().green(),
            status.canonical_reason().unwrap_or("")
        );
    } else {
        println!(
            "❌ Status: {} {}",
            status.as_u16().to_string().red(),
            status.canonical_reason().unwrap_or("")
        );
    }

    // Get response body
    let body = response.text()?;

    // Save to file if requested
    if let Some(path) = save_path {
        fs::write(path, &body)?;
        println!(
            "💾 Response saved to: {}",
            path.display().to_string().green()
        );
    }

    // Display based on format
    let content_type = headers
        .get("content-type")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("text/plain");

    if content_type.contains("json") {
        if let Ok(json) = serde_json::from_str::<Value>(&body) {
            match format {
                "json" => println!("{}", serde_json::to_string_pretty(&json)?),
                "yaml" => println!("{}", serde_yaml::to_string(&json)?),
                "table" => print_as_table(&json),
                _ => crate::core::request_runner::print_json_pretty(&json, 0),
            }
        } else {
            println!("{}", body);
        }
    } else {
        println!("{}", body);
    }

    Ok(())
}

// Helper functions

fn find_api_spec() -> Result<PathBuf> {
    // Look for spec files in common locations
    let spec_locations = [
        "specs/api.yaml",
        "specs/api.json",
        "specs/openapi.yaml",
        "specs/openapi.json",
        "specs/swagger.yaml",
        "specs/swagger.json",
        "api.yaml",
        "api.json",
        "openapi.yaml",
        "openapi.json",
    ];

    for location in &spec_locations {
        let path = PathBuf::from(location);
        if path.exists() {
            // Convert to absolute path
            return Ok(path.canonicalize()?);
        }
    }

    // Look for any spec file in specs directory
    if let Ok(entries) = fs::read_dir("specs") {
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            if let Some(ext) = path.extension() {
                if ext == "yaml" || ext == "yml" || ext == "json" {
                    // Convert to absolute path
                    return Ok(path.canonicalize()?);
                }
            }
        }
    }

    Err(anyhow::anyhow!(
        "No API specification found. Please run 'mrapids init' or place your spec in specs/api.yaml"
    ))
}

fn find_template(name: &str) -> Result<PathBuf> {
    let template_paths = [
        format!("templates/{}.yaml", name),
        format!("templates/{}.yml", name),
        format!("templates/{}.json", name),
        format!(".mrapids/templates/{}.yaml", name),
        format!("{}.yaml", name),
        format!("{}.yml", name),
    ];

    for path in &template_paths {
        let path = PathBuf::from(path);
        if path.exists() {
            return Ok(path);
        }
    }

    Err(anyhow::anyhow!("Template '{}' not found", name))
}

fn load_default_example(operation_id: &str) -> Result<String> {
    let example_paths = [
        format!("data/examples/{}.json", operation_id),
        format!("data/examples/{}.json", operation_id.replace('_', "-")),
        format!("examples/{}.json", operation_id),
    ];

    for path in &example_paths {
        if let Ok(content) = fs::read_to_string(path) {
            // Strip comments
            let cleaned: String = content
                .lines()
                .filter(|line| !line.trim().starts_with("//"))
                .collect::<Vec<_>>()
                .join("\n");
            return Ok(cleaned);
        }
    }

    Err(anyhow::anyhow!(
        "No example data found for operation '{}'",
        operation_id
    ))
}

fn needs_body(method: &str) -> bool {
    matches!(method.to_uppercase().as_str(), "POST" | "PUT" | "PATCH")
}

fn apply_environment(request: &mut Request, env: &str, spec_path: Option<&Path>) -> Result<()> {
    // Try to load environment config - check relative to spec first
    let config = if let Some(spec) = spec_path {
        // Try to find config relative to the spec file
        let spec_dir = spec.parent().unwrap_or(Path::new("."));
        let config_path = spec_dir.join("config").join(format!("{}.yaml", env));

        if config_path.exists() {
            match config::load_config(env, Some(&config_path)) {
                Ok(cfg) => cfg,
                Err(e) => {
                    if std::env::var("MRAPIDS_DEBUG").is_ok() {
                        eprintln!("Debug: Failed to load project config: {}", e);
                    }
                    // Fall back to default search
                    match config::load_config(env, None) {
                        Ok(cfg) => cfg,
                        Err(e) => {
                            if std::env::var("MRAPIDS_DEBUG").is_ok() {
                                eprintln!("Debug: Failed to load any config: {}", e);
                            }
                            return Ok(());
                        }
                    }
                }
            }
        } else {
            // Use default search
            match config::load_config(env, None) {
                Ok(cfg) => cfg,
                Err(e) => {
                    if std::env::var("MRAPIDS_DEBUG").is_ok() {
                        eprintln!("Debug: Failed to load config: {}", e);
                    }
                    return Ok(());
                }
            }
        }
    } else {
        // No spec path, use default search
        match config::load_config(env, None) {
            Ok(cfg) => cfg,
            Err(e) => {
                if std::env::var("MRAPIDS_DEBUG").is_ok() {
                    eprintln!("Debug: Failed to load config: {}", e);
                }
                return Ok(());
            }
        }
    };

    // Debug: Show what's in the config
    if std::env::var("MRAPIDS_DEBUG").is_ok() {
        eprintln!("Debug: Config loaded for env '{}'", env);
        eprintln!("Debug: Has global headers: {}", config.headers.is_some());
        eprintln!("Debug: Has global auth: {}", config.auth.is_some());
    }

    // Apply global headers first
    if let Some(headers) = &config.headers {
        for (key, value) in headers {
            request.headers.insert(key.clone(), value.clone());
        }
    }

    // Apply global auth
    if let Some(auth) = &config.auth {
        if std::env::var("MRAPIDS_DEBUG").is_ok() {
            eprintln!("Debug: Applying global auth: {:?}", auth);
        }
        apply_auth_to_request(request, auth);
    }

    // Extract the API name from the base URL
    let api_name = extract_api_name(&request.base_url);

    // Apply API-specific overrides if they exist
    if let Some(api) = api_name {
        if let Some(api_config) = config.apis.get(&api) {
            // Apply API-specific base URL if different
            if !api_config.base_url.is_empty() {
                // Check for version duplication
                let config_has_version =
                    api_config.base_url.ends_with("/v1") || api_config.base_url.ends_with("/v2");
                let path_has_version =
                    request.path.starts_with("/v1") || request.path.starts_with("/v2");

                if !(config_has_version && path_has_version) {
                    request.base_url = api_config.base_url.clone();
                }
            }

            // Apply API-specific auth (overrides global)
            if let Some(auth) = &api_config.auth {
                apply_auth_to_request(request, auth);
            }

            // Apply API-specific headers (overrides global)
            for (key, value) in &api_config.headers {
                request.headers.insert(key.clone(), value.clone());
            }

            // Apply content type if specified
            if let Some(content_type) = &api_config.content_type {
                request
                    .headers
                    .insert("Content-Type".to_string(), content_type.clone());
            }
        }
    }

    // Apply defaults
    if let Some(defaults) = &config.defaults {
        if let Some(timeout) = defaults.timeout {
            // Store timeout in request for later use
            request
                .headers
                .insert("X-MRapids-Timeout".to_string(), timeout.to_string());
        }
    }

    Ok(())
}

fn extract_api_name(base_url: &str) -> Option<String> {
    if base_url.contains("stripe.com") {
        Some("stripe".to_string())
    } else if base_url.contains("github.com") {
        Some("github".to_string())
    } else if base_url.contains("openai.com") {
        Some("openai".to_string())
    } else if base_url.contains("anthropic.com") {
        Some("anthropic".to_string())
    } else {
        // Try to extract from domain
        let clean_url = base_url.replace("https://", "").replace("http://", "");

        let domain = clean_url.split('/').next()?;

        // Extract the main part of domain (e.g., "example" from "api.example.com")
        let parts: Vec<&str> = domain.split('.').collect();
        if parts.len() >= 2 {
            Some(parts[parts.len() - 2].to_string())
        } else {
            None
        }
    }
}

fn apply_auth_to_request(request: &mut Request, auth: &config::AuthConfig) {
    match auth {
        config::AuthConfig::Bearer { token } => {
            request
                .headers
                .insert("Authorization".to_string(), format!("Bearer {}", token));
        }
        config::AuthConfig::Basic { username, password } => {
            use base64::Engine;
            let credentials = base64::engine::general_purpose::STANDARD
                .encode(format!("{}:{}", username, password));
            request.headers.insert(
                "Authorization".to_string(),
                format!("Basic {}", credentials),
            );
        }
        config::AuthConfig::ApiKey { header, key } => {
            request.headers.insert(header.clone(), key.clone());
        }
        config::AuthConfig::OAuth2 { .. } => {
            // OAuth2 would need token exchange logic
        }
    }
}

fn apply_oauth_profile_auth(request: &mut Request, profile: &str) -> Result<()> {
    use crate::core::auth;

    // Load tokens for the profile
    let mut tokens = auth::load_tokens(profile)?;

    // Check if token is expired and refresh if needed
    if tokens.is_expired() {
        println!("🔄 Token expired, refreshing...");
        // Note: This is a simplified approach. In a real implementation,
        // we'd need to make this async and properly handle the refresh
        let rt = tokio::runtime::Runtime::new()?;
        tokens = rt.block_on(auth::refresh_tokens(profile))?;
    }

    // Apply the authorization header
    request
        .headers
        .insert("Authorization".to_string(), tokens.auth_header());

    Ok(())
}

fn substitute_variables(template: &str, vars: &HashMap<String, String>) -> Result<String> {
    let mut result = template.to_string();

    for (key, value) in vars {
        let pattern = format!("${{{}}}", key);
        result = result.replace(&pattern, value);

        // Also handle with default values ${KEY:default}
        let pattern_with_default = format!("${{{}:", key);
        if result.contains(&pattern_with_default) {
            // This is simplified - full implementation would parse defaults properly
            let re = regex::Regex::new(&format!(r"\$\{{{}\:([^}}]+)\}}", regex::escape(key)))?;
            result = re.replace_all(&result, value).to_string();
        }
    }

    Ok(result)
}

fn print_as_curl(request: &Request) -> Result<()> {
    let mut curl_cmd = format!("curl -X {}", request.method);

    // Add headers
    for (key, value) in &request.headers {
        curl_cmd.push_str(&format!(" -H '{}: {}'", key, value));
    }

    // Add data
    if let Some(body) = &request.body {
        curl_cmd.push_str(&format!(" -d '{}'", body));
    }

    // Build URL with path params substituted
    let mut url_path = request.path.clone();
    for (param_name, param_value) in &request.path_params {
        let placeholder = format!("{{{}}}", param_name);
        let value_str = match param_value {
            Value::String(s) => s.clone(),
            Value::Number(n) => n.to_string(),
            _ => param_value.to_string(),
        };
        url_path = url_path.replace(&placeholder, &value_str);
    }

    let mut url = format!("{}{}", request.base_url.trim_end_matches('/'), url_path);
    if !request.query_params.is_empty() {
        let query: Vec<String> = request
            .query_params
            .iter()
            .map(|(k, v)| format!("{}={}", k, v))
            .collect();
        url.push_str(&format!("?{}", query.join("&")));
    }

    curl_cmd.push_str(&format!(" '{}'", url));

    println!("\n{} Equivalent curl command:", "🐚".bright_blue());
    println!("{}", curl_cmd.bright_cyan());

    Ok(())
}

fn print_as_table(json: &Value) {
    // Simple table output for arrays
    if let Some(array) = json.as_array() {
        if !array.is_empty() {
            // Get headers from first object
            if let Some(first) = array.first().and_then(|v| v.as_object()) {
                let headers: Vec<&str> = first.keys().map(|s| s.as_str()).collect();

                // Print headers
                println!("{}", headers.join("\t").bright_blue());

                // Print rows
                for item in array {
                    if let Some(obj) = item.as_object() {
                        let values: Vec<String> = headers
                            .iter()
                            .map(|h| obj.get(*h).map(|v| format!("{}", v)).unwrap_or_default())
                            .collect();
                        println!("{}", values.join("\t"));
                    }
                }
            }
        }
    } else {
        // For non-arrays, just print as JSON
        println!("{}", serde_json::to_string_pretty(json).unwrap());
    }
}

/// Generate minimal body with only required fields
fn generate_required_only_body(
    operation: &crate::core::parser::UnifiedOperation,
) -> Result<Option<String>> {
    if let Some(request_body) = &operation.request_body {
        if let Some((_, media_type)) = request_body.content.iter().next() {
            let schema = &media_type.schema;

            // Generate minimal object with only required fields
            if let crate::core::parser::SchemaType::Object = schema.schema_type {
                let mut obj = serde_json::Map::new();

                if let Some(properties) = &schema.properties {
                    if let Some(required) = &schema.required {
                        // Only include required fields
                        for field_name in required {
                            if let Some(field_schema) = properties.get(field_name) {
                                let value = generate_smart_example(field_name, field_schema);
                                obj.insert(field_name.clone(), value);
                            }
                        }
                    }

                    // If no required fields, include a helpful message
                    if obj.is_empty() {
                        obj.insert(
                            "_note".to_string(),
                            json!("No required fields - add your data here"),
                        );
                    }
                }

                let json_value = json!(obj);
                println!("📝 Generated minimal payload with required fields only:");
                println!(
                    "{}",
                    serde_json::to_string_pretty(&json_value)?.bright_black()
                );

                return Ok(Some(serde_json::to_string(&json_value)?));
            }
        }
    }

    Ok(None)
}

/// Intelligently decode URL-encoded parameters if they appear to be encoded
fn smart_decode_param(value: &str) -> String {
    // Check if the value contains % and looks like it might be URL-encoded
    if value.contains('%') && looks_like_url_encoded(value) {
        // Try to decode it
        match urlencoding::decode(value) {
            Ok(decoded) => {
                // Successfully decoded - return the decoded value
                decoded.to_string()
            }
            Err(_) => {
                // Decode failed - return original value
                value.to_string()
            }
        }
    } else {
        // Doesn't look URL-encoded - return as-is
        value.to_string()
    }
}

/// Check if a string looks like it contains URL encoding
fn looks_like_url_encoded(s: &str) -> bool {
    // Look for %XX patterns where X is a hex digit
    let encoded_pattern = regex::Regex::new(r"%[0-9A-Fa-f]{2}").unwrap();
    encoded_pattern.is_match(s)
}
