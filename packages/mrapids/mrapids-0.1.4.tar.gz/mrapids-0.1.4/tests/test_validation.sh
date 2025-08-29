#!/bin/bash

# Validation Test Cases - OpenAPI Spec Validation Tests
# Tests all validation levels and error detection

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_DIR="${TEST_DIR:-./test-specs}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test Result Tracking
PASSED=0
FAILED=0

# Setup test specifications
setup_test_specs() {
    mkdir -p "$TEST_DIR"
    
    # Valid OpenAPI 3.0 spec
    cat > "$TEST_DIR/valid.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Valid API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
      responses:
        '200':
          description: Success
EOF

    # Spec with broken references
    cat > "$TEST_DIR/invalid-refs.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Invalid Refs API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/NonExistent'
EOF

    # Spec with duplicate operation IDs
    cat > "$TEST_DIR/duplicate-ids.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Duplicate IDs API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getResource
      responses:
        '200':
          description: Success
  /posts:
    get:
      operationId: getResource
      responses:
        '200':
          description: Success
EOF

    # Spec with type constraint errors
    cat > "$TEST_DIR/type-errors.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Type Errors API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
      responses:
        '200':
          description: Success
components:
  schemas:
    User:
      type: string
      properties:
        name:
          type: string
EOF

    # Spec with warnings (missing descriptions)
    cat > "$TEST_DIR/warnings.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: API with Warnings
  version: 1.0.0
paths:
  /users:
    get:
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
EOF

    # Malformed YAML
    cat > "$TEST_DIR/malformed.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Malformed API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
      responses:
        '200':
          description: Success
          invalid yaml here:::
EOF
}

# Cleanup function
cleanup() {
    rm -rf "$TEST_DIR"
}

# Setup
setup_test_specs
trap cleanup EXIT

echo -e "${YELLOW}🧪 Agent CLI - Validation Test Suite${NC}"
echo "======================================"

# TC-011: Valid Spec Validation
echo -e "\n${BLUE}[TEST]${NC} TC-011: Valid Spec Validation"
if $CLI_PATH validate "$TEST_DIR/valid.yaml" 2>&1 | grep -q "Specification is valid"; then
    echo -e "${GREEN}✅ PASS${NC} - Valid spec passes validation"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Valid spec failed validation"
    ((FAILED++))
fi

# TC-012: Invalid Reference Detection
echo -e "\n${BLUE}[TEST]${NC} TC-012: Invalid Reference Detection"
if $CLI_PATH validate "$TEST_DIR/invalid-refs.yaml" 2>&1 | grep -q "Undefined reference\|NonExistent"; then
    echo -e "${GREEN}✅ PASS${NC} - Invalid references detected"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Failed to detect invalid references"
    ((FAILED++))
fi

# TC-013: Strict Mode Validation
echo -e "\n${BLUE}[TEST]${NC} TC-013: Strict Mode Validation"
if ! $CLI_PATH validate --strict "$TEST_DIR/warnings.yaml" 2>&1 | grep -q "Specification is valid"; then
    echo -e "${GREEN}✅ PASS${NC} - Strict mode treats warnings as errors"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Strict mode didn't catch warnings"
    ((FAILED++))
fi

# TC-014: Lint Mode Validation
echo -e "\n${BLUE}[TEST]${NC} TC-014: Lint Mode Validation"
if $CLI_PATH validate --lint "$TEST_DIR/warnings.yaml" 2>&1 | grep -q "Missing\|warning\|Warning"; then
    echo -e "${GREEN}✅ PASS${NC} - Lint mode detects best practice issues"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Lint mode failed to detect issues"
    ((FAILED++))
fi

# TC-015: JSON Output Format
echo -e "\n${BLUE}[TEST]${NC} TC-015: JSON Output Format"
JSON_OUTPUT=$($CLI_PATH validate --format json "$TEST_DIR/valid.yaml" 2>&1)
if echo "$JSON_OUTPUT" | grep -q '"valid".*:.*true' && echo "$JSON_OUTPUT" | grep -q '"errors".*:.*\[\]'; then
    echo -e "${GREEN}✅ PASS${NC} - JSON format output correct"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - JSON format output incorrect"
    ((FAILED++))
fi

# Test Duplicate Operation IDs
echo -e "\n${BLUE}[TEST]${NC} TC-CUSTOM-01: Duplicate Operation ID Detection"
if $CLI_PATH validate "$TEST_DIR/duplicate-ids.yaml" 2>&1 | grep -q "Duplicate operation ID\|duplicate"; then
    echo -e "${GREEN}✅ PASS${NC} - Duplicate operation IDs detected"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Failed to detect duplicate operation IDs"
    ((FAILED++))
fi

# Test Type Constraint Violations
echo -e "\n${BLUE}[TEST]${NC} TC-CUSTOM-02: Type Constraint Validation"
if $CLI_PATH validate "$TEST_DIR/type-errors.yaml" 2>&1 | grep -q "type.*properties\|Invalid.*constraint"; then
    echo -e "${GREEN}✅ PASS${NC} - Type constraint violations detected"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Failed to detect type constraint violations"
    ((FAILED++))
fi

# Test Malformed YAML
echo -e "\n${BLUE}[TEST]${NC} TC-048: Malformed YAML Detection"
if ! $CLI_PATH validate "$TEST_DIR/malformed.yaml" 2>&1 | grep -q "Specification is valid"; then
    echo -e "${GREEN}✅ PASS${NC} - Malformed YAML properly rejected"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Malformed YAML not detected"
    ((FAILED++))
fi

# Test Non-existent File
echo -e "\n${BLUE}[TEST]${NC} TC-047: Missing File Handling"
if $CLI_PATH validate "/path/to/nonexistent.yaml" 2>&1 | grep -q "No such file\|not found\|Error"; then
    echo -e "${GREEN}✅ PASS${NC} - Missing file error handled"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Missing file error not properly handled"
    ((FAILED++))
fi

# Summary
echo -e "\n${YELLOW}📊 Validation Test Summary${NC}"
echo "======================================"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All validation tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some validation tests failed${NC}"
    exit 1
fi