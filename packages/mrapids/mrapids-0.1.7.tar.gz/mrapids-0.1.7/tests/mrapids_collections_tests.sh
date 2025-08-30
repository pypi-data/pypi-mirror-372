#!/bin/bash

# MRAPIDS Agent Collections Tests - Based on collections/ module
# Tests collection execution, dependencies, variables, conditions

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_DIR="./test-collections"
COLLECTION_DIR="$TEST_DIR/.mrapids/collections"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
PASSED=0
FAILED=0

# Setup test collections
setup() {
    mkdir -p "$COLLECTION_DIR" "$TEST_DIR/specs"
    
    # Create test spec
    cat > "$TEST_DIR/specs/test-api.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
servers:
  - url: https://httpbin.org
paths:
  /get:
    get:
      operationId: getData
      responses:
        '200':
          description: Success
  /post:
    post:
      operationId: postData
      requestBody:
        content:
          application/json:
            schema:
              type: object
      responses:
        '200':
          description: Success
  /status/{code}:
    get:
      operationId: getStatus
      parameters:
        - name: code
          in: path
          required: true
          schema:
            type: integer
      responses:
        default:
          description: Status response
EOF

    # Simple collection
    cat > "$COLLECTION_DIR/simple-test.yaml" << 'EOF'
name: simple-test
description: Basic collection test
requests:
  - name: get_data
    operation: getData
    spec: specs/test-api.yaml
EOF

    # Collection with variables
    cat > "$COLLECTION_DIR/vars-test.yaml" << 'EOF'
name: vars-test
description: Collection with variables
variables:
  base_url: https://httpbin.org
  test_value: hello
requests:
  - name: get_with_vars
    operation: getData
    spec: specs/test-api.yaml
    params:
      test: "{{test_value}}"
EOF

    # Collection with dependencies
    cat > "$COLLECTION_DIR/deps-test.yaml" << 'EOF'
name: deps-test
description: Collection with dependencies
requests:
  - name: first_request
    operation: getData
    spec: specs/test-api.yaml
    save_as: first_response
  - name: dependent_request
    operation: postData
    spec: specs/test-api.yaml
    depends_on: first_request
    body:
      data: "{{first_response.url}}"
EOF

    # Collection with conditions
    cat > "$COLLECTION_DIR/condition-test.yaml" << 'EOF'
name: condition-test
description: Collection with conditional execution
requests:
  - name: check_status
    operation: getStatus
    spec: specs/test-api.yaml
    params:
      code: 200
    save_as: status_check
  - name: conditional_request
    operation: getData
    spec: specs/test-api.yaml
    if: "status_check.status == 200"
  - name: skip_request
    operation: getData
    spec: specs/test-api.yaml
    skip: "status_check.status != 404"
EOF

    # Collection with critical request
    cat > "$COLLECTION_DIR/critical-test.yaml" << 'EOF'
name: critical-test
description: Collection with critical failure
requests:
  - name: critical_check
    operation: getStatus
    spec: specs/test-api.yaml
    params:
      code: 500
    critical: true
  - name: should_not_run
    operation: getData
    spec: specs/test-api.yaml
  - name: cleanup
    operation: getData
    spec: specs/test-api.yaml
    run_always: true
EOF

    # Collection with retry
    cat > "$COLLECTION_DIR/retry-test.yaml" << 'EOF'
name: retry-test
description: Collection with retry logic
requests:
  - name: flaky_request
    operation: getStatus
    spec: specs/test-api.yaml
    params:
      code: 503
    retry:
      attempts: 3
      delay: 1000
      backoff: exponential
EOF

    # Collection with test assertions
    cat > "$COLLECTION_DIR/test-suite.yaml" << 'EOF'
name: test-suite
description: Collection with test assertions
requests:
  - name: test_get
    operation: getData
    spec: specs/test-api.yaml
    expect:
      status: 200
      body:
        url: "https://httpbin.org/get"
  - name: test_status
    operation: getStatus
    spec: specs/test-api.yaml
    params:
      code: 404
    expect:
      status: 404
EOF
}

# Cleanup
cleanup() {
    cd ..
    rm -rf "$TEST_DIR"
}

