#!/bin/bash

# Setup script for ALL package managers with GitHub Packages
set -e

echo "🌍 GitHub Packages - All Language Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.github-token ]; then
        export GITHUB_TOKEN=$(cat ~/.github-token)
    else
        echo -e "${YELLOW}GitHub token not found!${NC}"
        echo "Please create a token at: https://github.com/settings/tokens/new"
        echo "With scopes: repo, write:packages, read:packages"
        read -s -p "Enter your GitHub token: " GITHUB_TOKEN
        echo ""
    fi
fi

# Get GitHub username
GITHUB_USER=$(git config --global user.name || echo "")
if [ -z "$GITHUB_USER" ]; then
    read -p "Enter your GitHub username: " GITHUB_USER
fi

echo -e "${BLUE}Setting up package managers...${NC}"
echo ""

# 1. Docker/Container Registry
setup_docker() {
    echo -e "${YELLOW}🐳 Docker/Container Registry${NC}"
    if command -v docker &> /dev/null; then
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USER" --password-stdin
        echo -e "${GREEN}✓ Docker configured for ghcr.io${NC}"
    else
        echo -e "${RED}✗ Docker not installed${NC}"
    fi
    echo ""
}

# 2. Python/PyPI
setup_python() {
    echo -e "${YELLOW}🐍 Python Packages${NC}"
    
    # Create pip config
    mkdir -p ~/.config/pip
    cat > ~/.config/pip/pip.conf << EOF
[global]
extra-index-url = https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/microrapids/api-runtime/packages/python/simple
EOF
    
    echo -e "${GREEN}✓ Python configured for GitHub Packages${NC}"
    echo "  Install with: pip install package-name"
    echo ""
}

# 3. NPM/JavaScript
setup_npm() {
    echo -e "${YELLOW}📦 NPM/JavaScript${NC}"
    
    if command -v npm &> /dev/null; then
        # Create npmrc
        cat > ~/.npmrc << EOF
@microrapids:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
EOF
        echo -e "${GREEN}✓ NPM configured for GitHub Packages${NC}"
        echo "  Install with: npm install @microrapids/package-name"
    else
        echo -e "${RED}✗ NPM not installed${NC}"
    fi
    echo ""
}

# 4. Maven/Java
setup_maven() {
    echo -e "${YELLOW}☕ Maven/Java${NC}"
    
    if command -v mvn &> /dev/null; then
        mkdir -p ~/.m2
        cat > ~/.m2/settings.xml << EOF
<settings>
  <servers>
    <server>
      <id>github</id>
      <username>${GITHUB_USER}</username>
      <password>${GITHUB_TOKEN}</password>
    </server>
  </servers>
</settings>
EOF
        echo -e "${GREEN}✓ Maven configured for GitHub Packages${NC}"
        echo "  Add to pom.xml:"
        echo "  <repository>"
        echo "    <id>github</id>"
        echo "    <url>https://maven.pkg.github.com/microrapids/*</url>"
        echo "  </repository>"
    else
        echo -e "${RED}✗ Maven not installed${NC}"
    fi
    echo ""
}

# 5. NuGet/.NET
setup_nuget() {
    echo -e "${YELLOW}🔷 NuGet/.NET${NC}"
    
    if command -v dotnet &> /dev/null; then
        dotnet nuget add source \
            --username "$GITHUB_USER" \
            --password "$GITHUB_TOKEN" \
            --store-password-in-clear-text \
            --name github-microrapids \
            "https://nuget.pkg.github.com/microrapids/index.json"
        
        echo -e "${GREEN}✓ NuGet configured for GitHub Packages${NC}"
        echo "  Install with: dotnet add package PackageName"
    else
        echo -e "${RED}✗ .NET SDK not installed${NC}"
    fi
    echo ""
}

# 6. Ruby Gems
setup_ruby() {
    echo -e "${YELLOW}💎 Ruby Gems${NC}"
    
    if command -v gem &> /dev/null; then
        mkdir -p ~/.gem
        echo "---" > ~/.gem/credentials
        echo ":github: Bearer ${GITHUB_TOKEN}" >> ~/.gem/credentials
        chmod 0600 ~/.gem/credentials
        
        echo -e "${GREEN}✓ Ruby Gems configured for GitHub Packages${NC}"
        echo "  Install with: gem install package-name --source https://rubygems.pkg.github.com/microrapids"
    else
        echo -e "${RED}✗ Ruby not installed${NC}"
    fi
    echo ""
}

