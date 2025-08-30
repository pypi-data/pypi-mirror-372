# MicroRapid SDK Generation Examples

## Real-World SDK Generation Scenarios

### 1. Basic SDK Generation

```bash
# TypeScript SDK for a REST API
mrapids sdk petstore.yaml --lang typescript --output ./sdk-ts

# Python SDK with httpx
mrapids sdk petstore.yaml --lang python --output ./sdk-python

# Go SDK with zero dependencies
mrapids sdk petstore.yaml --lang go --output ./sdk-go
```

### 2. Generated TypeScript SDK Usage

```typescript
// Import the generated client
import { ApiClient } from './sdk-ts';

// Initialize with configuration
const api = new ApiClient({
    baseUrl: 'https://petstore3.swagger.io/api/v3',
    auth: {
        apiKey: {
            key: process.env.API_KEY,
            in: 'header'
        }
    }
});

// Use type-safe methods
async function example() {
    // Create a pet
    const newPet = await api.addPet({
        name: 'Fluffy',
        status: 'available',
        photoUrls: ['https://example.com/fluffy.jpg']
    });
    
    // Find pets by status
    const availablePets = await api.findPetsByStatus({
        status: 'available'
    });
    
    // Update a pet
    await api.updatePet({
        id: 123,
        name: 'Fluffy Updated',
        status: 'sold'
    });
}
```

### 3. Generated Python SDK Usage

```python
from sdk_python import ApiClient, ApiConfig, ApiError

# Configure the client
config = ApiConfig(
    base_url="https://petstore3.swagger.io/api/v3",
    api_key="your-api-key",
    timeout=30.0,
    max_retries=3
)

# Initialize client
client = ApiClient(config)

# Use the SDK
try:
    # Add a new pet
    new_pet = client.add_pet(body={
        "name": "Buddy",
        "status": "available",
        "photoUrls": ["https://example.com/buddy.jpg"]
    })
    
    # Find pets by status
    pets = client.find_pets_by_status(status="available")
    
    # Get a specific pet
    pet = client.get_pet_by_id(pet_id=123)
    
except ApiError as e:
    print(f"API Error: {e.message} (Status: {e.status_code})")
```

### 4. Generated Go SDK Usage

```go
package main

import (
    "context"
    "fmt"
    "log"
    
    petstore "github.com/yourcompany/sdk-go"
)

func main() {
    // Create client with config
    config := &petstore.Config{
        BaseURL: "https://petstore3.swagger.io/api/v3",
        APIKey:  "your-api-key",
        Timeout: 30 * time.Second,
    }
    
    client := petstore.NewClient(config)
    ctx := context.Background()
    
    // Add a pet
    newPet, err := client.AddPet(ctx, &petstore.Pet{
        Name:      "Max",
        Status:    "available",
        PhotoURLs: []string{"https://example.com/max.jpg"},
    })
    if err != nil {
        log.Fatal(err)
    }
    
    // Find pets by status
    pets, err := client.FindPetsByStatus(ctx, "available")
    if err != nil {
        log.Fatal(err)
    }
    
    fmt.Printf("Found %d available pets\n", len(pets))
}
```

### 5. Advanced Configuration Examples

#### TypeScript with Custom Headers
```typescript
const api = new ApiClient({
    baseUrl: 'https://api.example.com',
    headers: {
        'X-Custom-Header': 'value',
        'X-Request-ID': generateRequestId()
    },
    timeout: 60000, // 60 seconds
    resilience: {
        maxRetries: 3,
        retryDelay: 1000
    }
});
```

#### Python with OAuth
```python
config = ApiConfig(
    base_url="https://api.example.com",
    bearer_token=get_oauth_token(),
    headers={
        "X-Client-Version": "1.0.0"
    }
)

# Token refresh on 401
async def with_token_refresh():
    try:
        result = await client.protected_endpoint()
    except ApiError as e:
        if e.status_code == 401:
            config.bearer_token = refresh_oauth_token()
            result = await client.protected_endpoint()
```

#### Go with Context and Timeouts
```go
// Per-request timeout
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()

pet, err := client.GetPetById(ctx, "123")

// With custom headers per request
ctx = context.WithValue(ctx, "headers", map[string]string{
    "X-Request-ID": uuid.New().String(),
})
```

### 6. CI/CD Integration

#### GitHub Actions
```yaml
name: Generate SDKs
on:
  push:
    paths:
      - 'api/openapi.yaml'

jobs:
  generate-sdks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install MicroRapid
        run: npm install -g mrapids
      
      - name: Generate TypeScript SDK
        run: mrapids sdk api/openapi.yaml --lang typescript --output ./sdks/typescript
      
      - name: Generate Python SDK
        run: mrapids sdk api/openapi.yaml --lang python --output ./sdks/python
      
      - name: Generate Go SDK
        run: mrapids sdk api/openapi.yaml --lang go --output ./sdks/go
      
      - name: Commit SDKs
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add sdks/
          git commit -m "chore: regenerate SDKs from OpenAPI spec"
          git push
```

