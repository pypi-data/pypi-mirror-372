# Collections Framework Documentation

The Collections framework provides a powerful way to organize, execute, and test multiple API requests with advanced features like variable management, dependencies, conditional execution, and retry logic.

## Table of Contents

1. [Overview](#overview)
2. [Collection Structure](#collection-structure)
3. [Variable System](#variable-system)
4. [Request Dependencies](#request-dependencies)
5. [Conditional Execution](#conditional-execution)
6. [Flow Control](#flow-control)
7. [Retry Logic](#retry-logic)
8. [Testing & Assertions](#testing--assertions)
9. [CLI Commands](#cli-commands)
10. [Examples](#examples)

## Overview

Collections are YAML files that define groups of related API requests with shared configuration, variables, and execution logic. They enable:

- **Orchestrated Execution**: Run requests in dependency order
- **Variable Management**: Centralized configuration with precedence rules
- **Conditional Logic**: Execute requests based on runtime conditions
- **Error Handling**: Retry logic and failure recovery
- **Testing**: Built-in assertion and validation capabilities

## Collection Structure

### Basic Collection

```yaml
name: my-collection
description: Description of what this collection does
auth_profile: default-auth  # Optional default auth

# Collection-level variables (lowest precedence)
variables:
  api_url: "https://api.example.com"
  version: "v1"

requests:
  - name: request_name
    operation: operation_id
    # ... request configuration
```

### Request Structure

```yaml
- name: unique_request_name           # Required: unique within collection
  operation: operation_id             # Required: OpenAPI operation ID
  
  # Request data
  params:                             # Optional: query/path parameters
    param1: "{{variable}}"
    param2: "literal_value"
  body:                               # Optional: request body
    field1: "{{variable}}"
    field2: 123
  
  # Response handling
  save_as: response_key               # Optional: save response for later use
  expect:                             # Optional: test assertions
    status: 200
    body:
      field: expected_value
  
  # Phase 4: Dependencies and control flow
  depends_on:                         # Optional: request dependencies
    - other_request_name
    - another_dependency
  if: "condition_expression"          # Optional: execution condition
  skip: "skip_condition"              # Optional: skip condition
  run_always: false                   # Optional: run even on collection failure
  critical: false                     # Optional: stop collection if this fails
  
  # Phase 4: Retry configuration
  retry:                              # Optional: retry logic
    attempts: 3
    delay: 1000                       # milliseconds
    backoff: exponential              # linear or exponential
```

## Variable System

### Variable Precedence (Highest to Lowest)

The variable resolution follows a strict precedence hierarchy:

1. **CLI Overrides** (`--var key=value`) - Highest precedence
2. **Environment Variables** (`--use-env` with `COLLECTION_*` prefix)
3. **Environment Files** (`--env-file .env`)
4. **Collection Variables** (defined in YAML) - Lowest precedence

### Variable Sources

#### 1. CLI Overrides (Highest Precedence)
```bash
mrapids collection run my-collection --var api_url=http://localhost:3000 --var debug=true
```

#### 2. Environment Variables
```bash
# Set environment variables with COLLECTION_ prefix
export COLLECTION_API_URL=https://staging.api.com
export COLLECTION_DEBUG=true

# Use in command
mrapids collection run my-collection --use-env
```

#### 3. Environment Files
```bash
# .env.staging
API_URL=https://staging.api.com
DEBUG=true
TOKEN=staging_token

# Use in command
mrapids collection run my-collection --env-file .env.staging
```

#### 4. Collection Variables (Lowest Precedence)
```yaml
# In collection YAML
variables:
  api_url: "https://api.example.com"
  debug: false
  timeout: 30
```

### Variable Interpolation

Variables are resolved using Handlebars syntax:

```yaml
requests:
  - name: get_user
    operation: users/get-by-username
    params:
      username: "{{username}}"
      debug: "{{debug}}"
    body:
      api_key: "{{api_token}}"
      endpoint: "{{api_url}}/users"
```

### Saved Response Variables

Responses can be saved and used in subsequent requests:

```yaml
requests:
  - name: login
    operation: auth/login
    body:
      username: "{{username}}"
      password: "{{password}}"
    save_as: auth_response
    
  - name: get_profile
    operation: users/profile
    params:
      token: "{{auth_response.token}}"
    depends_on: login
```

## Request Dependencies

### Dependency Declaration

Dependencies ensure requests execute in the correct order:

```yaml
requests:
  - name: setup_data
    operation: data/create
    
  - name: process_data
    operation: data/process
    depends_on: setup_data          # Single dependency
    
  - name: finalize
    operation: data/finalize
    depends_on:                     # Multiple dependencies
      - setup_data
      - process_data
```

### Dependency Resolution

- Dependencies are resolved using topological sorting
- Circular dependencies are detected and cause validation errors
- Failed dependencies prevent dependent requests from running (unless `run_always: true`)

### Dependency Syntax Support

Both single string and array syntax are supported:

```yaml
# Single dependency
depends_on: request_name

# Multiple dependencies
depends_on:
  - request1
  - request2
```

## Conditional Execution

### Condition Expressions

Execute requests based on runtime conditions:

```yaml
requests:
  - name: dev_only_request
    operation: debug/info
    if: "env == 'development'"
    
  - name: prod_cleanup
    operation: cleanup/data
    skip: "env == 'development'"
    
  - name: retry_on_failure
    operation: data/process
    if: "previous_request.status != 200"
```

### Available Context

Conditions have access to:
- **Variables**: All resolved variables
- **Environment**: Environment variables
- **Saved Responses**: Previously saved response data
- **Request Results**: Status and response data from completed requests

### Condition Operators

- **Equality**: `==`, `!=`
- **Logical**: `&&`, `||`
- **Parentheses**: `(condition1 || condition2) && condition3`

### Examples

```yaml
# Environment-based execution
if: "env == 'production' && debug != 'true'"

# Response-based conditions
if: "login_response.status == 200"

# Multiple conditions
if: "(env == 'dev' || env == 'staging') && feature_flag == 'enabled'"

# Skip conditions (inverse logic)
skip: "env == 'production'"
```

## Flow Control

### run_always

Requests marked with `run_always: true` execute even if the collection fails:

```yaml
requests:
  - name: cleanup_temp_data
    operation: cleanup/temp
    run_always: true              # Always runs for cleanup
    
  - name: send_notification
    operation: notifications/send
    run_always: true              # Always notify of completion
```

### critical

Requests marked with `critical: true` stop the entire collection if they fail:

```yaml
requests:
  - name: authentication
    operation: auth/login
    critical: true                # Collection stops if auth fails
    
  - name: validate_permissions
    operation: auth/validate
    critical: true                # Collection stops if validation fails
    depends_on: authentication
```

### Execution Flow

1. **Dependency Resolution**: Build execution order
2. **Sequential Execution**: Execute requests in dependency groups
3. **Failure Handling**: 
   - Non-critical failures: Continue unless `continue_on_error: false`
   - Critical failures: Stop collection immediately
4. **Cleanup Phase**: Execute all `run_always` requests

## Retry Logic

### Retry Configuration

```yaml
requests:
  - name: flaky_api_call
    operation: external/api
    retry:
      attempts: 3                 # Number of retry attempts
      delay: 1000                 # Base delay in milliseconds
      backoff: exponential        # Backoff strategy: linear | exponential
```

### Backoff Strategies

#### Linear Backoff
Delay increases linearly: `delay * attempt_number`
- Attempt 1: 1000ms
- Attempt 2: 2000ms  
- Attempt 3: 3000ms

#### Exponential Backoff
Delay doubles each attempt: `delay * 2^(attempt_number - 1)`
- Attempt 1: 1000ms
- Attempt 2: 2000ms
- Attempt 3: 4000ms

### Retry Behavior

- Retries only occur on request failures (network errors, 5xx responses)
- Successful responses (even 4xx) do not trigger retries
- Final attempt failure propagates the original error

## Testing & Assertions

### Test Assertions

```yaml
requests:
  - name: api_health_check
    operation: health/status
    expect:
      status: 200                 # Expected HTTP status
      headers:
        content-type: "application/json"
      body:
        status: "healthy"
        version: "1.0.0"
```

### Running as Tests

```bash
# Run collection as tests with assertions
mrapids collection test my-collection

# Output formats
mrapids collection test my-collection --output json
mrapids collection test my-collection --output junit
```

### Test Results

Test mode provides:
- Pass/fail status for each request
- Detailed assertion results
- Summary statistics
- JUnit XML output for CI/CD integration

## CLI Commands

### List Collections

```bash
# List all collections
mrapids collection list

# List from specific directory
mrapids collection list --dir /path/to/collections
```

### Show Collection Details

```bash
# Show collection structure
mrapids collection show my-collection

# Show from specific directory
mrapids collection show my-collection --dir /path/to/collections
```

### Validate Collections

```bash
# Validate collection syntax
mrapids collection validate my-collection

# Validate with API spec
mrapids collection validate my-collection --spec api.yaml
```

### Run Collections

```bash
# Basic execution
mrapids collection run my-collection

# With variable overrides
mrapids collection run my-collection \
  --var api_url=http://localhost:3000 \
  --var debug=true

# With environment variables
mrapids collection run my-collection --use-env

# With environment file
mrapids collection run my-collection --env-file .env.staging

# Skip specific requests
mrapids collection run my-collection --skip-requests request1,request2

# Run only specific requests
mrapids collection run my-collection --requests request1,request2

# Continue on errors
mrapids collection run my-collection --continue-on-error

# Save responses
mrapids collection run my-collection \
  --save-all ./responses \
  --save-summary ./summary.json
```

### Test Collections

```bash
# Run as tests
mrapids collection test my-collection

# Different output formats
mrapids collection test my-collection --output json
mrapids collection test my-collection --output junit

# Continue on test failures
mrapids collection test my-collection --continue-on-error
```

## Examples

### Example 1: User Management Workflow

```yaml
name: user-management
description: Complete user lifecycle management

variables:
  api_url: "https://api.example.com"
  test_username: "testuser123"

requests:
  # 1. Create user
  - name: create_user
    operation: users/create
    body:
      username: "{{test_username}}"
      email: "{{test_username}}@example.com"
    save_as: user_response
    expect:
      status: 201
    
  # 2. Verify user creation
  - name: get_user
    operation: users/get-by-id
    params:
      user_id: "{{user_response.id}}"
    depends_on: create_user
    expect:
      status: 200
      body:
        username: "{{test_username}}"
    
  # 3. Update user (with retry for flaky endpoint)
  - name: update_user
    operation: users/update
    params:
      user_id: "{{user_response.id}}"
    body:
      email: "updated-{{test_username}}@example.com"
    depends_on: get_user
    retry:
      attempts: 3
      delay: 500
      backoff: exponential
    
  # 4. Delete user (only in non-production)
  - name: cleanup_user
    operation: users/delete
    params:
      user_id: "{{user_response.id}}"
    depends_on: update_user
    skip: "env == 'production'"
    run_always: true
```

### Example 2: Environment-Specific Deployment

```yaml
name: deployment-pipeline
description: Multi-environment deployment workflow

variables:
  env: "development"
  deploy_version: "1.0.0"

requests:
  # 1. Health check (critical)
  - name: health_check
    operation: health/status
    critical: true
    expect:
      status: 200
      body:
        status: "healthy"
  
  # 2. Deploy to staging (non-production only)
  - name: deploy_staging
    operation: deploy/staging
    body:
      version: "{{deploy_version}}"
    depends_on: health_check
    skip: "env == 'production'"
    
  # 3. Run integration tests (staging only)
  - name: integration_tests
    operation: tests/integration
    depends_on: deploy_staging
    if: "env == 'staging'"
    retry:
      attempts: 2
      delay: 5000
      backoff: linear
    
  # 4. Deploy to production (production only)
  - name: deploy_production
    operation: deploy/production
    body:
      version: "{{deploy_version}}"
    depends_on: health_check
    if: "env == 'production'"
    critical: true
    
  # 5. Notification (always runs)
  - name: notify_deployment
    operation: notifications/deployment
    body:
      environment: "{{env}}"
      version: "{{deploy_version}}"
      status: "completed"
    run_always: true
```

### Example 3: Complex Variable Precedence

```yaml
# .env.staging
API_URL=https://staging.api.com
DEBUG=true
RATE_LIMIT=100

# collection.yaml
name: api-testing
variables:
  api_url: "https://api.example.com"  # Overridden by env file
  debug: false                        # Overridden by env file  
  timeout: 30                         # Not overridden
  
requests:
  - name: test_api
    operation: test/endpoint
    params:
      url: "{{api_url}}"              # staging.api.com (from env file)
      debug: "{{debug}}"              # true (from env file)
      timeout: "{{timeout}}"          # 30 (from collection)
      override: "{{cli_override}}"    # Value from --var flag
```

```bash
# Command with all precedence levels
COLLECTION_API_URL=https://env.api.com mrapids collection run api-testing \
  --env-file .env.staging \
  --use-env \
  --var api_url=http://localhost:3000 \
  --var cli_override=test_value

# Final variable values:
# api_url: http://localhost:3000 (CLI override wins)
# debug: true (from .env.staging, env vars beat collection)
# timeout: 30 (from collection, not overridden)
# cli_override: test_value (only in CLI)
```

This framework provides a comprehensive solution for API workflow automation with sophisticated variable management, dependency resolution, and execution control.