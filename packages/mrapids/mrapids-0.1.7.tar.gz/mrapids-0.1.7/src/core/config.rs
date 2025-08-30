// Environment-based configuration management
use anyhow::{Context, Result};
use colored::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Config {
    pub name: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub defaults: Option<DefaultsConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub headers: Option<HashMap<String, String>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub auth: Option<AuthConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub safety: Option<SafetyConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub rate_limit: Option<RateLimitConfig>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub monitoring: Option<MonitoringConfig>,
    #[serde(default)]
    pub apis: HashMap<String, ApiConfig>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct MultiEnvConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub defaults: Option<DefaultsConfig>,
    pub environments: HashMap<String, EnvironmentConfig>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct DefaultsConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub output: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub retry: Option<RetryConfig>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct RetryConfig {
    pub enabled: bool,
    pub max_attempts: u32,
    pub backoff: String, // "exponential", "linear", "constant"
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct RateLimitConfig {
    pub requests_per_second: u32,
    pub burst: u32,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct MonitoringConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub trace_id_header: Option<String>,
    pub log_requests: bool,
    pub log_responses: bool,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct EnvironmentConfig {
    #[serde(skip_serializing_if = "Option::is_none")]
    pub safety: Option<SafetyConfig>,
    #[serde(flatten)]
    pub apis: HashMap<String, ApiConfig>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct SafetyConfig {
    #[serde(default)]
    pub require_confirmation: bool,
    #[serde(default)]
    pub audit_log: bool,
    #[serde(default)]
    pub dry_run_default: bool,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ApiConfig {
    pub base_url: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub auth: Option<AuthConfig>,
    #[serde(default)]
    pub headers: HashMap<String, String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub content_type: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timeout: Option<u64>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum AuthConfig {
    Bearer {
        token: String,
    },
    Basic {
        username: String,
        password: String,
    },
    ApiKey {
        header: String,
        key: String,
    },
    OAuth2 {
        client_id: String,
        client_secret: String,
        token_url: Option<String>,
    },
}

/// Load configuration for the specified environment
pub fn load_config(env_name: &str, custom_path: Option<&Path>) -> Result<Config> {
    // If custom path provided, use it directly
    if let Some(path) = custom_path {
        return load_config_from_file(path, env_name);
    }

    // Build possible config paths
    let config_paths = build_config_paths(env_name);

    // Find first existing config
    let config_path = config_paths.iter().find(|p| p.exists()).ok_or_else(|| {
        anyhow::anyhow!(
            "No config found for environment '{}'\n\
                Searched locations:\n{}\n\n\
                Create a config file with: mrapids init-config --env {}",
            env_name,
            config_paths
                .iter()
                .map(|p| format!("  - {}", p.display()))
                .collect::<Vec<_>>()
                .join("\n"),
            env_name
        )
    })?;

    load_config_from_file(config_path, env_name)
}

/// Load configuration from a specific file
fn load_config_from_file(path: &Path, env_name: &str) -> Result<Config> {
    println!(
        "📋 Loading config: {} ({})",
        path.display().to_string().cyan(),
        env_name.yellow()
    );

    // Read config file
    let config_content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read config file: {}", path.display()))?;

    // Load .env files in priority order:
    // 1. Workspace-level .env (project root)
    // 2. Config directory .env
    // 3. Environment-specific .env

    let workspace_env = PathBuf::from(".env");
    if workspace_env.exists() {
        println!(
            "📄 Loading workspace .env: {}",
            workspace_env.display().to_string().dimmed()
        );
        load_env_file(&workspace_env)?;
    }

    let config_dir_env =
        if path.parent().and_then(|p| p.file_name()) == Some(std::ffi::OsStr::new("config")) {
            // If config is in config/ folder, look for .env there
            path.parent().unwrap().join(".env")
        } else {
            // Otherwise look next to the config file
            path.with_extension("env")
        };

    if config_dir_env.exists() {
        println!(
            "📄 Loading config .env: {}",
            config_dir_env.display().to_string().dimmed()
        );
        load_env_file(&config_dir_env)?;
    }

    // Also check for environment-specific .env files
    let env_specific = config_dir_env.with_file_name(format!(".env.{}", env_name));
    if env_specific.exists() {
        println!(
            "📄 Loading env-specific .env: {}",
            env_specific.display().to_string().dimmed()
        );
        load_env_file(&env_specific)?;
    }

    // Parse config with environment variable substitution
    let expanded_content = substitute_env_vars(&config_content)?;

    // Check if it's a multi-environment config
    if expanded_content.contains("environments:") && !expanded_content.contains("name:") {
        // Multi-env config file
        let multi_config: MultiEnvConfig =
            serde_yaml::from_str(&expanded_content).with_context(|| {
                format!("Failed to parse multi-env config file: {}", path.display())
            })?;

        // Extract the specific environment
        let env_config = multi_config.environments.get(env_name).ok_or_else(|| {
            anyhow::anyhow!(
                "Environment '{}' not found in config. Available: {}",
                env_name,
                multi_config
                    .environments
                    .keys()
                    .cloned()
                    .collect::<Vec<_>>()
                    .join(", ")
            )
        })?;

        // Build Config from EnvironmentConfig
        Ok(Config {
            name: env_name.to_string(),
            defaults: None,
            headers: None,
            auth: None,
            safety: env_config.safety.clone(),
            rate_limit: None,
            monitoring: None,
            apis: env_config.apis.clone(),
        })
    } else {
        // Single environment config file
        let config: Config = serde_yaml::from_str(&expanded_content)
            .with_context(|| format!("Failed to parse config file: {}", path.display()))?;
        Ok(config)
    }
}

/// Build possible config paths in priority order
fn build_config_paths(env_name: &str) -> Vec<PathBuf> {
    let mut paths = Vec::new();

    // 1. Workspace-level config (highest priority)
    paths.push(PathBuf::from(format!("config/{}.yaml", env_name)));
    paths.push(PathBuf::from(format!("config/{}.yml", env_name)));

    // 2. Parent directories (for monorepos)
    let mut current = env::current_dir().ok();
    let mut depth = 0;
    while let Some(dir) = current {
        if depth > 5 {
            break;
        } // Don't go too deep
        if let Some(parent) = dir.parent() {
            let config_path = parent.join("config").join(format!("{}.yaml", env_name));
            if config_path.exists() {
                paths.push(config_path);
            }
            current = Some(parent.to_path_buf());
            depth += 1;
        } else {
            break;
        }
    }

    // 3. User home configs (global fallback)
    if let Some(home) = dirs::home_dir() {
        paths.push(home.join(format!(".mrapids/config/{}.yaml", env_name)));
    }

    // 4. System-wide configs (last resort)
    paths.push(PathBuf::from(format!("/etc/mrapids/{}.yaml", env_name)));

    paths
}

/// Load environment variables from a .env file
fn load_env_file(path: &Path) -> Result<()> {
    println!(
        "🔐 Loading environment variables from: {}",
        path.display().to_string().dimmed()
    );

    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read env file: {}", path.display()))?;

    for line in content.lines() {
        let line = line.trim();

        // Skip comments and empty lines
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        // Parse KEY=value
        if let Some((key, value)) = line.split_once('=') {
            let key = key.trim();
            let value = value.trim().trim_matches('"').trim_matches('\'');
            env::set_var(key, value);
        }
    }

    Ok(())
}

/// Substitute environment variables in the config content
fn substitute_env_vars(content: &str) -> Result<String> {
    let mut result = content.to_string();

    // Find all ${VAR} or ${VAR:default} patterns
    let re = regex::Regex::new(r"\$\{([^}:]+)(?::([^}]*))?\}")?;

    for cap in re.captures_iter(content) {
        let var_name = &cap[1];
        let default_value = cap.get(2).map(|m| m.as_str());

        let value = if let Ok(val) = env::var(var_name) {
            val
        } else if let Some(default) = default_value {
            default.to_string()
        } else {
            return Err(anyhow::anyhow!(
                "Environment variable '{}' not set and no default provided\n\
                Set it in your shell: export {}=value\n\
                Or provide a default: ${{{}:default_value}}",
                var_name,
                var_name,
                var_name
            ));
        };

        let pattern = &cap[0];
        result = result.replace(pattern, &value);
    }

    Ok(result)
}

/// Get API configuration for a specific API in the environment
pub fn _get_api_config<'a>(config: &'a Config, api_name: &str) -> Result<&'a ApiConfig> {
    config.apis.get(api_name).ok_or_else(|| {
        anyhow::anyhow!(
            "API '{}' not configured in environment '{}'\n\
                Available APIs: {}",
            api_name,
            config.name,
            config.apis.keys().cloned().collect::<Vec<_>>().join(", ")
        )
    })
}

/// Check if an operation requires confirmation (for production safety)
pub fn _requires_confirmation(config: &Config, _operation: &str, method: &str) -> bool {
    if let Some(safety) = &config.safety {
        if safety.require_confirmation {
            // Require confirmation for destructive operations in production
            matches!(
                method.to_uppercase().as_str(),
                "DELETE" | "PUT" | "PATCH" | "POST"
            )
        } else {
            false
        }
    } else {
        false
    }
}

/// Prompt user for confirmation
pub fn _confirm_operation(env_name: &str, api_name: &str, operation: &str) -> Result<bool> {
    use std::io::{self, Write};

    println!(
        "\n{} {} WARNING: Executing operation in {}",
        "🔴".red(),
        "[PRODUCTION]".red().bold(),
        env_name.to_uppercase().red()
    );
    println!("    API: {}", api_name.yellow());
    println!("    Operation: {}", operation.yellow());
    println!();
    print!("Type 'yes' to confirm: ");
    io::stdout().flush()?;

    let mut input = String::new();
    io::stdin().read_line(&mut input)?;

    Ok(input.trim().eq_ignore_ascii_case("yes"))
}

/// Get environment indicator emoji and color
pub fn _get_env_indicator(env_name: &str) -> (&str, Color) {
    match env_name.to_lowercase().as_str() {
        "production" | "prod" => ("🔴", Color::Red),
        "staging" | "stage" => ("🟡", Color::Yellow),
        "development" | "dev" => ("🟢", Color::Green),
        "local" => ("🔵", Color::Blue),
        "test" | "testing" => ("🟣", Color::Magenta),
        _ => ("⚪", Color::White),
    }
}

/// Initialize a new config file for an environment
pub fn init_config(
    env_name: &str,
    api_name: Option<&str>,
    output_path: Option<&Path>,
) -> Result<()> {
    // Determine output path - create separate file per environment
    let config_path = if let Some(path) = output_path {
        path.to_path_buf()
    } else {
        // Check if we're in a project with config/ folder
        let project_config = PathBuf::from("config");
        if !project_config.exists() {
            // Create config folder if it doesn't exist
            fs::create_dir_all(&project_config)?;
        }
        // Use separate file for each environment
        project_config.join(format!("{}.yaml", env_name))
    };

    // Create config for this environment
    let config = if let Some(api) = api_name {
        create_config_with_api(env_name, api)?
    } else {
        create_default_config(env_name)?
    };

    // Write config file with comprehensive comments
    let yaml = generate_config_with_comments(&config, env_name, api_name)?;
    fs::write(&config_path, yaml)?;

    println!(
        "✅ Created config file: {}",
        config_path.display().to_string().green()
    );

    // Create or update .env in config folder
    let env_file = config_path
        .parent()
        .map(|p| p.join(".env"))
        .unwrap_or_else(|| PathBuf::from("config/.env"));

    let env_example = config_path
        .parent()
        .map(|p| p.join(".env.example"))
        .unwrap_or_else(|| PathBuf::from("config/.env.example"));

    // Create .env.example if it doesn't exist or update it
    if !env_example.exists() || api_name.is_some() {
        let current_template = if env_example.exists() {
            fs::read_to_string(&env_example).unwrap_or_default()
        } else {
            String::new()
        };

        let additional_template = create_env_template(env_name, api_name);
        let updated_template = if current_template.is_empty() {
            additional_template
        } else if !current_template.contains(&additional_template) {
            format!("{}\n{}", current_template.trim(), additional_template)
        } else {
            current_template
        };

        fs::write(&env_example, updated_template)?;
        if !env_example.exists() {
            println!(
                "📝 Created env template: {}",
                env_example.display().to_string().green()
            );
        }
    }

    // Create .env if it doesn't exist
    if !env_file.exists() {
        let env_template = create_env_template(env_name, api_name);
        fs::write(&env_file, env_template)?;
        println!(
            "🔐 Created env file: {}",
            env_file.display().to_string().green()
        );
        println!(
            "\n⚠️  Remember to add {} to .gitignore!",
            env_file.display()
        );
    }

    println!("\nNext steps:");
    println!("  1. Edit {} to add your API keys", env_file.display());
    println!(
        "  2. Run: mrapids run {}:<operation> --env {}",
        api_name.unwrap_or("api_name"),
        env_name
    );

    Ok(())
}

/// Create a default config for an environment with all options documented
fn create_default_config(env_name: &str) -> Result<Config> {
    let is_production = env_name.to_lowercase().contains("prod");
    let is_staging = env_name.to_lowercase().contains("stag");

    Ok(Config {
        name: env_name.to_string(),
        defaults: Some(DefaultsConfig {
            timeout: Some(if is_production { 30 } else { 60 }),
            output: Some("pretty".to_string()),
            retry: Some(RetryConfig {
                enabled: true,
                max_attempts: if is_production { 2 } else { 3 },
                backoff: "exponential".to_string(),
            }),
        }),
        headers: Some({
            let mut headers = HashMap::new();
            headers.insert(
                "User-Agent".to_string(),
                format!(
                    "MicroRapid/1.0 ({})",
                    if is_production {
                        "Production"
                    } else if is_staging {
                        "Staging"
                    } else {
                        "Development"
                    }
                ),
            );
            if !is_production {
                headers.insert("X-Environment".to_string(), env_name.to_string());
            }
            headers
        }),
        auth: None, // Will be set per API or globally by user
        safety: if is_production {
            Some(SafetyConfig {
                require_confirmation: true,
                audit_log: true,
                dry_run_default: false,
            })
        } else {
            None
        },
        rate_limit: if is_production {
            Some(RateLimitConfig {
                requests_per_second: 10,
                burst: 20,
            })
        } else {
            None
        },
        monitoring: if is_production || is_staging {
            Some(MonitoringConfig {
                trace_id_header: Some("X-Trace-ID".to_string()),
                log_requests: true,
                log_responses: !is_production, // Don't log responses in production
            })
        } else {
            None
        },
        apis: HashMap::new(),
    })
}

/// Create a config with a specific API template
fn create_config_with_api(env_name: &str, api_name: &str) -> Result<Config> {
    let mut config = create_default_config(env_name)?;

    let api_config = match api_name.to_lowercase().as_str() {
        "stripe" => create_stripe_config(env_name),
        "github" => create_github_config(),
        "openai" => create_openai_config(),
        _ => create_generic_api_config(api_name),
    };

    config.apis.insert(api_name.to_string(), api_config);
    Ok(config)
}

/// Create Stripe API configuration
fn create_stripe_config(env_name: &str) -> ApiConfig {
    let is_production = env_name.to_lowercase().contains("prod");

    ApiConfig {
        base_url: "https://api.stripe.com/v1".to_string(),
        auth: Some(AuthConfig::Bearer {
            token: format!(
                "${{{}}}",
                if is_production {
                    "STRIPE_LIVE_KEY"
                } else {
                    "STRIPE_TEST_KEY"
                }
            ),
        }),
        headers: HashMap::new(),
        content_type: Some("application/x-www-form-urlencoded".to_string()),
        timeout: Some(30),
    }
}

/// Create GitHub API configuration
fn create_github_config() -> ApiConfig {
    ApiConfig {
        base_url: "https://api.github.com".to_string(),
        auth: Some(AuthConfig::Bearer {
            token: "${GITHUB_TOKEN}".to_string(),
        }),
        headers: {
            let mut headers = HashMap::new();
            headers.insert(
                "Accept".to_string(),
                "application/vnd.github.v3+json".to_string(),
            );
            headers
        },
        content_type: Some("application/json".to_string()),
        timeout: Some(30),
    }
}

/// Create OpenAI API configuration
fn create_openai_config() -> ApiConfig {
    ApiConfig {
        base_url: "https://api.openai.com/v1".to_string(),
        auth: Some(AuthConfig::Bearer {
            token: "${OPENAI_API_KEY}".to_string(),
        }),
        headers: HashMap::new(),
        content_type: Some("application/json".to_string()),
        timeout: Some(60),
    }
}

/// Create generic API configuration
fn create_generic_api_config(api_name: &str) -> ApiConfig {
    ApiConfig {
        base_url: format!("${{{}_BASE_URL}}", api_name.to_uppercase()),
        auth: Some(AuthConfig::Bearer {
            token: format!("${{{}_API_KEY}}", api_name.to_uppercase()),
        }),
        headers: HashMap::new(),
        content_type: Some("application/json".to_string()),
        timeout: Some(30),
    }
}

/// Generate config YAML with comprehensive comments
fn generate_config_with_comments(
    config: &Config,
    env_name: &str,
    _api_name: Option<&str>,
) -> Result<String> {
    let is_production = env_name.to_lowercase().contains("prod");

    let mut yaml = String::new();

    // Header comments
    yaml.push_str(&format!(
        "# {} environment configuration\n",
        capitalize_first(env_name)
    ));
    yaml.push_str("# Generated by MicroRapid - Your OpenAPI, but executable\n");
    yaml.push_str("# Documentation: https://github.com/yourorg/microrapid\n\n");

    yaml.push_str(&format!("name: {}\n\n", env_name));

    // Safety section (production only)
    if is_production {
        yaml.push_str("# Production safety settings\n");
        yaml.push_str("# These settings help prevent accidental destructive operations\n");
        yaml.push_str("safety:\n");
        yaml.push_str("  require_confirmation: true    # Confirm DELETE, PUT, PATCH operations\n");
        yaml.push_str("  audit_log: true              # Log all requests for audit trail\n");
        yaml.push_str("  dry_run_default: false       # Don't default to dry run\n\n");
    }

    // Defaults section
    yaml.push_str("# Default settings for all requests\n");
    yaml.push_str("# These can be overridden per request or per API\n");
    yaml.push_str("defaults:\n");
    yaml.push_str("  timeout: 30                  # Request timeout in seconds\n");
    yaml.push_str("  # output: pretty             # Output format: pretty, json, yaml, table\n");
    yaml.push_str("  retry:\n");
    yaml.push_str("    enabled: true\n");
    yaml.push_str("    max_attempts: 3            # Number of retry attempts\n");
    yaml.push_str(
        "    backoff: exponential       # Backoff strategy: exponential, linear, constant\n\n",
    );

    // Headers section
    yaml.push_str("# Headers applied to all requests\n");
    yaml.push_str("# Use environment variables with syntax: VAR_NAME or VAR_NAME:default\n");
    yaml.push_str("headers:\n");
    yaml.push_str(&format!(
        "  User-Agent: \"MicroRapid/1.0 ({})\"\n",
        capitalize_first(env_name)
    ));
    if !is_production {
        yaml.push_str(&format!("  X-Environment: \"{}\"\n", env_name));
    }
    yaml.push_str("  # X-Request-ID: \"REQUEST_ID_VALUE\"  # Uncomment for request tracking\n");
    yaml.push_str("  # X-API-Version: \"2024-01-01\"         # Uncomment for API versioning\n\n");

    // Global auth section
    yaml.push_str("# Default authentication (can be overridden per API)\n");
    yaml.push_str("# Uncomment and configure based on your auth type:\n");
    yaml.push_str("\n# Bearer token auth:\n");
    yaml.push_str("# auth:\n");
    yaml.push_str("#   type: bearer\n");
    yaml.push_str("#   token: YOUR_API_TOKEN\n");
    yaml.push_str("\n# Basic auth:\n");
    yaml.push_str("# auth:\n");
    yaml.push_str("#   type: basic\n");
    yaml.push_str("#   username: YOUR_USERNAME\n");
    yaml.push_str("#   password: YOUR_PASSWORD\n");
    yaml.push_str("\n# API Key auth:\n");
    yaml.push_str("# auth:\n");
    yaml.push_str("#   type: api_key\n");
    yaml.push_str("#   header: X-API-Key\n");
    yaml.push_str("#   key: YOUR_API_KEY\n\n");

    // Rate limiting section
    if is_production {
        yaml.push_str("# Rate limiting (production only by default)\n");
        yaml.push_str("rate_limit:\n");
        yaml.push_str("  requests_per_second: 10\n");
        yaml.push_str("  burst: 20                    # Allow burst up to this many requests\n\n");
    } else {
        yaml.push_str("# Rate limiting (uncomment to enable)\n");
        yaml.push_str("# rate_limit:\n");
        yaml.push_str("#   requests_per_second: 10\n");
        yaml.push_str("#   burst: 20\n\n");
    }

    // Monitoring section
    yaml.push_str("# Monitoring and observability\n");
    if is_production {
        yaml.push_str("monitoring:\n");
        yaml.push_str("  trace_id_header: X-Trace-ID  # Header for distributed tracing\n");
        yaml.push_str("  log_requests: true           # Log all requests\n");
        yaml.push_str("  log_responses: false         # Don't log response bodies (may contain sensitive data)\n\n");
    } else {
        yaml.push_str("# monitoring:\n");
        yaml.push_str("#   trace_id_header: X-Trace-ID\n");
        yaml.push_str("#   log_requests: true\n");
        yaml.push_str("#   log_responses: true        # Be careful in production!\n\n");
    }

    // APIs section
    yaml.push_str("# API-specific overrides (optional)\n");
    yaml.push_str("# Each API can have its own auth, headers, base_url, etc.\n");
    yaml.push_str("apis:\n");

    // Add configured APIs
    for (name, api_config) in &config.apis {
        yaml.push_str(&format!("  {}:\n", name));
        yaml.push_str(&format!("    base_url: {}\n", api_config.base_url));

        if let Some(auth) = &api_config.auth {
            yaml.push_str("    auth:\n");
            match auth {
                AuthConfig::Bearer { token } => {
                    yaml.push_str("      type: bearer\n");
                    yaml.push_str(&format!("      token: {}\n", token));
                }
                AuthConfig::Basic { username, password } => {
                    yaml.push_str("      type: basic\n");
                    yaml.push_str(&format!("      username: {}\n", username));
                    yaml.push_str(&format!("      password: {}\n", password));
                }
                AuthConfig::ApiKey { header, key } => {
                    yaml.push_str("      type: api_key\n");
                    yaml.push_str(&format!("      header: {}\n", header));
                    yaml.push_str(&format!("      key: {}\n", key));
                }
                AuthConfig::OAuth2 {
                    client_id,
                    client_secret,
                    token_url,
                } => {
                    yaml.push_str("      type: oauth2\n");
                    yaml.push_str(&format!("      client_id: {}\n", client_id));
                    yaml.push_str(&format!("      client_secret: {}\n", client_secret));
                    if let Some(url) = token_url {
                        yaml.push_str(&format!("      token_url: {}\n", url));
                    }
                }
            }
        }

        if !api_config.headers.is_empty() {
            yaml.push_str("    headers:\n");
            for (key, value) in &api_config.headers {
                yaml.push_str(&format!("      {}: \"{}\"\n", key, value));
            }
        }

        if let Some(content_type) = &api_config.content_type {
            yaml.push_str(&format!("    content_type: {}\n", content_type));
        }

        yaml.push_str("\n");
    }

    // Add example API configurations
    yaml.push_str("  # Example API configurations:\n");
    yaml.push_str("  # github:\n");
    yaml.push_str("  #   base_url: https://api.github.com\n");
    yaml.push_str("  #   auth:\n");
    yaml.push_str("  #     type: bearer\n");
    yaml.push_str("  #     token: YOUR_GITHUB_TOKEN\n");
    yaml.push_str("  #   headers:\n");
    yaml.push_str("  #     Accept: application/vnd.github.v3+json\n\n");

    yaml.push_str("  # openai:\n");
    yaml.push_str("  #   base_url: https://api.openai.com/v1\n");
    yaml.push_str("  #   auth:\n");
    yaml.push_str("  #     type: bearer\n");
    yaml.push_str("  #     token: YOUR_OPENAI_KEY\n");
    yaml.push_str("  #   headers:\n");
    yaml.push_str("  #     OpenAI-Beta: assistants=v1\n");

    Ok(yaml)
}

fn capitalize_first(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().chain(chars).collect(),
    }
}

/// Create environment variables template
fn create_env_template(env_name: &str, api_name: Option<&str>) -> String {
    let mut template = format!("# Environment variables for {}\n\n", env_name);

    if let Some(api) = api_name {
        match api.to_lowercase().as_str() {
            "stripe" => {
                let is_production = env_name.to_lowercase().contains("prod");
                if is_production {
                    template.push_str("# Stripe Live Key (production)\n");
                    template.push_str("STRIPE_LIVE_KEY=sk_live_...\n\n");
                } else {
                    template.push_str("# Stripe Test Key (development/staging)\n");
                    template.push_str("STRIPE_TEST_KEY=sk_test_...\n\n");
                }
            }
            "github" => {
                template.push_str("# GitHub Personal Access Token or App Token\n");
                template.push_str("GITHUB_TOKEN=ghp_... or ghs_...\n\n");
            }
            "openai" => {
                template.push_str("# OpenAI API Key\n");
                template.push_str("OPENAI_API_KEY=sk-...\n\n");
            }
            _ => {
                template.push_str(&format!("# {} API Configuration\n", api));
                template.push_str(&format!(
                    "{}_BASE_URL=https://api.example.com\n",
                    api.to_uppercase()
                ));
                template.push_str(&format!(
                    "{}_API_KEY=your_api_key_here\n\n",
                    api.to_uppercase()
                ));
            }
        }
    }

    template.push_str("# Add more environment variables as needed\n");
    template
}

// Add dirs crate dependency helper
pub use dirs;
