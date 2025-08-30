#!/bin/bash

# Script to build and push Docker image to GitHub Container Registry
set -e

echo "🐳 Docker Build & Push to GitHub Container Registry"
echo "==================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
REGISTRY="ghcr.io"
NAMESPACE="microrapids"
IMAGE_NAME="api-runtime"
FULL_IMAGE="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker from: https://docker.com"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop or Docker daemon"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker is running"
echo ""

# Get version from Cargo.toml
VERSION=$(grep "^version" Cargo.toml | head -1 | cut -d'"' -f2)
echo -e "${BLUE}ℹ${NC} Project version: ${VERSION}"

# Get current git commit
COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
echo -e "${BLUE}ℹ${NC} Git commit: ${COMMIT}"

# Check if on a branch or tag
BRANCH=$(git branch --show-current 2>/dev/null || echo "")
TAG=$(git describe --tags --exact-match 2>/dev/null || echo "")

if [ ! -z "$TAG" ]; then
    DOCKER_TAG=$TAG
elif [ ! -z "$BRANCH" ]; then
    # Sanitize branch name for Docker tag
    DOCKER_TAG=$(echo $BRANCH | sed 's/[^a-zA-Z0-9._-]/-/g')
else
    DOCKER_TAG="latest"
fi

echo -e "${BLUE}ℹ${NC} Docker tag: ${DOCKER_TAG}"
echo ""

# Step 1: Build the Docker image
echo "📦 Building Docker image..."
echo -e "${YELLOW}Running: docker build -t ${FULL_IMAGE}:${DOCKER_TAG} .${NC}"
echo ""

if docker build \
    --build-arg VERSION=${VERSION} \
    --build-arg COMMIT=${COMMIT} \
    --build-arg BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) \
    -t ${FULL_IMAGE}:${DOCKER_TAG} \
    -t ${FULL_IMAGE}:latest \
    .; then
    echo -e "${GREEN}✓${NC} Docker image built successfully"
else
    echo -e "${RED}❌ Failed to build Docker image${NC}"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 2: Login to GitHub Container Registry
echo "🔐 Logging in to GitHub Container Registry..."
echo ""
echo "You need a GitHub Personal Access Token (PAT) with 'write:packages' scope."
echo ""
echo "To create one:"
echo "1. Go to: https://github.com/settings/tokens/new"
echo "2. Select scopes: 'write:packages' and 'delete:packages' (if needed)"
echo "3. Copy the token"
echo ""

# Check if GITHUB_TOKEN is already set
if [ -z "$GITHUB_TOKEN" ]; then
    read -p "Enter your GitHub username: " GITHUB_USERNAME
    read -s -p "Enter your GitHub Personal Access Token: " GITHUB_TOKEN
    echo ""
else
    # Try to get username from git config
    GITHUB_USERNAME=$(git config --global user.name || echo "")
    if [ -z "$GITHUB_USERNAME" ]; then
        read -p "Enter your GitHub username: " GITHUB_USERNAME
    fi
fi

echo ""
echo "Logging in as ${GITHUB_USERNAME}..."

if echo $GITHUB_TOKEN | docker login ${REGISTRY} -u ${GITHUB_USERNAME} --password-stdin; then
    echo -e "${GREEN}✓${NC} Successfully logged in to ${REGISTRY}"
else
    echo -e "${RED}❌ Failed to login to GitHub Container Registry${NC}"
    echo "Make sure your token has 'write:packages' permission"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 3: Push the image
echo "🚀 Pushing Docker image to registry..."
echo -e "${YELLOW}Pushing: ${FULL_IMAGE}:${DOCKER_TAG}${NC}"
echo ""

if docker push ${FULL_IMAGE}:${DOCKER_TAG}; then
    echo -e "${GREEN}✓${NC} Successfully pushed ${FULL_IMAGE}:${DOCKER_TAG}"
else
    echo -e "${RED}❌ Failed to push Docker image${NC}"
    exit 1
fi

# Also push latest tag
if [ "$DOCKER_TAG" != "latest" ]; then
    echo ""
    echo -e "${YELLOW}Pushing: ${FULL_IMAGE}:latest${NC}"
    if docker push ${FULL_IMAGE}:latest; then
        echo -e "${GREEN}✓${NC} Successfully pushed ${FULL_IMAGE}:latest"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 4: Show results
echo "✨ Success! Your Docker image is now available at:"
echo ""
echo -e "${GREEN}${FULL_IMAGE}:${DOCKER_TAG}${NC}"
echo -e "${GREEN}${FULL_IMAGE}:latest${NC}"
echo ""
echo "📋 To use this image:"
echo ""
echo "Pull the image:"
echo -e "${BLUE}docker pull ${FULL_IMAGE}:${DOCKER_TAG}${NC}"
echo ""
echo "Run the container:"
echo -e "${BLUE}docker run -p 8080:8080 ${FULL_IMAGE}:${DOCKER_TAG}${NC}"
echo ""
echo "🔗 View your package at:"
echo -e "${BLUE}https://github.com/microrapids/api-runtime/pkgs/container/api-runtime${NC}"
echo ""
echo "📝 Make the package public (if needed):"
echo "1. Go to the package URL above"
echo "2. Click 'Package settings'"
echo "3. Scroll to 'Danger Zone'"
echo "4. Click 'Change visibility' → Make public"
echo ""
echo "Done! 🎉"