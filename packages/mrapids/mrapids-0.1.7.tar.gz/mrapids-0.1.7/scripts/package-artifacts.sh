#!/bin/bash

# Package MicroRapid artifacts for distribution

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DIST_DIR="$PROJECT_ROOT/dist"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create dist directory
mkdir -p "$DIST_DIR"

# Package function
package_platform() {
    local platform=$1
    local target=$2
    local ext=$3
    
    log_info "Packaging $platform..."
    
    local binary_dir="$PROJECT_ROOT/target/$target/release"
    
    # Check if binaries exist
    if [[ "$ext" == "zip" ]]; then
        # Windows
        if [[ -f "$binary_dir/mrapids.exe" ]] && [[ -f "$binary_dir/mrapids-agent.exe" ]]; then
            cd "$binary_dir"
            zip "$DIST_DIR/microrapid-$platform.zip" mrapids.exe mrapids-agent.exe
            cd - > /dev/null
            log_success "Created microrapid-$platform.zip"
        else
            log_error "Windows binaries not found in $binary_dir"
        fi
    else
        # Unix-like
        if [[ -f "$binary_dir/mrapids" ]] && [[ -f "$binary_dir/mrapids-agent" ]]; then
            tar -czf "$DIST_DIR/microrapid-$platform.tar.gz" \
                -C "$binary_dir" \
                mrapids mrapids-agent
            log_success "Created microrapid-$platform.tar.gz"
        else
            log_error "Binaries not found in $binary_dir"
        fi
    fi
}

# Main packaging
main() {
    echo -e "${BLUE}📦 MicroRapid Artifact Packaging${NC}"
    echo "=================================="
    
    # Check current platform binaries (always exist)
    local current_platform=""
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if [[ $(uname -m) == "arm64" ]]; then
            current_platform="darwin-arm64"
        else
            current_platform="darwin-x64"
        fi
        package_platform "$current_platform" "release" "tar.gz"
    elif [[ "$OSTYPE" == "linux"* ]]; then
        current_platform="linux-x64"
        package_platform "$current_platform" "release" "tar.gz"
    fi
    
    # Package cross-compiled targets if they exist
    log_info "Checking for cross-compiled targets..."
    
    # Linux x64
    if [[ -d "$PROJECT_ROOT/target/x86_64-unknown-linux-gnu" ]]; then
        package_platform "linux-x64" "x86_64-unknown-linux-gnu" "tar.gz"
    fi
    
    # macOS x64
    if [[ -d "$PROJECT_ROOT/target/x86_64-apple-darwin" ]]; then
        package_platform "darwin-x64" "x86_64-apple-darwin" "tar.gz"
    fi
    
    # macOS ARM64
    if [[ -d "$PROJECT_ROOT/target/aarch64-apple-darwin" ]]; then
        package_platform "darwin-arm64" "aarch64-apple-darwin" "tar.gz"
    fi
    
    # Windows x64
    if [[ -d "$PROJECT_ROOT/target/x86_64-pc-windows-msvc" ]]; then
        package_platform "win32-x64" "x86_64-pc-windows-msvc" "zip"
    fi
    
    # Generate checksums
    if ls "$DIST_DIR"/*.tar.gz 1> /dev/null 2>&1 || ls "$DIST_DIR"/*.zip 1> /dev/null 2>&1; then
        log_info "Generating checksums..."
        cd "$DIST_DIR"
        shasum -a 256 *.tar.gz *.zip 2>/dev/null > checksums.sha256 || true
        cd - > /dev/null
        log_success "Generated checksums.sha256"
        
        echo -e "\n${GREEN}📋 Checksums:${NC}"
        cat "$DIST_DIR/checksums.sha256"
    fi
    
    # Summary
    echo -e "\n${BLUE}📦 Artifacts created in: $DIST_DIR${NC}"
    ls -lh "$DIST_DIR"
    
    # Next steps
    echo -e "\n${YELLOW}📌 Next steps:${NC}"
    echo "1. Update SHA256 hashes in homebrew/microrapid.rb"
    echo "2. Update SHA256 hash in scoop/microrapid.json"
    echo "3. Create GitHub release and upload artifacts"
    echo "4. Run ./scripts/publish-packages.sh to publish"
}

main "$@"