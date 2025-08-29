# Quick Fix: Add Basic Update Checking

## Minimal Implementation (Can be added in 1 hour)

### 1. Add to Cargo.toml
```toml
[dependencies]
semver = "1.0"
```

### 2. Create src/core/update_check.rs
```rust
use colored::*;
use semver::Version;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

const CHECK_INTERVAL: u64 = 86400; // 24 hours in seconds
const NPM_REGISTRY_URL: &str = "https://registry.npmjs.org/@mrapids/cli/latest";

pub async fn check_for_updates_async() -> Option<String> {
    // Don't block startup - spawn in background
    tokio::spawn(async {
        if let Some(msg) = perform_update_check().await {
            eprintln!("{}", msg);
        }
    });
    None
}

async fn perform_update_check() -> Option<String> {
    // Check if we should check (once per day)
    if !should_check() {
        return None;
    }
    
    let current = env!("CARGO_PKG_VERSION");
    
    // Quick HTTP request to npm registry
    let client = reqwest::Client::builder()
        .timeout(Duration::from_secs(2))  // Don't wait long
        .build()
        .ok()?;
    
    let response = client
        .get(NPM_REGISTRY_URL)
        .send()
        .await
        .ok()?;
    
    let json: serde_json::Value = response.json().await.ok()?;
    let latest = json["version"].as_str()?;
    
    // Compare versions
    let current_ver = Version::parse(current).ok()?;
    let latest_ver = Version::parse(latest).ok()?;
    
    if latest_ver > current_ver {
        // Save check timestamp
        save_last_check_time();
        
        Some(format!(
            "\n{}\n{} {} → {}\n{}\n{}\n",
            "─".repeat(50).dimmed(),
            "📦 Update available:".bright_yellow(),
            current.red(),
            latest.bright_green(),
            "   npm install -g @mrapids/cli@latest".bright_cyan(),
            "─".repeat(50).dimmed()
        ))
    } else {
        save_last_check_time();
        None
    }
}

fn should_check() -> bool {
    // Check at most once per day
    let cache_file = dirs::cache_dir()
        .map(|d| d.join("mrapids").join("last_update_check"));
    
    if let Some(path) = cache_file {
        if let Ok(metadata) = std::fs::metadata(&path) {
            if let Ok(modified) = metadata.modified() {
                let elapsed = SystemTime::now()
                    .duration_since(modified)
                    .unwrap_or(Duration::MAX);
                return elapsed.as_secs() > CHECK_INTERVAL;
            }
        }
    }
    true
}

fn save_last_check_time() {
    if let Some(cache_dir) = dirs::cache_dir() {
        let dir = cache_dir.join("mrapids");
        let _ = std::fs::create_dir_all(&dir);
        let _ = std::fs::write(dir.join("last_update_check"), "");
    }
}
```

### 3. Add to src/main.rs (after argument parsing)
```rust
// Add after line 96 where global options are set
use crate::core::update_check;

// Only check if not explicitly disabled
if !args.no_update_check && !args.version && !args.help {
    update_check::check_for_updates_async().await;
}
```

### 4. Add to CLI args (src/cli/mod.rs)
```rust
/// Disable automatic update checking
#[arg(long, hide = true)]
pub no_update_check: bool,
```

### 5. Add Environment Variable Support
```rust
// In update_check.rs, at start of should_check():
if std::env::var("MRAPIDS_NO_UPDATE_CHECK").is_ok() {
    return false;
}
```

## User Experience

### Normal Usage (with update available)
```bash
$ mrapids run getUser --param id=123

──────────────────────────────────────────────────
📦 Update available: 0.1.0 → 2.0.0
   npm install -g @mrapids/cli@latest
──────────────────────────────────────────────────

✅ Request successful
...
```

### Disable Checking
```bash
# Per run
mrapids run getUser --no-update-check

# Permanently
export MRAPIDS_NO_UPDATE_CHECK=1
```

## Benefits
- ✅ Non-blocking (2 second timeout)
- ✅ Checks once per day maximum
- ✅ Can be disabled
- ✅ Minimal code changes
- ✅ No new dependencies (uses existing reqwest)

## Better Solution (For v1.0)

Add `mrapids self-update` command that:
1. Detects installation method
2. Runs appropriate update command
3. Handles permissions properly
4. Shows changelog

```bash
$ mrapids self-update
Checking for updates...
Current version: 0.1.0
Latest version: 2.0.0

Changes in 2.0.0:
- Breaking: Config format changed
- Feature: Added SDK generation
- Fix: Security vulnerability

Update? (y/n): y
Detected installation: npm
Running: npm install -g @mrapids/cli@2.0.0
✅ Successfully updated!
```