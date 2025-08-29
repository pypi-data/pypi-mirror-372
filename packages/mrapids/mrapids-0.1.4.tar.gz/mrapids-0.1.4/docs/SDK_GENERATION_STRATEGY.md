# MicroRapid SDK Generation Strategy

## Vision: Reliable Contract Engine + Thin SDKs

MicroRapid positions itself as the solution for complex, real-world OpenAPI specs where traditional generators fail. We focus on **spec truth before code** with deterministic resolution and minimal, idiomatic SDKs.

## Core Value Propositions

### 1. **Spec Truth Engine** 
- Two-pass parser handles mixed $ref patterns
- OpenAPI 3.1 JSON Schema support
- External reference resolution
- Circular reference detection
- Deterministic flattening and normalization

### 2. **Minimal, Idiomatic SDKs**
- Thin clients with pluggable HTTP
- Strong types from resolved schemas  
- First-class auth, pagination, error handling
- Zero bloat, no runtime frameworks
- Language-native patterns

### 3. **Contract-First Development**
- Auto-generated tests from resolved specs
- Breaking change detection
- Reference chain debugging
- Mock server integration

## Product Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MicroRapid Core                         │
├─────────────────────────────────────────────────────────────┤
│  Spec Parser & Resolver (Our Secret Sauce)                 │
│  • Two-pass parsing                                         │
│  • $ref resolution with caching                            │
│  • External reference support                              │
│  • Circular reference detection                            │
│  • OpenAPI 3.0/3.1 normalization                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Resolved Schema                            │
│  • Canonical, validated spec                               │
│  • Flattened references                                    │
│  • Normalized types and nullability                       │
│  • Language-specific "SDK views"                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                SDK Generation Layer                         │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│ TypeScript  │   Python    │     Go      │      Rust       │
│ (fetch)     │  (httpx)    │ (net/http)  │   (reqwest)     │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

## Command Structure

### Core Commands

#### 1. `mrapids resolve` / `mrapids flatten`
**Purpose**: Canonicalize and validate specs
```bash
mrapids resolve api.yaml --output resolved.yaml
mrapids flatten api.yaml --resolve-external --output flat.yaml
```

**Capabilities**:
- Handle mixed $ref patterns
- Resolve external references
- Normalize OpenAPI 3.0/3.1 differences
- Detect circular references
- Validate schema consistency

#### 2. `mrapids sdk --lang <language>`
**Purpose**: Generate minimal, idiomatic SDKs
```bash
mrapids sdk --lang typescript --output ./src/api/
mrapids sdk --lang python --output ./api_client/
mrapids sdk --lang go --package github.com/myorg/api --output ./api/
mrapids sdk --lang rust --output ./src/api/
```

**Features**:
- Pluggable HTTP clients
- Strong typing from resolved schemas
- Auth helpers (Bearer, API Key, OAuth)
- Pagination support
- Standardized error envelopes
- Retry/timeout configuration

#### 3. `mrapids test`
**Purpose**: Generate contract tests from resolved spec
```bash
mrapids test --output ./tests/ --mock-server
```

**Generates**:
- Contract test suites
- Mock data fixtures
- Snapshot tests
- Integration test helpers

#### 4. `mrapids diff old.yaml new.yaml`
**Purpose**: Contract-aware breaking change detection
```bash
mrapids diff v1.0.yaml v1.1.yaml --breaking-only
```

#### 5. `mrapids explain <operationId>`
**Purpose**: Debug $ref chains and schema resolution
```bash
mrapids explain getUserById
```

## SDK Generation Principles

### 1. **Thin and Idiomatic**
Each language follows its native patterns:

**TypeScript**:
```typescript
import { ApiClient } from './client';

const api = new ApiClient({
  baseURL: 'https://api.example.com',
  auth: { bearer: 'token' }
});

const users = await api.users.list({ limit: 10 });
```

**Python**:
```python
from api_client import ApiClient

api = ApiClient(
    base_url='https://api.example.com',
    auth=('bearer', 'token')
)

users = await api.users.list(limit=10)
```

### 2. **Pluggable HTTP Layer**
- TypeScript: fetch (default), axios (optional)
- Python: httpx (default), requests (optional)
- Go: net/http (default), resty (optional)
- Rust: reqwest (default), ureq (optional)

