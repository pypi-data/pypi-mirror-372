# How Popular CLI Tools Handle Updates

## 🎯 Industry Standard Patterns

### 1. **npm (Node Package Manager)**
```bash
$ npm outdated -g

# Shows after commands occasionally:
╭─────────────────────────────────────────────────────────╮
│                                                         │
│   New major version of npm available! 8.19.2 → 10.2.4  │
│   Run npm install -g npm to update!                    │
│                                                         │
╰─────────────────────────────────────────────────────────╯
```
**Strategy:**
- Checks periodically (not every run)
- Shows AFTER command completes (non-blocking)
- Caches check for 24 hours
- Can disable with `npm config set update-notifier false`

### 2. **Homebrew**
```bash
$ brew update  # Manual check
$ brew upgrade # Updates packages

# Auto-update (default enabled):
==> Auto-updated Homebrew!
Updated 2 formulae.
```
**Strategy:**
- Auto-updates itself before operations
- Can disable: `HOMEBREW_NO_AUTO_UPDATE=1`
- Shows what changed

### 3. **GitHub CLI (gh)**
```bash
$ gh --version
gh version 2.40.1 (2024-01-15)
https://github.com/cli/cli/releases/tag/v2.40.1

# After any command (once per day):
A new release of gh is available: 2.40.1 → 2.42.0
To upgrade, run: brew update && brew upgrade gh
```
**Strategy:**
- Checks once per 24 hours
- Shows AFTER command output
- Detects installation method
- Non-blocking background check

### 4. **Rust's Cargo**
```bash
$ cargo install-update -a  # Separate tool needed

# No built-in update checking!
# Users must manually check
```
**Strategy:**
- NO automatic checking
- Relies on cargo-update crate
- Philosophy: explicit over implicit

### 5. **AWS CLI**
```bash
$ aws --version
aws-cli/2.13.0 Python/3.11.4

# No auto-check, but:
$ aws --version --check-update
Latest version: 2.15.0 (New version available)
```
**Strategy:**
- No automatic checks
- Manual flag to check
- Enterprise environments prefer control

### 6. **Vercel CLI**
```bash
$ vercel --version
Vercel CLI 32.5.0

# Shows inline:
   UPDATE AVAILABLE   The latest version of Vercel CLI is 33.0.0
   Please run `npm i -g vercel@latest` to update
```
**Strategy:**
- Checks on every run (aggressive)
- Shows at top of output
- Includes exact update command

### 7. **pnpm**
```bash
$ pnpm --version
8.10.0

# Shows after command:
 WARN  A new version of pnpm is available: 8.10.0 → 8.14.0
 Run "pnpm add -g pnpm" to update
```
**Strategy:**
- Similar to npm
- Yellow warning style
- Non-blocking

### 8. **Docker CLI**
```bash
$ docker version
# No update checks - handled by Docker Desktop app
```
**Strategy:**
- Desktop app handles updates
- CLI doesn't check

### 9. **Firebase CLI**
```bash
$ firebase --version
12.0.0

# Shows warning:
┌─────────────────────────────────────────────────────────────┐
│  Update available 12.0.0 → 12.8.0                          │
│  Run npm i -g firebase-tools to update                     │
└─────────────────────────────────────────────────────────────┘
```
**Strategy:**
- Pretty box formatting
- Clear update command
- Checks periodically

### 10. **Yarn**
```bash
$ yarn --version
1.22.19

# Uses update-notifier npm package:
┌───────────────────────────────────────────────────┐
│   New version available 1.22.19 → 3.6.4          │
│   Run yarn set version latest to update          │
└───────────────────────────────────────────────────┘
```

## 📊 Pattern Analysis

