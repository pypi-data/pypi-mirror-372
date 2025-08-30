use crate::core::auth::{AuthProfile, OAuth2Token};
use aes_gcm::{
    aead::{Aead, AeadCore, KeyInit, OsRng},
    Aes256Gcm, Key, Nonce,
};
use anyhow::{Context, Result};
use argon2::password_hash::SaltString;
use argon2::{Argon2, PasswordHasher};
use chrono::Utc;
use std::fs;
use std::path::PathBuf;

/// Get the auth directory path
fn get_auth_dir() -> Result<PathBuf> {
    let home = dirs::home_dir().context("Could not determine home directory")?;
    let auth_dir = home.join(".mrapids").join("auth");
    fs::create_dir_all(&auth_dir)?;
    Ok(auth_dir)
}

/// Get the tokens directory path
fn get_tokens_dir() -> Result<PathBuf> {
    let auth_dir = get_auth_dir()?;
    let tokens_dir = auth_dir.join("tokens");
    fs::create_dir_all(&tokens_dir)?;

    // Set restrictive permissions on Unix systems
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&tokens_dir)?.permissions();
        perms.set_mode(0o700); // Only owner can read/write/execute
        fs::set_permissions(&tokens_dir, perms)?;
    }

    Ok(tokens_dir)
}

/// Derive an encryption key from machine-specific data and profile name
fn derive_encryption_key(profile: &str) -> Result<[u8; 32]> {
    // Get machine ID or fallback to hostname
    let machine_id = match fs::read_to_string("/etc/machine-id") {
        Ok(id) => id.trim().to_string(),
        Err(_) => {
            // Fallback for macOS and Windows
            hostname::get()?.to_string_lossy().to_string()
        }
    };

    // Combine machine ID with profile name for key derivation
    let salt = format!("mrapids-{}-{}", machine_id, profile);
    let salt = SaltString::encode_b64(salt.as_bytes())
        .map_err(|e| anyhow::anyhow!("Failed to create salt: {}", e))?;

    // Use Argon2 for key derivation
    let argon2 = Argon2::default();
    let password = format!("{}-{}", machine_id, profile);
    let password_hash = argon2
        .hash_password(password.as_bytes(), &salt)
        .map_err(|e| anyhow::anyhow!("Failed to derive key: {}", e))?;

    // Extract 32 bytes for AES-256
    let hash = password_hash.hash.unwrap();
    let mut key = [0u8; 32];
    key.copy_from_slice(&hash.as_bytes()[..32]);

    Ok(key)
}

/// Encrypt data using AES-256-GCM
fn encrypt_data(data: &[u8], key: &[u8; 32]) -> Result<Vec<u8>> {
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(key));
    let nonce = Aes256Gcm::generate_nonce(&mut OsRng);

    let ciphertext = cipher
        .encrypt(&nonce, data)
        .map_err(|e| anyhow::anyhow!("Encryption failed: {}", e))?;

    // Prepend nonce to ciphertext
    let mut result = nonce.to_vec();
    result.extend_from_slice(&ciphertext);

    Ok(result)
}

/// Decrypt data using AES-256-GCM
fn decrypt_data(encrypted: &[u8], key: &[u8; 32]) -> Result<Vec<u8>> {
    if encrypted.len() < 12 {
        anyhow::bail!("Invalid encrypted data");
    }

    let (nonce_bytes, ciphertext) = encrypted.split_at(12);
    let nonce = Nonce::from_slice(nonce_bytes);
    let cipher = Aes256Gcm::new(Key::<Aes256Gcm>::from_slice(key));

    let plaintext = cipher
        .decrypt(nonce, ciphertext)
        .map_err(|e| anyhow::anyhow!("Decryption failed: {}", e))?;

    Ok(plaintext)
}

/// Store OAuth tokens securely
pub fn store_tokens(profile: &str, tokens: &OAuth2Token) -> Result<()> {
    let tokens_dir = get_tokens_dir()?;
    let token_path = tokens_dir.join(format!("{}.enc", profile));

    // Serialize tokens
    let token_data = serde_json::to_vec(tokens)?;

    // Derive encryption key
    let key = derive_encryption_key(profile)?;

    // Encrypt tokens
    let encrypted = encrypt_data(&token_data, &key)?;

    // Write encrypted data
    fs::write(&token_path, encrypted)?;

    // Set restrictive permissions on Unix systems
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = fs::metadata(&token_path)?.permissions();
        perms.set_mode(0o600); // Only owner can read/write
        fs::set_permissions(&token_path, perms)?;
    }

    Ok(())
}