### 3. **Strong Types from Resolved Schema**
Generate types from the **resolved** schema, not the original messy spec:

```typescript
// Generated from resolved schema
interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
  role?: 'admin' | 'user' | 'guest';
}
```

### 4. **First-Class Features**

**Authentication**:
```typescript
// Multiple auth methods
const api = new ApiClient({
  auth: { 
    bearer: 'token',
    // or
    apiKey: { header: 'X-API-Key', value: 'key' },
    // or
    oauth: { clientId: 'id', clientSecret: 'secret' }
  }
});
```

**Error Handling**:
```typescript
try {
  const user = await api.users.get('123');
} catch (error) {
  if (error instanceof NotFoundError) {
    // 404 handling
  } else if (error instanceof ValidationError) {
    // 400 with validation details
  }
}
```

**Pagination**:
```typescript
// Auto-pagination support
for await (const user of api.users.listAll()) {
  console.log(user.name);
}
```

## Template System Architecture

### Template Structure
```
templates/
├── typescript/
│   ├── client.ts.hbs
│   ├── models.ts.hbs
│   ├── operations.ts.hbs
│   ├── auth.ts.hbs
│   └── errors.ts.hbs
├── python/
│   ├── client.py.jinja2
│   ├── models.py.jinja2
│   ├── operations.py.jinja2
│   └── auth.py.jinja2
├── go/
│   └── ...
└── rust/
    └── ...
```

### Template Context
Each template receives a normalized view of the resolved spec:

```json
{
  "info": {
    "title": "My API",
    "version": "1.0.0"
  },
  "baseUrl": "https://api.example.com",
  "auth": {
    "schemes": [
      { "type": "bearer", "format": "JWT" },
      { "type": "apiKey", "in": "header", "name": "X-API-Key" }
    ]
  },
  "models": [
    {
      "name": "User",
      "properties": [...],
      "required": [...]
    }
  ],
  "operations": [
    {
      "operationId": "getUser",
      "method": "GET",
      "path": "/users/{id}",
      "parameters": [...],
      "responses": [...]
    }
  ]
}
```

## Integration Strategy

### Reuse Existing Ecosystems
- **Templating**: Adapt OpenAPI Generator templates for our resolved specs
- **Linting**: Integrate with Spectral for additional validation rules
- **Mocking**: Use Prism/WireMock with our canonicalized specs
- **Documentation**: Generate clean specs for existing doc tools

### Differentiation Points
1. **Spec Resolution Quality**: Handle complex $ref patterns others can't
2. **SDK Minimalism**: Zero runtime dependencies, easy to customize
3. **Contract Testing**: Built-in test generation from resolved schemas
4. **Breaking Change Detection**: Semantic diff analysis
5. **Debugging**: Trace $ref resolution chains

## Target Languages (Priority Order)

### Phase 1: Core Languages
1. **TypeScript** - fetch-based, most popular
2. **Python** - httpx-based, data science/enterprise
3. **Go** - net/http-based, backend services  
4. **Rust** - reqwest-based, performance critical

### Phase 2: Enterprise Languages
- Java (Spring WebClient)
- C# (.NET HttpClient)

### Phase 3: Mobile/Others  
- Swift (URLSession)
- Kotlin (OkHttp)

## Success Metrics

### Technical
- Handle GitHub/Stripe/Kubernetes specs without errors
- Generate SDKs 10x smaller than OpenAPI Generator
- Sub-second generation times for complex specs
- Zero runtime dependencies in generated code

### Adoption
- Developer feedback: "Just works with complex specs"
- Reduced support tickets about generated code
- Integration into CI/CD pipelines
- Community contributions to templates

## Anti-Goals

❌ **Don't compete on language count**: Focus on quality over quantity
❌ **Don't build heavy runtimes**: Keep generated code minimal  
❌ **Don't reinvent docs/UI**: Integrate with existing tools
❌ **Don't replace simple cases**: Let OpenAPI Generator handle basic specs

## Decision Framework

**Use MicroRapid SDK generation when**:
- Spec has complex $ref patterns
- OpenAPI 3.1 features are used
- External references are needed
- Breaking change detection is critical
- Minimal SDK size is important

**Stick with OpenAPI Generator when**:
- Simple, flat spec structure
- Basic CRUD operations only
- Need language not yet supported
- Heavy customization of generated code