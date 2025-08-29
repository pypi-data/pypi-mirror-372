use super::{spec_to_context, SdkCommand, TemplateEngine};
use crate::core::parser::UnifiedSpec;
use anyhow::Result;
use colored::*;
use serde_json::json;
use std::fs;
use std::path::{Path, PathBuf};

pub fn generate(cmd: SdkCommand, spec: UnifiedSpec) -> Result<()> {
    println!("🐍 {} Python SDK Generation", "MicroRapid".bright_cyan());
    println!("📄 Spec: {}", cmd.spec.display());
    println!("📁 Output: {}", cmd.output.display());

    // Create output directory
    fs::create_dir_all(&cmd.output)?;

    // Convert spec to template context
    let context = spec_to_context(spec)?;

    // Create templates directory
    let templates_dir = create_python_templates(&cmd.output)?;

    // Initialize template engine
    let mut engine = TemplateEngine::new(templates_dir.clone())?;

    // Generate files
    generate_client_file(&mut engine, &context, &cmd)?;
    generate_models_file(&mut engine, &context, &cmd)?;
    generate_types_file(&mut engine, &context, &cmd)?;
    generate_init_file(&mut engine, &context, &cmd)?;
    generate_setup_py(&mut engine, &context, &cmd)?;
    generate_requirements(&mut engine, &context, &cmd)?;
    generate_readme(&mut engine, &context, &cmd)?;

    // Clean up templates directory
    let _ = fs::remove_dir_all(&templates_dir);

    println!("✅ Python SDK generated successfully!");
    println!("📦 Files generated:");
    println!("   • client.py - Main API client");
    println!("   • models.py - Type definitions");
    println!("   • types.py - Common types");
    println!("   • __init__.py - Package exports");
    println!("   • setup.py - Package configuration");
    println!("   • requirements.txt - Dependencies");
    println!("   • README.md - Usage documentation");

    Ok(())
}

