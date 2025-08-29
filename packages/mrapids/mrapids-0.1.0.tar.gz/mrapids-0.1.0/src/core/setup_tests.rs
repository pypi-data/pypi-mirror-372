use crate::cli::{SetupTestsCommand, TestSetupFormat};
use crate::core::parser::{parse_spec, UnifiedSpec};
use anyhow::Result;
use colored::*;
use serde_json::json;
use std::fs;

pub fn setup_tests_command(cmd: SetupTestsCommand) -> Result<()> {
    eprintln!("DEBUG: scaffold_command called");
    println!("🛠️  {} Setup Tests", "MicroRapid".bright_cyan());
    println!(
        "📄 Loading spec from: {}",
        cmd.spec.display().to_string().cyan()
    );

    eprintln!("DEBUG: About to read file...");
    // Load and parse the spec using the unified parser
    let content = match fs::read_to_string(&cmd.spec) {
        Ok(c) => {
            eprintln!("DEBUG: File read successfully, {} bytes", c.len());
            c
        }
        Err(e) => {
            eprintln!("DEBUG: File read failed: {}", e);
            return Err(anyhow::anyhow!("Cannot read spec file: {}", e));
        }
    };

    eprintln!("DEBUG: About to call parse_spec...");
    let spec = match parse_spec(&content) {
        Ok(s) => {
            eprintln!("DEBUG: parse_spec succeeded");
            s
        }
        Err(e) => {
            eprintln!("DEBUG: parse_spec failed with: {}", e);
            return Err(e);
        }
    };

    // Generate based on format
    match cmd.format {
        TestSetupFormat::Npm => generate_npm(&spec, &cmd)?,
        TestSetupFormat::Make => generate_makefile(&spec, &cmd)?,
        TestSetupFormat::Shell => generate_shell(&spec, &cmd)?,
        TestSetupFormat::Compose => generate_compose(&spec, &cmd)?,
        TestSetupFormat::Curl => generate_curl(&spec, &cmd)?,
        TestSetupFormat::All => {
            generate_npm(&spec, &cmd)?;
            generate_makefile(&spec, &cmd)?;
            generate_shell(&spec, &cmd)?;
            generate_compose(&spec, &cmd)?;
            generate_curl(&spec, &cmd)?;
        }
    }

    // Generate .env.example if requested
    if cmd.with_env {
        generate_env_example(&spec, &cmd)?;
    }

    if !cmd.dry_run {
        println!("\n✅ Test setup complete!");
        match cmd.format {
            TestSetupFormat::Npm => {
                println!("📦 Run: npm install && npm run api:list");
            }
            TestSetupFormat::Make => {
                println!("📦 Run: make help");
            }
            TestSetupFormat::Shell => {
                println!("📦 Run: chmod +x api-test.sh && ./api-test.sh help");
            }
            TestSetupFormat::Compose => {
                println!("📦 Run: docker-compose run --rm api-test help");
            }
            TestSetupFormat::Curl => {
                println!("📦 Run: chmod +x api-curl.sh && ./api-curl.sh help");
            }
            TestSetupFormat::All => {
                println!("📦 Multiple formats generated. Choose your preferred format.");
            }
        }
    }

    Ok(())
}

fn generate_npm(spec: &UnifiedSpec, cmd: &SetupTestsCommand) -> Result<()> {
    let mut scripts = serde_json::Map::new();

    // Base command
    let spec_path = cmd.spec.display().to_string();
    scripts.insert(
        "api".to_string(),
        json!(format!("mrapids run {}", spec_path)),
    );
    scripts.insert(
        "api:list".to_string(),
        json!("echo 'Available API commands:' && npm run | grep 'api:' | grep -v 'api:list'"),
    );

    // Generate script for each operation
    for operation in &spec.operations {
        let method = operation.method.to_lowercase();
        let script_name = format!("api:{}", to_kebab_case(&operation.operation_id));

        let command = format!("npm run api -- --operation {}", operation.operation_id);

        // Add data parameter hint
        let mut final_command = command.clone();
        if method != "get" && method != "delete" {
            final_command.push_str(" --data");
        }

        scripts.insert(script_name, json!(final_command));
    }

    // Add test commands
    scripts.insert(
        "test:all".to_string(),
        json!(format!("mrapids test {} --all", spec_path)),
    );

    // Create usage info
    let mut scripts_info = serde_json::Map::new();
    scripts_info.insert(
        "api:list".to_string(),
        json!("List all available API commands"),
    );
    scripts_info.insert("test:all".to_string(), json!("Run all API tests"));
    scripts_info.insert("_note".to_string(), json!("For paths with {parameters}, manually replace them. Example: --path /pet/{petId} → --path /pet/123. For better support, use 'mrapids scaffold --format curl'"));

    let package_json = json!({
        "name": "api-tests",
        "version": "1.0.0",
        "description": format!("{} - API Test Scripts", spec.info.title),
        "scripts": scripts,
        "scripts-info": scripts_info
    });

    let output_file = if cmd.output.is_dir() {
        cmd.output.join("package.json")
    } else {
        cmd.output.clone()
    };

    if cmd.dry_run {
        println!("Would generate: {}", output_file.display());
        println!("{}", serde_json::to_string_pretty(&package_json)?);
    } else {
        fs::write(&output_file, serde_json::to_string_pretty(&package_json)?)?;
        println!(
            "  ✅ Generated: {}",
            output_file.display().to_string().green()
        );
    }

    Ok(())
}

