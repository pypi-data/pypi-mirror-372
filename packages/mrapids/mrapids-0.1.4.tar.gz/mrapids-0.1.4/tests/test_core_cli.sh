#!/bin/bash

# Core CLI Test Cases - Executable Test Script
# Tests the fundamental CLI functionality

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_SPEC="${TEST_SPEC:-specs/httpbin.yaml}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test Result Tracking
PASSED=0
FAILED=0

# Helper Functions
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_pattern="$3"
    
    echo -e "\n${BLUE}[TEST]${NC} $test_name"
    echo "Command: $test_command"
    
    if eval "$test_command" 2>&1 | grep -q "$expected_pattern"; then
        echo -e "${GREEN}✅ PASS${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC}"
        ((FAILED++))
    fi
}

echo -e "${YELLOW}🧪 Agent CLI - Core Test Suite${NC}"
echo "================================="

# TC-001: Agent Banner Display
run_test "TC-001: Agent Banner Display" \
    "$CLI_PATH" \
    "agent automation"

# TC-002: Help Banner
run_test "TC-002: Help Banner" \
    "$CLI_PATH --help" \
    "agent automation.*Your OpenAPI"

# TC-003: Version Display
run_test "TC-003: Version Display" \
    "$CLI_PATH --version" \
    "Version.*[0-9]\+\.[0-9]\+\.[0-9]\+"

# TC-004: Verbose Mode
run_test "TC-004: Verbose Mode" \
    "$CLI_PATH --verbose validate $TEST_SPEC" \
    "Validating.*OpenAPI"

# TC-005: Quiet Mode
echo -e "\n${BLUE}[TEST]${NC} TC-005: Quiet Mode"
if $CLI_PATH --quiet validate $TEST_SPEC 2>&1 | wc -l | grep -q "^0$"; then
    echo -e "${GREEN}✅ PASS${NC} (No output in quiet mode)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (Output detected in quiet mode)"
    ((FAILED++))
fi

# TC-006: No Color Mode
run_test "TC-006: No Color Mode" \
    "$CLI_PATH --no-color list operations $TEST_SPEC" \
    "Operation ID"

# TC-011: Valid Spec Validation
run_test "TC-011: Valid Spec Validation" \
    "$CLI_PATH validate $TEST_SPEC" \
    "Specification is valid"

# TC-015: JSON Output Format
run_test "TC-015: JSON Output Format" \
    "$CLI_PATH validate --format json $TEST_SPEC" \
    '"valid".*true'

# TC-016: List All Operations
run_test "TC-016: List All Operations" \
    "$CLI_PATH list operations $TEST_SPEC" \
    "Available Operations"

# TC-019: Basic Operation Details
run_test "TC-019: Show Operation Details" \
    "$CLI_PATH show get $TEST_SPEC" \
    "Operation:.*get"

# TC-024: Basic Keyword Search
run_test "TC-024: Explore Search" \
    "$CLI_PATH explore status --spec $TEST_SPEC" \
    "Search Results"

# TC-035: List Collections
run_test "TC-035: List Collections" \
    "$CLI_PATH collection list" \
    "Available collections"

# TC-045: Invalid Command
echo -e "\n${BLUE}[TEST]${NC} TC-045: Invalid Command Handling"
if $CLI_PATH invalid-command 2>&1 | grep -q "error\|Error"; then
    echo -e "${GREEN}✅ PASS${NC} (Error properly handled)"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} (No error for invalid command)"
    ((FAILED++))
fi

# Summary
echo -e "\n${YELLOW}📊 Test Summary${NC}"
echo "================================="
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