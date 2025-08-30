# Agent CLI - Comprehensive Test Cases

## 🧪 Test Suite Overview

This document contains all test cases for the Agent CLI, organized by feature and priority.

---

## 1. Core CLI Tests

### 1.1 Banner & Branding Tests

#### TC-001: Agent Banner Display
```bash
# Test Case: Verify agent automation banner displays correctly
mrapids

# Expected Output:
# - Robot face ASCII art with "agent automation" theme
# - Status showing [READY] 100%
# - "Your OpenAPI, but executable" tagline
```

#### TC-002: Help Banner
```bash
# Test Case: Verify help command shows banner
mrapids --help

# Expected Output:
# - Agent automation banner at top
# - Complete command list
# - Global options listed
```

#### TC-003: Version Display
```bash
# Test Case: Verify version information
mrapids --version

# Expected Output:
# - Agent banner
# - Version: 0.1.0
# - Build: release
# - Homepage URL
```

### 1.2 Global Options Tests

#### TC-004: Verbose Mode
```bash
# Test Case: Enable verbose output
mrapids --verbose validate specs/api.yaml

# Expected Output:
# - Detailed validation process
# - Additional debug information
```

#### TC-005: Quiet Mode
```bash
# Test Case: Suppress output except errors
mrapids --quiet validate specs/api.yaml

# Expected Output:
# - No output if successful
# - Only errors shown if validation fails
```

#### TC-006: No Color Mode
```bash
# Test Case: Disable colored output
mrapids --no-color list operations specs/api.yaml

# Expected Output:
# - Plain text without ANSI color codes
```

#### TC-007: Environment Override
```bash
# Test Case: Set global environment
mrapids --env production run getUser

# Expected Output:
# - Uses production environment configuration
```

---

## 2. Project Management Tests

### 2.1 Init Command Tests

#### TC-008: Basic Project Init
```bash
# Test Case: Initialize new project
mrapids init my-api-project

# Expected Output:
# - Creates directory structure
# - Copies template files
# - Initializes git repository
```

#### TC-009: Init from URL
```bash
# Test Case: Initialize from remote spec
mrapids init --from-url https://api.github.com/openapi.json github-project

# Expected Output:
# - Downloads OpenAPI spec
# - Creates project structure
# - Saves spec as specs/api.yaml
```

#### TC-010: Force Overwrite
```bash
# Test Case: Force overwrite existing project
mrapids init existing-project --force

# Expected Output:
# - Overwrites existing files
# - Backs up previous content
```

---

## 3. Validation System Tests

### 3.1 Basic Validation

#### TC-011: Valid Spec Validation
```bash
# Test Case: Validate correct OpenAPI spec
mrapids validate specs/valid-openapi.yaml

# Expected Output:
# ✅ Specification is valid!
# - Shows spec version
# - Duration in ms
```

#### TC-012: Invalid Spec Detection
```bash
# Test Case: Validate spec with errors
mrapids validate specs/invalid-refs.yaml

# Expected Errors:
# - Undefined reference: #/components/schemas/NonExistent
# - Missing required fields
```

### 3.2 Validation Levels

#### TC-013: Strict Mode Validation
```bash
# Test Case: Treat warnings as errors
mrapids validate --strict specs/with-warnings.yaml

# Expected Output:
# - Warnings treated as errors
# - Non-zero exit code
```

#### TC-014: Lint Mode Validation
```bash
# Test Case: Full validation with best practices
mrapids validate --lint specs/api.yaml

# Expected Checks:
# - Missing descriptions
# - Naming conventions
# - Security warnings
# - Unused components
```

#### TC-015: JSON Output Format
```bash
# Test Case: Machine-readable validation output
mrapids validate --format json specs/api.yaml

# Expected Output:
{
  "valid": true,
  "version": "OpenAPI 3.0.0",
  "errors": [],
  "warnings": [],
  "duration_ms": 50
}
```

---

## 4. API Operations Tests

### 4.1 List Operations

