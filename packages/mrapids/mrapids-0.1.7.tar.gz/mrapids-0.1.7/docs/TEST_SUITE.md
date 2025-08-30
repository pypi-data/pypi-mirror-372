# MicroRapid Run Command - Complete Test Suite

## Overview
This comprehensive test suite covers all functionality of the simplified `mrapids run` command, from basic initialization to complex real-world scenarios.

## Prerequisites
- MicroRapid CLI installed (`mrapids`)
- Internet connection (for Petstore API)
- Unix-like environment (Mac/Linux) or Git Bash on Windows

## Test Environment Setup

### Step 1: Initialize Project
```bash
# Create a test directory and initialize with Petstore API
mkdir mrapids-test && cd mrapids-test
mrapids init --from-url https://petstore.swagger.io/v2/swagger.json --force

# Verify initialization
ls -la
# Expected: specs/, requests/, data/, .mrapids/
```

### Step 2: Analyze API and Generate Request Configs
```bash
# Analyze all operations to generate request examples
mrapids analyze --all

# Check generated files
ls requests/examples/
# Expected: get-pet-by-id.yaml, find-pets-by-status.yaml, etc.

ls data/examples/
# Expected: new-pet.json, new-user.json, etc.
```

## Test Cases

### 1. Discovery and Listing Operations
```bash
# See all available operations
mrapids list operations

# Filter by method
mrapids list operations --method GET
mrapids list operations --method POST

# Filter by keyword
mrapids list operations --filter pet
mrapids list operations --filter user
mrapids list operations --filter store

# List in different formats
mrapids list operations --format json
mrapids list operations --format simple
mrapids list operations --format table
```

### 2. Basic GET Operations (Direct Execution)
```bash
# Get pet by ID (direct operation)
mrapids run getPetById --id 10
mrapids run getPetById --id 1
mrapids run getPetById --id 2

# Find pets by status
mrapids run findPetsByStatus --status available
mrapids run findPetsByStatus --status pending
mrapids run findPetsByStatus --status sold

# With pagination
mrapids run findPetsByStatus --status available --limit 5
mrapids run findPetsByStatus --status available --limit 10 --offset 5

# Get store inventory
mrapids run getInventory

# Get user
mrapids run getUserByName --name user1
mrapids run getUserByName --name johndoe
```

### 3. Request Config File Execution
```bash
# Run using generated config files
mrapids run requests/examples/get-pet-by-id.yaml
mrapids run requests/examples/find-pets-by-status.yaml
mrapids run requests/examples/get-inventory.yaml
mrapids run requests/examples/get-user-by-name.yaml

# Override parameters in config
mrapids run requests/examples/get-pet-by-id.yaml --id 20
mrapids run requests/examples/find-pets-by-status.yaml --status sold
```

### 4. POST Operations - Creating Resources
```bash
# Create a new pet using default example
mrapids run addPet

# Create pet with inline JSON
mrapids run addPet --data '{
  "id": 1001,
  "name": "Fluffy",
  "category": {"id": 1, "name": "Dogs"},
  "photoUrls": ["http://example.com/photo1.jpg"],
  "tags": [{"id": 1, "name": "friendly"}],
  "status": "available"
}'

# Create pet from file
mrapids run addPet --file data/examples/new-pet.json

# Create using @ syntax
mrapids run addPet --data @data/examples/new-pet.json

# Create a new user
mrapids run createUser --data '{
  "id": 1001,
  "username": "testuser",
  "firstName": "Test",
  "lastName": "User",
  "email": "test@example.com",
  "password": "password123",
  "phone": "555-0123",
  "userStatus": 1
}'

# Create store order
mrapids run placeOrder --data '{
  "id": 1001,
  "petId": 10,
  "quantity": 1,
  "shipDate": "2024-01-15T10:00:00.000Z",
  "status": "placed",
  "complete": true
}'
```

### 5. PUT Operations - Updating Resources
```bash
# Update existing pet
mrapids run updatePet --data '{
  "id": 10,
  "name": "Updated Fluffy",
  "category": {"id": 1, "name": "Dogs"},
  "photoUrls": ["http://example.com/photo2.jpg"],
  "tags": [{"id": 1, "name": "friendly"}, {"id": 2, "name": "trained"}],
  "status": "sold"
}'

# Update with form data
mrapids run updatePetWithForm --id 10 --name "New Name" --status sold

# Update user
mrapids run updateUser --name testuser --data '{
  "id": 1001,
  "username": "testuser",
  "firstName": "Updated",
  "lastName": "User",
  "email": "updated@example.com",
  "password": "newpassword",
  "phone": "555-9999",
  "userStatus": 1
}'
```

