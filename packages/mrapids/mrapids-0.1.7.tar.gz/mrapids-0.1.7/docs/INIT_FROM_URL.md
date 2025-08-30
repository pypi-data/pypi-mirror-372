# MicroRapid Init --from-url Feature

## Overview
Initialize MicroRapid projects directly from API specification URLs. The tool automatically:
- Downloads the API specification
- Detects the specification version (Swagger 2.0, OpenAPI 3.0.x, OpenAPI 3.1.x, GraphQL)
- Creates appropriate project structure
- Configures the project with correct base URLs

## Version Detection
MicroRapid automatically detects and displays the API specification version:

- **OpenAPI 3.1.x** - Latest OpenAPI specification
- **OpenAPI 3.0.x** - Including 3.0.0, 3.0.1, 3.0.2, 3.0.3, 3.0.4
- **Swagger 2.0** - Also known as OpenAPI 2.0
- **GraphQL Schema** - GraphQL type definitions
- **AsyncAPI** - For event-driven APIs

## Command Syntax

```bash
mrapids init <project-name> --from-url <schema-url> [options]
```

### Options:
- `--from-url <URL>` - URL to download the schema from
- `--template <type>` - Override auto-detected template (minimal, rest, graphql)
- `--force` - Overwrite existing directory

## Examples

### Popular APIs

#### Petstore API (OpenAPI 3.0.4)
```bash
mrapids init petstore --from-url https://petstore3.swagger.io/api/v3/openapi.json
```
Output:
```
🌐 Fetching schema from: https://petstore3.swagger.io/api/v3/openapi.json
  📋 Detected: OpenAPI 3.0.4
🚀 Initializing MicroRapid project: petstore
  📥 Downloaded schema to: petstore/specs/api.yaml
✅ Project initialized successfully!
```

#### Swagger 2.0 Petstore
```bash
mrapids init petstore-v2 --from-url https://petstore.swagger.io/v2/swagger.json
```
Output:
```
🌐 Fetching schema from: https://petstore.swagger.io/v2/swagger.json
  📋 Detected: Swagger 2.0 (OpenAPI 2.0)
🚀 Initializing MicroRapid project: petstore-v2
```

#### HTTPBin API
```bash
mrapids init httpbin --from-url https://httpbin.org/spec.json
```

#### GitHub API
```bash
mrapids init github-api --from-url https://raw.githubusercontent.com/github/rest-api-description/main/descriptions/api.github.com/api.github.com.json
```

#### Stripe API
```bash
mrapids init stripe-api --from-url https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json
```

## What Gets Created

### Project Structure
```
my-api-project/
├── mrapids.yaml       # Project config with spec version info
├── .gitignore
├── specs/
│   └── api.yaml       # Downloaded and formatted specification
├── tests/
│   └── smoke.test.js
├── scripts/
│   └── .gitkeep
├── config/
│   └── .env.example   # Auto-configured with base URL
└── docs/
    └── README.md
```

### mrapids.yaml
The project configuration includes spec version information:
```yaml
# Spec Version: OpenAPI 3.0.4
# Source: https://petstore3.swagger.io/api/v3/openapi.json
# MicroRapid Project Configuration
name: my-rest-api
version: 1.0.0
type: rest

# Environments (auto-configured from URL)
environments:
  local:
    url: https://petstore3.swagger.io
    config: ./config/.env.local
```

### specs/api.yaml
The downloaded specification includes version information:
- For JSON specs: Kept in original format
- For YAML specs: Version info added as comments
```yaml
# OpenAPI 3.0.4
# Downloaded from: https://petstore3.swagger.io/api/v3/openapi.json
openapi: 3.0.4
info:
  title: Swagger Petstore
  ...
```

## Workflow Example

### 1. Initialize from URL
```bash
mrapids init petstore --from-url https://petstore3.swagger.io/api/v3/openapi.json
```

### 2. Generate Test Scripts
```bash
cd petstore
mrapids setup-tests specs/api.yaml --format npm --output .
```

### 3. Run Operations
```bash
# Using generated npm scripts
npm run api:find-pets-by-status

# Or directly with mrapids
mrapids run specs/api.yaml --operation findPetsByStatus
```

### 4. Generate SDK
```bash
mrapids generate specs/api.yaml --target typescript --output scripts/
```

## Benefits

1. **Quick Setup** - Start testing APIs in seconds
2. **Version Awareness** - Know exactly which spec version you're working with
3. **Auto-Configuration** - Base URLs and environments configured automatically
4. **Format Preservation** - JSON specs stay as JSON, YAML as YAML
5. **Documentation** - Spec source and version tracked in project files

## Supported Formats

- JSON format (`application/json`)
- YAML format (`application/yaml`, `text/yaml`)
- Plain text (`text/plain`)

## Error Handling

The tool validates downloaded content to ensure it's a valid API specification:
- Checks for required keywords (openapi, swagger, paths, type Query)
- Validates HTTP response status
- Provides clear error messages for invalid schemas

## Tips

1. **Check Version**: Always verify the detected version matches your expectations
2. **Review Schema**: Check `specs/api.yaml` after download to ensure completeness
3. **Update Config**: Modify `mrapids.yaml` if you need different environment URLs
4. **Use Templates**: Let auto-detection choose the template, or override with `--template`

## Troubleshooting

### Schema Not Downloading
- Check the URL is accessible
- Ensure it returns a valid API specification
- Try downloading with curl first to debug

### Wrong Version Detected
- Check the actual specification file
- Use `--template` to override auto-detection
- Report issues with version detection

### Base URL Issues
- Manually update `mrapids.yaml` after initialization
- Check `config/.env.example` for environment variables