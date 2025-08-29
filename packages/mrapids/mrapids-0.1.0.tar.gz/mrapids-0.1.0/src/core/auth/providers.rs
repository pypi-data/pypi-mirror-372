use crate::core::auth::oauth2::OAuth2Config;
use anyhow::{Context, Result};
use std::collections::HashMap;
use std::fs;
use std::path::PathBuf;

/// Get the auth directory path
fn get_auth_dir() -> Result<PathBuf> {
    let home = dirs::home_dir().context("Could not determine home directory")?;
    let auth_dir = home.join(".mrapids").join("auth");
    fs::create_dir_all(&auth_dir)?;
    Ok(auth_dir)
}

/// Get provider configuration for known providers
pub fn get_provider_config(provider: &str) -> Result<OAuth2Config> {
    // Check environment variables for client credentials
    let client_id_env = format!("{}_CLIENT_ID", provider.to_uppercase());
    let client_secret_env = format!("{}_CLIENT_SECRET", provider.to_uppercase());

    match provider.to_lowercase().as_str() {
        "github" => {
            let client_id = std::env::var(&client_id_env)
                .unwrap_or_else(|_| "YOUR_GITHUB_CLIENT_ID".to_string());
            let client_secret = std::env::var(&client_secret_env).ok();

            Ok(OAuth2Config {
                provider: "github".to_string(),
                client_id,
                client_secret,
                auth_url: "https://github.com/login/oauth/authorize".to_string(),
                token_url: "https://github.com/login/oauth/access_token".to_string(),
                redirect_uri: "http://localhost:8899/callback".to_string(),
                scopes: vec!["repo", "user"].into_iter().map(String::from).collect(),
                additional_params: None,
            })
        }

        "google" => {
            let client_id = std::env::var(&client_id_env)
                .unwrap_or_else(|_| "YOUR_GOOGLE_CLIENT_ID".to_string());
            let client_secret = std::env::var(&client_secret_env).ok();

            let mut additional_params = HashMap::new();
            additional_params.insert("access_type".to_string(), "offline".to_string());
            additional_params.insert("prompt".to_string(), "consent".to_string());

            Ok(OAuth2Config {
                provider: "google".to_string(),
                client_id,
                client_secret,
                auth_url: "https://accounts.google.com/o/oauth2/v2/auth".to_string(),
                token_url: "https://oauth2.googleapis.com/token".to_string(),
                redirect_uri: "http://localhost:8899/callback".to_string(),
                scopes: vec!["openid", "email", "profile"]
                    .into_iter()
                    .map(String::from)
                    .collect(),
                additional_params: Some(additional_params),
            })
        }

        "microsoft" => {
            let client_id = std::env::var(&client_id_env)
                .unwrap_or_else(|_| "YOUR_MICROSOFT_CLIENT_ID".to_string());
            let client_secret = std::env::var(&client_secret_env).ok();

            Ok(OAuth2Config {
                provider: "microsoft".to_string(),
                client_id,
                client_secret,
                auth_url: "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
                    .to_string(),
                token_url: "https://login.microsoftonline.com/common/oauth2/v2.0/token".to_string(),
                redirect_uri: "http://localhost:8899/callback".to_string(),
                scopes: vec!["openid", "profile", "email", "offline_access"]
                    .into_iter()
                    .map(String::from)
                    .collect(),
                additional_params: None,
            })
        }

        "gitlab" => {
            let client_id = std::env::var(&client_id_env)
                .unwrap_or_else(|_| "YOUR_GITLAB_CLIENT_ID".to_string());
            let client_secret = std::env::var(&client_secret_env).ok();

            Ok(OAuth2Config {
                provider: "gitlab".to_string(),
                client_id,
                client_secret,
                auth_url: "https://gitlab.com/oauth/authorize".to_string(),
                token_url: "https://gitlab.com/oauth/token".to_string(),
                redirect_uri: "http://localhost:8899/callback".to_string(),
                scopes: vec!["read_user", "api"]
                    .into_iter()
                    .map(String::from)
                    .collect(),
                additional_params: None,
            })
        }

        "slack" => {
            let client_id = std::env::var(&client_id_env)
                .unwrap_or_else(|_| "YOUR_SLACK_CLIENT_ID".to_string());
            let client_secret = std::env::var(&client_secret_env).ok();

            Ok(OAuth2Config {
                provider: "slack".to_string(),
                client_id,
                client_secret,
                auth_url: "https://slack.com/oauth/v2/authorize".to_string(),
                token_url: "https://slack.com/api/oauth.v2.access".to_string(),
                redirect_uri: "http://localhost:8899/callback".to_string(),
                scopes: vec!["channels:read", "chat:write", "users:read"]
                    .into_iter()
                    .map(String::from)
                    .collect(),
                additional_params: None,
            })
        }

        _ => anyhow::bail!("Unknown provider: {}. Use custom configuration.", provider),
    }
}