### 6. DELETE Operations
```bash
# Delete a pet
mrapids run deletePet --id 1001

# Delete with API key header
mrapids run deletePet --id 1001 --api-key "special-key"

# Delete order
mrapids run deleteOrder --id 1001

# Delete user
mrapids run deleteUser --name testuser
```

### 7. Advanced Options Testing

#### 7.1 Verbose and Dry Run
```bash
# Verbose mode (see all request details)
mrapids run getPetById --id 10 --verbose

# Dry run (don't actually send)
mrapids run getPetById --id 10 --dry-run
mrapids run addPet --data @data/examples/new-pet.json --dry-run

# Show as curl command
mrapids run getPetById --id 10 --as-curl
mrapids run addPet --data @data/examples/new-pet.json --as-curl

# Both curl and dry run
mrapids run getPetById --id 10 --as-curl --dry-run
```

#### 7.2 Output Formats
```bash
# JSON output
mrapids run findPetsByStatus --status available --output json

# YAML output
mrapids run findPetsByStatus --status available --output yaml

# Table output (for arrays)
mrapids run findPetsByStatus --status available --output table

# Pretty output (default)
mrapids run getPetById --id 10 --output pretty

# Save to file
mrapids run getPetById --id 10 --save pet-10.json
mrapids run findPetsByStatus --status available --save available-pets.json
```

### 8. Headers and Authentication
```bash
# Custom headers
mrapids run getPetById --id 10 --header "X-Request-ID: 12345"
mrapids run getPetById --id 10 --header "X-Custom: value1" --header "X-Another: value2"

# Authorization header
mrapids run getPetById --id 10 --auth "Bearer eyJhbGciOiJIUzI1NiIsInR..."

# API key header
mrapids run getPetById --id 10 --api-key "my-secret-api-key"

# Multiple auth methods
mrapids run deletePet --id 10 --api-key "key123" --header "X-Tenant: tenant1"
```

### 9. Error Handling and Retries
```bash
# Test with non-existent resource
mrapids run getPetById --id 99999

# Test with invalid data
mrapids run addPet --data '{"invalid": "data"}'

# Retry on failure
mrapids run getPetById --id 10 --retry 3

# Custom timeout
mrapids run getPetById --id 10 --timeout 5
mrapids run getPetById --id 10 --timeout 60
```

### 10. Complex Query Parameters
```bash
# Multiple query parameters
mrapids run findPetsByTags --param tags=friendly --param tags=trained

# Generic parameters
mrapids run findPetsByStatus --param status=available --param limit=5

# Mix of specific and generic
mrapids run findPetsByStatus --status available --limit 10 --param sort=name

# Query parameters explicitly
mrapids run findPetsByStatus --query status=available --query limit=5
```

### 11. Environment Configuration
```bash
# Create environment config
mkdir -p config
cat > config/environments.yaml << 'EOF'
environments:
  dev:
    base_url: http://localhost:8080/v2
  staging:
    base_url: https://staging-petstore.swagger.io/v2
  production:
    base_url: https://petstore.swagger.io/v2
EOF

# Test with different environments
mrapids run getPetById --id 10 --env dev
mrapids run getPetById --id 10 --env staging
mrapids run getPetById --id 10 --env production

# Override URL directly
mrapids run getPetById --id 10 --url https://petstore3.swagger.io/api/v3
```

### 12. Template System
```bash
# Create a template
mkdir -p templates
cat > templates/get-pet.yaml << 'EOF'
operation: getPetById
method: GET
path: /pet/${PET_ID:10}
headers:
  Accept: application/json
  X-Request-ID: ${REQUEST_ID:default-id}
EOF

# Use template
mrapids run my-request --template get-pet --set PET_ID=20 --set REQUEST_ID=req-123
```

### 13. Stdin Input Testing
```bash
# Pipe data through stdin
echo '{"id":8888,"name":"StdinPet","status":"available"}' | mrapids run addPet --stdin

# From file through stdin
cat data/examples/new-pet.json | mrapids run addPet --stdin
```

### 14. End-to-End Workflow Testing