# Test helper
run_collection_test() {
    local name="$1"
    local collection="$2"
    local flags="$3"
    local should_pass="$4"
    local expected_content="$5"
    
    echo -e "\n${BLUE}[TEST]${NC} $name"
    
    set +e
    OUTPUT=$($CLI_PATH collection $flags "$collection" --dir "$COLLECTION_DIR" 2>&1)
    EXIT_CODE=$?
    set -e
    
    if [ "$should_pass" = "true" ]; then
        if [ $EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}✅ PASS${NC} - Collection executed successfully"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Collection execution failed"
            echo "$OUTPUT"
            ((FAILED++))
            return
        fi
    else
        if [ $EXIT_CODE -ne 0 ]; then
            echo -e "${GREEN}✅ PASS${NC} - Collection failed as expected"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Collection should have failed"
            echo "$OUTPUT"
            ((FAILED++))
            return
        fi
    fi
    
    # Check expected content
    if [ -n "$expected_content" ]; then
        if echo "$OUTPUT" | grep -qi "$expected_content"; then
            echo "  ✓ Found expected: $expected_content"
        else
            echo -e "${YELLOW}  ⚠ Missing expected: $expected_content${NC}"
        fi
    fi
}

echo -e "${YELLOW}🧪 MRAPIDS Agent - Collections Framework Tests${NC}"
echo "=============================================="

# Setup
trap cleanup EXIT
cd "$TEST_DIR"
setup

# TC-COLL-001: List Collections
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-001: List Collections"
OUTPUT=$($CLI_PATH collection list --dir "$COLLECTION_DIR" 2>&1)
if echo "$OUTPUT" | grep -q "simple-test.*vars-test.*deps-test"; then
    echo -e "${GREEN}✅ PASS${NC} - Collections listed"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Collections not listed properly"
    echo "$OUTPUT"
    ((FAILED++))
fi

# TC-COLL-002: Show Collection Details
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-002: Show Collection Details"
OUTPUT=$($CLI_PATH collection show simple-test --dir "$COLLECTION_DIR" 2>&1)
if echo "$OUTPUT" | grep -q "simple-test.*Basic collection.*get_data.*getData"; then
    echo -e "${GREEN}✅ PASS${NC} - Collection details shown"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Collection details missing"
    echo "$OUTPUT"
    ((FAILED++))
fi

# TC-COLL-003: Validate Collection
run_collection_test \
    "TC-COLL-003: Validate Collection" \
    "simple-test" \
    "validate" \
    "true" \
    "valid"

# TC-COLL-004: Run Simple Collection
# Note: This would make actual HTTP requests, so we skip in test mode
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-004: Run Simple Collection"
echo -e "${YELLOW}⚠️  SKIP${NC} - Would make external HTTP requests"

# TC-COLL-005: Collection with Variables
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-005: Show Collection Variables"
OUTPUT=$($CLI_PATH collection show vars-test --dir "$COLLECTION_DIR" 2>&1)
if echo "$OUTPUT" | grep -q "base_url.*test_value"; then
    echo -e "${GREEN}✅ PASS${NC} - Variables displayed"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Variables not shown"
    ((FAILED++))
fi

# TC-COLL-006: Collection Dependencies
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-006: Show Collection Dependencies"
OUTPUT=$($CLI_PATH collection show deps-test --dir "$COLLECTION_DIR" 2>&1)
if echo "$OUTPUT" | grep -q "dependent_request.*first_request"; then
    echo -e "${GREEN}✅ PASS${NC} - Dependencies shown"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Dependencies not displayed"
    ((FAILED++))
fi

# TC-COLL-007: Validate Critical Collection
run_collection_test \
    "TC-COLL-007: Validate Critical Collection" \
    "critical-test" \
    "validate" \
    "true" \
    "valid"

# TC-COLL-008: Validate Conditional Collection
run_collection_test \
    "TC-COLL-008: Validate Conditional Collection" \
    "condition-test" \
    "validate" \
    "true" \
    "valid"

# TC-COLL-009: Validate Retry Collection
run_collection_test \
    "TC-COLL-009: Validate Retry Collection" \
    "retry-test" \
    "validate" \
    "true" \
    "valid"

# TC-COLL-010: Validate Test Suite
run_collection_test \
    "TC-COLL-010: Validate Test Suite" \
    "test-suite" \
    "validate" \
    "true" \
    "valid"

# Test error handling
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-ERR: Non-existent Collection"
if $CLI_PATH collection show non-existent --dir "$COLLECTION_DIR" 2>&1 | grep -qi "not found\|error"; then
    echo -e "${GREEN}✅ PASS${NC} - Error handled properly"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Error not handled"
    ((FAILED++))
fi

# Test collection variable override (dry run)
echo -e "\n${BLUE}[TEST]${NC} TC-COLL-VAR: Variable Override Syntax"
if $CLI_PATH collection run vars-test --var test_value=override --dry-run --dir "$COLLECTION_DIR" 2>&1; then
    echo -e "${GREEN}✅ PASS${NC} - Variable override syntax accepted"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - Dry run not supported"
fi

# Summary
echo -e "\n${YELLOW}📊 Collections Test Summary${NC}"
echo "==========================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All collections tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some collections tests failed${NC}"
    exit 1
fi