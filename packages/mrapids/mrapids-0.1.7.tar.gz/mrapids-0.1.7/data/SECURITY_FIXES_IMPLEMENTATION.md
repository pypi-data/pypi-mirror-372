# Security Fixes Implementation Guide

## Quick Fixes for Valid Issues

### 1. File Permissions Fix (PRIORITY: HIGH)

```rust
// agent/src/commands/init.rs - Add after line 16
use std::fs::Permissions;
#[cfg(unix)]
use std::os::unix::fs::PermissionsExt;

// Update directory creation (after line 16):
fs::create_dir_all(&cmd.config_dir)?;
#[cfg(unix)]
fs::set_permissions(&cmd.config_dir, Permissions::from_mode(0o700))?;

// Update each file write (after lines 29, 37, 53, 62):
fs::write(&config_path, config_content)?;
#[cfg(unix)]
fs::set_permissions(&config_path, Permissions::from_mode(0o600))?;
```

### 2. Error Handling Improvements

```rust
// agent/src/commands/init.rs - Replace download_spec function
async fn download_spec(url: &str, target: &Path) -> Result<()> {
    use reqwest;
    
    println!("📥 Downloading API spec from {}", url);
    
    let response = reqwest::get(url).await
        .context("Failed to download spec")?;
    
    if !response.status().is_success() {
        anyhow::bail!("Download failed with status: {}", response.status());
    }
    
    let content = response.text().await
        .context("Failed to read response body")?;
    
    // Validate it's valid OpenAPI/Swagger
    if !content.contains("openapi") && !content.contains("swagger") {
        anyhow::bail!("Downloaded content doesn't appear to be an API spec");
    }
    
    fs::write(target, content)?;
    #[cfg(unix)]
    fs::set_permissions(target, Permissions::from_mode(0o600))?;
    
    println!("✅ Successfully downloaded spec to {}", target.display());
    Ok(())
}

// Update create_example_spec to fail on unknown
fn create_example_spec(example: &str, config_dir: &Path) -> Result<()> {
    let (spec_content, auth_content) = match example {
        "github" => (
            include_str!("../../examples/specs/github-api.yaml"),
            GITHUB_AUTH_TEMPLATE
        ),
        "stripe" => (
            include_str!("../../examples/specs/stripe-api.yaml"),
            STRIPE_AUTH_TEMPLATE
        ),
        _ => {
            anyhow::bail!(
                "Unknown example '{}'. Available examples: github, stripe", 
                example
            );
        }
    };
    
    // ... rest of implementation
}
```

### 3. Backup Feature

```rust
// agent/src/commands/init.rs - Add backup function
fn backup_file(path: &Path) -> Result<()> {
    if path.exists() {
        let backup_dir = path.parent()
            .unwrap_or(Path::new("."))
            .join("backups");
        
        fs::create_dir_all(&backup_dir)?;
        
        let timestamp = chrono::Local::now().format("%Y%m%d_%H%M%S");
        let filename = path.file_name()
            .ok_or_else(|| anyhow::anyhow!("Invalid path"))?;
        let backup_name = format!("{}.{}.backup", 
            filename.to_string_lossy(), 
            timestamp
        );
        let backup_path = backup_dir.join(backup_name);
        
        fs::copy(path, &backup_path)?;
        #[cfg(unix)]
        fs::set_permissions(&backup_path, Permissions::from_mode(0o600))?;
        
        println!("📦 Backed up to {}", backup_path.display());
    }
    Ok(())
}

// Use in handle_init before overwriting
if cmd.force {
    backup_file(&config_path)?;
    backup_file(&policy_path)?;
}
```

### 4. Enhanced CLI Options

```rust
// agent/src/cli.rs - Update InitCommand
#[derive(Debug, Args)]
pub struct InitCommand {
    /// Force overwrite existing configuration
    #[arg(long, short = 'f')]
    pub force: bool,
    
    /// Download spec from URL
    #[arg(long, conflicts_with = "example")]
    pub from_url: Option<String>,
    
    /// Use example configuration
    #[arg(long, value_name = "NAME", conflicts_with = "from_url")]
    pub example: Option<String>,
    
    /// Configuration directory
    #[arg(long, default_value = ".mrapids")]
    pub config_dir: PathBuf,
    
    /// Server host (for initial config)
    #[arg(long, default_value = "127.0.0.1")]
    pub host: String,
    
    /// Server port (for initial config)
    #[arg(long, default_value = "3333")]
    pub port: u16,
    
    /// Initial API spec file
    #[arg(long)]
    pub spec: Option<PathBuf>,
    
    /// Skip creating example files
    #[arg(long)]
    pub minimal: bool,
}

// Update default_config to use these values
fn default_config(host: &str, port: u16) -> String {
    format!(r#"# MCP Server Configuration

[server]
host = "{}"
port = {}
# ... rest of config
"#, host, port)
}
```

---

## Design Decisions That Should Stay

### 1. Secrets in Environment Variables

**Current Design is CORRECT**:
```toml
# Good - Only store reference
[profile]
name = "github"
token_env = "GITHUB_TOKEN"

# Bad - Never store actual token
[profile]
name = "github" 
token = "ghp_actualSecretToken123"  # NEVER DO THIS
```

### 2. Default Fallbacks

**Consider Keeping Some Fallbacks**:
```rust
// For non-critical features, warnings are better than failures
if !example_exists(&example) {
    eprintln!("⚠️  Warning: Unknown example '{}', available: {:?}", 
        example, 
        available_examples()
    );
    if !prompt_continue()? {
        return Err(anyhow!("Initialization cancelled"));
    }
    // Continue with default
}
```

### 3. Separate Init and Start

**Current Design is Good**:
- Init creates static configuration
- Start accepts runtime parameters
- Allows config file editing between steps
- Better for automation/scripting

---

## Testing the Fixes

```bash
#!/bin/bash
# Test file permissions
mrapids-agent init
ls -la .mrapids/
# Should show: drwx------

# Test error handling
mrapids-agent init --from-url https://invalid.url
# Should fail with clear error

# Test backup
echo "custom = true" >> .mrapids/mcp-server.toml
mrapids-agent init --force
ls .mrapids/backups/
# Should show timestamped backup

# Test new CLI options
mrapids-agent init --host 0.0.0.0 --port 8080
grep "port = 8080" .mrapids/mcp-server.toml
# Should find the custom port
```

---

## Summary

The mrapids-agent has a **security-first architecture** that:
- Never stores secrets in files
- Uses comprehensive audit logging
- Provides secure defaults

The QA-identified issues are mostly **UX improvements**, not critical security flaws. The fixes above address all valid concerns while maintaining the security model.