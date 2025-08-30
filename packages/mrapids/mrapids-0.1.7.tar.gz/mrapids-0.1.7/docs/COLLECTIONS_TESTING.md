# Collections Testing Feature (Phase 2)

## Overview

The collections testing feature allows you to run collections with assertions to validate API responses. This is perfect for:

- **API Contract Testing**: Ensure APIs return expected responses
- **Regression Testing**: Catch breaking changes early
- **Integration Testing**: Validate complex workflows
- **CI/CD Integration**: Automated testing with JUnit output

## Test Collection Format

Add `expect` blocks to your collection requests to define assertions:

```yaml
name: api-tests
description: API test suite with assertions
requests:
  - name: test_get_user
    operation: users/get-by-username
    params:
      username: octocat
    expect:
      status: 200
      body:
        login: octocat
        type: User
      headers:
        content-type: application/json
```

## Assertion Types

### 1. Status Code Assertions

```yaml
expect:
  status: 200  # Exact status code match
```

### 2. Response Body Assertions

Supports partial matching for objects:

```yaml
expect:
  body:
    # These fields must exist and match
    id: 123
    name: "John Doe"
    # Nested objects
    address:
      city: "San Francisco"
```

### 3. Header Assertions

```yaml
expect:
  headers:
    content-type: "application/json"
    x-rate-limit: "100"
```

## Running Tests

### Basic Test Execution

```bash
mrapids collection test <name> [options]
```

Options:
- `--spec <path>`: API specification file
- `--profile <name>`: Authentication profile
- `--output <format>`: Output format (pretty, json, junit)
- `--continue-on-error`: Run all tests even if some fail

### Examples

```bash
# Run tests with pretty output
mrapids collection test api-tests --spec api.yaml

# Generate JUnit XML for CI
mrapids collection test api-tests --output junit > test-results.xml

# Continue running all tests on failure
mrapids collection test api-tests --continue-on-error
```

## Output Formats

### Pretty Output (Default)

```
🧪 Test Results: api-tests
──────────────────────────────────────────────────
✓ test_get_user PASSED (185ms)
✗ test_invalid_user FAILED (92ms)
    └ Status assertion: Expected status 200, got 404
      ├ Expected: 200
      └ Actual: 404
⊘ test_admin_api SKIPPED

──────────────────────────────────────────────────
Tests: 3, Passed: 1, Failed: 1, Skipped: 1
Duration: 0.28s

❌ Some tests failed
```

### JSON Output

```json
{
  "name": "api-tests",
  "total_tests": 3,
  "passed": 1,
  "failed": 1,
  "skipped": 1,
  "all_passed": false,
  "test_results": [
    {
      "name": "test_get_user",
      "operation": "users/get-by-username",
      "passed": true,
      "status": "passed",
      "duration_ms": 185,
      "assertions": [
        {
          "assertion_type": "status",
          "passed": true,
          "expected": 200,
          "actual": 200,
          "message": "Status code is 200"
        }
      ]
    }
  ],
  "total_duration_ms": 280
}
```

### JUnit XML Output

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="api-tests" tests="3" failures="1" time="0.280">
  <testsuite name="api-tests" tests="3" failures="1" skipped="1" time="0.280">
    <testcase name="test_get_user" classname="users/get-by-username" time="0.185" />
    <testcase name="test_invalid_user" classname="users/get-by-username" time="0.092">
      <failure message="Expected status 200, got 404" type="assertion">
        Expected status 200, got 404
      </failure>
    </testcase>
    <testcase name="test_admin_api" classname="admin/get-settings" time="0.000">
      <skipped />
    </testcase>
  </testsuite>
</testsuites>
```

## Advanced Testing Examples

### 1. Testing CRUD Operations

```yaml
name: user-crud-tests
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
        email: "test@example.com"
        
  - name: get_created_user
    operation: users/get
    params:
      id: "{{created_user.id}}"
    expect:
      status: 200
      body:
        id: "{{created_user.id}}"
        name: "Test User"
        
  - name: update_user
    operation: users/update
    params:
      id: "{{created_user.id}}"
    body:
      name: "Updated User"
    expect:
      status: 200
      body:
        name: "Updated User"
        
  - name: delete_user
    operation: users/delete
    params:
      id: "{{created_user.id}}"
    expect:
      status: 204
```

### 2. Testing Error Scenarios

```yaml
name: error-handling-tests
requests:
  - name: test_not_found
    operation: users/get
    params:
      id: 999999
    expect:
      status: 404
      body:
        error: "User not found"
        
  - name: test_validation_error
    operation: users/create
    body:
      name: ""  # Empty name should fail
    expect:
      status: 400
      body:
        errors:
          name: "Name is required"
          
  - name: test_unauthorized
    operation: admin/settings
    # No auth provided
    expect:
      status: 401
```

### 3. Testing Search and Filtering

```yaml
name: search-tests
variables:
  search_term: javascript
  min_stars: 1000
  
requests:
  - name: search_popular_repos
    operation: search/repos
    params:
      q: "language:{{search_term}} stars:>{{min_stars}}"
      sort: stars
      order: desc
    expect:
      status: 200
      body:
        total_count: 1000  # At least 1000 results
        items:
          - stargazers_count: 10000  # First result has >10k stars
```

## CI/CD Integration

### GitHub Actions Example

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
        run: |
          mrapids collection test api-tests \
            --spec specs/api.yaml \
            --output junit > test-results.xml
            
      - name: Publish Test Results
        uses: EnricoMi/publish-unit-test-result-action@v1
        if: always()
        with:
          files: test-results.xml
```

### GitLab CI Example

```yaml
api-tests:
  stage: test
  script:
    - mrapids collection test api-tests --output junit > test-results.xml
  artifacts:
    reports:
      junit: test-results.xml
```

## Best Practices

1. **Organize Tests by Feature**: Create separate collections for different features
2. **Use Variables**: Make tests reusable across environments
3. **Test Happy Path and Errors**: Include both success and failure scenarios
4. **Clean Up Test Data**: Use setup/teardown requests
5. **Version Control Tests**: Store test collections with your code
6. **Run in CI/CD**: Automate testing on every commit

## Limitations

**Note**: The current implementation has some limitations:

1. **Status Code Detection**: Due to underlying API limitations, status codes may not be accurately captured in some cases
2. **Headers**: Response headers are not yet fully captured
3. **Complex Assertions**: Advanced assertions like regex matching or JSONPath are not yet supported

These limitations will be addressed in future updates.

## Future Enhancements

- **JSONPath Assertions**: Query nested data with JSONPath
- **Regex Matching**: Pattern matching for strings
- **Schema Validation**: Validate against JSON Schema
- **Performance Assertions**: Assert on response times
- **Conditional Tests**: Skip/run based on previous results
- **Test Setup/Teardown**: Before/after hooks
- **Parallel Execution**: Run independent tests concurrently