# Micro Rapid CLI Reference

Complete reference for all Micro Rapid commands and options.

## Commands Overview

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize a new project from OpenAPI spec | `mrapids init api.yaml` |
| `gen` | Generate code, SDKs, and examples | `mrapids gen snippets` |
| `list` | List operations or requests | `mrapids list operations` |
| `show` | Show operation details | `mrapids show GetBalance` |
| `run` | Execute API operations | `mrapids run GetBalance` |
| `test` | Test API operations | `mrapids test --all` |
| `explore` | Search operations by keyword | `mrapids explore payment` |
| `auth` | Manage OAuth authentication | `mrapids auth login github` |
| `collection` | Manage and run API collections | `mrapids collection run smoke-tests` |
| `validate` | Validate OpenAPI specification | `mrapids validate specs/api.yaml` |
| `flatten` | Flatten OpenAPI spec (resolve $refs) | `mrapids flatten specs/api.yaml` |
| `diff` | Compare two OpenAPI specifications | `mrapids diff old.yaml new.yaml` |
| `setup-tests` | Set up test environment | `mrapids setup-tests specs/api.yaml` |
| `init-config` | Create environment configs | `mrapids init-config --env prod` |
| `cleanup` | Clean up test artifacts | `mrapids cleanup` |
| `help` | Show help information | `mrapids help` |

## Global Options

```bash
# Show version
mrapids --version

# Show help for any command
mrapids help <command>
mrapids <command> --help

# Enable debug output (for troubleshooting)
MRAPIDS_DEBUG=1 mrapids run GetBalance
```

---

## `init` - Initialize Project

Initialize a new Micro Rapid project from an OpenAPI specification.

### Usage
```bash
mrapids init <source> [output] [options]
```

### Arguments
- `<source>` - Path to OpenAPI spec file or URL
- `[output]` - Output directory (default: current directory)

### Options
```bash
--from-url              # Download spec from URL
--force                 # Overwrite existing files
--skip-examples         # Don't generate example requests
--skip-git              # Don't initialize git repository
--template <name>       # Use project template (default: standard)
```

### Examples
```bash
# From local file
mrapids init openapi.yaml my-api-project

# From URL
mrapids init --from-url https://api.example.com/openapi.json my-project

# Force overwrite
mrapids init api.yaml --force

# Minimal setup (no examples, no git)
mrapids init api.yaml --skip-examples --skip-git
```

### What it creates
```
project/
├── specs/
│   └── api.yaml          # Your OpenAPI spec
├── requests/
│   └── examples/         # Generated example requests
├── data/                 # Example payloads
├── config/               # Environment configs
├── scripts/              # Utility scripts
├── mrapids.yaml          # Project config
└── .gitignore
```

---

## `gen` - Generate Code, SDKs, and Examples

Generate various artifacts from your OpenAPI specification. This command consolidates all code generation functionality.

### Usage
```bash
mrapids gen <subcommand> [options]
```

### Subcommands

#### `gen snippets` - Generate Example Requests/Responses
**Replaces the deprecated `analyze` command.**

```bash
mrapids gen snippets [spec] [options]

Options:
  -o, --output <DIR>           # Output directory (default: ./examples)
  --operation <ID>             # Generate for specific operation only
  --format <FORMAT>            # Output format: json, yaml, curl, httpie, all
  --curl                       # Include cURL examples
  --httpie                     # Include HTTPie examples

Examples:
  # Generate all examples
  mrapids gen snippets
  
  # Generate for specific operation
  mrapids gen snippets --operation createUser
  
  # Generate cURL commands
  mrapids gen snippets --format curl
```

#### `gen sdk` - Generate SDK Client Libraries
**Replaces the deprecated `sdk` command.**

```bash
mrapids gen sdk [options]

Options:
  -l, --language <LANG>        # Language: typescript, python, go, rust
  -o, --output <DIR>           # Output directory
  --package <NAME>             # Package/module name
  --docs <BOOL>                # Include documentation (default: true)
  --examples <BOOL>            # Include examples (default: true)

Examples:
  # Generate TypeScript SDK
  mrapids gen sdk -l typescript
  
  # Generate Python SDK with custom name
  mrapids gen sdk -l python --package my-api-client
```

#### `gen stubs` - Generate Server Stubs
**Replaces the deprecated `generate` command.**

```bash
mrapids gen stubs [options]

Options:
  -f, --framework <NAME>       # Framework: express, fastapi, gin
  -o, --output <DIR>           # Output directory
  --with-tests                 # Include test stubs
  --with-validation            # Include validation middleware

Examples:
  # Generate Express.js server
  mrapids gen stubs --framework express
  
  # Generate with validation
  mrapids gen stubs --framework fastapi --with-validation
```

#### `gen fixtures` - Generate Test Fixtures
**Coming soon** - generates test data based on schemas.

### Migration from Deprecated Commands

