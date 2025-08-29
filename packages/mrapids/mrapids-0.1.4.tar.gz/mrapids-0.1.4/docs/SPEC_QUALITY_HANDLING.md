# How MicroRapid Handles Poor Quality API Specifications

## Overview

API specifications often have quality issues that make them difficult to work with. This document shows how MicroRapid handles these challenges.

## Challenge 1: Incomplete or Vague Specifications

### Problem
- Missing request bodies
- Missing response schemas
- Undocumented parameters
- Missing parameter types

### How MicroRapid Handles It

#### ✅ What Works:
- **Parsing**: Can parse specs with missing elements
- **Listing**: Shows all operations even with incomplete definitions
- **Running**: Can execute operations without full schemas

#### ⚠️ Limitations:
- **Example Generation**: Generates empty or minimal examples when schemas are missing
- **No Validation**: Cannot validate requests/responses without schemas
- **No Type Safety**: Missing types default to generic handling

### Example:
```yaml
paths:
  /users:
    post:
      operationId: createUser
      # Missing requestBody
      responses:
        '201':
          description: Created
          # Missing response schema
```

**MicroRapid's Response:**
- ✅ Lists the operation
- ✅ Can run it (sends empty body)
- ⚠️ Cannot generate meaningful examples

## Challenge 2: Complex Schema Combinations (anyOf, allOf, oneOf)

### Problem
- `oneOf` without discriminators
- `anyOf` with unclear selection logic
- `allOf` combining incompatible schemas

### How MicroRapid Handles It

#### ✅ What Works:
- **Parsing**: Successfully parses complex schema combinations
- **Reference Resolution**: Resolves `$ref` within complex schemas

#### ⚠️ Limitations:
- **Example Generation**: Cannot generate meaningful examples for `oneOf` without discriminators
- **Validation**: Cannot determine which schema variant to use
- **User Guidance**: No hints about which variant to choose

### Example:
```yaml
schema:
  oneOf:
    - $ref: '#/components/schemas/Document'
    - $ref: '#/components/schemas/Image'
    - $ref: '#/components/schemas/Video'
  # No discriminator property
```

**MicroRapid's Response:**
- ✅ Parses the schema
- ⚠️ Generates `null` as example data
- ⚠️ User must manually create correct variant

## Challenge 3: Generic/Overused Object Types

### Problem
- Schemas defined as just `type: object`
- `additionalProperties: true` everywhere
- No property definitions
- Arrays without item schemas

### How MicroRapid Handles It

#### ✅ What Works:
- **Flexibility**: Accepts any JSON for generic objects
- **Parsing**: No parsing errors with generic types

#### ⚠️ Limitations:
- **Poor Examples**: Generates empty objects `{}`
- **No Guidance**: Cannot help users understand expected structure
- **No Validation**: Cannot validate if data is correct

### Example:
```yaml
requestBody:
  content:
    application/json:
      schema:
        type: object
        # No properties defined
```

**MicroRapid's Response:**
- ✅ Accepts any JSON object
- ⚠️ Example: `{}`
- ⚠️ No validation possible

## Challenge 4: Inconsistent Parameter Documentation

### Problem
- Query parameters without schemas
- Path parameters missing types
- Headers not documented
- Required fields not marked

### How MicroRapid Handles It

#### ✅ What Works:
- **Default Handling**: Treats undocumented parameters as optional strings
- **Path Parameters**: Still substitutes in URL even without type

#### ⚠️ Limitations:
- **Type Coercion**: May send wrong types (string instead of number)
- **Missing Parameters**: No warning about undocumented parameters
- **Required Detection**: Cannot enforce required parameters without marking

## Best Practices for MicroRapid Users

### 1. Validate Your Spec First
```bash
# Use MicroRapid's validate command
mrapids validate api.yaml

# Consider external validators for comprehensive checks
npx @apidevtools/swagger-cli validate api.yaml
```

### 2. Use the Flatten Command
```bash
# Resolve all references for better visibility
mrapids flatten api.yaml --output resolved.yaml
```

### 3. Generate and Customize Examples
```bash
# Generate examples
mrapids analyze --all

# Then manually improve the generated files
vim data/examples/create-user.json
```

### 4. Progressive Enhancement
1. Start with what works (basic operations)
2. Add schemas incrementally
3. Test as you improve the spec
4. Use discriminators for `oneOf`/`anyOf`

### 5. Workaround Strategies

#### For Missing Request Bodies:
```bash
# Create data file manually
echo '{"name": "John", "email": "john@example.com"}' > data/create-user.json

# Run with explicit data
mrapids run createUser --data @data/create-user.json
```

#### For Generic Objects:
```bash
# Use inline JSON
mrapids run createData --data '{"whatever": "you need"}'
```

#### For Complex Schemas:
```bash
# Create specific examples for each variant
echo '{"type": "document", "content": "..."}' > data/document.json
echo '{"type": "image", "url": "..."}' > data/image.json
```

## Comparison with Other Tools

### MicroRapid Strengths:
- ✅ **Tolerant Parser**: Works with imperfect specs
- ✅ **Flexible Execution**: Can run operations despite missing schemas
- ✅ **No Code Generation**: No compile errors from bad specs

### MicroRapid Limitations:
- ⚠️ **Limited Intelligence**: Cannot infer missing information
- ⚠️ **No Schema Inference**: Doesn't guess types from examples
- ⚠️ **Manual Intervention**: Requires user knowledge for complex cases

## Future Improvements

1. **Smart Defaults**: Generate better examples for generic objects
2. **Schema Inference**: Analyze API responses to suggest schemas
3. **Interactive Mode**: Prompt for missing information
4. **Discriminator Support**: Better handling of `oneOf`/`anyOf`
5. **Validation Warnings**: Warn about spec quality issues

## Summary

MicroRapid takes a **pragmatic approach** to poor quality specs:
- **Parse what's possible**
- **Run what works**
- **Let users fill gaps**

While it can't magically fix bad specs, it provides tools to work around limitations and progressively improve API specifications.

### Key Takeaway
> "MicroRapid works with the spec you have, not the spec you wish you had."

The tool's flexibility allows you to start testing immediately while improving your specification quality over time.