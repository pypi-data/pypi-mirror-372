//! HTTP client with timeout and size limit enforcement

use super::auth::{AuthType, SimpleAuthProfile};
use super::rate_limiter::{RateLimitConfig, RateLimiter};
use super::response::HttpResponse;
use super::retry::{RetryPolicy, RetryStrategy};
use anyhow::{anyhow, Result};
use reqwest::{Client, ClientBuilder, Response};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::time::Duration;
use tokio::time::timeout;
use url::Url;

/// HTTP client configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HttpClientConfig {
    /// Request timeout in seconds
    pub timeout_secs: u64,
    /// Maximum request body size in bytes
    pub max_request_body_size: usize,
    /// Maximum response body size in bytes
    pub max_response_body_size: usize,
    /// Retry policy
    pub retry_policy: RetryPolicy,
    /// User agent string
    pub user_agent: String,
}

impl Default for HttpClientConfig {
    fn default() -> Self {
        Self {
            timeout_secs: 30,
            max_request_body_size: 10 * 1024 * 1024,  // 10MB
            max_response_body_size: 50 * 1024 * 1024, // 50MB
            retry_policy: RetryPolicy::default(),
            user_agent: format!("mrapids-agent/{}", env!("CARGO_PKG_VERSION")),
        }
    }
}

/// HTTP client with resource protection
pub struct HttpClient {
    client: Client,
    config: HttpClientConfig,
    rate_limiter: RateLimiter,
}

impl HttpClient {
    /// Create a new HTTP client
    pub fn new(config: HttpClientConfig) -> Result<Self> {
        let client = ClientBuilder::new()
            .timeout(Duration::from_secs(config.timeout_secs))
            .user_agent(&config.user_agent)
            .danger_accept_invalid_certs(false)
            .build()?;

        let rate_limiter = RateLimiter::new(RateLimitConfig::default());

        Ok(Self {
            client,
            config,
            rate_limiter,
        })
    }

    /// Execute a GET request
    pub async fn get(&self, url: &str, auth: Option<&SimpleAuthProfile>) -> Result<HttpResponse> {
        self.execute_with_retry("GET", url, None, auth).await
    }

    /// Execute a POST request
    pub async fn post(
        &self,
        url: &str,
        body: Option<&Value>,
        auth: Option<&SimpleAuthProfile>,
    ) -> Result<HttpResponse> {
        self.execute_with_retry("POST", url, body, auth).await
    }

    /// Execute a PUT request
    pub async fn put(
        &self,
        url: &str,
        body: Option<&Value>,
        auth: Option<&SimpleAuthProfile>,
    ) -> Result<HttpResponse> {
        self.execute_with_retry("PUT", url, body, auth).await
    }

    /// Execute a PATCH request
    pub async fn patch(
        &self,
        url: &str,
        body: Option<&Value>,
        auth: Option<&SimpleAuthProfile>,
    ) -> Result<HttpResponse> {
        self.execute_with_retry("PATCH", url, body, auth).await
    }

    /// Execute a DELETE request
    pub async fn delete(
        &self,
        url: &str,
        auth: Option<&SimpleAuthProfile>,
    ) -> Result<HttpResponse> {
        self.execute_with_retry("DELETE", url, None, auth).await
    }

    /// Execute request with retry logic
    async fn execute_with_retry(
        &self,
        method: &str,
        url: &str,
        body: Option<&Value>,
        auth: Option<&SimpleAuthProfile>,
    ) -> Result<HttpResponse> {
        let mut retry_strategy = RetryStrategy::new(&self.config.retry_policy);
        let mut last_error = None;

        while retry_strategy.should_retry() {
            match self.execute_request(method, url, body, auth).await {
                Ok(response) => return Ok(response),
                Err(e) => {
                    last_error = Some(e);

                    // Check if error is retryable
                    if !self.is_retryable_error(last_error.as_ref().unwrap()) {
                        break;
                    }

                    // Wait before retry
                    if let Some(delay) = retry_strategy.next_delay() {
                        tokio::time::sleep(delay).await;
                    } else {
                        break;
                    }
                }
            }
        }

        Err(last_error.unwrap_or_else(|| anyhow!("Request failed after retries")))
    }