#### 14.1 Simple Workflow
```bash
# Create a workflow script
cat > test-workflow.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting E2E Pet Store Workflow"

# 1. Create a pet
echo "Step 1: Creating pet..."
PET_ID=$(mrapids run addPet --data '{"id":9999,"name":"WorkflowPet","status":"available"}' --output json | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

# 2. Get the pet
echo "Step 2: Getting pet $PET_ID..."
mrapids run getPetById --id $PET_ID

# 3. Update pet status
echo "Step 3: Updating pet status..."
mrapids run updatePetWithForm --id $PET_ID --status sold

# 4. Find by status
echo "Step 4: Finding sold pets..."
mrapids run findPetsByStatus --status sold --limit 5

# 5. Delete the pet
echo "Step 5: Cleaning up - deleting pet..."
mrapids run deletePet --id $PET_ID

echo "✅ Workflow complete!"
EOF

chmod +x test-workflow.sh
./test-workflow.sh
```

#### 14.2 Complex Business Workflow
```bash
# Pet Store Business Workflow
cat > business-workflow.sh << 'EOF'
#!/bin/bash

echo "🏪 Pet Store Business Workflow"

# 1. Store opens - check inventory
echo "📦 Checking morning inventory..."
mrapids run getInventory --save morning-inventory.json

# 2. Add new pets to inventory
echo "🐕 Adding new pets..."
mrapids run addPet --data '{"id":2001,"name":"Rex","category":{"id":1,"name":"Dogs"},"status":"available"}'
mrapids run addPet --data '{"id":2002,"name":"Mittens","category":{"id":2,"name":"Cats"},"status":"available"}'

# 3. Customer searches for available pets
echo "🔍 Customer searching for pets..."
mrapids run findPetsByStatus --status available --output table

# 4. Customer creates account
echo "👤 Creating customer account..."
mrapids run createUser --data '{
  "id": 3001,
  "username": "customer1",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "secret",
  "phone": "555-1234",
  "userStatus": 1
}'

# 5. Customer places order
echo "🛒 Placing order..."
mrapids run placeOrder --data '{
  "id": 4001,
  "petId": 2001,
  "quantity": 1,
  "shipDate": "2024-01-20T10:00:00.000Z",
  "status": "placed",
  "complete": false
}'

# 6. Update pet status to sold
echo "💰 Marking pet as sold..."
mrapids run updatePetWithForm --id 2001 --status sold

# 7. Check end of day inventory
echo "📊 End of day inventory check..."
mrapids run getInventory --save evening-inventory.json

echo "✅ Business workflow complete!"
EOF

chmod +x business-workflow.sh
./business-workflow.sh
```

### 15. Error Scenarios and Edge Cases
```bash
# Missing required parameter
mrapids run getPetById
# Expected: Error about missing --id

# Invalid operation name
mrapids run nonExistentOperation
# Expected: List of available operations

# Malformed JSON
mrapids run addPet --data '{"broken": json'
# Expected: JSON parse error

# File not found
mrapids run addPet --file non-existent-file.json
# Expected: File not found error

# Invalid status value
mrapids run findPetsByStatus --status invalid_status
# Expected: API error or empty result

# GET request with body (should be ignored)
mrapids run getPetById --id 10 --data '{"test":"data"}'
# Expected: Body ignored for GET request
```

### 16. Performance Testing
```bash
# Test with large result sets
mrapids run findPetsByStatus --status available --limit 100

# Test timeout handling
mrapids run getPetById --id 10 --timeout 1

# Test retry mechanism
mrapids run getPetById --id 10 --retry 3 --timeout 2
```

### 17. Cleanup Operations
```bash
# List what would be cleaned
mrapids cleanup --dry-run

# Clean test artifacts
mrapids cleanup --test-artifacts

# Clean backup directories
mrapids cleanup --backups

# Clean empty directories
mrapids cleanup --empty-dirs

# Clean everything
mrapids cleanup --test-artifacts --backups --empty-dirs
```

## Automated Test Scripts

### Quick Smoke Test
```bash
cat > smoke-test.sh << 'EOF'
#!/bin/bash
set -e

echo "🧪 Running MicroRapid Smoke Tests"

# Test basic GET
echo "Test 1: Basic GET..."
mrapids run getPetById --id 10 --dry-run

# Test with parameters
echo "Test 2: Query parameters..."
mrapids run findPetsByStatus --status available --limit 3 --dry-run

# Test config file
echo "Test 3: Config file..."
mrapids run requests/examples/get-pet-by-id.yaml --dry-run

# Test output formats
echo "Test 4: Output formats..."
mrapids run getInventory --output json --dry-run

echo "✅ Smoke tests passed!"
EOF

chmod +x smoke-test.sh
./smoke-test.sh
```

