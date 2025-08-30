# MicroRapid Init Command Design

## Philosophy: Practical Organization

After careful consideration, we've chosen a **balanced approach** that provides meaningful structure without complexity.

## The 5-Folder Pattern

```
my-api-project/
├── specs/           # API specifications (OpenAPI, GraphQL schemas)
├── tests/           # Test scripts and test data  
├── scripts/         # Generated SDK/test scripts
├── config/          # Environment configs (.env files)
├── docs/            # API documentation
└── mrapids.yaml     # Project configuration
```

## Why This Structure Works

### 1. **For Developers**
- **Clear separation of concerns** - Each folder has one clear purpose
- **Easy to navigate** - 5 folders is manageable, not overwhelming
- **Gitignore-friendly** - Can easily ignore `scripts/` for generated code
- **IDE-friendly** - Modern IDEs can collapse/expand folders

### 2. **For AI Agents**
- **Predictable locations** - Agents know exactly where to find/place files
- **Context efficiency** - Can focus on specific folders
- **Clear boundaries** - Generated vs human-written code separation

### 3. **For Teams**
- **Onboarding simplicity** - New developers understand structure immediately
- **CI/CD friendly** - Build pipelines know where to find specs and tests
- **Review friendly** - PRs are organized by concern

## Template-Specific Structures

### REST API Project
```bash
mrapids init --template rest
```
```
my-rest-api/
├── specs/
│   └── api.yaml         # OpenAPI specification
├── tests/
│   └── smoke.test.js    # Basic smoke tests
├── scripts/
│   └── .gitkeep
├── config/
│   ├── .env.example     # Environment template
│   └── .env.local       # Local overrides (gitignored)
├── docs/
│   └── README.md        # API documentation
└── mrapids.yaml         # Project config
```

### GraphQL Project
```bash
mrapids init --template graphql
```
```
my-graphql-api/
├── specs/
│   ├── schema.graphql   # GraphQL schema
│   └── operations.graphql # Common operations
├── tests/
│   └── queries.test.js  # Query tests
├── scripts/
│   └── .gitkeep
├── config/
│   ├── .env.example
│   └── .env.local
├── docs/
│   └── README.md
└── mrapids.yaml
```

### Minimal Project (Default)
```bash
mrapids init
```
```
my-api/
├── specs/
│   └── api.yaml
├── config/
│   └── .env.example
└── mrapids.yaml
```

## The mrapids.yaml File

Central configuration that tells both humans and agents how the project is organized:

```yaml
name: my-api-project
version: 1.0.0
type: rest  # or 'graphql'

# Where things are
paths:
  specs: ./specs
  tests: ./tests
  scripts: ./scripts
  config: ./config

# Default spec to use
default_spec: ./specs/api.yaml

# Environments
environments:
  local:
    url: http://localhost:3000
    config: ./config/.env.local
  staging:
    url: https://staging.api.com
    config: ./config/.env.staging
  production:
    url: https://api.com
    config: ./config/.env.production

# Generation preferences
generate:
  output: ./scripts
  languages: [typescript, python]
  
# Testing preferences  
test:
  framework: jest  # or mocha, pytest, etc.
  pattern: "**/*.test.js"
```

## Commands That Work With Structure

```bash
# Initialize project
mrapids init --template rest

# Run using default spec
mrapids run  # Uses specs/api.yaml automatically

# Generate SDKs into scripts/
mrapids generate --language typescript  # Output: scripts/typescript-sdk/

# Setup Tests test scripts
mrapids setup-tests --format npm  # Output: scripts/package.json

# Run tests
mrapids test  # Finds tests in tests/ automatically
```

## Migration Path

For existing projects:
```bash
# Analyze and suggest structure
mrapids init --analyze

# Output:
# Found: api.yaml, test.js, config.json
# Suggested structure:
#   api.yaml → specs/api.yaml
#   test.js → tests/test.js
#   config.json → config/config.json
# 
# Run 'mrapids init --migrate' to reorganize
```

## Benefits Over Alternatives

### vs. Enterprise (10+ folders)
- ✅ Faster to understand
- ✅ Less decision fatigue
- ✅ Easier to maintain

### vs. Minimal (no folders)
- ✅ Better organization
- ✅ Scales better
- ✅ Clearer git history

### vs. Flat (all in root)
- ✅ Cleaner root directory
- ✅ Better for IDEs
- ✅ Easier .gitignore rules

## The "Boring is Good" Test

✅ **Predictable** - Anyone can guess where files go
✅ **Simple** - Can explain structure in 30 seconds  
✅ **Flexible** - Works for small and medium projects
✅ **Proven** - Similar to popular frameworks (Next.js, Rails)
✅ **Tool-friendly** - IDEs, git, CI/CD all work well

## Summary

The 5-folder pattern strikes the perfect balance:
- **Not too complex** (avoiding enterprise over-engineering)
- **Not too simple** (avoiding chaos as project grows)
- **Just right** (Goldilocks principle)

This structure helps developers stay organized while keeping AI agents efficient and predictable.