    /// Execute a single request
    async fn execute_request(
        &self,
        method: &str,
        url: &str,
        body: Option<&Value>,
        auth: Option<&SimpleAuthProfile>,
    ) -> Result<HttpResponse> {
        // Extract host from URL for rate limiting
        let parsed_url =
            Url::parse(url).map_err(|e| anyhow!("Failed to parse URL '{}': {}", url, e))?;
        let host = parsed_url.host_str();

        // Apply rate limiting
        self.rate_limiter
            .wait_if_needed(host)
            .await
            .map_err(|e| anyhow!("Rate limit exceeded for URL '{}': {}", url, e))?;

        // Check request body size
        if let Some(body_value) = body {
            let body_size = serde_json::to_vec(body_value)?.len();
            if body_size > self.config.max_request_body_size {
                return Err(anyhow!(
                    "Request body too large: {} bytes (max: {} bytes)",
                    body_size,
                    self.config.max_request_body_size
                ));
            }
        }

        // Build request
        let mut request_builder = match method {
            "GET" => self.client.get(url),
            "POST" => self.client.post(url),
            "PUT" => self.client.put(url),
            "PATCH" => self.client.patch(url),
            "DELETE" => self.client.delete(url),
            _ => return Err(anyhow!("Unsupported HTTP method: {}", method)),
        };

        // Add authentication
        if let Some(auth) = auth {
            request_builder = self.apply_auth(request_builder, auth);
        }

        // Add body
        if let Some(body_value) = body {
            request_builder = request_builder
                .header("Content-Type", "application/json")
                .json(body_value);
        }

        // Execute with timeout enforcement
        let response = timeout(
            Duration::from_secs(self.config.timeout_secs),
            request_builder.send(),
        )
        .await
        .map_err(|_| {
            anyhow!(
                "Request timed out after {} seconds",
                self.config.timeout_secs
            )
        })??;

        // Capture status and headers
        let status_code = response.status().as_u16();
        let mut headers = HashMap::new();

        // Convert headers to HashMap
        for (key, value) in response.headers() {
            if let Ok(value_str) = value.to_str() {
                headers.insert(key.to_string(), value_str.to_string());
            }
        }

        // Check response size
        if let Some(content_length) = response.content_length() {
            if content_length as usize > self.config.max_response_body_size {
                return Err(anyhow!(
                    "Response too large: {} bytes (max: {} bytes)",
                    content_length,
                    self.config.max_response_body_size
                ));
            }
        }

        // Read response body
        let response_bytes = self.read_response_with_limit(response).await?;

        // Try to parse as JSON
        let (body, raw_body) =
            if let Ok(json_value) = serde_json::from_slice::<Value>(&response_bytes) {
                (Some(json_value), None)
            } else {
                // If not JSON, store as raw string
                let raw = String::from_utf8_lossy(&response_bytes).to_string();
                (None, Some(raw))
            };

        Ok(HttpResponse {
            status_code,
            headers,
            body,
            raw_body,
        })
    }

    /// Apply authentication to request
    fn apply_auth(
        &self,
        mut builder: reqwest::RequestBuilder,
        auth: &SimpleAuthProfile,
    ) -> reqwest::RequestBuilder {
        match &auth.auth_type {
            AuthType::Bearer => {
                if let Some(token) = &auth.token {
                    builder = builder.bearer_auth(token);
                }
            }
            AuthType::Basic => {
                if let (Some(username), Some(password)) = (&auth.username, &auth.password) {
                    builder = builder.basic_auth(username, Some(password));
                }
            }
            AuthType::ApiKey => {
                if let (Some(header), Some(token)) = (&auth.header, &auth.token) {
                    builder = builder.header(header, token);
                }
            }
        }
        builder
    }

    /// Read response body with size limit
    async fn read_response_with_limit(&self, response: Response) -> Result<Vec<u8>> {
        let mut body = Vec::new();
        let mut stream = response.bytes_stream();

        use futures::StreamExt;
        while let Some(chunk) = stream.next().await {
            let chunk = chunk?;
            body.extend_from_slice(&chunk);

            if body.len() > self.config.max_response_body_size {
                return Err(anyhow!(
                    "Response body too large: exceeds {} bytes",
                    self.config.max_response_body_size
                ));
            }
        }

        Ok(body)
    }

    /// Check if error is retryable
    fn is_retryable_error(&self, error: &anyhow::Error) -> bool {
        let error_str = error.to_string();

        // Timeout errors are retryable
        if error_str.contains("timed out") {
            return true;
        }

        // Network errors are retryable
        if error_str.contains("connection") || error_str.contains("network") {
            return true;
        }

        // HTTP 5xx errors are retryable
        if error_str.contains("HTTP 5") {
            return true;
        }

        // HTTP 429 (rate limit) is retryable
        if error_str.contains("HTTP 429") {
            return true;
        }

        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_config() {
        let config = HttpClientConfig::default();
        assert_eq!(config.timeout_secs, 30);
        assert_eq!(config.max_request_body_size, 10 * 1024 * 1024);
        assert_eq!(config.max_response_body_size, 50 * 1024 * 1024);
    }

    #[test]
    fn test_client_creation() {
        let config = HttpClientConfig::default();
        let client = HttpClient::new(config);
        assert!(client.is_ok());
    }
}