/// Load OAuth tokens
pub fn load_tokens(profile: &str) -> Result<OAuth2Token> {
    let tokens_dir = get_tokens_dir()?;
    let token_path = tokens_dir.join(format!("{}.enc", profile));

    if !token_path.exists() {
        anyhow::bail!("No tokens found for profile '{}'", profile);
    }

    // Read encrypted data
    let encrypted = fs::read(&token_path)?;

    // Derive encryption key
    let key = derive_encryption_key(profile)?;

    // Decrypt tokens
    let decrypted = decrypt_data(&encrypted, &key)?;

    // Deserialize tokens
    let tokens: OAuth2Token = serde_json::from_slice(&decrypted)?;

    // Update last used time
    if let Ok(mut auth_profile) = load_profile(profile) {
        auth_profile.last_used = Some(Utc::now());
        let _ = store_profile(&auth_profile);
    }

    Ok(tokens)
}

/// Store auth profile
pub fn store_profile(profile: &AuthProfile) -> Result<()> {
    let auth_dir = get_auth_dir()?;
    let profiles_path = auth_dir.join("profiles.json");

    // Load existing profiles
    let mut profiles: Vec<AuthProfile> = if profiles_path.exists() {
        let data = fs::read_to_string(&profiles_path)?;
        serde_json::from_str(&data).unwrap_or_default()
    } else {
        Vec::new()
    };

    // Update or add profile
    if let Some(pos) = profiles.iter().position(|p| p.name == profile.name) {
        profiles[pos] = profile.clone();
    } else {
        profiles.push(profile.clone());
    }

    // Save profiles
    let data = serde_json::to_string_pretty(&profiles)?;
    fs::write(profiles_path, data)?;

    Ok(())
}

/// Load auth profile
pub fn load_profile(name: &str) -> Result<AuthProfile> {
    let auth_dir = get_auth_dir()?;
    let profiles_path = auth_dir.join("profiles.json");

    if !profiles_path.exists() {
        anyhow::bail!("No profiles found");
    }

    let data = fs::read_to_string(&profiles_path)?;
    let profiles: Vec<AuthProfile> = serde_json::from_str(&data)?;

    profiles
        .into_iter()
        .find(|p| p.name == name)
        .context(format!("Profile '{}' not found", name))
}

/// List all auth profiles
pub fn list_profiles() -> Result<Vec<AuthProfile>> {
    let auth_dir = get_auth_dir()?;
    let profiles_path = auth_dir.join("profiles.json");

    if !profiles_path.exists() {
        return Ok(Vec::new());
    }

    let data = fs::read_to_string(&profiles_path)?;
    let profiles: Vec<AuthProfile> = serde_json::from_str(&data)?;

    Ok(profiles)
}

/// Delete an auth profile and its tokens
pub fn delete_profile(name: &str) -> Result<()> {
    // Delete tokens
    let tokens_dir = get_tokens_dir()?;
    let token_path = tokens_dir.join(format!("{}.enc", name));
    if token_path.exists() {
        fs::remove_file(token_path)?;
    }

    // Delete provider config
    let auth_dir = get_auth_dir()?;
    let provider_path = auth_dir.join("providers").join(format!("{}.json", name));
    if provider_path.exists() {
        fs::remove_file(provider_path)?;
    }

    // Remove from profiles list
    let profiles_path = auth_dir.join("profiles.json");
    if profiles_path.exists() {
        let data = fs::read_to_string(&profiles_path)?;
        let mut profiles: Vec<AuthProfile> = serde_json::from_str(&data)?;
        profiles.retain(|p| p.name != name);

        let data = serde_json::to_string_pretty(&profiles)?;
        fs::write(profiles_path, data)?;
    }

    Ok(())
}

/// Check if a profile exists
pub fn profile_exists(name: &str) -> bool {
    if let Ok(profiles) = list_profiles() {
        profiles.iter().any(|p| p.name == name)
    } else {
        false
    }
}
