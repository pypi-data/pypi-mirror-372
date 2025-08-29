use super::{spec_to_context, SdkCommand, TemplateEngine};
use crate::core::parser::UnifiedSpec;
use anyhow::Result;
use colored::*;
use serde_json::json;
use std::fs;
use std::path::{Path, PathBuf};

pub fn generate(cmd: SdkCommand, spec: UnifiedSpec) -> Result<()> {
    println!(
        "🔨 {} TypeScript SDK Generation",
        "MicroRapid".bright_cyan()
    );
    println!("📄 Spec: {}", cmd.spec.display());
    println!("📁 Output: {}", cmd.output.display());

    // Create output directory
    fs::create_dir_all(&cmd.output)?;

    // Convert spec to template context
    let context = spec_to_context(spec)?;

    // Create templates directory (embedded templates would be better)
    let templates_dir = create_typescript_templates(&cmd.output)?;

    // Initialize template engine
    let mut engine = TemplateEngine::new(templates_dir.clone())?;

    // Generate files
    generate_client_file(&mut engine, &context, &cmd)?;
    generate_models_file(&mut engine, &context, &cmd)?;
    generate_types_file(&mut engine, &context, &cmd)?;
    generate_package_json(&mut engine, &context, &cmd)?;
    generate_readme(&mut engine, &context, &cmd)?;

    // Clean up templates directory
    let _ = fs::remove_dir_all(&templates_dir);

    println!("✅ TypeScript SDK generated successfully!");
    println!("📦 Files generated:");
    println!("   • client.ts - Main API client");
    println!("   • models.ts - Type definitions");
    println!("   • types.ts - Common types");
    println!("   • package.json - Package configuration");
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
        "httpClient": cmd.http_client.as_deref().unwrap_or("fetch"),
        "includeAuth": cmd.auth,
        "includePagination": cmd.pagination,
        "includeResilience": cmd.resilience,
    });

    let output_path = cmd.output.join("client.ts");
    engine.render_to_file("client.ts.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_models_file(
    engine: &mut TemplateEngine,
    context: &super::SdkContext,
    _cmd: &SdkCommand,
) -> Result<()> {
    let template_context = json!({
        "models": context.models,
    });

    let output_path = _cmd.output.join("models.ts");
    engine.render_to_file("models.ts.hbs", &template_context, &output_path)?;
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

    let output_path = cmd.output.join("types.ts");
    engine.render_to_file("types.ts.hbs", &template_context, &output_path)?;
    Ok(())
}

fn generate_package_json(
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
        "httpClient": cmd.http_client.as_deref().unwrap_or("fetch"),
    });

    let output_path = cmd.output.join("package.json");
    engine.render_to_file("package.json.hbs", &template_context, &output_path)?;
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
    });

    let output_path = cmd.output.join("README.md");
    engine.render_to_file("README.md.hbs", &template_context, &output_path)?;
    Ok(())
}

/// Create TypeScript templates (in production, these would be embedded)
fn create_typescript_templates(_output_dir: &PathBuf) -> Result<PathBuf> {
    // Use system temp directory instead of output directory
    let temp_dir =
        std::env::temp_dir().join(format!("mrapids-ts-templates-{}", std::process::id()));
    fs::create_dir_all(&temp_dir)?;

    // Always use embedded templates
    create_embedded_templates(&temp_dir)?;

    Ok(temp_dir)
}

/// Create embedded templates as fallback
fn create_embedded_templates(templates_dir: &PathBuf) -> Result<()> {
    // Basic client template
    fs::write(
        templates_dir.join("client.ts.hbs"),
        r#"
/**
 * {{info.title}} API Client
 * Generated by MicroRapid
 */

export class ApiClient {
    private baseUrl: string;
    
    constructor(config: { baseUrl?: string } = {}) {
        this.baseUrl = config.baseUrl || '{{baseUrl}}';
    }
    
    private async request<T>(method: string, path: string, options: any = {}): Promise<T> {
        const url = new URL(path, this.baseUrl);
        
        const response = await fetch(url.toString(), {
            method,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            body: options.body ? JSON.stringify(options.body) : undefined,
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return response.json();
    }
    
    {{#each operations}}
    {{#if operationId}}
    async {{operationId}}(): Promise<any> {
        return this.request('{{method}}', '{{path}}');
    }
    {{else}}
    // Warning: Operation {{method}} {{path}} has no operationId
    {{/if}}
    {{/each}}
}
"#,
    )?;

    // Basic models template
    fs::write(
        templates_dir.join("models.ts.hbs"),
        r#"
/**
 * {{info.title}} API Models
 */

{{#each models}}
export interface {{pascalCase name}} {
    {{#each properties}}
    {{name}}: any;
    {{/each}}
}
{{/each}}
"#,
    )?;

    // Basic types template
    fs::write(
        templates_dir.join("types.ts.hbs"),
        r#"
/**
 * {{info.title}} API Types
 */

export interface ApiConfig {
    baseUrl?: string;
}

export class ApiError extends Error {
    constructor(message: string, public status: number) {
        super(message);
        this.name = 'ApiError';
    }
}
"#,
    )?;

    // Basic package.json template
    fs::write(
        templates_dir.join("package.json.hbs"),
        r#"
{
  "name": "{{packageName}}",
  "version": "{{version}}",
  "description": "TypeScript SDK for {{packageName}}",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "dependencies": {},
  "devDependencies": {
    "typescript": "^5.0.0"
  }
}
"#,
    )?;

    // Basic README template
    fs::write(
        templates_dir.join("README.md.hbs"),
        r#"
# {{title}} TypeScript SDK

Version: {{version}}

## Installation

```bash
npm install {{packageName}}
```

## Usage

```typescript
import { ApiClient } from '{{packageName}}';

const api = new ApiClient({
  baseUrl: '{{baseUrl}}'
});
```
"#,
    )?;

    Ok(())
}

/// Wrapper function for direct SDK generation (used by main.rs)
pub fn generate_typescript_sdk(
    spec: &UnifiedSpec,
    output_dir: &Path,
    package_name: Option<&str>,
    include_docs: bool,
    include_examples: bool,
) -> Result<()> {
    // Create SdkCommand for the internal generate function
    let cmd = SdkCommand {
        spec: output_dir.to_path_buf(), // This is a bit hacky but needed for logging
        lang: crate::cli::SdkLanguage::Typescript,
        output: output_dir.to_path_buf(),
        package_name: package_name.map(String::from),
        http_client: Some("fetch".to_string()),
        auth: true,
        pagination: true,
        resilience: true,
        docs: include_docs,
        examples: include_examples,
    };

    generate(cmd, spec.clone())
}
