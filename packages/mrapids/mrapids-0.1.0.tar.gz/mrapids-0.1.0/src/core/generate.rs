#![allow(dead_code)]

use crate::cli::GenerateTarget;
use crate::core::swagger::SwaggerSpec;
use crate::core::validation::{SpecValidator, ValidationLevel};
use crate::utils::security::{validate_file_path, validate_output_path};
use anyhow::Result;
use colored::*;
use std::fs;
use std::path::{Path, PathBuf};

// Internal command structure for generate functionality
pub struct GenerateCommand {
    pub spec: PathBuf,
    pub target: GenerateTarget,
    pub output: PathBuf,
    pub client: bool,
    pub server: bool,
    pub both: bool,
    pub package_name: Option<String>,
    #[allow(dead_code)]
    pub skip_validation: bool,
}

pub fn generate_code(cmd: GenerateCommand) -> Result<()> {
    println!("🚀 {} Code Generator", "MicroRapid".bright_cyan());
    println!(
        "📄 Loading spec from: {}",
        cmd.spec.display().to_string().cyan()
    );

    // Validate input spec path
    validate_file_path(&cmd.spec)?;

    // Validate output directory path
    validate_output_path(&cmd.output)?;

    // Load and parse the spec
    let content = fs::read_to_string(&cmd.spec)
        .map_err(|e| anyhow::anyhow!("Cannot read spec file: {}", e))?;

    // Validate the specification before code generation
    println!("{} Validating specification...", "🔍".bright_cyan());
    let validator = SpecValidator::new()?;
    let validation_report = validator.validate_content(&content, ValidationLevel::Standard)?;

    if !validation_report.is_valid() {
        println!("\n{} Specification has validation errors:", "❌".red());
        validation_report.display();
        println!(
            "\n{} Code generation requires a valid specification",
            "💡".blue()
        );
        return Err(anyhow::anyhow!("Specification validation failed"));
    } else if validation_report.has_warnings() {
        println!("{} Specification has warnings:", "⚠️".yellow());
        validation_report.display();
        println!("{} Proceeding with code generation...", "➡️".blue());
    } else {
        println!("{} Specification is valid!", "✅".green());
    }

    let spec_value: serde_json::Value =
        if cmd.spec.extension().and_then(|s| s.to_str()) == Some("json") {
            serde_json::from_str(&content)?
        } else {
            serde_yaml::from_str(&content)?
        };

    // Detect spec format
    let is_swagger_2 = spec_value.get("swagger").is_some();
    let is_openapi_3 = spec_value.get("openapi").is_some();

    if !is_swagger_2 && !is_openapi_3 {
        return Err(anyhow::anyhow!("Unable to detect API specification format"));
    }

    // Parse spec
    let swagger_spec: SwaggerSpec = if cmd.spec.extension().and_then(|s| s.to_str()) == Some("json")
    {
        serde_json::from_str(&content)?
    } else {
        serde_yaml::from_str(&content)?
    };

    // Determine what to generate
    let generate_client = cmd.client || (!cmd.server && !cmd.both) || cmd.both;
    let generate_server = cmd.server || cmd.both;

    // Create output directory
    fs::create_dir_all(&cmd.output)?;

    println!("🎯 Target: {}", format!("{:?}", cmd.target).yellow());
    println!("📁 Output: {}", cmd.output.display().to_string().green());

    if generate_client {
        println!("\n📦 Generating {} code...", "client".bright_blue());
        generate_client_code(
            &swagger_spec,
            &cmd.target,
            &cmd.output,
            cmd.package_name.as_deref(),
        )?;
    }

    if generate_server {
        println!("\n📦 Generating {} code...", "server".bright_blue());
        generate_server_code(
            &swagger_spec,
            &cmd.target,
            &cmd.output,
            cmd.package_name.as_deref(),
        )?;
    }

    println!("\n✅ Code generation complete!");
    println!(
        "📁 Generated files in: {}",
        cmd.output.display().to_string().green()
    );

    Ok(())
}

