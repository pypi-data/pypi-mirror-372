use crate::core::parser::ReferenceOr;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SwaggerSpec {
    pub swagger: Option<String>,
    pub openapi: Option<String>,
    pub info: Info,
    pub host: Option<String>,
    #[serde(rename = "basePath")]
    pub base_path: Option<String>,
    pub schemes: Option<Vec<String>>,
    pub paths: HashMap<String, PathItem>,
    pub servers: Option<Vec<Server>>,
    pub parameters: Option<HashMap<String, Parameter>>,
    pub definitions: Option<HashMap<String, Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Info {
    pub title: String,
    pub version: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Server {
    pub url: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PathItem {
    pub get: Option<Operation>,
    pub post: Option<Operation>,
    pub put: Option<Operation>,
    pub delete: Option<Operation>,
    pub patch: Option<Operation>,
    pub head: Option<Operation>,
    pub options: Option<Operation>,
    pub trace: Option<Operation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Operation {
    #[serde(rename = "operationId")]
    pub operation_id: Option<String>,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub parameters: Option<Vec<ReferenceOr<Parameter>>>,
    #[serde(rename = "requestBody")]
    pub request_body: Option<Value>,
    pub responses: Option<HashMap<String, Value>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Parameter {
    pub name: String,
    #[serde(rename = "in")]
    pub location: String,
    pub required: Option<bool>,
    #[serde(rename = "type")]
    pub param_type: Option<String>,
    pub schema: Option<Value>,
}

impl SwaggerSpec {
    #[allow(dead_code)]
    pub fn is_swagger_2(&self) -> bool {
        self.swagger.is_some()
    }

    pub fn is_openapi_3(&self) -> bool {
        self.openapi.is_some()
    }

    pub fn get_base_url(&self) -> String {
        if self.is_openapi_3() {
            // Use servers for OpenAPI 3.0
            self.servers
                .as_ref()
                .and_then(|s| s.first())
                .map(|s| s.url.clone())
                .unwrap_or_else(|| "http://localhost:8080".to_string())
        } else {
            // Build URL from host, basePath, and schemes for Swagger 2.0
            let scheme = self
                .schemes
                .as_ref()
                .and_then(|s| s.first())
                .unwrap_or(&"https".to_string())
                .clone();
            let host = self.host.as_deref().unwrap_or("localhost");
            let base_path = self.base_path.as_deref().unwrap_or("");
            format!("{}://{}{}", scheme, host, base_path)
        }
    }

    #[allow(dead_code)]
    pub fn find_operation_by_id(&self, operation_id: &str) -> Option<(String, String, &Operation)> {
        for (path, path_item) in &self.paths {
            let operations = [
                ("GET", &path_item.get),
                ("POST", &path_item.post),
                ("PUT", &path_item.put),
                ("DELETE", &path_item.delete),
                ("PATCH", &path_item.patch),
                ("HEAD", &path_item.head),
                ("OPTIONS", &path_item.options),
                ("TRACE", &path_item.trace),
            ];

            for (method, op) in operations {
                if let Some(operation) = op {
                    if operation.operation_id.as_deref() == Some(operation_id) {
                        return Some((path.clone(), method.to_string(), operation));
                    }
                }
            }
        }
        None
    }

    #[allow(dead_code)]
    pub fn find_operation_by_path_method(&self, path: &str, method: &str) -> Option<&Operation> {
        self.paths
            .get(path)
            .and_then(|path_item| match method.to_uppercase().as_str() {
                "GET" => path_item.get.as_ref(),
                "POST" => path_item.post.as_ref(),
                "PUT" => path_item.put.as_ref(),
                "DELETE" => path_item.delete.as_ref(),
                "PATCH" => path_item.patch.as_ref(),
                "HEAD" => path_item.head.as_ref(),
                "OPTIONS" => path_item.options.as_ref(),
                "TRACE" => path_item.trace.as_ref(),
                _ => None,
            })
    }

    #[allow(dead_code)]
    pub fn list_operations(&self) -> Vec<String> {
        let mut operations = Vec::new();

        for (path, path_item) in &self.paths {
            let ops = [
                ("GET", &path_item.get),
                ("POST", &path_item.post),
                ("PUT", &path_item.put),
                ("DELETE", &path_item.delete),
                ("PATCH", &path_item.patch),
            ];

            for (method, op) in ops {
                if let Some(operation) = op {
                    if let Some(id) = &operation.operation_id {
                        operations.push(format!("{} ({})", id, method));
                    } else {
                        operations.push(format!("{} {}", method, path));
                    }
                }
            }
        }

        operations
    }
}
