# MicroRapid Help Documentation

> **Your OpenAPI, but executable** - Complete guide to MicroRapid CLI

## 📚 Documentation Overview

### Getting Started
- **[Quick Reference](./QUICK_REFERENCE.md)** - Essential commands and patterns
- **[CLI Command Guide](./CLI_COMMAND_GUIDE.md)** - Comprehensive command documentation
- **[Role-Based Commands](./ROLE_BASED_COMMANDS.md)** - Commands by job function
- **[Command Workflows](./COMMAND_WORKFLOWS.md)** - How commands work together

### Quick Links by Need

#### "I'm new to MicroRapid"
Start here: [Quick Reference](./QUICK_REFERENCE.md#-essential-commands)

#### "I need to test an API"
```bash
mrapids run api.yaml --operation getUser --dry-run
mrapids test api.yaml --operation getUser --validate
```
See: [Execution Commands](./CLI_COMMAND_GUIDE.md#-api-execution--testing)

#### "I need to set up CI/CD"
```bash
mrapids setup-tests api.yaml --with-ci github-actions
```
See: [DevOps Workflows](./ROLE_BASED_COMMANDS.md#-for-devops-engineers)

#### "I need to generate an SDK"
```bash
mrapids sdk api.yaml --language typescript
```
See: [Development Tools](./CLI_COMMAND_GUIDE.md#️-development-tools)

## 🎯 Command Categories

### 1. **Setup & Configuration**
- `init` - Create new project
- `init-config` - Configure environments
- `auth` - Manage authentication

### 2. **Discovery & Analysis**
- `list` - Browse operations
- `show` - Operation details
- `explore` - Search operations
- `analyze` - Generate examples

### 3. **Execution & Testing**
- `run` - Execute operations
- `test` - Test with validation
- `setup-tests` - Create test suites

### 4. **Development Tools**
- `validate` - Check spec validity
- `generate` - Generate code
- `sdk` - Create client SDKs
- `diff` - Compare versions

### 5. **Maintenance**
- `flatten` - Simplify specs
- `resolve` - Fix references
- `cleanup` - Remove temp files

## 🚀 Quick Start Examples

### Your First Commands
```bash
# 1. Initialize a project
mrapids init my-api --from-url https://petstore.swagger.io/v2/swagger.json

# 2. See what's available
mrapids list operations openapi.yaml

# 3. Try an operation
mrapids run openapi.yaml --operation getPetById --param petId=1

# 4. Generate SDK
mrapids sdk openapi.yaml --language python
```

### Common Patterns

#### Testing Pattern
```bash
validate → test → report
```

#### Development Pattern
```bash
diff → generate → test → run
```

#### CI/CD Pattern
```bash
validate --strict && test --all && diff --breaking-only
```

## 💡 Key Concepts

### 1. **Direct Execution**
Your OpenAPI spec IS the test. No conversion or import needed.

### 2. **Environment-Aware**
```bash
mrapids run api.yaml --operation getUser --env production
```

### 3. **Dry Run Safety**
Always preview with `--dry-run` before executing:
```bash
mrapids run api.yaml --operation deleteUser --dry-run
```

### 4. **Format Flexibility**
- Default: Human-readable tables
- `--format json`: For scripting
- `--format csv`: For reports
- `--curl-output`: For debugging

## 📖 Learning Path

### Beginner (Day 1)
1. Read [Quick Reference](./QUICK_REFERENCE.md)
2. Try `init`, `list`, `show`, `run`
3. Use `--help` on each command

### Intermediate (Week 1)
1. Read [CLI Command Guide](./CLI_COMMAND_GUIDE.md)
2. Set up authentication with `auth`
3. Create test suites with `setup-tests`
4. Generate SDKs with `sdk`

### Advanced (Month 1)
1. Study [Command Workflows](./COMMAND_WORKFLOWS.md)
2. Automate with CI/CD integration
3. Create custom workflows
4. Contribute to the project

## 🔧 Troubleshooting

### Common Issues

**"Command not found"**
```bash
# Check installation
which mrapids

# Reinstall if needed
cargo install mrapids
```

**"Invalid specification"**
```bash
# Validate first
mrapids validate api.yaml --verbose
```

**"Authentication failed"**
```bash
# Check auth profile
mrapids auth list
mrapids auth test <profile-name>
```

**"Operation not found"**
```bash
# List available operations
mrapids list operations api.yaml
# Search for similar
mrapids explore <keyword> --spec api.yaml
```

## 🎪 Tips & Tricks

### Speed Tips
```bash
# Set defaults
export MRAPIDS_SPEC=./api.yaml
export MRAPIDS_ENV=dev

# Create aliases
alias mr='mrapids'
alias mrt='mrapids test'
```

### Power User Features
```bash
# Pipe to other tools
mrapids run api.yaml --operation getUsers --format json | jq '.[] | .email'

# Parallel testing
cat operations.txt | xargs -P 4 -I {} mrapids test api.yaml --operation {}

# Watch mode (with fswatch)
fswatch api.yaml | xargs -I {} mrapids validate api.yaml
```

## 📞 Getting More Help

### In the CLI
```bash
mrapids --help              # General help
mrapids <command> --help    # Command-specific help
mrapids help <command>      # Alternative syntax
```

### Online Resources
- [GitHub Issues](https://github.com/microrapid/microrapid/issues)
- [Discord Community](https://discord.gg/microrapid)
- [Stack Overflow Tag](https://stackoverflow.com/questions/tagged/microrapid)

### Contributing
- [Contribution Guide](../CONTRIBUTING.md)
- [Development Setup](../DEVELOPMENT.md)
- [Architecture](../ARCHITECTURE.md)

---

## 🎯 Remember

**MicroRapid's Philosophy**: Your OpenAPI specification is directly executable. No conversion, no drift, no hassle.

**Start Simple**: 
```bash
mrapids run your-api.yaml --operation getHealth
```

**Grow from there**: The tool grows with your needs, from simple API calls to complex CI/CD pipelines.

---

*Happy API Testing! 🚀*