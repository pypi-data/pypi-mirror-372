//! Show operation details functionality

use super::errors::*;
use crate::core::parser::{
    ApiInfo, ParameterLocation, SchemaType, UnifiedOperation, UnifiedParameter, UnifiedSchema,
    UnifiedSpec,
};
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ShowRequest {
    pub operation_id: String,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub spec_path: Option<PathBuf>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ShowResponse {
    pub operation_id: String,
    pub method: String,
    pub path: String,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub summary: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    pub parameters: Vec<ParameterDetail>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub request_body: Option<RequestBodyDetail>,

    pub responses: HashMap<String, ResponseDetail>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ParameterDetail {
    pub name: String,
    pub location: String,
    pub required: bool,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub schema: Option<Value>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub example: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct RequestBodyDetail {
    pub required: bool,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    pub content_types: Vec<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub schema: Option<Value>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub example: Option<Value>,
}

#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct ResponseDetail {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    pub content_types: Vec<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub schema: Option<Value>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub example: Option<Value>,
}

/// Show operation details
#[allow(dead_code)]
pub async fn show_operation(
    request: ShowRequest,
    spec: &UnifiedSpec,
) -> Result<ShowResponse, ApiError> {
    // Find the operation
    let operation = spec
        .operations
        .iter()
        .find(|op| op.operation_id == request.operation_id)
        .ok_or_else(|| ApiError::OperationNotFound(request.operation_id.clone()))?;

    // Build parameter details
    let parameters: Vec<ParameterDetail> = operation
        .parameters
        .iter()
        .map(|param| ParameterDetail {
            name: param.name.clone(),
            location: format_parameter_location(&param),
            required: param.required,
            description: param.description.clone(),
            schema: None, // TODO: Convert UnifiedSchema to JSON Value
            example: param.example.clone(),
        })
        .collect();

    // Build request body details
    let request_body = operation.request_body.as_ref().map(|body| {
        RequestBodyDetail {
            required: body.required,
            description: body.description.clone(),
            content_types: body.content.keys().cloned().collect(),
            schema: None, // TODO: Convert UnifiedSchema to JSON Value
            example: body
                .content
                .values()
                .next()
                .and_then(|media| media.example.clone()),
        }
    });

    // Build response details
    let responses: HashMap<String, ResponseDetail> = operation
        .responses
        .iter()
        .map(|(status, response)| {
            let detail = ResponseDetail {
                description: Some(response.description.clone()),
                content_types: response.content.keys().cloned().collect(),
                schema: None,  // TODO: Convert UnifiedSchema to JSON Value
                example: None, // TODO: Extract examples
            };
            (status.clone(), detail)
        })
        .collect();

    Ok(ShowResponse {
        operation_id: operation.operation_id.clone(),
        method: operation.method.clone(),
        path: operation.path.clone(),
        summary: operation.summary.clone(),
        description: None, // TODO: Add description to UnifiedOperation
        parameters,
        request_body,
        responses,
    })
}

#[allow(dead_code)]
fn format_parameter_location(_param: &UnifiedParameter) -> String {
    // TODO: This should be extracted from the parameter definition
    // For now, return a default
    "query".to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::core::parser::UnifiedOperation;

    #[tokio::test]
    async fn test_show_operation() {
        let spec = UnifiedSpec {
            info: ApiInfo {
                title: "Test API".to_string(),
                version: "1.0.0".to_string(),
                description: None,
            },
            base_url: "https://api.example.com".to_string(),
            operations: vec![UnifiedOperation {
                operation_id: "getUser".to_string(),
                method: "GET".to_string(),
                path: "/users/{id}".to_string(),
                summary: Some("Get a user by ID".to_string()),
                description: Some("Get user details by ID".to_string()),
                parameters: vec![UnifiedParameter {
                    name: "id".to_string(),
                    location: ParameterLocation::Path,
                    required: true,
                    description: Some("User ID".to_string()),
                    schema: UnifiedSchema {
                        schema_type: SchemaType::String,
                        format: None,
                        description: None,
                        example: None,
                        default: None,
                        minimum: None,
                        maximum: None,
                        enum_values: None,
                        properties: None,
                        required: None,
                        items: None,
                    },
                    example: Some(serde_json::json!("12345")),
                }],
                request_body: None,
                responses: HashMap::new(),
                security: None,
            }],
            security_schemes: HashMap::new(),
        };

        let request = ShowRequest {
            operation_id: "getUser".to_string(),
            spec_path: None,
        };

        let response = show_operation(request, &spec).await.unwrap();
        assert_eq!(response.operation_id, "getUser");
        assert_eq!(response.method, "GET");
        assert_eq!(response.path, "/users/{id}");
        assert_eq!(response.parameters.len(), 1);
        assert_eq!(response.parameters[0].name, "id");
    }

    #[tokio::test]
    async fn test_show_operation_not_found() {
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

        let request = ShowRequest {
            operation_id: "nonexistent".to_string(),
            spec_path: None,
        };

        let result = show_operation(request, &spec).await;
        assert!(result.is_err());

        match result {
            Err(ApiError::OperationNotFound(op)) => {
                assert_eq!(op, "nonexistent");
            }
            _ => panic!("Expected OperationNotFound error"),
        }
    }
}
