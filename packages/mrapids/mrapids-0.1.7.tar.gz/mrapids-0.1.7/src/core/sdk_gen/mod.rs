use crate::cli::SdkLanguage;
use crate::core::parser::UnifiedSpec;
use anyhow::Result;
use std::path::PathBuf;

// Internal command structure for SDK generation
pub struct SdkCommand {
    pub spec: PathBuf,
    #[allow(dead_code)]
    pub lang: SdkLanguage,
    pub output: PathBuf,
    pub package_name: Option<String>,
    pub http_client: Option<String>,
    pub auth: bool,
    pub pagination: bool,
    pub resilience: bool,
    #[allow(dead_code)]
    pub docs: bool,
    #[allow(dead_code)]
    pub examples: bool,
}

pub mod go;
pub mod python;
pub mod rust_gen;
mod template_engine;
pub mod typescript;

pub use template_engine::TemplateEngine;

/// Represents the normalized view of the spec for template generation
#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkContext {
    pub info: SdkInfo,
    #[serde(rename = "baseUrl")]
    pub base_url: String,
    pub auth: SdkAuth,
    pub models: Vec<SdkModel>,
    pub operations: Vec<SdkOperation>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkInfo {
    pub title: String,
    pub version: String,
    pub description: Option<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkAuth {
    pub schemes: Vec<SdkAuthScheme>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkAuthScheme {
    pub name: String,
    #[serde(rename = "schemeType")]
    pub scheme_type: String,
    #[serde(rename = "inLocation")]
    pub in_location: Option<String>,
    pub format: Option<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkModel {
    pub name: String,
    pub properties: Vec<SdkProperty>,
    pub required: Vec<String>,
    pub description: Option<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkProperty {
    pub name: String,
    #[serde(rename = "typeInfo")]
    pub type_info: SdkType,
    pub required: bool,
    pub description: Option<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkType {
    #[serde(rename = "baseType")]
    pub base_type: String,
    #[serde(rename = "isNullable")]
    pub is_nullable: bool,
    #[serde(rename = "isArray")]
    pub is_array: bool,
    pub format: Option<String>,
    #[serde(rename = "enumValues")]
    pub enum_values: Option<Vec<String>>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkOperation {
    #[serde(rename = "operationId")]
    pub operation_id: String,
    pub method: String,
    pub path: String,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub parameters: Vec<SdkParameter>,
    pub request_body: Option<SdkRequestBody>,
    pub responses: Vec<SdkResponse>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkParameter {
    pub name: String,
    #[serde(rename = "inLocation")]
    pub in_location: String,
    pub required: bool,
    pub type_info: SdkType,
    pub description: Option<String>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkRequestBody {
    #[serde(rename = "contentType")]
    pub content_type: String,
    #[serde(rename = "typeInfo")]
    pub type_info: SdkType,
    pub required: bool,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkResponse {
    #[serde(rename = "statusCode")]
    pub status_code: String,
    pub description: String,
    #[serde(rename = "contentType")]
    pub content_type: Option<String>,
    #[serde(rename = "typeInfo")]
    pub type_info: Option<SdkType>,
}

/// Convert UnifiedSpec to SdkContext for template generation
pub fn spec_to_context(spec: UnifiedSpec) -> Result<SdkContext> {
    let info = SdkInfo {
        title: spec.info.title.clone(),
        version: spec.info.version.clone(),
        description: spec.info.description.clone(),
    };

    let auth = SdkAuth {
        schemes: spec
            .security_schemes
            .iter()
            .map(|(name, scheme)| SdkAuthScheme {
                name: name.clone(),
                scheme_type: scheme.scheme_type.clone(),
                in_location: scheme.location.clone(),
                format: scheme.scheme.clone(),
            })
            .collect(),
    };

    // Convert operations
    let operations: Vec<SdkOperation> = spec
        .operations
        .iter()
        .map(|op| {
            // Generate operation ID if missing
            let operation_id = if op.operation_id.is_empty() {
                generate_operation_id(&op.method, &op.path)
            } else {
                op.operation_id.clone()
            };

            SdkOperation {
                operation_id,
                method: op.method.clone(),
                path: op.path.clone(),
                summary: op.summary.clone(),
                description: op.description.clone(),
                parameters: op
                    .parameters
                    .iter()
                    .map(|param| SdkParameter {
                        name: param.name.clone(),
                        in_location: format!("{:?}", param.location).to_lowercase(),
                        required: param.required,
                        type_info: schema_to_sdk_type(&param.schema),
                        description: param.description.clone(),
                    })
                    .collect(),
                request_body: op.request_body.as_ref().map(|rb| SdkRequestBody {
                    content_type: rb
                        .content
                        .keys()
                        .next()
                        .cloned()
                        .unwrap_or_else(|| "application/json".to_string()),
                    type_info: rb
                        .content
                        .values()
                        .next()
                        .map(|mt| schema_to_sdk_type(&mt.schema))
                        .unwrap_or_else(|| SdkType {
                            base_type: "object".to_string(),
                            is_nullable: false,
                            is_array: false,
                            format: None,
                            enum_values: None,
                        }),
                    required: rb.required,
                }),
                responses: op
                    .responses
                    .iter()
                    .map(|(status, resp)| SdkResponse {
                        status_code: status.clone(),
                        description: resp.description.clone(),
                        content_type: resp.content.keys().next().cloned(),
                        type_info: resp
                            .content
                            .values()
                            .next()
                            .map(|mt| schema_to_sdk_type(&mt.schema)),
                    })
                    .collect(),
            }
        })
        .collect();

    // Extract models from spec
    let models = extract_models_from_spec(&spec)?;

    Ok(SdkContext {
        info,
        base_url: spec.base_url,
        auth,
        models,
        operations,
    })
}

/// Convert UnifiedSchema to SdkType
fn schema_to_sdk_type(schema: &crate::core::parser::UnifiedSchema) -> SdkType {
    use crate::core::parser::SchemaType;

    let base_type = match schema.schema_type {
        SchemaType::String => "string",
        SchemaType::Integer => "integer",
        SchemaType::Number => "number",
        SchemaType::Boolean => "boolean",
        SchemaType::Array => "array",
        SchemaType::Object => "object",
        SchemaType::Unknown => "any",
    }
    .to_string();

    SdkType {
        base_type,
        is_nullable: false, // TODO: Detect from schema
        is_array: schema.schema_type == SchemaType::Array,
        format: schema.format.clone(),
        enum_values: schema.enum_values.as_ref().map(|values| {
            values
                .iter()
                .filter_map(|v| v.as_str().map(String::from))
                .collect()
        }),
    }
}

/// Extract models from OpenAPI spec components
fn extract_models_from_spec(_spec: &UnifiedSpec) -> Result<Vec<SdkModel>> {
    // For now, return empty models since UnifiedSpec doesn't have components
    // In a full implementation, we would parse components/schemas from the original spec
    Ok(Vec::new())
}

/// Generate operation ID from method and path
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
