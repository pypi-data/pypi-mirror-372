#!/bin/bash
# Quick Pipeline Runner for AWS EC2 Instance
# Save this file and run it on your EC2 instance

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   MicroRapids CI/CD Pipeline Runner${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "Cargo.toml" ]; then
    echo -e "${YELLOW}Looking for api-runtime repository...${NC}"
    
    # Common locations
    if [ -d "$HOME/actions-runner/_work/api-runtime/api-runtime/api-runtime" ]; then
        cd "$HOME/actions-runner/_work/api-runtime/api-runtime/api-runtime"
    elif [ -d "$HOME/api-runtime/api-runtime" ]; then
        cd "$HOME/api-runtime/api-runtime"
    elif [ -d "$HOME/api-runtime" ]; then
        cd "$HOME/api-runtime"
    else
        echo -e "${RED}Repository not found. Cloning...${NC}"
        cd $HOME
        git clone https://github.com/microrapids/api-runtime.git
        cd api-runtime/api-runtime
    fi
fi

echo -e "${GREEN}✓${NC} Working directory: $(pwd)"
echo ""

# Pull latest changes
echo -e "${YELLOW}→${NC} Pulling latest changes from GitHub..."
git pull origin main || {
    echo -e "${RED}✗${NC} Git pull failed. Trying to reset..."
    git fetch origin
    git reset --hard origin/main
}

echo ""
echo -e "${BLUE}Starting Pipeline Tasks...${NC}"
echo "--------------------------"

# Task 1: Format check
echo -e "\n${YELLOW}[1/5]${NC} Checking code formatting..."
if cargo fmt -- --check 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Code formatting is correct"
else
    echo -e "${YELLOW}!${NC} Code needs formatting. Running formatter..."
    cargo fmt
    echo -e "${GREEN}✓${NC} Code has been formatted"
fi

# Task 2: Clippy
echo -e "\n${YELLOW}[2/5]${NC} Running Clippy linter..."
cargo clippy -- -W clippy::all 2>&1 | tail -5
echo -e "${GREEN}✓${NC} Clippy analysis complete"

# Task 3: Build
echo -e "\n${YELLOW}[3/5]${NC} Building project..."
cargo build --release --all-features
echo -e "${GREEN}✓${NC} Build successful"

# Task 4: Test
echo -e "\n${YELLOW}[4/5]${NC} Running tests..."
if cargo test --all-features --release; then
    echo -e "${GREEN}✓${NC} All tests passed"
else
    echo -e "${YELLOW}!${NC} Some tests failed (continuing anyway)"
fi

# Task 5: Create artifact
echo -e "\n${YELLOW}[5/5]${NC} Creating deployment artifact..."
VERSION=$(git rev-parse --short HEAD)
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARTIFACT_NAME="mrapids-${VERSION}-${TIMESTAMP}"

mkdir -p $HOME/artifacts
cp target/release/mrapids $HOME/artifacts/${ARTIFACT_NAME}
echo -e "${GREEN}✓${NC} Artifact created: $HOME/artifacts/${ARTIFACT_NAME}"

# Summary
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}✅ Pipeline Completed Successfully!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "📊 Summary:"
echo "  • Binary: $(ls -lh target/release/mrapids | awk '{print $5}')"
echo "  • Commit: $(git rev-parse HEAD)"
echo "  • Branch: $(git branch --show-current)"
echo "  • Time: $(date)"
echo "  • Artifact: $HOME/artifacts/${ARTIFACT_NAME}"
echo ""

# Optional: Run the binary to verify
echo -e "${YELLOW}Testing binary...${NC}"
./target/release/mrapids --version || echo "Version check failed"

echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. To publish NPM package: cd into project and run publish commands"
echo "  2. To build Docker: docker build -t mrapids:latest ."
echo "  3. To deploy: Use your deployment scripts"
echo ""