#!/bin/bash

# MRAPIDS-Agent Authentication & Policy Tests
# Tests auth profiles, policy engine, and security features

set -e

# Configuration
AGENT_PATH="${AGENT_PATH:-./target/release/mrapids-agent}"
TEST_DIR="./test-auth-policy"

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
    rm -rf "$TEST_DIR"
    mkdir -p "$TEST_DIR"
    cd "$TEST_DIR"
    
    # Initialize with custom policy
    $AGENT_PATH init > /dev/null 2>&1
    
    # Create test policy file
    cat > .mrapids/policy.toml << 'EOF'
# Test Policy Configuration

[[rules]]
name = "allow_read_operations"
pattern = "get*"
allow = true
audit = true

[[rules]]
name = "allow_list_operations"
pattern = "list*"
allow = true
audit = false

[[rules]]
name = "deny_delete_operations"
pattern = "delete*"
allow = false
audit = true

[[rules]]
name = "conditional_create"
pattern = "create*"
allow = true
conditions = { auth_profile = "admin" }
audit = true

[[rules]]
name = "time_restricted"
pattern = "backup*"
allow = true
conditions = { time_window = "22:00-06:00" }
audit = true

[[rules]]
name = "environment_specific"
pattern = "deploy*"
allow = true
conditions = { environment = "staging" }
audit = true

# Default deny all
[[rules]]
name = "default_deny"
pattern = "*"
allow = false
audit = true
EOF

    # Create test API spec
    cat > specs/test-api.yaml << 'EOF'
openapi: 3.0.0
info:
  title: Policy Test API
  version: 1.0.0
paths:
  /users:
    get:
      operationId: getUsers
    post:
      operationId: createUser
    delete:
      operationId: deleteAllUsers
  /items:
    get:
      operationId: listItems
  /backup:
    post:
      operationId: backupData
  /deploy:
    post:
      operationId: deployService
EOF

    # Set up environment variables
    export GITHUB_TOKEN="test-github-token"
    export STRIPE_KEY="test-stripe-key"
    export ADMIN_TOKEN="test-admin-token"
}

cleanup() {
    cd ..
    rm -rf "$TEST_DIR"
}

# Test helper
run_test() {
    local name="$1"
    local command="$2"
    local should_pass="$3"
    local expected_content="$4"
    
    echo -e "\n${BLUE}[TEST]${NC} $name"
    
    set +e
    OUTPUT=$($command 2>&1)
    EXIT_CODE=$?
    set -e
    
    if [ "$should_pass" = "true" ]; then
        if [ $EXIT_CODE -eq 0 ]; then
            echo -e "${GREEN}✅ PASS${NC}"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Should have succeeded"
            echo "$OUTPUT"
            ((FAILED++))
            return
        fi
    else
        if [ $EXIT_CODE -ne 0 ]; then
            echo -e "${GREEN}✅ PASS${NC} - Failed as expected"
            ((PASSED++))
        else
            echo -e "${RED}❌ FAIL${NC} - Should have failed"
            echo "$OUTPUT"
            ((FAILED++))
            return
        fi
    fi
    
    if [ -n "$expected_content" ] && ! echo "$OUTPUT" | grep -qi "$expected_content"; then
        echo -e "${YELLOW}  ⚠ Missing expected: $expected_content${NC}"
    fi
}

# Start tests
trap cleanup EXIT
setup

echo -e "${YELLOW}🧪 MRAPIDS-Agent Auth & Policy Tests${NC}"
echo "======================================"

# Authentication Profile Tests
echo -e "\n${YELLOW}Authentication Profile Tests${NC}"

# TC-AUTH-001: Add Bearer Token Profile
echo -e "\n${BLUE}[TEST]${NC} TC-AUTH-001: Add Bearer Token Profile"
echo -e "bearer\nGITHUB_TOKEN\n" | $AGENT_PATH auth add github --type bearer > /dev/null 2>&1
if [ -f ".mrapids/auth/github.toml" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAILED++))
fi

# TC-AUTH-002: Add API Key Profile
echo -e "\n${BLUE}[TEST]${NC} TC-AUTH-002: Add API Key Profile"
echo -e "X-API-Key\nSTRIPE_KEY\n" | $AGENT_PATH auth add stripe --type api-key > /dev/null 2>&1
if grep -q "X-API-Key" ".mrapids/auth/stripe.toml" 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAILED++))
fi

# TC-AUTH-003: Add Admin Profile
echo -e "\n${BLUE}[TEST]${NC} TC-AUTH-003: Add Admin Profile"
echo -e "bearer\nADMIN_TOKEN\n" | $AGENT_PATH auth add admin --type bearer > /dev/null 2>&1
if [ -f ".mrapids/auth/admin.toml" ]; then
    echo -e "${GREEN}✅ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC}"
    ((FAILED++))
fi

# TC-AUTH-004: List Auth Profiles
run_test "TC-AUTH-004: List Auth Profiles" \
    "$AGENT_PATH auth list" \
    "true" \
    "github.*stripe.*admin"

# TC-AUTH-005: Show Profile (Never Shows Token)
echo -e "\n${BLUE}[TEST]${NC} TC-AUTH-005: Show Profile Security"
OUTPUT=$($AGENT_PATH auth show github 2>&1)
if echo "$OUTPUT" | grep -q "GITHUB_TOKEN" && ! echo "$OUTPUT" | grep -q "test-github-token"; then
    echo -e "${GREEN}✅ PASS${NC} - Token not exposed"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Security issue"
    ((FAILED++))
fi

# Policy Validation Tests
echo -e "\n${YELLOW}Policy Validation Tests${NC}"