| Old Command | New Command |
|-------------|-------------|
| `mrapids analyze` | `mrapids gen snippets` |
| `mrapids generate` | `mrapids gen stubs` |
| `mrapids sdk` | `mrapids gen sdk` |

### Output
- `requests/examples/*.yaml` - Request configurations
- `data/*.json` - Example request bodies
- Shows statistics about operations found

---

## `validate` - Validate OpenAPI Specification

Comprehensive validation of OpenAPI/Swagger specifications with multiple validation levels and best practice checks.

### Usage
```bash
mrapids validate [options] <spec>
```

### Arguments
- `<spec>` - Path to OpenAPI/Swagger specification file

### Options
```bash
--strict                  # Treat warnings as errors
--lint                    # Enable full validation with best practices
--format <text|json>      # Output format (default: text)
```

### Validation Levels

1. **Quick (default)** - Basic structural validation
2. **Standard (--strict)** - Comprehensive error checking including:
   - Reference validation (undefined schemas, responses, parameters)
   - Duplicate operation ID detection
   - Type constraint validation
   - Path parameter validation
3. **Full (--lint)** - All standard checks plus:
   - Missing descriptions and examples
   - Naming convention checks
   - Security warnings
   - Unused component detection

### Examples
```bash
# Basic validation
mrapids validate api-spec.yaml

# Strict mode for CI/CD
mrapids validate --strict api-spec.yaml

# Full linting with best practices
mrapids validate --lint api-spec.yaml

# JSON output for automation
mrapids validate --strict --format json api-spec.yaml | jq '.valid'
```

### Common Errors Detected
- **Undefined references**: `$ref` pointing to non-existent components
- **Duplicate operation IDs**: Multiple operations with same ID
- **Type violations**: Invalid type/constraint combinations (e.g., string with numeric constraints)
- **Missing path parameters**: Path variables not defined in parameters
- **Security issues**: HTTP instead of HTTPS, missing security schemes

### Output
- **Text format**: Human-readable with colors, error locations, and summaries
- **JSON format**: Machine-readable for CI/CD integration

---

## `list` - List Resources

List operations from API spec or saved request configurations.

### Usage
```bash
mrapids list <resource> [options]
```

### Arguments
- `<resource>` - What to list: `operations` (default), `requests`, `all`

### Options
```bash
-f, --filter <text>       # Filter by text
-m, --method <method>     # Filter by HTTP method
-t, --tag <tag>           # Filter by tag (operations only)
--format <format>         # Output format: table (default), simple, json, yaml
```

### Examples
```bash
# List all operations
mrapids list operations

# List only GET operations
mrapids list operations --method GET

# Filter by text
mrapids list operations --filter customer

# Filter by tag
mrapids list operations --tag "Payment Methods"

# List saved requests
mrapids list requests

# Simple format for scripts
mrapids list operations --format simple

# JSON output for processing
mrapids list operations --format json | jq '.[] | .operationId'
```

### Output Formats
- **table** - Formatted table with colors
- **simple** - One operation per line
- **json** - JSON array
- **yaml** - YAML format

---

## `show` - Show Operation Details

Display detailed information about an API operation.

### Usage
```bash
mrapids show <operation> [options]
```

### Arguments
- `<operation>` - Operation ID or partial name

### Options
```bash
-s, --spec <path>         # API spec file (default: specs/api.yaml)
--examples                # Show example requests
-f, --format <format>     # Output format: pretty (default), json, yaml
```

### Examples
```bash
# Show operation details
mrapids show GetBalance

# Partial name matching
mrapids show balance    # matches GetBalance

# Show with examples
mrapids show CreateCustomer --examples

# JSON output
mrapids show GetBalance --format json

# Custom spec file
mrapids show GetUser --spec other-api.yaml
```

### Output includes
- HTTP method and path
- Authentication requirements
- Path parameters
- Query parameters with examples
- Request body schema (for POST/PUT/PATCH)
- Response schemas

---

## `run` - Execute API Operations

Execute API operations directly from OpenAPI spec.

### Usage
```bash
mrapids run <operation> [options]
```

### Arguments
- `<operation>` - Operation ID, request file, or API spec

### Options

#### Data & Parameters
```bash
-d, --data <json>         # Request body: JSON string or @file
-f, --file <path>         # Request body from file
--stdin                   # Read request body from stdin
--required-only           # Generate minimal required fields

# Common parameters (auto-mapped)
--id <id>                 # Maps to {id}, {userId}, etc.
--name <name>             
--status <status>
--limit <n>
--offset <n>
--sort <field>

# Generic parameters
--param <key=value>       # Add any parameter (repeatable)
--query <key=value>       # Force query parameter (repeatable)
```

#### Headers & Auth
```bash
-H, --header <key:value>  # HTTP headers (repeatable)
--auth <token>            # Authorization header
--api-key <key>           # X-API-Key header
```

#### Environment & Config
```bash
--env <name>              # Environment config (default: development)
-u, --url <url>           # Override base URL
--template <name>         # Use request template
--template-vars <k=v>     # Template variables
```

