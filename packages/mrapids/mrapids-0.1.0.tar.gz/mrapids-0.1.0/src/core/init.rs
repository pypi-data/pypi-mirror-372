use crate::cli::InitCommand;
use crate::core::validation::{SpecValidator, ValidationLevel};
use anyhow::{Context, Result};
use colored::*;
use serde_json;
use serde_yaml;
use std::fs;
use std::path::{Path, PathBuf};

pub fn init_project(cmd: InitCommand) -> Result<()> {
    // First, validate the project path for security
    let project_path = validate_project_path(&cmd.name)?;
    // If --from-url or --from-file is provided, download/load the schema first
    let (schema_content, is_json_format) = if let Some(url) = &cmd.from_url {
        // Validate that it's actually a URL
        // Basic URL validation for security
        if !url.starts_with("http://") && !url.starts_with("https://") {
            return Err(anyhow::anyhow!(
                "Invalid URL: {}. Use --from-file for local files or provide a valid HTTP/HTTPS URL", 
                url
            ));
        }

        // Enforce HTTPS for downloads
        use crate::utils::security::enforce_https;
        enforce_https(url, cmd.allow_insecure)?;
        println!(
            "{} Fetching schema from: {}",
            "🌐".bright_blue(),
            url.bright_cyan()
        );
        if let Some((content, is_json)) = download_schema(url)? {
            (Some(content), is_json)
        } else {
            (None, false)
        }
    } else if let Some(file_path) = &cmd.from_file {
        println!(
            "{} Loading schema from: {}",
            "📁".bright_blue(),
            file_path.bright_cyan()
        );
        // Basic file path validation for security
        let file_path_lower = file_path.to_lowercase();
        if file_path.contains("..")
            || file_path.starts_with("/etc")
            || file_path.starts_with("/usr")
            || file_path.starts_with("/var")
            || file_path.starts_with("~")
            || file_path_lower.contains("passwd")
            || file_path_lower.contains("shadow")
            || file_path_lower.contains("ssh")
        {
            return Err(anyhow::anyhow!("Access denied: suspicious file path"));
        }

        if let Some((content, is_json)) = load_local_schema(file_path)? {
            (Some(content), is_json)
        } else {
            (None, false)
        }
    } else {
        (None, false)
    };

    println!(
        "{} Initializing MicroRapid project: {}",
        "🚀".bright_blue(),
        cmd.name.bright_yellow()
    );

    // Check if directory exists and is not empty
    if project_path.exists() && project_path.read_dir()?.count() > 0 && !cmd.force {
        println!(
            "{} Directory '{}' is not empty. Use --force to overwrite.",
            "❌".red(),
            project_path.display()
        );
        return Ok(());
    }

    // Create project directory if needed
    if !project_path.exists() {
        fs::create_dir_all(&project_path)?;
    }

    // Detect template type from schema if downloaded
    let template = if let Some(ref content) = schema_content {
        if content.contains("\"openapi\"")
            || content.contains("openapi:")
            || content.contains("\"swagger\"")
            || content.contains("swagger:")
        {
            "rest"
        } else if content.contains("type Query") || content.contains("type Mutation") {
            "graphql"
        } else {
            &cmd.template
        }
    } else {
        &cmd.template
    };

    // Create project structure based on template
    create_project_structure(&project_path, template)?;

    // If we downloaded a schema, validate and save it
    if let Some(ref content) = schema_content {
        // Validate OpenAPI/Swagger specs before saving
        if template != "graphql" && (content.contains("openapi") || content.contains("swagger")) {
            println!("{} Validating OpenAPI specification...", "🔍".bright_cyan());

            let validator = SpecValidator::new()?;
            let validation_report =
                validator.validate_content(content, ValidationLevel::Standard)?;

            if !validation_report.is_valid() {
                println!("\n{} Specification has validation errors:", "⚠️".yellow());
                validation_report.display();

                if !cmd.force {
                    println!(
                        "\n{} Use --force to initialize with an invalid specification",
                        "💡".blue()
                    );
                    return Err(anyhow::anyhow!("Specification validation failed"));
                } else {
                    println!(
                        "\n{} Proceeding with invalid specification (--force used)",
                        "⚠️".yellow()
                    );
                }
            } else if validation_report.has_warnings() {
                println!("{} Specification has warnings:", "⚠️".yellow());
                validation_report.display();
            } else {
                println!("{} Specification is valid!", "✅".green());
            }
        }

        let spec_file = if template == "graphql" {
            project_path.join("specs/schema.graphql")
        } else {
            project_path.join("specs/api.yaml")
        };

        // Add a comment at the top with spec version info
        let spec_version = detect_spec_version(content);

        // Convert JSON to YAML if needed
        let yaml_content = if is_json_format || content.trim().starts_with("{") {
            // JSON format - convert to YAML
            println!("  {} Converting JSON to YAML format...", "🔄".bright_cyan());
            match convert_json_to_yaml(content) {
                Ok(yaml) => yaml,
                Err(e) => {
                    return Err(anyhow::anyhow!("Failed to convert JSON to YAML: {}", e));
                }
            }
        } else {
            // Already YAML
            content.clone()
        };

        // Add header comment
        let content_with_header = format!(
            "# {}\n# Downloaded from: {}\n# Converted to YAML by MicroRapid\n\n{}",
            spec_version,
            cmd.from_url.as_ref().unwrap_or(&"Unknown".to_string()),
            yaml_content
        );

        fs::write(&spec_file, content_with_header)?;
        println!(
            "  {} Downloaded schema to: {}",
            "📥".green(),
            spec_file.display().to_string().cyan()
        );

        // Extract API title and base URL if possible
        if let Some(url) = &cmd.from_url {
            update_project_config(&project_path, url, &spec_version)?;
        }
    }

    println!("{} Project initialized successfully!", "✅".green());
    println!("\n{} Project structure:", "📁".bright_blue());
    print_tree(&project_path, template);

    // Print next steps
    println!("\n{} Next steps:", "🎯".bright_green());
    if cmd.from_url.is_some() || cmd.from_file.is_some() {
        println!("  1. Review the downloaded schema in specs/");
        println!("  2. Configure environments in config/.env.example");
        println!("  3. Generate test scripts: mrapids setup-tests --format npm");
        println!("  4. Run operations: mrapids run");
    } else {
        match template {
            "minimal" => {
                println!("  1. Edit specs/api.yaml with your API specification");
                println!("  2. Configure environments in config/.env.example");
                println!("  3. Run: mrapids run");
            }
            "graphql" => {
                println!("  1. Define your schema in specs/schema.graphql");
                println!("  2. Add operations to specs/operations.graphql");
                println!("  3. Configure environments in config/.env.example");
                println!("  4. Run: mrapids run --query <operation>");
            }
            _ => {
                // "rest" is default
                println!("  1. Edit specs/api.yaml with your OpenAPI specification");
                println!("  2. Configure environments in config/.env.example");
                println!("  3. Generate test scripts: mrapids setup-tests --format npm");
                println!("  4. Run operations: mrapids run");
            }
        }
    }

    Ok(())
}

