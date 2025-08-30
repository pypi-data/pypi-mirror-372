#!/bin/bash

# Complete GitHub Packages Setup Script
set -e

echo "📦 GitHub Packages Complete Setup"
echo "=================================="
echo ""
echo "This will set up GitHub Packages for:"
echo "  ✓ Docker/Container images"
echo "  ✓ Binary releases"
echo "  ✓ Generic packages"
echo "  ✓ Private package registry"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Function to create PAT instructions
create_pat_instructions() {
    echo -e "${YELLOW}📝 Creating a Personal Access Token (PAT)${NC}"
    echo ""
    echo "You need a GitHub token to publish packages."
    echo ""
    echo -e "${BLUE}Steps:${NC}"
    echo "1. Open in browser: https://github.com/settings/tokens/new"
    echo "2. Token name: 'GitHub Packages'"
    echo "3. Select scopes:"
    echo "   ✓ repo (for private repos)"
    echo "   ✓ write:packages"
    echo "   ✓ read:packages"
    echo "   ✓ delete:packages (optional)"
    echo "4. Click 'Generate token'"
    echo "5. COPY THE TOKEN (you won't see it again!)"
    echo ""
    
    read -p "Press Enter when you have copied your token..."
    echo ""
    
    read -s -p "Paste your GitHub token here: " GITHUB_TOKEN
    echo ""
    
    if [ -z "$GITHUB_TOKEN" ]; then
        echo -e "${RED}❌ No token provided${NC}"
        exit 1
    fi
    
    # Save token to file (optional)
    read -p "Save token to ~/.github-token for future use? (y/n): " save_token
    if [ "$save_token" = "y" ]; then
        echo "$GITHUB_TOKEN" > ~/.github-token
        chmod 600 ~/.github-token
        echo -e "${GREEN}✓ Token saved to ~/.github-token${NC}"
    fi
}

# Function to setup Docker
setup_docker() {
    echo ""
    echo -e "${YELLOW}🐳 Setting up Docker for GitHub Packages${NC}"
    echo ""
    
    # Get username
    GITHUB_USER=$(git config --global user.name || echo "")
    if [ -z "$GITHUB_USER" ]; then
        read -p "Enter your GitHub username: " GITHUB_USER
    fi
    
    # Login to ghcr.io
    echo "Logging into GitHub Container Registry..."
    echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USER" --password-stdin
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully logged into ghcr.io${NC}"
        
        # Save to Docker config
        echo -e "${GREEN}✓ Docker credentials saved${NC}"
    else
        echo -e "${RED}❌ Failed to login to Docker${NC}"
        return 1
    fi
}

# Function to create package.json for npm packages (if needed)
setup_npm() {
    echo ""
    echo -e "${YELLOW}📦 Setting up NPM for GitHub Packages${NC}"
    echo ""
    
    if [ ! -f "package.json" ]; then
        echo "No package.json found, skipping NPM setup"
        return
    fi
    
    # Create .npmrc
    cat > .npmrc << EOF
@microrapids:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=\${NPM_TOKEN}
EOF
    
    echo -e "${GREEN}✓ Created .npmrc for GitHub Packages${NC}"
}

