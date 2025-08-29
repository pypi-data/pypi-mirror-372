# MicroRapid Collections - Complete Guide

## Overview

Collections in MicroRapid allow you to group related API requests, execute them sequentially, and test API behaviors. This feature is now fully implemented with advanced capabilities including testing, variable management, and CI/CD integration.

## Features Implemented

### Phase 1: Core Collections (✅ Complete)
- YAML-based collection format
- Sequential request execution  
- Variable interpolation with Handlebars
- Response chaining (save_as)
- Multiple output formats (pretty, JSON, YAML)
- Save responses to files

### Phase 2: Testing & Assertions (✅ Complete)
- Test execution mode with assertions
- Status code assertions
- Response body assertions (partial matching)
- Header assertions
- JUnit XML output for CI/CD
- Continue-on-error mode
- Detailed test reporting

### Phase 3: Advanced Variables (✅ Complete)
- Environment variable support (COLLECTION_* prefix)
- .env file loading (--env-file)
- CLI variable overrides (--var key=value)
- Variable interpolation in all fields
- HTTP status code and header capture

## Quick Start

### 1. Create a Collection

```yaml
# .mrapids/collections/my-api-tests.yaml
name: my-api-tests
description: API test collection
variables:
  base_url: https://api.example.com
  api_key: test-key

requests:
  - name: get_user
    operation: users/get
    params:
      id: "123"
    save_as: user_data
    
  - name: update_user
    operation: users/update
    params:
      id: "{{user_data.id}}"
    body:
      name: "Updated Name"
    expect:
      status: 200
      body:
        id: "123"
        name: "Updated Name"
```

### 2. Run the Collection

```bash
# Basic execution
mrapids collection run my-api-tests --spec api.yaml

# With variables
mrapids collection run my-api-tests --var api_key=prod-key

# With environment file
mrapids collection run my-api-tests --env-file .env.production

# As tests
mrapids collection test my-api-tests --output junit > results.xml
```

## Variable Management

### Variable Sources (in order of precedence)

1. **CLI Overrides**: `--var key=value`
2. **Environment File**: `--env-file .env`
3. **Environment Variables**: `COLLECTION_*` prefix
4. **Collection Variables**: Defined in YAML
5. **Saved Responses**: From previous requests

### Example: Using Variables

```yaml
variables:
  environment: staging
  
requests:
  - name: api_call
    operation: "{{environment}}/users/list"
    params:
      limit: "{{PAGE_SIZE}}"  # From env var COLLECTION_PAGE_SIZE
    headers:
      Authorization: "Bearer {{auth_token}}"  # From .env file
```

### Loading Variables

```bash
# From environment
export COLLECTION_PAGE_SIZE=50
mrapids collection run my-api --use-env

# From .env file
cat > .env.staging << EOF
COLLECTION_auth_token=staging-token-123
COLLECTION_api_url=https://staging.example.com
EOF
mrapids collection run my-api --env-file .env.staging

# From CLI
mrapids collection run my-api --var auth_token=override-token
```

## Testing Features

### Assertion Types

```yaml
expect:
  # Status code assertion
  status: 200
  
  # Response body assertion (partial match)
  body:
    success: true
    data:
      id: "123"
      # Nested objects supported
      profile:
        email: "user@example.com"
  
  # Header assertions
  headers:
    content-type: "application/json"
    x-rate-limit: "100"
```

### Test Output Formats

#### Pretty (Default)
```
🧪 Test Results: my-api-tests
──────────────────────────────────────────────────
✓ get_user PASSED (185ms)
✗ invalid_request FAILED (92ms)
    └ Status assertion: Expected 200, got 400
```

#### JUnit XML
```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="my-api-tests" tests="2" failures="1">
  <testsuite name="my-api-tests">
    <testcase name="get_user" time="0.185" />
    <testcase name="invalid_request" time="0.092">
      <failure message="Expected status 200, got 400" />
    </testcase>
  </testsuite>
</testsuites>
```

## CI/CD Integration

### GitHub Actions

```yaml
name: API Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Install mrapids
        run: cargo install mrapids
        
      - name: Run API tests
        env:
          COLLECTION_API_KEY: ${{ secrets.API_KEY }}
        run: |
          mrapids collection test api-tests \
            --spec specs/api.yaml \
            --use-env \
            --output junit > test-results.xml
            
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v1
        if: always()
        with:
          files: test-results.xml
```