#### TC-016: List All Operations
```bash
# Test Case: Display all API operations
mrapids list operations specs/github.yaml

# Expected Output:
# - Table with operation ID, method, path
# - Total count displayed
# - Usage instructions
```

#### TC-017: Filter by Method
```bash
# Test Case: Filter operations by HTTP method
mrapids list operations specs/api.yaml --method GET

# Expected Output:
# - Only GET operations shown
```

#### TC-018: JSON Output Format
```bash
# Test Case: List operations as JSON
mrapids list operations specs/api.yaml --format json

# Expected Output:
[
  {
    "operationId": "getUser",
    "method": "GET",
    "path": "/users/{id}"
  }
]
```

### 4.2 Show Operation Details

#### TC-019: Basic Operation Details
```bash
# Test Case: Show operation information
mrapids show getUser specs/api.yaml

# Expected Output:
# - HTTP method and path
# - Parameters with types
# - Request/response schemas
# - Authentication requirements
```

#### TC-020: Show with Examples
```bash
# Test Case: Include example requests
mrapids show createUser specs/api.yaml --examples

# Expected Output:
# - Operation details
# - Example request body
# - Example response
```

### 4.3 Run Operations

#### TC-021: Dry Run Execution
```bash
# Test Case: Preview request without sending
mrapids run getUser --param id=123 --dry-run

# Expected Output:
# - Shows generated request
# - Headers and body displayed
# - No actual HTTP call made
```

#### TC-022: Execute with Parameters
```bash
# Test Case: Run operation with parameters
mrapids run getUser --param username=octocat

# Expected Output:
# - Executes HTTP request
# - Shows response status
# - Displays response body
```

#### TC-023: POST with Request Body
```bash
# Test Case: Execute POST with JSON data
mrapids run createRepo --data '{"name":"test-repo","private":true}'

# Expected Output:
# - Sends POST request
# - Shows created resource
```

---

## 5. Search & Discovery Tests

### 5.1 Explore Command

#### TC-024: Basic Keyword Search
```bash
# Test Case: Search operations by keyword
mrapids explore "user"

# Expected Output:
# - Exact matches first
# - Related operations
# - Fuzzy matches
```

#### TC-025: Detailed Search Results
```bash
# Test Case: Show detailed descriptions
mrapids explore "payment" --detailed

# Expected Output:
# - Operation summaries
# - Full descriptions
# - Parameter details
```

#### TC-026: Limited Results
```bash
# Test Case: Limit search results
mrapids explore "create" --limit 3

# Expected Output:
# - Maximum 3 results per category
```

---

## 6. Code Generation Tests

### 6.1 SDK Generation

#### TC-027: TypeScript SDK
```bash
# Test Case: Generate TypeScript client
mrapids gen sdk --language typescript --output ./sdk-ts specs/api.yaml

# Expected Files:
# - client.ts (API client class)
# - models.ts (TypeScript interfaces)
# - types.ts (Common types)
# - package.json (NPM configuration)
# - README.md (Usage documentation)
```

#### TC-028: Python SDK
```bash
# Test Case: Generate Python client
mrapids gen sdk --language python --output ./sdk-py specs/api.yaml

# Expected Files:
# - client.py (API client)
# - models.py (Pydantic models)
# - __init__.py (Package init)
# - requirements.txt (Dependencies)
# - setup.py (Package setup)
```

#### TC-029: Go SDK
```bash
# Test Case: Generate Go client
mrapids gen sdk --language go --output ./sdk-go specs/api.yaml

# Expected Files:
# - client.go (API client)
# - models.go (Struct definitions)
# - types.go (Common types)
# - go.mod (Module definition)
```

#### TC-030: Rust SDK
```bash
# Test Case: Generate Rust client
mrapids gen sdk --language rust --output ./sdk-rust specs/api.yaml

# Expected Files:
# - lib.rs (Library root)
# - client.rs (API client)
# - models.rs (Struct definitions)
# - Cargo.toml (Package manifest)
```

