# MicroRapid Parser Capabilities Analysis

## Requirement vs Current Implementation

### 🔍 Smart OpenAPI Parser Requirements

| Feature | Required | MicroRapid Status | Details |
|---------|----------|-------------------|---------|
| **OpenAPI 3.0 Support** | ✅ Full | ✅ **COMPLETE** | Full parsing, validation, all features |
| **OpenAPI 3.1 Support** | ✅ Full | ⚠️ **PARTIAL** | Basic parsing, no JSON Schema 2020-12 |
| **JSON Schema 2020-12** | ✅ Full validation | ❌ **MISSING** | Uses basic validation only |
| **$ref Resolution** | ✅ With inline flattening | ✅ **COMPLETE** | Full resolver with caching |
| **Schema Simplification** | ✅ Flatten oneOf, nullable | ⚠️ **PARTIAL** | Flattens refs, no oneOf simplification |
| **Built-in Linter** | ✅ Like Spectral | ⚠️ **BASIC** | Basic validation, no style rules |

## Current Parser Architecture

### ✅ What MicroRapid Has

#### 1. **Reference Resolution ($ref)**
```rust
// Full reference resolver with caching
pub struct SpecResolver {
    cache: HashMap<String, Value>,
    root: Value,
}

// Supports:
- Internal refs: ✅ `$ref: '#/components/schemas/User'`
- Recursive refs: ✅ Handles circular references
- Caching: ✅ Resolves each ref once
```

**Evidence**:
```bash
# Flatten command resolves all refs
mrapids flatten api.yaml --output resolved.yaml
```

#### 2. **Two-Pass Parsing**
```rust
// Handles mixed arrays of refs and objects
fn parse_openapi_v3(spec_value: &Value) -> Result<UnifiedSpec> {
    // Pass 1: Parse to Value
    // Pass 2: Convert with ref handling
}
```

**Why**: Overcomes serde limitations with untagged enums

#### 3. **Basic Validation**
```bash
mrapids validate api.yaml

# Outputs:
❌ Errors: 
   • Missing required fields
   • Invalid parameter locations
   • Undefined path parameters

⚠️  Warnings:
   • Unused schemas
   • Missing descriptions
```

#### 4. **Format Support**
- Swagger 2.0: ✅ Full support
- OpenAPI 3.0.x: ✅ Full support  
- OpenAPI 3.1: ⚠️ Basic (no JSON Schema features)
- YAML & JSON: ✅ Both supported

### ❌ What MicroRapid Lacks

#### 1. **JSON Schema 2020-12 Features**
```yaml
# These OpenAPI 3.1 features fail:
schema:
  type: ["string", "null"]  # ❌ Array types
  $id: "https://..."         # ❌ Schema identifiers  
  $dynamicRef: "#meta"       # ❌ Dynamic references
  unevaluatedProperties: false # ❌ Advanced validation
  prefixItems: [...]         # ❌ Tuple validation
```

#### 2. **Schema Simplification**
```yaml
# Currently keeps complex structures:
oneOf:
  - $ref: '#/components/schemas/Cat'
  - $ref: '#/components/schemas/Dog'

# Doesn't simplify to discriminated union
```

#### 3. **Advanced Linting**
No style rules like:
- Operation naming conventions
- Description requirements
- Example requirements
- Security best practices

#### 4. **External References**
```yaml
# Not supported:
$ref: 'https://api.example.com/schemas/user.yaml'
$ref: '../common/schemas.yaml#/components/schemas/Error'
```

## Comparison with Advanced Parsers

### MicroRapid vs Ideal Smart Parser

| Aspect | MicroRapid | Ideal Smart Parser |
|--------|------------|--------------------|
| **Parse Speed** | ✅ Fast | ✅ Fast with caching |
| **Memory Usage** | ✅ Efficient | ✅ Streaming for large specs |
| **Error Messages** | ⚠️ Basic | ✅ Detailed with fixes |
| **Ref Resolution** | ✅ Internal only | ✅ Internal + External + HTTP |
| **Validation** | ⚠️ Structure only | ✅ Full JSON Schema |
| **Linting** | ⚠️ Basic | ✅ Configurable rules |
| **Output** | ✅ Unified model | ✅ + Simplified schemas |

### Example: oneOf Simplification

**Input** (Current - kept as-is):
```yaml
requestBody:
  content:
    application/json:
      schema:
        oneOf:
          - $ref: '#/components/schemas/Cat'
          - $ref: '#/components/schemas/Dog'
```

**Ideal Output** (Not implemented):
```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        discriminator:
          propertyName: petType
        required: [petType]
        properties:
          petType:
            type: string
            enum: [cat, dog]
        # Merged properties with conditions
```

## Implementation Gaps

### 1. **To Support Full JSON Schema 2020-12**
Would need:
- New schema parser (not serde-based)
- Type array handling
- Dynamic reference resolver
- Conditional schema evaluator

### 2. **To Add Spectral-like Linting**
Would need:
- Rule engine
- AST visitor pattern
- Configurable rulesets
- Custom rule support

### 3. **To Simplify Schemas**
Would need:
- Schema analyzer
- Pattern detector (discriminators)
- Schema merger
- Nullable flattener

## Current Strengths

Despite gaps, MicroRapid's parser excels at:

1. **Practical Parsing** - Handles real-world specs well
2. **Fast Execution** - No complex validation overhead
3. **Error Recovery** - Continues parsing despite issues
4. **Memory Efficient** - Streaming for large specs
5. **Format Agnostic** - Unified internal model

## Recommendations

### For MicroRapid Users Now:
1. **Use OpenAPI 3.0.x** for best compatibility
2. **Run `flatten`** to resolve refs before sharing
3. **Use external linters** if needed (spectral, etc.)
4. **Keep schemas simple** - avoid complex oneOf

### For MicroRapid Development:
1. **Priority 1**: External ref support (../schemas.yaml)
2. **Priority 2**: Better error messages with fixes
3. **Priority 3**: Basic discriminator detection
4. **Priority 4**: JSON Schema 2020-12 subset
5. **Future**: Full linting engine

## Summary

MicroRapid's parser is **production-ready for common use cases** but lacks advanced features for complex schemas. It prioritizes:

- ✅ **Practical execution** over theoretical completeness
- ✅ **Fast parsing** over deep validation  
- ✅ **Wide compatibility** over latest features

This aligns with its philosophy: "Your API, but executable" - focusing on running APIs rather than perfect validation.