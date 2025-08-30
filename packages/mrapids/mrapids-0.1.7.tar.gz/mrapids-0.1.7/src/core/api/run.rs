//! API operation execution logic

use super::errors::*;
use super::types::*;
use crate::core::auth::AuthProfile;
use crate::core::http::{HttpClient, HttpClientConfig, HttpResponse, SimpleAuthProfile};
use crate::core::parser::UnifiedSpec;
use crate::utils::security::validate_url;
use regex::Regex;
use serde_json::Value;
use std::collections::HashMap;
use std::time::Instant;
use uuid::Uuid;

/// Execute an API operation
#[allow(dead_code)]
pub async fn run_operation(
    request: RunRequest,
    spec: &UnifiedSpec,
    auth: Option<AuthProfile>,
) -> Result<RunResponse, ApiError> {
    let start = Instant::now();
    let request_id = Uuid::new_v4().to_string();
    let timestamp = chrono::Utc::now();

    // Find the operation
    let operation = spec
        .operations
        .iter()
        .find(|op| op.operation_id == request.operation_id)
        .ok_or_else(|| ApiError::OperationNotFound(request.operation_id.clone()))?;

    // Build the full URL
    let base_url = if let Some(env) = &request.env {
        // Load environment-specific base URL
        load_base_url_for_env(env, &spec.base_url)?
    } else {
        spec.base_url.clone()
    };

    // Validate base URL for security
    validate_url(&base_url)
        .map_err(|e| ApiError::ValidationError(format!("Invalid base URL: {}", e)))?;

    let url = format!("{}{}", base_url, operation.path);

    // Execute the operation
    match execute_http_request(operation, &url, request.parameters, request.body, auth).await {
        Ok((response_data, status_code, headers)) => Ok(RunResponse {
            status: ResponseStatus::Success,
            data: Some(response_data),
            error: None,
            meta: ResponseMeta {
                operation_id: request.operation_id,
                method: operation.method.clone(),
                url,
                status_code,
                duration_ms: start.elapsed().as_millis() as u64,
                request_id,
                timestamp,
                headers: Some(headers),
            },
        }),
        Err(e) => {
            let error_code = ErrorCode::from(&e);
            Ok(RunResponse {
                status: ResponseStatus::Error,
                data: None,
                error: Some(ErrorDetail {
                    code: error_code as u16,
                    message: e.to_string(),
                    details: None,
                }),
                meta: ResponseMeta {
                    operation_id: request.operation_id,
                    method: operation.method.clone(),
                    url,
                    status_code: 0,
                    duration_ms: start.elapsed().as_millis() as u64,
                    request_id,
                    timestamp,
                    headers: None,
                },
            })
        }
    }
}

/// Execute the HTTP request
#[allow(dead_code)]
async fn execute_http_request(
    operation: &crate::core::parser::UnifiedOperation,
    url: &str,
    parameters: Option<HashMap<String, Value>>,
    body: Option<Value>,
    auth: Option<AuthProfile>,
) -> Result<(Value, u16, HashMap<String, String>), ApiError> {
    // Validate URL again before making the request
    validate_url(url)
        .map_err(|e| ApiError::ValidationError(format!("Invalid request URL: {}", e)))?;

    // Create HTTP client with resource protection
    let config = HttpClientConfig::default();
    let client = HttpClient::new(config).map_err(|e| ApiError::NetworkError(e.to_string()))?;

    // Build full URL with parameters
    let full_url = build_url_with_params(url, &parameters);

    // Convert AuthProfile to SimpleAuthProfile if provided
    let simple_auth = auth
        .map(|_| {
            // TODO: Properly convert OAuth AuthProfile to SimpleAuthProfile
            // For now, return None as OAuth profile doesn't have direct auth fields
            None::<SimpleAuthProfile>
        })
        .flatten();

    // Execute request based on method
    let response: Result<HttpResponse, anyhow::Error> =
        match operation.method.to_uppercase().as_str() {
            "GET" => client.get(&full_url, simple_auth.as_ref()).await,
            "POST" => {
                client
                    .post(&full_url, body.as_ref(), simple_auth.as_ref())
                    .await
            }
            "PUT" => {
                client
                    .put(&full_url, body.as_ref(), simple_auth.as_ref())
                    .await
            }
            "PATCH" => {
                client
                    .patch(&full_url, body.as_ref(), simple_auth.as_ref())
                    .await
            }
            "DELETE" => client.delete(&full_url, simple_auth.as_ref()).await,
            method => {
                return Err(ApiError::ValidationError(format!(
                    "Unsupported HTTP method: {}",
                    method
                )))
            }
        };

    match response {
        Ok(http_response) => {
            // Extract the response body as Value
            let response_value = if let Some(json_body) = http_response.body {
                json_body
            } else if let Some(raw_body) = http_response.raw_body {
                // For non-JSON responses, return as a string value
                Value::String(raw_body)
            } else {
                // No body - return null
                Value::Null
            };

            Ok((
                response_value,
                http_response.status_code,
                http_response.headers,
            ))
        }
        Err(e) => {
            // Parse error for proper status code
            let error_str = e.to_string();
            if error_str.contains("HTTP 4") {
                Err(ApiError::ClientError(error_str))
            } else if error_str.contains("HTTP 5") {
                Err(ApiError::ServerError(error_str))
            } else if error_str.contains("timed out") {
                Err(ApiError::TimeoutError(error_str))
            } else if error_str.contains("too large") {
                Err(ApiError::PayloadTooLarge(error_str))
            } else {
                Err(ApiError::NetworkError(error_str))
            }
        }
    }
}

