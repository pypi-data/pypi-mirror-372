# MicroRapid SDK Generation Implementation

## Overview

MicroRapid SDK generation is built on the philosophy of being a **"reliable contract engine"** that solves real-world OpenAPI problems others can't handle. Instead of competing with OpenAPI Generator on language count, we focus on **spec truth**, **minimal SDKs**, and **idiomatic code**.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────┐
│                 CLI Layer                       │
│  mrapids sdk --lang typescript --output ./sdk   │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│              Parser & Resolver                  │
│  • Two-pass parsing                             │
│  • $ref resolution                              │
│  • Circular reference detection                 │
│  • External reference support                   │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│            SDK Context Builder                  │
│  • UnifiedSpec → SdkContext                     │
│  • Type normalization                           │
│  • Operation extraction                         │
│  • Model generation                             │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│            Template Engine                      │
│  • Handlebars templates                         │
│  • Case conversion helpers                      │
│  • Language-specific generation                 │
└─────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────┐
│           Generated SDK Files                   │
│  • client.ts                                    │
│  • models.ts                                    │
│  • types.ts                                     │
│  • package.json                                 │
│  • README.md                                    │
└─────────────────────────────────────────────────┘
```

## Implementation Details

### 1. CLI Commands

#### `mrapids sdk` Command

```rust
#[derive(Parser)]
pub struct SdkCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,
    
    /// Target programming language
    #[arg(short, long, value_enum)]
    pub lang: SdkLanguage,
    
    /// Output directory for generated SDK
    #[arg(short, long)]
    pub output: PathBuf,
    
    /// Package name (language-specific)
    #[arg(short, long)]
    pub package: Option<String>,
    
    /// HTTP client library to use
    #[arg(long)]
    pub http_client: Option<String>,
    
    /// Include authentication helpers
    #[arg(long, default_value = "true")]
    pub auth: bool,
    
    /// Include pagination helpers  
    #[arg(long, default_value = "true")]
    pub pagination: bool,
    
    /// Include retry/timeout configuration
    #[arg(long, default_value = "true")]  
    pub resilience: bool,
}
```

#### `mrapids diff` Command

```rust
#[derive(Parser)]
pub struct DiffCommand {
    /// Path to the old OpenAPI/Swagger specification file
    pub old_spec: PathBuf,
    
    /// Path to the new OpenAPI/Swagger specification file  
    pub new_spec: PathBuf,
    
    /// Only show breaking changes
    #[arg(long)]
    pub breaking_only: bool,
    
    /// Output format (text, json, markdown)
    #[arg(short, long, value_enum, default_value = "text")]
    pub format: DiffFormat,
    
    /// Exit with non-zero code if breaking changes found
    #[arg(long)]
    pub fail_on_breaking: bool,
}
```

### 2. SDK Context Model

The SDK context is a normalized view of the OpenAPI spec optimized for template generation:

```rust
#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkContext {
    pub info: SdkInfo,
    pub base_url: String,
    pub auth: SdkAuth,
    pub models: Vec<SdkModel>,
    pub operations: Vec<SdkOperation>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkOperation {
    pub operation_id: String,
    pub method: String,
    pub path: String,
    pub summary: Option<String>,
    pub description: Option<String>,
    pub parameters: Vec<SdkParameter>,
    pub request_body: Option<SdkRequestBody>,
    pub responses: Vec<SdkResponse>,
}

#[derive(Debug, Clone, serde::Serialize)]
pub struct SdkModel {
    pub name: String,
    pub properties: Vec<SdkProperty>,
    pub required: Vec<String>,
    pub description: Option<String>,
}
```

### 3. Template Engine

The template engine uses Handlebars with custom helpers for case conversion:

```rust
pub struct TemplateEngine {
    handlebars: Handlebars<'static>,
    templates_dir: PathBuf,
}

impl TemplateEngine {
    pub fn new(templates_dir: PathBuf) -> Result<Self> {
        let mut handlebars = Handlebars::new();
        
        // Register helpers
        handlebars.register_helper("camelCase", Box::new(camel_case_helper));
        handlebars.register_helper("pascalCase", Box::new(pascal_case_helper));
        handlebars.register_helper("snakeCase", Box::new(snake_case_helper));
        handlebars.register_helper("kebabCase", Box::new(kebab_case_helper));
        
        Ok(Self {
            handlebars,
            templates_dir,
        })
    }
}
```

### 4. TypeScript SDK Generation

The TypeScript generator creates a minimal, fetch-based SDK:

#### Generated Client Structure

```typescript
export class ApiClient {
    private config: ApiConfig;
    private baseUrl: string;

    constructor(config: ApiConfig) {
        this.config = config;
        this.baseUrl = config.baseUrl || 'https://api.example.com';
    }

    private async request<T>(
        method: string,
        path: string,
        options: RequestOptions = {}
    ): Promise<T> {
        // Fetch-based implementation with:
        // - Authentication headers
        // - Retry logic
        // - Error handling
        // - Type safety
    }

    // Generated methods for each operation
    async listUsers(params?: ListUsersParams): Promise<User[]> {
        return this.request('GET', '/users', { params });
    }

