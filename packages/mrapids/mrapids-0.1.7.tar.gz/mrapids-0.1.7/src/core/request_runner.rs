// Request configuration runner
use anyhow::{Context, Result};
use colored::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize, Serialize)]
pub struct RequestConfig {
    pub operation: String,
    pub method: String,
    pub path: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,
    #[serde(default)]
    pub headers: HashMap<String, String>,
    #[serde(default)]
    pub params: HashMap<String, String>,
    #[serde(default)]
    pub path_params: HashMap<String, Value>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expect: Option<ExpectConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub base_url: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
pub struct ExpectConfig {
    pub status: u16,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content_type: Option<String>,
}

/// Check if a file is a request config (not an API spec)
pub fn is_request_config(path: &Path) -> bool {
    if let Ok(content) = fs::read_to_string(path) {
        // Quick check - request configs have specific fields
        content.contains("operation:")
            && content.contains("method:")
            && content.contains("path:")
            && !content.contains("openapi:")
            && !content.contains("swagger:")
            && !content.contains("paths:")
    } else {
        false
    }
}

/// Load request configuration from YAML file
pub fn load_request_config(path: &Path) -> Result<RequestConfig> {
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read request config: {}", path.display()))?;

    let config: RequestConfig = serde_yaml::from_str(&content)
        .with_context(|| format!("Failed to parse request config: {}", path.display()))?;

    Ok(config)
}

/// Execute a request from configuration
pub fn execute_request_config(
    config: RequestConfig,
    override_url: Option<String>,
    override_data: Option<String>,
    output_format: &str,
) -> Result<()> {
    println!(
        "⚡ Executing request: {} {}",
        config.method.bright_green(),
        config.path.bright_cyan()
    );

    if let Some(desc) = &config.description {
        println!("   {}", desc.dimmed());
    }

    // Determine base URL
    let base_url = override_url
        .or(config.base_url)
        .or_else(|| {
            // Try to find base URL from environment or default
            std::env::var("API_BASE_URL").ok()
        })
        .unwrap_or_else(|| {
            // Check if we're in a petstore project
            if config.path.contains("/pet")
                || config.path.contains("/store")
                || config.path.contains("/user")
            {
                "https://petstore.swagger.io/v2".to_string()
            } else {
                "http://localhost:8080".to_string()
            }
        });

    // Validate URL for security
    validate_request_url(&base_url)?;

    // Build full URL with path parameter substitution
    let mut url_path = config.path.clone();
    for (param_name, param_value) in &config.path_params {
        let placeholder = format!("{{{}}}", param_name);
        let value_str = match param_value {
            Value::String(s) => s.clone(),
            Value::Number(n) => n.to_string(),
            Value::Bool(b) => b.to_string(),
            _ => param_value.to_string(),
        };
        url_path = url_path.replace(&placeholder, &value_str);
    }

    let full_url = format!("{}{}", base_url.trim_end_matches('/'), url_path);
    println!("🌐 Request URL: {}", full_url.bright_blue());

    // Prepare request
    let client = reqwest::blocking::Client::new();
    let mut request = match config.method.to_uppercase().as_str() {
        "GET" => client.get(&full_url),
        "POST" => client.post(&full_url),
        "PUT" => client.put(&full_url),
        "DELETE" => client.delete(&full_url),
        "PATCH" => client.patch(&full_url),
        "HEAD" => client.head(&full_url),
        _ => {
            return Err(anyhow::anyhow!(
                "Unsupported HTTP method: {}",
                config.method
            ))
        }
    };

    // Add headers
    for (key, value) in &config.headers {
        request = request.header(key, value);
    }

    // Add query parameters
    if !config.params.is_empty() {
        request = request.query(&config.params);
    }

    // Add body if present
    if let Some(body_ref) = &config.body {
        let body_content = if let Some(override_body) = override_data {
            // Check if override starts with @ to indicate file
            if override_body.starts_with('@') {
                let file_path = &override_body[1..];
                let path = if file_path.starts_with('/') {
                    PathBuf::from(file_path)
                } else {
                    std::env::current_dir()?.join(file_path)
                };

                let content = fs::read_to_string(&path)
                    .with_context(|| format!("Failed to read data file: {}", path.display()))?;

                // Strip comment lines if JSON file
                if file_path.ends_with(".json") {
                    content
                        .lines()
                        .filter(|line| !line.trim().starts_with("//"))
                        .collect::<Vec<_>>()
                        .join("\n")
                } else {
                    content
                }
            } else {
                override_body
            }
        } else if body_ref.starts_with("data/") || body_ref.ends_with(".json") {
            // Load from file
            let body_path = if body_ref.starts_with('/') {
                PathBuf::from(body_ref)
            } else {
                std::env::current_dir()?.join(body_ref)
            };

            {
                let content = fs::read_to_string(&body_path).with_context(|| {
                    format!("Failed to read body file: {}", body_path.display())
                })?;
                // Strip comment lines (lines starting with //)
                let cleaned: String = content
                    .lines()
                    .filter(|line| !line.trim().starts_with("//"))
                    .collect::<Vec<_>>()
                    .join("\n");
                cleaned
            }
        } else {
            // Use as inline JSON
            body_ref.clone()
        };

        request = request.body(body_content);
    }

    // Execute request
    println!("🚀 Sending request...");
    let response = request
        .send()
        .with_context(|| format!("Failed to send request to {}", full_url))?;

    let status = response.status();
    let status_code = status.as_u16();

    // Check expectations if present
    if let Some(expect) = &config.expect {
        if status_code != expect.status {
            println!(
                "⚠️  Status mismatch: expected {}, got {}",
                expect.status.to_string().yellow(),
                status_code.to_string().red()
            );
        } else {
            println!(
                "✅ Status: {} {}",
                status_code.to_string().green(),
                status.canonical_reason().unwrap_or("")
            );
        }
    } else {
        let status_color = if status.is_success() {
            status_code.to_string().green()
        } else if status.is_client_error() {
            status_code.to_string().yellow()
        } else {
            status_code.to_string().red()
        };
        println!(
            "📡 Status: {} {}",
            status_color,
            status.canonical_reason().unwrap_or("")
        );
    }

    // Display response
    display_response(response, output_format)?;

    Ok(())
}

/// Display response in requested format
fn display_response(response: reqwest::blocking::Response, format: &str) -> Result<()> {
    let headers = response.headers().clone();
    let content_type = headers
        .get("content-type")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("text/plain");

    println!("📥 Response (Content-Type: {}):", content_type.dimmed());

    let body = response.text()?;

    match format {
        "json" => {
            if content_type.contains("json") {
                if let Ok(json) = serde_json::from_str::<Value>(&body) {
                    println!("{}", serde_json::to_string_pretty(&json)?);
                } else {
                    println!("{}", body);
                }
            } else {
                println!("{}", body);
            }
        }
        "yaml" => {
            if content_type.contains("json") {
                if let Ok(json) = serde_json::from_str::<Value>(&body) {
                    println!("{}", serde_yaml::to_string(&json)?);
                } else {
                    println!("{}", body);
                }
            } else {
                println!("{}", body);
            }
        }
        "pretty" | _ => {
            if content_type.contains("json") {
                if let Ok(json) = serde_json::from_str::<Value>(&body) {
                    print_json_pretty(&json, 0);
                } else {
                    println!("{}", body);
                }
            } else {
                println!("{}", body);
            }
        }
    }

    Ok(())
}

/// Pretty print JSON with colors
pub fn print_json_pretty(value: &Value, indent: usize) {
    let indent_str = "  ".repeat(indent);

    match value {
        Value::Object(map) => {
            println!("{{");
            let entries: Vec<_> = map.iter().collect();
            for (i, (key, val)) in entries.iter().enumerate() {
                print!("{}  {}: ", indent_str, key.bright_blue());
                match val {
                    Value::Object(_) | Value::Array(_) => {
                        print_json_pretty(val, indent + 1);
                    }
                    _ => {
                        print_json_value(val);
                        if i < entries.len() - 1 {
                            println!(",");
                        } else {
                            println!();
                        }
                    }
                }
            }
            print!("{}}}", indent_str);
            if indent > 0 {
                println!(",");
            } else {
                println!();
            }
        }
        Value::Array(arr) => {
            println!("[");
            for (i, val) in arr.iter().enumerate() {
                print!("{}  ", indent_str);
                print_json_pretty(val, indent + 1);
                if i < arr.len() - 1 {
                    println!(",");
                }
            }
            print!("{}]", indent_str);
        }
        _ => print_json_value(value),
    }
}

/// Print a JSON value with color
fn print_json_value(value: &Value) {
    match value {
        Value::String(s) => print!("{}", format!("\"{}\"", s).green()),
        Value::Number(n) => print!("{}", n.to_string().yellow()),
        Value::Bool(b) => print!("{}", b.to_string().cyan()),
        Value::Null => print!("{}", "null".dimmed()),
        _ => print!("{}", value),
    }
}

/// Validate request URL for security
fn validate_request_url(base_url: &str) -> Result<()> {
    let url_lower = base_url.to_lowercase();

    // Block localhost and private IPs
    if url_lower.contains("localhost")
        || url_lower.contains("127.0.0.1")
        || url_lower.contains("0.0.0.0")
        || url_lower.contains("[::1]")
    {
        return Err(anyhow::anyhow!(
            "Access to localhost is not allowed. Use actual hostnames or IPs."
        ));
    }

    // Block private IP ranges
    if url_lower.contains("192.168.")
        || url_lower.contains("10.0.")
        || url_lower.contains("10.1.")
        || url_lower.contains("172.16.")
        || url_lower.contains("172.17.")
        || url_lower.contains("172.18.")
        || url_lower.contains("172.19.")
        || url_lower.contains("172.20.")
        || url_lower.contains("172.21.")
        || url_lower.contains("172.22.")
        || url_lower.contains("172.23.")
        || url_lower.contains("172.24.")
        || url_lower.contains("172.25.")
        || url_lower.contains("172.26.")
        || url_lower.contains("172.27.")
        || url_lower.contains("172.28.")
        || url_lower.contains("172.29.")
        || url_lower.contains("172.30.")
        || url_lower.contains("172.31.")
    {
        return Err(anyhow::anyhow!(
            "Access to private IP ranges is not allowed for security reasons."
        ));
    }

    // Block metadata endpoints
    if url_lower.contains("169.254.169.254")
        || url_lower.contains("metadata.google")
        || url_lower.contains("metadata.goog")
        || url_lower.contains("metadata") && url_lower.contains("internal")
    {
        return Err(anyhow::anyhow!(
            "Access to cloud metadata endpoints is not allowed."
        ));
    }

    // Block file:// and other dangerous schemes
    if !base_url.starts_with("http://") && !base_url.starts_with("https://") {
        return Err(anyhow::anyhow!("Only HTTP and HTTPS URLs are allowed."));
    }

    Ok(())
}
