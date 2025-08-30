#!/bin/bash
# Alternative SBOM generation using cargo-cyclonedx

set -e

echo "🔧 MicroRapid SBOM Generator (cargo-cyclonedx)"
echo "============================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if cargo-cyclonedx is installed
if ! command -v cargo-cyclonedx &> /dev/null; then
    echo -e "${YELLOW}Installing cargo-cyclonedx...${NC}"
    cargo install cargo-cyclonedx
fi

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Create sbom directory
SBOM_DIR="$PROJECT_ROOT/sbom"
mkdir -p "$SBOM_DIR"

echo -e "${BLUE}📦 Generating SBOM for mrapids CLI...${NC}"
cd "$PROJECT_ROOT"

# Generate CycloneDX SBOM
if cargo cyclonedx --format json; then
    # Move generated file to our desired location
    if [ -f "mrapids.cdx.json" ]; then
        mv "mrapids.cdx.json" "$SBOM_DIR/mrapids-sbom-cyclonedx.json"
        echo -e "${GREEN}✓ Generated: mrapids-sbom-cyclonedx.json${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to find generated SBOM for mrapids${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Failed to generate SBOM for mrapids${NC}"
fi

echo -e "\n${BLUE}📦 Generating SBOM for mrapids-agent CLI...${NC}"
cd "$PROJECT_ROOT/agent"

# Generate CycloneDX SBOM
if cargo cyclonedx --format json; then
    # Move generated file to our desired location
    if [ -f "mrapids-agent.cdx.json" ]; then
        mv "mrapids-agent.cdx.json" "$SBOM_DIR/mrapids-agent-sbom-cyclonedx.json"
        echo -e "${GREEN}✓ Generated: mrapids-agent-sbom-cyclonedx.json${NC}"
    else
        echo -e "${YELLOW}⚠️  Failed to find generated SBOM for mrapids-agent${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Failed to generate SBOM for mrapids-agent${NC}"
fi

# Generate summary
echo -e "\n${BLUE}📊 Generating SBOM summary...${NC}"
cd "$PROJECT_ROOT"

# Count dependencies using cargo tree
MRAPIDS_DEPS=$(cargo tree --prefix none 2>/dev/null | grep -v "^\[" | sort -u | wc -l || echo "0")
AGENT_DEPS=$(cd agent && cargo tree --prefix none 2>/dev/null | grep -v "^\[" | sort -u | wc -l || echo "0")

cat > "$SBOM_DIR/README.md" << EOF
# MicroRapid Software Bill of Materials (SBOM)

Generated on: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
Tool: cargo-cyclonedx

## Files

### MicroRapid CLI (mrapids)
- **CycloneDX Format**: mrapids-sbom-cyclonedx.json
- **Dependencies**: $MRAPIDS_DEPS unique crates

### MCP Agent CLI (mrapids-agent)
- **CycloneDX Format**: mrapids-agent-sbom-cyclonedx.json
- **Dependencies**: $AGENT_DEPS unique crates

## Verification

To verify these SBOMs:

\`\`\`bash
# Validate CycloneDX format
cyclonedx-cli validate --input-file mrapids-sbom-cyclonedx.json

# Check for vulnerabilities
grype sbom:mrapids-sbom-cyclonedx.json
\`\`\`

## Quick Dependency Summary

### Top dependencies for mrapids:
$(cargo tree --prefix none 2>/dev/null | grep -v "^\[" | sort | uniq -c | sort -rn | head -10 || echo "Run 'cargo tree' for details")

### Top dependencies for mrapids-agent:
$(cd agent && cargo tree --prefix none 2>/dev/null | grep -v "^\[" | sort | uniq -c | sort -rn | head -10 || echo "Run 'cargo tree' for details")
EOF

echo -e "${GREEN}✓ Generated: README.md${NC}"

echo -e "\n${GREEN}✅ SBOM generation complete!${NC}"
echo -e "📁 Output directory: ${SBOM_DIR}"

# Display summary
echo -e "\n${BLUE}Summary:${NC}"
ls -lh "$SBOM_DIR"/*.json 2>/dev/null || echo "No SBOM files generated"

# Optional: Validate if cyclonedx-cli is installed
if command -v cyclonedx-cli &> /dev/null; then
    echo -e "\n${BLUE}🔍 Validating SBOMs...${NC}"
    cyclonedx-cli validate --input-file "$SBOM_DIR/mrapids-sbom-cyclonedx.json" 2>/dev/null && echo -e "${GREEN}✓ mrapids SBOM is valid${NC}" || echo -e "${YELLOW}⚠️  mrapids SBOM validation failed${NC}"
    cyclonedx-cli validate --input-file "$SBOM_DIR/mrapids-agent-sbom-cyclonedx.json" 2>/dev/null && echo -e "${GREEN}✓ mrapids-agent SBOM is valid${NC}" || echo -e "${YELLOW}⚠️  mrapids-agent SBOM validation failed${NC}"
fi