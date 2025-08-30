# Collections Feature - Quick Start

## What are Collections?

Collections allow you to group and execute multiple API requests sequentially. Think of them as "playlists" for your API calls.

## Quick Example

1. Create a collection file `.mrapids/collections/my-first-collection.yaml`:

```yaml
name: my-first-collection
description: Get user info and their repos
variables:
  username: octocat
  
requests:
  - name: get_user
    operation: users/get-by-username
    params:
      username: "{{username}}"
    save_as: user
    
  - name: get_repos
    operation: repos/list-for-user
    params:
      username: "{{username}}"
      per_page: 5
```

2. Run the collection:

```bash
# List available collections
mrapids collection list

# Show collection details
mrapids collection show my-first-collection

# Run the collection
mrapids collection run my-first-collection --spec api.yaml

# Run with different user
mrapids collection run my-first-collection --var username=torvalds

# Save all responses
mrapids collection run my-first-collection --save-all ./results/
```

## Key Features

- **Variables**: Use `{{variable}}` syntax for dynamic values
- **Response Chaining**: Save responses with `save_as` and reference them later
- **Override Options**: Change variables, auth profiles, and more at runtime
- **Multiple Output Formats**: JSON, YAML, or pretty console output
- **Error Handling**: Continue on errors or stop at first failure

## Collection Structure

```yaml
name: collection-name
description: What this collection does
variables:              # Optional: Define reusable values
  key: value
auth_profile: default   # Optional: Default authentication

requests:
  - name: request_1     # Unique name within collection
    operation: op_id    # Operation ID from your API spec
    params:             # Query, path, header parameters
      key: value
    body:               # Request body (if needed)
      key: value
    save_as: var_name   # Save response for later use
```

## Common Use Cases

### 1. API Testing Workflow
```yaml
name: crud-test
requests:
  - name: create
    operation: createResource
    body: { name: "test" }
    save_as: created
    
  - name: read
    operation: getResource
    params: { id: "{{created.id}}" }
    
  - name: update
    operation: updateResource
    params: { id: "{{created.id}}" }
    body: { name: "updated" }
    
  - name: delete
    operation: deleteResource
    params: { id: "{{created.id}}" }
```

### 2. Data Collection
```yaml
name: analytics-gather
requests:
  - name: get_users
    operation: listUsers
    save_as: users
    
  - name: get_stats
    operation: getStatistics
    params: { user_count: "{{users.total}}" }
    
  - name: get_report
    operation: generateReport
    body: { users: "{{users.items}}" }
```

### 3. Environment Setup
```yaml
name: setup-test-env
requests:
  - name: create_test_user
    operation: createUser
    body: { email: "test@example.com" }
    
  - name: create_test_data
    operation: seedData
    params: { type: "test" }
    
  - name: verify_setup
    operation: healthCheck
```

## Tips

1. **Start Simple**: Begin with basic collections and add complexity as needed
2. **Use Variables**: Make collections reusable across environments
3. **Document Well**: Use descriptions to explain what each collection does
4. **Version Control**: Store collections in git for team collaboration
5. **Validate First**: Always validate before running in production

See the full [Collections Documentation](docs/COLLECTIONS.md) for advanced features and examples.