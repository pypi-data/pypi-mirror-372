.PHONY: help build run test clean install fmt lint audit sbom sbom-check

# Default target
help:
	@echo "MicroRapid Development Commands"
	@echo "==============================="
	@echo "make build       - Build debug version"
	@echo "make release     - Build release version"
	@echo "make run         - Run with example"
	@echo "make test        - Run all tests"
	@echo "make clean       - Clean build artifacts"
	@echo "make install     - Install locally"
	@echo "make fmt         - Format code"
	@echo "make lint        - Run clippy linter"
	@echo "make audit       - Security audit"
	@echo "make sbom        - Generate Software Bill of Materials"
	@echo "make sbom-check  - Generate SBOM and check vulnerabilities"
	@echo "make all         - Format, lint, test, and build"

# Build debug version
build:
	cargo build

# Build release version
release:
	cargo build --release

# Run with example
run:
	cargo run -- run examples/petstore.yaml --operation getPetById

# Run init command
init:
	cargo run -- init test-project

# Run all tests
test:
	cargo test

# Run tests with output
test-verbose:
	cargo test -- --nocapture

# Clean build artifacts
clean:
	cargo clean
	rm -rf test-* tmp/

# Install locally
install:
	cargo install --path .

# Format code
fmt:
	cargo fmt

# Check formatting
fmt-check:
	cargo fmt -- --check

# Run clippy
lint:
	cargo clippy -- -D warnings

# Fix clippy warnings
lint-fix:
	cargo clippy --fix --allow-dirty

# Security audit
audit:
	cargo audit

# Check dependencies
deny:
	cargo deny check

# Run all checks (CI)
ci: fmt-check lint test build

# Full build pipeline
all: fmt lint test release

# Development watch mode (requires cargo-watch)
watch:
	cargo watch -x build

watch-test:
	cargo watch -x test

watch-run:
	cargo watch -x "run -- run examples/petstore.yaml --operation getPetById"

# Quick test of all commands
demo:
	@echo "Testing init command..."
	cargo run -- init demo-project --force
	@echo "\nTesting run command..."
	cargo run -- run examples/jsonplaceholder.yaml --operation getUsers
	@echo "\nTesting test command..."
	cargo run -- test examples/petstore.yaml --operation getPetById
	@echo "\nCleaning up..."
	rm -rf demo-project

# Show binary size
size: release
	@ls -lh target/release/mrapids | awk '{print "Release binary size: " $$5}'

# Run benchmarks
bench:
	cargo bench

# Generate documentation
docs:
	cargo doc --open

# Update dependencies
update:
	cargo update

# Check for outdated dependencies
outdated:
	cargo outdated

# Generate Software Bill of Materials (SBOM)
sbom:
	@echo "Generating Software Bill of Materials..."
	@./scripts/generate-sbom.sh

# Generate SBOM and check for vulnerabilities
sbom-check: sbom
	@echo "Checking for vulnerabilities in SBOMs..."
	@if command -v grype >/dev/null 2>&1; then \
		echo "Running Grype vulnerability scan..."; \
		grype sbom:sbom/mrapids-sbom-spdx.json --quiet || true; \
		grype sbom:sbom/mrapids-agent-sbom-spdx.json --quiet || true; \
	else \
		echo "Grype not installed. Install with: brew install grype"; \
	fi

# Install SBOM tools
install-sbom-tools:
	@echo "Installing SBOM generation tools..."
	cargo install cargo-sbom
	@echo "Installing vulnerability scanner..."
	@if [[ "$$(uname)" == "Darwin" ]]; then \
		brew install grype; \
	else \
		echo "Please install grype from https://github.com/anchore/grype"; \
	fi