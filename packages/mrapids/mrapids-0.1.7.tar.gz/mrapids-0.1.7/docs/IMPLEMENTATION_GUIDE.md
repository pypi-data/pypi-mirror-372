# Implementation Guide: Reference-Aware Parsing

## Technical Deep Dive

This guide provides implementation details for developers working with the reference-aware parsing system.

## Core Problem: Serde Untagged Enum Limitation

### The Issue

Serde's `#[serde(untagged)]` attribute attempts to deserialize into each variant in order. When encountering a mixed array like:

```json
[
  { "name": "limit", "in": "query" },
  { "$ref": "#/components/parameters/page" }
]
```

Serde tries to deserialize the second element as a Parameter object, fails (missing "name" field), and reports an error before trying the Reference variant.

### Why Two-Pass Parsing?

1. **First Pass**: Parse as generic Value (always succeeds)
2. **Second Pass**: Inspect each value and route to appropriate type

This approach gives us full control over the deserialization logic.

## Implementation Patterns

### 1. Generic Reference Conversion

```rust
/// Pattern for converting any type that might be a reference
fn convert_value_to_ref_or<T, F>(value: &Value, convert_fn: F) -> Result<ReferenceOr<T>>
where
    T: Clone,
    F: FnOnce(&Value) -> Result<T>,
{
    // Check for $ref first
    if let Some(reference) = value.get("$ref").and_then(|v| v.as_str()) {
        Ok(ReferenceOr::Reference {
            reference: reference.to_string(),
        })
    } else {
        // Attempt conversion to concrete type
        Ok(ReferenceOr::Item(convert_fn(value)?))
    }
}
```

### 2. Array Conversion Pattern

```rust
/// Convert array of potentially mixed references/items
fn convert_array_to_reference_or_parameters(arr: &Vec<Value>) -> Vec<ReferenceOr<Parameter>> {
    arr.iter()
        .filter_map(|v| {
            match convert_value_to_ref_or(v, |val| {
                serde_json::from_value::<Parameter>(val.clone())
                    .context("Failed to parse parameter")
            }) {
                Ok(ref_or_param) => Some(ref_or_param),
                Err(e) => {
                    eprintln!("Warning: Failed to parse parameter: {}", e);
                    None
                }
            }
        })
        .collect()
}
```

### 3. Map Conversion Pattern

```rust
/// Convert HashMap of potentially mixed references/items
fn convert_map_to_reference_or<T, F>(
    map: &serde_json::Map<String, Value>,
    converter: F,
) -> HashMap<String, ReferenceOr<T>>
where
    F: Fn(&Value) -> Result<T>,
    T: Clone,
{
    let mut result = HashMap::new();
    for (key, value) in map {
        match convert_value_to_ref_or(value, |v| converter(v)) {
            Ok(ref_or_item) => {
                result.insert(key.clone(), ref_or_item);
            }
            Err(e) => {
                eprintln!("Warning: Failed to convert {} - {}", key, e);
            }
        }
    }
    result
}
```

## Reference Resolution Strategy

### 1. Caching Architecture

```rust
pub struct SpecResolver {
    components: Option<Components>,
    // Type-specific caches
    parameter_cache: HashMap<String, Parameter>,
    schema_cache: HashMap<String, Schema>,
    response_cache: HashMap<String, Response>,
    request_body_cache: HashMap<String, RequestBody>,
}
```

Benefits:
- Avoids repeated lookups
- Handles circular references gracefully
- Improves performance for large specs

### 2. Resolution Pattern

```rust
pub fn resolve_parameter(&mut self, item: &ReferenceOr<Parameter>) -> Result<Parameter> {
    match item {
        ReferenceOr::Item(p) => Ok(p.clone()),
        ReferenceOr::Reference { reference } => {
            // 1. Check cache first
            if let Some(cached) = self.parameter_cache.get(reference) {
                return Ok(cached.clone());
            }
            
            // 2. Parse reference path
            let param_name = reference.strip_prefix("#/components/parameters/")
                .ok_or_else(|| anyhow::anyhow!("Invalid parameter reference: {}", reference))?;
            
            // 3. Look up in components
            let components = self.components.as_ref()
                .ok_or_else(|| anyhow::anyhow!("No components section found"))?;
            
            // 4. Get the parameter (might itself be a reference)
            let param_ref = components.parameters.as_ref()
                .and_then(|params| params.get(param_name))
                .ok_or_else(|| anyhow::anyhow!("Parameter not found: {}", param_name))?;
            
            // 5. Recursively resolve if needed
            let resolved = match param_ref {
                ReferenceOr::Item(p) => p.clone(),
                ReferenceOr::Reference { .. } => {
                    // Clone to avoid borrow conflicts
                    let param_ref_clone = param_ref.clone();
                    self.resolve_parameter(&param_ref_clone)?
                }
            };
            
            // 6. Cache the result
            self.parameter_cache.insert(reference.clone(), resolved.clone());
            Ok(resolved)
        }
    }
}
```

