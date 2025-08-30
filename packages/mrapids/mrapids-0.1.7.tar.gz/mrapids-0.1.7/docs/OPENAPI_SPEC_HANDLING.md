# OpenAPI 3.0/3.1 Specification Handling in MicroRapid

## Overview

MicroRapid implements a custom OpenAPI parser that handles both OpenAPI 3.0 and 3.1 specifications, with special focus on proper `$ref` reference handling. This document explains the architecture, libraries used, and implementation details.

## Libraries Used

### 1. **openapiv3** Crate (Initial Attempt - Limited Use)
```toml
openapiv3 = "1.0"
```

**Why we moved away from it:**
- The `openapiv3` crate uses serde's `#[serde(untagged)]` for handling `$ref` references
- This causes parsing failures when arrays contain mixed types (inline objects + references)
- Example failure:
  ```yaml
  parameters:
    - name: limit      # Inline parameter
      in: query
    - $ref: '#/components/parameters/pageParam'  # Reference - causes failure
  ```
- Error: `missing field 'name'` because serde tries to parse the reference as a Parameter object

**Current use:**
- Still used in `src/core/spec.rs` for backward compatibility
- Being phased out in favor of custom parsing

### 2. **serde_yaml** and **serde_json**
```toml
serde_yaml = "0.9"
serde_json = "1.0"
```

**Primary parsing libraries:**
- `serde_yaml::Value` - Generic YAML parsing (first pass)
- `serde_json::Value` - JSON manipulation and conversion
- Used for two-pass parsing approach

### 3. **serde** Framework
```toml
serde = { version = "1.0", features = ["derive"] }
```

**For custom deserialization:**
- `#[derive(Deserialize, Serialize)]` for all OpenAPI models
- Custom `ReferenceOr<T>` enum with untagged deserialization
- Manual conversion functions for proper reference handling

## Architecture: Two-Pass Parsing

### Why Two-Pass?

The fundamental issue with single-pass parsing:
```rust
// This fails with mixed arrays
#[derive(Deserialize)]
#[serde(untagged)]
enum ReferenceOr<T> {
    Reference { #[serde(rename = "$ref")] reference: String },
    Item(T),
}
```

When serde encounters `{"$ref": "..."}`, it:
1. Tries to deserialize as `Item(T)` first (due to untagged)
2. Fails because `$ref` doesn't match expected fields
3. Never tries the `Reference` variant

### Our Solution: Two-Pass Parsing

```rust
pub fn parse_openapi_v3(content: &str) -> Result<UnifiedSpec> {
    // Pass 1: Parse as generic Value
    let raw_value: serde_yaml::Value = serde_yaml::from_str(content)?;
    let json_value: Value = serde_json::to_value(raw_value)?;
    
    // Pass 2: Manual conversion with reference detection
    let openapi = convert_value_to_openapi_doc(&json_value)?;
    
    // Create resolver and process references
    let mut resolver = SpecResolver::new(openapi.components.clone());
    // ... convert to UnifiedSpec
}
```

## Reference Handling (`$ref`)

### 1. Reference Model

```rust
#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(untagged)]
pub enum ReferenceOr<T> {
    Reference {
        #[serde(rename = "$ref")]
        reference: String,
    },
    Item(T),
}
```

### 2. Generic Conversion Utility

```rust
fn convert_value_to_ref_or<T, F>(value: &Value, convert_fn: F) -> Result<ReferenceOr<T>>
where
    T: Clone,
    F: FnOnce(&Value) -> Result<T>,
{
    // Check if it's a reference FIRST
    if let Some(reference) = value.get("$ref").and_then(|v| v.as_str()) {
        Ok(ReferenceOr::Reference {
            reference: reference.to_string(),
        })
    } else {
        // Only then try to convert to the actual type
        Ok(ReferenceOr::Item(convert_fn(value)?))
    }
}
```

### 3. Reference Resolution with Caching

```rust
pub struct SpecResolver {
    components: Option<Components>,
    parameter_cache: HashMap<String, Parameter>,
    schema_cache: HashMap<String, Schema>,
    response_cache: HashMap<String, Response>,
    request_body_cache: HashMap<String, RequestBody>,
}

impl SpecResolver {
    pub fn resolve_parameter(&mut self, item: &ReferenceOr<Parameter>) -> Result<Parameter> {
        match item {
            ReferenceOr::Item(p) => Ok(p.clone()),
            ReferenceOr::Reference { reference } => {
                // 1. Check cache
                if let Some(cached) = self.parameter_cache.get(reference) {
                    return Ok(cached.clone());
                }
                
                // 2. Parse reference (e.g., "#/components/parameters/limitParam")
                let param_name = reference
                    .strip_prefix("#/components/parameters/")
                    .ok_or_else(|| anyhow!("Invalid reference"))?;
                
                // 3. Look up in components
                let param = self.components
                    .as_ref()
                    .and_then(|c| c.parameters.as_ref())
                    .and_then(|p| p.get(param_name))
                    .ok_or_else(|| anyhow!("Parameter not found"))?;
                
                // 4. Recursively resolve if it's another reference
                let resolved = match param {
                    ReferenceOr::Item(p) => p.clone(),
                    ReferenceOr::Reference { .. } => {
                        self.resolve_parameter(&param.clone())?
                    }
                };
                
                // 5. Cache result
                self.parameter_cache.insert(reference.clone(), resolved.clone());
                Ok(resolved)
            }
        }
    }
}
```

