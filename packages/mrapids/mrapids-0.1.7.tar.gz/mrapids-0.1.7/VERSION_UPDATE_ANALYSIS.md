# Version Update Analysis for MicroRapids

## Current State Analysis (Based on Code Review)

### 🔍 What Currently Exists

1. **Version Display**
   - Version is compiled from `Cargo.toml` using `env!("CARGO_PKG_VERSION")`
   - Users can check version with `mrapids --version`
   - Version shown in banner: src/core/banner.rs:83

2. **No Update Mechanism**
   - ❌ No update checking functionality
   - ❌ No self-update command
   - ❌ No version comparison
   - ❌ No update notifications
   - ❌ No migration tools

### 📦 How Users Currently Update (v1.0.0 → v2.0.0)

#### NPM (@mrapids/cli)
```bash
# Current version check
mrapids --version  # Shows: 1.0.0

# Manual update required
npm update -g @mrapids/cli        # May not work for major versions
npm install -g @mrapids/cli@latest # Force latest version
npm install -g @mrapids/cli@2.0.0  # Specific version
```

**Problems:**
- User won't know v2.0.0 exists
- `npm update` doesn't update major versions by default
- No deprecation warnings in v1.0.0

#### Cargo (mrapids)
```bash
# Current version check  
mrapids --version  # Shows: 1.0.0

# Manual update required
cargo install mrapids --force      # Force reinstall latest
cargo install mrapids --version 2.0.0 --force
```

**Problems:**
- Must use `--force` to overwrite
- No notification of new versions
- Binary replacement can fail if running

#### PyPI (mrapids)
```bash
# Current version check
python -c "import mrapids; print(mrapids.__version__)"  # If exposed

# Manual update required
pip install --upgrade mrapids      # Updates to latest
pip install mrapids==2.0.0        # Specific version
```

**Problems:**
- Version not exposed in Python module
- No update notifications
- No breaking change warnings

## 🚨 Critical Issues Found

### 1. **No Update Discovery**
Users with v1.0.0 have NO WAY to know v2.0.0 exists unless they:
- Manually check GitHub releases
- Visit npm/crates.io/PyPI
- Follow social media/blog

### 2. **Silent Failures**
Breaking changes in v2.0.0 would cause:
- Runtime errors with no explanation
- Config file incompatibilities
- API changes breaking scripts

### 3. **No Migration Path**
- No migration guides
- No config upgrade tools
- No backwards compatibility checks

## 💡 Recommended Solutions

### Quick Fix (Minimal Changes)
```rust
// In src/core/version_check.rs (NEW FILE)
use semver::Version;

pub async fn check_for_updates() -> Option<String> {
    let current = env!("CARGO_PKG_VERSION");
    
    // Check npm registry
    let latest = fetch_latest_version().await?;
    
    if Version::parse(&latest).ok()? > Version::parse(current).ok()? {
        Some(format!(
            "\n📦 New version available: {} → {}\n\
            Update with: npm install -g @mrapids/cli@latest\n",
            current, latest
        ))
    } else {
        None
    }
}

// Add to main.rs after parsing args
if !args.no_update_check {
    if let Some(msg) = check_for_updates().await {
        eprintln!("{}", msg.yellow());
    }
}
```

### Proper Solution (Recommended)

#### 1. Add Update Command
```bash
mrapids self-update          # Auto-update to latest
mrapids self-update --check  # Just check for updates
mrapids self-update 2.0.0    # Update to specific version
```

#### 2. Add Version Check on Startup
```rust
// Check once per day, cache result
if should_check_version() {
    spawn_version_check();  // Non-blocking
}
```

#### 3. Add Migration System
```rust
// In v2.0.0
pub fn migrate_from_v1(config: &str) -> Result<String> {
    // Convert v1 config to v2 format
}

// On startup
if config_version < current_version {
    println!("Migrating config from v{} to v{}", old, new);
    migrate_config()?;
}
```

#### 4. Add Update Config
```toml
# .mrapids/config.toml
[updates]
check_enabled = true
check_frequency = "daily"
channel = "stable"  # or "beta", "nightly"
last_check = "2024-01-20T10:00:00Z"
```

## 📋 Implementation Checklist

### Phase 1: Detection (v0.2.0)
- [ ] Add version check on startup (non-blocking)
- [ ] Add `--no-update-check` flag
- [ ] Cache check results (24 hours)
- [ ] Show update notice in banner

### Phase 2: Self-Update (v0.3.0)
- [ ] Add `mrapids self-update` command
- [ ] Detect installation method (npm/cargo/pip)
- [ ] Execute appropriate update command
- [ ] Handle permission issues

### Phase 3: Migration (v1.0.0)
- [ ] Version config files
- [ ] Add migration framework
- [ ] Create upgrade guides
- [ ] Add rollback capability

## 🎯 Expected User Experience

### With Update System
```bash
$ mrapids --version
mrapids 1.0.0

📦 Update available: 2.0.0 (current: 1.0.0)
   Run 'mrapids self-update' to upgrade
   See changes: https://github.com/microrapids/api-runtime/releases/tag/v2.0.0

$ mrapids self-update
Detecting installation method... npm
Running: npm install -g @mrapids/cli@2.0.0
✅ Successfully updated to v2.0.0

⚠️  Breaking changes detected. Migrating config...
✅ Config migrated successfully
```

### Version Check API Response
```json
{
  "latest": "2.0.0",
  "current": "1.0.0",
  "update_available": true,
  "breaking_changes": true,
  "update_command": "npm install -g @mrapids/cli@latest",
  "release_notes": "https://github.com/microrapids/api-runtime/releases/tag/v2.0.0",
  "deprecations": ["config.yaml format changed", "API endpoint renamed"]
}
```

## 🔴 Current Risk Assessment

**Without update mechanism:**
- Users stuck on old versions
- Security vulnerabilities unfixed
- No adoption of new features
- Poor user experience
- Support burden increases

**Recommendation: Implement Phase 1 (Detection) immediately in next release**

---

## Summary

Currently, users must:
1. **Manually check** for updates (they won't)
2. **Manually update** using package manager
3. **Manually fix** breaking changes (no guidance)

This is **not enterprise-ready** and will cause adoption issues.