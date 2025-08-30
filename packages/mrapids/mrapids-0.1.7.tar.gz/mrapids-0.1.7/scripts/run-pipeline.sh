#!/bin/bash

# MicroRapid Manual CI/CD Pipeline Script
# Run all pipeline stages manually

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_stage() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Stage 1: Build Check
stage_build() {
    log_stage "STAGE 1: BUILD CHECK"
    
    echo "Running cargo check..."
    if cargo check --all-targets; then
        log_success "Build check passed"
        return 0
    else
        log_error "Build check failed"
        return 1
    fi
}

# Stage 2: Security Scans
stage_security() {
    log_stage "STAGE 2: SECURITY SCANS"
    
    # Check for cargo-audit
    if command -v cargo-audit &> /dev/null; then
        echo "Running cargo audit..."
        cargo audit || log_warning "Some vulnerabilities found"
    else
        log_warning "cargo-audit not installed. Install with: cargo install cargo-audit"
    fi
    
    # Check for semgrep
    if command -v semgrep &> /dev/null; then
        echo "Running semgrep..."
        semgrep --config=.semgrep.yml --json --output=semgrep-results.json . || log_warning "Semgrep found issues"
    else
        log_warning "semgrep not installed. Install from: https://semgrep.dev/"
    fi
    
    # Basic security checks
    echo "Checking for hardcoded secrets..."
    if grep -r "password\|secret\|key\|token" src/ --include="*.rs" | grep -v "// " | grep -E "(=|:)\s*\"" | grep -v "format"; then
        log_warning "Potential hardcoded secrets found"
    else
        log_success "No hardcoded secrets detected"
    fi
    
    echo "Checking for unsafe code..."
    UNSAFE_COUNT=$(grep -r "unsafe" src/ --include="*.rs" | wc -l)
    if [ "$UNSAFE_COUNT" -gt 0 ]; then
        log_warning "Found $UNSAFE_COUNT unsafe blocks"
    else
        log_success "No unsafe code found"
    fi
}

# Stage 3: Run Tests
stage_tests() {
    log_stage "STAGE 3: RUN TESTS"
    
    echo "Running all tests..."
    if cargo test --all; then
        log_success "All tests passed"
        return 0
    else
        log_warning "Some tests failed"
        return 1
    fi
}

# Stage 4: Build Release Binaries
stage_release() {
    log_stage "STAGE 4: BUILD RELEASE BINARIES"
    
    mkdir -p "$BUILD_DIR"
    
    # Build for current platform
    echo "Building release binaries..."
    if cargo build --release --all; then
        log_success "Release build successful"
        
        # Copy binaries
        cp target/release/mrapids "$BUILD_DIR/"
        cp target/release/mrapids-agent "$BUILD_DIR/"
        
        # Check sizes
        echo -e "\nBinary sizes:"
        ls -lh "$BUILD_DIR"/mrapids* | awk '{print $9 ": " $5}'
        
        return 0
    else
        log_error "Release build failed"
        return 1
    fi
}

# Stage 5: Cross-platform builds
stage_cross_build() {
    log_stage "STAGE 5: CROSS-PLATFORM BUILDS"
    
    # Check if cross is installed
    if ! command -v cross &> /dev/null; then
        log_warning "cross not installed. Install with: cargo install cross"
        echo "Skipping cross-platform builds"
        return 0
    fi
    
    mkdir -p "$DIST_DIR"
    
    # Define targets
    TARGETS=(
        "x86_64-unknown-linux-gnu"
        "x86_64-apple-darwin"
        "aarch64-apple-darwin"
        "x86_64-pc-windows-msvc"
    )
    
    for target in "${TARGETS[@]}"; do
        echo "Building for $target..."
        if cross build --release --target "$target"; then
            log_success "Built for $target"
            
            # Package binaries
            case "$target" in
                *windows*)
                    ext=".exe"
                    archive="microrapid-${target}.zip"
                    ;;
                *)
                    ext=""
                    archive="microrapid-${target}.tar.gz"
                    ;;
            esac
            
            # Create archive (simplified - in real pipeline would create proper archives)
            echo "Would create: $DIST_DIR/$archive"
        else
            log_warning "Failed to build for $target"
        fi
    done
}

# Stage 6: Package for Distribution
stage_package() {
    log_stage "STAGE 6: PACKAGE FOR DISTRIBUTION"
    
    mkdir -p "$DIST_DIR"/{npm,python,homebrew,scoop}
    
    # NPM Package
    echo "Preparing npm package..."
    if [ -d "npm" ]; then
        cp -r npm/* "$DIST_DIR/npm/"
        log_success "NPM package prepared"
    fi
    
    # Python Package
    echo "Preparing Python package..."
    if [ -d "python" ] && command -v python3 &> /dev/null; then
        cd python
        python3 setup.py sdist bdist_wheel
        cp dist/* "$DIST_DIR/python/"
        cd ..
        log_success "Python package prepared"
    else
        log_warning "Python packaging skipped"
    fi
    
    # Update Homebrew formula
    echo "Updating Homebrew formula..."
    if [ -f "homebrew/microrapid.rb" ]; then
        cp homebrew/microrapid.rb "$DIST_DIR/homebrew/"
        log_success "Homebrew formula copied"
    fi
    
    # Update Scoop manifest
    echo "Updating Scoop manifest..."
    if [ -f "scoop/microrapid.json" ]; then
        cp scoop/microrapid.json "$DIST_DIR/scoop/"
        log_success "Scoop manifest copied"
    fi
}

# Stage 7: Generate SBOM
stage_sbom() {
    log_stage "STAGE 7: GENERATE SBOM"
    
    # Check for cargo-cyclonedx
    if command -v cargo-cyclonedx &> /dev/null; then
        echo "Generating CycloneDX SBOM..."
        cargo cyclonedx --format json --output "$DIST_DIR/microrapid-sbom.json"
        log_success "SBOM generated"
    else
        log_warning "cargo-cyclonedx not installed. Install with: cargo install cargo-cyclonedx"
        
        # Fallback to basic dependency list
        echo "Generating basic dependency list..."
        cargo tree > "$DIST_DIR/dependencies.txt"
        log_success "Dependency list generated"
    fi
}

# Main pipeline execution
main() {
    echo -e "${BLUE}🚀 MicroRapid Manual CI/CD Pipeline${NC}"
    echo "================================================"
    
    cd "$PROJECT_ROOT"
    
    # Track overall status
    PIPELINE_STATUS=0
    
    # Run stages
    if stage_build; then
        stage_security  # Security is non-blocking
        
        if stage_tests; then
            :  # Tests passed
        else
            PIPELINE_STATUS=1
            log_warning "Tests failed but continuing..."
        fi
        
        if stage_release; then
            stage_cross_build  # Optional
            stage_package
            stage_sbom
        else
            PIPELINE_STATUS=1
            log_error "Release build failed"
        fi
    else
        PIPELINE_STATUS=1
        log_error "Build check failed - stopping pipeline"
    fi
    
    # Summary
    echo -e "\n${BLUE}=== PIPELINE SUMMARY ===${NC}"
    if [ $PIPELINE_STATUS -eq 0 ]; then
        log_success "Pipeline completed successfully!"
        echo -e "\nArtifacts available in:"
        echo "  - Binaries: $BUILD_DIR"
        echo "  - Packages: $DIST_DIR"
    else
        log_warning "Pipeline completed with warnings"
    fi
    
    return $PIPELINE_STATUS
}

# Run pipeline
main "$@"