fn generate_client_code(
    spec: &SwaggerSpec,
    target: &GenerateTarget,
    output_dir: &Path,
    package_name: Option<&str>,
) -> Result<()> {
    match target {
        GenerateTarget::Typescript => generate_typescript_client(spec, output_dir, package_name),
        GenerateTarget::Python => generate_python_client(spec, output_dir, package_name),
        GenerateTarget::Curl => generate_curl_commands(spec, output_dir),
        GenerateTarget::Postman => generate_postman_collection(spec, output_dir, package_name),
        _ => {
            println!(
                "⚠️  {} client generation not yet implemented",
                format!("{:?}", target).yellow()
            );
            Ok(())
        }
    }
}

fn generate_server_code(
    _spec: &SwaggerSpec,
    target: &GenerateTarget,
    _output_dir: &Path,
    _package_name: Option<&str>,
) -> Result<()> {
    match target {
        GenerateTarget::Typescript => {
            println!("  📝 Generating Express.js server stubs...");
            // TODO: Implement Express server generation
            Ok(())
        }
        GenerateTarget::Python => {
            println!("  📝 Generating FastAPI server stubs...");
            // TODO: Implement FastAPI server generation
            Ok(())
        }
        _ => {
            println!(
                "⚠️  {} server generation not yet implemented",
                format!("{:?}", target).yellow()
            );
            Ok(())
        }
    }
}

fn generate_typescript_client(
    spec: &SwaggerSpec,
    output_dir: &Path,
    package_name: Option<&str>,
) -> Result<()> {
    let client_name = package_name.unwrap_or("ApiClient");
    let file_path = output_dir.join("client.ts");

    let mut content = String::new();

    // Generate header
    content.push_str(&format!(
        r#"/**
 * {} API Client
 * Version: {}
 * Auto-generated by MicroRapid
 */

export interface RequestConfig {{
    baseURL?: string;
    headers?: Record<string, string>;
    timeout?: number;
}}

export class {} {{
    private baseURL: string;
    private headers: Record<string, string>;
    
    constructor(config: RequestConfig = {{}}) {{
        this.baseURL = config.baseURL || '{}';
        this.headers = config.headers || {{}};
    }}
    
    private async request<T>(
        method: string,
        path: string,
        params?: any,
        data?: any
    ): Promise<T> {{
        const url = new URL(path, this.baseURL);
        
        if (params) {{
            Object.keys(params).forEach(key => 
                url.searchParams.append(key, params[key])
            );
        }}
        
        const options: RequestInit = {{
            method,
            headers: {{
                'Content-Type': 'application/json',
                ...this.headers
            }}
        }};
        
        if (data) {{
            options.body = JSON.stringify(data);
        }}
        
        const response = await fetch(url.toString(), options);
        
        if (!response.ok) {{
            throw new Error(`HTTP ${{response.status}}: ${{response.statusText}}`);
        }}
        
        return response.json();
    }}
"#,
        spec.info.title,
        spec.info.version,
        client_name,
        spec.get_base_url()
    ));

    // Generate methods for each operation
    for (path, path_item) in &spec.paths {
        let operations = [
            ("get", &path_item.get),
            ("post", &path_item.post),
            ("put", &path_item.put),
            ("delete", &path_item.delete),
            ("patch", &path_item.patch),
        ];

        for (method, operation) in operations {
            if let Some(op) = operation {
                let method_name = op
                    .operation_id
                    .as_ref()
                    .map(|s| s.clone())
                    .unwrap_or_else(|| format!("{}_{}", method, sanitize_path(path)));

                let summary = op.summary.as_deref().unwrap_or("");

                content.push_str(&format!(
                    r#"
    /**
     * {}
     * {} {}
     */
    async {}(params?: any, data?: any): Promise<any> {{
        return this.request('{}', '{}', params, data);
    }}
"#,
                    summary,
                    method.to_uppercase(),
                    path,
                    method_name,
                    method.to_uppercase(),
                    path
                ));
            }
        }
    }

    content.push_str("}\n");

    fs::write(&file_path, content)?;
    println!("  ✅ Generated: {}", file_path.display());

    // Generate package.json
    let package_json = output_dir.join("package.json");
    let package_content = format!(
        r#"{{
  "name": "{}",
  "version": "1.0.0",
  "description": "{} API Client",
  "main": "client.js",
  "types": "client.ts",
  "scripts": {{
    "build": "tsc",
    "test": "echo \"No tests yet\""
  }},
  "keywords": ["api", "client", "openapi"],
  "author": "MicroRapid",
  "license": "MIT",
  "devDependencies": {{
    "typescript": "^5.0.0"
  }}
}}
"#,
        package_name.unwrap_or("api-client"),
        spec.info.title
    );

    fs::write(&package_json, package_content)?;
    println!("  ✅ Generated: {}", package_json.display());

    Ok(())
}