#### GitLab CI
```yaml
generate-sdks:
  stage: build
  script:
    - npm install -g mrapids
    - mrapids sdk api.yaml --lang typescript --output ./sdk-ts
    - mrapids sdk api.yaml --lang python --output ./sdk-python
    - mrapids sdk api.yaml --lang go --output ./sdk-go
  artifacts:
    paths:
      - sdk-ts/
      - sdk-python/
      - sdk-go/
  only:
    changes:
      - api.yaml
```

### 7. Custom Templates

Create custom templates for your organization's standards:

```bash
# Copy default templates
mrapids sdk api.yaml --lang typescript --output ./sdk --export-templates ./my-templates

# Customize templates
vim my-templates/client.ts.hbs

# Use custom templates
mrapids sdk api.yaml --lang typescript --output ./sdk --templates ./my-templates
```

### 8. Multi-API Project

```bash
# Generate SDKs for multiple APIs
for api in apis/*.yaml; do
  name=$(basename "$api" .yaml)
  mrapids sdk "$api" --lang typescript --output "./sdks/$name-ts"
  mrapids sdk "$api" --lang python --output "./sdks/$name-python"
done
```

### 9. Package Publishing

#### NPM (TypeScript)
```json
// Generated package.json
{
  "name": "@yourcompany/petstore-sdk",
  "version": "1.0.0",
  "main": "dist/index.js",
  "types": "dist/index.d.ts",
  "scripts": {
    "build": "tsc",
    "prepublishOnly": "npm run build"
  }
}
```

```bash
cd sdk-ts
npm run build
npm publish
```

#### PyPI (Python)
```bash
cd sdk-python
python setup.py sdist bdist_wheel
twine upload dist/*
```

#### Go Module
```bash
cd sdk-go
git init
git add .
git commit -m "Initial SDK"
git remote add origin https://github.com/yourcompany/petstore-sdk-go
git push -u origin main
git tag v1.0.0
git push --tags
```

### 10. Testing Generated SDKs

#### TypeScript
```typescript
// sdk-ts/__tests__/client.test.ts
import { ApiClient } from '../client';

describe('PetStore API Client', () => {
    const client = new ApiClient({
        baseUrl: 'http://localhost:3000/mock'
    });
    
    test('should create a pet', async () => {
        const pet = await client.addPet({
            name: 'Test Pet',
            status: 'available'
        });
        expect(pet.name).toBe('Test Pet');
    });
});
```

#### Python
```python
# sdk-python/tests/test_client.py
import pytest
from sdk import ApiClient, ApiConfig

@pytest.fixture
def client():
    return ApiClient(ApiConfig(base_url="http://localhost:3000/mock"))

def test_add_pet(client):
    pet = client.add_pet(body={
        "name": "Test Pet",
        "status": "available"
    })
    assert pet["name"] == "Test Pet"
```

## Benefits Summary

1. **Type Safety**: Full TypeScript/Python types prevent runtime errors
2. **Zero Dependencies**: Minimal footprint, maximum compatibility
3. **Idiomatic Code**: Follows language best practices
4. **Easy Integration**: Drop-in replacement for hand-coded clients
5. **Maintainable**: Regenerate when API changes
6. **Production Ready**: Error handling, retries, timeouts built-in
7. **Documentation**: Comprehensive README and inline docs
8. **Customizable**: Template-based for organization standards

## Common Patterns

### Error Handling
```typescript
try {
    const result = await api.someOperation();
} catch (error) {
    if (error instanceof ApiError) {
        switch (error.statusCode) {
            case 404:
                console.log('Not found');
                break;
            case 401:
                // Refresh token
                break;
            default:
                console.error('API Error:', error.message);
        }
    }
}
```

### Pagination
```python
# If API supports pagination
all_items = []
page = 1
while True:
    response = client.list_items(page=page, limit=100)
    all_items.extend(response['items'])
    if len(response['items']) < 100:
        break
    page += 1
```

### File Uploads
```go
// Multipart file upload
file, err := os.Open("image.jpg")
if err != nil {
    log.Fatal(err)
}
defer file.Close()

response, err := client.UploadFile(ctx, petID, "profile-photo", file)
```

## Next Steps

1. Install MicroRapid: `npm install -g mrapids`
2. Generate your first SDK: `mrapids sdk your-api.yaml --lang typescript --output ./sdk`
3. Customize templates if needed
4. Integrate into your CI/CD pipeline
5. Enjoy maintenance-free SDKs!

**MicroRapid: Your OpenAPI, but as native code.**