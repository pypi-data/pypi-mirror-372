# MicroRapid Project Structure

## Overview
This document describes the organization of the MicroRapid API Runtime project after cleanup and MCP integration.

## Directory Structure

```
api-runtime/
├── src/                      # Main application source
│   ├── main.rs              # CLI entry point
│   ├── lib.rs               # Library exports for external use
│   ├── cli/                 # CLI command definitions
│   ├── core/                # Core business logic
│   │   ├── api/            # Programmatic API layer
│   │   ├── policy/         # Policy engine for agent safety
│   │   ├── auth/           # Authentication management
│   │   ├── sdk_gen/        # SDK generation engine
│   │   └── commands/       # Command implementations
│   └── utils/              # Utility functions
│
├── agent/                   # MCP Server for AI agents
│   ├── src/                # MCP server source
│   │   ├── main.rs        # Server entry point
│   │   ├── audit.rs       # Audit logging
│   │   ├── auth.rs        # Auth profiles
│   │   ├── config.rs      # Configuration
│   │   ├── redact.rs      # Response redaction
│   │   └── tools/         # JSON-RPC tools
│   └── TESTING_GUIDE.md   # Testing documentation
│
├── schemas/                 # JSON schemas
│   └── tools/              # MCP tool schemas
│
├── specs/                   # API specifications
│   ├── examples/           # Example specs (petstore, etc.)
│   └── github-api.yaml     # GitHub API spec
│
├── examples/                # Usage examples
│   ├── api/               # API usage examples
│   ├── policy_integration.rs
│   └── mcp_test_client.py # MCP test client
│
├── requests/               # Example API requests
│   └── examples/          # Petstore examples
│
├── data/                   # Request/response data
│   └── examples/          # Example payloads
│
├── docs/                   # Documentation
│   ├── commands/          # Command documentation
│   ├── MCP_*.md          # MCP integration docs
│   └── ...               # Other documentation
│
├── github-api/            # GitHub API test suite
│   ├── specs/            # GitHub API specs
│   ├── requests/         # GitHub API requests
│   └── tests/            # GitHub API tests
│
├── Cargo.toml            # Rust project config
├── README.md             # Project README
├── Makefile              # Build automation
├── test_mcp_server.sh    # MCP test script
└── .gitignore            # Git ignore rules
```

## Key Components

### Core Application (`src/`)
The main MicroRapid CLI application with commands for:
- `run` - Execute API operations
- `list` - List available operations
- `show` - Show operation details
- `generate` - Generate SDKs
- `auth` - Manage authentication
- `validate` - Validate OpenAPI specs
- `resolve` - Resolve spec references
- And more...

### MCP Server (`agent/`)
A separate binary that provides AI agents with safe access to API operations through:
- JSON-RPC protocol
- Policy-based access control
- Audit logging
- Response redaction
- Auth profile management

### Documentation (`docs/`)
Comprehensive documentation including:
- Architecture guides
- Command references
- MCP integration design
- Implementation guides

### Examples (`examples/`)
Working examples demonstrating:
- API usage patterns
- Policy integration
- MCP client implementation

## Development Workflow

1. **Building**
   ```bash
   cargo build --release
   ```

2. **Testing**
   ```bash
   cargo test
   ./test_mcp_server.sh
   ```

3. **Running MCP Server**
   ```bash
   cd agent
   cargo run -- --config-dir .mrapids
   ```

## Cleanup Notes

The following temporary files and directories are ignored:
- Test SDK outputs (`test-sdk-*`, `test-*-sdk/`)
- Temporary test files (`*.test.json`, `test_*.py`)
- Build artifacts (`dist/`, `build/`)
- Log files (`*.log`)
- MCP test directories (`mcp-test-*/`)

See `.gitignore` for the complete list of ignored patterns.