### 3. Handling Borrow Checker Conflicts

When resolving nested references, we might need to access `self.components` multiple times. Solution:

```rust
// Clone the reference to avoid borrow conflict
let param_ref_clone = param_ref.clone();
// Drop temporary borrows
let _ = components;
let _ = parameters;
// Now we can call self.resolve_parameter again
self.resolve_parameter(&param_ref_clone)?
```

## Flattening Implementation

### 1. Recursive Value Flattening

```rust
fn flatten_value(value: &mut Value, resolver: &mut SpecResolver, path: &mut Vec<String>) -> Result<()> {
    match value {
        Value::Object(map) => {
            // Check if this is a reference object
            if let Some(Value::String(ref_str)) = map.get("$ref") {
                let ref_str = ref_str.clone();
                
                // Resolve the reference
                let resolved = resolve_reference(&ref_str, resolver)?;
                
                // Replace the entire object with resolved value
                *value = resolved;
                
                // Continue flattening the resolved value
                flatten_value(value, resolver, path)?;
            } else {
                // Recursively flatten all values in the object
                for (key, val) in map.iter_mut() {
                    path.push(key.clone());
                    flatten_value(val, resolver, path)?;
                    path.pop();
                }
            }
        }
        Value::Array(arr) => {
            // Recursively flatten all values in the array
            for (i, val) in arr.iter_mut().enumerate() {
                path.push(format!("[{}]", i));
                flatten_value(val, resolver, path)?;
                path.pop();
            }
        }
        _ => {} // Primitive values don't need flattening
    }
    
    Ok(())
}
```

### 2. Reference Resolution for Flattening

```rust
fn resolve_reference(reference: &str, resolver: &mut SpecResolver) -> Result<Value> {
    // Parse the reference path
    if let Some(path) = reference.strip_prefix("#/components/") {
        let parts: Vec<&str> = path.split('/').collect();
        let component_type = parts[0];
        let component_name = parts[1];
        
        // Resolve based on component type
        match component_type {
            "parameters" => {
                let param_ref = ReferenceOr::Reference { reference: reference.to_string() };
                let param = resolver.resolve_parameter(&param_ref)?;
                serde_json::to_value(param).context("Failed to serialize parameter")
            }
            "schemas" => {
                let schema_ref = ReferenceOr::Reference { reference: reference.to_string() };
                let schema = resolver.resolve_schema(&schema_ref)?;
                serde_json::to_value(schema).context("Failed to serialize schema")
            }
            // ... handle other types
            _ => Err(anyhow::anyhow!("Unsupported component type: {}", component_type))
        }
    } else {
        Err(anyhow::anyhow!("Only local references (#/components/...) are currently supported"))
    }
}
```

## Validation Implementation

### 1. Validation Result Structure

```rust
pub struct ValidationResult {
    pub errors: Vec<ValidationError>,
    pub warnings: Vec<ValidationError>,
}

pub struct ValidationError {
    pub path: String,    // JSONPath-like location
    pub message: String, // Human-readable error
}
```

### 2. Path Parameter Validation

```rust
fn extract_path_parameters(path: &str) -> HashSet<String> {
    let mut params = HashSet::new();
    let mut in_param = false;
    let mut current_param = String::new();
    
    for ch in path.chars() {
        if ch == '{' {
            in_param = true;
            current_param.clear();
        } else if ch == '}' {
            if in_param {
                params.insert(current_param.clone());
                in_param = false;
            }
        } else if in_param {
            current_param.push(ch);
        }
    }
    
    params
}
```

### 3. Reference Tracking for Unused Detection

