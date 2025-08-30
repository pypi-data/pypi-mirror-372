# OpenAPI Version Compatibility in MicroRapid

## Overview

MicroRapid handles different OpenAPI/Swagger versions with varying levels of support. This document details the compatibility and limitations for each version.

## Version Support Summary

| Version | Parse | List | Run | Validate | Notes |
|---------|-------|------|-----|----------|-------|
| Swagger 2.0 | ✅ | ✅ | ✅ | ⚠️ | Validation not implemented |
| OpenAPI 3.0 | ✅ | ✅ | ✅ | ✅ | Full support |
| OpenAPI 3.1 | ⚠️ | ⚠️ | ⚠️ | ❌ | Partial support, JSON Schema features cause issues |

## Swagger 2.0 Support

### ✅ What Works:
- **Full parsing** of Swagger 2.0 specifications
- **Parameter references** (`$ref: '#/parameters/name'`)
- **Definition references** (`$ref: '#/definitions/Model'`)
- **Global parameters** at spec level
- **Body parameters** (converted to requestBody internally)
- **Security definitions** (apiKey, oauth2)
- **File responses** (`type: file`)
- **Discriminators** for polymorphism
- **All HTTP methods**

### ⚠️ Limitations:
- **No validation** - Validator shows warning: "Swagger 2.0 validation is not yet implemented"
- **No examples** in spec (Swagger 2.0 didn't support inline examples)

### Example Features:
```yaml
# Global parameters (Swagger 2.0 specific)
parameters:
  limitParam:
    name: limit
    in: query
    type: integer

# Body parameter (Swagger 2.0 style)
parameters:
  - name: body
    in: body
    required: true
    schema:
      $ref: '#/definitions/UserInput'

# File response
responses:
  200:
    description: File content
    schema:
      type: file
```

## OpenAPI 3.0 Support

### ✅ What Works:
- **Full parsing and validation**
- **Multiple servers** with variables
- **Reusable components** (schemas, parameters, requestBodies, responses)
- **Request body** as separate entity
- **Multiple content types** per operation
- **Callbacks** for webhooks
- **Links** between operations
- **Examples** in schemas
- **OAuth2 flows** (authorization code, implicit, etc.)
- **Discriminators** with mapping
- **Nullable** properties

### ✅ OpenAPI 3.0 Specific Features Supported:
```yaml
# Reusable request bodies
components:
  requestBodies:
    UserRequest:
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/User'

# Callbacks
callbacks:
  userCreated:
    '{$request.body#/callbackUrl}':
      post:
        requestBody:
          required: true

# Links
responses:
  '200':
    links:
      GetUserById:
        operationId: getUser
        parameters:
          userId: '$response.body#/id'

# Multiple examples
examples:
  simple:
    summary: Simple example
    value:
      name: "Test"
```

## OpenAPI 3.1 Support

### ⚠️ Partial Support:
OpenAPI 3.1 brings full JSON Schema compatibility, which causes parsing issues in MicroRapid.

### What Works:
- **Basic operations** still parse and run
- **Simple schemas** without advanced JSON Schema features
- **License identifier** field
- **Webhooks** at top level (though not processed differently from paths)

### ❌ What Doesn't Work:
- **Type arrays**: `type: ["string", "null"]` causes schema parsing failures
- **JSON Schema keywords**: 
  - `$id`, `$schema`, `$dynamicRef`, `$dynamicAnchor`
  - `unevaluatedProperties`
  - `prefixItems` (replacement for tuple validation)
  - `dependentSchemas`, `dependentRequired`
  - `patternProperties` with complex patterns
- **External schema references** with `$id`
- **Const keyword** for discriminators
- **Complex conditionals** (if/then/else)
- **Content schemas** in parameters

### Example Issues:
```yaml
# This causes parsing warnings/errors:
schema:
  type: ["string", "null"]  # ❌ Array type not supported

# This fails validation:
properties:
  age:
    type: integer
    exclusiveMinimum: 0  # ❌ Number value not recognized

# This is ignored:
unevaluatedProperties: false  # ❌ JSON Schema 2019-09 feature

# This causes parse errors:
$dynamicRef: "#content"  # ❌ JSON Schema 2020-12 feature
```

## Migration Guide

### Swagger 2.0 → OpenAPI 3.0
MicroRapid handles both well, so migration is straightforward:
- ✅ Both versions work side by side
- ✅ Automatic conversion of body parameters to requestBody
- ✅ Parameter references work in both

### OpenAPI 3.0 → OpenAPI 3.1
⚠️ **Caution**: Upgrading to 3.1 may break parsing:
- ❌ Avoid type arrays - use single types with nullable
- ❌ Don't use advanced JSON Schema features
- ❌ Stick to OpenAPI 3.0 schema subset

## Recommendations

### For Maximum Compatibility:
1. **Use OpenAPI 3.0.x** - Best balance of features and compatibility
2. **Avoid OpenAPI 3.1** unless you need specific features
3. **Swagger 2.0** works fine but lacks modern features

### For OpenAPI 3.1 Users:
1. **Limit JSON Schema usage** to draft-04 compatible features
2. **Use single types** instead of type arrays
3. **Avoid dynamic references** and advanced validation
4. **Test thoroughly** with MicroRapid before committing

### Version Detection:
```bash
# Check which version MicroRapid detects
mrapids validate api.yaml

# Output shows version:
📄 Loading spec from: api.yaml
# For Swagger 2.0: "⚠️  Warning: Swagger 2.0 validation is not yet implemented"
# For OpenAPI 3.0: Proceeds with validation
# For OpenAPI 3.1: May show parsing errors
```

## Future Improvements

1. **Full Swagger 2.0 validation** - Currently shows warning only
2. **OpenAPI 3.1 JSON Schema support** - Handle type arrays and new keywords
3. **Version conversion** - Tool to downgrade 3.1 → 3.0 for compatibility
4. **Better error messages** - Explain which 3.1 features aren't supported

## Summary

- **Swagger 2.0**: ✅ Fully functional (except validation)
- **OpenAPI 3.0**: ✅ Recommended - full support
- **OpenAPI 3.1**: ⚠️ Use with caution - limited JSON Schema support

For production use, **OpenAPI 3.0.x** provides the best experience with MicroRapid.