fn load_local_schema(file_path: &str) -> Result<Option<(String, bool)>> {
    // Handle file:// URLs
    let path = if file_path.starts_with("file://") {
        file_path.trim_start_matches("file://")
    } else {
        file_path
    };

    // Check if file exists
    if !Path::new(path).exists() {
        return Err(anyhow::anyhow!("File not found: {}", path));
    }

    // Read local file
    let content =
        fs::read_to_string(path).map_err(|e| anyhow::anyhow!("Failed to read file: {}", e))?;

    // Detect format based on file extension
    let is_json = path.ends_with(".json");

    // Detect API specification version
    let spec_version = detect_spec_version(&content);
    println!(
        "  {} Detected: {}",
        "📄".bright_cyan(),
        spec_version.bright_green()
    );

    Ok(Some((content, is_json)))
}

fn download_schema(url: &str) -> Result<Option<(String, bool)>> {
    // Size limit for schemas (10MB)
    const MAX_SCHEMA_SIZE: u64 = 10 * 1024 * 1024;

    // Use blocking client in a separate thread to avoid runtime conflicts
    let url_clone = url.to_string();
    let (content, is_json) = std::thread::spawn(move || {
        use reqwest::blocking::Client;

        let client = Client::builder()
            .timeout(std::time::Duration::from_secs(30))
            .build()?;

        let response = client
            .get(&url_clone)
            .header("Accept", "application/json, application/yaml, text/plain")
            .send()
            .map_err(|e| anyhow::anyhow!("Failed to fetch schema: {}", e))?;

        // Check content length before downloading
        if let Some(content_length) = response.content_length() {
            if content_length > MAX_SCHEMA_SIZE {
                return Err(anyhow::anyhow!(
                    "Schema file too large: {} bytes (max: {} bytes)",
                    content_length,
                    MAX_SCHEMA_SIZE
                ));
            }
        }

        if !response.status().is_success() {
            return Err(anyhow::anyhow!(
                "Failed to download schema: HTTP {} {}",
                response.status().as_u16(),
                response
                    .status()
                    .canonical_reason()
                    .unwrap_or("Unknown error")
            ));
        }

        // Check Content-Type header to determine format
        let is_json = if let Some(content_type) = response.headers().get("content-type") {
            let content_type_str = content_type.to_str().unwrap_or("");
            println!(
                "  {} Content-Type: {}",
                "📄".bright_cyan(),
                content_type_str.dimmed()
            );
            content_type_str.contains("application/json") || content_type_str.contains("text/json")
        } else {
            false
        };

        let content = response
            .text()
            .map_err(|e| anyhow::anyhow!("Failed to read response: {}", e))?;

        Ok::<_, anyhow::Error>((content, is_json))
    })
    .join()
    .map_err(|_| anyhow::anyhow!("Download thread panicked"))??;

    // Double-check content size after reading
    if content.len() > MAX_SCHEMA_SIZE as usize {
        return Err(anyhow::anyhow!(
            "Schema content too large: {} bytes",
            content.len()
        ));
    }

    // Detect and display API specification version
    let spec_info = detect_spec_version(&content);
    println!(
        "  {} Detected: {}",
        "📋".bright_cyan(),
        spec_info.bright_yellow()
    );

    // Validate that it looks like a valid schema
    if !content.contains("openapi")
        && !content.contains("swagger")
        && !content.contains("type Query")
        && !content.contains("paths")
    {
        return Err(anyhow::anyhow!(
            "Downloaded content doesn't appear to be a valid OpenAPI/GraphQL schema"
        ));
    }

    Ok(Some((content, is_json)))
}

