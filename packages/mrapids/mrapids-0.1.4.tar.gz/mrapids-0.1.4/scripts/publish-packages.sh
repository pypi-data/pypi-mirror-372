#!/bin/bash

# MicroRapid Package Publishing Script
# Publish to all package managers

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_stage() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Publish to crates.io
publish_cargo() {
    log_stage "PUBLISHING TO CRATES.IO"
    
    echo "Publishing mrapids..."
    cargo publish --dry-run
    
    read -p "Publish to crates.io? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cargo publish
        log_success "Published to crates.io"
    else
        echo "Skipped crates.io publishing"
    fi
}

# Publish to npm
publish_npm() {
    log_stage "PUBLISHING TO NPM"
    
    cd "$PROJECT_ROOT/npm"
    
    echo "Current version: $(node -p "require('./package.json').version")"
    
    # Check if logged in
    if ! npm whoami &> /dev/null; then
        log_error "Not logged in to npm. Run: npm login"
        return 1
    fi
    
    # Dry run
    npm publish --dry-run
    
    read -p "Publish to npm? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        npm publish --access public
        log_success "Published to npm"
    else
        echo "Skipped npm publishing"
    fi
    
    cd ..
}

# Publish to PyPI
publish_pypi() {
    log_stage "PUBLISHING TO PYPI"
    
    cd "$PROJECT_ROOT/python"
    
    # Check for twine
    if ! command -v twine &> /dev/null; then
        log_error "twine not installed. Install with: pip install twine"
        return 1
    fi
    
    # Build distribution
    python3 setup.py sdist bdist_wheel
    
    # Check package
    twine check dist/*
    
    read -p "Upload to PyPI? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        twine upload dist/*
        log_success "Published to PyPI"
    else
        echo "Skipped PyPI publishing"
    fi
    
    cd ..
}

# Submit to Homebrew
submit_homebrew() {
    log_stage "SUBMITTING TO HOMEBREW"
    
    echo "To submit to Homebrew:"
    echo "1. Fork homebrew-core repository"
    echo "2. Copy formula: cp homebrew/microrapid.rb /path/to/homebrew-core/Formula/"
    echo "3. Update SHA256 hashes in the formula"
    echo "4. Test locally: brew install --build-from-source microrapid"
    echo "5. Submit PR to homebrew-core"
    
    echo -e "\n${YELLOW}Manual step required${NC}"
}

# Submit to Scoop
submit_scoop() {
    log_stage "SUBMITTING TO SCOOP"
    
    echo "To submit to Scoop:"
    echo "1. Fork scoop-extras bucket"
    echo "2. Copy manifest: cp scoop/microrapid.json /path/to/scoop-extras/bucket/"
    echo "3. Update SHA256 hash in the manifest"
    echo "4. Test locally: scoop install microrapid.json"
    echo "5. Submit PR to scoop-extras"
    
    echo -e "\n${YELLOW}Manual step required${NC}"
}

# Main
main() {
    echo -e "${BLUE}🚀 MicroRapid Package Publishing${NC}"
    echo "=================================="
    
    cd "$PROJECT_ROOT"
    
    # Check for release build
    if [ ! -f "target/release/mrapids" ]; then
        log_error "No release build found. Run: cargo build --release"
        exit 1
    fi
    
    PS3="Select package manager to publish to: "
    options=("Cargo (crates.io)" "NPM" "PyPI" "Homebrew (instructions)" "Scoop (instructions)" "All" "Quit")
    
    select opt in "${options[@]}"
    do
        case $opt in
            "Cargo (crates.io)")
                publish_cargo
                ;;
            "NPM")
                publish_npm
                ;;
            "PyPI")
                publish_pypi
                ;;
            "Homebrew (instructions)")
                submit_homebrew
                ;;
            "Scoop (instructions)")
                submit_scoop
                ;;
            "All")
                publish_cargo
                publish_npm
                publish_pypi
                submit_homebrew
                submit_scoop
                break
                ;;
            "Quit")
                break
                ;;
            *) echo "Invalid option";;
        esac
    done
    
    log_success "Publishing workflow complete!"
}

main "$@"