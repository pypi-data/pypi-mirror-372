pub mod lint;
pub mod operations;
/// Embedded validation rules for different OpenAPI versions
pub mod references;
pub mod schemas;

/// Basic validation rules that can be checked without external tools
pub mod basic {
    use crate::core::validation::types::{Severity, ValidationError, ValidationResult};
    use serde_json::Value;

    /// Perform basic structural validation
    pub fn validate_basic_structure(spec: &Value) -> ValidationResult {
        let mut result = ValidationResult::new();

        // Check for version field
        if !spec.get("swagger").is_some() && !spec.get("openapi").is_some() {
            result.errors.push(
                ValidationError::new(
                    "missing-version",
                    "Specification must have either 'swagger' or 'openapi' field",
                )
                .with_path("$"),
            );
        }

        // Check for info section
        if spec.get("info").is_none() {
            result.errors.push(
                ValidationError::new("missing-info", "Specification must have an 'info' section")
                    .with_path("$"),
            );
        } else if let Some(info) = spec.get("info") {
            // Check info has required fields
            if info.get("title").is_none() {
                result.errors.push(
                    ValidationError::new("missing-title", "Info section must have a 'title'")
                        .with_path("$.info"),
                );
            }
            if info.get("version").is_none() {
                result.errors.push(
                    ValidationError::new("missing-version", "Info section must have a 'version'")
                        .with_path("$.info"),
                );
            }
        }

        // Check for API content
        let has_paths = spec.get("paths").is_some();
        let has_webhooks = spec.get("webhooks").is_some();
        let has_components = spec.get("components").is_some();

        if !has_paths && !has_webhooks && !has_components {
            result.errors.push(
                ValidationError::new(
                    "missing-api-content",
                    "Specification must have at least one of: paths, webhooks, or components",
                )
                .with_path("$"),
            );
        }

        result
    }

    /// Validate security aspects
    pub fn validate_security(spec: &Value) -> ValidationResult {
        let mut result = ValidationResult::new();

        // Check servers for HTTPS
        if let Some(servers) = spec.get("servers").and_then(|s| s.as_array()) {
            for (i, server) in servers.iter().enumerate() {
                if let Some(url) = server.get("url").and_then(|u| u.as_str()) {
                    let url_lower = url.to_lowercase();

                    // Check for HTTPS
                    if url_lower.starts_with("http://") && !url_lower.contains("localhost") {
                        result.warnings.push(
                            ValidationError::new(
                                "insecure-server",
                                format!("Server URL should use HTTPS instead of HTTP: {}", url),
                            )
                            .with_path(&format!("$.servers[{}].url", i))
                            .with_severity(Severity::Warning),
                        );
                    }

                    // Check for localhost/private IPs
                    if url_lower.contains("localhost")
                        || url_lower.contains("127.0.0.1")
                        || url_lower.contains("192.168.")
                        || url_lower.contains("10.0.")
                        || url_lower.contains("172.16.")
                    {
                        result.errors.push(
                            ValidationError::new(
                                "private-server-url",
                                format!("Server URL contains private/local address: {}", url),
                            )
                            .with_path(&format!("$.servers[{}].url", i)),
                        );
                    }

                    // Check for metadata endpoints
                    if url_lower.contains("169.254.169.254") || url_lower.contains("metadata") {
                        result.errors.push(
                            ValidationError::new(
                                "metadata-endpoint",
                                format!("Server URL points to metadata endpoint: {}", url),
                            )
                            .with_path(&format!("$.servers[{}].url", i)),
                        );
                    }
                }
            }
        }

        // Check for Swagger 2.0 schemes
        if let Some(schemes) = spec.get("schemes").and_then(|s| s.as_array()) {
            let has_https = schemes.iter().any(|s| s.as_str() == Some("https"));
            if !has_https {
                result.warnings.push(
                    ValidationError::new(
                        "no-https-scheme",
                        "API should support HTTPS scheme for security",
                    )
                    .with_path("$.schemes")
                    .with_severity(Severity::Warning),
                );
            }
        }

        result
    }

    /// Check for MicroRapid-specific requirements
    pub fn validate_mrapids_requirements(spec: &Value) -> ValidationResult {
        let mut result = ValidationResult::new();

        // Check all operations have operationId
        if let Some(paths) = spec.get("paths").and_then(|p| p.as_object()) {
            for (path, path_item) in paths {
                if let Some(path_obj) = path_item.as_object() {
                    for (method, operation) in path_obj {
                        // Skip non-operation fields
                        if ["parameters", "servers", "$ref"].contains(&method.as_str()) {
                            continue;
                        }

                        if let Some(op) = operation.as_object() {
                            if op.get("operationId").is_none() {
                                result.errors.push(
                                    ValidationError::new(
                                        "missing-operation-id",
                                        "Operation must have operationId for CLI usage",
                                    )
                                    .with_path(&format!("$.paths.{}.{}", path, method)),
                                );
                            }
                        }
                    }
                }
            }
        }

        result
    }
}
