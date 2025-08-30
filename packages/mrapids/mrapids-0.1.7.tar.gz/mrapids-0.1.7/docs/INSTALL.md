# Installation Guide for mrapids

## Quick Install

### From Source (Recommended for Development)
```bash
# Clone the repository
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime

# Install locally (to ~/.cargo/bin)
cargo install --path .

# Verify installation
mrapids --version
```

### Update PATH (if needed)

If `mrapids` is not found after installation, add cargo bin to your PATH:

```bash
# Add to ~/.zshrc or ~/.bashrc
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell configuration
source ~/.zshrc  # or source ~/.bashrc
```

### Dealing with Conflicts

If you have another `mrapids` installed:

```bash
# Check which mrapids is being used
which mrapids

# Use full path to our version
~/.cargo/bin/mrapids --version

# Or force reinstall
cargo install --path . --force

# Create an alias (add to ~/.zshrc or ~/.bashrc)
alias mrapids='~/.cargo/bin/mrapids'
```

## Using mrapids Command

Once installed, you can use `mrapids` directly:

### Initialize a New Project
```bash
# Create a basic REST API project
mrapids init my-api-project

# Create a GraphQL project
mrapids init my-graphql --template graphql

# Create an OpenAPI project
mrapids init my-openapi --template openapi
```

### Run API Operations
```bash
# Execute an operation from an OpenAPI spec
mrapids run api.yaml --operation getUserById

# With custom data
mrapids run api.yaml --operation createUser --data '{"name":"John"}'

# With custom base URL
mrapids run api.yaml --operation getUsers --url https://api.example.com
```

### Test APIs
```bash
# Test all operations in a spec
mrapids test api.yaml --all

# Test a specific operation
mrapids test api.yaml --operation getUserById
```

### Get Help
```bash
# General help
mrapids --help

# Command-specific help
mrapids init --help
mrapids run --help
mrapids test --help
```

## Example Workflow

```bash
# 1. Install mrapids
cargo install --path .

# 2. Create a new project
mrapids init my-api-project
cd my-api-project

# 3. Edit your OpenAPI spec
# Edit specs/api.yaml with your API definition

# 4. Test your API
mrapids run specs/api.yaml --operation getUsers

# 5. Run all tests
mrapids test specs/api.yaml --all
```

## Uninstall

```bash
# Remove mrapids
cargo uninstall mrapids
```

## Troubleshooting

### Command Not Found
- Ensure `~/.cargo/bin` is in your PATH
- Try using the full path: `~/.cargo/bin/mrapids`

### Permission Denied
```bash
chmod +x ~/.cargo/bin/mrapids
```

### Version Conflicts
```bash
# Check installed version
mrapids --version

# Force reinstall
cargo install --path . --force
```

## System Requirements

- Rust 1.70+ (install from [rustup.rs](https://rustup.rs/))
- macOS, Linux, or Windows
- ~10MB disk space for binary

## Binary Locations

- **Cargo install**: `~/.cargo/bin/mrapids`
- **System-wide**: `/usr/local/bin/mrapids` (requires sudo)
- **Development**: `./target/release/mrapids`

## Next Steps

After installation:
1. Run `mrapids init my-project` to create your first project
2. Check out the [examples](./examples/) folder for sample OpenAPI specs
3. Read [BUILD.md](./BUILD.md) for development instructions