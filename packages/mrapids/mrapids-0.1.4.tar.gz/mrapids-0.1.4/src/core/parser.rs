// Proper parsers for different API specification formats
// Philosophy: Use battle-tested libraries, don't reinvent the wheel

use crate::core::diagnostics::{enhance_error, yaml_parse_error, DiagnosticError};
use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use serde_yaml;
use std::collections::HashMap;

/// Generic enum for handling $ref references in OpenAPI specs
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(untagged)]
pub enum ReferenceOr<T> {
    Reference {
        #[serde(rename = "$ref")]
        reference: String,
    },
    Item(T),
}

/// OpenAPI 3.x models with proper reference handling
#[derive(Debug, Clone, Deserialize)]
pub struct OpenAPIDocument {
    #[allow(dead_code)]
    pub openapi: String,
    pub info: Info,
    pub servers: Option<Vec<Server>>,
    pub paths: HashMap<String, PathItem>,
    pub components: Option<Components>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Info {
    pub title: String,
    pub version: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Server {
    pub url: String,
    #[allow(dead_code)]
    pub description: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct PathItem {
    #[serde(rename = "$ref")]
    #[allow(dead_code)]
    pub reference: Option<String>,
    pub get: Option<Operation>,
    pub post: Option<Operation>,
    pub put: Option<Operation>,
    pub delete: Option<Operation>,
    pub patch: Option<Operation>,
    pub head: Option<Operation>,
    pub options: Option<Operation>,
    pub trace: Option<Operation>,
    pub parameters: Option<Vec<ReferenceOr<Parameter>>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Operation {
    #[serde(rename = "operationId")]
    pub operation_id: Option<String>,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub parameters: Option<Vec<ReferenceOr<Parameter>>>,
    #[serde(rename = "requestBody")]
    pub request_body: Option<ReferenceOr<RequestBody>>,
    pub responses: HashMap<String, ReferenceOr<Response>>,
    pub security: Option<Vec<HashMap<String, Vec<String>>>>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Parameter {
    pub name: String,
    #[serde(rename = "in")]
    pub location: String,
    pub required: Option<bool>,
    pub description: Option<String>,
    pub schema: Option<ReferenceOr<Schema>>,
    pub example: Option<Value>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct RequestBody {
    pub required: Option<bool>,
    pub description: Option<String>,
    pub content: HashMap<String, MediaType>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct MediaType {
    pub schema: Option<ReferenceOr<Schema>>,
    pub example: Option<Value>,
    #[allow(dead_code)]
    pub examples: Option<HashMap<String, ReferenceOr<Example>>>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Response {
    pub description: String,
    #[allow(dead_code)]
    pub content: Option<HashMap<String, MediaType>>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Schema {
    #[serde(rename = "type")]
    pub schema_type: Option<String>,
    pub format: Option<String>,
    pub description: Option<String>,
    pub properties: Option<HashMap<String, ReferenceOr<Schema>>>,
    pub required: Option<Vec<String>>,
    pub items: Option<Box<ReferenceOr<Schema>>>,
    pub example: Option<Value>,
    pub default: Option<Value>,
    pub minimum: Option<f64>,
    pub maximum: Option<f64>,
    #[serde(rename = "enum")]
    pub enum_values: Option<Vec<Value>>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[allow(dead_code)]
pub struct Example {
    pub value: Option<Value>,
    pub summary: Option<String>,
    pub description: Option<String>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct Components {
    pub schemas: Option<HashMap<String, ReferenceOr<Schema>>>,
    pub parameters: Option<HashMap<String, ReferenceOr<Parameter>>>,
    pub responses: Option<HashMap<String, ReferenceOr<Response>>>,
    #[serde(rename = "requestBodies")]
    pub request_bodies: Option<HashMap<String, ReferenceOr<RequestBody>>>,
    #[allow(dead_code)]
    pub examples: Option<HashMap<String, ReferenceOr<Example>>>,
    #[serde(rename = "securitySchemes")]
    pub security_schemes: Option<HashMap<String, ReferenceOr<OApiSecurityScheme>>>,
}

#[derive(Debug, Clone, Deserialize)]
pub struct OApiSecurityScheme {
    #[serde(rename = "type")]
    pub scheme_type: String,
    pub description: Option<String>,
    pub name: Option<String>,
    #[serde(rename = "in")]
    pub location: Option<String>,
    pub scheme: Option<String>,
}

/// SpecResolver handles reference resolution for OpenAPI specs
pub struct SpecResolver {
    components: Option<Components>,
    // Cache for resolved references to avoid repeated work
    parameter_cache: HashMap<String, Parameter>,
    schema_cache: HashMap<String, Schema>,
    request_body_cache: HashMap<String, RequestBody>,
    response_cache: HashMap<String, Response>,
    // Track circular references
    resolution_stack: Vec<String>,
    // External reference support
    external_docs: HashMap<String, Value>,
}

impl SpecResolver {
    pub fn new(components: Option<Components>) -> Self {
        Self {
            components,
            parameter_cache: HashMap::new(),
            schema_cache: HashMap::new(),
            request_body_cache: HashMap::new(),
            response_cache: HashMap::new(),
            resolution_stack: Vec::new(),
            external_docs: HashMap::new(),
        }
    }

    /// Check if we're in a circular reference loop
    fn check_circular_reference(&self, reference: &str) -> Result<()> {
        if self.resolution_stack.contains(&reference.to_string()) {
            let cycle = self.resolution_stack.join(" -> ") + " -> " + reference;
            Err(anyhow::anyhow!(
                "Circular reference detected in OpenAPI spec: {}. This creates an infinite loop.",
                cycle
            ))
        } else {
            Ok(())
        }
    }

    /// Add support for external references
    #[allow(dead_code)]
    pub fn add_external_doc(&mut self, url: &str, content: Value) {
        self.external_docs.insert(url.to_string(), content);
    }

    /// Parse reference path and determine if it's external
    fn parse_reference(&self, reference: &str) -> Result<(Option<String>, String)> {
        if reference.starts_with("http://") || reference.starts_with("https://") {
            // External HTTP reference
            if let Some(hash_pos) = reference.find('#') {
                let url = &reference[..hash_pos];
                let path = &reference[hash_pos + 1..];
                Ok((Some(url.to_string()), path.to_string()))
            } else {
                Err(anyhow::anyhow!("Invalid external reference '{}': missing fragment identifier (e.g., #/components/schemas/MySchema)", reference))
            }
        } else if reference.starts_with("../") || reference.starts_with("./") {
            // Relative file reference
            if let Some(hash_pos) = reference.find('#') {
                let file = &reference[..hash_pos];
                let path = &reference[hash_pos + 1..];
                Ok((Some(file.to_string()), path.to_string()))
            } else {
                Err(anyhow::anyhow!("Invalid file reference '{}': missing fragment identifier. Expected format: 'file.yaml#/path/to/component'", reference))
            }
        } else if reference.starts_with("#/") {
            // Internal reference
            Ok((None, reference[2..].to_string()))
        } else {
            Err(anyhow::anyhow!("Invalid reference format: '{}'. References must start with '#/' for internal or 'http://', 'https://', or be a file path for external references", reference))
        }
    }

    /// Resolve a parameter reference
    pub fn resolve_parameter(&mut self, item: &ReferenceOr<Parameter>) -> Result<Parameter> {
        match item {
            ReferenceOr::Item(p) => Ok(p.clone()),
            ReferenceOr::Reference { reference } => {
                // Check for circular reference
                self.check_circular_reference(reference)?;

                // Check cache first (memoization)
                if let Some(cached) = self.parameter_cache.get(reference) {
                    return Ok(cached.clone());
                }

                // Push to resolution stack
                self.resolution_stack.push(reference.clone());

                let result = {
                    // Parse reference to check if external
                    let (external_doc, ref_path) = self.parse_reference(reference)?;

                    if let Some(_doc_url) = external_doc {
                        // External reference handling
                        Err(anyhow::anyhow!(
                            "External parameter references not yet implemented: {}",
                            reference
                        ))
                    } else {
                        // Internal reference
                        let param_name = ref_path
                            .strip_prefix("components/parameters/")
                            .ok_or_else(|| {
                                anyhow::anyhow!("Invalid parameter reference path: {}", ref_path)
                            })?;

                        // Look up in components
                        let components = self.components.as_ref().ok_or_else(|| {
                            anyhow::anyhow!(
                                "No components section found for parameter: {}",
                                param_name
                            )
                        })?;

                        let parameters = components.parameters.as_ref()
                            .ok_or_else(|| anyhow::anyhow!("No parameters in components. Available sections: schemas={}, responses={}, requestBodies={}",
                                components.schemas.is_some(),
                                components.responses.is_some(),
                                components.request_bodies.is_some()))?;

                        let param_ref = parameters.get(param_name).ok_or_else(|| {
                            let available: Vec<String> = parameters.keys().cloned().collect();
                            anyhow::anyhow!(
                                "Parameter '{}' not found. Available parameters: {}",
                                param_name,
                                available.join(", ")
                            )
                        })?;

                        // Recursively resolve if it's another reference
                        match param_ref {
                            ReferenceOr::Item(p) => Ok(p.clone()),
                            ReferenceOr::Reference { .. } => {
                                // Clone to avoid borrow conflict
                                let param_ref_clone = param_ref.clone();
                                self.resolve_parameter(&param_ref_clone)
                            }
                        }
                    }
                };

                // Pop from resolution stack
                self.resolution_stack.pop();

                // Cache the result if successful
                if let Ok(ref resolved) = result {
                    self.parameter_cache
                        .insert(reference.clone(), resolved.clone());
                }

                result
            }
        }
    }

    /// Resolve a schema reference
    pub fn resolve_schema(&mut self, item: &ReferenceOr<Schema>) -> Result<Schema> {
        match item {
            ReferenceOr::Item(s) => Ok(s.clone()),
            ReferenceOr::Reference { reference } => {
                // Check for circular reference
                self.check_circular_reference(reference)?;

                // Check cache first (memoization)
                if let Some(cached) = self.schema_cache.get(reference) {
                    return Ok(cached.clone());
                }

                // Push to resolution stack
                self.resolution_stack.push(reference.clone());

                let result = {
                    // Parse reference to check if external
                    let (external_doc, ref_path) = self.parse_reference(reference)?;

                    if let Some(doc_url) = external_doc {
                        // External reference handling
                        if let Some(external_value) = self.external_docs.get(&doc_url) {
                            // Navigate to the path in external doc
                            let path_parts: Vec<&str> = ref_path.split('/').collect();
                            let mut current = external_value;
                            for part in path_parts {
                                current = current.get(part).ok_or_else(|| {
                                    anyhow::anyhow!(
                                        "Path '{}' not found in external document '{}'",
                                        ref_path,
                                        doc_url
                                    )
                                })?;
                            }
                            // Convert Value to Schema
                            serde_json::from_value(current.clone()).map_err(|e| {
                                anyhow::anyhow!("Failed to parse external schema: {}", e)
                            })
                        } else {
                            Err(anyhow::anyhow!("External document not loaded: {}. Use add_external_doc() to load it first.", doc_url))
                        }
                    } else {
                        // Internal reference
                        let schema_name =
                            ref_path
                                .strip_prefix("components/schemas/")
                                .ok_or_else(|| {
                                    anyhow::anyhow!("Invalid schema reference path: {}", ref_path)
                                })?;

                        // Look up in components
                        let components = self.components.as_ref().ok_or_else(|| {
                            anyhow::anyhow!(
                                "No components section found for schema: {}",
                                schema_name
                            )
                        })?;

                        let schemas = components.schemas.as_ref()
                            .ok_or_else(|| anyhow::anyhow!("No schemas in components. Available sections: parameters={}, responses={}, requestBodies={}",
                                components.parameters.is_some(),
                                components.responses.is_some(),
                                components.request_bodies.is_some()))?;

                        let schema_ref = schemas.get(schema_name).ok_or_else(|| {
                            let available: Vec<String> = schemas.keys().take(10).cloned().collect();
                            let more = if schemas.len() > 10 {
                                format!(" and {} more", schemas.len() - 10)
                            } else {
                                String::new()
                            };
                            anyhow::anyhow!(
                                "Schema '{}' not found. Available schemas: {}{}",
                                schema_name,
                                available.join(", "),
                                more
                            )
                        })?;

                        // Recursively resolve if it's another reference
                        match schema_ref {
                            ReferenceOr::Item(s) => Ok(s.clone()),
                            ReferenceOr::Reference { .. } => {
                                let schema_ref_clone = schema_ref.clone();
                                self.resolve_schema(&schema_ref_clone)
                            }
                        }
                    }
                };

                // Pop from resolution stack
                self.resolution_stack.pop();

                // Cache the result if successful
                if let Ok(ref resolved) = result {
                    self.schema_cache
                        .insert(reference.clone(), resolved.clone());
                }

                result
            }
        }
    }

    /// Resolve a request body reference
    pub fn resolve_request_body(&mut self, item: &ReferenceOr<RequestBody>) -> Result<RequestBody> {
        match item {
            ReferenceOr::Item(rb) => Ok(rb.clone()),
            ReferenceOr::Reference { reference } => {
                // Check for circular reference
                self.check_circular_reference(reference)?;

                // Check cache first (memoization)
                if let Some(cached) = self.request_body_cache.get(reference) {
                    return Ok(cached.clone());
                }

                // Push to resolution stack
                self.resolution_stack.push(reference.clone());

                let result = {
                    // Parse reference to check if external
                    let (external_doc, ref_path) = self.parse_reference(reference)?;

                    if let Some(_doc_url) = external_doc {
                        // External reference handling
                        Err(anyhow::anyhow!(
                            "External request body references not yet implemented: {}",
                            reference
                        ))
                    } else {
                        // Internal reference
                        let rb_name = ref_path
                            .strip_prefix("components/requestBodies/")
                            .ok_or_else(|| {
                                anyhow::anyhow!("Invalid request body reference path: {}", ref_path)
                            })?;

                        // Look up in components
                        let components = self.components.as_ref().ok_or_else(|| {
                            anyhow::anyhow!(
                                "No components section found for request body: {}",
                                rb_name
                            )
                        })?;

                        let request_bodies = components.request_bodies.as_ref()
                            .ok_or_else(|| anyhow::anyhow!("No request bodies in components. Try checking if your spec uses 'requestBody' (singular) instead."))?;

                        let rb_ref = request_bodies.get(rb_name).ok_or_else(|| {
                            let available: Vec<String> = request_bodies.keys().cloned().collect();
                            anyhow::anyhow!(
                                "Request body '{}' not found. Available request bodies: {}",
                                rb_name,
                                if available.is_empty() {
                                    "none".to_string()
                                } else {
                                    available.join(", ")
                                }
                            )
                        })?;

                        // Recursively resolve if it's another reference
                        match rb_ref {
                            ReferenceOr::Item(rb) => Ok(rb.clone()),
                            ReferenceOr::Reference { .. } => {
                                let rb_ref_clone = rb_ref.clone();
                                self.resolve_request_body(&rb_ref_clone)
                            }
                        }
                    }
                };

                // Pop from resolution stack
                self.resolution_stack.pop();

                // Cache the result if successful
                if let Ok(ref resolved) = result {
                    self.request_body_cache
                        .insert(reference.clone(), resolved.clone());
                }

                result
            }
        }
    }

    /// Resolve a response reference
    pub fn resolve_response(&mut self, item: &ReferenceOr<Response>) -> Result<Response> {
        match item {
            ReferenceOr::Item(r) => Ok(r.clone()),
            ReferenceOr::Reference { reference } => {
                // Check for circular reference
                self.check_circular_reference(reference)?;

                // Check cache first (memoization)
                if let Some(cached) = self.response_cache.get(reference) {
                    return Ok(cached.clone());
                }

                // Push to resolution stack
                self.resolution_stack.push(reference.clone());

                let result = {
                    // Parse reference to check if external
                    let (external_doc, ref_path) = self.parse_reference(reference)?;

                    if let Some(_doc_url) = external_doc {
                        // External reference handling
                        Err(anyhow::anyhow!(
                            "External response references not yet implemented: {}",
                            reference
                        ))
                    } else {
                        // Internal reference
                        let resp_name =
                            ref_path
                                .strip_prefix("components/responses/")
                                .ok_or_else(|| {
                                    anyhow::anyhow!("Invalid response reference path: {}", ref_path)
                                })?;

                        // Look up in components
                        let components = self.components.as_ref().ok_or_else(|| {
                            anyhow::anyhow!(
                                "No components section found for response: {}",
                                resp_name
                            )
                        })?;

                        let responses = components.responses.as_ref()
                            .ok_or_else(|| anyhow::anyhow!("No responses in components. Check if your spec defines shared responses."))?;

                        let resp_ref = responses.get(resp_name).ok_or_else(|| {
                            let available: Vec<String> = responses.keys().cloned().collect();
                            anyhow::anyhow!(
                                "Response '{}' not found. Available responses: {}",
                                resp_name,
                                if available.is_empty() {
                                    "none".to_string()
                                } else {
                                    available.join(", ")
                                }
                            )
                        })?;

                        // Recursively resolve if it's another reference
                        match resp_ref {
                            ReferenceOr::Item(r) => Ok(r.clone()),
                            ReferenceOr::Reference { .. } => {
                                let resp_ref_clone = resp_ref.clone();
                                self.resolve_response(&resp_ref_clone)
                            }
                        }
                    }
                };

                // Pop from resolution stack
                self.resolution_stack.pop();

                // Cache the result if successful
                if let Ok(ref resolved) = result {
                    self.response_cache
                        .insert(reference.clone(), resolved.clone());
                }

                result
            }
        }
    }
}

/// Unified API specification that works for our analyze/run commands
#[derive(Debug, Clone)]
pub struct UnifiedSpec {
    pub info: ApiInfo,
    pub base_url: String,
    pub operations: Vec<UnifiedOperation>,
    pub security_schemes: HashMap<String, SecurityScheme>,
}

impl UnifiedSpec {
    pub fn get_base_url(&self) -> &str {
        &self.base_url
    }
}

#[derive(Debug, Clone)]
pub struct SecurityScheme {
    pub scheme_type: String,
    #[allow(dead_code)]
    pub description: Option<String>,
    pub name: Option<String>,     // For apiKey
    pub location: Option<String>, // For apiKey (header, query, cookie)
    pub scheme: Option<String>,   // For http (bearer, basic)
    #[allow(dead_code)]
    pub flows: Option<String>, // For oauth2
}

#[derive(Debug, Clone)]
pub struct ApiInfo {
    pub title: String,
    pub version: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone)]
pub struct UnifiedOperation {
    pub operation_id: String,
    pub method: String,
    pub path: String,
    pub summary: Option<String>,
    #[allow(dead_code)]
    pub description: Option<String>,
    pub parameters: Vec<UnifiedParameter>,
    pub request_body: Option<UnifiedRequestBody>,
    pub responses: HashMap<String, UnifiedResponse>,
    pub security: Option<Vec<SecurityRequirement>>,
}

#[derive(Debug, Clone)]
pub struct SecurityRequirement {
    pub scheme_name: String,
    pub scopes: Vec<String>,
}

#[derive(Debug, Clone)]
pub struct UnifiedParameter {
    pub name: String,
    pub location: ParameterLocation,
    #[allow(dead_code)]
    pub required: bool,
    pub schema: UnifiedSchema,
    #[allow(dead_code)]
    pub description: Option<String>,
    pub example: Option<Value>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ParameterLocation {
    Path,
    Query,
    Header,
    Cookie,
}

#[derive(Debug, Clone)]
pub struct UnifiedRequestBody {
    #[allow(dead_code)]
    pub required: bool,
    pub content: HashMap<String, UnifiedMediaType>,
    #[allow(dead_code)]
    pub description: Option<String>,
}

#[derive(Debug, Clone)]
pub struct UnifiedMediaType {
    pub schema: UnifiedSchema,
    pub example: Option<Value>,
}

#[derive(Debug, Clone)]
pub struct UnifiedResponse {
    #[allow(dead_code)]
    pub description: String,
    pub content: HashMap<String, UnifiedMediaType>,
}

#[derive(Debug, Clone)]
pub struct UnifiedSchema {
    pub schema_type: SchemaType,
    pub format: Option<String>,
    pub description: Option<String>,
    pub example: Option<Value>,
    pub default: Option<Value>,
    pub minimum: Option<f64>,
    pub maximum: Option<f64>,
    pub enum_values: Option<Vec<Value>>,
    pub properties: Option<HashMap<String, UnifiedSchema>>,
    pub required: Option<Vec<String>>,
    pub items: Option<Box<UnifiedSchema>>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum SchemaType {
    String,
    Integer,
    Number,
    Boolean,
    Array,
    Object,
    Unknown,
}

impl std::fmt::Display for SchemaType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            SchemaType::String => write!(f, "string"),
            SchemaType::Integer => write!(f, "integer"),
            SchemaType::Number => write!(f, "number"),
            SchemaType::Boolean => write!(f, "boolean"),
            SchemaType::Array => write!(f, "array"),
            SchemaType::Object => write!(f, "object"),
            SchemaType::Unknown => write!(f, "unknown"),
        }
    }
}

/// Resolve parameter reference from the full spec value
pub fn parse_spec(content: &str) -> Result<UnifiedSpec> {
    // Try to detect format
    if content.contains("\"openapi\"") || content.contains("openapi:") {
        parse_openapi_v3(content).map_err(|e| {
            let diagnostic = enhance_error(e);
            diagnostic.display();
            diagnostic.error
        })
    } else if content.contains("\"swagger\"") || content.contains("swagger:") {
        parse_swagger_v2(content).map_err(|e| {
            let diagnostic = enhance_error(e);
            diagnostic.display();
            diagnostic.error
        })
    } else {
        let diagnostic = DiagnosticError::new(anyhow::anyhow!("Unknown API specification format"))
            .with_suggestion("The spec must contain either 'openapi' or 'swagger' field")
            .with_suggestion(
                "OpenAPI 3.x specs should have: openapi: '3.0.0' (or 3.0.1, 3.0.2, 3.0.3, 3.1.0)",
            )
            .with_suggestion("Swagger 2.0 specs should have: swagger: '2.0'")
            .with_suggestion("Check that your file is valid YAML or JSON");
        diagnostic.display();
        Err(diagnostic.error)
    }
}

/// Parse OpenAPI 3.x specification using two-pass approach
pub fn parse_openapi_v3(content: &str) -> Result<UnifiedSpec> {
    // eprintln!("Using two-pass parsing for OpenAPI spec...");

    // Step 1: Parse as serde_yaml::Value for better YAML handling
    let raw_value: serde_yaml::Value = serde_yaml::from_str(content).map_err(|e| {
        let diagnostic = yaml_parse_error(e, content);
        diagnostic.display();
        diagnostic.error
    })?;

    // Convert to serde_json::Value for easier manipulation
    let raw_value: Value =
        serde_json::to_value(raw_value).context("Failed to convert YAML value to JSON value")?;

    // Validate it's OpenAPI 3.x
    if !raw_value.get("openapi").is_some() {
        return Err(anyhow::anyhow!("Not an OpenAPI 3.x specification"));
    }

    // Step 2: Convert to typed structure manually
    let openapi = convert_value_to_openapi_doc(&raw_value)?;

    // eprintln!("Successfully converted to OpenAPI document with {} paths", openapi.paths.len());

    // Create resolver for handling references
    let mut resolver = SpecResolver::new(openapi.components.clone());

    // Extract API info
    let api_info = ApiInfo {
        title: openapi.info.title.clone(),
        version: openapi.info.version.clone(),
        description: openapi.info.description.clone(),
    };

    // Extract base URL from servers
    let base_url = openapi
        .servers
        .as_ref()
        .and_then(|servers| servers.first())
        .map(|server| server.url.clone())
        .unwrap_or_else(|| "http://localhost".to_string());

    // Convert operations to unified format
    let mut operations = Vec::new();

    for (path, path_item) in &openapi.paths {
        // Process path-level parameters if any
        let path_params = if let Some(params) = &path_item.parameters {
            let mut resolved = Vec::new();
            for param_ref in params {
                match resolver.resolve_parameter(param_ref) {
                    Ok(param) => resolved.push(param),
                    Err(e) => eprintln!("Warning: Failed to resolve path parameter: {}", e),
                }
            }
            resolved
        } else {
            Vec::new()
        };

        // Process each HTTP method
        let methods = [
            ("GET", &path_item.get),
            ("POST", &path_item.post),
            ("PUT", &path_item.put),
            ("DELETE", &path_item.delete),
            ("PATCH", &path_item.patch),
            ("HEAD", &path_item.head),
            ("OPTIONS", &path_item.options),
            ("TRACE", &path_item.trace),
        ];

        for (method, operation_opt) in methods {
            if let Some(operation) = operation_opt {
                let operation_id = operation
                    .operation_id
                    .clone()
                    .unwrap_or_else(|| generate_operation_id(method, path));

                // Combine path-level and operation-level parameters
                let mut all_parameters = path_params.clone();

                // Resolve operation parameters
                if let Some(op_params) = &operation.parameters {
                    for param_ref in op_params {
                        match resolver.resolve_parameter(param_ref) {
                            Ok(param) => all_parameters.push(param),
                            Err(e) => eprintln!(
                                "Warning: Failed to resolve parameter in {}: {}",
                                operation_id, e
                            ),
                        }
                    }
                }

                // Convert parameters to unified format
                let unified_params = all_parameters
                    .into_iter()
                    .filter_map(|param| convert_parameter_to_unified(&param, &mut resolver).ok())
                    .collect();

                // Resolve and convert request body
                let request_body = if let Some(rb_ref) = &operation.request_body {
                    match resolver.resolve_request_body(rb_ref) {
                        Ok(rb) => convert_request_body_to_unified(&rb, &mut resolver).ok(),
                        Err(e) => {
                            eprintln!(
                                "Warning: Failed to resolve request body in {}: {}",
                                operation_id, e
                            );
                            None
                        }
                    }
                } else {
                    None
                };

                // Convert responses (simplified for now)
                let mut unified_responses = HashMap::new();
                for (status_code, response_ref) in &operation.responses {
                    match resolver.resolve_response(response_ref) {
                        Ok(response) => {
                            unified_responses.insert(
                                status_code.clone(),
                                UnifiedResponse {
                                    description: response.description.clone(),
                                    content: HashMap::new(), // TODO: Convert media types
                                },
                            );
                        }
                        Err(e) => {
                            eprintln!(
                                "Warning: Failed to resolve response {} in {}: {}",
                                status_code, operation_id, e
                            );
                        }
                    }
                }

                // Convert security requirements
                let security = operation.security.as_ref().map(|sec| {
                    sec.iter()
                        .flat_map(|sec_req| {
                            sec_req.iter().map(|(name, scopes)| SecurityRequirement {
                                scheme_name: name.clone(),
                                scopes: scopes.clone(),
                            })
                        })
                        .collect()
                });

                // Create unified operation
                operations.push(UnifiedOperation {
                    operation_id,
                    method: method.to_string(),
                    path: path.clone(),
                    summary: operation.summary.clone(),
                    description: operation.description.clone(),
                    parameters: unified_params,
                    request_body,
                    responses: unified_responses,
                    security,
                });
            }
        }
    }

    // Extract security schemes
    let mut security_schemes = HashMap::new();
    if let Some(components) = &openapi.components {
        if let Some(schemes) = &components.security_schemes {
            for (name, scheme_ref) in schemes {
                match scheme_ref {
                    ReferenceOr::Item(scheme) => {
                        security_schemes.insert(
                            name.clone(),
                            SecurityScheme {
                                scheme_type: scheme.scheme_type.clone(),
                                description: scheme.description.clone(),
                                name: scheme.name.clone(),
                                location: scheme.location.clone(),
                                scheme: scheme.scheme.clone(),
                                flows: None,
                            },
                        );
                    }
                    ReferenceOr::Reference { reference } => {
                        eprintln!(
                            "Warning: Security scheme reference not yet supported: {}",
                            reference
                        );
                    }
                }
            }
        }
    }

    Ok(UnifiedSpec {
        info: api_info,
        base_url,
        operations,
        security_schemes,
    })
}

/// Generic utility to convert a Value to ReferenceOr<T>
fn convert_value_to_ref_or<T, F>(value: &Value, convert_fn: F) -> Result<ReferenceOr<T>>
where
    T: Clone,
    F: FnOnce(&Value) -> Result<T>,
{
    // Check if it's a reference
    if let Some(reference) = value.get("$ref").and_then(|v| v.as_str()) {
        Ok(ReferenceOr::Reference {
            reference: reference.to_string(),
        })
    } else {
        // Convert to the actual type
        Ok(ReferenceOr::Item(convert_fn(value)?))
    }
}

// Note: Keeping this utility for future use when we need to convert entire arrays
// /// Convert an array of Values to Vec<ReferenceOr<T>>
// fn convert_vec_of_value_to_ref_or<T, F>(values: &[Value], convert_fn: F) -> Result<Vec<ReferenceOr<T>>>
// where
//     T: Clone,
//     F: Fn(&Value) -> Result<T>,
// {
//     values.iter()
//         .map(|v| convert_value_to_ref_or(v, &convert_fn))
//         .collect()
// }

/// Convert a JSON Value to OpenAPIDocument with proper reference handling
fn convert_value_to_openapi_doc(value: &Value) -> Result<OpenAPIDocument> {
    // Extract basic info
    let openapi = value
        .get("openapi")
        .and_then(|v| v.as_str())
        .ok_or_else(|| anyhow::anyhow!("Missing openapi version"))?
        .to_string();

    // Convert info section
    let info = convert_value_to_info(
        value
            .get("info")
            .ok_or_else(|| anyhow::anyhow!("Missing info section"))?,
    )?;

    // Convert servers
    let servers = value
        .get("servers")
        .and_then(|v| v.as_array())
        .map(|arr| {
            arr.iter()
                .filter_map(|s| convert_value_to_server(s).ok())
                .collect()
        })
        .unwrap_or_default();

    // Convert paths with reference handling
    let paths = convert_value_to_paths(
        value
            .get("paths")
            .ok_or_else(|| anyhow::anyhow!("Missing paths section"))?,
    )?;

    // Convert components if present
    let components = value
        .get("components")
        .map(|c| convert_value_to_components(c))
        .transpose()?;

    Ok(OpenAPIDocument {
        openapi,
        info,
        servers: Some(servers),
        paths,
        components,
    })
}

/// Convert Value to Info
fn convert_value_to_info(value: &Value) -> Result<Info> {
    Ok(Info {
        title: value
            .get("title")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow::anyhow!("Missing title in info"))?
            .to_string(),
        version: value
            .get("version")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow::anyhow!("Missing version in info"))?
            .to_string(),
        description: value
            .get("description")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
    })
}

/// Convert Value to Server
fn convert_value_to_server(value: &Value) -> Result<Server> {
    Ok(Server {
        url: value
            .get("url")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow::anyhow!("Missing url in server"))?
            .to_string(),
        description: value
            .get("description")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
    })
}

/// Convert Value to paths map
fn convert_value_to_paths(value: &Value) -> Result<HashMap<String, PathItem>> {
    let paths_obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Paths must be an object"))?;

    let mut paths = HashMap::new();
    for (path, path_value) in paths_obj {
        let path_item = convert_value_to_path_item(path_value)?;
        paths.insert(path.clone(), path_item);
    }

    Ok(paths)
}

/// Convert Value to PathItem
fn convert_value_to_path_item(value: &Value) -> Result<PathItem> {
    let obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Path item must be an object"))?;

    Ok(PathItem {
        reference: obj
            .get("$ref")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        get: obj
            .get("get")
            .and_then(|v| convert_value_to_operation(v).ok()),
        post: obj
            .get("post")
            .and_then(|v| convert_value_to_operation(v).ok()),
        put: obj
            .get("put")
            .and_then(|v| convert_value_to_operation(v).ok()),
        delete: obj
            .get("delete")
            .and_then(|v| convert_value_to_operation(v).ok()),
        patch: obj
            .get("patch")
            .and_then(|v| convert_value_to_operation(v).ok()),
        head: obj
            .get("head")
            .and_then(|v| convert_value_to_operation(v).ok()),
        options: obj
            .get("options")
            .and_then(|v| convert_value_to_operation(v).ok()),
        trace: obj
            .get("trace")
            .and_then(|v| convert_value_to_operation(v).ok()),
        parameters: obj
            .get("parameters")
            .and_then(|v| v.as_array())
            .map(|arr| convert_array_to_reference_or_parameters(arr)),
    })
}

/// Convert Value to Operation
fn convert_value_to_operation(value: &Value) -> Result<Operation> {
    let obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Operation must be an object"))?;

    Ok(Operation {
        operation_id: obj
            .get("operationId")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        summary: obj
            .get("summary")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        description: obj
            .get("description")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        parameters: obj
            .get("parameters")
            .and_then(|v| v.as_array())
            .map(|arr| convert_array_to_reference_or_parameters(arr)),
        request_body: obj
            .get("requestBody")
            .map(|v| convert_value_to_reference_or_request_body(v))
            .transpose()?,
        responses: obj
            .get("responses")
            .and_then(|v| v.as_object())
            .map(|resp_obj| {
                let mut responses = HashMap::new();
                for (status, resp_value) in resp_obj {
                    if let Ok(resp) = convert_value_to_reference_or_response(resp_value) {
                        responses.insert(status.clone(), resp);
                    }
                }
                responses
            })
            .unwrap_or_default(),
        security: obj.get("security").and_then(|v| v.as_array()).map(|arr| {
            arr.iter()
                .filter_map(|v| v.as_object())
                .map(|obj| {
                    obj.iter()
                        .map(|(k, v)| {
                            (
                                k.clone(),
                                v.as_array()
                                    .map(|a| {
                                        a.iter()
                                            .filter_map(|s| s.as_str().map(|s| s.to_string()))
                                            .collect()
                                    })
                                    .unwrap_or_default(),
                            )
                        })
                        .collect()
                })
                .collect()
        }),
    })
}

/// Convert array of Values to Vec<ReferenceOr<Parameter>> for OpenAPI
fn convert_array_to_reference_or_parameters(arr: &Vec<Value>) -> Vec<ReferenceOr<Parameter>> {
    arr.iter()
        .filter_map(|v| {
            match convert_value_to_ref_or(v, |val| {
                serde_json::from_value::<Parameter>(val.clone())
                    .context("Failed to parse parameter")
            }) {
                Ok(ref_or_param) => Some(ref_or_param),
                Err(e) => {
                    eprintln!("Warning: Failed to parse parameter: {}", e);
                    None
                }
            }
        })
        .collect()
}

/// Convert array of Values to Vec<ReferenceOr<swagger::Parameter>> for Swagger
fn convert_array_to_reference_or_swagger_parameters(
    arr: &Vec<Value>,
) -> Vec<ReferenceOr<crate::core::swagger::Parameter>> {
    arr.iter()
        .filter_map(|v| {
            match convert_value_to_ref_or(v, |val| {
                serde_json::from_value::<crate::core::swagger::Parameter>(val.clone())
                    .context("Failed to parse swagger parameter")
            }) {
                Ok(ref_or_param) => Some(ref_or_param),
                Err(e) => {
                    eprintln!("Warning: Failed to parse swagger parameter: {}", e);
                    None
                }
            }
        })
        .collect()
}

/// Convert Value to ReferenceOr<RequestBody>
fn convert_value_to_reference_or_request_body(value: &Value) -> Result<ReferenceOr<RequestBody>> {
    convert_value_to_ref_or(value, |val| {
        serde_json::from_value::<RequestBody>(val.clone()).context("Failed to parse request body")
    })
}

/// Convert Value to ReferenceOr<Response>
fn convert_value_to_reference_or_response(value: &Value) -> Result<ReferenceOr<Response>> {
    convert_value_to_ref_or(value, |val| {
        serde_json::from_value::<Response>(val.clone()).context("Failed to parse response")
    })
}

/// Convert Value to Components
fn convert_value_to_components(value: &Value) -> Result<Components> {
    let obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Components must be an object"))?;

    Ok(Components {
        schemas: obj
            .get("schemas")
            .and_then(|v| v.as_object())
            .map(|schemas_obj| {
                convert_map_to_reference_or(schemas_obj, |v| {
                    serde_json::from_value::<Schema>(v.clone()).context("Failed to parse schema")
                })
            }),
        parameters: obj
            .get("parameters")
            .and_then(|v| v.as_object())
            .map(|params_obj| {
                convert_map_to_reference_or(params_obj, |v| {
                    serde_json::from_value::<Parameter>(v.clone())
                        .context("Failed to parse parameter")
                })
            }),
        responses: obj
            .get("responses")
            .and_then(|v| v.as_object())
            .map(|resp_obj| {
                convert_map_to_reference_or(resp_obj, |v| {
                    serde_json::from_value::<Response>(v.clone())
                        .context("Failed to parse response")
                })
            }),
        request_bodies: obj
            .get("requestBodies")
            .and_then(|v| v.as_object())
            .map(|rb_obj| {
                convert_map_to_reference_or(rb_obj, |v| {
                    serde_json::from_value::<RequestBody>(v.clone())
                        .context("Failed to parse request body")
                })
            }),
        examples: obj
            .get("examples")
            .and_then(|v| v.as_object())
            .map(|ex_obj| {
                convert_map_to_reference_or(ex_obj, |v| {
                    serde_json::from_value::<Example>(v.clone()).context("Failed to parse example")
                })
            }),
        security_schemes: obj
            .get("securitySchemes")
            .and_then(|v| v.as_object())
            .map(|ss_obj| {
                convert_map_to_reference_or(ss_obj, |v| {
                    serde_json::from_value::<OApiSecurityScheme>(v.clone())
                        .context("Failed to parse security scheme")
                })
            }),
    })
}

/// Generic function to convert a map of Values to HashMap<String, ReferenceOr<T>>
fn convert_map_to_reference_or<T, F>(
    map: &serde_json::Map<String, Value>,
    converter: F,
) -> HashMap<String, ReferenceOr<T>>
where
    F: Fn(&Value) -> Result<T>,
    T: Clone,
{
    let mut result = HashMap::new();
    for (key, value) in map {
        match convert_value_to_ref_or(value, |v| converter(v)) {
            Ok(ref_or_item) => {
                result.insert(key.clone(), ref_or_item);
            }
            Err(e) => {
                eprintln!("Warning: Failed to convert {} - {}", key, e);
            }
        }
    }
    result
}

/// Convert OpenAPI parameter to unified format
fn convert_parameter_to_unified(
    param: &Parameter,
    resolver: &mut SpecResolver,
) -> Result<UnifiedParameter> {
    let location = match param.location.as_str() {
        "path" => ParameterLocation::Path,
        "query" => ParameterLocation::Query,
        "header" => ParameterLocation::Header,
        "cookie" => ParameterLocation::Cookie,
        _ => {
            return Err(anyhow::anyhow!(
                "Unknown parameter location: {}",
                param.location
            ))
        }
    };

    // Resolve schema if it's a reference
    let schema = if let Some(schema_ref) = &param.schema {
        match resolver.resolve_schema(schema_ref) {
            Ok(s) => convert_schema_to_unified(&s, resolver)?,
            Err(e) => {
                eprintln!(
                    "Warning: Failed to resolve schema for parameter {}: {}",
                    param.name, e
                );
                // Provide a default schema
                UnifiedSchema {
                    schema_type: SchemaType::String,
                    format: None,
                    description: None,
                    example: None,
                    default: None,
                    minimum: None,
                    maximum: None,
                    enum_values: None,
                    items: None,
                    properties: None,
                    required: None,
                }
            }
        }
    } else {
        // Default schema if none provided
        UnifiedSchema {
            schema_type: SchemaType::String,
            format: None,
            description: None,
            example: None,
            default: None,
            minimum: None,
            maximum: None,
            enum_values: None,
            items: None,
            properties: None,
            required: None,
        }
    };

    Ok(UnifiedParameter {
        name: param.name.clone(),
        location,
        required: param.required.unwrap_or(false),
        schema,
        description: param.description.clone(),
        example: param.example.clone(),
    })
}

/// Convert OpenAPI schema to unified format
fn convert_schema_to_unified(
    schema: &Schema,
    resolver: &mut SpecResolver,
) -> Result<UnifiedSchema> {
    let schema_type = schema
        .schema_type
        .as_ref()
        .map(|t| match t.as_str() {
            "string" => SchemaType::String,
            "integer" => SchemaType::Integer,
            "number" => SchemaType::Number,
            "boolean" => SchemaType::Boolean,
            "array" => SchemaType::Array,
            "object" => SchemaType::Object,
            _ => SchemaType::Unknown,
        })
        .unwrap_or(SchemaType::Unknown);

    // Handle array items
    let items = if schema_type == SchemaType::Array {
        if let Some(items_ref) = &schema.items {
            match resolver.resolve_schema(items_ref) {
                Ok(item_schema) => {
                    Some(Box::new(convert_schema_to_unified(&item_schema, resolver)?))
                }
                Err(e) => {
                    eprintln!("Warning: Failed to resolve array items: {}", e);
                    None
                }
            }
        } else {
            None
        }
    } else {
        None
    };

    // Handle object properties
    let properties = if schema_type == SchemaType::Object {
        if let Some(props) = &schema.properties {
            let mut unified_props = HashMap::new();
            for (prop_name, prop_ref) in props {
                match resolver.resolve_schema(prop_ref) {
                    Ok(prop_schema) => {
                        if let Ok(unified_prop) = convert_schema_to_unified(&prop_schema, resolver)
                        {
                            unified_props.insert(prop_name.clone(), unified_prop);
                        }
                    }
                    Err(e) => {
                        eprintln!("Warning: Failed to resolve property {}: {}", prop_name, e);
                    }
                }
            }
            if !unified_props.is_empty() {
                Some(unified_props)
            } else {
                None
            }
        } else {
            None
        }
    } else {
        None
    };

    Ok(UnifiedSchema {
        schema_type,
        format: schema.format.clone(),
        description: schema.description.clone(),
        example: schema.example.clone(),
        default: schema.default.clone(),
        minimum: schema.minimum,
        maximum: schema.maximum,
        enum_values: schema.enum_values.clone(),
        items,
        properties,
        required: schema.required.clone(),
    })
}

/// Convert OpenAPI request body to unified format
fn convert_request_body_to_unified(
    rb: &RequestBody,
    resolver: &mut SpecResolver,
) -> Result<UnifiedRequestBody> {
    let mut content = HashMap::new();

    for (media_type, media_type_obj) in &rb.content {
        let schema = if let Some(schema_ref) = &media_type_obj.schema {
            match resolver.resolve_schema(schema_ref) {
                Ok(s) => convert_schema_to_unified(&s, resolver)?,
                Err(e) => {
                    eprintln!(
                        "Warning: Failed to resolve schema for media type {}: {}",
                        media_type, e
                    );
                    // Provide a default schema
                    UnifiedSchema {
                        schema_type: SchemaType::Unknown,
                        format: None,
                        description: None,
                        example: None,
                        default: None,
                        minimum: None,
                        maximum: None,
                        enum_values: None,
                        items: None,
                        properties: None,
                        required: None,
                    }
                }
            }
        } else {
            // Default schema
            UnifiedSchema {
                schema_type: SchemaType::Unknown,
                format: None,
                description: None,
                example: None,
                default: None,
                minimum: None,
                maximum: None,
                enum_values: None,
                items: None,
                properties: None,
                required: None,
            }
        };

        content.insert(
            media_type.clone(),
            UnifiedMediaType {
                schema,
                example: media_type_obj.example.clone(),
            },
        );
    }

    Ok(UnifiedRequestBody {
        required: rb.required.unwrap_or(false),
        content,
        description: rb.description.clone(),
    })
}

/// Convert a JSON Value to SwaggerSpec with proper reference handling
fn convert_swagger_spec(value: &Value) -> Result<crate::core::swagger::SwaggerSpec> {
    use crate::core::swagger::{Info, SwaggerSpec};

    let obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Swagger spec must be an object"))?;

    // Extract basic info
    let swagger = obj
        .get("swagger")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());

    let info = obj
        .get("info")
        .ok_or_else(|| anyhow::anyhow!("Missing info section"))?;
    let info =
        serde_json::from_value::<Info>(info.clone()).context("Failed to parse info section")?;

    // Extract other fields
    let host = obj
        .get("host")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());

    let base_path = obj
        .get("basePath")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());

    let schemes = obj.get("schemes").and_then(|v| v.as_array()).map(|arr| {
        arr.iter()
            .filter_map(|v| v.as_str().map(|s| s.to_string()))
            .collect()
    });

    // Convert paths with proper parameter reference handling
    let paths_value = obj
        .get("paths")
        .ok_or_else(|| anyhow::anyhow!("Missing paths section"))?;
    let paths_obj = paths_value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Paths must be an object"))?;

    let mut paths = HashMap::new();
    for (path, path_value) in paths_obj {
        let path_item = convert_swagger_path_item(path_value)?;
        paths.insert(path.clone(), path_item);
    }

    // Extract parameter definitions
    let parameters = obj
        .get("parameters")
        .and_then(|v| v.as_object())
        .map(|params_obj| {
            let mut params = HashMap::new();
            for (name, param_value) in params_obj {
                if let Ok(param) =
                    serde_json::from_value::<crate::core::swagger::Parameter>(param_value.clone())
                {
                    params.insert(name.clone(), param);
                }
            }
            params
        });

    // Extract definitions
    let definitions = obj
        .get("definitions")
        .and_then(|v| v.as_object())
        .map(|defs| {
            let mut hashmap = HashMap::new();
            for (k, v) in defs {
                hashmap.insert(k.clone(), v.clone());
            }
            hashmap
        });

    Ok(SwaggerSpec {
        swagger,
        openapi: None,
        info,
        host,
        base_path,
        schemes,
        paths,
        servers: None,
        parameters,
        definitions,
    })
}

/// Convert Swagger PathItem with reference handling
fn convert_swagger_path_item(value: &Value) -> Result<crate::core::swagger::PathItem> {
    let obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Path item must be an object"))?;

    Ok(crate::core::swagger::PathItem {
        get: obj
            .get("get")
            .and_then(|v| convert_swagger_operation(v).ok()),
        post: obj
            .get("post")
            .and_then(|v| convert_swagger_operation(v).ok()),
        put: obj
            .get("put")
            .and_then(|v| convert_swagger_operation(v).ok()),
        delete: obj
            .get("delete")
            .and_then(|v| convert_swagger_operation(v).ok()),
        patch: obj
            .get("patch")
            .and_then(|v| convert_swagger_operation(v).ok()),
        head: obj
            .get("head")
            .and_then(|v| convert_swagger_operation(v).ok()),
        options: obj
            .get("options")
            .and_then(|v| convert_swagger_operation(v).ok()),
        trace: obj
            .get("trace")
            .and_then(|v| convert_swagger_operation(v).ok()),
    })
}

/// Convert Swagger Operation with parameter reference handling
fn convert_swagger_operation(value: &Value) -> Result<crate::core::swagger::Operation> {
    let obj = value
        .as_object()
        .ok_or_else(|| anyhow::anyhow!("Operation must be an object"))?;

    // Convert parameters array to handle references
    let parameters = obj
        .get("parameters")
        .and_then(|v| v.as_array())
        .map(|arr| convert_array_to_reference_or_swagger_parameters(arr));

    Ok(crate::core::swagger::Operation {
        operation_id: obj
            .get("operationId")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        summary: obj
            .get("summary")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        description: obj
            .get("description")
            .and_then(|v| v.as_str())
            .map(|s| s.to_string()),
        parameters,
        request_body: obj.get("requestBody").cloned(),
        responses: obj
            .get("responses")
            .and_then(|v| v.as_object())
            .map(|resp_obj| {
                let mut responses = HashMap::new();
                for (status, resp_value) in resp_obj {
                    responses.insert(status.clone(), resp_value.clone());
                }
                responses
            }),
    })
}

/// Resolve Swagger parameter references
fn resolve_swagger_parameters(
    params: &Vec<ReferenceOr<crate::core::swagger::Parameter>>,
    global_params: &Option<HashMap<String, crate::core::swagger::Parameter>>,
) -> Vec<crate::core::swagger::Parameter> {
    let mut resolved = Vec::new();

    for param_ref in params {
        match param_ref {
            ReferenceOr::Item(param) => {
                resolved.push(param.clone());
            }
            ReferenceOr::Reference { reference } => {
                // Extract parameter name from reference
                // Format: "#/parameters/paramName"
                if let Some(param_name) = reference.strip_prefix("#/parameters/") {
                    if let Some(params_map) = global_params {
                        if let Some(param) = params_map.get(param_name) {
                            resolved.push(param.clone());
                        } else {
                            eprintln!("Warning: Parameter not found: {}", param_name);
                        }
                    }
                } else {
                    eprintln!("Warning: Invalid parameter reference: {}", reference);
                }
            }
        }
    }

    resolved
}

pub fn parse_swagger_v2(content: &str) -> Result<UnifiedSpec> {
    // Parse the raw JSON/YAML to handle definitions
    let spec_value: Value = serde_json::from_str(content)
        .or_else(|_| serde_yaml::from_str(content))
        .context("Failed to parse Swagger 2.0 JSON/YAML")?;

    // For Swagger 2.0, we need to handle parameter references differently
    // Try to parse with our two-pass approach similar to OpenAPI
    let swagger = convert_swagger_spec(&spec_value)?;

    // Convert to unified format
    let base_url = swagger.get_base_url();
    let mut operations = Vec::new();

    // Extract definitions for reference resolution
    let definitions = spec_value.get("definitions");

    for (path, path_item) in &swagger.paths {
        let ops = [
            ("GET", &path_item.get),
            ("POST", &path_item.post),
            ("PUT", &path_item.put),
            ("DELETE", &path_item.delete),
            ("PATCH", &path_item.patch),
        ];

        for (method, op) in ops {
            if let Some(operation) = op {
                // Extract body parameter and convert to request body
                let mut request_body = None;
                let mut regular_params = Vec::new();

                if let Some(params) = &operation.parameters {
                    // First resolve all parameter references
                    let resolved_params = resolve_swagger_parameters(params, &swagger.parameters);

                    for param in &resolved_params {
                        if param.location == "body" {
                            // This is a body parameter - extract schema
                            if let Some(schema_value) = &param.schema {
                                // Resolve $ref if present
                                let resolved_schema =
                                    resolve_swagger_ref(schema_value, definitions);
                                let schema = convert_swagger_schema_value(&resolved_schema)?;

                                request_body = Some(UnifiedRequestBody {
                                    required: param.required.unwrap_or(true),
                                    content: {
                                        let mut content = HashMap::new();
                                        content.insert(
                                            "application/json".to_string(),
                                            UnifiedMediaType {
                                                schema,
                                                example: None,
                                            },
                                        );
                                        content
                                    },
                                    description: None,
                                });
                            }
                        } else {
                            // Regular parameter (path, query, header)
                            regular_params.push(param.clone());
                        }
                    }
                }

                operations.push(UnifiedOperation {
                    operation_id: operation
                        .operation_id
                        .clone()
                        .unwrap_or_else(|| generate_operation_id(method, path)),
                    method: method.to_string(),
                    path: path.clone(),
                    summary: operation.summary.clone(),
                    description: operation.description.clone(),
                    parameters: convert_swagger_parameters(&regular_params),
                    request_body,
                    responses: HashMap::new(), // TODO: Convert responses with schema resolution
                    security: None,            // TODO: Extract from Swagger 2.0 security
                });
            }
        }
    }

    Ok(UnifiedSpec {
        info: ApiInfo {
            title: swagger.info.title,
            version: swagger.info.version,
            description: swagger.info.description,
        },
        base_url,
        operations,
        security_schemes: HashMap::new(), // TODO: Extract from Swagger 2.0 securityDefinitions
    })
}

/// Convert Swagger 2.0 parameters to unified format
fn convert_swagger_parameters(
    params: &Vec<crate::core::swagger::Parameter>,
) -> Vec<UnifiedParameter> {
    let mut result = Vec::new();

    for param in params {
        let location = match param.location.as_str() {
            "path" => ParameterLocation::Path,
            "query" => ParameterLocation::Query,
            "header" => ParameterLocation::Header,
            _ => ParameterLocation::Query,
        };

        let schema_type = match param.param_type.as_deref() {
            Some("string") => SchemaType::String,
            Some("integer") => SchemaType::Integer,
            Some("number") => SchemaType::Number,
            Some("boolean") => SchemaType::Boolean,
            Some("array") => SchemaType::Array,
            Some("object") => SchemaType::Object,
            _ => SchemaType::String,
        };

        result.push(UnifiedParameter {
            name: param.name.clone(),
            location,
            required: param.required.unwrap_or(false),
            schema: UnifiedSchema {
                schema_type,
                ..Default::default()
            },
            description: None,
            example: None,
        });
    }

    result
}

/// Default implementation for UnifiedSchema
impl Default for UnifiedSchema {
    fn default() -> Self {
        UnifiedSchema {
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
        }
    }
}

/// Generate a valid operation ID from HTTP method and path
fn generate_operation_id(method: &str, path: &str) -> String {
    let mut result = method.to_lowercase();

    // Split path and build the operation ID
    let path_segments: Vec<&str> = path.split('/').filter(|s| !s.is_empty()).collect();

    for segment in path_segments {
        if segment.starts_with('{') && segment.ends_with('}') {
            // Path parameter like {id} becomes "ById"
            result.push_str("By");
            let param_name = &segment[1..segment.len() - 1];
            result.push_str(&to_pascal_case(param_name));
        } else {
            // Regular path segment
            result.push_str(&to_pascal_case(segment));
        }
    }

    result
}

/// Convert string to PascalCase
fn to_pascal_case(s: &str) -> String {
    s.split(|c: char| !c.is_alphanumeric())
        .filter(|s| !s.is_empty())
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                None => String::new(),
                Some(first) => {
                    first.to_uppercase().collect::<String>()
                        + chars.as_str().to_lowercase().as_str()
                }
            }
        })
        .collect()
}

