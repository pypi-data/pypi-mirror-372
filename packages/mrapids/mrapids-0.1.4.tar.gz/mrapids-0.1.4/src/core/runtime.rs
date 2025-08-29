use super::errors::CoreError;
use crate::utils::security::enforce_https;
use colored::*;
use openapiv3::{OpenAPI, Operation};
use reqwest::blocking::{Client, Response};
use serde_json::Value;

pub fn execute_operation(
    spec: &OpenAPI,
    _operation: &Operation,
    base_url: Option<&str>,
    _data: Option<String>,
    allow_insecure: bool,
) -> Result<Response, CoreError> {
    // Get base URL from spec or override
    let base_url = base_url.unwrap_or_else(|| {
        spec.servers
            .first()
            .map(|s| s.url.as_str())
            .unwrap_or("http://localhost:3000")
    });

    // Validate URL for security and enforce HTTPS
    enforce_https(base_url, allow_insecure).map_err(|e| CoreError::RequestFailed {
        reason: format!("Security validation failed: {}", e),
    })?;

    // For MVP, just do a simple GET request
    // TODO: Handle other methods, parameters, body, etc.
    let client = Client::new();
    let url = format!("{}/example", base_url); // Simplified for MVP

    println!("🌐 Request URL: {}", url.cyan());

    let response = client
        .get(&url)
        .send()
        .map_err(|e| CoreError::RequestFailed {
            reason: e.to_string(),
        })?;

    Ok(response)
}

pub fn test_operation(
    spec: &OpenAPI,
    operation_id: &str,
    allow_insecure: bool,
) -> Result<(), CoreError> {
    let operation = super::spec::find_operation(spec, operation_id)?;
    let response = execute_operation(spec, operation, None, None, allow_insecure)?;

    if response.status().is_success() {
        Ok(())
    } else {
        Err(CoreError::RequestFailed {
            reason: format!("HTTP {}", response.status()),
        })
    }
}

#[allow(dead_code)]
pub fn display_response(response: Response, format: &str) -> Result<(), CoreError> {
    let status = response.status();
    let headers = response.headers().clone();

    // Display status
    let status_color = if status.is_success() {
        status.to_string().green()
    } else {
        status.to_string().red()
    };
    println!("\n📊 Status: {}", status_color);

    // Display headers (if verbose)
    if format == "verbose" {
        println!("\n📋 Headers:");
        for (key, value) in headers.iter() {
            println!("  {}: {:?}", key.to_string().dimmed(), value);
        }
    }

    // Display body
    let body = response.text().map_err(|e| CoreError::RequestFailed {
        reason: format!("Cannot read response: {}", e),
    })?;

    match format {
        "json" => {
            println!("{}", body);
        }
        _ => {
            println!("\n📦 Response:");

            // Try to pretty-print JSON
            if let Ok(json) = serde_json::from_str::<Value>(&body) {
                let pretty = serde_json::to_string_pretty(&json).unwrap_or(body.clone());
                println!("{}", pretty.bright_white());
            } else {
                println!("{}", body.bright_white());
            }
        }
    }

    Ok(())
}