### 6.2 Server Stubs Generation

#### TC-031: Express.js Server
```bash
# Test Case: Generate Express server stubs
mrapids gen stubs --framework express --output ./server specs/api.yaml

# Expected Files:
# - app.js (Express application)
# - routes/*.js (Route handlers)
# - middleware/*.js (Validation middleware)
# - package.json (Dependencies)
```

#### TC-032: FastAPI Server
```bash
# Test Case: Generate FastAPI server stubs
mrapids gen stubs --framework fastapi --output ./server specs/api.yaml

# Expected Files:
# - main.py (FastAPI application)
# - routers/*.py (Route modules)
# - models/*.py (Pydantic models)
# - requirements.txt (Dependencies)
```

### 6.3 Examples Generation

#### TC-033: Generate Request Snippets
```bash
# Test Case: Generate example requests
mrapids gen snippets --output ./examples specs/api.yaml

# Expected Output:
# - JSON request examples
# - Response examples
# - Parameter examples
```

#### TC-034: cURL Command Generation
```bash
# Test Case: Generate cURL commands
mrapids gen snippets --format curl specs/api.yaml

# Expected Output:
# - cURL commands for each operation
# - Proper headers and authentication
```

---

## 7. Collections Framework Tests

### 7.1 Collection Management

#### TC-035: List Collections
```bash
# Test Case: Display available collections
mrapids collection list

# Expected Output:
# - List of collection names
# - Brief descriptions
# - Collection count
```

#### TC-036: Show Collection Details
```bash
# Test Case: Display collection information
mrapids collection show github-test

# Expected Output:
# - Collection name and description
# - Request list with dependencies
# - Variables used
```

#### TC-037: Validate Collection
```bash
# Test Case: Check collection syntax
mrapids collection validate test-suite

# Expected Output:
# - Syntax validation results
# - Operation ID verification
# - Variable usage check
```

### 7.2 Collection Execution

#### TC-038: Run Collection
```bash
# Test Case: Execute collection requests
mrapids collection run smoke-tests

# Expected Output:
# - Sequential request execution
# - Response status for each
# - Variable interpolation
```

#### TC-039: Run with Variables
```bash
# Test Case: Override collection variables
mrapids collection run api-tests --var base_url=https://api.staging.com --var api_key=$API_KEY

# Expected Output:
# - Uses provided variables
# - Successful execution
```

#### TC-040: Test Collection
```bash
# Test Case: Run collection as tests
mrapids collection test integration-tests

# Expected Output:
# - Assertion results
# - Pass/fail status
# - Test summary
```

---

## 8. Authentication Tests

### 8.1 OAuth Flow

#### TC-041: GitHub Login
```bash
# Test Case: OAuth login for GitHub
mrapids auth login github --scopes "repo read:user"

# Expected Output:
# - Opens browser for OAuth
# - Saves tokens securely
# - Shows success message
```

#### TC-042: Custom OAuth Provider
```bash
# Test Case: Configure custom OAuth
mrapids auth login custom \
  --auth-url https://auth.example.com/oauth/authorize \
  --token-url https://auth.example.com/oauth/token \
  --client-id $CLIENT_ID

# Expected Output:
# - Custom OAuth flow initiated
# - Tokens saved to profile
```

### 8.2 Profile Management

#### TC-043: List Auth Profiles
```bash
# Test Case: Show saved auth profiles
mrapids auth list

# Expected Output:
# - Profile names
# - Provider types
# - Last used dates
```

#### TC-044: Test Authentication
```bash
# Test Case: Verify auth token works
mrapids auth test github

# Expected Output:
# - Makes test API call
# - Shows authenticated user
# - Confirms token validity
```

---

## 9. Error Handling Tests

### 9.1 Invalid Input Handling

#### TC-045: Invalid Command
```bash
# Test Case: Handle unknown command
mrapids invalid-command

# Expected Output:
# - Error message
# - Suggested commands
# - Help instructions
```

