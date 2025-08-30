#!/bin/bash
# Security setup script for MicroRapids API Runtime

set -e

echo "🔒 MicroRapids Security Setup"
echo "=============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running in project root
if [ ! -f "Cargo.toml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

echo "📦 Installing security tools..."
echo ""

# Install cargo-audit
if ! command -v cargo-audit &> /dev/null; then
    echo "Installing cargo-audit..."
    cargo install cargo-audit
    print_status "cargo-audit installed"
else
    print_status "cargo-audit already installed"
fi

# Install cargo-deny
if ! command -v cargo-deny &> /dev/null; then
    echo "Installing cargo-deny..."
    cargo install cargo-deny
    print_status "cargo-deny installed"
else
    print_status "cargo-deny already installed"
fi

# Install cargo-license
if ! command -v cargo-license &> /dev/null; then
    echo "Installing cargo-license..."
    cargo install cargo-license
    print_status "cargo-license installed"
else
    print_status "cargo-license already installed"
fi

# Install cargo-outdated
if ! command -v cargo-outdated &> /dev/null; then
    echo "Installing cargo-outdated..."
    cargo install cargo-outdated
    print_status "cargo-outdated installed"
else
    print_status "cargo-outdated already installed"
fi

# Install cargo-sbom
if ! command -v cargo-sbom &> /dev/null; then
    echo "Installing cargo-sbom..."
    cargo install cargo-sbom
    print_status "cargo-sbom installed"
else
    print_status "cargo-sbom already installed"
fi

echo ""
echo "🔍 Installing secret scanning tools..."
echo ""

# Install gitleaks
if ! command -v gitleaks &> /dev/null; then
    echo "Installing gitleaks..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gitleaks
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Download latest release for Linux
        curl -sSfL https://github.com/gitleaks/gitleaks/releases/latest/download/gitleaks_linux_x64.tar.gz | tar -xz
        sudo mv gitleaks /usr/local/bin/
    fi
    print_status "gitleaks installed"
else
    print_status "gitleaks already installed"
fi

# Install pre-commit
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip install pre-commit || pip3 install pre-commit
    print_status "pre-commit installed"
else
    print_status "pre-commit already installed"
fi

echo ""
echo "⚙️ Configuring security tools..."
echo ""

# Set up pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    pre-commit install --hook-type commit-msg
    print_status "Pre-commit hooks installed"
else
    print_warning "No .pre-commit-config.yaml found"
fi

# Create cargo-deny configuration if it doesn't exist
if [ ! -f "deny.toml" ]; then
    cat > deny.toml << 'EOF'
# cargo-deny configuration

[licenses]
unlicensed = "deny"
allow = [
    "MIT",
    "Apache-2.0",
    "Apache-2.0 WITH LLVM-exception",
    "BSD-2-Clause",
    "BSD-3-Clause",
    "ISC",
    "Unicode-DFS-2016",
]
copyleft = "warn"

[bans]
multiple-versions = "warn"
wildcards = "allow"
highlight = "all"

[advisories]
db-path = "~/.cargo/advisory-db"
db-urls = ["https://github.com/rustsec/advisory-db"]
vulnerability = "deny"
unmaintained = "warn"
yanked = "warn"
notice = "warn"
ignore = []

[sources]
unknown-registry = "warn"
unknown-git = "warn"
allow-registry = ["https://github.com/rust-lang/crates.io-index"]
allow-git = []
EOF
    print_status "Created deny.toml configuration"
else
    print_status "deny.toml already exists"
fi

echo ""
echo "🏃 Running security checks..."
echo ""

# Run cargo audit
echo "Running cargo audit..."
if cargo audit; then
    print_status "No vulnerabilities found"
else
    print_warning "Vulnerabilities detected - please review and fix"
fi

# Run cargo deny check
echo "Running cargo deny..."
if cargo deny check 2>/dev/null; then
    print_status "Dependency check passed"
else
    print_warning "Dependency issues found - please review"
fi

# Run gitleaks
echo "Running gitleaks scan..."
if gitleaks detect --source . --verbose --no-git; then
    print_status "No secrets detected"
else
    print_warning "Potential secrets detected - please review"
fi

echo ""
echo "📊 Security Report"
echo "=================="
echo ""

# Generate security report
echo "## Dependency Licenses"
cargo license | head -20

echo ""
echo "## Outdated Dependencies"
cargo outdated | head -20 || echo "No outdated dependencies"

echo ""
echo "📋 Security Checklist"
echo "====================="
echo ""

# Security checklist
checklist=(
    "SECURITY.md policy file exists"
    "Dependabot configuration exists"
    "Security GitHub workflow exists"
    "Pre-commit hooks configured"
    "Gitleaks configuration exists"
    "Cargo audit passes"
)

for item in "${checklist[@]}"; do
    case "$item" in
        "SECURITY.md policy file exists")
            [ -f "SECURITY.md" ] && print_status "$item" || print_error "$item"
            ;;
        "Dependabot configuration exists")
            [ -f ".github/dependabot.yml" ] && print_status "$item" || print_error "$item"
            ;;
        "Security GitHub workflow exists")
            [ -f ".github/workflows/security.yml" ] && print_status "$item" || print_error "$item"
            ;;
        "Pre-commit hooks configured")
            [ -f ".pre-commit-config.yaml" ] && print_status "$item" || print_error "$item"
            ;;
        "Gitleaks configuration exists")
            [ -f ".gitleaks.toml" ] && print_status "$item" || print_error "$item"
            ;;
        "Cargo audit passes")
            cargo audit &>/dev/null && print_status "$item" || print_warning "$item (has warnings)"
            ;;
    esac
done

echo ""
echo "✅ Security setup complete!"
echo ""
echo "Next steps:"
echo "1. Review and fix any vulnerabilities found by cargo audit"
echo "2. Update any outdated dependencies"
echo "3. Configure GitHub repository settings:"
echo "   - Enable Dependabot alerts"
echo "   - Enable secret scanning (Settings > Security > Code security)"
echo "   - Enable branch protection rules"
echo "4. Run 'pre-commit run --all-files' to check all files"
echo "5. Commit and push security improvements"