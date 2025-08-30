# MCP Agent Implementation Plan

## Quick Implementation Guide

### Step 1: Update main.rs (Immediate)

Replace current main.rs with CLI-based structure:

```rust
// main.rs
use clap::Parser;
mod cli;
mod commands;

#[tokio::main]
async fn main() -> Result<()> {
    let cli = cli::Cli::parse();
    
    match cli.command {
        cli::Commands::Init(cmd) => commands::init::handle_init(cmd),
        cli::Commands::Start(cmd) => commands::start::handle_start(cmd).await,
        cli::Commands::Stop => commands::status::handle_stop(),
        cli::Commands::Status => commands::status::handle_status(),
        cli::Commands::Test(cmd) => commands::test::handle_test(cmd).await,
        cli::Commands::Auth(cmd) => commands::auth::handle_auth(cmd),
        cli::Commands::Logs(cmd) => commands::status::handle_logs(cmd),
        cli::Commands::Validate => commands::validate::handle_validate(),
        // Keep old behavior for compatibility
        cli::Commands::GenerateConfig => generate_example_config(),
    }
}
```

### Step 2: Implement Missing Commands

#### init.rs (✅ Created - needs integration)
```rust
// Already implemented, just needs to be wired up
```

#### start.rs (TODO)
```rust
pub async fn handle_start(cmd: StartCommand) -> Result<()> {
    if cmd.daemon {
        // Fork to background
        daemonize::Daemonize::new()
            .pid_file(cli::pid_file())
            .start()?;
    }
    
    // Current server start logic
    start_server(cmd).await
}
```

#### test.rs (TODO)
```rust
pub async fn handle_test(cmd: TestCommand) -> Result<()> {
    // Test connection
    let client = TestClient::new(&cmd.url);
    
    // Health check
    println!("Testing connection to {}...", cmd.url);
    client.health_check().await?;
    
    if let Some(op) = cmd.operation {
        // Test specific operation
        client.test_operation(&op, cmd.params).await?;
    } else {
        // List available operations
        client.list_operations().await?;
    }
    
    Ok(())
}
```

#### status.rs (TODO)
```rust
pub fn handle_status() -> Result<()> {
    let pid_file = cli::pid_file();
    if pid_file.exists() {
        let pid = fs::read_to_string(&pid_file)?;
        // Check if process is running
        if process_exists(pid.trim()) {
            println!("✅ MCP Agent is running (PID: {})", pid.trim());
        } else {
            println!("❌ MCP Agent is not running (stale PID file)");
            fs::remove_file(&pid_file)?;
        }
    } else {
        println!("❌ MCP Agent is not running");
    }
    Ok(())
}
```

### Step 3: Create Cargo.toml Updates

```toml
[package]
name = "mrapids-agent"
version = "0.1.0"
edition = "2021"
description = "MCP Agent for MicroRapid - Enable AI agents to safely execute API operations"
homepage = "https://github.com/deepwissen/api-runtime"
repository = "https://github.com/deepwissen/api-runtime"
license = "MIT"
keywords = ["mcp", "api", "agent", "ai", "microrapid"]
categories = ["command-line-utilities", "web-programming"]

[dependencies]
# Add for daemon support
daemonize = "0.5"
nix = "0.27"  # For process management

[dev-dependencies]
# For integration tests
assert_cmd = "2.0"
predicates = "3.0"
tempfile = "3.0"
```

### Step 4: Integration Tests

```rust
// tests/integration_test.rs
#[test]
fn test_init_command() {
    let temp_dir = tempdir().unwrap();
    let mut cmd = Command::cargo_bin("mrapids-agent").unwrap();
    
    cmd.arg("init")
       .arg("--config-dir")
       .arg(temp_dir.path())
       .assert()
       .success();
    
    // Check created files
    assert!(temp_dir.path().join("mcp-server.toml").exists());
    assert!(temp_dir.path().join("policy.yaml").exists());
    assert!(temp_dir.path().join("api.yaml").exists());
}

#[test]
fn test_server_lifecycle() {
    // Test start -> status -> stop cycle
}
```

### Step 5: Build & Release Script

```bash
#!/bin/bash
# scripts/release.sh

VERSION=$(cargo metadata --no-deps --format-version 1 | jq -r '.packages[0].version')

# Build for all platforms
echo "Building mrapids-agent v$VERSION"

# macOS
cargo build --release --target x86_64-apple-darwin
cargo build --release --target aarch64-apple-darwin

# Linux
cross build --release --target x86_64-unknown-linux-gnu
cross build --release --target aarch64-unknown-linux-gnu

# Windows
cross build --release --target x86_64-pc-windows-msvc

# Create archives
mkdir -p dist
# ... tar/zip commands ...

echo "Ready to publish to crates.io"
echo "Run: cargo publish"
```

## Timeline

### Day 1-2: CLI Implementation
- [ ] Update main.rs
- [ ] Implement start with daemon
- [ ] Implement stop/status
- [ ] Implement test command
- [ ] Basic integration tests

### Day 3: Polish & Test
- [ ] Auth commands
- [ ] Logs command
- [ ] Validate command
- [ ] Comprehensive testing
- [ ] Update documentation

### Day 4: Release
- [ ] Set up GitHub Actions
- [ ] Build all platforms
- [ ] Publish to crates.io
- [ ] Create GitHub release
- [ ] Update installation docs

## Testing Checklist

- [ ] Init creates correct structure
- [ ] Server starts and responds to health
- [ ] Policy enforcement works
- [ ] Auth profiles load correctly
- [ ] Daemon mode works
- [ ] Stop command kills daemon
- [ ] Test command validates operations
- [ ] Works with Claude Desktop

## Definition of Done

1. User can `cargo install mrapids-agent`
2. `mrapids-agent init` creates working setup
3. `mrapids-agent start` runs the server
4. Claude Desktop can connect and use it
5. Documentation is accurate
6. CI/CD builds all platforms

This plan gets us from current state (working core, incomplete CLI) to a fully installable, user-friendly tool in about 4 days of focused development.