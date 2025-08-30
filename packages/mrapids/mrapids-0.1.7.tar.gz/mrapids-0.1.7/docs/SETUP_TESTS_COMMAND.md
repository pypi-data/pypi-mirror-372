# 🛠️ MicroRapid Setup Tests Command - Generate Test Scripts from Your API

## The Problem

Testing APIs manually is tedious:
- 🔍 **Finding operations** - Digging through documentation
- 📝 **Writing commands** - Memorizing complex syntax
- 🔄 **Sharing tests** - Everyone writes their own scripts
- 🖥️ **Cross-platform** - Different scripts for different OS

## The Solution: `mrapids setup-tests`

Generate simple, executable test scripts from your OpenAPI spec. **One command, instant productivity.**

```bash
mrapids setup-tests api.yaml
```

## 🎯 Philosophy

- **One file, not 47** - Generate only what you need
- **Use familiar tools** - npm, make, shell, docker
- **Cross-platform by default** - Works everywhere
- **Zero learning curve** - It's just npm scripts
- **Fully customizable** - Edit the generated files

## 📦 Format Options

Choose the format that fits your team's workflow:

### 1. **NPM Format** (Default) - Universal, Cross-Platform

```bash
mrapids setup-tests api.yaml --format npm
```

**Generates:** `package.json`

```json
{
  "name": "api-tests",
  "version": "1.0.0",
  "scripts": {
    "api": "mrapids run api.yaml",
    "api:list": "echo 'Available commands:' && npm run | grep 'api:'",
    "api:list-users": "npm run api -- --operation getUsers",
    "api:get-user": "npm run api -- --operation getUserById --param id",
    "api:create-user": "npm run api -- --operation createUser --data",
    "api:update-user": "npm run api -- --operation updateUser --param id --data",
    "api:delete-user": "npm run api -- --operation deleteUser --param id"
  }
}
```

**Usage:**
```bash
# List all available commands
npm run api:list

# Run operations
npm run api:list-users
npm run api:get-user -- --param id=123
npm run api:create-user -- --data '{"name":"John"}'
```

**Perfect for:**
- ✅ Frontend teams
- ✅ Full-stack developers
- ✅ Cross-platform projects
- ✅ CI/CD pipelines

### 2. **Makefile Format** - Clean, Powerful, Unix-Friendly

```bash
mrapids setup-tests api.yaml --format make
```

**Generates:** `Makefile`

```makefile
# API Testing Commands
# Generated from: api.yaml

API := mrapids run api.yaml

.PHONY: help list-users get-user create-user update-user delete-user

help:
	@echo "Available commands:"
	@echo "  make list-users"
	@echo "  make get-user ID=123"
	@echo "  make create-user DATA='{\"name\":\"John\"}'"

list-users:
	$(API) --operation getUsers

get-user:
	$(API) --operation getUserById --param id=$(ID)

create-user:
	$(API) --operation createUser --data '$(DATA)'
```

**Usage:**
```bash
# See available commands
make help

# Run operations
make list-users
make get-user ID=123
make create-user DATA='{"name":"John"}'
```

**Perfect for:**
- ✅ Backend teams
- ✅ Go/Rust/C++ developers
- ✅ DevOps engineers
- ✅ Linux/Mac environments

### 3. **Shell Format** - Simple, Portable, CI-Friendly

```bash
mrapids setup-tests api.yaml --format shell
```

**Generates:** `api-test.sh`

```bash
#!/bin/bash
# API Test Commands
# Generated from: api.yaml

BASE_CMD="mrapids run api.yaml"

case "${1:-help}" in
  list-users)
    $BASE_CMD --operation getUsers "${@:2}"
    ;;
  get-user)
    $BASE_CMD --operation getUserById --param id="${2:-123}" "${@:3}"
    ;;
  create-user)
    $BASE_CMD --operation createUser --data "${2:-'{}'}" "${@:3}"
    ;;
  help|*)
    echo "Usage: $0 {list-users|get-user|create-user|update-user|delete-user}"
    echo ""
    echo "Examples:"
    echo "  $0 list-users"
    echo "  $0 get-user 123"
    echo "  $0 create-user '{\"name\":\"John\"}'"
    ;;
esac
```

**Usage:**
```bash
# Make executable
chmod +x api-test.sh

# Run operations
./api-test.sh list-users
./api-test.sh get-user 123
./api-test.sh create-user '{"name":"John"}'
```