/// Resolve Swagger 2.0 $ref references
fn resolve_swagger_ref(schema_value: &Value, definitions: Option<&Value>) -> Value {
    if let Some(ref_str) = schema_value.get("$ref").and_then(|v| v.as_str()) {
        // Extract definition name from #/definitions/Name
        if let Some(def_name) = ref_str.strip_prefix("#/definitions/") {
            if let Some(defs) = definitions {
                if let Some(definition) = defs.get(def_name) {
                    return definition.clone();
                }
            }
        }
    }
    schema_value.clone()
}

/// Convert Swagger 2.0 schema JSON value to UnifiedSchema
fn convert_swagger_schema_value(schema_value: &Value) -> Result<UnifiedSchema> {
    let mut unified = UnifiedSchema::default();

    // Extract type
    if let Some(type_str) = schema_value.get("type").and_then(|v| v.as_str()) {
        unified.schema_type = match type_str {
            "string" => SchemaType::String,
            "integer" => SchemaType::Integer,
            "number" => SchemaType::Number,
            "boolean" => SchemaType::Boolean,
            "array" => SchemaType::Array,
            "object" => SchemaType::Object,
            _ => SchemaType::Unknown,
        };
    }

    // Extract format
    unified.format = schema_value
        .get("format")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());

    // Extract common fields
    unified.example = schema_value.get("example").cloned();
    unified.description = schema_value
        .get("description")
        .and_then(|v| v.as_str())
        .map(|s| s.to_string());
    unified.default = schema_value.get("default").cloned();
    unified.minimum = schema_value.get("minimum").and_then(|v| v.as_f64());
    unified.maximum = schema_value.get("maximum").and_then(|v| v.as_f64());

    // Extract enum values
    if let Some(enum_array) = schema_value.get("enum").and_then(|v| v.as_array()) {
        unified.enum_values = Some(enum_array.clone());
    }

    // Handle object properties
    if unified.schema_type == SchemaType::Object {
        if let Some(props_value) = schema_value.get("properties") {
            if let Some(props_obj) = props_value.as_object() {
                let mut properties = HashMap::new();
                for (name, prop_value) in props_obj {
                    properties.insert(name.clone(), convert_swagger_schema_value(prop_value)?);
                }
                unified.properties = Some(properties);
            }
        }

        // Extract required fields
        if let Some(req_array) = schema_value.get("required").and_then(|v| v.as_array()) {
            unified.required = Some(
                req_array
                    .iter()
                    .filter_map(|v| v.as_str().map(|s| s.to_string()))
                    .collect(),
            );
        }
    }

    // Handle array items
    if unified.schema_type == SchemaType::Array {
        if let Some(items_value) = schema_value.get("items") {
            unified.items = Some(Box::new(convert_swagger_schema_value(items_value)?));
        }
    }

    Ok(unified)
}