/// Create a custom OAuth2 configuration
pub fn create_custom_config(
    provider_name: &str,
    client_id: String,
    client_secret: Option<String>,
    auth_url: String,
    token_url: String,
    scopes: Vec<String>,
) -> OAuth2Config {
    OAuth2Config {
        provider: provider_name.to_string(),
        client_id,
        client_secret,
        auth_url,
        token_url,
        redirect_uri: "http://localhost:8899/callback".to_string(),
        scopes,
        additional_params: None,
    }
}

/// Store provider configuration for a profile
pub fn store_provider_config(profile: &str, config: &OAuth2Config) -> Result<()> {
    let auth_dir = get_auth_dir()?;
    let providers_dir = auth_dir.join("providers");
    fs::create_dir_all(&providers_dir)?;

    let config_path = providers_dir.join(format!("{}.json", profile));
    let config_json = serde_json::to_string_pretty(config)?;
    fs::write(config_path, config_json)?;

    Ok(())
}

/// Load provider configuration for a profile
pub fn load_provider_config(profile: &str) -> Result<OAuth2Config> {
    let auth_dir = get_auth_dir()?;
    let config_path = auth_dir.join("providers").join(format!("{}.json", profile));

    let config_data = fs::read_to_string(&config_path)
        .with_context(|| format!("Failed to load provider config for profile '{}'", profile))?;

    let config: OAuth2Config = serde_json::from_str(&config_data)?;
    Ok(config)
}

/// Get provider details for a profile
pub fn get_provider_details(profile: &str) -> Result<OAuth2Config> {
    load_provider_config(profile)
}

/// Provider-specific configuration help
pub fn get_provider_help(provider: &str) -> String {
    match provider.to_lowercase().as_str() {
        "github" => {
            r#"GitHub OAuth Setup:
1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Set Authorization callback URL to: http://localhost:8899/callback
4. Save Client ID and Client Secret
5. Export environment variables:
   export GITHUB_CLIENT_ID=your_client_id
   export GITHUB_CLIENT_SECRET=your_client_secret"#
        },

        "google" => {
            r#"Google OAuth Setup:
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new OAuth 2.0 Client ID
3. Set Authorized redirect URI to: http://localhost:8899/callback
4. Download credentials or copy Client ID and Secret
5. Export environment variables:
   export GOOGLE_CLIENT_ID=your_client_id
   export GOOGLE_CLIENT_SECRET=your_client_secret"#
        },

        "microsoft" => {
            r#"Microsoft OAuth Setup:
1. Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
2. Register a new application
3. Add redirect URI: http://localhost:8899/callback (Web platform)
4. Create a client secret under "Certificates & secrets"
5. Export environment variables:
   export MICROSOFT_CLIENT_ID=your_application_id
   export MICROSOFT_CLIENT_SECRET=your_client_secret"#
        },

        _ => {
            return format!("No specific setup instructions available for '{}'. Please refer to the provider's OAuth documentation.", provider)
        }
    }.to_string()
}
