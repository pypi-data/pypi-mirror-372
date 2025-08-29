#!/bin/bash
# Quick release script for local testing

set -e

VERSION=${1:-0.1.0}

echo "🚀 Building MicroRapid v${VERSION} for current platform..."

# Detect current platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
    darwin)
        PLATFORM="darwin"
        ;;
    linux)
        PLATFORM="linux"
        ;;
    mingw*|msys*|cygwin*)
        PLATFORM="windows"
        ;;
    *)
        echo "Unsupported OS: $OS"
        exit 1
        ;;
esac

case "$ARCH" in
    x86_64|amd64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

SUFFIX="${PLATFORM}-${ARCH}"

# Build in release mode
echo "Building for ${SUFFIX}..."
cargo build --release
cd agent && cargo build --release && cd ..

# Create release directory
mkdir -p release/v${VERSION}

# Copy binaries
if [[ "$PLATFORM" == "windows" ]]; then
    cp target/release/mrapids.exe release/v${VERSION}/
    cp target/release/mrapids-agent.exe release/v${VERSION}/
    
    # Create zip
    cd release/v${VERSION}
    zip mrapids-${VERSION}-${SUFFIX}.zip mrapids.exe mrapids-agent.exe
else
    cp target/release/mrapids release/v${VERSION}/
    cp target/release/mrapids-agent release/v${VERSION}/
    
    # Create tar.gz
    cd release/v${VERSION}
    tar czf mrapids-${VERSION}-${SUFFIX}.tar.gz mrapids mrapids-agent
fi

# Generate checksum
if command -v shasum &> /dev/null; then
    shasum -a 256 mrapids-${VERSION}-${SUFFIX}.* > checksums.txt
elif command -v sha256sum &> /dev/null; then
    sha256sum mrapids-${VERSION}-${SUFFIX}.* > checksums.txt
fi

cd ../..

echo "✅ Build complete!"
echo "📦 Artifacts in: release/v${VERSION}/"
ls -la release/v${VERSION}/

# Test the binaries
echo -e "\n📋 Testing binaries..."
./release/v${VERSION}/mrapids --version
./release/v${VERSION}/mrapids-agent --version

echo -e "\n🎉 Ready for distribution!"