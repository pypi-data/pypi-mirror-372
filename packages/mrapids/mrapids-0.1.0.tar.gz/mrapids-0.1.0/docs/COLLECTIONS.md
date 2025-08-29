# Collections Feature Documentation

## Overview

Collections in mrapids allow you to group multiple API requests together and execute them sequentially. This is useful for:

- **Testing workflows**: Execute a series of related API calls
- **Data gathering**: Collect data from multiple endpoints
- **Environment setup**: Run initialization sequences
- **API exploration**: Save and replay common request patterns

## Collection File Format

Collections are defined in YAML files with the following structure:

```yaml
name: my-collection
description: Optional description of the collection
variables:
  username: default_user
  api_key: ${API_KEY}
auth_profile: my-profile  # Optional default auth

requests:
  - name: unique_request_name
    operation: operation-id-from-spec
    params:
      param1: value1
      param2: "{{username}}"  # Variable substitution
    body:
      key: value
    save_as: response_data  # Save response for later use
    
  - name: second_request
    operation: another-operation
    params:
      id: "{{response_data.id}}"  # Use saved data
```

## Commands

### List Collections

```bash
mrapids collection list [--dir .mrapids/collections]
```

Lists all available collections in the specified directory.

### Show Collection Details

```bash
mrapids collection show <name> [--dir .mrapids/collections]
```

Displays collection details including requests and variables.

### Validate Collection

```bash
mrapids collection validate <name> [--spec path/to/spec.yaml]
```

Validates collection syntax and checks if operations exist in the API spec.

### Run Collection

```bash
mrapids collection run <name> [options]
```

Options:
- `--spec <path>`: API specification file
- `--output <format>`: Output format (json, yaml, pretty)
- `--var <key>=<value>`: Override variables
- `--profile <name>`: Authentication profile
- `--continue-on-error`: Don't stop on failures
- `--request <name>`: Run specific request(s)
- `--skip <name>`: Skip specific request(s)
- `--save-all <dir>`: Save all responses to directory
- `--save-summary <file>`: Save execution summary
- `--use-env`: Use environment variables

### Test Collection (Coming Soon)

```bash
mrapids collection test <name> [options]
```

Run collection with assertions and test reporting.

## Features

### 1. Variable Substitution

Use `{{variable}}` syntax to substitute variables throughout your collection:

```yaml
variables:
  base_url: https://api.example.com
  user_id: 12345

requests:
  - name: get_user
    operation: getUser
    params:
      id: "{{user_id}}"
```

Override variables at runtime:
```bash
mrapids collection run my-collection --var user_id=67890
```

### 2. Response Chaining

Save responses from one request to use in subsequent requests:

```yaml
requests:
  - name: create_user
    operation: createUser
    body:
      name: Test User
    save_as: new_user
    
  - name: get_created_user
    operation: getUser
    params:
      id: "{{new_user.id}}"
```

### 3. Environment Variables

Access environment variables with the `--use-env` flag:

```bash
export COLLECTION_API_KEY=secret123
mrapids collection run my-collection --use-env
```

In your collection:
```yaml
params:
  api_key: "{{API_KEY}}"
```

### 4. Authentication

Specify authentication at collection or request level:

```yaml
auth_profile: github-work  # Default for all requests

requests:
  - name: public_request
    operation: getPublicData
    # Uses collection auth
    
  - name: different_auth
    operation: getPrivateData
    # Override with --profile flag
```

### 5. Output Formats

- **pretty** (default): Human-readable console output with progress
- **json**: Machine-readable JSON output
- **yaml**: YAML formatted output

### 6. Error Handling

By default, collection execution stops on first error. Use `--continue-on-error` to run all requests regardless of failures.

## Examples

### Basic Collection

```yaml
name: user-workflow
description: Create and verify a user
requests:
  - name: create_user
    operation: users/create
    body:
      name: John Doe
      email: john@example.com
    save_as: user
    
  - name: verify_user
    operation: users/get
    params:
      id: "{{user.id}}"
```

### GitHub API Collection

```yaml
name: github-exploration
variables:
  username: octocat
  
requests:
  - name: get_user
    operation: users/get-by-username
    params:
      username: "{{username}}"
    save_as: user_info
    
  - name: list_repos
    operation: repos/list-for-user
    params:
      username: "{{username}}"
      per_page: 10
      sort: updated
```

### Testing Collection (Phase 2)

```yaml
name: api-tests
requests:
  - name: test_valid_user
    operation: users/get
    params:
      id: 123
    expect:
      status: 200
      body:
        id: 123
        
  - name: test_not_found
    operation: users/get
    params:
      id: 999999
    expect:
      status: 404
```

## Best Practices

1. **Use descriptive names**: Both for collections and individual requests
2. **Document with descriptions**: Help others understand the collection's purpose
3. **Parameterize with variables**: Make collections reusable across environments
4. **Save intermediate results**: Use `save_as` for complex workflows
5. **Validate before running**: Use the validate command to catch errors early
6. **Version control collections**: Store in git for team collaboration

## Directory Structure

```
.mrapids/
├── collections/
│   ├── user-tests.yaml
│   ├── setup-workflow.yaml
│   └── integration-tests.yaml
├── auth/
│   └── profiles.yaml
└── config.yaml
```

## Troubleshooting

### Collection not found
- Check the collection name and directory
- Ensure file has .yaml or .yml extension
- Use `mrapids collection list` to see available collections

### Operation not found
- Validate against your API spec: `mrapids collection validate <name> --spec <spec>`
- Check operation ID matches exactly
- List available operations: `mrapids list operations`

### Variable not resolved
- Check variable is defined in collection or passed via --var
- For environment variables, use --use-env flag
- Variable names are case-sensitive

### Authentication errors
- Verify auth profile exists: `mrapids auth list`
- Check profile is specified correctly
- Use --profile to override collection default

## Future Enhancements

1. **Test Assertions**: Run collections as test suites with pass/fail reporting
2. **Parallel Execution**: Run independent requests concurrently
3. **Conditional Logic**: Skip or run requests based on conditions
4. **Loops and Iteration**: Repeat requests with different data
5. **Import/Export**: Share collections in different formats
6. **Collection Recording**: Generate collections from interactive sessions