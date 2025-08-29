# MicroRapid Exit Codes

MicroRapid uses standardized exit codes for scripting and CI/CD integration.

## Exit Code Reference

| Code | Name | Description | Example |
|------|------|-------------|---------|
| `0` | SUCCESS | Command completed successfully | `mrapids validate api.yaml` |
| `1` | UNKNOWN_ERROR | Unexpected error occurred | Internal errors |
| `2` | USAGE_ERROR | Invalid command or arguments | `mrapids invalid-command` |
| `3` | AUTH_ERROR | Authentication failed | OAuth token expired |
| `4` | NETWORK_ERROR | Network connection failed | Timeout, DNS failure |
| `5` | RATE_LIMIT_ERROR | API rate limit exceeded | 429 Too Many Requests |
| `6` | SERVER_ERROR | Server returned error | 500, 502, 503 errors |
| `7` | VALIDATION_ERROR | Validation failed | Invalid OpenAPI spec |
| `8` | BREAKING_CHANGE | Breaking changes detected | `mrapids diff` found breaks |

## Usage in Scripts

### Bash
```bash
#!/bin/bash
mrapids validate api.yaml --strict
if [ $? -eq 0 ]; then
    echo "Validation passed"
else
    echo "Validation failed with code $?"
    exit $?
fi
```

### CI/CD Examples

#### GitHub Actions
```yaml
- name: Validate API Spec
  run: |
    mrapids validate api.yaml --strict
    # Automatically fails the step if exit code != 0

- name: Check Breaking Changes
  run: |
    mrapids diff api-prod.yaml api.yaml --breaking-only
    # Exits with code 8 if breaking changes found
```

#### Jenkins
```groovy
stage('API Validation') {
    steps {
        script {
            def exitCode = sh(
                script: 'mrapids validate api.yaml --strict',
                returnStatus: true
            )
            if (exitCode == 7) {
                error "Validation failed"
            } else if (exitCode != 0) {
                error "Command failed with exit code ${exitCode}"
            }
        }
    }
}
```

#### GitLab CI
```yaml
validate:
  script:
    - mrapids validate api.yaml --strict
  # Job fails automatically on non-zero exit

check-breaking:
  script:
    - mrapids diff api-prod.yaml api.yaml
  allow_failure:
    exit_codes: [8]  # Allow breaking changes in some branches
```

## Error Detection Patterns

### Network Errors (Exit Code 4)
- Connection timeout
- DNS resolution failure
- Connection refused
- Network unreachable

### Rate Limit Errors (Exit Code 5)
- HTTP 429 status
- X-RateLimit-Remaining: 0
- Retry-After header present

### Server Errors (Exit Code 6)
- HTTP 5xx status codes
- Bad Gateway (502)
- Service Unavailable (503)
- Gateway Timeout (504)

### Validation Errors (Exit Code 7)
- Invalid OpenAPI specification
- Schema validation failures
- Missing required fields
- Type mismatches
- Test assertion failures

### Breaking Changes (Exit Code 8)
- Removed endpoints
- Changed required parameters
- Modified response schemas
- Incompatible type changes

## Best Practices

1. **Always check exit codes in scripts**
   ```bash
   mrapids test api.yaml --all || exit $?
   ```

2. **Use specific error handling**
   ```bash
   case $? in
       0) echo "Success" ;;
       3) echo "Fix authentication" ;;
       4) echo "Check network connection" ;;
       7) echo "Fix validation errors" ;;
       8) echo "Breaking changes detected" ;;
       *) echo "Unknown error" ;;
   esac
   ```

3. **Set up monitoring**
   ```bash
   # Alert on specific errors
   mrapids test api.yaml --env prod
   [ $? -eq 5 ] && send-alert "Rate limit hit"
   ```

4. **Fail fast in CI/CD**
   ```bash
   set -e  # Exit on any non-zero code
   mrapids validate api.yaml
   mrapids test api.yaml --all
   mrapids diff api-main.yaml api.yaml
   ```

## Debugging

To see more details about why a command failed:

```bash
# Enable verbose output
mrapids validate api.yaml --verbose

# Enable trace output (includes HTTP details)
RUST_LOG=trace mrapids run api.yaml --operation failing-op

# Check the exact exit code
mrapids command-that-fails; echo "Exit code: $?"
```

## Migration Note

Previous versions of MicroRapid only returned 0 (success) or 1 (failure). Scripts relying on this behavior should be updated to handle the new exit codes appropriately.