```rust
// Track all referenced components during validation
let mut referenced_params = HashSet::new();
let mut referenced_schemas = HashSet::new();

// When encountering a reference:
if reference.starts_with("#/components/parameters/") {
    let param_name = reference.trim_start_matches("#/components/parameters/");
    referenced_params.insert(param_name.to_string());
}

// After validation, check for unused:
for param_name in params.keys() {
    if !referenced_params.contains(param_name) {
        result.add_warning(
            &format!("components.parameters.{}", param_name),
            "Parameter is defined but never used"
        );
    }
}
```

## Error Handling Best Practices

### 1. Context-Rich Errors

```rust
let content = fs::read_to_string(&cmd.spec)
    .map_err(|e| anyhow::anyhow!("Cannot read spec file: {}", e))?;

let raw_value: serde_yaml::Value = serde_yaml::from_str(content)
    .context("Failed to parse OpenAPI spec as YAML")?;
```

### 2. Graceful Degradation

```rust
// In conversion functions, log warnings but continue
match convert_value_to_ref_or(value, |v| converter(v)) {
    Ok(ref_or_item) => {
        result.insert(key.clone(), ref_or_item);
    }
    Err(e) => {
        eprintln!("Warning: Failed to convert {} - {}", key, e);
        // Continue processing other items
    }
}
```

### 3. User-Friendly Output

```rust
// Provide actionable error messages
if param.location == "path" && param.required != Some(true) {
    result.add_error(
        &format!("{}.parameters[{}]", path, i),
        &format!("Path parameter '{}' must be required", param.name)
    );
}
```

## Performance Considerations

1. **Caching**: All resolved references are cached to avoid repeated lookups
2. **Lazy Evaluation**: Components are only parsed when needed
3. **Early Returns**: Cache checks happen before any parsing
4. **Minimal Cloning**: Use references where possible, clone only when necessary

## Testing Strategies

### 1. Unit Tests for Conversion Functions

```rust
#[test]
fn test_convert_value_to_ref_or() {
    // Test reference
    let ref_value = json!({"$ref": "#/components/parameters/limit"});
    let result = convert_value_to_ref_or(&ref_value, |_| unreachable!()).unwrap();
    assert!(matches!(result, ReferenceOr::Reference { .. }));
    
    // Test inline item
    let item_value = json!({"name": "limit", "in": "query"});
    let result = convert_value_to_ref_or(&item_value, |v| {
        serde_json::from_value::<Parameter>(v.clone())
    }).unwrap();
    assert!(matches!(result, ReferenceOr::Item(_)));
}
```

### 2. Integration Tests with Real Specs

```rust
#[test]
fn test_github_api_spec() {
    let content = fs::read_to_string("tests/fixtures/github-api.yaml").unwrap();
    let result = parse_openapi_v3(&content);
    assert!(result.is_ok());
    let spec = result.unwrap();
    assert!(spec.operations.len() > 700);
}
```

### 3. Validation Tests

```rust
#[test]
fn test_validation_catches_errors() {
    let invalid_spec = r#"
    openapi: 3.0.0
    info:
      title: ""
      version: 1.0.0
    paths:
      /users: {}
    "#;
    
    let doc: OpenAPIDocument = serde_yaml::from_str(invalid_spec).unwrap();
    let result = validate_openapi(&doc);
    
    assert!(!result.is_valid());
    assert!(result.errors.iter().any(|e| e.message.contains("Title cannot be empty")));
}
```

## Debugging Tips

1. **Enable Debug Output**: Temporarily uncomment `eprintln!` statements
2. **Use JSON Output**: `mrapids validate spec.yaml -f json` for structured errors
3. **Test Incrementally**: Use small test specs before large ones
4. **Check Caches**: Add debug prints to see what's being cached
5. **Path Tracking**: The `path` parameter in recursive functions helps locate issues

## Common Pitfalls and Solutions

1. **Borrow Checker Issues**: Clone references when needed for recursive calls
2. **Missing Null Checks**: Always check Option values before unwrapping
3. **Reference Format**: Ensure references start with `#/components/`
4. **Array Indices**: Remember arrays can contain references at any position
5. **Error Propagation**: Use `?` operator consistently for clean error handling

## Future Extension Points

1. **External References**: Add HTTP client for remote refs
2. **Circular Detection**: Implement visited set in resolver
3. **Custom Validators**: Plugin system for domain-specific validation
4. **Performance Metrics**: Add timing information for large specs
5. **Streaming Parser**: For extremely large specifications