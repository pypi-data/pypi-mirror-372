use reqwest::{Client, RequestBuilder, Response, redirect::Policy};
use reqwest::header::{HeaderMap, HeaderValue, USER_AGENT};
use std::time::Duration;

use crate::security::{UrlValidator, SecurityConfig, SecurityError};

pub struct SecureHttpClient {
    client: Client,
    url_validator: UrlValidator,
    config: SecurityConfig,
}

impl SecureHttpClient {
    pub fn new(config: SecurityConfig) -> Result<Self, Box<dyn std::error::Error>> {
        // Build secure headers
        let mut headers = HeaderMap::new();
        headers.insert(USER_AGENT, HeaderValue::from_static("MicroRapid/1.0"));
        
        // Create URL validator from config
        let mut url_validator = UrlValidator::default();
        url_validator.allowed_schemes = config.network.allowed_schemes.iter()
            .cloned()
            .collect();
        url_validator.allowed_ports = config.network.allowed_ports.iter()
            .cloned()
            .collect();
        url_validator.max_redirects = config.network.max_redirects;
        
        // Build secure client
        let client = Client::builder()
            .default_headers(headers)
            .timeout(Duration::from_millis(config.limits.request_timeout))
            .redirect(Policy::limited(config.network.max_redirects as usize))
            .danger_accept_invalid_certs(!config.tls.verify)
            .min_tls_version(parse_tls_version(&config.tls.min_version))
            .build()?;
        
        Ok(Self {
            client,
            url_validator,
            config,
        })
    }
    
    pub fn from_defaults() -> Result<Self, Box<dyn std::error::Error>> {
        Self::new(SecurityConfig::default())
    }
    
    pub async fn get(&self, url: &str) -> Result<Response, Box<dyn std::error::Error>> {
        // Validate URL with DNS resolution
        let validated = self.url_validator.validate_with_dns(url).await?;
        
        // Create request
        let request = self.client.get(validated.url.as_str());
        
        // Apply size limits via stream processing
        let response = self.execute_with_limits(request).await?;
        
        Ok(response)
    }
    
    pub async fn post(&self, url: &str) -> Result<RequestBuilder, Box<dyn std::error::Error>> {
        // Validate URL with DNS resolution
        let validated = self.url_validator.validate_with_dns(url).await?;
        
        // Return builder for further configuration
        Ok(self.client.post(validated.url.as_str()))
    }
    
    pub async fn execute_with_limits(&self, request: RequestBuilder) -> Result<Response, Box<dyn std::error::Error>> {
        let response = request.send().await?;
        
        // Check response size from headers
        if let Some(content_length) = response.headers().get("content-length") {
            if let Ok(length_str) = content_length.to_str() {
                if let Ok(length) = length_str.parse::<usize>() {
                    if length > self.config.limits.max_response_size {
                        return Err(Box::new(SecurityError::ConfigError(
                            format!("Response too large: {} bytes", length)
                        )));
                    }
                }
            }
        }
        
        Ok(response)
    }
    
    pub fn validate_request_size(&self, size: usize) -> Result<(), SecurityError> {
        if size > self.config.limits.max_request_size {
            return Err(SecurityError::ConfigError(
                format!("Request too large: {} bytes", size)
            ));
        }
        Ok(())
    }
}

fn parse_tls_version(version: &str) -> reqwest::tls::Version {
    match version {
        "1.0" => reqwest::tls::Version::TLS_1_0,
        "1.1" => reqwest::tls::Version::TLS_1_1,
        "1.2" => reqwest::tls::Version::TLS_1_2,
        "1.3" => reqwest::tls::Version::TLS_1_3,
        _ => reqwest::tls::Version::TLS_1_2, // Default to 1.2
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[tokio::test]
    async fn test_blocks_dangerous_urls() {
        let client = SecureHttpClient::from_defaults().unwrap();
        
        // Should block localhost
        assert!(client.get("http://localhost/api").await.is_err());
        
        // Should block private IPs
        assert!(client.get("http://192.168.1.1/api").await.is_err());
        
        // Should block metadata endpoints
        assert!(client.get("http://169.254.169.254/").await.is_err());
    }
}