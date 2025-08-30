#!/bin/bash

# Generation Test Cases - SDK and Code Generation Tests
# Tests all code generation functionality

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_SPEC="${TEST_SPEC:-specs/httpbin.yaml}"
OUTPUT_DIR="${OUTPUT_DIR:-./test-output}"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test Result Tracking
PASSED=0
FAILED=0

# Cleanup function
cleanup() {
    rm -rf "$OUTPUT_DIR"
}

# Setup
mkdir -p "$OUTPUT_DIR"
trap cleanup EXIT

# Helper Functions
test_sdk_generation() {
    local language="$1"
    local test_name="TC-SDK-$language"
    local output_path="$OUTPUT_DIR/sdk-$language"
    
    echo -e "\n${BLUE}[TEST]${NC} $test_name: Generate $language SDK"
    
    if $CLI_PATH gen sdk --language "$language" --output "$output_path" "$TEST_SPEC" 2>&1 | grep -q "generated successfully"; then
        # Verify expected files exist
        case "$language" in
            typescript)
                if [ -f "$output_path/client.ts" ] && [ -f "$output_path/package.json" ]; then
                    echo -e "${GREEN}✅ PASS${NC} - TypeScript SDK generated with expected files"
                    ((PASSED++))
                else
                    echo -e "${RED}❌ FAIL${NC} - Missing expected TypeScript files"
                    ((FAILED++))
                fi
                ;;
            python)
                if [ -f "$output_path/client.py" ] && [ -f "$output_path/requirements.txt" ]; then
                    echo -e "${GREEN}✅ PASS${NC} - Python SDK generated with expected files"
                    ((PASSED++))
                else
                    echo -e "${RED}❌ FAIL${NC} - Missing expected Python files"
                    ((FAILED++))
                fi
                ;;
            go)
                if [ -f "$output_path/client.go" ] && [ -f "$output_path/go.mod" ]; then
                    echo -e "${GREEN}✅ PASS${NC} - Go SDK generated with expected files"
                    ((PASSED++))
                else
                    echo -e "${RED}❌ FAIL${NC} - Missing expected Go files"
                    ((FAILED++))
                fi
                ;;
            rust)
                if [ -f "$output_path/Cargo.toml" ]; then
                    echo -e "${GREEN}✅ PASS${NC} - Rust SDK generated with expected files"
                    ((PASSED++))
                else
                    echo -e "${RED}❌ FAIL${NC} - Missing expected Rust files"
                    ((FAILED++))
                fi
                ;;
        esac
    else
        echo -e "${RED}❌ FAIL${NC} - SDK generation failed"
        ((FAILED++))
    fi
}

test_stub_generation() {
    local framework="$1"
    local test_name="TC-STUB-$framework"
    local output_path="$OUTPUT_DIR/stubs-$framework"
    
    echo -e "\n${BLUE}[TEST]${NC} $test_name: Generate $framework server stubs"
    
    if $CLI_PATH gen stubs --framework "$framework" --output "$output_path" "$TEST_SPEC" 2>&1 | grep -q "generated successfully\|Files generated"; then
        echo -e "${GREEN}✅ PASS${NC} - $framework stubs generated"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - $framework stub generation failed"
        ((FAILED++))
    fi
}

echo -e "${YELLOW}🧪 Agent CLI - Generation Test Suite${NC}"
echo "======================================"

# TC-027 to TC-030: SDK Generation Tests
echo -e "\n${YELLOW}SDK Generation Tests${NC}"
test_sdk_generation "typescript"
test_sdk_generation "python"
test_sdk_generation "go"
test_sdk_generation "rust"

# TC-031 to TC-032: Server Stub Tests
echo -e "\n${YELLOW}Server Stub Generation Tests${NC}"
test_stub_generation "express"
test_stub_generation "fastapi"
test_stub_generation "gin"

# TC-033: Generate Request Snippets
echo -e "\n${BLUE}[TEST]${NC} TC-033: Generate Request Snippets"
if $CLI_PATH gen snippets --output "$OUTPUT_DIR/snippets" "$TEST_SPEC" 2>&1 | grep -q "generated\|Generated"; then
    echo -e "${GREEN}✅ PASS${NC} - Request snippets generated"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Snippet generation failed"
    ((FAILED++))
fi

# TC-034: cURL Command Generation
echo -e "\n${BLUE}[TEST]${NC} TC-034: Generate cURL Commands"
if $CLI_PATH gen snippets --format curl "$TEST_SPEC" 2>&1 | grep -q "curl\|Generated"; then
    echo -e "${GREEN}✅ PASS${NC} - cURL commands generated"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - cURL generation failed"
    ((FAILED++))
fi

# Test Package Names
echo -e "\n${BLUE}[TEST]${NC} TC-CUSTOM: Custom Package Name"
if $CLI_PATH gen sdk --language typescript --output "$OUTPUT_DIR/custom-sdk" --package "my-custom-api" "$TEST_SPEC" 2>&1 | grep -q "generated successfully"; then
    if grep -q "my-custom-api" "$OUTPUT_DIR/custom-sdk/package.json" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC} - Custom package name applied"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - Custom package name not found"
        ((FAILED++))
    fi
else
    echo -e "${RED}❌ FAIL${NC} - Custom package generation failed"
    ((FAILED++))
fi

# Summary
echo -e "\n${YELLOW}📊 Generation Test Summary${NC}"
echo "======================================"
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All generation tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some generation tests failed${NC}"
    exit 1
fi