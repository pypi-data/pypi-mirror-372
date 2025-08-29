pub mod oauth2;
pub mod providers;
pub mod server;
pub mod token_store;

pub use oauth2::{oauth_login, refresh_tokens, AuthProfile, OAuth2Token};
pub use token_store::{delete_profile, list_profiles, load_tokens};

use anyhow::Result;
use chrono::{DateTime, Utc};

/// Check if a token is expired
pub fn is_token_expired(expires_at: &Option<DateTime<Utc>>) -> bool {
    if let Some(expiry) = expires_at {
        Utc::now() >= *expiry
    } else {
        false
    }
}

/// Test if authentication works by making a simple API call
pub async fn test_auth_profile(profile: &str) -> Result<()> {
    let tokens = load_tokens(profile)?;
    let provider_config = providers::get_provider_details(profile)?;

    // Make a test request based on provider
    match provider_config.provider.as_str() {
        "github" => test_github_auth(&tokens.access_token).await,
        "google" => test_google_auth(&tokens.access_token).await,
        _ => Ok(()), // Skip test for custom providers
    }
}

async fn test_github_auth(token: &str) -> Result<()> {
    let client = reqwest::Client::new();
    let response = client
        .get("https://api.github.com/user")
        .header("Authorization", format!("Bearer {}", token))
        .header("User-Agent", "MicroRapid")
        .send()
        .await?;

    if response.status().is_success() {
        println!("✅ GitHub authentication is working");
        Ok(())
    } else {
        anyhow::bail!("GitHub authentication failed: {}", response.status())
    }
}

async fn test_google_auth(token: &str) -> Result<()> {
    let client = reqwest::Client::new();
    let response = client
        .get("https://www.googleapis.com/oauth2/v1/userinfo")
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await?;

    if response.status().is_success() {
        println!("✅ Google authentication is working");
        Ok(())
    } else {
        anyhow::bail!("Google authentication failed: {}", response.status())
    }
}