fn detect_spec_version(content: &str) -> String {
    // Check for OpenAPI 3.1
    if content.contains("\"openapi\":\"3.1")
        || content.contains("openapi: 3.1")
        || content.contains("\"openapi\": \"3.1")
        || content.contains("openapi: '3.1")
    {
        return "OpenAPI 3.1.x".to_string();
    }

    // Check for OpenAPI 3.0
    if content.contains("\"openapi\":\"3.0")
        || content.contains("openapi: 3.0")
        || content.contains("\"openapi\": \"3.0")
        || content.contains("openapi: '3.0")
    {
        // Try to extract exact version
        if let Some(version) = extract_version(content, "openapi") {
            return format!("OpenAPI {}", version);
        }
        return "OpenAPI 3.0.x".to_string();
    }

    // Check for Swagger 2.0
    if content.contains("\"swagger\":\"2.0")
        || content.contains("swagger: \"2.0")
        || content.contains("\"swagger\": \"2.0")
        || content.contains("swagger: '2.0")
    {
        return "Swagger 2.0 (OpenAPI 2.0)".to_string();
    }

    // Check for GraphQL
    if content.contains("type Query")
        || content.contains("type Mutation")
        || content.contains("schema {")
    {
        return "GraphQL Schema".to_string();
    }

    // Check for AsyncAPI
    if content.contains("\"asyncapi\"") || content.contains("asyncapi:") {
        if let Some(version) = extract_version(content, "asyncapi") {
            return format!("AsyncAPI {}", version);
        }
        return "AsyncAPI".to_string();
    }

    // Default fallback based on structure
    if content.contains("paths") {
        return "OpenAPI/Swagger (version unknown)".to_string();
    }

    "Unknown API Specification".to_string()
}