fn generate_client_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "info": context.info,
        "baseUrl": context.base_url,
        "auth": context.auth,
        "operations": context.operations,
        "httpClient": cmd.http_client.as_deref().unwrap_or("httpx"),
        "includeAuth": cmd.auth,
        "includePagination": cmd.pagination,
        "includeResilience": cmd.resilience,
    });

    let output_path = cmd.output.join("client.py");
    engine.render_to_file("client.py.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_models_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "models": context.models,
    });

    let output_path = cmd.output.join("models.py");
    engine.render_to_file("models.py.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_types_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "auth": context.auth,
        "includeAuth": cmd.auth,
        "includePagination": cmd.pagination,
        "includeResilience": cmd.resilience,
    });

    let output_path = cmd.output.join("types.py");
    engine.render_to_file("types.py.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_init_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "info": context.info,
    });

    let output_path = cmd.output.join("__init__.py");
    engine.render_to_file("__init__.py.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_setup_py(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let default_name = context.info.title.to_lowercase().replace(" ", "-");
    let package_name = cmd.package_name.as_deref().unwrap_or(&default_name);

    let template_context = json!({
        "packageName": package_name,
        "version": context.info.version,
        "description": context.info.description,
        "httpClient": cmd.http_client.as_deref().unwrap_or("httpx"),
    });

    let output_path = cmd.output.join("setup.py");
    engine.render_to_file("setup.py.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_requirements(
    engine: &mut TemplateEngine,
    _context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let http_client = cmd.http_client.as_deref().unwrap_or("httpx");

    let template_context = json!({
        "httpClient": http_client,
        "includeAuth": cmd.auth,
        "includeResilience": cmd.resilience,
    });

    let output_path = cmd.output.join("requirements.txt");
    engine.render_to_file("requirements.txt.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_readme(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let default_name = context.info.title.to_lowercase().replace(" ", "-");
    let package_name = cmd.package_name.as_deref().unwrap_or(&default_name);

    let template_context = json!({
        "packageName": package_name,
        "title": context.info.title,
        "description": context.info.description,
        "version": context.info.version,
        "baseUrl": context.base_url,
        "auth": context.auth,
        "operations": context.operations.iter().take(3).collect::<Vec<_>>(), // Show first 3 operations
        "httpClient": cmd.http_client.as_deref().unwrap_or("httpx"),
    });

    let output_path = cmd.output.join("README.md");
    engine.render_to_file("README.md.hbs", &template_context, &output_path)?;
    Ok(())
}

/// Create Python templates
fn create_python_templates(_output_dir: &PathBuf) -> Result<PathBuf> {
    // Use system temp directory instead of output directory
    let temp_dir =
        std::env::temp_dir().join(format!("mrapids-py-templates-{}", std::process::id()));
    fs::create_dir_all(&temp_dir)?;

    // Always use embedded templates
    create_embedded_templates(&temp_dir)?;

    Ok(temp_dir)
}

/// Create embedded templates as fallback
fn create_embedded_templates(templates_dir: &PathBuf) -> Result<()> {
    // Basic client template
    fs::write(
        templates_dir.join("client.py.hbs"),
        r#""""
{{info.title}} API Client
Generated by MicroRapid
"""
import httpx
from typing import Optional, Dict, Any, Union
from .types import ApiConfig, ApiError
from .models import *


class ApiClient:
    """Main API client for {{info.title}}"""
    
    def __init__(self, config: ApiConfig = None):
        if config is None:
            config = ApiConfig()
        self.config = config
        self.base_url = config.base_url or "{{baseUrl}}"
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=config.timeout,
            {{#if includeAuth}}
            headers=self._get_auth_headers()
            {{/if}}
        )
    
    {{#if includeAuth}}
    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        headers = {}
        if hasattr(self.config, 'bearer_token') and self.config.bearer_token:
            headers["Authorization"] = f"Bearer {self.config.bearer_token}"
        if hasattr(self.config, 'api_key') and self.config.api_key:
            # Assuming API key goes in header
            headers["X-API-Key"] = self.config.api_key
        return headers
    {{/if}}
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        """Make an HTTP request"""
        try:
            response = self._client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                headers=headers,
            )
            response.raise_for_status()
            return response.json() if response.content else None
        except httpx.HTTPStatusError as e:
            raise ApiError(f"HTTP {e.response.status_code}: {e.response.text}", e.response.status_code)
        except Exception as e:
            raise ApiError(str(e), 0)
    
    {{#each operations}}
    {{#if operationId}}
    def {{operationId}}(
        self,
        {{#each parameters}}
        {{name}}: {{#if required}}{{else}}Optional[{{/if}}Any{{#if required}}{{else}}] = None{{/if}},
        {{/each}}
        {{#if requestBody}}
        body: {{#if requestBody.required}}{{else}}Optional[{{/if}}Dict[str, Any]{{#if requestBody.required}}{{else}}] = None{{/if}},
        {{/if}}
    ) -> Any:
        """
        {{#if summary}}{{summary}}{{else}}{{method}} {{path}}{{/if}}
        {{#if description}}
        
        {{description}}
        {{/if}}
        """
        {{#if parameters}}
        params = {}
        {{#each parameters}}
        # Assuming query parameters (adjust if needed)
        if {{snakeCase name}} is not None:
            params["{{name}}"] = {{snakeCase name}}
        {{/each}}
        {{/if}}
        
        path = "{{path}}"
        {{#each parameters}}
        # Replace path parameters
        path = path.replace("{{{name}}}", str({{snakeCase name}}))
        {{/each}}
        
        return self._request(
            method="{{method}}",
            path=path,
            {{#if parameters}}params=params,{{/if}}
            {{#if requestBody}}json=body,{{/if}}
        )
    {{else}}
    # Warning: Operation {{method}} {{path}} has no operationId
    {{/if}}
    
    {{/each}}
    
    def close(self):
        """Close the HTTP client"""
        self._client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
"#,
    )?;

    // Basic models template
    fs::write(
        templates_dir.join("models.py.hbs"),
        r#""""
{{info.title}} API Models
Generated by MicroRapid
"""
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import datetime


{{#each models}}
@dataclass
class {{pascalCase name}}:
    """{{#if description}}{{description}}{{/if}}"""
    {{#each properties}}
    {{snakeCase name}}: {{#if required}}{{else}}Optional[{{/if}}Any{{#if required}}{{else}}] = None{{/if}}
    {{/each}}
    {{#unless properties}}
    pass
    {{/unless}}


{{/each}}
"#,
    )?;

    // Basic types template
    fs::write(
        templates_dir.join("types.py.hbs"),
        r#""""
{{info.title}} API Types
Generated by MicroRapid
"""
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class ApiConfig:
    """API client configuration"""
    base_url: Optional[str] = None
    {{#if includeAuth}}
    bearer_token: Optional[str] = None
    api_key: Optional[str] = None
    {{/if}}
    {{#if includeResilience}}
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    {{else}}
    timeout: float = 30.0
    {{/if}}
    headers: Dict[str, str] = field(default_factory=dict)


class ApiError(Exception):
    """API error"""
    
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
"#,
    )?;

    // __init__.py template
    fs::write(
        templates_dir.join("__init__.py.hbs"),
        r#""""
{{info.title}} Python SDK
Version: {{info.version}}
{{#if info.description}}

{{info.description}}
{{/if}}
"""
from .client import ApiClient
from .types import ApiConfig, ApiError
from .models import *

__version__ = "{{info.version}}"
__all__ = ["ApiClient", "ApiConfig", "ApiError"]
"#,
    )?;

    // setup.py template
    fs::write(
        templates_dir.join("setup.py.hbs"),
        r#"from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="{{packageName}}",
    version="{{version}}",
    description="Python SDK for {{packageName}}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "httpx>=0.23.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
"#,
    )?;

    // requirements.txt template
    fs::write(
        templates_dir.join("requirements.txt.hbs"),
        r#"httpx>=0.23.0
{{#if includeAuth}}
# Authentication dependencies included
{{/if}}
{{#if includeResilience}}
# Resilience features included (retry, timeout)
{{/if}}
"#,
    )?;

    // README template
    fs::write(
        templates_dir.join("README.md.hbs"),
        r#"# {{title}} Python SDK

Version: {{version}}

{{#if description}}
{{description}}
{{/if}}

## Installation

```bash
pip install {{packageName}}
```

## Usage

```python
from {{snakeCase packageName}} import ApiClient, ApiConfig

# Create client
config = ApiConfig(
    base_url="{{baseUrl}}"{{#if includeAuth}},
    {{#each auth.schemes}}
    {{#if (eq scheme_type "bearer")}}
    bearer_token="your-token"
    {{else if (eq scheme_type "apiKey")}}
    api_key="your-api-key"
    {{/if}}
    {{/each}}{{/if}}
)

client = ApiClient(config)

# Make API calls
{{#each operations}}
{{#if @first}}
{{#if operationId}}
result = client.{{snakeCase operationId}}()
{{/if}}
{{/if}}
{{/each}}
```

{{#if (eq httpClient "httpx")}}
## Using with async

```python
import httpx
from {{snakeCase packageName}} import ApiConfig

# The SDK uses httpx which supports both sync and async
async with httpx.AsyncClient(base_url="{{baseUrl}}") as client:
    response = await client.get("/endpoint")
```
{{/if}}

## Available Operations

{{#each operations}}
{{#if operationId}}
- `{{snakeCase operationId}}()` - {{#if summary}}{{summary}}{{else}}{{method}} {{path}}{{/if}}
{{/if}}
{{/each}}

## Error Handling

```python
from your_package import ApiError

try:
    result = client.{{#if operations.[0]}}{{#if operations.[0].operationId}}{{snakeCase operations.[0].operationId}}{{else}}some_operation{{/if}}{{else}}some_operation{{/if}}()
except ApiError as e:
    print(f"API error: {e.message} (status: {e.status_code})")
```

## Configuration

The `ApiConfig` class supports the following options:

- `base_url` - API base URL (default: `{{baseUrl}}`)
{{#if includeAuth}}
{{#each auth.schemes}}
{{#if (eq scheme_type "bearer")}}
- `bearer_token` - Bearer token for authentication
{{else if (eq scheme_type "apiKey")}}
- `api_key` - API key for authentication
{{/if}}
{{/each}}
{{/if}}
{{#if includeResilience}}
- `timeout` - Request timeout in seconds (default: 30.0)
- `max_retries` - Maximum number of retries (default: 3)
- `retry_delay` - Delay between retries in seconds (default: 1.0)
{{/if}}
- `headers` - Additional headers to include in requests

---

Generated by [MicroRapid](https://github.com/yourusername/microrapid)
"#,
    )?;

    Ok(())
}

/// Wrapper function for direct SDK generation (used by main.rs)
pub fn generate_python_sdk(
    spec: &UnifiedSpec,
    output_dir: &Path,
    package_name: Option<&str>,
    include_docs: bool,
    include_examples: bool,
) -> Result<()> {
    // Create SdkCommand for the internal generate function
    let cmd = SdkCommand {
        spec: output_dir.to_path_buf(), // This is a bit hacky but needed for logging
        lang: crate::cli::SdkLanguage::Python,
        output: output_dir.to_path_buf(),
        package_name: package_name.map(String::from),
        http_client: Some("httpx".to_string()),
        auth: true,
        pagination: true,
        resilience: true,
        docs: include_docs,
        examples: include_examples,
    };

    generate(cmd, spec.clone())
}
