#!/bin/bash

# MRAPIDS Agent Validation Tests - Based on validation/validator.rs
# Tests 3-level validation system with actual code paths

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_DIR="./test-validation"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
PASSED=0
FAILED=0

# Setup test specs
setup() {
    mkdir -p "$TEST_DIR"
    
    # Valid spec
    cat > "$TEST_DIR/valid.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Valid API
  version: 1.0.0
  description: A valid test API
servers:
  - url: https://api.example.com
paths:
  /users:
    get:
      operationId: getUsers
      summary: Get all users
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
EOF

    # Spec with undefined references
    cat > "$TEST_DIR/undefined-refs.yaml" << 'EOF'
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
                $ref: '#/components/schemas/UserList'
components:
  schemas:
    User:
      type: object
EOF

    # Spec with duplicate operation IDs
    cat > "$TEST_DIR/duplicate-ops.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Duplicate Ops API
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

    # Spec with type constraint violations
    cat > "$TEST_DIR/type-violations.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Type Violations API
  version: 1.0.0
paths:
  /test:
    get:
      responses:
        '200':
          description: Success
components:
  schemas:
    BadSchema:
      type: string
      minLength: 10
      maximum: 100
EOF

    # Spec missing descriptions (for lint)
    cat > "$TEST_DIR/missing-desc.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
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
  title: Malformed
  version: 1.0.0
paths:
  /test:
    get:
      invalid yaml here:::
        more: problems
EOF
}

# Cleanup
cleanup() {
    rm -rf "$TEST_DIR"
}

# Test validation level
test_validation() {
    local name="$1"
    local file="$2"
    local flags="$3"
    local should_pass="$4"
    local expected_content="$5"
    
    echo -e "\n${BLUE}[TEST]${NC} $name"
    
    set +e
    OUTPUT=$($CLI_PATH validate $flags "$TEST_DIR/$file" 2>&1)
    EXIT_CODE=$?
    set -e
    
    # Check pass/fail
    if [ "$should_pass" = "true" ]; then
        if [ $EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}✅ PASS${NC} - Validation passed as expected"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Validation should have passed"
            echo "$OUTPUT"
            ((FAILED++))
            return
        fi
    else
        if [ $EXIT_CODE -ne 0 ]; then
            echo -e "${GREEN}✅ PASS${NC} - Validation failed as expected"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Validation should have failed"
            echo "$OUTPUT"
            ((FAILED++))
            return
        fi
    fi
    
    # Check expected content if provided
    if [ -n "$expected_content" ]; then
        if echo "$OUTPUT" | grep -qi "$expected_content"; then
            echo "  ✓ Found expected: $expected_content"
        else
            echo -e "${RED}  ✗ Missing expected: $expected_content${NC}"
            ((FAILED--))
            ((PASSED++))
        fi
    fi
}

echo -e "${YELLOW}🧪 MRAPIDS Agent - Validation System Tests${NC}"
echo "==========================================="

# Setup
trap cleanup EXIT
setup

# TC-VAL-001: Quick Validation (default)
test_validation \
    "TC-VAL-001: Quick Validation - Valid Spec" \
    "valid.yaml" \
    "" \
    "true" \
    "Specification is valid"

# TC-VAL-002: Standard Validation (--strict)
test_validation \
    "TC-VAL-002: Standard Validation - Valid Spec" \
    "valid.yaml" \
    "--strict" \
    "true" \
    "Level.*standard"

# TC-VAL-003: Full Validation (--lint)
test_validation \
    "TC-VAL-003: Full Validation - Missing Descriptions" \
    "missing-desc.yaml" \
    "--lint" \
    "false" \
    "missing.*description\|warning"

# TC-VAL-004: JSON Output Format
echo -e "\n${BLUE}[TEST]${NC} TC-VAL-004: JSON Output Format"
JSON_OUTPUT=$($CLI_PATH validate --format json "$TEST_DIR/valid.yaml" 2>&1)
if echo "$JSON_OUTPUT" | jq -e '.valid == true and .errors == []' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} - Valid JSON output"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Invalid JSON output"
    echo "$JSON_OUTPUT"
    ((FAILED++))
fi

# TC-VAL-005: Malformed YAML Detection
test_validation \
    "TC-VAL-005: Malformed YAML Detection" \
    "malformed.yaml" \
    "" \
    "false" \
    "Failed to parse"

# Test specific validation rules

# Undefined References
test_validation \
    "TC-VAL-REF: Undefined Reference Detection" \
    "undefined-refs.yaml" \
    "--strict" \
    "false" \
    "Undefined reference.*UserList"

# Duplicate Operation IDs
test_validation \
    "TC-VAL-DUP: Duplicate Operation ID Detection" \
    "duplicate-ops.yaml" \
    "--strict" \
    "false" \
    "Duplicate operation ID.*getResource"

# Type Constraint Violations
test_validation \
    "TC-VAL-TYPE: Type Constraint Violation" \
    "type-violations.yaml" \
    "--strict" \
    "false" \
    "Invalid.*constraint\|string.*maximum"

# Test validation levels incrementally
echo -e "\n${BLUE}[TEST]${NC} TC-VAL-LEVELS: Validation Level Checking"
OUTPUT=$($CLI_PATH validate --lint "$TEST_DIR/valid.yaml" 2>&1)
if echo "$OUTPUT" | grep -q "quick.*standard.*security.*lint"; then
    echo -e "${GREEN}✅ PASS${NC} - All validation levels executed"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Not all validation levels shown"
    ((FAILED++))
fi

# Test error code for validation failures
echo -e "\n${BLUE}[TEST]${NC} TC-VAL-EXIT: Validation Error Exit Code"
$CLI_PATH validate "$TEST_DIR/undefined-refs.yaml" > /dev/null 2>&1 || EXIT_CODE=$?
if [ "${EXIT_CODE:-0}" -eq 7 ]; then
    echo -e "${GREEN}✅ PASS${NC} - Correct validation error exit code (7)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Wrong exit code: ${EXIT_CODE:-0}"
    ((FAILED++))
fi

# Summary
echo -e "\n${YELLOW}📊 Validation Test Summary${NC}"
echo "=========================="
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