### Full Test Suite
```bash
cat > full-test.sh << 'EOF'
#!/bin/bash

PASS=0
FAIL=0

run_test() {
    echo -n "Testing: $1... "
    if $2 > /dev/null 2>&1; then
        echo "✅ PASS"
        ((PASS++))
    else
        echo "❌ FAIL"
        ((FAIL++))
    fi
}

echo "🧪 MicroRapid Comprehensive Test Suite"
echo "======================================"

# Basic Operations
run_test "GET by ID" "mrapids run getPetById --id 10 --dry-run"
run_test "GET with query" "mrapids run findPetsByStatus --status available --dry-run"
run_test "GET inventory" "mrapids run getInventory --dry-run"

# POST Operations
run_test "POST with data" "mrapids run addPet --dry-run --as-curl"

# Config Files
run_test "Config file execution" "mrapids run requests/examples/get-pet-by-id.yaml --dry-run"

# Output Formats
run_test "JSON output" "mrapids run getPetById --id 10 --output json --dry-run"
run_test "YAML output" "mrapids run getPetById --id 10 --output yaml --dry-run"

# Advanced Options
run_test "Verbose mode" "mrapids run getPetById --id 10 --verbose --dry-run"
run_test "Curl output" "mrapids run getPetById --id 10 --as-curl --dry-run"

# Headers
run_test "Custom headers" "mrapids run getPetById --id 10 --header 'X-Test: value' --dry-run"
run_test "Auth header" "mrapids run getPetById --id 10 --auth 'Bearer token' --dry-run"

echo "======================================"
echo "Results: $PASS passed, $FAIL failed"

if [ $FAIL -eq 0 ]; then
    echo "✅ All tests passed!"
    exit 0
else
    echo "❌ Some tests failed"
    exit 1
fi
EOF

chmod +x full-test.sh
./full-test.sh
```

## Validation Checklist

### Core Functionality
- [ ] Direct operation execution works
- [ ] Request config file execution works
- [ ] Parameter substitution works correctly
- [ ] Path parameters are mapped correctly
- [ ] Query parameters are added properly
- [ ] Request bodies are handled correctly

### Input Methods
- [ ] Inline JSON data works
- [ ] File input with --file works
- [ ] @ syntax for files works
- [ ] Stdin input works
- [ ] Default examples load correctly

### Output Options
- [ ] JSON format displays correctly
- [ ] YAML format displays correctly
- [ ] Table format works for arrays
- [ ] Pretty format (default) works
- [ ] Save to file works

### Advanced Features
- [ ] Verbose mode shows details
- [ ] Dry run prevents execution
- [ ] Curl command generation works
- [ ] Retry mechanism works
- [ ] Timeout is respected
- [ ] Custom headers are sent
- [ ] Authentication headers work

### Error Handling
- [ ] Missing parameters show helpful errors
- [ ] Invalid operations list alternatives
- [ ] File not found errors are clear
- [ ] Network errors are handled gracefully
- [ ] JSON parse errors are informative

## Expected Results

### Successful Test Indicators
1. All GET operations return data
2. POST operations create resources (or show correct curl in dry-run)
3. Config files execute without errors
4. Output formats render correctly
5. Error messages are helpful and clear

### Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "Operation not found" | Check operation name matches exactly |
| "Missing required parameter" | Add --id or other required params |
| "File not found" | Ensure file path is correct |
| "Connection refused" | Check API endpoint is accessible |
| "Invalid JSON" | Validate JSON syntax |

## Performance Benchmarks

Expected response times:
- Simple GET: < 1 second
- Complex query: < 2 seconds
- Large result set: < 5 seconds
- With retries: < timeout × (retry + 1)

## Conclusion

This test suite covers:
- ✅ All HTTP methods (GET, POST, PUT, DELETE)
- ✅ All input methods (inline, file, stdin)
- ✅ All output formats (json, yaml, table, pretty)
- ✅ Authentication methods
- ✅ Error scenarios
- ✅ Advanced features (retry, timeout, dry-run)
- ✅ Real-world workflows

Run the automated test scripts to validate your MicroRapid installation is working correctly.