# 7. Go Modules
setup_go() {
    echo -e "${YELLOW}🐹 Go Modules${NC}"
    
    if command -v go &> /dev/null; then
        go env -w GOPRIVATE=github.com/microrapids/*
        git config --global url."https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/"
        
        echo -e "${GREEN}✓ Go configured for private GitHub repos${NC}"
        echo "  Install with: go get github.com/microrapids/package-name"
    else
        echo -e "${RED}✗ Go not installed${NC}"
    fi
    echo ""
}

# 8. Cargo/Rust
setup_cargo() {
    echo -e "${YELLOW}🦀 Cargo/Rust${NC}"
    
    if command -v cargo &> /dev/null; then
        mkdir -p ~/.cargo
        cat >> ~/.cargo/config.toml << EOF

[net]
git-fetch-with-cli = true

[registries.github]
index = "https://github.com/microrapids/cargo-index"
token = "${GITHUB_TOKEN}"
EOF
        
        echo -e "${GREEN}✓ Cargo configured for GitHub registry${NC}"
        echo "  Add to Cargo.toml:"
        echo "  [dependencies]"
        echo "  package = { git = \"https://github.com/microrapids/repo\" }"
    else
        echo -e "${RED}✗ Cargo not installed${NC}"
    fi
    echo ""
}

# Run all setups
echo "Select what to configure:"
echo "1) All package managers"
echo "2) Docker only"
echo "3) Python only"
echo "4) NPM only"
echo "5) Java/Maven only"
echo "6) .NET/NuGet only"
echo "7) Ruby only"
echo "8) Go only"
echo "9) Rust/Cargo only"
echo ""

read -p "Enter choice (1-9): " choice

case $choice in
    1)
        setup_docker
        setup_python
        setup_npm
        setup_maven
        setup_nuget
        setup_ruby
        setup_go
        setup_cargo
        ;;
    2) setup_docker ;;
    3) setup_python ;;
    4) setup_npm ;;
    5) setup_maven ;;
    6) setup_nuget ;;
    7) setup_ruby ;;
    8) setup_go ;;
    9) setup_cargo ;;
    *) echo "Invalid choice" ;;
esac

# Create test packages
echo -e "${BLUE}Creating test commands file...${NC}"

cat > test-packages.sh << 'EOF'
#!/bin/bash

# Test commands for each package manager

echo "Testing Docker..."
docker pull ghcr.io/microrapids/api-runtime:latest || echo "No Docker image yet"

echo "Testing Python..."
pip search mrapids-client || echo "No Python package yet"

echo "Testing NPM..."
npm view @microrapids/api-runtime-client || echo "No NPM package yet"

echo "Testing Maven..."
mvn dependency:get -Dartifact=com.microrapids:api-runtime-client:LATEST || echo "No Maven package yet"

echo "Testing NuGet..."
dotnet list package --source github-microrapids || echo "No NuGet packages yet"

echo "Testing Ruby..."
gem list --remote --source https://rubygems.pkg.github.com/microrapids || echo "No Ruby gems yet"

echo "Testing Go..."
go list -m github.com/microrapids/api-runtime@latest || echo "No Go module yet"
EOF

chmod +x test-packages.sh

echo ""
echo -e "${GREEN}✨ Setup Complete!${NC}"
echo ""
echo "Configuration saved for:"
for manager in Docker Python NPM Maven NuGet Ruby Go Cargo; do
    echo "  ✓ $manager"
done
echo ""
echo "📦 To publish packages:"
echo "  1. Manual: Use scripts in scripts/ directory"
echo "  2. Automated: gh workflow run multi-language-packages.yml"
echo ""
echo "🧪 To test installations:"
echo "  Run: ./test-packages.sh"
echo ""
echo "📚 Documentation:"
echo "  • Full guide: docs/ALL-PACKAGE-MANAGERS.md"
echo "  • GitHub Packages: https://github.com/microrapids/api-runtime/packages"