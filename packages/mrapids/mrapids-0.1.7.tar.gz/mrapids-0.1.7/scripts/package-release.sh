#!/bin/bash
# Package release artifacts with security checks

set -e

TARGET=$1
SUFFIX=$2
VERSION=${GITHUB_REF_NAME:-v0.1.0}

echo "📦 Packaging release for $TARGET ($SUFFIX)"

# Create release directories
mkdir -p release/{cli,agent,suite}

# Determine binary extension
if [[ "$TARGET" == *"windows"* ]]; then
    EXT=".exe"
else
    EXT=""
fi

# Copy binaries
cp target/$TARGET/release/mrapids$EXT release/cli/
cp target/$TARGET/release/mrapids-agent$EXT release/agent/
cp target/$TARGET/release/mrapids$EXT release/suite/
cp target/$TARGET/release/mrapids-agent$EXT release/suite/

# Generate checksums for each binary
cd release

for dir in cli agent suite; do
    cd $dir
    
    # Generate SHA256
    if command -v sha256sum &> /dev/null; then
        sha256sum * > SHA256SUMS
    else
        shasum -a 256 * > SHA256SUMS
    fi
    
    # Generate SHA512 for extra security
    if command -v sha512sum &> /dev/null; then
        sha512sum * > SHA512SUMS
    else
        shasum -a 512 * > SHA512SUMS
    fi
    
    # Create archives
    if [[ "$SUFFIX" == *"windows"* ]]; then
        # Windows ZIP
        if [ "$dir" == "cli" ]; then
            zip mrapids-$VERSION-$SUFFIX.zip mrapids$EXT SHA256SUMS SHA512SUMS
        elif [ "$dir" == "agent" ]; then
            zip mrapids-agent-$VERSION-$SUFFIX.zip mrapids-agent$EXT SHA256SUMS SHA512SUMS
        else
            zip mrapids-suite-$VERSION-$SUFFIX.zip mrapids$EXT mrapids-agent$EXT SHA256SUMS SHA512SUMS
        fi
    else
        # Unix TAR.GZ
        if [ "$dir" == "cli" ]; then
            tar czf mrapids-$VERSION-$SUFFIX.tar.gz mrapids$EXT SHA256SUMS SHA512SUMS
        elif [ "$dir" == "agent" ]; then
            tar czf mrapids-agent-$VERSION-$SUFFIX.tar.gz mrapids-agent$EXT SHA256SUMS SHA512SUMS
        else
            tar czf mrapids-suite-$VERSION-$SUFFIX.tar.gz mrapids$EXT mrapids-agent$EXT SHA256SUMS SHA512SUMS
        fi
    fi
    
    # Clean up raw binaries
    rm -f mrapids$EXT mrapids-agent$EXT
    
    cd ..
done

# Generate master checksum file
find . -name "*.tar.gz" -o -name "*.zip" | xargs sha256sum > CHECKSUMS.txt

echo "✅ Packaging complete for $SUFFIX"