#### Output & Control
```bash
-o, --output <format>     # Output: pretty (default), json, yaml, table
--save <path>             # Save response to file
--as-curl                 # Show as curl command
--dry-run                 # Don't send request
--verbose                 # Show request details
--no-color                # Disable colored output
```

#### Advanced
```bash
--timeout <seconds>       # Request timeout (default: 30)
--retry <count>           # Retry attempts (default: 0)
--follow-redirects        # Follow HTTP redirects
--insecure                # Skip TLS verification
```

### Examples - [See RUN_COMMAND.md for detailed examples]

---

## `explore` - Search Operations

Intelligent search for API operations using fuzzy matching across operation IDs, paths, summaries, descriptions, and tags.

### Usage
```bash
mrapids explore <keyword> [options]
```

### Arguments
- `<keyword>` - Search term or phrase (use quotes for multi-word searches)

### Options
```bash
-s, --spec <path>         # API spec file (auto-detects if not provided)
-l, --limit <n>           # Max results per category (default: 5)
--detailed                # Show full descriptions and context
-f, --format <format>     # Output: pretty (default), simple, json
```

### Search Features
- **Fuzzy Matching** - Handles typos and variations
- **Multi-field Search** - Searches across all operation metadata
- **Relevance Scoring** - Most relevant results appear first
- **Smart Grouping** - Results grouped by match quality

### Examples
```bash
# Search for payment-related operations
mrapids explore payment

# Multi-word search
mrapids explore "reset password"

# Show more results with descriptions
mrapids explore customer --limit 10 --detailed

# Find all operations (empty search)
mrapids explore "" --format json

# Simple format for scripting
mrapids explore user --format simple | grep POST

# Search and execute
op=$(mrapids explore "list users" --format simple | head -1 | awk '{print $1}')
mrapids run "$op"
```

### Output Formats
- **Pretty**: Colored output with relevance groups and descriptions
- **Simple**: One operation per line (scriptable)
- **JSON**: Structured data with scores and metadata

### Performance
- Sub-second results even for large APIs
- Works offline - no internet required
- Handles specs with 1000+ operations

---

## `init-config` - Initialize Environment Config

Create environment configuration files with examples.

### Usage
```bash
mrapids init-config [options]
```

### Options
```bash
-e, --env <name>          # Environment name (default: development)
-a, --api <name>          # Pre-configure for API: stripe, github, openai
-o, --output <path>       # Output path for config file
-f, --force               # Overwrite existing config
```

### Examples
```bash
# Create development config
mrapids init-config

# Create production config with safety checks
mrapids init-config --env production

# Pre-configured for Stripe
mrapids init-config --env production --api stripe

# Custom output location
mrapids init-config --output ~/configs/staging.yaml --env staging

# Force overwrite
mrapids init-config --env development --force
```

### Creates
- `config/{env}.yaml` - Environment configuration
- `config/.env` - Environment variables template
- `config/.env.example` - Example for version control

### Config includes
- Authentication setup
- Default headers
- Rate limiting
- Safety checks (for production)
- API-specific overrides

---

## Environment Variables

### Configuration
```bash
# Set default environment
export MRAPIDS_ENV=production

# API tokens (referenced in configs)
export STRIPE_TEST_KEY=sk_test_...
export GITHUB_TOKEN=ghp_...
export API_TOKEN=your_token_here
```

### Debugging
```bash
# Enable debug output
export MRAPIDS_DEBUG=1

# Disable color output
export NO_COLOR=1
```

### Proxy Settings
```bash
# HTTP proxy
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# No proxy for internal
export NO_PROXY=localhost,127.0.0.1,.internal.company.com
```

---

## Exit Codes

- `0` - Success
- `1` - General error
- `2` - Invalid arguments
- `3` - File not found
- `4` - Network error
- `5` - Authentication error
- `6` - Validation error

---

## Tips & Tricks

### Auto-completion
```bash
# Generate completion script
mrapids completions bash > /etc/bash_completion.d/mrapids
mrapids completions zsh > ~/.zsh/completions/_mrapids
mrapids completions fish > ~/.config/fish/completions/mrapids.fish
```

### Common Workflows
```bash
# Quick API test
mrapids show CreateUser && mrapids run CreateUser --required-only --dry-run

# Explore and run
mrapids explore payment | grep -i refund
mrapids show CreateRefund
mrapids run CreateRefund --id ch_123 --amount 500

# Test in different environments
for env in dev staging prod; do
  echo "Testing $env..."
  mrapids run HealthCheck --env $env
done
```

### Debugging
```bash
# Verbose output with curl
mrapids run GetBalance --verbose --as-curl

# Debug config loading
MRAPIDS_DEBUG=1 mrapids run GetBalance --env production

# Test without sending
mrapids run CreatePayment --data @big-payload.json --dry-run
```

---

## See Also

- [RUN_COMMAND.md](./RUN_COMMAND.md) - Detailed run command guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Technical architecture
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines