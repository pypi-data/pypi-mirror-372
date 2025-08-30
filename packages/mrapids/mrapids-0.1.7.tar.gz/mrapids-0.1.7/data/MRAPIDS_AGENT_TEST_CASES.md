# MRAPIDS Agent - Comprehensive Test Cases Based on Code Review

## 🔍 Deep Code Analysis Summary

Based on thorough code review, MRAPIDS is an advanced OpenAPI automation CLI with:
- **Agent automation** theme with robot branding
- **Collections framework** for workflow automation
- **Multi-language SDK generation** (TypeScript, Python, Go, Rust)
- **Advanced validation system** with 3 levels
- **Smart error handling** with specific exit codes
- **OAuth authentication** support
- **Request templating** and variable interpolation

---

## 📋 Test Cases by Feature

### 1. CLI Core & Exit Codes (main.rs)

#### TC-CORE-001: No Arguments Banner Display
```bash
# Test: Display agent banner when no args provided
mrapids

# Expected:
# - Agent automation banner with robot face
# - "Your OpenAPI, but executable" tagline
# - Quick start examples
# - Exit code: 0
```

#### TC-CORE-002: Version Flag Early Check
```bash
# Test: Version flag bypasses arg parsing
mrapids --version
mrapids -V

# Expected:
# - Banner with version info
# - Build: release
# - Homepage URL
# - Exit code: 0
```

#### TC-CORE-003: Invalid Command Error
```bash
# Test: Invalid command returns usage error
mrapids invalid-command

# Expected:
# - Error message with suggestions
# - Exit code: 2 (EXIT_USAGE_ERROR)
```

#### TC-CORE-004: Network Error Exit Code
```bash
# Test: Network errors return specific code
mrapids run getUser --url https://invalid.local

# Expected:
# - Network error message
# - Exit code: 4 (EXIT_NETWORK_ERROR)
```

#### TC-CORE-005: Auth Error Exit Code
```bash
# Test: Authentication errors return auth code
mrapids run getUser --auth "invalid-token"

# Expected:
# - Authentication error message
# - Exit code: 3 (EXIT_AUTH_ERROR)
```

#### TC-CORE-006: Validation Error Exit Code
```bash
# Test: Validation errors return validation code
mrapids validate invalid-spec.yaml

# Expected:
# - Validation error details
# - Exit code: 7 (EXIT_VALIDATION_ERROR)
```

### 2. Global Options Environment Variables

#### TC-ENV-001: Verbose Mode Environment
```bash
# Test: Verbose flag sets environment variable
mrapids --verbose validate spec.yaml

# Verify:
# - MRAPIDS_VERBOSE=true in environment
# - Additional debug output shown
```

#### TC-ENV-002: Trace Mode Environment
```bash
# Test: Trace flag sets trace environment
mrapids --trace run getUser

# Verify:
# - MRAPIDS_TRACE=true in environment
# - HTTP request/response details shown
```

#### TC-ENV-003: Quiet Mode Environment
```bash
# Test: Quiet flag suppresses output
mrapids --quiet validate spec.yaml

# Verify:
# - MRAPIDS_QUIET=true in environment
# - Only errors shown
```

#### TC-ENV-004: No Color Mode
```bash
# Test: No color flag disables ANSI colors
mrapids --no-color list operations spec.yaml

# Verify:
# - colored::control::set_override(false) called
# - No ANSI color codes in output
```

#### TC-ENV-005: Global Environment Setting
```bash
# Test: Global env flag sets MRAPIDS_ENV
mrapids --env production run getUser

# Verify:
# - MRAPIDS_ENV=production in environment
# - Production config loaded
```

### 3. Run Command v2 Implementation

#### TC-RUN-001: Direct Operation Execution
```bash
# Test: Run operation by name with partial matching
mrapids run getUser --param id=123

# Expected:
# - Finds spec in project (specs/api.yaml)
# - Partial matching finds "getUser" operation
# - Executes HTTP request
```

#### TC-RUN-002: Request Config File Execution
```bash
# Test: Run from request config file
mrapids run requests/get-user.yaml

# Expected:
# - Loads request config from file
# - Executes with saved parameters
```

