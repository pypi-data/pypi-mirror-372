# Phase 4: Request Dependencies and Conditional Execution

## Overview
Phase 4 introduces advanced flow control features to collections, allowing complex workflows with dependencies, conditions, and intelligent execution ordering.

## Features to Implement

### 1. Request Dependencies (`depends_on`)
Allow requests to declare dependencies on other requests, ensuring proper execution order.

```yaml
requests:
  - name: create_user
    operation: users/create
    body:
      name: "Test User"
    
  - name: get_user_profile
    operation: users/profile
    depends_on: create_user
    params:
      id: "{{create_user.id}}"
      
  - name: update_preferences
    operation: users/preferences
    depends_on: 
      - create_user
      - get_user_profile
    body:
      theme: "dark"
```

### 2. Conditional Execution (`if` / `skip`)
Execute or skip requests based on conditions evaluated at runtime.

```yaml
requests:
  - name: check_feature
    operation: features/status
    save_as: feature_check
    
  - name: use_new_endpoint
    operation: v2/process
    if: "{{feature_check.enabled == true}}"
    
  - name: use_legacy_endpoint
    operation: v1/process
    skip: "{{feature_check.enabled == true}}"
```

### 3. Always Run (`run_always`)
Ensure cleanup/teardown requests run even if previous requests fail.

```yaml
requests:
  - name: setup_test_data
    operation: test/setup
    
  - name: run_test
    operation: test/execute
    
  - name: cleanup
    operation: test/cleanup
    run_always: true  # Runs even if run_test fails
```

### 4. Early Exit Strategies
Stop execution based on critical failures or conditions.

```yaml
name: critical-workflow
options:
  stop_on_critical: true
  
requests:
  - name: auth_check
    operation: auth/verify
    critical: true  # Stops entire collection if this fails
    
  - name: process_data
    operation: data/process
    stop_on_fail: true  # Stops remaining requests if this fails
```

### 5. Retry Logic
Retry failed requests with configurable strategies.

```yaml
requests:
  - name: flaky_endpoint
    operation: external/api
    retry:
      attempts: 3
      delay: 1000  # ms
      backoff: exponential  # or linear
```

## Implementation Details

### 1. Dependency Resolution
- Build dependency graph
- Detect circular dependencies
- Topological sort for execution order
- Parallel execution of independent requests

### 2. Condition Evaluation
- JavaScript-like expression evaluation
- Access to all variables and saved responses
- Support for common operators (==, !=, >, <, &&, ||)
- Type coercion and null safety

### 3. Execution Flow
```
1. Parse collection
2. Build dependency graph
3. Validate no circular dependencies
4. For each request in topological order:
   a. Check if dependencies succeeded
   b. Evaluate conditions (if/skip)
   c. Execute request (with retry if configured)
   d. Save response if needed
   e. Check if should stop (critical/stop_on_fail)
5. Execute run_always requests
```

## Examples

### Example 1: User Registration Flow
```yaml
name: user-registration
requests:
  - name: check_email
    operation: users/check-email
    params:
      email: "{{email}}"
    save_as: email_check
    
  - name: register
    operation: users/register
    if: "{{email_check.available == true}}"
    body:
      email: "{{email}}"
      password: "{{password}}"
    save_as: user
    critical: true
    
  - name: send_verification
    operation: email/send-verification
    depends_on: register
    params:
      user_id: "{{user.id}}"
      
  - name: cleanup_on_failure
    operation: users/delete
    if: "{{user.id != null}}"
    params:
      id: "{{user.id}}"
    run_always: true
    skip: "{{email_check.available == true && send_verification.success == true}}"
```

### Example 2: Data Migration
```yaml
name: data-migration
options:
  stop_on_critical: true
  
requests:
  - name: backup_data
    operation: backup/create
    critical: true
    save_as: backup
    
  - name: migrate_users
    operation: migrate/users
    depends_on: backup_data
    retry:
      attempts: 3
      delay: 5000
      
  - name: migrate_posts
    operation: migrate/posts
    depends_on: backup_data
    retry:
      attempts: 3
      delay: 5000
      
  - name: verify_migration
    operation: migrate/verify
    depends_on:
      - migrate_users
      - migrate_posts
    save_as: verification
    
  - name: rollback
    operation: backup/restore
    if: "{{verification.success == false}}"
    params:
      backup_id: "{{backup.id}}"
    run_always: true
```

### Example 3: A/B Testing
```yaml
name: ab-test
variables:
  test_group: "{{random(['A', 'B'])}}"
  
requests:
  - name: assign_group
    operation: ab/assign
    body:
      user_id: "{{user_id}}"
      group: "{{test_group}}"
      
  - name: feature_a
    operation: feature/a/process
    if: "{{test_group == 'A'}}"
    
  - name: feature_b
    operation: feature/b/process
    if: "{{test_group == 'B'}}"
    
  - name: track_result
    operation: analytics/track
    depends_on:
      - feature_a
      - feature_b
    body:
      group: "{{test_group}}"
      success: true
```

## Benefits
- Complex workflow orchestration
- Proper cleanup handling
- Conditional logic for dynamic flows
- Dependency management
- Resilient execution with retries
- Parallel execution where possible

## CLI Updates
```bash
# Show execution plan
mrapids collection plan <name> --spec <spec>

# Dry run to see what would execute
mrapids collection run <name> --dry-run

# Force sequential execution
mrapids collection run <name> --sequential

# Set retry defaults
mrapids collection run <name> --retry-attempts 3 --retry-delay 1000
```

## Phase 4 Deliverables
1. Dependency graph builder and validator
2. Condition expression evaluator
3. Updated execution engine with flow control
4. Retry mechanism with backoff strategies
5. Execution planner and visualizer
6. Documentation and examples