## OpenAPI 3.0 vs 3.1 Differences

### Detection
```rust
// OpenAPI 3.0
openapi: "3.0.0"
openapi: "3.0.1"
openapi: "3.0.2"
openapi: "3.0.3"

// OpenAPI 3.1
openapi: "3.1.0"
```

### Key Differences Handled

1. **JSON Schema Compatibility**
   - 3.1 uses full JSON Schema Draft 2020-12
   - 3.0 uses a subset of JSON Schema Draft 7
   - Our Schema model supports both:
   ```rust
   pub struct Schema {
       #[serde(rename = "type")]
       pub schema_type: Option<String>,
       pub format: Option<String>,
       pub items: Option<Box<ReferenceOr<Schema>>>,
       pub properties: Option<HashMap<String, ReferenceOr<Schema>>>,
       pub required: Option<Vec<String>>,
       // Common to both versions
       pub default: Option<Value>,
       pub example: Option<Value>,
       pub enum_values: Option<Vec<Value>>,
       // 3.1 specific (but safe to include)
       pub minimum: Option<f64>,
       pub maximum: Option<f64>,
   }
   ```

2. **Reference Handling**
   - Both versions use JSON Reference (RFC 6901)
   - Format: `#/components/schemas/ModelName`
   - External refs: `./external.yaml#/components/schemas/Model`
   - Currently support local refs only

3. **Nullable Types**
   - 3.0: `nullable: true` property
   - 3.1: `type: ["string", "null"]` array
   - We handle both patterns in schema parsing

## Data Models

### Core OpenAPI Structure
```rust
pub struct OpenAPIDocument {
    pub openapi: String,  // Version: "3.0.0" or "3.1.0"
    pub info: Info,
    pub servers: Option<Vec<Server>>,
    pub paths: HashMap<String, PathItem>,
    pub components: Option<Components>,
    // Optional fields
    pub security: Option<Vec<SecurityRequirement>>,
    pub tags: Option<Vec<Tag>>,
    pub externalDocs: Option<ExternalDocumentation>,
}
```

### Path and Operations
```rust
pub struct PathItem {
    #[serde(rename = "$ref")]
    pub reference: Option<String>,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub get: Option<Operation>,
    pub put: Option<Operation>,
    pub post: Option<Operation>,
    pub delete: Option<Operation>,
    pub options: Option<Operation>,
    pub head: Option<Operation>,
    pub patch: Option<Operation>,
    pub trace: Option<Operation>,
    pub servers: Option<Vec<Server>>,
    pub parameters: Option<Vec<ReferenceOr<Parameter>>>,
}

pub struct Operation {
    pub tags: Option<Vec<String>>,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub externalDocs: Option<ExternalDocumentation>,
    pub operationId: Option<String>,
    pub parameters: Option<Vec<ReferenceOr<Parameter>>>,
    pub requestBody: Option<ReferenceOr<RequestBody>>,
    pub responses: HashMap<String, ReferenceOr<Response>>,
    pub callbacks: Option<HashMap<String, ReferenceOr<Callback>>>,
    pub deprecated: Option<bool>,
    pub security: Option<Vec<SecurityRequirement>>,
    pub servers: Option<Vec<Server>>,
}
```

### Components (Reusable Objects)
```rust
pub struct Components {
    pub schemas: Option<HashMap<String, ReferenceOr<Schema>>>,
    pub responses: Option<HashMap<String, ReferenceOr<Response>>>,
    pub parameters: Option<HashMap<String, ReferenceOr<Parameter>>>,
    pub examples: Option<HashMap<String, ReferenceOr<Example>>>,
    pub requestBodies: Option<HashMap<String, ReferenceOr<RequestBody>>>,
    pub headers: Option<HashMap<String, ReferenceOr<Header>>>,
    pub securitySchemes: Option<HashMap<String, ReferenceOr<SecurityScheme>>>,
    pub links: Option<HashMap<String, ReferenceOr<Link>>>,
    pub callbacks: Option<HashMap<String, ReferenceOr<Callback>>>,
}
```

## Unified Spec Format

After parsing, we convert to a simplified unified format:

