# Who Defines the Validation Rules?

## 1. Official OpenAPI Specification Rules

### Source: OpenAPI Initiative (OAI)
- **Organization**: Linux Foundation project
- **Repository**: https://github.com/OAI/OpenAPI-Specification
- **What they define**: The official specification structure

```yaml
# Example: Official OAS 3.0 requirements
- "openapi" field is required
- "info" object is required
- "paths" or "webhooks" or "components" is required
- Version must match pattern "3.0.[0-3]"
```

### Source: Stoplight (Spectral)
- **Organization**: Stoplight.io (API tooling company)
- **Repository**: https://github.com/stoplightio/spectral
- **What they provide**: Pre-built rulesets that implement OAI specs

```yaml
# Spectral's OAS ruleset (@stoplight/spectral-oas)
extends: [[spectral:oas, all]]

# They maintain rules for:
- OAS 2.0 (Swagger)
- OAS 3.0.x
- OAS 3.1.x
```

## 2. Security Rules

### Source: OWASP (Open Web Application Security Project)
- **API Security Top 10**: https://owasp.org/www-project-api-security/
- **What they define**: Security best practices for APIs

```yaml
# Example OWASP-based rules:
- Enforce HTTPS for all server URLs
- Require authentication on all operations
- Prevent exposure of sensitive data in responses
```

### Source: Industry Best Practices
Companies share their API guidelines:

**Zalando** (E-commerce)
```yaml
# From Zalando RESTful API Guidelines
rules:
  must-use-semantic-versioning:
    message: "API version must follow semantic versioning"
  must-authenticate-all-endpoints:
    message: "All endpoints must define security"
```

**Adidas** (Sportswear)
```yaml
# From Adidas API Guidelines
rules:
  must-use-kebab-case-paths:
    message: "URL paths must use kebab-case"
```

**Microsoft** (Azure API Guidelines)
```yaml
# From Azure REST API Guidelines
rules:
  must-support-pagination:
    message: "Collection endpoints must support pagination"
```

## 3. MicroRapid Custom Rules

### Who Defines: MicroRapid Team (You!)
Based on user needs and common issues:

```yaml
# MicroRapid-specific rules
rules:
  # Prevent SSRF attacks
  no-localhost-servers:
    description: "Prevent SSRF via localhost servers"
    given: $.servers[*].url
    then:
      function: pattern
      functionOptions:
        notMatch: "localhost|127.0.0.1"
        
  # Ensure testability
  operation-id-required:
    description: "Every operation needs an ID for CLI"
    severity: error
```

## 4. Community Contributions

### Source: Open Source Community
- GitHub repos with shared rulesets
- NPM packages with Spectral rules
- Community forums and discussions

```bash
# Popular community rulesets
npm install --save-dev @apisyouwonthate/style-guide
npm install --save-dev @readme/oas-ruleset
npm install --save-dev spectral-aws-apigateway-ruleset
```

## How Rules Are Aggregated

### Layer 1: Core Specification Rules
```yaml
# Based on official OAI specification
oas3-schema: 
  description: "OpenAPI 3.0.x schema validation"
  formats: [oas3]
  given: $
  then:
    function: oas3Schema
```

### Layer 2: Security Rules
```yaml
# Based on OWASP + industry standards
security-rules:
  extends: [[spectral:oas, all]]
  rules:
    # OWASP API1:2019 - Broken Object Level Authorization
    operation-security-defined:
      given: $.paths[*][*]
      then:
        field: security
        function: truthy
```

### Layer 3: Style/Convention Rules
```yaml
# Based on popular style guides
style-rules:
  rules:
    # Google API Design Guide
    paths-camelCase:
      given: $.paths[*]~
      then:
        function: pattern
        functionOptions:
          match: "^/[a-z][a-zA-Z0-9]*"
```

### Layer 4: MicroRapid-Specific Rules
```yaml
# For optimal CLI experience
mrapids-rules:
  rules:
    # Ensure CLI can identify operations
    operation-id-required:
      severity: error
    
    # Ensure examples for testing
    response-examples-required:
      severity: warning
```

## Maintenance and Updates

### Who Maintains What:

1. **OpenAPI Initiative** → Core spec changes
   - Updates when new OAS versions release
   - Example: OAS 3.1 added webhook support

2. **Spectral Team** → Rule engine and base rules
   - Regular updates for bug fixes
   - New functions and capabilities

3. **Security Organizations** → Security guidelines
   - OWASP updates API Security Top 10
   - New threats = new rules

4. **MicroRapid Team** → Integration and custom rules
   - Bundle the best rules
   - Add CLI-specific validations
   - Update based on user feedback

## Practical Implementation

### For MicroRapid:
```rust
// src/validation/rules/mod.rs

pub fn get_bundled_rules() -> RuleSet {
    RuleSet {
        // 1. Core OAS rules from Spectral
        core: include_str!("spectral-oas-rules.yaml"),
        
        // 2. Security rules from OWASP + industry
        security: include_str!("security-rules.yaml"),
        
        // 3. Style rules from popular guides
        style: include_str!("style-rules.yaml"),
        
        // 4. MicroRapid-specific rules
        custom: include_str!("mrapids-rules.yaml"),
    }
}
```

### Updating Rules:
```bash
# Quarterly update process
1. Check Spectral for rule updates
2. Review OWASP for new security guidelines
3. Incorporate user feedback
4. Test with real-world OpenAPI specs
5. Bundle into new MicroRapid release
```

## Summary

The validation rules come from:

1. **Official Sources** (OAI, Spectral) - Core compliance
2. **Security Experts** (OWASP) - Security best practices
3. **Industry Leaders** (Zalando, Microsoft) - Proven patterns
4. **MicroRapid Team** - CLI-specific needs
5. **Community** - Shared wisdom

MicroRapid bundles the best of all these sources into a single, curated ruleset that gives users comprehensive validation out of the box!