fn generate_makefile(spec: &UnifiedSpec, cmd: &SetupTestsCommand) -> Result<()> {
    let mut content = String::new();

    // Header
    content.push_str(&format!(
        r#"# {} - API Test Commands
# Generated from: {}
# Generated by: MicroRapid

API := mrapids run {}

.PHONY: help
help:
	@echo "Available commands:"
"#,
        spec.info.title,
        cmd.spec.display(),
        cmd.spec.display()
    ));

    // Generate targets for each operation
    let mut targets = Vec::new();

    for operation in &spec.operations {
        let target_name = to_snake_case(&operation.operation_id);
        targets.push(target_name.clone());

        // Add to help
        let default_desc = format!("{} {}", operation.method.to_uppercase(), operation.path);
        let description = operation.summary.as_deref().unwrap_or(&default_desc);
        content.push_str(&format!(
            "\t@echo \"  make {} - {}\"\n",
            target_name, description
        ));

        // Add target
        content.push_str(&format!("\n.PHONY: {}\n{}:\n", target_name, target_name));
        content.push_str(&format!("\t$(API) --operation {}", operation.operation_id));

        // Add parameter placeholders
        let method = operation.method.to_lowercase();
        if method != "get" && method != "delete" {
            content.push_str(" --data '$(DATA)'");
        }

        content.push_str("\n");
    }

    // Add test-all target
    content.push_str(&format!(
        r#"
.PHONY: test-all
test-all:
	mrapids test {} --all

.PHONY: list
list:
	@echo "Available targets:"
	@echo "{}"
"#,
        cmd.spec.display(),
        targets.join(" ")
    ));

    let output_file = if cmd.output.is_dir() {
        cmd.output.join("Makefile")
    } else {
        cmd.output.clone()
    };

    if cmd.dry_run {
        println!("Would generate: {}", output_file.display());
        println!("{}", content);
    } else {
        fs::write(&output_file, content)?;
        println!(
            "  ✅ Generated: {}",
            output_file.display().to_string().green()
        );
    }

    Ok(())
}