#### TC-RUN-003: Template Execution
```bash
# Test: Run with template
mrapids run getUser --template user-fetch --set id=123

# Expected:
# - Loads template file
# - Variable interpolation
# - Executes templated request
```

#### TC-RUN-004: Deprecated Spec Execution
```bash
# Test: Direct spec file execution (deprecated)
mrapids run api-spec.yaml

# Expected:
# - Error: "Direct spec execution is deprecated"
# - Suggests using operation names
```

#### TC-RUN-005: Data File Handling
```bash
# Test: Load request body from file
mrapids run createUser --file user-data.json

# Expected:
# - Reads file content
# - Sets as request body
# - Sends POST request
```

### 4. Validation System (3 Levels)

#### TC-VAL-001: Quick Validation
```bash
# Test: Basic structural validation
mrapids validate spec.yaml

# Expected:
# - Level: quick
# - Basic structure checks only
# - Fast execution (<100ms)
```

#### TC-VAL-002: Standard Validation (--strict)
```bash
# Test: Comprehensive validation
mrapids validate --strict spec.yaml

# Expected:
# - Levels: quick + standard
# - Reference validation
# - Operation ID uniqueness
# - Schema type constraints
```

#### TC-VAL-003: Full Validation (--lint)
```bash
# Test: Complete validation with linting
mrapids validate --lint spec.yaml

# Expected:
# - Levels: quick + standard + security + lint
# - Missing descriptions warnings
# - Security best practices
# - Naming conventions
```

#### TC-VAL-004: JSON Output Format
```bash
# Test: Machine-readable validation output
mrapids validate --format json spec.yaml

# Expected JSON:
{
  "valid": true,
  "version": "OpenAPI 3.0.0",
  "errors": [],
  "warnings": [],
  "duration_ms": 50
}
```

#### TC-VAL-005: Malformed YAML Detection
```bash
# Test: Parse error handling
mrapids validate malformed.yaml

# Expected:
# - "Failed to parse OpenAPI specification"
# - Exit code: 7
```

### 5. Collections Framework

#### TC-COLL-001: List Collections
```bash
# Test: Display available collections
mrapids collection list

# Expected:
# - Lists all .yaml files in .mrapids/collections
# - Shows collection names
```

#### TC-COLL-002: Show Collection Details
```bash
# Test: Display collection info
mrapids collection show github-test

# Expected:
# - Collection name and description
# - Request list with operation IDs
# - Variables defined
# - Dependencies shown
```

#### TC-COLL-003: Validate Collection
```bash
# Test: Check collection syntax
mrapids collection validate test-suite

# Expected:
# - Parses collection YAML
# - Validates request structure
# - Checks operation references
```

#### TC-COLL-004: Run Collection
```bash
# Test: Execute collection requests
mrapids collection run smoke-tests

# Expected:
# - Sequential request execution
# - Variable interpolation
# - Dependency resolution
# - Response saving
```

#### TC-COLL-005: Collection with Variables
```bash
# Test: Override collection variables
mrapids collection run api-tests \
  --var base_url=https://staging.api.com \
  --var api_key=$API_KEY

# Expected:
# - Variables replaced in requests
# - Environment variables used
```

#### TC-COLL-006: Collection Dependencies
```bash
# Test: Request dependency handling
# Collection has: request2 depends on request1
mrapids collection run dependency-test

# Expected:
# - request1 executes first
# - request2 waits for request1 success
# - Saved responses available
```

#### TC-COLL-007: Critical Request Failure
```bash
# Test: Critical request stops collection
# Collection has: critical: true on request
mrapids collection run critical-test

# Expected:
# - Stops on critical request failure
# - Cleanup requests still run (run_always: true)
```

#### TC-COLL-008: Conditional Execution
```bash
# Test: if/skip conditions
# Collection has: if: "response.status == 200"
mrapids collection run conditional-test

# Expected:
# - Evaluates conditions
# - Skips requests when condition false
```

#### TC-COLL-009: Retry Configuration
```bash
# Test: Retry failed requests
# Collection has: retry: {attempts: 3, delay: 1000}
mrapids collection run retry-test

# Expected:
# - Retries failed requests
# - Exponential/linear backoff
# - Max 3 attempts
```

