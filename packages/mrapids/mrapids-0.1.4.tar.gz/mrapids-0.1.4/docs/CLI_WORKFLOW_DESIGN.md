# MicroRapid CLI Workflow Design

## Problem Statement
- Writing JSON payloads in CLI commands is painful
- Headers, query params, and filters are hard to manage
- No way to save and reuse complex requests
- Need to remember exact parameter names and formats

## Solution: File-Based Request Management

### Core Philosophy
- **Files over flags** - Complex data lives in files, not CLI arguments
- **Save and reuse** - Every successful request can be saved
- **Progressive disclosure** - Start simple, add complexity as needed
- **No interactive UI** - Pure CLI with smart defaults

## Workflow Design

### Step 1: Initialize Workspace

```bash
# Basic init (creates structure)
mrapids init my-api

# Init with schema URL
mrapids init my-api --from-url https://petstore3.swagger.io/api/v3/openapi.json

# Init with local spec file
mrapids init my-api --spec ./openapi.yaml
```

**Creates structure:**
```
my-api/
├── specs/           # API specifications
│   └── api.yaml
├── requests/        # Saved request configurations
│   └── examples/    # Auto-generated examples
├── data/            # Request payloads
│   └── examples/    # Auto-generated payload examples
├── responses/       # Saved responses (optional)
└── mrapids.yaml     # Project configuration
```

### Step 2: Analyze Specification

```bash
# Analyze and generate examples for all operations
mrapids analyze

# Analyze specific operation
mrapids analyze --operation createPet

# List all available operations
mrapids list
```

**What `analyze` does:**
1. Parses the OpenAPI/Swagger spec
2. For each operation, generates:
   - Request configuration file
   - Example payload (if needed)
   - Header requirements
   - Parameter templates

**Example output:**
```
🔍 Analyzing specs/api.yaml...

✅ Found 20 operations
📝 Generating request templates...

Created:
  requests/examples/pet-create.yaml
  requests/examples/pet-get.yaml
  requests/examples/pet-update.yaml
  requests/examples/pet-delete.yaml
  data/examples/pet-create.json
  data/examples/pet-update.json
  ...

Run 'mrapids list' to see all operations
Run 'mrapids run <operation>' to execute
```

### Step 3: Request Configuration Format

**requests/examples/pet-create.yaml:**
```yaml
# Auto-generated from OpenAPI spec
operation: createPet
method: POST
path: /pet

# Headers (can be overridden)
headers:
  Content-Type: application/json
  Accept: application/json
  # API-Key: ${API_KEY}  # Uncomment if needed

# Query parameters
params:
  # key: value

# Path parameters
path_params:
  # petId: 123

# Request body (points to data file)
body: data/examples/pet-create.json

# Response validation
expect:
  status: 200
  # contains: ["id", "name"]
```

**data/examples/pet-create.json:**
```json
{
  "id": 0,
  "name": "Buddy",
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "photoUrls": [
    "https://example.com/photo.jpg"
  ],
  "tags": [
    {
      "id": 1,
      "name": "friendly"
    }
  ],
  "status": "available"
}
```

### Step 4: Run and Save Requests

#### Basic Execution
```bash
# Run using example request
mrapids run pet-create

# Run with custom data file
mrapids run pet-create --data my-pet.json

# Run with inline overrides
mrapids run pet-create --set name=Max --set status=pending

# Run and save as new request
mrapids run pet-create --save-as my-custom-pet
```

#### Direct Operation Execution
```bash
# Run by operation ID (uses generated example)
mrapids run-op createPet

# Run with custom data
mrapids run-op createPet --data my-data.json

# Run with inline JSON
mrapids run-op createPet --json '{"name":"Rex","status":"available"}'

# Run with parameters
mrapids run-op getPetById --param petId=123
```

#### Save Successful Requests
```bash
# After successful run, save for reuse
mrapids run pet-create --save-as test-pet-max

# This creates:
#   requests/test-pet-max.yaml  (request config)
#   data/test-pet-max.json      (payload used)
```

### Step 5: Request Management

```bash
# List saved requests
mrapids list requests
┌──────────────────┬──────────┬─────────────────┬──────────────┐
│ Name             │ Method   │ Path            │ Last Run     │
├──────────────────┼──────────┼─────────────────┼──────────────┤
│ pet-create       │ POST     │ /pet            │ Never        │
│ test-pet-max     │ POST     │ /pet            │ 2 mins ago   │
│ get-production   │ GET      │ /pet/123        │ 1 hour ago   │
└──────────────────┴──────────┴─────────────────┴──────────────┘

# List operations from spec
mrapids list operations
┌──────────────────┬──────────┬─────────────────┬──────────────┐
│ Operation ID     │ Method   │ Path            │ Has Example  │
├──────────────────┼──────────┼─────────────────┼──────────────┤
│ createPet        │ POST     │ /pet            │ ✓            │
│ getPetById       │ GET      │ /pet/{petId}    │ ✓            │
│ updatePet        │ PUT      │ /pet            │ ✓            │
│ deletePet        │ DELETE   │ /pet/{petId}    │ ✓            │
└──────────────────┴──────────┴─────────────────┴──────────────┘

# Search requests
mrapids list requests --filter pet
mrapids list operations --method POST
```