fn extract_version(content: &str, key: &str) -> Option<String> {
    // Try to extract version number after the key
    let patterns = vec![
        format!("\"{}\":\"", key),
        format!("\"{}\": \"", key),
        format!("{}: \"", key),
        format!("{}: '", key),
    ];

    for pattern in patterns {
        if let Some(pos) = content.find(&pattern) {
            let start = pos + pattern.len();
            let remaining = &content[start..];
            if let Some(end) = remaining.find(|c: char| c == '"' || c == '\'') {
                return Some(remaining[..end].to_string());
            }
        }
    }

    None
}

fn update_project_config(project_path: &Path, schema_url: &str, spec_version: &str) -> Result<()> {
    // Extract base URL from the schema URL if possible
    let base_url = if let Ok(url) = url::Url::parse(schema_url) {
        format!(
            "{}://{}",
            url.scheme(),
            url.host_str().unwrap_or("localhost")
        )
    } else {
        "http://localhost:3000".to_string()
    };

    // Update the mrapids.yaml with the actual URL and spec info
    let config_path = project_path.join("mrapids.yaml");
    if config_path.exists() {
        let content = fs::read_to_string(&config_path)?;
        let updated = content
            .replace("http://localhost:3000", &base_url)
            .replace("https://staging.api.com", &base_url)
            .replace("https://api.com", &base_url);

        // Add spec version info as a comment
        let updated_with_info = format!(
            "# Spec Version: {}\n# Source: {}\n{}",
            spec_version, schema_url, updated
        );

        fs::write(&config_path, updated_with_info)?;
    }

    // Update .env.example
    let env_path = project_path.join("config/.env.example");
    if env_path.exists() {
        let content = fs::read_to_string(&env_path)?;
        let updated = content
            .replace("http://localhost:3000", &base_url)
            .replace("http://localhost:4000/graphql", &base_url);
        fs::write(&env_path, updated)?;
    }

    Ok(())
}

fn create_project_structure(base: &Path, template: &str) -> Result<()> {
    match template {
        "minimal" => create_minimal_structure(base)?,
        "graphql" => create_graphql_structure(base)?,
        _ => create_rest_structure(base)?, // "rest" is default
    }

    Ok(())
}

fn create_minimal_structure(base: &Path) -> Result<()> {
    // Minimal: Just specs, config, and project file
    fs::create_dir_all(base.join("specs"))?;
    fs::create_dir_all(base.join("config"))?;

    // Create mrapids.yaml
    let config = r#"# MicroRapid Project Configuration
name: my-api
version: 1.0.0
type: rest

# Where things are
paths:
  specs: ./specs
  config: ./config

# Default spec to use
default_spec: ./specs/api.yaml

# Environments
environments:
  local:
    url: http://localhost:3000
    config: ./config/.env.local
"#;
    fs::write(base.join("mrapids.yaml"), config)?;

    // Create basic spec
    let spec = r#"openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
  description: API specification
servers:
  - url: http://localhost:3000
paths:
  /health:
    get:
      operationId: healthCheck
      summary: Health check endpoint
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: healthy
"#;
    fs::write(base.join("specs/api.yaml"), spec)?;

    // Create .env.example
    let env = r#"# API Configuration
API_BASE_URL=http://localhost:3000
API_KEY=your-api-key-here

# Environment
NODE_ENV=development
"#;
    fs::write(base.join("config/.env.example"), env)?;

    Ok(())
}