#### TC-COLL-010: Test Mode Assertions
```bash
# Test: Run collection as tests
mrapids collection test integration-suite

# Expected:
# - Executes assertions
# - Reports pass/fail
# - Test summary shown
```

### 6. SDK Generation

#### TC-SDK-001: TypeScript SDK Generation
```bash
# Test: Generate TypeScript client
mrapids gen sdk --language typescript \
  --output ./sdk-ts \
  --package my-api-client \
  specs/api.yaml

# Expected Files:
# - client.ts (API client class)
# - models.ts (TypeScript interfaces)
# - types.ts (Common types)
# - package.json (name: "my-api-client")
# - README.md
```

#### TC-SDK-002: Python SDK Generation
```bash
# Test: Generate Python client
mrapids gen sdk --language python \
  --output ./sdk-py \
  --package my_api_client \
  specs/api.yaml

# Expected Files:
# - client.py (API client)
# - models.py (Pydantic models)
# - __init__.py
# - requirements.txt
# - setup.py (name="my_api_client")
```

#### TC-SDK-003: Go SDK Generation
```bash
# Test: Generate Go client
mrapids gen sdk --language go \
  --output ./sdk-go \
  --package myapi \
  specs/api.yaml

# Expected Files:
# - client.go
# - models.go
# - types.go
# - go.mod (module myapi)
```

#### TC-SDK-004: Rust SDK Generation
```bash
# Test: Generate Rust client
mrapids gen sdk --language rust \
  --output ./sdk-rust \
  --package my-api-client \
  specs/api.yaml

# Expected Files:
# - Cargo.toml (name = "my-api-client")
# - src/lib.rs
# - src/client.rs
# - src/models.rs
```

#### TC-SDK-005: SDK with Docs and Examples
```bash
# Test: Include documentation and examples
mrapids gen sdk --language typescript \
  --docs --examples \
  specs/api.yaml

# Expected:
# - Inline documentation in code
# - Example usage in README
# - Test examples included
```

### 7. Server Stub Generation

#### TC-STUB-001: Express.js Stubs
```bash
# Test: Generate Express server
mrapids gen stubs --framework express \
  --output ./server \
  --with-validation \
  specs/api.yaml

# Expected:
# - Express app with routes
# - Request validation middleware
# - Error handlers
```

#### TC-STUB-002: FastAPI Stubs
```bash
# Test: Generate FastAPI server
mrapids gen stubs --framework fastapi \
  --output ./server \
  --with-tests \
  specs/api.yaml

# Expected:
# - FastAPI app with routers
# - Pydantic models
# - Test files included
```

#### TC-STUB-003: Gin Framework Stubs
```bash
# Test: Generate Gin server
mrapids gen stubs --framework gin \
  --output ./server \
  specs/api.yaml

# Expected:
# - Gin router setup
# - Handler functions
# - Middleware chain
```

### 8. Authentication System

#### TC-AUTH-001: OAuth Login Flow
```bash
# Test: GitHub OAuth login
mrapids auth login github \
  --scopes "repo read:user" \
  --profile work-github

# Expected:
# - Opens browser for OAuth
# - Receives callback
# - Stores encrypted tokens
```

#### TC-AUTH-002: Custom OAuth Provider
```bash
# Test: Custom OAuth configuration
mrapids auth login custom \
  --client-id $CLIENT_ID \
  --client-secret $CLIENT_SECRET \
  --auth-url https://auth.example.com/oauth/authorize \
  --token-url https://auth.example.com/oauth/token \
  --scopes "api:read api:write"

# Expected:
# - Custom OAuth flow
# - Token storage
```

#### TC-AUTH-003: List Auth Profiles
```bash
# Test: Show stored profiles
mrapids auth list --detailed

# Expected:
# - Profile names
# - Provider types
# - Token expiry info
# - Last used dates
```

#### TC-AUTH-004: Refresh Tokens
```bash
# Test: Refresh expired tokens
mrapids auth refresh github

# Expected:
# - Uses refresh token
# - Updates access token
# - Updates token store
```

