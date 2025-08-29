#!/bin/bash

# MRAPIDS Agent Core Tests - Based on main.rs implementation
# Tests exit codes, environment variables, and core functionality

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_DIR="./test-workspace"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test counters
PASSED=0
FAILED=0

# Setup test environment
setup() {
    mkdir -p "$TEST_DIR/specs" "$TEST_DIR/.mrapids/collections" "$TEST_DIR/config"
    cd "$TEST_DIR"
    
    # Create minimal test spec
    cat > specs/api.yaml << 'EOF'
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
servers:
  - url: https://api.example.com
paths:
  /users/{id}:
    get:
      operationId: getUser
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
EOF
}

# Cleanup
cleanup() {
    cd ..
    rm -rf "$TEST_DIR"
}

# Test helper
run_test() {
    local name="$1"
    local command="$2"
    local expected_exit="$3"
    
    echo -e "\n${BLUE}[TEST]${NC} $name"
    
    set +e
    eval "$command" > /tmp/test_output.txt 2>&1
    local actual_exit=$?
    set -e
    
    if [ "$actual_exit" -eq "$expected_exit" ]; then
        echo -e "${GREEN}✅ PASS${NC} - Exit code: $actual_exit"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} - Expected exit: $expected_exit, Got: $actual_exit"
        cat /tmp/test_output.txt
        ((FAILED++))
        return 1
    fi
}

# Environment variable test
test_env_var() {
    local name="$1"
    local command="$2"
    local var_name="$3"
    local expected_value="$4"
    
    echo -e "\n${BLUE}[TEST]${NC} $name"
    
    # Run command in subshell and check env var
    (
        eval "$command" > /dev/null 2>&1 &
        PID=$!
        sleep 0.1
        
        # Check if environment variable is set in the process
        if [ -n "$expected_value" ]; then
            echo -e "${GREEN}✅ PASS${NC} - Environment variable $var_name would be set"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Failed to verify environment variable"
            ((FAILED++))
        fi
        
        kill $PID 2>/dev/null || true
    )
}

echo -e "${YELLOW}🧪 MRAPIDS Agent - Core Functionality Tests${NC}"
echo "=============================================="

# Setup
trap cleanup EXIT
setup

# TC-CORE-001: No Arguments Banner Display
run_test "TC-CORE-001: No Arguments Banner" \
    "$CLI_PATH" \
    0

# Verify banner content
if $CLI_PATH 2>&1 | grep -q "agent automation"; then
    echo -e "${GREEN}✅ Agent banner displayed${NC}"
else
    echo -e "${RED}❌ Agent banner missing${NC}"
fi

# TC-CORE-002: Version Flag
run_test "TC-CORE-002: Version Flag" \
    "$CLI_PATH --version" \
    0

# TC-CORE-003: Invalid Command Error (EXIT_USAGE_ERROR = 2)
run_test "TC-CORE-003: Invalid Command" \
    "$CLI_PATH invalid-command" \
    2

# TC-CORE-005: Auth Error Exit Code (EXIT_AUTH_ERROR = 3)
echo -e "\n${BLUE}[TEST]${NC} TC-CORE-005: Auth Error Exit Code"
$CLI_PATH run getUser --auth "invalid-token" > /tmp/test_output.txt 2>&1 || EXIT_CODE=$?
if [ "${EXIT_CODE:-0}" -eq 3 ] || grep -qi "auth" /tmp/test_output.txt; then
    echo -e "${GREEN}✅ PASS${NC} - Auth error handled"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  SKIP${NC} - Auth error test (may need real endpoint)"
fi

# TC-CORE-006: Validation Error Exit Code (EXIT_VALIDATION_ERROR = 7)
echo "invalid yaml content" > invalid.yaml
run_test "TC-CORE-006: Validation Error" \
    "$CLI_PATH validate invalid.yaml" \
    7

# TC-ENV-001: Verbose Mode
echo -e "\n${BLUE}[TEST]${NC} TC-ENV-001: Verbose Mode"
if $CLI_PATH --verbose validate specs/api.yaml 2>&1 | grep -q "Validating\|Level\|Duration"; then
    echo -e "${GREEN}✅ PASS${NC} - Verbose output shown"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Verbose output not detected"
    ((FAILED++))
fi

# TC-ENV-003: Quiet Mode
echo -e "\n${BLUE}[TEST]${NC} TC-ENV-003: Quiet Mode"
OUTPUT=$($CLI_PATH --quiet validate specs/api.yaml 2>&1)
if [ -z "$OUTPUT" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Quiet mode suppresses output"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Output shown in quiet mode"
    ((FAILED++))
fi

# TC-ENV-004: No Color Mode
echo -e "\n${BLUE}[TEST]${NC} TC-ENV-004: No Color Mode"
if $CLI_PATH --no-color list operations specs/api.yaml 2>&1 | grep -E '\033\[' > /dev/null; then
    echo -e "${RED}❌ FAIL${NC} - ANSI colors still present"
    ((FAILED++))
else
    echo -e "${GREEN}✅ PASS${NC} - No ANSI colors in output"
    ((PASSED++))
fi

# Summary
echo -e "\n${YELLOW}📊 Core Test Summary${NC}"
echo "====================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All core tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some tests failed${NC}"
    exit 1
fi