### Most Common Approach (70% of tools):
1. **Check periodically** (every 24 hours)
2. **Cache the check** (don't spam registry)
3. **Show AFTER command** (non-blocking)
4. **Provide disable option** (environment variable)
5. **Include update command** (copy-paste ready)

### Implementation Methods:

#### Method 1: Background Check (Most Popular)
```javascript
// Pseudocode used by npm, yarn, etc.
if (shouldCheckForUpdate()) {  // Once per day
  spawn(async () => {
    const latest = await fetchLatestVersion();
    if (latest > current) {
      saveNotification(latest);
    }
  });
}

// After command completes:
if (hasUpdateNotification()) {
  showUpdateMessage();
}
```

#### Method 2: Registry File Check
```bash
# Tools check package registry
https://registry.npmjs.org/package-name/latest
https://api.github.com/repos/owner/repo/releases/latest
https://pypi.org/pypi/package-name/json
```

#### Method 3: Built-in Package (npm ecosystem)
```javascript
// Many Node CLIs use this package
const updateNotifier = require('update-notifier');
const pkg = require('./package.json');

updateNotifier({
  pkg,
  updateCheckInterval: 1000 * 60 * 60 * 24, // 1 day
}).notify();
```

## 🏆 Best Practices

### DO:
- ✅ Check **asynchronously** (never block)
- ✅ Cache for **24 hours minimum**
- ✅ Show **AFTER** command output
- ✅ Provide **disable mechanism**
- ✅ Include **exact update command**
- ✅ Detect **installation method**
- ✅ Use **color** for visibility
- ✅ Keep message **concise**

### DON'T:
- ❌ Check on every run (too aggressive)
- ❌ Block command execution
- ❌ Auto-update without permission
- ❌ Show before command output
- ❌ Require internet to function
- ❌ Fail if check errors

## 🎨 UI Patterns

### Minimal (AWS CLI style):
```
New version available: 1.0.0 → 2.0.0
```

### Boxed (npm/Firebase style):
```
┌─────────────────────────────────────────────┐
│  Update available 1.0.0 → 2.0.0            │
│  Run npm i -g @mrapids/cli to update       │
└─────────────────────────────────────────────┘
```

### Inline Warning (pnpm style):
```
WARN  Update available: 1.0.0 → 2.0.0
      Run: npm i -g @mrapids/cli
```

### Banner (Vercel style):
```
UPDATE AVAILABLE  The latest version is 2.0.0
Please run `npm i -g @mrapids/cli` to update
```

## 🔧 Implementation for MicroRapids

### Recommended Approach:

```rust
// 1. Non-blocking check after command starts
tokio::spawn(async move {
    if should_check_update() {  // Once per 24h
        if let Some(latest) = fetch_latest().await {
            save_for_display(latest);
        }
    }
});

// 2. Display after command completes
fn display_update_if_available() {
    if let Some(update) = get_saved_update() {
        eprintln!("\n{}", format_update_box(update));
    }
}

// 3. Provide self-update command
mrapids self-update  // Auto-detects npm/cargo/pip
```

### Cache Location:
```bash
# macOS/Linux
~/.cache/mrapids/update-check

# Windows  
%LOCALAPPDATA%\mrapids\cache\update-check
```

### Disable Methods:
```bash
# Environment variable
export MRAPIDS_NO_UPDATE_CHECK=1

# Config file
[updates]
check = false

# CLI flag
mrapids --no-update-check
```

## 📈 Update Check Frequency by Tool

| Tool | Frequency | Method |
|------|-----------|---------|
| npm | 24 hours | Cache file |
| gh | 24 hours | Cache file |
| yarn | 24 hours | Cache file |
| firebase | 7 days | Cache file |
| vercel | Every run | No cache |
| homebrew | Before operations | Git pull |
| cargo | Never | Manual only |

## 🚀 Modern Approach: Smart Updates

### Next-Gen Features (used by Vercel, Deno):
1. **Semantic version awareness** - Only notify for major versions
2. **Channel selection** - stable/beta/canary
3. **Breaking change detection** - Warn about migrations
4. **Rollback capability** - Keep previous version
5. **Delta updates** - Only download changes

### Example Implementation:
```rust
pub struct UpdateChecker {
    channel: UpdateChannel,  // stable, beta, nightly
    frequency: Duration,     // How often to check
    auto_update: bool,       // Auto-update minor versions
    show_prereleases: bool,  // Show beta versions
}

// Smart notification
match version_diff {
    Major => "⚠️  Major update with breaking changes",
    Minor => "✨ New features available",
    Patch => "🔧 Bug fixes available",
}
```

## Summary

**Industry Standard:**
1. Check for updates **once per day**
2. Do it **asynchronously** 
3. Show message **after** command completes
4. Always provide **opt-out** mechanism
5. Never **auto-update** without permission

**For MicroRapids:**
Should follow GitHub CLI or npm pattern - check daily, show after command, provide `self-update` command.