#!/bin/bash

# Setup script for configuring artifact publishing
set -e

echo "🚀 MicroRapids Publishing Setup"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if in project root
if [ ! -f "Cargo.toml" ]; then
    echo -e "${RED}❌ Please run this script from the project root${NC}"
    exit 1
fi

echo "This script will help you set up publishing to:"
echo "  • crates.io (Rust packages)"
echo "  • Docker Hub (Container images)"
echo "  • GitHub Packages (Releases)"
echo ""

# Function to check command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "📋 Checking prerequisites..."
echo ""

if command_exists cargo; then
    echo -e "${GREEN}✓${NC} Rust/Cargo installed"
else
    echo -e "${RED}✗${NC} Rust/Cargo not found"
    echo "  Install from: https://rustup.rs"
fi

if command_exists docker; then
    echo -e "${GREEN}✓${NC} Docker installed"
else
    echo -e "${YELLOW}⚠${NC} Docker not found (optional)"
    echo "  Install from: https://docker.com"
fi

if command_exists gh; then
    echo -e "${GREEN}✓${NC} GitHub CLI installed"
else
    echo -e "${YELLOW}⚠${NC} GitHub CLI not found (optional)"
    echo "  Install from: https://cli.github.com"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Setup crates.io
echo "📦 Setting up crates.io"
echo "------------------------"
echo ""
echo "1. Create account at: https://crates.io/signup"
echo "2. Get your API token from: https://crates.io/me"
echo ""

read -p "Do you have a crates.io API token? (y/n): " has_crates_token
if [ "$has_crates_token" = "y" ]; then
    echo ""
    echo "Run this command to save your token locally:"
    echo -e "${YELLOW}cargo login <your-token>${NC}"
    echo ""
    echo "For CI/CD, add this secret to GitHub:"
    echo "  • Go to: https://github.com/microrapids/api-runtime/settings/secrets/actions"
    echo "  • Add new secret:"
    echo "    Name: CARGO_REGISTRY_TOKEN"
    echo "    Value: <your-token>"
    echo -e "${GREEN}✓${NC} crates.io setup instructions provided"
else
    echo -e "${YELLOW}ℹ${NC} Skip crates.io setup for now"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Setup Docker Hub
echo "🐳 Setting up Docker Hub"
echo "------------------------"
echo ""
echo "1. Create account at: https://hub.docker.com/signup"
echo "2. Create repository: https://hub.docker.com/repository/create"
echo "   Repository name: api-runtime"
echo ""

read -p "Do you have a Docker Hub account? (y/n): " has_docker
if [ "$has_docker" = "y" ]; then
    echo ""
    echo "Run this command to login locally:"
    echo -e "${YELLOW}docker login${NC}"
    echo ""
    echo "For CI/CD, add these secrets to GitHub:"
    echo "  • Go to: https://github.com/microrapids/api-runtime/settings/secrets/actions"
    echo "  • Add two secrets:"
    echo "    1. Name: DOCKER_USERNAME"
    echo "       Value: <your-docker-username>"
    echo "    2. Name: DOCKER_PASSWORD"
    echo "       Value: <your-docker-password>"
    echo -e "${GREEN}✓${NC} Docker Hub setup instructions provided"
else
    echo -e "${YELLOW}ℹ${NC} Skip Docker Hub setup for now"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Setup GitHub Packages
echo "📦 Setting up GitHub Packages"
echo "-----------------------------"
echo ""
echo "GitHub Packages works automatically with your GitHub account!"
echo "No additional setup needed for public repositories."
echo ""
echo -e "${GREEN}✓${NC} GitHub Packages ready to use"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Create example commands file
echo "📝 Creating example commands..."
cat > publishing-commands.md << 'EOF'
# Publishing Commands Reference

## Local Testing

```bash
# Build release binary
cargo build --release

# Test that package is ready to publish
cargo publish --dry-run

# Build Docker image
docker build -t api-runtime:test .
```

## Manual Publishing

### Publish to crates.io
```bash
# Make sure version in Cargo.toml is updated
cargo publish
```

### Publish to Docker Hub
```bash
docker build -t yourusername/api-runtime:v1.0.0 .
docker push yourusername/api-runtime:v1.0.0
```

## Automated Publishing (Recommended)

### Create a Release
```bash
# 1. Update version in Cargo.toml
# 2. Commit changes
git add Cargo.toml
git commit -m "chore: bump version to 1.0.0"

# 3. Create and push tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 4. Create release on GitHub
gh release create v1.0.0 --title "Release v1.0.0" --notes "See CHANGELOG.md"
```

The CI/CD will automatically:
- Publish to crates.io
- Push to Docker Hub
- Create GitHub release with binaries

## Check Published Artifacts

```bash
# Check crates.io
cargo search mrapids

# Check Docker Hub
docker pull yourusername/api-runtime:latest

# Check GitHub Packages
docker pull ghcr.io/microrapids/api-runtime:latest

# Download release binary
curl -LO https://github.com/microrapids/api-runtime/releases/latest/download/mrapids-linux-amd64.tar.gz
```
EOF

echo -e "${GREEN}✓${NC} Created publishing-commands.md"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Summary
echo "✨ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure the services you want to use (see instructions above)"
echo "2. Add the required secrets to GitHub"
echo "3. Test with a dry run: ${YELLOW}gh workflow run publish.yml -f dry_run=true${NC}"
echo "4. Create your first release!"
echo ""
echo "📚 Resources:"
echo "  • Artifact guide: docs/ARTIFACT-MANAGEMENT.md"
echo "  • Publishing commands: publishing-commands.md"
echo "  • CI/CD docs: docs/CI-CD.md"
echo ""
echo "Need help? Check the documentation or create an issue on GitHub."