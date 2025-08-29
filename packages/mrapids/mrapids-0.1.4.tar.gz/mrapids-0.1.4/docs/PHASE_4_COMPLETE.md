# Phase 4 Complete: Request Dependencies and Conditional Execution

## Summary

Phase 4 has been successfully implemented, adding sophisticated flow control capabilities to the collections feature. This enables users to create complex API workflows with proper dependency management, conditional logic, and error handling.

## Features Implemented

### 1. Request Dependencies ✅
- Requests can declare dependencies using `depends_on`
- Automatic dependency resolution with topological sorting
- Circular dependency detection
- Parallel execution groups identified (future optimization)

### 2. Conditional Execution ✅
- `if` conditions for conditional execution
- `skip` conditions for inverse logic
- Expression evaluation with comparison and boolean operators
- Access to all variables, saved responses, and execution results

### 3. Flow Control ✅
- `run_always` flag for cleanup operations
- `critical` flag to stop execution on failure
- Proper execution state tracking
- Early exit strategies

### 4. Retry Logic ✅
- Per-request retry configuration
- Configurable attempts and delays
- Linear and exponential backoff strategies
- Automatic retry on failure

## Examples

### Dependencies Example
```yaml
requests:
  - name: create_resource
    operation: resources/create
    save_as: resource
    
  - name: configure_resource
    operation: resources/configure
    depends_on: [create_resource]
    params:
      id: "{{resource.id}}"
```

### Conditional Execution Example
```yaml
requests:
  - name: check_feature
    operation: features/check
    save_as: feature
    
  - name: use_new_api
    operation: v2/endpoint
    if: "feature.enabled == true"
    
  - name: use_legacy_api
    operation: v1/endpoint
    skip: "feature.enabled == true"
```

### Critical and Cleanup Example
```yaml
requests:
  - name: critical_setup
    operation: setup
    critical: true  # Stops execution if fails
    
  - name: main_operation
    operation: process
    depends_on: [critical_setup]
    
  - name: cleanup
    operation: cleanup
    run_always: true  # Runs even if others fail
```

### Retry Example
```yaml
requests:
  - name: unreliable_service
    operation: external/api
    retry:
      attempts: 3
      delay: 1000
      backoff: exponential
```

## Technical Implementation

### New Modules
1. **dependency.rs**: Manages dependency graphs and execution order
2. **condition.rs**: Evaluates conditional expressions

### Updated Components
1. **models.rs**: Added new fields to CollectionRequest
2. **executor.rs**: New execute_with_dependencies method
3. **mod.rs**: Included new modules

## Testing

Created comprehensive test collections:
- **dependency-test.yaml**: Tests all dependency and condition features
- **critical-retry-test.yaml**: Tests critical failures and retry logic

All tests passing with correct behavior:
- Dependencies resolve in correct order
- Conditions evaluate properly
- run_always requests execute even after failures
- Retry logic works with backoff strategies

## Next Steps

With Phase 4 complete, the collections feature now supports:
- ✅ Core collection execution (Phase 1)
- ✅ Testing with assertions (Phase 2)
- ✅ Advanced variables and environment (Phase 3)
- ✅ Dependencies and conditional execution (Phase 4)

Ready for Phase 5: Enhanced test assertions and reporting.