#### TC-046: Missing Required Arguments
```bash
# Test Case: Handle missing arguments
mrapids validate

# Expected Output:
# - Error: missing required argument 'spec'
# - Usage information
```

### 9.2 File Error Handling

#### TC-047: Missing File
```bash
# Test Case: Handle non-existent file
mrapids validate /path/to/missing.yaml

# Expected Output:
# - Error: No such file or directory
# - Clear error message
```

#### TC-048: Invalid YAML/JSON
```bash
# Test Case: Handle malformed spec
mrapids validate specs/malformed.yaml

# Expected Output:
# - Parse error details
# - Line number if available
```

---

## 10. Integration Tests

### 10.1 End-to-End Workflows

#### TC-049: Complete Project Setup
```bash
# Test Case: Full project initialization workflow
# 1. Initialize project
mrapids init e2e-test --from-url https://api.example.com/openapi.json

# 2. Validate the spec
mrapids validate specs/api.yaml --strict

# 3. Generate SDK
mrapids gen sdk --language typescript --output ./sdk

# 4. Create test collection
mrapids collection validate integration-tests

# Expected: All steps complete successfully
```

#### TC-050: API Development Workflow
```bash
# Test Case: Complete API development cycle
# 1. Explore available operations
mrapids explore "user" --detailed

# 2. Show specific operation
mrapids show createUser --examples

# 3. Test the operation
mrapids run createUser --dry-run

# 4. Generate client code
mrapids gen snippets --operation createUser

# Expected: Smooth workflow completion
```

---

## 11. Performance Tests

### 11.1 Large Spec Handling

#### TC-051: Large OpenAPI Spec
```bash
# Test Case: Process spec with 1000+ operations
mrapids validate specs/large-api.yaml

# Expected Performance:
# - Completes in < 5 seconds
# - Memory usage < 500MB
```

#### TC-052: Bulk Operations
```bash
# Test Case: List many operations efficiently
mrapids list operations specs/enterprise-api.yaml

# Expected Performance:
# - Renders 500+ operations smoothly
# - Pagination if needed
```

---

## 12. Security Tests

### 12.1 Input Validation

#### TC-053: Path Traversal Prevention
```bash
# Test Case: Prevent directory traversal
mrapids validate ../../../etc/passwd

# Expected Output:
# - Error: Invalid file path
# - Security warning
```

#### TC-054: URL Validation
```bash
# Test Case: Validate remote URLs
mrapids init --from-url javascript:alert(1)

# Expected Output:
# - Error: Invalid URL scheme
# - Only HTTP/HTTPS allowed
```

### 12.2 Credential Security

#### TC-055: Token Masking
```bash
# Test Case: Ensure tokens are masked
mrapids auth show github --show-tokens

# Expected Output:
# - Tokens partially masked
# - Security warning displayed
```

---

## 📊 Test Execution Matrix

| Priority | Test Categories | Test Count | Coverage |
|----------|----------------|------------|----------|
| 🔴 Critical | Core CLI, Validation, Operations | 25 | 100% |
| 🟡 High | Generation, Collections, Auth | 20 | 100% |
| 🟢 Medium | Search, Error Handling | 8 | 100% |
| 🔵 Low | Performance, Security | 5 | 80% |

## 🎯 Test Automation

### Automated Test Script
```bash
#!/bin/bash
# Run all test cases automatically

# Core Tests
./test_core_cli.sh

# Feature Tests  
./test_validation.sh
./test_operations.sh
./test_generation.sh
./test_collections.sh
./test_auth.sh

# Integration Tests
./test_workflows.sh

# Performance Tests
./test_performance.sh

# Generate Report
./generate_test_report.sh
```

## 📈 Success Criteria

- ✅ All critical tests must pass
- ✅ 95% of high priority tests must pass
- ✅ 90% of medium priority tests must pass
- ✅ No security vulnerabilities
- ✅ Performance within acceptable limits
- ✅ User experience is smooth and intuitive