fn generate_python_client(
    spec: &SwaggerSpec,
    output_dir: &Path,
    package_name: Option<&str>,
) -> Result<()> {
    let client_name = package_name.unwrap_or("api_client");
    let file_path = output_dir.join(format!("{}.py", client_name));

    let mut content = String::new();

    // Generate header
    content.push_str(&format!(
        r#""""
{} API Client
Version: {}
Auto-generated by MicroRapid
"""

import requests
from typing import Dict, Any, Optional
from urllib.parse import urljoin


class {}:
    """API Client for {}"""
    
    def __init__(self, base_url: str = "{}", headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request"""
        url = urljoin(self.base_url + '/', path.lstrip('/'))
        
        response = self.session.request(
            method=method,
            url=url,
            params=params,
            json=json,
            data=data
        )
        
        response.raise_for_status()
        return response.json() if response.content else {{}}
"#,
        spec.info.title,
        spec.info.version,
        to_pascal_case(client_name),
        spec.info.title,
        spec.get_base_url()
    ));

    // Generate methods for each operation
    for (path, path_item) in &spec.paths {
        let operations = [
            ("get", &path_item.get),
            ("post", &path_item.post),
            ("put", &path_item.put),
            ("delete", &path_item.delete),
            ("patch", &path_item.patch),
        ];

        for (method, operation) in operations {
            if let Some(op) = operation {
                let method_name = op
                    .operation_id
                    .as_ref()
                    .map(|s| to_snake_case(s))
                    .unwrap_or_else(|| format!("{}_{}", method, sanitize_path_snake(path)));

                let summary = op.summary.as_deref().unwrap_or("");

                content.push_str(&format!(
                    r#"
    def {}(self, params: Optional[Dict[str, Any]] = None, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        {}
        {} {}
        """
        return self._request('{}', '{}', params=params, json=json)
"#,
                    method_name,
                    summary,
                    method.to_uppercase(),
                    path,
                    method.to_uppercase(),
                    path
                ));
            }
        }
    }

    fs::write(&file_path, content)?;
    println!("  ✅ Generated: {}", file_path.display());

    // Generate requirements.txt
    let requirements = output_dir.join("requirements.txt");
    fs::write(&requirements, "requests>=2.28.0\n")?;
    println!("  ✅ Generated: {}", requirements.display());

    // Generate __init__.py
    let init_file = output_dir.join("__init__.py");
    fs::write(
        &init_file,
        format!(
            "from .{} import {}\n",
            client_name,
            to_pascal_case(client_name)
        ),
    )?;
    println!("  ✅ Generated: {}", init_file.display());

    Ok(())
}

fn generate_curl_commands(spec: &SwaggerSpec, output_dir: &Path) -> Result<()> {
    let file_path = output_dir.join("api_commands.sh");
    let mut content = String::new();

    content.push_str(&format!(
        r#"#!/bin/bash
# {} API - cURL Commands
# Version: {}
# Auto-generated by MicroRapid

BASE_URL="{}"

# Set your API key or auth token here if needed
# AUTH_HEADER="Authorization: Bearer YOUR_TOKEN"

"#,
        spec.info.title,
        spec.info.version,
        spec.get_base_url()
    ));

    for (path, path_item) in &spec.paths {
        let operations = [
            ("GET", &path_item.get),
            ("POST", &path_item.post),
            ("PUT", &path_item.put),
            ("DELETE", &path_item.delete),
            ("PATCH", &path_item.patch),
        ];

        for (method, operation) in operations {
            if let Some(op) = operation {
                let op_id = op.operation_id.as_deref().unwrap_or("operation");
                let summary = op.summary.as_deref().unwrap_or("");

                content.push_str(&format!(
                    r#"# {}
# {}
{}() {{
    curl -X {} \
        "${{BASE_URL}}{}" \
        -H "Content-Type: application/json" \
        -H "${{AUTH_HEADER:-}}" \
        "$@"
}}

"#,
                    op_id, summary, op_id, method, path
                ));
            }
        }
    }

    fs::write(&file_path, content)?;

    // Make the script executable
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&file_path)?.permissions();
        perms.set_mode(0o755);
        fs::set_permissions(&file_path, perms)?;
    }

    println!("  ✅ Generated: {}", file_path.display());
    Ok(())
}

fn generate_postman_collection(
    spec: &SwaggerSpec,
    output_dir: &Path,
    package_name: Option<&str>,
) -> Result<()> {
    let collection_name = package_name.unwrap_or(&spec.info.title);
    let file_path = output_dir.join("postman_collection.json");

    let mut items = Vec::new();

    for (path, path_item) in &spec.paths {
        let operations = [
            ("GET", &path_item.get),
            ("POST", &path_item.post),
            ("PUT", &path_item.put),
            ("DELETE", &path_item.delete),
            ("PATCH", &path_item.patch),
        ];

        for (method, operation) in operations {
            if let Some(op) = operation {
                let default_name = format!("{} {}", method, path);
                let name = op
                    .operation_id
                    .as_deref()
                    .or(op.summary.as_deref())
                    .unwrap_or(&default_name);

                items.push(serde_json::json!({
                    "name": name,
                    "request": {
                        "method": method,
                        "header": [
                            {
                                "key": "Content-Type",
                                "value": "application/json"
                            }
                        ],
                        "url": {
                            "raw": format!("{}{}", spec.get_base_url(), path),
                            "host": [spec.get_base_url()],
                            "path": path.split('/').filter(|s| !s.is_empty()).collect::<Vec<_>>()
                        }
                    }
                }));
            }
        }
    }

    let collection = serde_json::json!({
        "info": {
            "name": collection_name,
            "description": spec.info.description.as_deref().unwrap_or(""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": items
    });

    fs::write(&file_path, serde_json::to_string_pretty(&collection)?)?;
    println!("  ✅ Generated: {}", file_path.display());

    Ok(())
}

// Helper functions
fn sanitize_path(path: &str) -> String {
    path.replace('/', "_")
        .replace('{', "")
        .replace('}', "")
        .trim_matches('_')
        .to_string()
}

fn sanitize_path_snake(path: &str) -> String {
    to_snake_case(&sanitize_path(path))
}

fn to_snake_case(s: &str) -> String {
    let mut result = String::new();
    for (i, ch) in s.chars().enumerate() {
        if ch.is_uppercase() && i > 0 {
            result.push('_');
        }
        result.push(ch.to_lowercase().next().unwrap());
    }
    result
}

fn to_pascal_case(s: &str) -> String {
    s.split('_')
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                None => String::new(),
                Some(first) => first.to_uppercase().chain(chars).collect(),
            }
        })
        .collect()
}
