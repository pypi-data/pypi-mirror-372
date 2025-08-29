/// OpenAPI specification version detection
use anyhow::{anyhow, Result};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::fmt;

/// Supported OpenAPI/Swagger specification versions
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum SpecVersion {
    /// Swagger 2.0
    Swagger2_0,
    /// OpenAPI 3.0.x (stores exact version)
    OpenAPI3_0(String),
    /// OpenAPI 3.1.x (stores exact version)
    OpenAPI3_1(String),
}

impl fmt::Display for SpecVersion {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            SpecVersion::Swagger2_0 => write!(f, "Swagger 2.0"),
            SpecVersion::OpenAPI3_0(v) => write!(f, "OpenAPI {}", v),
            SpecVersion::OpenAPI3_1(v) => write!(f, "OpenAPI {}", v),
        }
    }
}

impl SpecVersion {}

/// Detect the specification version from the content
pub fn detect_spec_version(content: &str) -> Result<SpecVersion> {
    // Try to parse as JSON first, then YAML
    let value: Value = serde_json::from_str(content)
        .or_else(|_| serde_yaml::from_str(content))
        .map_err(|e| anyhow!("Failed to parse spec: {}", e))?;

    detect_version_from_value(&value)
}

/// Detect version from a parsed JSON value
pub fn detect_version_from_value(value: &Value) -> Result<SpecVersion> {
    // Check for Swagger 2.0
    if let Some(swagger_version) = value.get("swagger").and_then(|v| v.as_str()) {
        if swagger_version == "2.0" {
            return Ok(SpecVersion::Swagger2_0);
        } else {
            return Err(anyhow!(
                "Unsupported Swagger version: {}. Only 2.0 is supported.",
                swagger_version
            ));
        }
    }

    // Check for OpenAPI 3.x
    if let Some(openapi_version) = value.get("openapi").and_then(|v| v.as_str()) {
        // Parse version string
        let parts: Vec<&str> = openapi_version.split('.').collect();
        if parts.len() < 2 {
            return Err(anyhow!(
                "Invalid OpenAPI version format: {}",
                openapi_version
            ));
        }

        match parts[0] {
            "3" => {
                match parts[1] {
                    "0" => {
                        // Validate it's a known 3.0.x version
                        if ["3.0.0", "3.0.1", "3.0.2", "3.0.3"].contains(&openapi_version) {
                            Ok(SpecVersion::OpenAPI3_0(openapi_version.to_string()))
                        } else {
                            Err(anyhow!(
                                "Unsupported OpenAPI 3.0.x version: {}. Supported: 3.0.0, 3.0.1, 3.0.2, 3.0.3",
                                openapi_version
                            ))
                        }
                    }
                    "1" => {
                        // OpenAPI 3.1.x
                        Ok(SpecVersion::OpenAPI3_1(openapi_version.to_string()))
                    }
                    _ => Err(anyhow!(
                        "Unsupported OpenAPI version: {}. Supported: 3.0.x and 3.1.x",
                        openapi_version
                    )),
                }
            }
            _ => Err(anyhow!(
                "Unsupported OpenAPI major version: {}. Only version 3.x is supported.",
                openapi_version
            )),
        }
    } else {
        Err(anyhow!(
            "No 'swagger' or 'openapi' field found. This doesn't appear to be a valid OpenAPI/Swagger specification."
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_detect_swagger_2_0() {
        let spec = json!({
            "swagger": "2.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            }
        });

        let version = detect_version_from_value(&spec).unwrap();
        assert_eq!(version, SpecVersion::Swagger2_0);
    }

    #[test]
    fn test_detect_openapi_3_0() {
        let spec = json!({
            "openapi": "3.0.2",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            }
        });

        let version = detect_version_from_value(&spec).unwrap();
        assert_eq!(version, SpecVersion::OpenAPI3_0("3.0.2".to_string()));
    }

    #[test]
    fn test_detect_openapi_3_1() {
        let spec = json!({
            "openapi": "3.1.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            }
        });

        let version = detect_version_from_value(&spec).unwrap();
        assert_eq!(version, SpecVersion::OpenAPI3_1("3.1.0".to_string()));
    }

    #[test]
    fn test_invalid_version() {
        let spec = json!({
            "openapi": "2.0",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            }
        });

        let result = detect_version_from_value(&spec);
        assert!(result.is_err());
    }

    #[test]
    fn test_missing_version() {
        let spec = json!({
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            }
        });

        let result = detect_version_from_value(&spec);
        assert!(result.is_err());
    }
}
