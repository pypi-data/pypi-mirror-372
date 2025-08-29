# MicroRapid

> **Your OpenAPI, but executable**

MicroRapid is a universal API execution engine that makes existing API specifications directly executable without conversion. Built on the core insight that "APIs should be executable, not just documented," MicroRapid eliminates the need for multiple tools by providing a single CLI that can execute OpenAPI specs, GraphQL schemas, and cURL commands directly.

## Key Features

- **Zero Learning Curve** - Uses existing OpenAPI/GraphQL knowledge
- **No Format Conversion** - Execute specs directly, no intermediate files
- **Always In Sync** - No drift between specs and tests
- **Universal Support** - One tool for multiple API formats
- **Cross-Platform** - Works everywhere Rust runs
- **OAuth 2.0 Support** - Built-in authentication for GitHub, Google, Microsoft, and more

## Quick Start

```bash
# Execute OpenAPI operations directly
mrapids run openapi.yaml --operation getUserById --data user.json

# With OAuth authentication
mrapids auth login github
mrapids run list-repos --profile github

# Execute GraphQL queries from schema
mrapids run schema.graphql --query getUserById --variables user.json

# Execute cURL commands with organization
mrapids run commands.curl --batch

# Watch for spec changes and re-run tests
mrapids watch openapi.yaml --operation getUserById

# Verify API implementation matches specification
mrapids verify openapi.yaml --against https://api.example.com
```

## Installation

```bash
# Using Cargo
cargo install microrapid

# Using Homebrew
brew install microrapid

# Using npm (wrapper)
npm install -g microrapid
```

## Core Capabilities

### OpenAPI Direct Execution
Execute OpenAPI 3.0/3.1 specifications directly without any conversion or intermediate files. Support for all standard HTTP methods, authentication schemes, and request/response validation.

### GraphQL Schema Execution
Run queries, mutations, and subscriptions directly from GraphQL schema files with full variable support and schema validation.

### cURL Command Execution
Organize and execute cURL commands with environment variable substitution and batch execution capabilities.

### Advanced Features
- **Watch Mode** - Automatically re-run tests when specifications change
- **Data Generation** - Generate test data from schemas
- **Performance Testing** - Load test APIs directly from specifications
- **Contract Validation** - Verify API implementations match their specifications

## Documentation

- [Architecture](./ARCHITECTURE.md) - Core development principles
- [Contributing](./CONTRIBUTING.md) - How to contribute
- [Full Documentation](./docs/) - Requirements, roadmap, and more

## Project Status

MicroRapid is currently in active development. See our [Roadmap](./docs/ROADMAP.md) for upcoming features and release plans.

## Target Users

- **API Developers** - Building and maintaining REST/GraphQL APIs
- **Frontend Developers** - Consuming APIs, need quick testing
- **DevOps Engineers** - Automating API testing in CI/CD pipelines
- **QA Engineers** - API testing and validation

## Why MicroRapid?

Traditional API development requires maintaining multiple tools and formats:
- API specifications for documentation
- Separate test files for validation
- Different tools for different API types
- Constant synchronization between specs and tests

MicroRapid solves this by making your existing specifications directly executable, eliminating the need for format conversion and reducing maintenance overhead.

## Documentation

- [Features Overview](./docs/FEATURES.md) - Complete feature list and capabilities
- [Project Structure](./docs/PROJECT_STRUCTURE.md) - Repository organization guide
- [CLI Reference](./docs/CLI_REFERENCE.md) - Detailed command documentation
- [Architecture](./docs/ARCHITECTURE.md) - Technical architecture overview
- [MCP Integration](./docs/MCP_INTEGRATION_DESIGN.md) - AI agent integration guide

For more documentation, see the [docs](./docs/) directory.

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](./docs/CONTRIBUTING.md) for details.

## License

MicroRapid is open source software licensed under the MIT License.

## Support

- [GitHub Issues](https://github.com/deepwissen/api-runtime/issues) - Bug reports and feature requests
- [Discussions](https://github.com/deepwissen/api-runtime/discussions) - Community discussions
- [Documentation](./docs/) - Full documentation

---

Built with Rust for performance and reliability. Designed for developers who value simplicity and efficiency.