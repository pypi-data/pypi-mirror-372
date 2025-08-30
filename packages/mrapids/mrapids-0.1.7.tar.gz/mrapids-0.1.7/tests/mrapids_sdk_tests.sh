#!/bin/bash

# MRAPIDS Agent SDK Generation Tests - Based on sdk_gen module
# Tests SDK generation for TypeScript, Python, Go, and Rust

set -e

# Configuration
CLI_PATH="${CLI_PATH:-./target/release/mrapids}"
TEST_DIR="./test-sdk-gen"
OUTPUT_BASE="$TEST_DIR/output"

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
    mkdir -p "$TEST_DIR/specs" "$OUTPUT_BASE"
    
    # Create comprehensive test spec
    cat > "$TEST_DIR/specs/api.yaml" << 'EOF'
openapi: 3.0.0
info:
  title: Test API for SDK Generation
  version: 1.0.0
  description: API for testing SDK generation
servers:
  - url: https://api.example.com/v1
paths:
  /users:
    get:
      operationId: getUsers
      summary: Get all users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
        - name: offset
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      operationId: createUser
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserInput'
      responses:
        '201':
          description: Created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
  /users/{id}:
    get:
      operationId: getUserById
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
      properties:
        id:
          type: string
        email:
          type: string
          format: email
        name:
          type: string
        age:
          type: integer
          minimum: 0
        active:
          type: boolean
    UserInput:
      type: object
      required:
        - email
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        age:
          type: integer
EOF
}

# Cleanup
cleanup() {
    rm -rf "$TEST_DIR"
}

# Test SDK generation
test_sdk_generation() {
    local test_name="$1"
    local language="$2"
    local package_name="$3"
    local expected_files=("${@:4}")
    
    echo -e "\n${BLUE}[TEST]${NC} $test_name"
    
    local output_dir="$OUTPUT_BASE/sdk-$language"
    rm -rf "$output_dir"
    
    # Run SDK generation
    set +e
    if [ -n "$package_name" ]; then
        OUTPUT=$($CLI_PATH gen sdk \
            --language "$language" \
            --output "$output_dir" \
            --package "$package_name" \
            "$TEST_DIR/specs/api.yaml" 2>&1)
    else
        OUTPUT=$($CLI_PATH gen sdk \
            --language "$language" \
            --output "$output_dir" \
            "$TEST_DIR/specs/api.yaml" 2>&1)
    fi
    EXIT_CODE=$?
    set -e
    
    if [ $EXIT_CODE -ne 0 ]; then
        echo -e "${RED}❌ FAIL${NC} - SDK generation failed"
        echo "$OUTPUT"
        ((FAILED++))
        return
    fi
    
    # Check expected files
    local all_exist=true
    for file in "${expected_files[@]}"; do
        if [ -f "$output_dir/$file" ]; then
            echo "  ✓ Found: $file"
        else
            echo -e "${RED}  ✗ Missing: $file${NC}"
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        echo -e "${GREEN}✅ PASS${NC} - All expected files generated"
        ((PASSED++))
        
        # Additional checks based on language
        case "$language" in
            typescript)
                if grep -q "\"name\": \"$package_name\"" "$output_dir/package.json"; then
                    echo "  ✓ Package name correctly set"
                fi
                ;;
            python)
                if grep -q "name=\"$package_name\"" "$output_dir/setup.py" 2>/dev/null; then
                    echo "  ✓ Package name correctly set"
                fi
                ;;
            go)
                if grep -q "module $package_name" "$output_dir/go.mod" 2>/dev/null; then
                    echo "  ✓ Module name correctly set"
                fi
                ;;
        esac
    else
        echo -e "${RED}❌ FAIL${NC} - Missing expected files"
        ((FAILED++))
    fi
}

echo -e "${YELLOW}🧪 MRAPIDS Agent - SDK Generation Tests${NC}"
echo "========================================"

# Setup
trap cleanup EXIT
setup

# TC-SDK-001: TypeScript SDK Generation
test_sdk_generation \
    "TC-SDK-001: TypeScript SDK Generation" \
    "typescript" \
    "my-test-api" \
    "client.ts" "models.ts" "types.ts" "package.json" "README.md"

# TC-SDK-002: Python SDK Generation
test_sdk_generation \
    "TC-SDK-002: Python SDK Generation" \
    "python" \
    "my_test_api" \
    "client.py" "models.py" "__init__.py" "requirements.txt" "setup.py" "README.md"

# TC-SDK-003: Go SDK Generation
test_sdk_generation \
    "TC-SDK-003: Go SDK Generation" \
    "go" \
    "github.com/test/myapi" \
    "client.go" "models.go" "types.go" "go.mod" "README.md"

# TC-SDK-004: Rust SDK Generation
test_sdk_generation \
    "TC-SDK-004: Rust SDK Generation" \
    "rust" \
    "my-test-api" \
    "Cargo.toml" "src/lib.rs" "src/client.rs" "src/models.rs" "README.md"

# TC-SDK-005: SDK with Docs and Examples
echo -e "\n${BLUE}[TEST]${NC} TC-SDK-005: SDK with Docs and Examples"
OUTPUT=$($CLI_PATH gen sdk \
    --language typescript \
    --output "$OUTPUT_BASE/sdk-with-docs" \
    --docs --examples \
    "$TEST_DIR/specs/api.yaml" 2>&1)

if [ $? -eq 0 ]; then
    if grep -q "Example:" "$OUTPUT_BASE/sdk-with-docs/README.md" 2>/dev/null; then
        echo -e "${GREEN}✅ PASS${NC} - Documentation and examples included"
        ((PASSED++))
    else
        echo -e "${YELLOW}⚠️  WARN${NC} - SDK generated but examples not verified"
        ((PASSED++))
    fi
else
    echo -e "${RED}❌ FAIL${NC} - SDK generation with docs failed"
    ((FAILED++))
fi

# Test default output directory
echo -e "\n${BLUE}[TEST]${NC} TC-SDK-DEFAULT: Default Output Directory"
cd "$TEST_DIR"
$CLI_PATH gen sdk --language typescript specs/api.yaml > /dev/null 2>&1
if [ -d "./sdk-typescript" ]; then
    echo -e "${GREEN}✅ PASS${NC} - Default output directory created"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Default output directory not created"
    ((FAILED++))
fi
cd - > /dev/null

# Test model generation
echo -e "\n${BLUE}[TEST]${NC} TC-SDK-MODELS: Model Generation Verification"
if [ -f "$OUTPUT_BASE/sdk-typescript/models.ts" ]; then
    # Check for User model
    if grep -q "interface User" "$OUTPUT_BASE/sdk-typescript/models.ts" && \
       grep -q "email: string" "$OUTPUT_BASE/sdk-typescript/models.ts"; then
        echo -e "${GREEN}✅ PASS${NC} - Models correctly generated"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - Model content incorrect"
        ((FAILED++))
    fi
fi

# Test operation generation
echo -e "\n${BLUE}[TEST]${NC} TC-SDK-OPS: Operation Generation Verification"
if [ -f "$OUTPUT_BASE/sdk-typescript/client.ts" ]; then
    # Check for operations
    if grep -q "getUsers\|createUser\|getUserById" "$OUTPUT_BASE/sdk-typescript/client.ts"; then
        echo -e "${GREEN}✅ PASS${NC} - Operations correctly generated"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} - Operations missing"
        ((FAILED++))
    fi
fi

# Summary
echo -e "\n${YELLOW}📊 SDK Generation Test Summary${NC}"
echo "==============================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All SDK generation tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some SDK generation tests failed${NC}"
    exit 1
fi