**Perfect for:**
- ✅ CI/CD pipelines
- ✅ Automation scripts
- ✅ DevOps workflows
- ✅ Minimal dependencies

### 4. **Docker Compose Format** - Container-Ready

```bash
mrapids setup-tests api.yaml --format compose
```

**Generates:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  api-test:
    image: mrapids:latest
    volumes:
      - ./api.yaml:/api.yaml:ro
    environment:
      - API_BASE_URL=${API_BASE_URL:-http://localhost:8080}
      - API_KEY=${API_KEY}
    
  list-users:
    extends: api-test
    command: run /api.yaml --operation getUsers
    
  get-user:
    extends: api-test
    command: run /api.yaml --operation getUserById --param id=${USER_ID:-123}
    
  create-user:
    extends: api-test
    command: run /api.yaml --operation createUser --data '${USER_DATA:-{}}'
```

**Usage:**
```bash
# Run operations
docker-compose run list-users
docker-compose run get-user USER_ID=456
docker-compose run create-user USER_DATA='{"name":"John"}'
```

**Perfect for:**
- ✅ Microservices teams
- ✅ Kubernetes environments
- ✅ Cloud-native projects
- ✅ Isolated testing

### 5. **cURL Format** - Direct HTTP, No Dependencies

```bash
mrapids setup-tests api.yaml --format curl
```

**Generates:** `api-curl.sh`

```bash
#!/bin/bash
# Direct API Calls
# Generated from: api.yaml

BASE_URL="${API_BASE_URL:-https://api.example.com}"
AUTH_HEADER="${API_KEY:+Authorization: Bearer $API_KEY}"

# List all users
list_users() {
    curl -X GET \
        "${BASE_URL}/users" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        "$@"
}

# Get user by ID
get_user() {
    local id="${1:-123}"
    curl -X GET \
        "${BASE_URL}/users/${id}" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        "${@:2}"
}

# Create user
create_user() {
    local data="${1:-'{}'}"
    curl -X POST \
        "${BASE_URL}/users" \
        ${AUTH_HEADER:+-H "$AUTH_HEADER"} \
        -H "Content-Type: application/json" \
        -d "${data}" \
        "${@:2}"
}

# Main
case "${1:-help}" in
    list-users) list_users "${@:2}" ;;
    get-user) get_user "${@:2}" ;;
    create-user) create_user "${@:2}" ;;
    *) echo "Usage: $0 {list-users|get-user|create-user}" ;;
esac
```

**Usage:**
```bash
# Direct execution
./api-curl.sh list-users
./api-curl.sh get-user 123
./api-curl.sh create-user '{"name":"John"}'

# Or source and use functions
source api-curl.sh
list_users
get_user 456
```

**Perfect for:**
- ✅ Minimal environments
- ✅ Debugging
- ✅ No mrapids installation
- ✅ Production troubleshooting

## 🚀 Smart Features

### Auto-Detection

```bash
# Automatically detects best format based on existing files
mrapids setup-tests api.yaml

# If package.json exists → generates npm format
# If Makefile exists → generates make format
# If docker-compose.yml exists → generates compose format
# Otherwise → uses npm (most universal)
```

### Multiple Formats

```bash
# Generate multiple formats when needed
mrapids setup-tests api.yaml --format npm,make,shell

# Or generate all formats
mrapids setup-tests api.yaml --format all
```

### Custom Output

```bash
# Specify output directory
mrapids setup-tests api.yaml --output ./tests

# Custom file names
mrapids setup-tests api.yaml --format npm --output ./my-tests.json
```

### Environment Variables

All formats support environment variables:

```bash
# Set base URL
export API_BASE_URL=https://staging.api.com
export API_KEY=secret-key-123

# All formats will use these
npm run api:list-users
make list-users
./api-test.sh list-users
```

## 📊 Format Comparison

| Format | File | Platform | Dependencies | Best For |
|--------|------|----------|--------------|----------|
| **npm** | package.json | All | Node.js | Frontend teams, CI/CD |
| **make** | Makefile | Unix/Mac | Make | Backend teams |
| **shell** | .sh | Unix/Mac | Bash | Automation, DevOps |
| **compose** | docker-compose.yml | All | Docker | Microservices |
| **curl** | .sh | Unix/Mac | cURL | Debugging, minimal |

## 🎯 Real-World Examples

### Frontend Team Workflow

```bash
# Generate npm scripts
mrapids setup-tests api.yaml --format npm