# Function to test package publishing
test_publishing() {
    echo ""
    echo -e "${YELLOW}🧪 Testing Package Publishing${NC}"
    echo ""
    
    read -p "Do you want to test publishing now? (y/n): " test_now
    if [ "$test_now" != "y" ]; then
        return
    fi
    
    echo "Choose what to test:"
    echo "1) Docker image (quick)"
    echo "2) GitHub Action workflow"
    echo "3) Manual binary upload"
    
    read -p "Select option (1-3): " option
    
    case $option in
        1)
            echo "Building and pushing test Docker image..."
            docker build -t ghcr.io/microrapids/api-runtime:test .
            docker push ghcr.io/microrapids/api-runtime:test
            echo -e "${GREEN}✓ Test image pushed to ghcr.io${NC}"
            echo "View at: https://github.com/microrapids/api-runtime/packages"
            ;;
        2)
            echo "Triggering GitHub Action..."
            gh workflow run github-packages-all.yml -f package_types=docker
            echo -e "${GREEN}✓ Workflow triggered${NC}"
            echo "Check status: gh run list --workflow=github-packages-all.yml"
            ;;
        3)
            echo "Creating test package..."
            echo "test content" > test-package.txt
            tar czf test-package.tar.gz test-package.txt
            
            curl -X PUT \
                -H "Authorization: token $GITHUB_TOKEN" \
                -H "Content-Type: application/gzip" \
                --data-binary @test-package.tar.gz \
                "https://uploads.github.com/repos/microrapids/api-runtime/packages/generic/test-package/1.0.0/test-package.tar.gz"
            
            echo -e "${GREEN}✓ Test package uploaded${NC}"
            rm test-package.txt test-package.tar.gz
            ;;
    esac
}

# Function to create quick reference
create_reference() {
    cat > github-packages-quick-ref.md << 'EOF'
# GitHub Packages Quick Reference

## Authentication
```bash
# Docker
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Using stored token
export GITHUB_TOKEN=$(cat ~/.github-token)
```

## Publishing Commands

### Docker
```bash
# Build and tag
docker build -t ghcr.io/microrapids/api-runtime:latest .

# Push
docker push ghcr.io/microrapids/api-runtime:latest
```

### Generic Package
```bash
# Upload any file
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @myfile.tar.gz \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/generic/my-package/1.0.0/myfile.tar.gz"
```

### Using GitHub Actions
```bash
# Trigger workflow
gh workflow run github-packages-all.yml -f package_types=all

# Check status
gh run list --workflow=github-packages-all.yml
```

## Consuming Packages

### Docker
```bash
docker pull ghcr.io/microrapids/api-runtime:latest
```

### Generic Package
```bash
curl -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://github.com/microrapids/api-runtime/packages/generic/my-package/1.0.0/myfile.tar.gz" \
  -o myfile.tar.gz
```

## Package URLs
- View all: https://github.com/microrapids/api-runtime/packages
- Container: https://github.com/microrapids/api-runtime/pkgs/container/api-runtime
EOF
    
    echo -e "${GREEN}✓ Created github-packages-quick-ref.md${NC}"
}

# Main execution
main() {
    echo -e "${BLUE}Starting GitHub Packages setup...${NC}"
    echo ""
    
    # Step 1: Create PAT
    if [ -z "$GITHUB_TOKEN" ]; then
        if [ -f ~/.github-token ]; then
            echo "Found existing token in ~/.github-token"
            GITHUB_TOKEN=$(cat ~/.github-token)
        else
            create_pat_instructions
        fi
    fi
    
    # Step 2: Setup Docker
    if command -v docker &> /dev/null; then
        setup_docker
    else
        echo -e "${YELLOW}⚠ Docker not installed, skipping Docker setup${NC}"
    fi
    
    # Step 3: Setup NPM (if applicable)
    setup_npm
    
    # Step 4: Create reference
    create_reference
    
    # Step 5: Test publishing
    test_publishing
    
    echo ""
    echo -e "${GREEN}✨ GitHub Packages Setup Complete!${NC}"
    echo ""
    echo "📚 Resources:"
    echo "  • Quick reference: github-packages-quick-ref.md"
    echo "  • Full guide: docs/GITHUB-PACKAGES-GUIDE.md"
    echo "  • View packages: https://github.com/microrapids/api-runtime/packages"
    echo ""
    echo "🚀 Next steps:"
    echo "  1. Run: docker push ghcr.io/microrapids/api-runtime:test"
    echo "  2. Or trigger workflow: gh workflow run github-packages-all.yml"
    echo "  3. View your packages in GitHub!"
}

# Run main function
main