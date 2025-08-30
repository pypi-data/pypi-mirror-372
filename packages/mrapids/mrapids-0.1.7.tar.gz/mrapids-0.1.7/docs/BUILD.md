# Build, Run, and Test Guide

## Prerequisites

- Rust 1.70+ (install from [rustup.rs](https://rustup.rs/))
- Git

## Quick Start

```bash
# Clone the repository
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime

# Build the project
cargo build

# Run the CLI
cargo run -- --help
```

## Build Commands

### Development Build
```bash
# Build with debug symbols (fast compile, slow runtime)
cargo build

# Binary location: target/debug/mrapids
```

### Release Build
```bash
# Build optimized version (slow compile, fast runtime)
cargo build --release

# Binary location: target/release/mrapids
# Size: ~5.8MB
```

### Check Without Building
```bash
# Just check if code compiles
cargo check
```

## Run Commands

### Using Cargo

```bash
# Initialize a new project
cargo run -- init my-api-project
cargo run -- init my-graphql --template graphql

# Run an OpenAPI operation
cargo run -- run examples/petstore.yaml --operation getPetById

# Test all operations in a spec
cargo run -- test examples/jsonplaceholder.yaml --all

# Get help
cargo run -- --help
cargo run -- run --help
```

### Using Compiled Binary

```bash
# First build the release version
cargo build --release

# Then run directly
./target/release/mrapids init my-project
./target/release/mrapids run examples/petstore.yaml --operation getPetById
./target/release/mrapids test examples/jsonplaceholder.yaml --all
```

### Install Locally

```bash
# Install to ~/.cargo/bin
cargo install --path .

# Now you can run from anywhere
mrapids init my-project
mrapids run api.yaml --operation getUser
```

## Test Commands

### Run All Tests
```bash
# Run unit and integration tests
cargo test

# Run tests with output
cargo test -- --nocapture

# Run tests in parallel
cargo test -- --test-threads=4
```

### Run Specific Tests
```bash
# Test a specific module
cargo test core::spec

# Test a specific function
cargo test test_load_openapi_spec

# Run only unit tests
cargo test --lib

# Run only integration tests
cargo test --test '*'
```

### Test Coverage
```bash
# Install tarpaulin for coverage
cargo install cargo-tarpaulin

# Generate coverage report
cargo tarpaulin --out Html

# Open coverage report
open tarpaulin-report.html
```

## Code Quality

### Linting
```bash
# Run clippy for linting
cargo clippy

# Run clippy and fail on warnings
cargo clippy -- -D warnings

# Auto-fix clippy suggestions
cargo clippy --fix
```

### Formatting
```bash
# Check formatting
cargo fmt -- --check

# Auto-format code
cargo fmt
```

### Security Audit
```bash
# Check for security vulnerabilities
cargo audit

# Check dependencies
cargo deny check
```

## Development Workflow

### Watch Mode
```bash
# Install cargo-watch
cargo install cargo-watch

# Auto-rebuild on changes
cargo watch -x build

# Auto-test on changes
cargo watch -x test

# Auto-run on changes
cargo watch -x "run -- run examples/petstore.yaml --operation getPetById"
```

### Clean Build
```bash
# Remove all build artifacts
cargo clean

# Then rebuild
cargo build
```

## Example Usage

### 1. Initialize a Project
```bash
# Create a REST API project
cargo run -- init my-api
cd my-api
# Edit specs/api.yaml with your OpenAPI spec
```

### 2. Run Operations
```bash
# Execute a specific operation
cargo run -- run specs/api.yaml --operation getUserById

# With data
cargo run -- run specs/api.yaml --operation createUser --data '{"name":"John"}'

# With custom base URL
cargo run -- run specs/api.yaml --operation getUsers --url https://api.example.com
```

### 3. Test APIs
```bash
# Test all operations
cargo run -- test specs/api.yaml --all

# Test specific operation
cargo run -- test specs/api.yaml --operation getUserById
```

## Benchmarking

```bash
# Run benchmarks
cargo bench

# Run specific benchmark
cargo bench bench_name
```

## Troubleshooting

### Common Issues

1. **Compilation Errors**
   ```bash
   # Update dependencies
   cargo update
   
   # Clean and rebuild
   cargo clean
   cargo build
   ```

2. **Slow Compilation**
   ```bash
   # Use faster linker (on macOS)
   brew install michaeleisel/zld/zld
   
   # Add to ~/.cargo/config
   [target.x86_64-apple-darwin]
   rustflags = ["-C", "link-arg=-fuse-ld=/usr/local/bin/zld"]
   ```

3. **Out of Memory**
   ```bash
   # Limit parallel jobs
   cargo build -j 2
   ```

## CI/CD Commands

```bash
# Run all checks (for CI)
cargo fmt -- --check && \
cargo clippy -- -D warnings && \
cargo test && \
cargo build --release
```

## Performance Profiling

```bash
# Install flamegraph
cargo install flamegraph

# Generate flamegraph
cargo flamegraph --bin mrapids -- run examples/petstore.yaml --operation getPetById

# Open flamegraph
open flamegraph.svg
```

## Docker Build (Optional)

```bash
# Create Dockerfile first, then:
docker build -t mrapids .
docker run mrapids --help
```

## Summary

- **Build**: `cargo build` (dev) or `cargo build --release` (prod)
- **Run**: `cargo run -- [command]` or `./target/release/mrapids [command]`
- **Test**: `cargo test`
- **Lint**: `cargo clippy`
- **Format**: `cargo fmt`
- **Clean**: `cargo clean`