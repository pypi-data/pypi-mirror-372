use crate::utils::security::validate_url;
use anyhow::{Context, Result};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use chrono::{DateTime, Duration, Utc};
use rand::Rng;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OAuth2Config {
    pub provider: String,
    pub client_id: String,
    pub client_secret: Option<String>,
    pub auth_url: String,
    pub token_url: String,
    pub redirect_uri: String,
    pub scopes: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub additional_params: Option<HashMap<String, String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OAuth2Token {
    pub access_token: String,
    pub token_type: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expires_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub refresh_token: Option<String>,
    pub scopes: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AuthProfile {
    pub name: String,
    pub provider: String,
    pub created_at: DateTime<Utc>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub last_used: Option<DateTime<Utc>>,
    pub metadata: HashMap<String, Value>,
}

/// Token response from OAuth provider
#[derive(Debug, Deserialize)]
struct TokenResponse {
    access_token: String,
    token_type: String,
    #[serde(default)]
    expires_in: Option<i64>,
    #[serde(default)]
    refresh_token: Option<String>,
    #[serde(default)]
    scope: Option<String>,
}

/// PKCE (Proof Key for Code Exchange) parameters
pub struct PkceParams {
    pub verifier: String,
    pub challenge: String,
}

/// Generate a random state parameter for OAuth
pub fn generate_state() -> String {
    let mut rng = rand::thread_rng();
    let random_bytes: Vec<u8> = (0..32).map(|_| rng.gen::<u8>()).collect();
    URL_SAFE_NO_PAD.encode(&random_bytes)
}

/// Generate PKCE verifier and challenge
pub fn generate_pkce_pair() -> PkceParams {
    let mut rng = rand::thread_rng();
    let verifier_bytes: Vec<u8> = (0..32).map(|_| rng.gen::<u8>()).collect();
    let verifier = URL_SAFE_NO_PAD.encode(&verifier_bytes);

    let mut hasher = Sha256::new();
    hasher.update(&verifier);
    let challenge = URL_SAFE_NO_PAD.encode(hasher.finalize());

    PkceParams {
        verifier,
        challenge,
    }
}

/// Build the authorization URL
pub fn build_auth_url(config: &OAuth2Config, state: &str, pkce_challenge: &str) -> Result<String> {
    // Validate auth URL for security
    validate_url(&config.auth_url).context("Invalid auth URL - security validation failed")?;

    let mut url = url::Url::parse(&config.auth_url).context("Invalid auth URL")?;

    {
        let mut params = url.query_pairs_mut();
        params.append_pair("client_id", &config.client_id);
        params.append_pair("redirect_uri", &config.redirect_uri);
        params.append_pair("response_type", "code");
        params.append_pair("state", state);
        params.append_pair("code_challenge", pkce_challenge);
        params.append_pair("code_challenge_method", "S256");

        if !config.scopes.is_empty() {
            params.append_pair("scope", &config.scopes.join(" "));
        }

        // Add any additional provider-specific parameters
        if let Some(additional) = &config.additional_params {
            for (key, value) in additional {
                params.append_pair(key, value);
            }
        }
    }

    Ok(url.to_string())
}

/// Exchange authorization code for tokens
pub async fn exchange_code_for_tokens(
    config: &OAuth2Config,
    code: &str,
    pkce_verifier: &str,
) -> Result<OAuth2Token> {
    // Validate token URL for security
    validate_url(&config.token_url).context("Invalid token URL - security validation failed")?;

    let client = reqwest::Client::new();

    let mut params = HashMap::new();
    params.insert("grant_type", "authorization_code");
    params.insert("code", code);
    params.insert("redirect_uri", &config.redirect_uri);
    params.insert("client_id", &config.client_id);
    params.insert("code_verifier", pkce_verifier);

    let mut request = client.post(&config.token_url);

    // Some providers want client credentials in the body, others in Basic auth
    if let Some(client_secret) = &config.client_secret {
        if config.provider == "github" {
            // GitHub wants it in the body
            params.insert("client_secret", client_secret);
        } else {
            // Most providers use Basic auth
            request = request.basic_auth(&config.client_id, Some(client_secret));
        }
    }

    let response = request
        .form(&params)
        .header("Accept", "application/json")
        .send()
        .await
        .context("Failed to exchange code for tokens")?;

    if !response.status().is_success() {
        let error_text = response.text().await?;
        anyhow::bail!("Token exchange failed: {}", error_text);
    }

    let token_response: TokenResponse = response
        .json()
        .await
        .context("Failed to parse token response")?;

    // Calculate expiration time
    let expires_at = token_response
        .expires_in
        .map(|seconds| Utc::now() + Duration::seconds(seconds));

    // Parse scopes
    let scopes = token_response
        .scope
        .map(|s| s.split_whitespace().map(String::from).collect())
        .unwrap_or_else(|| config.scopes.clone());

    Ok(OAuth2Token {
        access_token: token_response.access_token,
        token_type: token_response.token_type,
        expires_at,
        refresh_token: token_response.refresh_token,
        scopes,
    })
}

/// Refresh an access token
pub async fn refresh_access_token(
    config: &OAuth2Config,
    refresh_token: &str,
) -> Result<OAuth2Token> {
    // Validate token URL for security
    validate_url(&config.token_url).context("Invalid token URL - security validation failed")?;

    let client = reqwest::Client::new();

    let mut params = HashMap::new();
    params.insert("grant_type", "refresh_token");
    params.insert("refresh_token", refresh_token);
    params.insert("client_id", &config.client_id);

    let mut request = client.post(&config.token_url);

    if let Some(client_secret) = &config.client_secret {
        request = request.basic_auth(&config.client_id, Some(client_secret));
    }

    let response = request
        .form(&params)
        .header("Accept", "application/json")
        .send()
        .await
        .context("Failed to refresh token")?;

    if !response.status().is_success() {
        let error_text = response.text().await?;
        anyhow::bail!("Token refresh failed: {}", error_text);
    }

    let token_response: TokenResponse = response
        .json()
        .await
        .context("Failed to parse refresh response")?;

    let expires_at = token_response
        .expires_in
        .map(|seconds| Utc::now() + Duration::seconds(seconds));

    let scopes = token_response
        .scope
        .map(|s| s.split_whitespace().map(String::from).collect())
        .unwrap_or_else(|| config.scopes.clone());

    Ok(OAuth2Token {
        access_token: token_response.access_token,
        token_type: token_response.token_type,
        expires_at,
        refresh_token: token_response
            .refresh_token
            .or(Some(refresh_token.to_string())),
        scopes,
    })
}

/// Main OAuth login flow
pub async fn oauth_login(config: OAuth2Config, profile_name: String) -> Result<()> {
    use colored::*;
    use std::time::Duration;

    println!("🔐 {} OAuth Authentication", "Starting".bright_cyan());
    println!("   Provider: {}", config.provider.bright_yellow());
    println!("   Profile: {}", profile_name.bright_green());

    // Generate security parameters
    let state = generate_state();
    let pkce = generate_pkce_pair();

    // Start callback server
    let (tx, rx) = std::sync::mpsc::channel();
    let server_handle = crate::core::auth::server::start_callback_server(tx, state.clone()).await?;

    // Build and open authorization URL
    let auth_url = build_auth_url(&config, &state, &pkce.challenge)?;
    println!("\n🌐 Opening browser for authentication...");
    println!("   If browser doesn't open, visit:");
    println!("   {}", auth_url.bright_blue());

    if let Err(e) = open::that(&auth_url) {
        eprintln!("   ⚠️  Could not open browser: {}", e);
    }

    // Wait for callback
    println!("\n⏳ Waiting for authorization (timeout: 5 minutes)...");
    let auth_code = rx
        .recv_timeout(Duration::from_secs(300))
        .context("Authorization timeout - no response received")?;

    // Stop the server
    drop(server_handle);

    println!("✅ Authorization code received!");

    // Exchange code for tokens
    println!("🔄 Exchanging code for tokens...");
    let tokens = exchange_code_for_tokens(&config, &auth_code, &pkce.verifier).await?;

    // Create profile
    let profile = AuthProfile {
        name: profile_name.clone(),
        provider: config.provider.clone(),
        created_at: Utc::now(),
        last_used: None,
        metadata: HashMap::new(),
    };

    // Store everything
    crate::core::auth::token_store::store_profile(&profile)?;
    crate::core::auth::token_store::store_tokens(&profile_name, &tokens)?;
    crate::core::auth::providers::store_provider_config(&profile_name, &config)?;

    println!("\n✅ {} successful!", "Authentication".bright_green());
    println!(
        "   Profile '{}' created and ready to use",
        profile_name.bright_yellow()
    );
    println!(
        "\n   Use it with: {}",
        format!("mrapids run <operation> --profile {}", profile_name).bright_cyan()
    );

    Ok(())
}

/// Refresh tokens for a profile
pub async fn refresh_tokens(profile: &str) -> Result<OAuth2Token> {
    use colored::*;

    println!(
        "🔄 Refreshing tokens for profile '{}'...",
        profile.bright_yellow()
    );

    let tokens = crate::core::auth::token_store::load_tokens(profile)?;
    let config = crate::core::auth::providers::load_provider_config(profile)?;

    if let Some(refresh_token) = &tokens.refresh_token {
        let new_tokens = refresh_access_token(&config, refresh_token).await?;
        crate::core::auth::token_store::store_tokens(profile, &new_tokens)?;

        println!("✅ Tokens refreshed successfully!");
        Ok(new_tokens)
    } else {
        anyhow::bail!("No refresh token available for profile '{}'", profile)
    }
}

impl OAuth2Token {
    /// Check if the token is expired
    pub fn is_expired(&self) -> bool {
        crate::core::auth::is_token_expired(&self.expires_at)
    }

    /// Get the authorization header value
    pub fn auth_header(&self) -> String {
        format!("{} {}", self.token_type, self.access_token)
    }
}