fn generate_shell(spec: &UnifiedSpec, cmd: &SetupTestsCommand) -> Result<()> {
    let mut content = String::new();

    // Header
    content.push_str(&format!(
        r#"#!/bin/bash
# {} - API Test Commands
# Generated from: {}
# Generated by: MicroRapid

BASE_CMD="mrapids run {}"

# Show help
show_help() {{
    echo "Usage: $0 <command> [options]"
    echo ""
    echo "Available commands:"
"#,
        spec.info.title,
        cmd.spec.display(),
        cmd.spec.display()
    ));

    // Collect all operations
    let mut operations = Vec::new();

    for operation in &spec.operations {
        let cmd_name = to_kebab_case(&operation.operation_id);
        let default_desc = format!("{} {}", operation.method.to_uppercase(), operation.path);
        let description = operation.summary.as_deref().unwrap_or(&default_desc);
        operations.push((
            cmd_name.clone(),
            operation.operation_id.clone(),
            operation.method.to_lowercase(),
            operation.path.clone(),
            description.to_string(),
        ));

        // Add to help
        content.push_str(&format!("    echo \"  {} - {}\"\n", cmd_name, description));
    }

    content.push_str(
        r#"    echo ""
    echo "Examples:"
    echo "  $0 list-users"
    echo "  $0 get-user 123"
    echo "  $0 create-user '{\"name\":\"John\"}'"
}

# Main command switch
case "${1:-help}" in
"#,
    );

    // Generate case statements
    for (cmd_name, op_id, method, _path, _description) in &operations {
        content.push_str(&format!("    {})\n", cmd_name));
        content.push_str(&format!("        $BASE_CMD --operation {}", op_id));

        // Handle parameters
        if method != "get" && method != "delete" {
            content.push_str(" --data \"${2:-'{}'}\"");
            content.push_str(" \"${@:3}\"");
        } else {
            content.push_str(" \"${@:2}\"");
        }

        content.push_str("\n        ;;\n");
    }

    content.push_str(
        r#"    help|*)
        show_help
        ;;
esac
"#,
    );

    let output_file = if cmd.output.is_dir() {
        cmd.output.join("api-test.sh")
    } else {
        cmd.output.clone()
    };

    if cmd.dry_run {
        println!("Would generate: {}", output_file.display());
        println!("{}", content);
    } else {
        fs::write(&output_file, content)?;

        // Make executable on Unix
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(&output_file)?.permissions();
            perms.set_mode(0o755);
            fs::set_permissions(&output_file, perms)?;
        }

        println!(
            "  ✅ Generated: {}",
            output_file.display().to_string().green()
        );
    }

    Ok(())
}

fn generate_compose(spec: &UnifiedSpec, cmd: &SetupTestsCommand) -> Result<()> {
    let mut services = serde_json::Map::new();

    // Base service
    services.insert(
        "api-test".to_string(),
        json!({
            "image": "mrapids:latest",
            "volumes": [
                format!("./{}:/api.yaml:ro", cmd.spec.display())
            ],
            "environment": [
                "API_BASE_URL=${API_BASE_URL:-http://localhost:8080}",
                "API_KEY=${API_KEY}"
            ]
        }),
    );

    // Generate service for each operation
    for operation in &spec.operations {
        let service_name = to_kebab_case(&operation.operation_id);
        let command = format!("run /api.yaml --operation {}", operation.operation_id);

        services.insert(
            service_name,
            json!({
                "extends": "api-test",
                "command": command
            }),
        );
    }

    let compose = json!({
        "version": "3.8",
        "services": services
    });

    let output_file = if cmd.output.is_dir() {
        cmd.output.join("docker-compose.yml")
    } else {
        cmd.output.clone()
    };

    if cmd.dry_run {
        println!("Would generate: {}", output_file.display());
        println!("{}", serde_yaml::to_string(&compose)?);
    } else {
        fs::write(&output_file, serde_yaml::to_string(&compose)?)?;
        println!(
            "  ✅ Generated: {}",
            output_file.display().to_string().green()
        );
    }

    Ok(())
}