    async createUser(body: CreateUserRequest): Promise<User> {
        return this.request('POST', '/users', { body });
    }
}
```

#### Key Features

1. **Zero Dependencies**: Uses native fetch API
2. **Type Safety**: Full TypeScript types for all operations
3. **Authentication**: Bearer, API Key, OAuth support
4. **Resilience**: Built-in retry logic and timeout handling
5. **Error Handling**: Typed error classes for different HTTP statuses

## File Structure

### Generated SDK Files

```
generated-sdk/
├── client.ts       # Main API client class
├── models.ts       # TypeScript interfaces for all models
├── types.ts        # Common types (ApiConfig, errors, etc.)
├── package.json    # NPM package configuration
├── README.md       # Usage documentation
└── .templates/     # Template cache (development only)
```

### Template Structure

```
src/core/templates/typescript/
├── client.ts.hbs       # Client class template
├── models.ts.hbs       # Model interfaces template
├── types.ts.hbs        # Common types template
├── package.json.hbs    # Package configuration template
└── README.md.hbs       # Documentation template
```

## Usage Examples

### Basic SDK Generation

```bash
# Generate TypeScript SDK
mrapids sdk --lang typescript --output ./my-api-sdk api.yaml

# With custom package name
mrapids sdk --lang typescript --output ./sdk --package @myorg/api-client api.yaml

# Without authentication helpers
mrapids sdk --lang typescript --output ./sdk --auth false api.yaml
```

### Generated SDK Usage

```typescript
import { ApiClient } from './my-api-sdk';

const api = new ApiClient({
  baseUrl: 'https://api.example.com',
  auth: {
    bearer: 'your-jwt-token'
  },
  maxRetries: 3,
  retryDelay: 1000
});

// Type-safe API calls
const users = await api.listUsers({ limit: 10 });
const newUser = await api.createUser({
  name: 'John Doe',
  email: 'john@example.com'
});

// Error handling
try {
  const user = await api.getUser({ id: '123' });
} catch (error) {
  if (error instanceof NotFoundError) {
    console.log('User not found');
  }
}
```

## Template System

### Handlebars Helpers

- `{{camelCase operationId}}` - Converts to camelCase
- `{{pascalCase name}}` - Converts to PascalCase
- `{{snakeCase property}}` - Converts to snake_case
- `{{kebabCase package}}` - Converts to kebab-case

### Template Context

Templates receive a normalized context:

```json
{
  "info": {
    "title": "My API",
    "version": "1.0.0",
    "description": "API description"
  },
  "baseUrl": "https://api.example.com",
  "auth": {
    "schemes": [
      {
        "name": "bearerAuth",
        "scheme_type": "bearer",
        "format": "JWT"
      }
    ]
  },
  "models": [...],
  "operations": [...],
  "includeAuth": true,
  "includePagination": true,
  "includeResilience": true
}
```

## Strategic Advantages

### 1. **Spec Truth Before Code**
- Two-pass parser handles mixed $ref patterns
- Resolves circular references
- Supports external references
- Normalizes OpenAPI 3.0/3.1 differences

### 2. **Minimal, Idiomatic SDKs**
- No runtime frameworks
- Language-native patterns
- Pluggable HTTP clients
- Zero bloat philosophy

### 3. **Developer Experience**
- Type-safe by default
- Built-in error handling
- Retry/resilience out of the box
- Clear, readable generated code

## Future Enhancements

### Language Support
- [ ] Python SDK (httpx-based)
- [ ] Go SDK (net/http-based)
- [ ] Rust SDK (reqwest-based)
- [ ] Java SDK (Spring WebClient)

### Features
- [ ] Contract test generation
- [ ] Mock server integration
- [ ] GraphQL support
- [ ] WebSocket operations
- [ ] Streaming responses

### Tooling
- [ ] IDE plugins
- [ ] CI/CD integrations
- [ ] Version management
- [ ] SDK diffing tools

## Configuration

### Environment Variables
- `MRAPIDS_TEMPLATES_DIR` - Custom templates directory
- `MRAPIDS_SDK_CACHE` - Cache directory for templates

### Config File (.mrapids.yaml)
```yaml
sdk:
  typescript:
    http_client: fetch
    target: es2020
    module: commonjs
  python:
    http_client: httpx
    async: true
  go:
    module_path: github.com/myorg
```

## Troubleshooting

### Common Issues

1. **Operations not generated**
   - Ensure operationId is present on all operations
   - Check for $ref resolution errors

2. **Type errors in generated code**
   - Verify schema definitions are complete
   - Check for circular references

3. **Authentication not working**
   - Ensure security schemes are defined in spec
   - Verify auth configuration in client

## Contributing

### Adding a New Language

1. Create generator module in `src/core/sdk_gen/`
2. Implement `generate` function
3. Create templates in `src/core/templates/<language>/`
4. Add language to `SdkLanguage` enum
5. Update documentation

### Template Development

1. Templates use Handlebars syntax
2. Keep templates minimal and idiomatic
3. Use helpers for case conversion
4. Test with various OpenAPI specs

## Performance

- **Parsing**: < 100ms for typical specs
- **Generation**: < 500ms for complete SDK
- **Memory**: < 50MB for large specs
- **Templates**: Cached after first use