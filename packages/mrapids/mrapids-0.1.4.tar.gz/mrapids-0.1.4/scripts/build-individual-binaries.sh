#!/bin/bash
# Build and package individual binaries for modular installation

set -e

VERSION=${1:-0.1.0}
PLATFORMS=(
    "darwin-amd64:x86_64-apple-darwin"
    "darwin-arm64:aarch64-apple-darwin"
    "linux-amd64:x86_64-unknown-linux-gnu"
    "linux-arm64:aarch64-unknown-linux-gnu"
    "windows-amd64:x86_64-pc-windows-gnu"
)

echo "🚀 Building MicroRapid v${VERSION} - Individual Binaries"
echo "=================================================="

# Create release directories
mkdir -p release/v${VERSION}/{cli,agent,suite}

for platform_pair in "${PLATFORMS[@]}"; do
    IFS=':' read -r platform rust_target <<< "$platform_pair"
    
    echo -e "\n📦 Building for ${platform}..."
    
    # Add target if needed
    rustup target add ${rust_target} 2>/dev/null || true
    
    # Build both binaries
    echo "  Building mrapids..."
    cargo build --release --target ${rust_target}
    
    echo "  Building mrapids-agent..."
    cd agent
    cargo build --release --target ${rust_target}
    cd ..
    
    # Determine binary extension
    if [[ "$platform" == *"windows"* ]]; then
        EXT=".exe"
        ARCHIVE_EXT=".zip"
    else
        EXT=""
        ARCHIVE_EXT=".tar.gz"
    fi
    
    # Package CLI only
    echo "  📦 Packaging CLI..."
    cp target/${rust_target}/release/mrapids${EXT} release/v${VERSION}/cli/
    cd release/v${VERSION}/cli
    if [[ "$ARCHIVE_EXT" == ".zip" ]]; then
        zip mrapids-${VERSION}-${platform}.zip mrapids${EXT}
        # Include a small README
        echo "MicroRapid CLI - API Testing Tool" > README.txt
        zip -u mrapids-${VERSION}-${platform}.zip README.txt
        rm README.txt
    else
        tar czf mrapids-${VERSION}-${platform}.tar.gz mrapids${EXT}
    fi
    rm mrapids${EXT}
    cd ../../..
    
    # Package Agent only
    echo "  📦 Packaging Agent..."
    cp target/${rust_target}/release/mrapids-agent${EXT} release/v${VERSION}/agent/
    cd release/v${VERSION}/agent
    if [[ "$ARCHIVE_EXT" == ".zip" ]]; then
        zip mrapids-agent-${VERSION}-${platform}.zip mrapids-agent${EXT}
        echo "MicroRapid Agent - MCP Server for AI Agents" > README.txt
        zip -u mrapids-agent-${VERSION}-${platform}.zip README.txt
        rm README.txt
    else
        tar czf mrapids-agent-${VERSION}-${platform}.tar.gz mrapids-agent${EXT}
    fi
    rm mrapids-agent${EXT}
    cd ../../..
    
    # Package Suite (both)
    echo "  📦 Packaging Suite..."
    cp target/${rust_target}/release/mrapids${EXT} release/v${VERSION}/suite/
    cp target/${rust_target}/release/mrapids-agent${EXT} release/v${VERSION}/suite/
    cd release/v${VERSION}/suite
    if [[ "$ARCHIVE_EXT" == ".zip" ]]; then
        zip mrapids-suite-${VERSION}-${platform}.zip mrapids${EXT} mrapids-agent${EXT}
        echo "MicroRapid Suite - Complete Toolkit" > README.txt
        zip -u mrapids-suite-${VERSION}-${platform}.zip README.txt
        rm README.txt
    else
        tar czf mrapids-suite-${VERSION}-${platform}.tar.gz mrapids${EXT} mrapids-agent${EXT}
    fi
    rm mrapids${EXT} mrapids-agent${EXT}
    cd ../../..
done

# Generate checksums
echo -e "\n🔐 Generating checksums..."
cd release/v${VERSION}
for dir in cli agent suite; do
    cd $dir
    if command -v shasum &> /dev/null; then
        shasum -a 256 * > checksums.txt
    else
        sha256sum * > checksums.txt
    fi
    cd ..
done
cd ../..

# Create release summary
cat > release/v${VERSION}/RELEASE_NOTES.md << EOF
# MicroRapid v${VERSION} - Modular Release

## Installation Options

### 1. CLI Only (mrapids)
- For API testing and automation
- Lightweight option for developers
- Download from \`cli/\` directory

### 2. Agent Only (mrapids-agent)  
- MCP server for AI agents
- For AI/LLM integration
- Download from \`agent/\` directory

### 3. Complete Suite
- Both CLI and Agent
- Full toolkit
- Download from \`suite/\` directory

## File Sizes

| Component | macOS | Linux | Windows |
|-----------|-------|-------|---------|
| CLI Only | ~7MB | ~8MB | ~7MB |
| Agent Only | ~6MB | ~7MB | ~6MB |
| Suite | ~13MB | ~15MB | ~13MB |

## Installation

Choose the package that matches your needs:
- **CLI only**: API developers, testers
- **Agent only**: AI developers, MCP users
- **Suite**: Full platform users
EOF

echo -e "\n✅ Build complete!"
echo "📁 Release structure:"
tree -L 3 release/v${VERSION}/ 2>/dev/null || ls -la release/v${VERSION}/*/

echo -e "\n📊 Package sizes:"
du -sh release/v${VERSION}/cli/* | grep -E "\.(tar\.gz|zip)$"
du -sh release/v${VERSION}/agent/* | grep -E "\.(tar\.gz|zip)$"
du -sh release/v${VERSION}/suite/* | grep -E "\.(tar\.gz|zip)$"