fn generate_curl(spec: &UnifiedSpec, cmd: &SetupTestsCommand) -> Result<()> {
    let mut content = String::new();

    // Header
    content.push_str(&format!(
        r#"#!/bin/bash
# {} - Direct API Calls
# Generated from: {}
# Generated by: MicroRapid

BASE_URL="${{API_BASE_URL:-{}}}"
AUTH_HEADER="${{API_KEY:+Authorization: Bearer $API_KEY}}"

"#,
        spec.info.title,
        cmd.spec.display(),
        spec.get_base_url()
    ));

    // Generate functions for each operation
    for operation in &spec.operations {
        let func_name = to_snake_case(&operation.operation_id);
        let method = operation.method.to_uppercase();
        let path = &operation.path;

        let default_desc = format!("{} {}", method, path);
        let description = operation.summary.as_deref().unwrap_or(&default_desc);

        content.push_str(&format!("# {}\n", description));
        content.push_str(&format!("{}() {{\n", func_name));

        // Build the curl command
        content.push_str(&format!("    curl -X {} \\\n", method));

        // Handle path parameters - replace all {param} patterns
        let url_path = if has_path_params(path) {
            // Use regex to replace all {param} patterns with ${1:-123}
            let mut result = String::new();
            let mut chars = path.chars().peekable();
            let mut in_param = false;

            while let Some(ch) = chars.next() {
                if ch == '{' {
                    in_param = true;
                    result.push_str("${1:-123}");
                } else if ch == '}' {
                    in_param = false;
                } else if !in_param {
                    result.push(ch);
                }
            }
            result
        } else {
            path.clone()
        };

        content.push_str(&format!("        \"${{BASE_URL}}{}\" \\\n", url_path));
        content.push_str("        ${AUTH_HEADER:+-H \"$AUTH_HEADER\"} \\\n");

        if method != "GET" && method != "DELETE" {
            content.push_str("        -H \"Content-Type: application/json\" \\\n");
            if has_path_params(path) {
                content.push_str("        -d \"${2:-'{}'}\" \\\n");
                content.push_str("        \"${@:3}\"\n");
            } else {
                content.push_str("        -d \"${1:-'{}'}\" \\\n");
                content.push_str("        \"${@:2}\"\n");
            }
        } else {
            content.push_str("        \"${@:2}\"\n");
        }

        content.push_str("}\n\n");
    }

    // Add main switch
    content.push_str(
        r#"# Show usage
show_usage() {
    echo "Usage: $0 <function> [arguments]"
    echo ""
    echo "Available functions:"
"#,
    );

    for operation in &spec.operations {
        let func_name = to_snake_case(&operation.operation_id);
        let method = operation.method.to_uppercase();
        let path = &operation.path;

        let default_desc = format!("{} {}", method, path);
        let description = operation.summary.as_deref().unwrap_or(&default_desc);

        // Add usage hint based on method
        let usage_hint = if method == "POST" || method == "PUT" || method == "PATCH" {
            if has_path_params(path) {
                format!(" <id> <json_data>")
            } else {
                format!(" <json_data>")
            }
        } else if has_path_params(path) {
            format!(" <id>")
        } else {
            String::new()
        };

        content.push_str(&format!(
            "    echo \"  {}{}  - {}\"\n",
            func_name, usage_hint, description
        ));
    }

    content.push_str(
        r#"    echo ""
    echo "Examples:"
    echo "  $0 list_users"
    echo "  $0 get_user 123"
    echo "  $0 add_pet '{\"name\":\"Fluffy\",\"status\":\"available\"}'"
    echo "  $0 update_pet 123 '{\"name\":\"Fluffy Updated\"}'"
}

# Main
if [ $# -eq 0 ]; then
    show_usage
else
    # Call the function if it exists
    if declare -f "$1" > /dev/null; then
        "$@"
    else
        echo "Unknown function: $1"
        echo ""
        show_usage
        exit 1
    fi
fi
"#,
    );

    let output_file = if cmd.output.is_dir() {
        cmd.output.join("api-curl.sh")
    } else {
        cmd.output.clone()
    };

    if cmd.dry_run {
        println!("Would generate: {}", output_file.display());
        println!("{}", content);
    } else {
        fs::write(&output_file, content)?;

        // Make executable on Unix
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(&output_file)?.permissions();
            perms.set_mode(0o755);
            fs::set_permissions(&output_file, perms)?;
        }

        println!(
            "  ✅ Generated: {}",
            output_file.display().to_string().green()
        );
    }

    Ok(())
}

fn generate_env_example(spec: &UnifiedSpec, cmd: &SetupTestsCommand) -> Result<()> {
    let content = format!(
        r#"# API Configuration
# Generated from: {}

# Base URL for API calls
API_BASE_URL={}

# Authentication
API_KEY=your-api-key-here
# API_TOKEN=your-token-here
# API_SECRET=your-secret-here

# Test Data
TEST_USER_ID=123
TEST_USER_NAME=John Doe
TEST_USER_EMAIL=john@example.com

# Environment
NODE_ENV=development
DEBUG=false
"#,
        cmd.spec.display(),
        spec.base_url
    );

    let output_file = cmd.output.join(".env.example");

    if cmd.dry_run {
        println!("Would generate: {}", output_file.display());
        println!("{}", content);
    } else {
        fs::write(&output_file, content)?;
        println!(
            "  ✅ Generated: {}",
            output_file.display().to_string().green()
        );
    }

    Ok(())
}

// Helper functions
fn has_path_params(path: &str) -> bool {
    path.contains('{') && path.contains('}')
}

fn to_kebab_case(s: &str) -> String {
    let mut result = String::new();
    for (i, ch) in s.chars().enumerate() {
        if ch.is_uppercase() && i > 0 {
            result.push('-');
        }
        result.push(ch.to_lowercase().next().unwrap());
    }
    result
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
