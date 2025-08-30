//! List operations functionality

use super::errors::*;
use crate::core::parser::{ApiInfo, UnifiedOperation, UnifiedSpec};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListRequest {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub filter: Option<ListFilter>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub spec_path: Option<PathBuf>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListFilter {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub method: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tag: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub pattern: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ListResponse {
    pub operations: Vec<OperationSummary>,
    pub total: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct OperationSummary {
    pub operation_id: String,
    pub method: String,
    pub path: String,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub summary: Option<String>,

    #[serde(default)]
    pub tags: Vec<String>,
}

/// List available operations
#[allow(dead_code)]
pub async fn list_operations(
    request: ListRequest,
    spec: &UnifiedSpec,
) -> Result<ListResponse, ApiError> {
    let operations: Vec<OperationSummary> = spec
        .operations
        .iter()
        .filter(|op| {
            // Apply filters
            if let Some(filter) = &request.filter {
                // Filter by method
                if let Some(method) = &filter.method {
                    if op.method.to_lowercase() != method.to_lowercase() {
                        return false;
                    }
                }

                // Filter by tag
                if let Some(_tag) = &filter.tag {
                    // TODO: Extract tags from operation
                    // For now, skip tag filtering
                }

                // Filter by pattern
                if let Some(pattern) = &filter.pattern {
                    if !op.operation_id.contains(pattern) && !op.path.contains(pattern) {
                        return false;
                    }
                }
            }
            true
        })
        .map(|op| OperationSummary {
            operation_id: op.operation_id.clone(),
            method: op.method.clone(),
            path: op.path.clone(),
            summary: op.summary.clone(),
            tags: vec![], // TODO: Extract from operation
        })
        .collect();

    let total = operations.len();

    Ok(ListResponse { operations, total })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::parser::{ApiInfo, UnifiedOperation};
    use std::collections::HashMap;

    #[tokio::test]
    async fn test_list_operations_no_filter() {
        let spec = UnifiedSpec {
            info: ApiInfo {
                title: "Test API".to_string(),
                version: "1.0.0".to_string(),
                description: None,
            },
            base_url: "https://api.example.com".to_string(),
            operations: vec![
                UnifiedOperation {
                    operation_id: "getUser".to_string(),
                    method: "GET".to_string(),
                    path: "/users/{id}".to_string(),
                    summary: Some("Get a user by ID".to_string()),
                    description: None,
                    parameters: vec![],
                    request_body: None,
                    responses: HashMap::new(),
                    security: None,
                },
                UnifiedOperation {
                    operation_id: "createUser".to_string(),
                    method: "POST".to_string(),
                    path: "/users".to_string(),
                    summary: Some("Create a new user".to_string()),
                    description: None,
                    parameters: vec![],
                    request_body: None,
                    responses: HashMap::new(),
                    security: None,
                },
            ],
            security_schemes: HashMap::new(),
        };

        let request = ListRequest {
            filter: None,
            spec_path: None,
        };

        let response = list_operations(request, &spec).await.unwrap();
        assert_eq!(response.total, 2);
        assert_eq!(response.operations.len(), 2);
    }

    #[tokio::test]
    async fn test_list_operations_with_method_filter() {
        let spec = UnifiedSpec {
            info: ApiInfo {
                title: "Test API".to_string(),
                version: "1.0.0".to_string(),
                description: None,
            },
            base_url: "https://api.example.com".to_string(),
            operations: vec![
                UnifiedOperation {
                    operation_id: "getUser".to_string(),
                    method: "GET".to_string(),
                    path: "/users/{id}".to_string(),
                    summary: None,
                    description: None,
                    parameters: vec![],
                    request_body: None,
                    responses: HashMap::new(),
                    security: None,
                },
                UnifiedOperation {
                    operation_id: "createUser".to_string(),
                    method: "POST".to_string(),
                    path: "/users".to_string(),
                    summary: None,
                    description: None,
                    parameters: vec![],
                    request_body: None,
                    responses: HashMap::new(),
                    security: None,
                },
            ],
            security_schemes: HashMap::new(),
        };

        let request = ListRequest {
            filter: Some(ListFilter {
                method: Some("GET".to_string()),
                tag: None,
                pattern: None,
            }),
            spec_path: None,
        };

        let response = list_operations(request, &spec).await.unwrap();
        assert_eq!(response.total, 1);
        assert_eq!(response.operations[0].operation_id, "getUser");
    }
}