### GitLab CI

```yaml
api-tests:
  stage: test
  variables:
    COLLECTION_API_KEY: $API_KEY
  script:
    - mrapids collection test api-tests --use-env --output junit > results.xml
  artifacts:
    reports:
      junit: results.xml
```

## Advanced Examples

### 1. CRUD Operations with Assertions

```yaml
name: user-crud
requests:
  - name: create_user
    operation: users/create
    body:
      name: "Test User"
      email: "test@example.com"
    save_as: created_user
    expect:
      status: 201
      body:
        name: "Test User"
        
  - name: verify_user
    operation: users/get
    params:
      id: "{{created_user.id}}"
    expect:
      status: 200
      body:
        id: "{{created_user.id}}"
        name: "Test User"
        
  - name: cleanup
    operation: users/delete
    params:
      id: "{{created_user.id}}"
    expect:
      status: 204
```

### 2. Conditional Execution

```yaml
name: conditional-flow
requests:
  - name: check_feature
    operation: features/check
    params:
      feature: "new-api"
    save_as: feature_check
    
  - name: use_new_api
    operation: v2/process
    # Only runs if feature is enabled
    skip: "{{feature_check.enabled != true}}"
    body:
      data: "test"
```

### 3. Multi-Environment Testing

```bash
# Test against multiple environments
for env in dev staging prod; do
  echo "Testing $env environment..."
  mrapids collection test api-tests \
    --env-file .env.$env \
    --var environment=$env \
    --output json > results-$env.json
done
```

## Best Practices

1. **Organize by Feature**: Create separate collections for different features
2. **Use Variables**: Make collections reusable across environments
3. **Clean Test Data**: Include cleanup requests to maintain test isolation
4. **Version Control**: Store collections alongside your code
5. **Partial Assertions**: Only assert on fields you care about
6. **Error Scenarios**: Test both success and failure paths

## Command Reference

### List Collections
```bash
mrapids collection list [--dir <path>]
```

### Show Collection Details
```bash
mrapids collection show <name> [--dir <path>]
```

### Validate Collection
```bash
mrapids collection validate <name> [--spec <path>]
```

### Run Collection
```bash
mrapids collection run <name> [options]
  --spec <path>           API specification file
  --profile <name>        Auth profile to use
  --var <key=value>       Override variables
  --env-file <path>       Load variables from .env file
  --use-env               Use environment variables
  --output <format>       Output format (pretty|json|yaml)
  --save-all <dir>        Save all responses
  --continue-on-error     Don't stop on failures
  --request <name>        Run specific requests only
  --skip <name>           Skip specific requests
```

### Test Collection
```bash
mrapids collection test <name> [options]
  --spec <path>           API specification file
  --profile <name>        Auth profile to use
  --output <format>       Output format (pretty|json|junit)
  --continue-on-error     Run all tests even on failure
```

## Troubleshooting

### Variables Not Resolving
- Check variable precedence order
- Verify environment variable prefix (COLLECTION_)
- Ensure .env file exists and is readable
- Use `--output json` to see actual values

### Assertions Failing
- Remember assertions use partial matching for objects
- Arrays must match exactly (length and order)
- Use `--output json` to see actual vs expected values

### Status Codes Not Captured
- Fixed in Phase 3 - update to latest version
- Ensure your API returns proper HTTP status codes

## Future Enhancements

While the core features are complete, potential future additions include:
- JSONPath assertions for complex queries
- Regex pattern matching
- Performance assertions (response time)
- Parallel request execution
- GraphQL support
- WebSocket testing
- OAuth2 flow automation

## Contributing

To contribute to the collections feature:
1. Check existing issues on GitHub
2. Create test collections for new features
3. Update documentation
4. Submit PR with tests

## Summary

The MicroRapid collections feature provides a powerful way to:
- Group and execute related API requests
- Test API contracts with assertions
- Manage variables across environments
- Integrate with CI/CD pipelines
- Share and version control API workflows

With full variable interpolation, environment support, and comprehensive testing capabilities, collections make API testing and automation simple and maintainable.