# Add to existing package.json
npm install

# Use in development
npm run api:get-user -- --param id=123

# Add custom test sequences
npm run test:user-flow
```

### Backend Team Workflow

```bash
# Generate Makefile
mrapids setup-tests api.yaml --format make

# Run tests
make test-all

# Use in CI
make test-users || exit 1
```

### DevOps Automation

```bash
# Generate shell script
mrapids setup-tests api.yaml --format shell

# Use in automation
./api-test.sh list-users | jq '.[] | .id' > user-ids.txt
```

### Microservices Testing

```bash
# Generate compose file
mrapids setup-tests api.yaml --format compose

# Test service interactions
docker-compose run list-users
docker-compose run create-user USER_DATA="$(cat user.json)"
```

## 💡 Tips & Tricks

### 1. Combine with `jq` for JSON Processing

```bash
# npm format
npm run api:list-users | jq '.[] | {id, name}'

# shell format
./api-test.sh get-user 123 | jq '.email'
```

### 2. Create Test Pipelines

```json
{
  "scripts": {
    "test:create-and-verify": "npm run api:create-user -- --data '{\"name\":\"Test\"}' && npm run api:list-users | grep Test",
    "test:cleanup": "npm run api:delete-user -- --param id=test-user"
  }
}
```

### 3. Use with CI/CD

```yaml
# GitHub Actions
- name: Test API
  run: |
    mrapids setup-tests api.yaml --format npm
    npm run api:list-users
    npm run api:get-user -- --param id=1
```

### 4. Version Control

```bash
# Generate and commit
mrapids setup-tests api.yaml --format npm
git add package.json
git commit -m "Add API test commands"

# Team uses same commands
git pull
npm run api:list-users
```

## 🎁 Getting Started

### Installation

```bash
# Install MicroRapid
cargo install mrapids

# Or use pre-built binary
curl -L https://github.com/deepwissen/api-runtime/releases/latest/download/mrapids -o /usr/local/bin/mrapids
chmod +x /usr/local/bin/mrapids
```

### Your First Setup Tests

```bash
# 1. Generate test commands (npm by default)
mrapids setup-tests your-api.yaml

# 2. See what was generated
cat package.json

# 3. Use immediately
npm run api:list

# 4. Run your first test
npm run api:list-users
```

### Choose Your Format

```bash
# For backend team
mrapids setup-tests api.yaml --format make

# For DevOps
mrapids setup-tests api.yaml --format shell

# For containers
mrapids setup-tests api.yaml --format compose

# For debugging
mrapids setup-tests api.yaml --format curl
```

## 🚦 Command Reference

```bash
mrapids setup-tests <spec> [options]

Arguments:
  <spec>              Path to OpenAPI/Swagger specification

Options:
  -f, --format        Output format [npm|make|shell|compose|curl|all]
                      (default: npm or auto-detect)
  
  -o, --output        Output directory or file
                      (default: current directory)
  
  --force             Overwrite existing files
  
  --dry-run           Show what would be generated without creating files
  
  --with-examples     Include example usage in generated files
  
  --with-env          Generate .env.example file
  
  -h, --help          Show help
```

## 🎯 Value Proposition

### Without MicroRapid Setup Tests

- 📝 **2 hours** writing test scripts
- 🔄 **Constant updates** when API changes
- 🤷 **Inconsistent** scripts across team
- 🐛 **Typos and errors** in URLs and methods

### With MicroRapid Setup Tests

- ⚡ **2 seconds** to generate scripts
- 🔄 **Regenerate** when API changes
- 👥 **Same commands** for everyone
- ✅ **Error-free** generated code

**ROI: 2 hours → 2 seconds = 3600x faster**

## 📈 Success Metrics

- ⏱️ **Time saved:** 2+ hours per API
- 🐛 **Errors prevented:** 100% typo elimination
- 👥 **Team adoption:** 100% can use npm
- 📊 **Test coverage:** All endpoints accessible

## 🤝 Summary

The `setup-tests` command embodies MicroRapid's philosophy:

1. **Simple** - One command, one file
2. **Familiar** - Uses tools you know
3. **Flexible** - Choose your format
4. **Practical** - Immediately useful

Stop writing boilerplate test scripts. Start setup-testsing.

```bash
mrapids setup-tests your-api.yaml
```

**Your test commands are ready. What will you test first?**