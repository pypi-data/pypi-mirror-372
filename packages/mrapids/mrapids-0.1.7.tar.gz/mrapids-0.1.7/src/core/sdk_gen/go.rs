use super::{spec_to_context, SdkCommand, TemplateEngine};
use crate::core::parser::UnifiedSpec;
use anyhow::Result;
use colored::*;
use serde_json::json;
use std::fs;
use std::path::{Path, PathBuf};

pub fn generate(cmd: SdkCommand, spec: UnifiedSpec) -> Result<()> {
    println!("🐹 {} Go SDK Generation", "MicroRapid".bright_cyan());
    println!("📄 Spec: {}", cmd.spec.display());
    println!("📁 Output: {}", cmd.output.display());

    // Create output directory
    fs::create_dir_all(&cmd.output)?;

    // Convert spec to template context
    let context = spec_to_context(spec)?;

    // Create templates directory
    let templates_dir = create_go_templates(&cmd.output)?;

    // Initialize template engine
    let mut engine = TemplateEngine::new(templates_dir.clone())?;

    // Generate files
    generate_client_file(&mut engine, &context, &cmd)?;
    generate_models_file(&mut engine, &context, &cmd)?;
    generate_types_file(&mut engine, &context, &cmd)?;
    generate_go_mod(&mut engine, &context, &cmd)?;
    generate_readme(&mut engine, &context, &cmd)?;

    // Clean up templates directory
    let _ = fs::remove_dir_all(&templates_dir);

    println!("✅ Go SDK generated successfully!");
    println!("📦 Files generated:");
    println!("   • client.go - Main API client");
    println!("   • models.go - Type definitions");
    println!("   • types.go - Common types");
    println!("   • go.mod - Module definition");
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
        "packageName": get_package_name(context, cmd),
        "includeAuth": cmd.auth,
        "includePagination": cmd.pagination,
        "includeResilience": cmd.resilience,
    });

    let output_path = cmd.output.join("client.go");
    engine.render_to_file("client.go.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_models_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "models": context.models,
        "packageName": get_package_name(context, cmd),
    });

    let output_path = cmd.output.join("models.go");
    engine.render_to_file("models.go.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_types_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "auth": context.auth,
        "packageName": get_package_name(context, cmd),
        "includeAuth": cmd.auth,
        "includePagination": cmd.pagination,
        "includeResilience": cmd.resilience,
    });

    let output_path = cmd.output.join("types.go");
    engine.render_to_file("types.go.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_go_mod(
    engine: &mut TemplateEngine,
    _context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let module_name = cmd
        .package_name
        .as_deref()
        .unwrap_or("github.com/example/api-client");

    let template_context = json!({
        "moduleName": module_name,
        "goVersion": "1.21",
    });

    let output_path = cmd.output.join("go.mod");
    engine.render_to_file("go.mod.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_readme(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    cmd: &SdkCommand,
) -> Result<()> {
    let package_name = get_package_name(context, cmd);
    let module_name = cmd
        .package_name
        .as_deref()
        .unwrap_or("github.com/example/api-client");

    let template_context = json!({
        "packageName": package_name,
        "moduleName": module_name,
        "title": context.info.title,
        "description": context.info.description,
        "version": context.info.version,
        "baseUrl": context.base_url,
        "auth": context.auth,
        "operations": context.operations.iter().take(3).collect::<Vec<_>>(), // Show first 3 operations
    });

    let output_path = cmd.output.join("README.md");
    engine.render_to_file("README.md.hbs", &template_context, &output_path)?;
    Ok(())
}

fn get_package_name(context: &super::SdkContext, cmd: &SdkCommand) -> String {
    if let Some(package) = &cmd.package_name {
        // Extract last part of module path as package name
        package.split('/').last().unwrap_or("client").to_string()
    } else {
        // Generate from API title
        context
            .info
            .title
            .to_lowercase()
            .replace(" ", "")
            .replace("-", "")
            .chars()
            .filter(|c| c.is_alphanumeric())
            .collect()
    }
}

/// Create Go templates
fn create_go_templates(_output_dir: &PathBuf) -> Result<PathBuf> {
    // Use system temp directory instead of output directory
    let temp_dir =
        std::env::temp_dir().join(format!("mrapids-go-templates-{}", std::process::id()));
    fs::create_dir_all(&temp_dir)?;

    // Always use embedded templates
    create_embedded_templates(&temp_dir)?;

    Ok(temp_dir)
}

/// Create embedded templates as fallback
fn create_embedded_templates(templates_dir: &PathBuf) -> Result<()> {
    // Basic client template
    fs::write(
        templates_dir.join("client.go.hbs"),
        r#"// Package {{packageName}} provides a client for the {{info.title}} API
// Generated by MicroRapid
package {{packageName}}

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"
    "strings"
    "time"
)

// Client is the main API client for {{info.title}}
type Client struct {
    baseURL    string
    httpClient *http.Client
    {{#if includeAuth}}
    config     *Config
    {{/if}}
}

// NewClient creates a new API client
func NewClient(config *Config) *Client {
    if config == nil {
        config = &Config{}
    }
    
    baseURL := config.BaseURL
    if baseURL == "" {
        baseURL = "{{baseUrl}}"
    }
    
    httpClient := &http.Client{
        Timeout: config.Timeout,
    }
    
    {{#if includeResilience}}
    if config.MaxRetries > 0 {
        httpClient.Transport = &retryTransport{
            underlying: http.DefaultTransport,
            maxRetries: config.MaxRetries,
            retryDelay: config.RetryDelay,
        }
    }
    {{/if}}
    
    return &Client{
        baseURL:    baseURL,
        httpClient: httpClient,
        {{#if includeAuth}}
        config:     config,
        {{/if}}
    }
}

// request makes an HTTP request
func (c *Client) request(ctx context.Context, method, path string, query url.Values, body interface{}) ([]byte, error) {
    u, err := url.Parse(c.baseURL + path)
    if err != nil {
        return nil, err
    }
    
    if query != nil {
        u.RawQuery = query.Encode()
    }
    
    var bodyReader io.Reader
    if body != nil {
        jsonBody, err := json.Marshal(body)
        if err != nil {
            return nil, err
        }
        bodyReader = bytes.NewReader(jsonBody)
    }
    
    req, err := http.NewRequestWithContext(ctx, method, u.String(), bodyReader)
    if err != nil {
        return nil, err
    }
    
    if body != nil {
        req.Header.Set("Content-Type", "application/json")
    }
    req.Header.Set("Accept", "application/json")
    
    {{#if includeAuth}}
    // Add authentication headers
    if c.config.BearerToken != "" {
        req.Header.Set("Authorization", "Bearer " + c.config.BearerToken)
    } else if c.config.APIKey != "" {
        req.Header.Set("X-API-Key", c.config.APIKey)
    }
    {{/if}}
    
    resp, err := c.httpClient.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    respBody, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }
    
    if resp.StatusCode >= 400 {
        var apiErr APIError
        apiErr.StatusCode = resp.StatusCode
        apiErr.Message = string(respBody)
        return nil, &apiErr
    }
    
    return respBody, nil
}

{{#each operations}}
{{#if operationId}}
// {{pascalCase operationId}} {{#if summary}}{{summary}}{{/if}}
func (c *Client) {{pascalCase operationId}}(ctx context.Context{{#each parameters}}, {{camelCase name}} string{{/each}}{{#if requestBody}}, body interface{}{{/if}}) (interface{}, error) {
    {{#if parameters}}
    query := url.Values{}
    {{#each parameters}}
    // Add query parameters
    if {{camelCase name}} != "" {
        query.Set("{{name}}", {{camelCase name}})
    }
    {{/each}}
    {{/if}}
    
    path := "{{path}}"
    {{#each parameters}}
    // Replace path parameters
    path = strings.ReplaceAll(path, "{{{name}}}", {{camelCase name}})
    {{/each}}
    
    respBody, err := c.request(ctx, "{{method}}", path, {{#if parameters}}query{{else}}nil{{/if}}, {{#if requestBody}}body{{else}}nil{{/if}})
    if err != nil {
        return nil, err
    }
    
    var result interface{}
    if err := json.Unmarshal(respBody, &result); err != nil {
        return nil, err
    }
    return result, nil
}
{{/if}}

{{/each}}

{{#if includeResilience}}
// retryTransport implements automatic retry logic
type retryTransport struct {
    underlying http.RoundTripper
    maxRetries int
    retryDelay time.Duration
}

func (t *retryTransport) RoundTrip(req *http.Request) (*http.Response, error) {
    var resp *http.Response
    var err error
    
    for i := 0; i <= t.maxRetries; i++ {
        resp, err = t.underlying.RoundTrip(req)
        if err == nil && resp.StatusCode < 500 {
            return resp, nil
        }
        
        if i < t.maxRetries {
            time.Sleep(t.retryDelay * time.Duration(i+1))
        }
    }
    
    return resp, err
}
{{/if}}
"#,
    )?;

    // Basic models template
    fs::write(
        templates_dir.join("models.go.hbs"),
        r#"// Package {{packageName}} provides models for the {{info.title}} API
// Generated by MicroRapid
package {{packageName}}

import (
    "time"
)

{{#each models}}
// {{pascalCase name}} {{#if description}}{{description}}{{/if}}
type {{pascalCase name}} struct {
    {{#each properties}}
    {{pascalCase name}} interface{} `json:"{{name}}{{#unless required}},omitempty{{/unless}}"`
    {{/each}}
}

{{/each}}
"#,
    )?;

    // Basic types template
    fs::write(
        templates_dir.join("types.go.hbs"),
        r#"// Package {{packageName}} provides common types for the {{info.title}} API
// Generated by MicroRapid
package {{packageName}}

import (
    "fmt"
    "time"
)

// Config holds the configuration for the API client
type Config struct {
    // BaseURL is the base URL for the API
    BaseURL string
    
    {{#if includeAuth}}
    // BearerToken is the bearer token for authentication
    BearerToken string
    
    // APIKey is the API key for authentication
    APIKey string
    {{/if}}
    
    // Timeout is the HTTP client timeout
    Timeout time.Duration
    
    {{#if includeResilience}}
    // MaxRetries is the maximum number of retries
    MaxRetries int
    
    // RetryDelay is the delay between retries
    RetryDelay time.Duration
    {{/if}}
}

// NewConfig creates a new configuration with defaults
func NewConfig() *Config {
    return &Config{
        Timeout: 30 * time.Second,
        {{#if includeResilience}}
        MaxRetries: 3,
        RetryDelay: 1 * time.Second,
        {{/if}}
    }
}

// APIError represents an API error response
type APIError struct {
    StatusCode int    `json:"status_code"`
    Message    string `json:"message"`
}

// Error implements the error interface
func (e *APIError) Error() string {
    return fmt.Sprintf("API error (status %d): %s", e.StatusCode, e.Message)
}

{{#if includePagination}}
// PageInfo contains pagination information
type PageInfo struct {
    Page       int `json:"page"`
    PerPage    int `json:"per_page"`
    Total      int `json:"total"`
    TotalPages int `json:"total_pages"`
}

// ListOptions specifies optional parameters for list operations
type ListOptions struct {
    Page    int `url:"page,omitempty"`
    PerPage int `url:"per_page,omitempty"`
}
{{/if}}
"#,
    )?;

    // go.mod template
    fs::write(
        templates_dir.join("go.mod.hbs"),
        r#"module {{moduleName}}

go {{goVersion}}
"#,
    )?;

    // README template
    fs::write(
        templates_dir.join("README.md.hbs"),
        r#"# {{title}} Go SDK

Version: {{version}}

{{#if description}}
{{description}}
{{/if}}

## Installation

```bash
go get {{moduleName}}
```

## Usage

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    "{{moduleName}}"
)

func main() {
    // Create configuration
    config := {{packageName}}.NewConfig()
    config.BaseURL = "{{baseUrl}}"
    {{#if includeAuth}}
    // Set authentication
    config.BearerToken = "your-token"
    // or
    config.APIKey = "your-api-key"
    {{/if}}
    
    // Create client
    client := {{packageName}}.NewClient(config)
    
    // Make API calls
    ctx := context.Background()
    {{#each operations}}
    {{#if @first}}
    {{#if operationId}}
    result, err := client.{{pascalCase operationId}}(ctx)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Result: %+v\n", result)
    {{/if}}
    {{/if}}
    {{/each}}
}
```

## Error Handling

```go
result, err := client.SomeOperation(ctx)
if err != nil {
    if apiErr, ok := err.(*{{packageName}}.APIError); ok {
        fmt.Printf("API error %d: %s\n", apiErr.StatusCode, apiErr.Message)
    } else {
        fmt.Printf("Network error: %v\n", err)
    }
}
```

## Available Operations

{{#each operations}}
{{#if operationId}}
- `{{pascalCase operationId}}()` - {{#if summary}}{{summary}}{{else}}{{method}} {{path}}{{/if}}
{{/if}}
{{/each}}

## Configuration

The `Config` struct supports the following options:

- `BaseURL` - API base URL (default: `{{baseUrl}}`)
{{#if includeAuth}}
- `BearerToken` - Bearer token for authentication
- `APIKey` - API key for authentication
{{/if}}
{{#if includeResilience}}
- `Timeout` - Request timeout (default: 30s)
- `MaxRetries` - Maximum number of retries (default: 3)
- `RetryDelay` - Delay between retries (default: 1s)
{{/if}}

---

Generated by [MicroRapid](https://github.com/yourusername/microrapid)
"#,
    )?;

    Ok(())
}

/// Wrapper function for direct SDK generation (used by main.rs)
pub fn generate_go_sdk(
    spec: &UnifiedSpec,
    output_dir: &Path,
    package_name: Option<&str>,
    include_docs: bool,
    include_examples: bool,
) -> Result<()> {
    // Create SdkCommand for the internal generate function
    let cmd = SdkCommand {
        spec: output_dir.to_path_buf(), // This is a bit hacky but needed for logging
        lang: crate::cli::SdkLanguage::Go,
        output: output_dir.to_path_buf(),
        package_name: package_name.map(String::from),
        http_client: Some("net/http".to_string()),
        auth: true,
        pagination: true,
        resilience: true,
        docs: include_docs,
        examples: include_examples,
    };

    generate(cmd, spec.clone())
}
