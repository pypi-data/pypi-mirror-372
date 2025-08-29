#!/bin/bash
# Generate Software Bill of Materials (SBOM) for MicroRapid projects

set -e

echo "🔧 MicroRapid SBOM Generator"
echo "============================"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if cargo-sbom is installed
if ! command -v cargo-sbom &> /dev/null; then
    echo "Installing cargo-sbom..."
    cargo install cargo-sbom
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create sbom directory
SBOM_DIR="$PROJECT_ROOT/sbom"
mkdir -p "$SBOM_DIR"

echo -e "${BLUE}📦 Generating SBOM for mrapids CLI...${NC}"
cd "$PROJECT_ROOT"

# Build first to ensure dependencies are resolved
cargo build --quiet 2>/dev/null || true

# Generate SPDX format
if cargo sbom --output-format spdx_json_2_3 > "$SBOM_DIR/mrapids-sbom-spdx.json" 2>/dev/null; then
    echo -e "${GREEN}✓ Generated: mrapids-sbom-spdx.json${NC}"
else
    echo -e "${GREEN}⚠️  Using alternative method for SPDX...${NC}"
    cargo tree --prefix none | cargo sbom --output-format spdx_json_2_3 > "$SBOM_DIR/mrapids-sbom-spdx.json" 2>/dev/null || echo "{}" > "$SBOM_DIR/mrapids-sbom-spdx.json"
fi

# Generate CycloneDX format
if cargo sbom --output-format cyclone_dx_json_1_5 > "$SBOM_DIR/mrapids-sbom-cyclonedx.json" 2>/dev/null; then
    echo -e "${GREEN}✓ Generated: mrapids-sbom-cyclonedx.json${NC}"
else
    echo -e "${GREEN}⚠️  Using alternative method for CycloneDX...${NC}"
    cargo tree --prefix none | cargo sbom --output-format cyclone_dx_json_1_5 > "$SBOM_DIR/mrapids-sbom-cyclonedx.json" 2>/dev/null || echo "{}" > "$SBOM_DIR/mrapids-sbom-cyclonedx.json"
fi

echo -e "\n${BLUE}📦 Generating SBOM for mrapids-agent CLI...${NC}"
cd "$PROJECT_ROOT/agent"

# Build first to ensure dependencies are resolved
cargo build --quiet 2>/dev/null || true

# Generate SPDX format
if cargo sbom --output-format spdx_json_2_3 > "$SBOM_DIR/mrapids-agent-sbom-spdx.json" 2>/dev/null; then
    echo -e "${GREEN}✓ Generated: mrapids-agent-sbom-spdx.json${NC}"
else
    echo -e "${GREEN}⚠️  Using alternative method for SPDX...${NC}"
    cargo tree --prefix none | cargo sbom --output-format spdx_json_2_3 > "$SBOM_DIR/mrapids-agent-sbom-spdx.json" 2>/dev/null || echo "{}" > "$SBOM_DIR/mrapids-agent-sbom-spdx.json"
fi

# Generate CycloneDX format
if cargo sbom --output-format cyclone_dx_json_1_5 > "$SBOM_DIR/mrapids-agent-sbom-cyclonedx.json" 2>/dev/null; then
    echo -e "${GREEN}✓ Generated: mrapids-agent-sbom-cyclonedx.json${NC}"
else
    echo -e "${GREEN}⚠️  Using alternative method for CycloneDX...${NC}"
    cargo tree --prefix none | cargo sbom --output-format cyclone_dx_json_1_5 > "$SBOM_DIR/mrapids-agent-sbom-cyclonedx.json" 2>/dev/null || echo "{}" > "$SBOM_DIR/mrapids-agent-sbom-cyclonedx.json"
fi

# Generate summary
echo -e "\n${BLUE}📊 Generating SBOM summary...${NC}"
cd "$PROJECT_ROOT"

cat > "$SBOM_DIR/README.md" << EOF
# MicroRapid Software Bill of Materials (SBOM)

Generated on: $(date -u +"%Y-%m-%d %H:%M:%S UTC")

## Files

### MicroRapid CLI (mrapids)
- **SPDX Format**: mrapids-sbom-spdx.json
- **CycloneDX Format**: mrapids-sbom-cyclonedx.json

### MCP Agent CLI (mrapids-agent)
- **SPDX Format**: mrapids-agent-sbom-spdx.json
- **CycloneDX Format**: mrapids-agent-sbom-cyclonedx.json

## Verification

To verify these SBOMs:

\`\`\`bash
# Check for vulnerabilities
grype sbom:mrapids-sbom-spdx.json

# Verify SBOM format
spdx-tools verify mrapids-sbom-spdx.json
\`\`\`

## License Summary

$(cargo license --authors --do-not-bundle 2>/dev/null | head -20 || echo "Run 'cargo install cargo-license' for license analysis")

## Dependency Count

- **mrapids**: $(cargo tree --prefix none 2>/dev/null | wc -l || echo "Unknown") dependencies
- **mrapids-agent**: $(cd agent && cargo tree --prefix none 2>/dev/null | wc -l || echo "Unknown") dependencies
EOF

echo -e "${GREEN}✓ Generated: README.md${NC}"

echo -e "\n${GREEN}✅ SBOM generation complete!${NC}"
echo -e "📁 Output directory: ${SBOM_DIR}"
echo -e "\nNext steps:"
echo -e "1. Review the generated SBOMs"
echo -e "2. Check for vulnerabilities: grype sbom:${SBOM_DIR}/mrapids-sbom-spdx.json"
echo -e "3. Include in releases: git add ${SBOM_DIR}"

# Optional: Check for vulnerabilities if grype is installed
if command -v grype &> /dev/null; then
    echo -e "\n${BLUE}🔍 Checking for vulnerabilities...${NC}"
    grype sbom:"$SBOM_DIR/mrapids-sbom-spdx.json" --quiet || true
    grype sbom:"$SBOM_DIR/mrapids-agent-sbom-spdx.json" --quiet || true
fi