```rust
pub struct UnifiedSpec {
    pub info: ApiInfo,
    pub base_url: String,
    pub operations: Vec<UnifiedOperation>,
    pub security_schemes: HashMap<String, SecurityScheme>,
}

pub struct UnifiedOperation {
    pub operation_id: String,
    pub method: String,
    pub path: String,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub parameters: Vec<UnifiedParameter>,
    pub request_body: Option<UnifiedRequestBody>,
    pub responses: Vec<UnifiedResponse>,
    pub security: Vec<SecurityRequirement>,
}
```

## Reference Resolution Process

### 1. Parameter References
```yaml
# In operation
parameters:
  - $ref: '#/components/parameters/limitParam'

# In components
components:
  parameters:
    limitParam:
      name: limit
      in: query
      schema:
        type: integer
```

Resolution flow:
1. Detect `$ref` in parameters array
2. Extract reference path: `#/components/parameters/limitParam`
3. Look up in `components.parameters.limitParam`
4. Return resolved Parameter object
5. Cache for future use

### 2. Schema References (Most Complex)
```yaml
# Nested schema references
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        profile:
          $ref: '#/components/schemas/UserProfile'
        addresses:
          type: array
          items:
            $ref: '#/components/schemas/Address'
```

Challenges:
- Schemas can reference other schemas recursively
- Array items can be references
- Properties can be references
- Additional properties can be references

### 3. Response References
```yaml
responses:
  '200':
    $ref: '#/components/responses/UserResponse'
  '404':
    $ref: '#/components/responses/NotFound'
```

### 4. Request Body References
```yaml
requestBody:
  $ref: '#/components/requestBodies/UserInput'
```

## Error Handling

### Common Parsing Errors

1. **Mixed Array Error (Before Fix)**
   ```
   paths./users.get.parameters[1]: missing field `name` at line 17 column 11
   ```

2. **Invalid Reference**
   ```
   Invalid parameter reference: #/invalid/path/param
   ```

3. **Missing Component**
   ```
   Parameter not found: nonExistentParam
   ```

### Error Recovery Strategies

1. **Graceful Degradation**
   ```rust
   // Skip invalid parameters but continue parsing
   arr.iter()
       .filter_map(|v| {
           match convert_value_to_ref_or(v, |val| {...}) {
               Ok(ref_or_param) => Some(ref_or_param),
               Err(e) => {
                   eprintln!("Warning: Failed to parse parameter: {}", e);
                   None  // Skip this parameter
               }
           }
       })
       .collect()
   ```

2. **Validation After Parsing**
   - Parse first, validate later
   - Separate concerns: parsing vs business rules
   - Better error messages with context

## Performance Optimizations

### 1. Caching
- All resolved references are cached
- Prevents repeated lookups
- Essential for large specs (GitHub has 700+ operations)

### 2. Lazy Resolution
- References resolved only when needed
- Not all operations use all components
- Faster initial parsing

### 3. Parallel Processing
- Operations can be processed in parallel after parsing
- Each operation's references resolved independently

## Testing Strategy

### Test Cases
1. **Simple References**: Basic parameter/schema refs
2. **Nested References**: Refs pointing to refs
3. **Mixed Arrays**: Inline + reference parameters
4. **Large Specs**: GitHub (8MB), Stripe, OpenAI APIs
5. **Invalid Specs**: Missing refs, circular refs

### Example Test Spec
```yaml
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths:
  /users/{id}:
    parameters:
      - $ref: '#/components/parameters/pathId'
    get:
      parameters:
        - $ref: '#/components/parameters/includeParam'
        - name: fields
          in: query
          schema:
            type: array
            items:
              type: string
      responses:
        '200':
          $ref: '#/components/responses/UserResponse'
components:
  parameters:
    pathId:
      name: id
      in: path
      required: true
      schema:
        type: string
    includeParam:
      $ref: '#/components/parameters/baseInclude'
    baseInclude:
      name: include
      in: query
      schema:
        type: array
  responses:
    UserResponse:
      description: User found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/User'
  schemas:
    User:
      type: object
      properties:
        id:
          type: string
        email:
          type: string
```

## Future Enhancements

### 1. External References
```yaml
$ref: './common/parameters.yaml#/components/parameters/pagination'
$ref: 'https://api.example.com/schemas/user.json'
```

### 2. Circular Reference Detection
- Track resolution path
- Detect cycles: A → B → C → A
- Provide clear error messages

### 3. OpenAPI 3.1 Full Support
- JSON Schema 2020-12 features
- `prefixItems` for tuple validation
- `unevaluatedProperties`
- Conditional schemas (`if`/`then`/`else`)

### 4. Performance Improvements
- Streaming parser for huge specs
- Incremental validation
- Memory-mapped file support

## Conclusion

MicroRapid's OpenAPI handling provides:
- ✅ Robust reference resolution
- ✅ Support for complex real-world specs
- ✅ Clear error messages
- ✅ Performance optimization through caching
- ✅ Extensible architecture for future enhancements

The two-pass parsing approach successfully overcomes serde's limitations while maintaining type safety and providing excellent performance.