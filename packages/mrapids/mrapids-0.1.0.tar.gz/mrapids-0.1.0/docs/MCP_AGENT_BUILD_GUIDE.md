# Building and Installing MCP Agent

Since `mrapids-agent` is not yet published to crates.io, you need to build it from source.

## Quick Build Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime
git checkout Agentic_features
```

### 2. Build the Agent
```bash
cd agent
cargo build --release
```

### 3. Install Locally
```bash
# Option 1: Copy to system path
sudo cp target/release/mrapids-agent /usr/local/bin/

# Option 2: Add to PATH
export PATH="$PATH:$(pwd)/target/release"

# Option 3: Create alias
alias mrapids-agent="$(pwd)/target/release/mrapids-agent"
```

### 4. Verify Installation
```bash
mrapids-agent --version
```

## Alternative: Direct Cargo Install from Git

```bash
# Install directly from GitHub (when ready)
cargo install --git https://github.com/deepwissen/api-runtime.git --branch Agentic_features mrapids-agent
```

## For Testing Without Installation

If you just want to test the agent without installing:

```bash
# From the agent directory
cargo run -- init
cargo run -- start
```

## Building for Distribution

### macOS
```bash
cargo build --release --target x86_64-apple-darwin
cargo build --release --target aarch64-apple-darwin

# Create universal binary
lipo -create \
  target/x86_64-apple-darwin/release/mrapids-agent \
  target/aarch64-apple-darwin/release/mrapids-agent \
  -output mrapids-agent-macos
```

### Linux
```bash
cargo build --release --target x86_64-unknown-linux-gnu
cp target/x86_64-unknown-linux-gnu/release/mrapids-agent mrapids-agent-linux
```

### Windows
```bash
cargo build --release --target x86_64-pc-windows-msvc
# Creates mrapids-agent.exe
```

## Current Status

⚠️ **Note**: `mrapids-agent` is currently in development and not yet published to crates.io. 

### What's Working:
- ✅ Core MCP server functionality
- ✅ Policy engine
- ✅ Audit logging
- ✅ Response redaction
- ✅ JSON-RPC protocol
- ✅ Basic CLI structure

### In Progress:
- 🚧 Full CLI command implementation
- 🚧 Daemon mode support
- 🚧 Binary distribution
- 🚧 Cargo package publishing

## For Claude Integration Testing

Since the agent isn't packaged yet, use the full path in Claude's config:

```json
{
  "mcpServers": {
    "mrapids": {
      "command": "/path/to/api-runtime/agent/target/release/mrapids-agent",
      "args": ["start", "--port", "8080"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

Or if you're testing with `cargo run`:

```json
{
  "mcpServers": {
    "mrapids": {
      "command": "cargo",
      "args": ["run", "--manifest-path", "/path/to/api-runtime/agent/Cargo.toml", "--", "start"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

## Development Setup

For active development:

```bash
# Clone and setup
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime/agent

# Run in development mode
cargo run -- start --dev

# Run tests
cargo test

# Check code
cargo clippy
cargo fmt
```

## Future Installation

Once published to crates.io:
```bash
# This will work in the future
cargo install mrapids-agent

# Or download pre-built binaries
curl -L https://github.com/deepwissen/api-runtime/releases/latest/download/mrapids-agent -o /usr/local/bin/mrapids-agent
chmod +x /usr/local/bin/mrapids-agent
```

## Need Help?

- Check the [MCP Agent Quickstart](./MCP_AGENT_QUICKSTART.md)
- See [Claude Integration Guide](./MCP_CLAUDE_INTEGRATION.md)
- Review [Testing Guide](../agent/TESTING_GUIDE.md)