### Step 6: Advanced Features

#### Environments
```yaml
# mrapids.yaml
environments:
  dev:
    base_url: http://localhost:3000
    headers:
      API-Key: dev-key-123
  staging:
    base_url: https://staging.api.com
    headers:
      API-Key: ${STAGING_API_KEY}
  production:
    base_url: https://api.com
    headers:
      API-Key: ${PROD_API_KEY}
```

```bash
# Run with environment
mrapids run pet-create --env staging
mrapids run pet-create --env production
```

#### Batch Testing
```bash
# Run multiple requests in sequence
mrapids batch requests/test-suite/*.yaml

# Run with specific environment
mrapids batch requests/smoke-tests/*.yaml --env staging
```

#### Response Assertions
```yaml
# In request file
expect:
  status: 200
  headers:
    Content-Type: application/json
  body:
    id: "${any}"
    name: "Buddy"
    status: "available"
```

## Command Reference

### Core Commands
```bash
# Initialize
mrapids init <name> [--from-url URL] [--spec FILE]

# Analyze spec and generate examples  
mrapids analyze [--operation OPERATION]

# List operations or requests
mrapids list [operations|requests] [--filter TEXT] [--method METHOD]

# Run requests
mrapids run <request-name> [options]
mrapids run-op <operation-id> [options]

# Save/manage requests
mrapids save <name> --from-last
mrapids copy <source> <dest>
mrapids delete <request-name>
```

### Run Options
```bash
--data FILE          # Use different data file
--json JSON          # Inline JSON payload
--set KEY=VALUE      # Override specific fields
--param KEY=VALUE    # Set path/query parameters  
--header KEY=VALUE   # Add/override headers
--env NAME           # Use environment config
--save-as NAME       # Save successful request
--output FILE        # Save response to file
--verbose           # Show full request/response
```

## Example User Session

```bash
# 1. Initialize project
$ mrapids init petstore --from-url https://petstore3.swagger.io/api/v3/openapi.json
✅ Downloaded OpenAPI spec
✅ Created project structure

# 2. Analyze and generate examples
$ mrapids analyze
✅ Generated 20 request examples
✅ Generated 8 data templates

# 3. List available operations
$ mrapids list operations --method POST
┌──────────────────┬──────────┬─────────────────┬──────────────┐
│ Operation ID     │ Method   │ Path            │ Has Example  │
├──────────────────┼──────────┼─────────────────┼──────────────┤
│ createPet        │ POST     │ /pet            │ ✓            │
│ placeOrder       │ POST     │ /store/order    │ ✓            │
│ createUser       │ POST     │ /user           │ ✓            │
└──────────────────┴──────────┴─────────────────┴──────────────┘

# 4. Run an example request
$ mrapids run pet-create
🚀 POST https://petstore3.swagger.io/api/v3/pet
✅ 200 OK
Response saved to: responses/pet-create-2024-01-15.json

# 5. Modify and run again
$ vi data/examples/pet-create.json
# (change name to "Max")

$ mrapids run pet-create --save-as max-pet
🚀 POST https://petstore3.swagger.io/api/v3/pet
✅ 200 OK
✅ Saved request as 'max-pet'

# 6. Run saved request
$ mrapids run max-pet
🚀 POST https://petstore3.swagger.io/api/v3/pet
✅ 200 OK

# 7. Quick operation with parameters
$ mrapids run-op getPetById --param petId=123
🚀 GET https://petstore3.swagger.io/api/v3/pet/123
✅ 200 OK
{
  "id": 123,
  "name": "Max",
  ...
}
```

## Benefits of This Approach

1. **No Complex CLI Input** - Payloads live in files, not command line
2. **Reusable** - Save successful requests for regression testing
3. **Discoverable** - Generated examples show what's possible
4. **Versionable** - All configs and data in Git-friendly files
5. **CI/CD Ready** - Easy to integrate in automated pipelines
6. **Progressive** - Start with examples, customize as needed

## Implementation Priority

### Phase 1: Core (MVP)
- [x] `init` with --from-url
- [ ] `analyze` command to generate examples
- [ ] `run` with file-based configs
- [ ] `list` operations and requests

### Phase 2: Enhancements
- [ ] `--save-as` functionality
- [ ] `--set` parameter overrides
- [ ] Environment support
- [ ] Response validation

### Phase 3: Advanced
- [ ] Batch execution
- [ ] Response assertions
- [ ] Test report generation
- [ ] Collection export (Postman, Insomnia)