#### TC-AUTH-005: Test Authentication
```bash
# Test: Verify auth works
mrapids auth test github

# Expected:
# - Makes test API call
# - Shows authenticated user
# - Confirms token validity
```

### 9. Advanced Features

#### TC-ADV-001: Operation Partial Matching
```bash
# Test: Find operation by partial name
mrapids show balance  # matches "getAccountBalance"

# Expected:
# - Fuzzy matching algorithm
# - Shows matching operation
```

#### TC-ADV-002: Smart Example Generation
```bash
# Test: Generate examples based on field names
mrapids gen snippets --operation createUser

# Expected:
# - email: "user@example.com"
# - phone: "+1-555-0123"
# - age: 25
# - Smart data based on field names
```

#### TC-ADV-003: Environment Config Loading
```bash
# Test: Load environment-specific config
MRAPIDS_ENV=production mrapids run getUser

# Expected:
# - Loads config/production.yaml
# - Uses production base URL
# - Applies auth from config
```

#### TC-ADV-004: Request Warnings
```bash
# Test: Security warnings for sensitive data
mrapids run login --data '{"password":"secret"}'

# Expected:
# - Warning about password in request
# - Suggests using --file or stdin
# - Unless --no-warnings flag
```

#### TC-ADV-005: Template Variable Interpolation
```bash
# Test: Complex variable substitution
mrapids run getUser \
  --template user-fetch \
  --set id={{user_id}} \
  --set format=json

# Expected:
# - Handlebars template processing
# - Variable replacement
# - Nested variable support
```

### 10. Error Handling & Edge Cases

#### TC-ERR-001: Missing Spec File
```bash
# Test: Handle missing API spec
rm specs/api.yaml
mrapids run getUser

# Expected:
# - Error: Cannot find API spec
# - Suggests creating spec file
```

#### TC-ERR-002: Circular Dependencies
```bash
# Test: Detect circular collection dependencies
# Collection has: A→B→C→A
mrapids collection run circular-test

# Expected:
# - Error: Circular dependency detected
# - Shows dependency chain
```

#### TC-ERR-003: Rate Limit Handling
```bash
# Test: 429 response handling
# API returns 429 Too Many Requests
mrapids run getUser

# Expected:
# - Rate limit error message
# - Exit code: 5 (EXIT_RATE_LIMIT_ERROR)
# - Retry-After header respected
```

#### TC-ERR-004: Invalid Collection YAML
```bash
# Test: Malformed collection file
echo "invalid: yaml: here:" > test.yaml
mrapids collection validate test

# Expected:
# - YAML parse error
# - Line number shown
# - Helpful error message
```

#### TC-ERR-005: Operation Not Found
```bash
# Test: Non-existent operation
mrapids run nonExistentOperation

# Expected:
# - Error: No operation found
# - Suggests similar operations
# - Lists available operations
```

---

## 🧪 Test Execution Strategy

### Priority 1: Critical Path Tests
1. Basic CLI functionality (TC-CORE-*)
2. Core operations (TC-RUN-*)
3. Validation system (TC-VAL-*)

### Priority 2: Feature Tests
1. Collections framework (TC-COLL-*)
2. SDK generation (TC-SDK-*)
3. Authentication (TC-AUTH-*)

### Priority 3: Advanced Tests
1. Advanced features (TC-ADV-*)
2. Error handling (TC-ERR-*)
3. Edge cases

### Test Environment Setup
```bash
# Create test structure
mkdir -p specs .mrapids/collections config
echo 'openapi: 3.0.0' > specs/api.yaml

# Set up test collections
cp .mrapids/collections/*.yaml test-collections/

# Configure test environment
export MRAPIDS_TEST_MODE=true
```

---

## 📊 Expected Test Coverage

- **Core CLI**: 100% coverage of main.rs paths
- **Run Command**: All execution modes tested
- **Validation**: All 3 levels + error cases
- **Collections**: Full workflow coverage
- **SDK Generation**: All 4 languages
- **Authentication**: OAuth flow + profiles
- **Error Handling**: All exit codes tested

Total: **80+ comprehensive test cases** based on actual code implementation