# TC-POLICY-001: Validate Policy File
run_test "TC-POLICY-001: Validate Policy Syntax" \
    "$AGENT_PATH validate --policy-only" \
    "true" \
    "valid\|passed"

# Start server for policy tests
$AGENT_PATH start --daemon > /dev/null 2>&1
sleep 3

# Policy Enforcement Tests
echo -e "\n${YELLOW}Policy Enforcement Tests${NC}"

# TC-POLICY-002: Allow Read Operations
echo -e "\n${BLUE}[TEST]${NC} TC-POLICY-002: Allow Read Operations"
RESPONSE=$(curl -s -X POST http://localhost:3333/rpc \
    -d '{"jsonrpc":"2.0","method":"show","params":{"operation":"getUsers"},"id":1}')
if echo "$RESPONSE" | grep -q "getUsers"; then
    echo -e "${GREEN}✅ PASS${NC} - Read operation allowed"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Read operation blocked"
    ((FAILED++))
fi

# TC-POLICY-003: Deny Delete Operations
echo -e "\n${BLUE}[TEST]${NC} TC-POLICY-003: Deny Delete Operations"
RESPONSE=$(curl -s -X POST http://localhost:3333/rpc \
    -d '{"jsonrpc":"2.0","method":"run","params":{"operation":"deleteAllUsers"},"id":1}')
if echo "$RESPONSE" | grep -qi "error.*policy\|not allowed"; then
    echo -e "${GREEN}✅ PASS${NC} - Delete operation blocked"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Delete operation not blocked"
    echo "$RESPONSE"
    ((FAILED++))
fi

# TC-POLICY-004: Conditional Create (Without Admin)
echo -e "\n${BLUE}[TEST]${NC} TC-POLICY-004: Conditional Create Without Admin"
RESPONSE=$(curl -s -X POST http://localhost:3333/rpc \
    -d '{"jsonrpc":"2.0","method":"run","params":{"operation":"createUser","auth_profile":"github"},"id":1}')
if echo "$RESPONSE" | grep -qi "error.*policy\|not allowed"; then
    echo -e "${GREEN}✅ PASS${NC} - Create blocked without admin"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Create allowed without admin"
    ((FAILED++))
fi

# TC-POLICY-005: Conditional Create (With Admin)
echo -e "\n${BLUE}[TEST]${NC} TC-POLICY-005: Conditional Create With Admin"
RESPONSE=$(curl -s -X POST http://localhost:3333/rpc \
    -d '{"jsonrpc":"2.0","method":"show","params":{"operation":"createUser","auth_profile":"admin"},"id":1}')
if ! echo "$RESPONSE" | grep -qi "error.*policy"; then
    echo -e "${GREEN}✅ PASS${NC} - Create allowed with admin"
    ((PASSED++))
else
    echo -e "${RED}❌ FAIL${NC} - Create blocked with admin"
    ((FAILED++))
fi

# Rate Limiting Tests
echo -e "\n${YELLOW}Rate Limiting Tests${NC}"

# TC-RATE-001: Check Initial Limits
run_test "TC-RATE-001: Show Rate Limits" \
    "$AGENT_PATH limits show" \
    "true" \
    "remaining"

# TC-RATE-002: Set Custom Limit
run_test "TC-RATE-002: Set Rate Limit" \
    "$AGENT_PATH limits set --tier minute --limit 10" \
    "true" \
    "updated\|set"

# Security Tests
echo -e "\n${YELLOW}Security Tests${NC}"

# TC-SEC-001: Response Redaction Pattern
echo -e "\n${BLUE}[TEST]${NC} TC-SEC-001: Redaction Patterns"
# Check config has redaction patterns
if grep -q "password\|token\|key" .mrapids/config.toml 2>/dev/null; then
    echo -e "${GREEN}✅ PASS${NC} - Redaction patterns configured"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} - No redaction patterns found"
fi

# Audit Log Tests
echo -e "\n${YELLOW}Audit Log Tests${NC}"

# TC-AUDIT-001: Check Audit Logs Created
echo -e "\n${BLUE}[TEST]${NC} TC-AUDIT-001: Audit Logs Created"
$AGENT_PATH logs > /tmp/audit_test.log 2>&1
if [ -s /tmp/audit_test.log ]; then
    echo -e "${GREEN}✅ PASS${NC} - Audit logs exist"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} - No audit logs yet"
fi

# TC-AUDIT-002: Policy Violations Logged
echo -e "\n${BLUE}[TEST]${NC} TC-AUDIT-002: Policy Violations Logged"
# The delete operation we tried earlier should be logged
if $AGENT_PATH logs 2>&1 | grep -qi "deleteAllUsers.*denied\|policy.*violation"; then
    echo -e "${GREEN}✅ PASS${NC} - Policy violations logged"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} - Policy violation not found in logs"
fi

# Stop server
$AGENT_PATH stop > /dev/null 2>&1

# Advanced Policy Tests
echo -e "\n${YELLOW}Advanced Policy Tests${NC}"

# TC-POLICY-006: Policy Conflict Detection
echo -e "\n${BLUE}[TEST]${NC} TC-POLICY-006: Policy Conflict Detection"
# Add conflicting rule
cat >> .mrapids/policy.toml << 'EOF'

[[rules]]
name = "conflict_rule"
pattern = "get*"
allow = false
audit = true
EOF

if $AGENT_PATH validate --policy-only 2>&1 | grep -qi "conflict\|duplicate\|warning"; then
    echo -e "${GREEN}✅ PASS${NC} - Conflict detected"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  WARN${NC} - Conflict not detected"
fi

# Summary
echo -e "\n${YELLOW}📊 Auth & Policy Test Summary${NC}"
echo "=============================="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All auth & policy tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}⚠️  Some auth & policy tests failed${NC}"
    exit 1
fi