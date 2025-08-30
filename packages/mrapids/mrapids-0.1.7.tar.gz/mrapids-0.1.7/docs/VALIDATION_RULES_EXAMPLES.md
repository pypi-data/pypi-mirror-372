# Validation Rules Examples: From Source to Implementation

## 1. Official OpenAPI Rules (from OAI Specification)

### OAS 3.0 Specification Requirements
From: https://spec.openapis.org/oas/v3.0.3

```yaml
# Official requirement: "The OpenAPI document MUST contain at least one paths field, a components field or a webhooks field"

# Translated to Spectral rule:
oas3-valid-schema:
  description: "OpenAPI 3.0.x must be a valid schema"
  formats: [oas3]
  given: $
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        required: [openapi, info]
        properties:
          openapi:
            type: string
            pattern: "^3\\.0\\.[0-3]$"
          info:
            type: object
            required: [title, version]
        anyOf:
          - required: [paths]
          - required: [components]
          - required: [webhooks]
```

### OAS 2.0 (Swagger) Requirements
From: https://swagger.io/specification/v2/

```yaml
# Swagger requirement: "basePath must start with /"

swagger2-basepath:
  description: "Swagger 2.0 basePath must start with /"
  formats: [oas2]
  given: $.basePath
  then:
    function: pattern
    functionOptions:
      match: "^/"
```

## 2. Security Rules (from OWASP)

### OWASP API Security Top 10
From: https://owasp.org/www-project-api-security/

```yaml
# API1:2019 Broken Object Level Authorization
# Recommendation: All endpoints must implement authorization

owasp-api1-authorization:
  description: "All operations must define security (OWASP API1:2019)"
  severity: error
  given: $.paths[*][*]
  then:
    field: security
    function: truthy
  message: "Operation must define security to prevent unauthorized access"

# API7:2019 Security Misconfiguration  
# Recommendation: Don't use HTTP in production

owasp-api7-https-only:
  description: "Server URLs must use HTTPS (OWASP API7:2019)"
  severity: error
  given: $.servers[*].url
  then:
    function: pattern
    functionOptions:
      match: "^https://"
  message: "Use HTTPS to prevent man-in-the-middle attacks"
```

## 3. Industry Best Practice Rules

### Zalando RESTful API Guidelines
From: https://opensource.zalando.com/restful-api-guidelines/

```yaml
# Rule 116: Use semantic versioning
zalando-semantic-versioning:
  description: "Must use semantic versioning (Zalando Rule 116)"
  given: $.info.version
  then:
    function: pattern
    functionOptions:
      match: "^(0|[1-9]\\d*)\\.(0|[1-9]\\d*)\\.(0|[1-9]\\d*)"
  message: "Version must follow semantic versioning (e.g., 1.0.0)"

# Rule 134: Use kebab-case for path segments
zalando-kebab-case-paths:
  description: "Path segments must use kebab-case (Zalando Rule 134)"
  given: $.paths[*]~
  then:
    function: pattern
    functionOptions:
      match: "^(/[a-z0-9]+(-[a-z0-9]+)*)+$"
```

### Microsoft Azure API Guidelines
From: https://github.com/microsoft/api-guidelines

```yaml
# Azure: All collections must support pagination
azure-pagination-required:
  description: "Collection endpoints must support pagination (Azure guideline)"
  given: $.paths[*].get[?(@.tags contains 'collection')]
  then:
    function: schema
    functionOptions:
      schema:
        type: object
        properties:
          parameters:
            type: array
            contains:
              oneOf:
                - properties:
                    name: 
                      const: "$top"
                - properties:
                    name:
                      const: "$skip"
```

## 4. MicroRapid-Specific Rules

### CLI Optimization Rules

```yaml
# MicroRapid needs operation IDs for CLI commands
mrapids-operation-id-required:
  description: "Operations must have operationId for CLI usage"
  severity: error
  given: $.paths[*][*]
  then:
    field: operationId
    function: truthy
  message: "operationId is required for 'mrapids run <operation>'"

# MicroRapid benefits from examples for testing
mrapids-examples-recommended:
  description: "Operations should include examples for testing"
  severity: warning
  given: $.paths[*][*].responses[*].content[*]
  then:
    field: example
    function: truthy
  message: "Add examples to enable 'mrapids test' functionality"

# Prevent SSRF in MicroRapid init
mrapids-no-private-servers:
  description: "Server URLs must not point to private networks"
  severity: error
  given: $.servers[*].url
  then:
    function: pattern
    functionOptions:
      notMatch: "(localhost|127\\.0\\.0\\.1|192\\.168\\.|10\\.|172\\.(1[6-9]|2[0-9]|3[01])\\.)"
  message: "Private IPs blocked for security"
```

## 5. How These Become Bundled Rules

### Step 1: Aggregate from Sources
```bash
# Download/copy official rulesets
curl -o spectral-oas.yaml https://raw.githubusercontent.com/stoplightio/spectral/main/packages/rulesets/src/oas/index.json

# Get security guidelines
curl -o owasp-rules.yaml https://example.com/owasp-api-security-rules.yaml

# Industry best practices
curl -o zalando-rules.yaml https://example.com/zalando-api-rules.yaml
```

### Step 2: Merge and Customize
```yaml
# mrapids-complete-ruleset.yaml
extends:
  # Start with official Spectral OAS rules
  - [spectral:oas, all]
  
rules:
  # Override severity for critical rules
  oas3-api-servers:
    severity: error  # Upgrade from warning
    
  # Add security rules
  <<: !include owasp-rules.yaml
  
  # Add style rules
  <<: !include zalando-rules.yaml
  
  # Add MicroRapid-specific rules
  operation-id-required:
    description: "Required for MicroRapid CLI"
    severity: error
    given: $.paths[*][*]
    then:
      field: operationId
      function: truthy
```

### Step 3: Bundle into Binary
```rust
// Include at compile time
pub const BUNDLED_RULES: &str = include_str!("../rules/mrapids-complete-ruleset.yaml");

pub fn get_validation_rules() -> &'static str {
    BUNDLED_RULES
}
```

## Real-World Example

When a user runs validation:

```bash
$ mrapids validate spec api.yaml

🔍 Applying validation rules from:
  ✓ OpenAPI Initiative (core compliance)
  ✓ OWASP (security best practices)
  ✓ Industry standards (Zalando, Microsoft)
  ✓ MicroRapid optimizations

❌ Errors found:
  • Operation missing security definition (OWASP API1:2019)
    at paths > /users > get
    
  • Server URL using HTTP instead of HTTPS (OWASP API7:2019)
    at servers > 0 > url
    
  • Missing operationId (MicroRapid requirement)
    at paths > /users > post

⚠️  Warnings:
  • Version not using semantic versioning (Zalando Rule 116)
    at info > version
    
  • Path not using kebab-case (Zalando Rule 134)
    at paths > /userData
```

## Summary

The validation rules are:
1. **Sourced** from authoritative organizations (OAI, OWASP, industry leaders)
2. **Curated** by the Spectral/tooling community
3. **Customized** by MicroRapid for CLI-specific needs
4. **Bundled** into the binary for offline use
5. **Applied** automatically based on spec version

This gives users enterprise-grade validation without having to be API design experts!