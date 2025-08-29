# Variable Precedence in MicroRapid Collections

## Overview

Variables in MicroRapid collections can come from multiple sources. Understanding the precedence order is crucial for managing configurations across different environments.

## Variable Sources and Precedence

Variables are resolved in the following order (from **highest** to **lowest** precedence):

1. **CLI Overrides** (`--var key=value`)
   - Highest precedence
   - Always wins over other sources
   - Use case: Quick testing, debugging, CI/CD overrides

2. **Environment Variables** (`COLLECTION_*` prefix)
   - Set via shell: `export COLLECTION_api_key=secret`
   - Loaded with `--use-env` flag
   - Use case: Secrets, environment-specific config

3. **.env Files** (`--env-file path/to/.env`)
   - Format: `COLLECTION_variable=value`
   - Loaded from specified file
   - Use case: Environment configurations

4. **Collection Variables** (defined in YAML)
   - Lowest precedence
   - Default values
   - Use case: Sensible defaults, documentation

## Examples

### Example Collection
```yaml
name: api-test
variables:
  api_url: http://localhost:3000  # Default
  api_key: dev_key                 # Default
  timeout: 30                      # Default
```

### Variable Resolution Examples

```bash
# Uses collection defaults
mrapids collection run api-test

# Override with .env file
# .env.production:
# COLLECTION_api_url=https://api.prod.com
# COLLECTION_api_key=prod_key
mrapids collection run api-test --env-file .env.production

# Override with environment variables
export COLLECTION_api_url=https://api.staging.com
mrapids collection run api-test --use-env

# Override with CLI (highest precedence)
mrapids collection run api-test \
  --var api_url=https://api.test.com \
  --var timeout=60
```

### Precedence in Action

Given:
- Collection YAML: `api_url: http://localhost`
- .env file: `COLLECTION_api_url=https://staging.com`
- Environment: `COLLECTION_api_url=https://prod.com`
- CLI: `--var api_url=https://test.com`

Result with all sources:
```bash
mrapids collection run test --env-file .env --use-env --var api_url=https://test.com
# api_url = https://test.com (CLI wins)
```

## Variable Usage

Variables can be used in:

1. **Operation IDs**
```yaml
operation: "{{method}}"  # Dynamic operation selection
```

2. **Parameters**
```yaml
params:
  user_id: "{{user_id}}"
  limit: "{{page_size}}"
```

3. **Request Bodies**
```yaml
body:
  name: "{{user_name}}"
  config:
    timeout: "{{timeout}}"
```

4. **Nested Templates**
```yaml
params:
  message: "User {{user_name}} from {{environment}}"
```

## Best Practices

1. **Use Collection Variables for Defaults**
   - Document expected variables
   - Provide sensible defaults
   - Make collections self-documenting

2. **Use .env Files for Environments**
   - Create .env.dev, .env.staging, .env.prod
   - Version control example files (not secrets)
   - Keep consistent naming

3. **Use Environment Variables for Secrets**
   - Never commit secrets
   - Use CI/CD secret management
   - Document required variables

4. **Use CLI Overrides for Testing**
   - Quick iterations
   - Temporary changes
   - Debugging specific scenarios

## Special Variables

### Saved Responses
Variables from `save_as` have the highest precedence:
```yaml
- name: create_user
  operation: users/create
  save_as: new_user
  
- name: get_user
  operation: users/get
  params:
    id: "{{new_user.id}}"  # Always available
```

### Resolution Context
During execution, the context includes:
- All variable sources (resolved by precedence)
- Saved responses from previous requests
- Built-in variables (future feature)

## Debugging Variables

To debug variable resolution:

1. **Use Simple Echo Request**
```yaml
- name: debug_vars
  operation: get
  params:
    var1: "{{var1}}"
    var2: "{{var2}}"
    source: "{{source}}"
```

2. **Check Output**
The response will show actual values used

3. **Use JSON Output**
```bash
mrapids collection run test --output json
```

## Common Issues and Solutions

### Issue: Variable Not Resolving
- Check variable name spelling
- Verify source is loaded (--use-env, --env-file)
- Check COLLECTION_ prefix for env vars

### Issue: Wrong Value Used
- Check precedence order
- Look for multiple sources defining same variable
- Use --var to force specific value

### Issue: Operation Not Found
- Ensure operation variable resolves correctly
- Check if operation exists in spec
- Use static operation for debugging