fn create_rest_structure(base: &Path) -> Result<()> {
    // Full REST structure: 5 folders
    fs::create_dir_all(base.join("specs"))?;
    fs::create_dir_all(base.join("tests"))?;
    fs::create_dir_all(base.join("scripts"))?;
    fs::create_dir_all(base.join("config"))?;
    fs::create_dir_all(base.join("docs"))?;

    // Create mrapids.yaml
    let config = r#"# MicroRapid Project Configuration
name: my-rest-api
version: 1.0.0
type: rest

# Where things are
paths:
  specs: ./specs
  tests: ./tests
  scripts: ./scripts
  config: ./config

# Default spec to use
default_spec: ./specs/api.yaml

# Environments
environments:
  local:
    url: http://localhost:3000
    config: ./config/.env.local
  staging:
    url: https://staging.api.com
    config: ./config/.env.staging
  production:
    url: https://api.com
    config: ./config/.env.production

# Generation preferences
generate:
  output: ./scripts
  languages: [typescript, python]
  
# Testing preferences  
test:
  framework: jest
  pattern: "**/*.test.js"
"#;
    fs::write(base.join("mrapids.yaml"), config)?;

    // Create OpenAPI spec
    let spec = r#"openapi: 3.0.3
info:
  title: Sample API
  version: 1.0.0
  description: A sample REST API specification
servers:
  - url: https://jsonplaceholder.typicode.com
    description: JSONPlaceholder API
paths:
  /users:
    get:
      operationId: listUsers
      summary: Get all users
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      operationId: createUser
      summary: Create a new user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserInput'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
  /users/{id}:
    get:
      operationId: getUser
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
    put:
      operationId: updateUser
      summary: Update user
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserInput'
      responses:
        '200':
          description: User updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
    delete:
      operationId: deleteUser
      summary: Delete user
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '204':
          description: User deleted
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
        username:
          type: string
    UserInput:
      type: object
      required:
        - name
        - email
      properties:
        name:
          type: string
        email:
          type: string
        username:
          type: string
"#;
    fs::write(base.join("specs/api.yaml"), spec)?;

    // Create test file
    let test = r#"// Sample test file for API testing
const mrapids = require('mrapids');

describe('User API Tests', () => {
  test('List all users', async () => {
    const response = await mrapids.run('specs/api.yaml', {
      operation: 'listUsers'
    });
    expect(response.status).toBe(200);
    expect(Array.isArray(response.data)).toBe(true);
  });

  test('Get specific user', async () => {
    const response = await mrapids.run('specs/api.yaml', {
      operation: 'getUser',
      params: { id: 1 }
    });
    expect(response.status).toBe(200);
    expect(response.data).toHaveProperty('id');
  });
});
"#;
    fs::write(base.join("tests/smoke.test.js"), test)?;

    // Create .gitkeep in scripts
    fs::write(base.join("scripts/.gitkeep"), "")?;

    // Create README in docs
    let readme = r#"# API Documentation

## Overview
This REST API provides endpoints for managing users and related resources.

## Quick Start

### Install MicroRapid
```bash
npm install -g mrapids
```

### Run Operations
```bash
# List all users
mrapids run --operation listUsers

# Get specific user
mrapids run --operation getUser --param id=1

# Generate SDK
mrapids generate --language typescript

# Set up test scripts
mrapids setup-tests --format npm
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /users | List all users |
| POST | /users | Create new user |
| GET | /users/{id} | Get user by ID |
| PUT | /users/{id} | Update user |
| DELETE | /users/{id} | Delete user |

## Testing

Run all tests:
```bash
npm test
```

## Environment Configuration

Copy `.env.example` to `.env.local` and configure:
```bash
cp config/.env.example config/.env.local
```
"#;
    fs::write(base.join("docs/README.md"), readme)?;

    // Create env files
    let env_example = r#"# API Configuration
API_BASE_URL=http://localhost:3000
API_KEY=your-api-key-here

# Authentication
AUTH_TOKEN=
API_SECRET=

# Test Data
TEST_USER_ID=1
TEST_USER_EMAIL=test@example.com

# Environment
NODE_ENV=development
DEBUG=false
LOG_LEVEL=info
"#;
    fs::write(base.join("config/.env.example"), env_example)?;

    // Create .gitignore
    let gitignore = r#"# Environment files
config/.env.local
config/.env.staging
config/.env.production
.env

# Generated files
scripts/*
!scripts/.gitkeep

# Dependencies
node_modules/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"#;
    fs::write(base.join(".gitignore"), gitignore)?;

    Ok(())
}

fn create_graphql_structure(base: &Path) -> Result<()> {
    // GraphQL structure: 5 folders
    fs::create_dir_all(base.join("specs"))?;
    fs::create_dir_all(base.join("tests"))?;
    fs::create_dir_all(base.join("scripts"))?;
    fs::create_dir_all(base.join("config"))?;
    fs::create_dir_all(base.join("docs"))?;

    // Create mrapids.yaml
    let config = r#"# MicroRapid Project Configuration
name: my-graphql-api
version: 1.0.0
type: graphql

# Where things are
paths:
  specs: ./specs
  tests: ./tests
  scripts: ./scripts
  config: ./config

# Default schema
default_spec: ./specs/schema.graphql

# GraphQL endpoint
graphql:
  endpoint: http://localhost:4000/graphql
  playground: true

# Environments
environments:
  local:
    url: http://localhost:4000/graphql
    config: ./config/.env.local
  staging:
    url: https://staging.api.com/graphql
    config: ./config/.env.staging
  production:
    url: https://api.com/graphql
    config: ./config/.env.production

# Generation preferences
generate:
  output: ./scripts
  languages: [typescript, graphql-codegen]
  
# Testing preferences  
test:
  framework: jest
  pattern: "**/*.test.js"
"#;
    fs::write(base.join("mrapids.yaml"), config)?;

    // Create GraphQL schema
    let schema = r#"# GraphQL Schema
type Query {
  # Get a specific user by ID
  user(id: ID!): User
  
  # List all users with optional pagination
  users(limit: Int = 10, offset: Int = 0): UserConnection!
  
  # Get a specific post
  post(id: ID!): Post
  
  # List posts with filters
  posts(userId: ID, limit: Int = 10): [Post!]!
}

type Mutation {
  # Create a new user
  createUser(input: CreateUserInput!): User!
  
  # Update existing user
  updateUser(id: ID!, input: UpdateUserInput!): User
  
  # Delete a user
  deleteUser(id: ID!): DeleteResponse!
  
  # Create a new post
  createPost(input: CreatePostInput!): Post!
}

type Subscription {
  # Subscribe to user updates
  userUpdated(id: ID!): User!
  
  # Subscribe to new posts
  postCreated: Post!
}

# User type
type User {
  id: ID!
  name: String!
  email: String!
  username: String!
  posts: [Post!]!
  createdAt: String!
  updatedAt: String!
}

# Post type
type Post {
  id: ID!
  title: String!
  body: String!
  author: User!
  comments: [Comment!]!
  published: Boolean!
  createdAt: String!
}

# Comment type
type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
}

# Connection type for pagination
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

# Input types
input CreateUserInput {
  name: String!
  email: String!
  username: String!
}

input UpdateUserInput {
  name: String
  email: String
  username: String
}

input CreatePostInput {
  title: String!
  body: String!
  authorId: ID!
  published: Boolean = false
}

# Response types
type DeleteResponse {
  success: Boolean!
  message: String
}
"#;
    fs::write(base.join("specs/schema.graphql"), schema)?;

    // Create sample operations
    let operations = r#"# Sample GraphQL Operations

# Queries
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    posts {
      id
      title
    }
  }
}

query ListUsers($limit: Int) {
  users(limit: $limit) {
    edges {
      node {
        id
        name
        email
      }
    }
    totalCount
  }
}

query GetUserPosts($userId: ID!) {
  posts(userId: $userId) {
    id
    title
    body
    published
  }
}

# Mutations
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
    username
  }
}

mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
  updateUser(id: $id, input: $input) {
    id
    name
    email
  }
}

mutation DeleteUser($id: ID!) {
  deleteUser(id: $id) {
    success
    message
  }
}

mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    body
    author {
      name
    }
  }
}

# Subscriptions
subscription OnUserUpdate($id: ID!) {
  userUpdated(id: $id) {
    id
    name
    email
    updatedAt
  }
}

subscription OnNewPost {
  postCreated {
    id
    title
    author {
      name
    }
  }
}
"#;
    fs::write(base.join("specs/operations.graphql"), operations)?;

    // Create test file
    let test = r#"// GraphQL API Tests
const mrapids = require('mrapids');

describe('GraphQL User API', () => {
  test('Query single user', async () => {
    const response = await mrapids.graphql({
      schema: 'specs/schema.graphql',
      query: `
        query GetUser($id: ID!) {
          user(id: $id) {
            id
            name
            email
          }
        }
      `,
      variables: { id: '1' }
    });
    
    expect(response.data.user).toBeDefined();
    expect(response.data.user.id).toBe('1');
  });

  test('Create new user', async () => {
    const response = await mrapids.graphql({
      schema: 'specs/schema.graphql',
      query: `
        mutation CreateUser($input: CreateUserInput!) {
          createUser(input: $input) {
            id
            name
            email
          }
        }
      `,
      variables: {
        input: {
          name: 'Test User',
          email: 'test@example.com',
          username: 'testuser'
        }
      }
    });
    
    expect(response.data.createUser).toBeDefined();
    expect(response.data.createUser.email).toBe('test@example.com');
  });
});
"#;
    fs::write(base.join("tests/queries.test.js"), test)?;

    // Create .gitkeep in scripts
    fs::write(base.join("scripts/.gitkeep"), "")?;

    // Create README in docs
    let readme = r#"# GraphQL API Documentation

## Overview
This GraphQL API provides a flexible query interface for managing users, posts, and comments.

## Quick Start

### Install MicroRapid
```bash
npm install -g mrapids
```

### Run Operations
```bash
# Execute a query
mrapids run --query GetUser --variables '{"id": "1"}'

# Execute a mutation
mrapids run --mutation CreateUser --variables '{"input": {"name": "John", "email": "john@example.com"}}'

# Generate TypeScript SDK
mrapids generate --language typescript

# Generate GraphQL Codegen
mrapids generate --language graphql-codegen
```

## Schema Overview

### Queries
- `user(id: ID!)` - Get a specific user
- `users(limit: Int, offset: Int)` - List users with pagination
- `post(id: ID!)` - Get a specific post
- `posts(userId: ID, limit: Int)` - List posts with filters

### Mutations
- `createUser(input: CreateUserInput!)` - Create new user
- `updateUser(id: ID!, input: UpdateUserInput!)` - Update user
- `deleteUser(id: ID!)` - Delete user
- `createPost(input: CreatePostInput!)` - Create new post

### Subscriptions
- `userUpdated(id: ID!)` - Subscribe to user updates
- `postCreated` - Subscribe to new posts

## Testing

Run all tests:
```bash
npm test
```

## GraphQL Playground

Access the GraphQL playground at:
```
http://localhost:4000/graphql
```

## Environment Configuration

Copy `.env.example` to `.env.local`:
```bash
cp config/.env.example config/.env.local
```
"#;
    fs::write(base.join("docs/README.md"), readme)?;

    // Create env files
    let env_example = r#"# GraphQL Configuration
GRAPHQL_ENDPOINT=http://localhost:4000/graphql
GRAPHQL_WS_ENDPOINT=ws://localhost:4000/graphql

# Authentication
AUTH_TOKEN=
API_KEY=

# Test Data
TEST_USER_ID=1
TEST_POST_ID=1

# Environment
NODE_ENV=development
DEBUG=false
ENABLE_PLAYGROUND=true
"#;
    fs::write(base.join("config/.env.example"), env_example)?;

    // Create .gitignore
    let gitignore = r#"# Environment files
config/.env.local
config/.env.staging
config/.env.production
.env

# Generated files
scripts/*
!scripts/.gitkeep

# Dependencies
node_modules/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"#;
    fs::write(base.join(".gitignore"), gitignore)?;

    Ok(())
}

fn print_tree(base: &Path, template: &str) {
    let project_name = if base == Path::new(".") {
        "."
    } else {
        base.file_name()
            .and_then(|s| s.to_str())
            .unwrap_or("project")
    };

    println!("   {}/", project_name.bright_yellow());

    match template {
        "minimal" => {
            println!("   ├── {}", "mrapids.yaml".bright_cyan());
            println!("   ├── {}/", "specs".bright_blue());
            println!("   │   └── {}", "api.yaml");
            println!("   └── {}/", "config".bright_blue());
            println!("       └── {}", ".env.example");
        }
        "graphql" => {
            println!("   ├── {}", "mrapids.yaml".bright_cyan());
            println!("   ├── {}", ".gitignore".dimmed());
            println!("   ├── {}/", "specs".bright_blue());
            println!("   │   ├── {}", "schema.graphql");
            println!("   │   └── {}", "operations.graphql");
            println!("   ├── {}/", "tests".bright_blue());
            println!("   │   └── {}", "queries.test.js");
            println!("   ├── {}/", "scripts".bright_blue());
            println!("   │   └── {}", ".gitkeep".dimmed());
            println!("   ├── {}/", "config".bright_blue());
            println!("   │   └── {}", ".env.example");
            println!("   └── {}/", "docs".bright_blue());
            println!("       └── {}", "README.md");
        }
        _ => {
            // rest
            println!("   ├── {}", "mrapids.yaml".bright_cyan());
            println!("   ├── {}", ".gitignore".dimmed());
            println!("   ├── {}/", "specs".bright_blue());
            println!("   │   └── {}", "api.yaml");
            println!("   ├── {}/", "tests".bright_blue());
            println!("   │   └── {}", "smoke.test.js");
            println!("   ├── {}/", "scripts".bright_blue());
            println!("   │   └── {}", ".gitkeep".dimmed());
            println!("   ├── {}/", "config".bright_blue());
            println!("   │   └── {}", ".env.example");
            println!("   └── {}/", "docs".bright_blue());
            println!("       └── {}", "README.md");
        }
    }
}

/// Convert JSON content to YAML format
fn convert_json_to_yaml(json_content: &str) -> Result<String> {
    // Parse JSON into a generic Value
    let json_value: serde_json::Value =
        serde_json::from_str(json_content).context("Failed to parse JSON content")?;

    // Convert to YAML
    let yaml_string =
        serde_yaml::to_string(&json_value).context("Failed to convert to YAML format")?;

    Ok(yaml_string)
}

/// Validate project path for security
fn validate_project_path(name: &str) -> Result<PathBuf> {
    let project_path = if name == "." {
        std::env::current_dir()?
    } else {
        std::env::current_dir()?.join(name)
    };

    // Canonicalize to resolve any .. or symlinks
    let canonical = if project_path.exists() {
        project_path.canonicalize()?
    } else {
        // For non-existent paths, canonicalize the parent
        if let Some(parent) = project_path.parent() {
            parent
                .canonicalize()?
                .join(project_path.file_name().unwrap())
        } else {
            project_path.clone()
        }
    };

    // Check against forbidden system directories
    let forbidden_prefixes = [
        "/etc", "/usr", "/bin", "/sbin", "/var", "/opt", "/sys", "/proc", "/boot", "/dev", "/lib",
        "/lib64", "/root",
    ];

    let path_str = canonical.to_string_lossy();
    for forbidden in &forbidden_prefixes {
        if path_str.starts_with(forbidden) {
            return Err(anyhow::anyhow!(
                "Cannot create project in system directory: {}",
                forbidden
            ));
        }
    }

    // Windows system directories
    #[cfg(windows)]
    {
        let forbidden_windows = [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\ProgramData",
            "C:\\System32",
        ];
        for forbidden in &forbidden_windows {
            if path_str.starts_with(forbidden) {
                return Err(anyhow::anyhow!(
                    "Cannot create project in system directory: {}",
                    forbidden
                ));
            }
        }
    }

    Ok(canonical)
}