/// Intelligently decode URL-encoded parameters if they appear to be encoded
fn smart_decode_if_needed(value: &str) -> String {
    // Check if the value contains % and looks like it might be URL-encoded
    if value.contains('%') && looks_like_url_encoded(value) {
        // Try to decode it
        match urlencoding::decode(value) {
            Ok(decoded) => decoded.to_string(),
            Err(_) => value.to_string(), // If decode fails, use original
        }
    } else {
        value.to_string()
    }
}

/// Check if a string looks like it contains URL encoding
fn looks_like_url_encoded(s: &str) -> bool {
    // Look for %XX patterns where X is a hex digit
    regex::Regex::new(r"%[0-9A-Fa-f]{2}")
        .map(|re| re.is_match(s))
        .unwrap_or(false)
}

/// Build URL with query parameters
fn build_url_with_params(base_url: &str, parameters: &Option<HashMap<String, Value>>) -> String {
    if let Some(params) = parameters {
        let query_params: Vec<String> = params
            .iter()
            .filter_map(|(key, value)| {
                match value {
                    Value::String(s) => {
                        // Apply smart decoding before encoding to prevent double-encoding
                        let decoded = smart_decode_if_needed(s);
                        Some(format!("{}={}", key, urlencoding::encode(&decoded)))
                    }
                    Value::Number(n) => Some(format!("{}={}", key, n)),
                    Value::Bool(b) => Some(format!("{}={}", key, b)),
                    _ => None,
                }
            })
            .collect();

        if !query_params.is_empty() {
            format!("{}?{}", base_url, query_params.join("&"))
        } else {
            base_url.to_string()
        }
    } else {
        base_url.to_string()
    }
}

/// Load base URL for the specified environment
#[allow(dead_code)]
fn load_base_url_for_env(_env: &str, default: &str) -> Result<String, ApiError> {
    // TODO: Load from config file
    // For now, just return the default
    Ok(default.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::parser::ApiInfo;

    #[tokio::test]
    async fn test_run_operation_not_found() {
        let request = RunRequest {
            operation_id: "nonexistent".to_string(),
            parameters: None,
            body: None,
            spec_path: None,
            env: None,
            auth_profile: None,
        };

        let spec = UnifiedSpec {
            info: ApiInfo {
                title: "Test API".to_string(),
                version: "1.0.0".to_string(),
                description: None,
            },
            base_url: "https://api.example.com".to_string(),
            operations: vec![],
            security_schemes: HashMap::new(),
        };

        let result = run_operation(request, &spec, None).await;
        assert!(result.is_err());

        match result {
            Err(ApiError::OperationNotFound(op)) => {
                assert_eq!(op, "nonexistent");
            }
            _ => panic!("Expected OperationNotFound error"),
        }
    }
}
