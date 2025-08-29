use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "mrapids")]
#[command(about = "Your OpenAPI, but executable", long_about = None)]
#[command(version)]
pub struct Args {
    #[command(subcommand)]
    pub command: Commands,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Initialize a new MicroRapid project
    Init(InitCommand),
    
    /// Analyze API spec and generate request examples
    Analyze(AnalyzeCommand),
    
    /// Execute an API operation from a specification
    Run(RunCommand),
    
    /// Test API operations
    Test(TestCommand),
    
    /// Generate code from API specifications
    Generate(GenerateCommand),
    
    /// Set up complete test environment from API specifications
    SetupTests(SetupTestsCommand),
    
    /// List operations, requests, or other resources
    List(ListCommand),
    
    /// Show detailed information about an operation
    Show(ShowCommand),
    
    /// Clean up test artifacts and temporary files
    Cleanup(CleanupCommand),
    
    /// Initialize configuration for an environment
    InitConfig(InitConfigCommand),
    
    /// Explore API operations by keyword search
    Explore(ExploreCommand),
    
    /// Manage OAuth authentication
    Auth(AuthCommand),
    
    /// Flatten an OpenAPI specification by resolving all $ref references
    Flatten(FlattenCommand),
    
    /// Validate an OpenAPI specification
    Validate(ValidateCommand),
    
    /// Generate SDK from OpenAPI specification
    Sdk(SdkCommand),
    
    /// Compare two OpenAPI specifications for breaking changes
    Diff(DiffCommand),
    
    /// Resolve all references in an OpenAPI specification
    Resolve(ResolveCommand),
}

#[derive(Parser)]
pub struct ValidateCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,
    
    /// Strict mode - treat warnings as errors
    #[arg(long)]
    pub strict: bool,
    
    /// Output format (text or json)
    #[arg(short, long, value_enum, default_value = "text")]
    pub format: ValidateFormat,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum ValidateFormat {
    /// Human-readable text format
    Text,
    /// JSON format for tooling
    Json,
}

#[derive(Parser)]
pub struct InitCommand {
    /// Project name (defaults to current directory name)
    #[arg(default_value = "my-api-project")]
    pub name: String,
    
    /// Project template (minimal, rest, graphql)
    #[arg(short, long, default_value = "rest")]
    pub template: String,
    
    /// Initialize from a URL (downloads OpenAPI/GraphQL schema)
    #[arg(long, value_name = "URL", conflicts_with = "from_file")]
    pub from_url: Option<String>,
    
    /// Initialize from a local file (OpenAPI/GraphQL schema)
    #[arg(long, value_name = "FILE", conflicts_with = "from_url")]
    pub from_file: Option<String>,
    
    /// Force overwrite if directory exists
    #[arg(short, long)]
    pub force: bool,
    
    /// Allow insecure HTTP connections when downloading specs (not recommended)
    #[arg(long)]
    pub allow_insecure: bool,
}

#[derive(Parser)]
#[command(args_override_self = true)]
pub struct RunCommand {
    /// Operation to execute (e.g., get-user, create-order, search-products)
    /// OR path to a request config file (e.g., requests/get-user.yaml)
    /// OR path to an API spec file for backward compatibility
    pub operation: String,
    
    /// Input data: JSON string, @file.json, or --file file.json
    #[arg(short, long, conflicts_with = "file")]
    pub data: Option<String>,
    
    /// Input data from file
    #[arg(short, long, conflicts_with = "data")]
    pub file: Option<PathBuf>,
    
    /// Common parameters (automatically mapped to path/query params)
    #[arg(long)]
    pub id: Option<String>,
    
    #[arg(long)]
    pub name: Option<String>,
    
    #[arg(long)]
    pub status: Option<String>,
    
    #[arg(long)]
    pub limit: Option<u32>,
    
    #[arg(long)]
    pub offset: Option<u32>,
    
    #[arg(long)]
    pub sort: Option<String>,
    
    /// Generic parameters: --param key=value (can be used multiple times)
    #[arg(long = "param", value_name = "KEY=VALUE")]
    pub params: Vec<String>,
    
    /// Query parameters: --query key=value (can be used multiple times)
    #[arg(long = "query", value_name = "KEY=VALUE")]
    pub query_params: Vec<String>,
    
    /// HTTP headers: --header "Key: Value" (can be used multiple times)
    #[arg(short = 'H', long = "header", value_name = "KEY: VALUE")]
    pub headers: Vec<String>,
    
    /// Authorization header shortcut
    #[arg(long, conflicts_with = "auth_profile")]
    pub auth: Option<String>,
    
    /// API key header shortcut (sets X-API-Key)
    #[arg(long, conflicts_with = "auth_profile")]
    pub api_key: Option<String>,
    
    /// Use OAuth profile for authentication
    #[arg(long, conflicts_with_all = &["auth", "api_key"])]
    pub auth_profile: Option<String>,
    
    /// Environment to use (dev, staging, prod)
    #[arg(short, long, default_value = "development")]
    pub env: String,
    
    /// Base URL to override default
    #[arg(short, long)]
    pub url: Option<String>,
    
    /// Output format (json, yaml, table, pretty)
    #[arg(short, long, default_value = "pretty")]
    pub output: String,
    
    /// Save response to file
    #[arg(long)]
    pub save: Option<PathBuf>,
    
    /// Use template file
    #[arg(long)]
    pub template: Option<String>,
    
    /// Set template variables: --set key=value (can be used multiple times)
    #[arg(long = "set", value_name = "KEY=VALUE")]
    pub template_vars: Vec<String>,
    
    /// Use only required fields (useful for quick testing)
    #[arg(long)]
    pub required_only: bool,
    
    /// Verbose output (show request details)
    #[arg(short, long)]
    pub verbose: bool,
    
    /// Dry run (show request without sending)
    #[arg(long)]
    pub dry_run: bool,
    
    /// Show equivalent curl command
    #[arg(long)]
    pub as_curl: bool,
    
    /// Edit default data before sending
    #[arg(long)]
    pub edit: bool,
    
    /// Read data from stdin
    #[arg(long)]
    pub stdin: bool,
    
    /// Retry failed requests
    #[arg(long, default_value = "0")]
    pub retry: u32,
    
    /// Timeout in seconds
    #[arg(long, default_value = "30")]
    pub timeout: u32,
    
    /// Allow insecure HTTP connections (not recommended)
    #[arg(long)]
    pub allow_insecure: bool,
    
    /// Suppress security warnings about request content
    #[arg(long)]
    pub no_warnings: bool,
}

#[derive(Parser)]
pub struct TestCommand {
    /// Path to the OpenAPI specification file
    pub spec: PathBuf,
    
    /// Test all operations
    #[arg(long)]
    pub all: bool,
    
    /// Specific operation to test
    #[arg(short, long)]
    pub operation: Option<String>,
    
    /// Automatically clean up test artifacts after completion
    #[arg(long, default_value = "true")]
    pub cleanup: bool,
    
    /// Keep test artifacts even after cleanup (for debugging)
    #[arg(long)]
    pub keep_artifacts: bool,
    
    /// Allow insecure HTTP connections (not recommended)
    #[arg(long)]
    pub allow_insecure: bool,
    
    /// Suppress security warnings about request content
    #[arg(long)]
    pub no_warnings: bool,
}

#[derive(Parser)]
pub struct AnalyzeCommand {
    /// Path to the OpenAPI/Swagger specification file (defaults to specs/api.yaml)
    #[arg(default_value = "specs/api.yaml")]
    pub spec: PathBuf,
    
    /// Analyze specific operation only
    #[arg(short, long)]
    pub operation: Option<String>,
    
    /// Output directory for generated examples (defaults to current directory)
    #[arg(short = 'd', long, default_value = ".")]
    pub output: PathBuf,
    
    /// Generate examples for all operations
    #[arg(long)]
    pub all: bool,
    
    /// Skip generating data files for request bodies
    #[arg(long)]
    pub skip_data: bool,
    
    /// Skip OpenAPI validation
    #[arg(long)]
    pub skip_validate: bool,
    
    /// Overwrite existing files
    #[arg(short, long)]
    pub force: bool,
    
    /// Clean up old backup directories after analysis
    #[arg(long, default_value = "true")]
    pub cleanup_backups: bool,
}

#[derive(Parser)]
pub struct ListCommand {
    /// What to list: operations, requests, or all
    #[arg(value_enum, default_value = "operations")]
    pub resource: ListResource,
    
    /// Filter results by text
    #[arg(short, long)]
    pub filter: Option<String>,
    
    /// Filter by HTTP method
    #[arg(short, long)]
    pub method: Option<String>,
    
    /// Filter by tag (for operations)
    #[arg(short, long)]
    pub tag: Option<String>,
    
    /// Output format
    #[arg(long, value_enum, default_value = "table")]
    pub format: ListFormat,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum ListResource {
    /// List operations from API spec
    Operations,
    /// List saved request configurations
    Requests,
    /// List all resources
    All,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum ListFormat {
    /// Table format with borders
    Table,
    /// Simple list format
    Simple,
    /// JSON output
    Json,
    /// YAML output
    Yaml,
}

#[derive(Parser)]
pub struct GenerateCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,
    
    /// Target language/framework for code generation
    #[arg(short, long, value_enum, default_value = "typescript")]
    pub target: GenerateTarget,
    
    /// Output directory for generated code
    #[arg(short, long, default_value = "./generated")]
    pub output: PathBuf,
    
    /// Generate client code
    #[arg(long, conflicts_with = "server")]
    pub client: bool,
    
    /// Generate server code
    #[arg(long, conflicts_with = "client")]
    pub server: bool,
    
    /// Generate both client and server (default)
    #[arg(long)]
    pub both: bool,
    
    /// Package/module name for generated code
    #[arg(short = 'n', long)]
    pub package_name: Option<String>,
    
    /// Skip validation of the spec
    #[arg(long)]
    pub skip_validation: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum GenerateTarget {
    /// TypeScript/JavaScript with Fetch API
    Typescript,
    /// Python with Requests
    Python,
    /// Go with net/http
    Go,
    /// Rust with reqwest
    Rust,
    /// Java with OkHttp
    Java,
    /// C# with HttpClient
    Csharp,
    /// Ruby with Net::HTTP
    Ruby,
    /// PHP with Guzzle
    Php,
    /// Swift with URLSession
    Swift,
    /// Kotlin with Ktor
    Kotlin,
    /// cURL commands
    Curl,
    /// Postman collection
    Postman,
}

#[derive(Parser)]
pub struct SetupTestsCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,
    
    /// Output format for test setup
    #[arg(short, long, value_enum, default_value = "npm")]
    pub format: TestSetupFormat,
    
    /// Output directory or file
    #[arg(short, long, default_value = ".")]
    pub output: PathBuf,
    
    /// Overwrite existing files
    #[arg(long)]
    pub force: bool,
    
    /// Show what would be generated without creating files
    #[arg(long)]
    pub dry_run: bool,
    
    /// Include example usage in generated files
    #[arg(long)]
    pub with_examples: bool,
    
    /// Generate .env.example file
    #[arg(long)]
    pub with_env: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum TestSetupFormat {
    /// NPM package.json with scripts (cross-platform)
    Npm,
    /// Makefile for Unix/Mac
    Make,
    /// Shell script for automation
    Shell,
    /// Docker Compose for containers
    Compose,
    /// Direct cURL commands (no mrapids needed)
    Curl,
    /// Generate all formats
    All,
}

#[derive(Parser)]
pub struct CleanupCommand {
    /// Clean all test artifacts in current directory
    #[arg(long, default_value = "true")]
    pub test_artifacts: bool,
    
    /// Clean empty directories
    #[arg(long, default_value = "true")]
    pub empty_dirs: bool,
    
    /// Clean backup directories (.backup, .old, etc)
    #[arg(long, default_value = "true")]
    pub backups: bool,
    
    /// Preserve directories containing spec files
    #[arg(long, default_value = "true")]
    pub preserve_specs: bool,
    
    /// Target directory to clean (defaults to current directory)
    #[arg(short, long, default_value = ".")]
    pub path: PathBuf,
    
    /// Dry run - show what would be deleted without actually deleting
    #[arg(long)]
    pub dry_run: bool,
}

#[derive(Parser)]
pub struct ShowCommand {
    /// Operation to show details for (e.g., create-customer, list-users)
    pub operation: String,
    
    /// Path to the API specification file (defaults to specs/api.yaml)
    #[arg(short, long)]
    pub spec: Option<PathBuf>,
    
    /// Show examples for the operation
    #[arg(long)]
    pub examples: bool,
    
    /// Output format
    #[arg(short, long, value_enum, default_value = "pretty")]
    pub format: ShowFormat,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum ShowFormat {
    /// Human-readable format with colors
    Pretty,
    /// JSON output
    Json,
    /// YAML output
    Yaml,
}

#[derive(Parser)]
pub struct InitConfigCommand {
    /// Environment name (e.g., development, staging, production)
    #[arg(short, long, default_value = "development")]
    pub env: String,
    
    /// API to configure (e.g., stripe, github, openai)
    #[arg(short, long)]
    pub api: Option<String>,
    
    /// Output path for the config file
    #[arg(short, long)]
    pub output: Option<PathBuf>,
    
    /// Force overwrite if config already exists
    #[arg(short, long)]
    pub force: bool,
}

#[derive(Parser)]
pub struct ExploreCommand {
    /// Keyword to search for in operations, paths, and descriptions
    pub keyword: String,
    
    /// Path to the API specification file (defaults to specs/api.yaml)
    #[arg(short, long)]
    pub spec: Option<PathBuf>,
    
    /// Maximum number of results to show per category
    #[arg(short, long, default_value = "5")]
    pub limit: usize,
    
    /// Show detailed results including descriptions
    #[arg(long)]
    pub detailed: bool,
    
    /// Output format
    #[arg(short, long, value_enum, default_value = "pretty")]
    pub format: ExploreFormat,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum ExploreFormat {
    /// Human-readable format with colors and grouping
    Pretty,
    /// Simple list format
    Simple,
    /// JSON output for machine processing
    Json,
}

#[derive(Parser)]
pub struct AuthCommand {
    #[command(subcommand)]
    pub command: AuthCommands,
}

#[derive(Subcommand)]
pub enum AuthCommands {
    /// Login to an OAuth provider
    Login {
        /// Provider name (github, google, microsoft, etc.) or 'custom' for custom provider
        provider: String,
        
        /// Client ID (required for custom providers)
        #[arg(long)]
        client_id: Option<String>,
        
        /// Client Secret (for custom providers)
        #[arg(long)]
        client_secret: Option<String>,
        
        /// Authorization URL (required for custom providers)
        #[arg(long)]
        auth_url: Option<String>,
        
        /// Token URL (required for custom providers) 
        #[arg(long)]
        token_url: Option<String>,
        
        /// OAuth scopes to request (space-separated)
        #[arg(long, value_delimiter = ' ')]
        scopes: Vec<String>,
        
        /// Profile name (defaults to provider name)
        #[arg(long)]
        profile: Option<String>,
        
        /// Show provider-specific setup instructions
        #[arg(long)]
        setup_help: bool,
    },
    
    /// List stored auth profiles
    List {
        /// Show detailed information
        #[arg(long)]
        detailed: bool,
    },
    
    /// Show auth profile details
    Show {
        /// Profile name to show
        profile: String,
        
        /// Show decrypted tokens (security warning)
        #[arg(long)]
        show_tokens: bool,
    },
    
    /// Refresh tokens for a profile
    Refresh {
        /// Profile name to refresh
        profile: String,
    },
    
    /// Remove auth profile
    Logout {
        /// Profile name to remove
        profile: String,
        
        /// Skip confirmation prompt
        #[arg(long)]
        force: bool,
    },
    
    /// Test authentication by making a simple API call
    Test {
        /// Profile name to test
        profile: String,
    },
    
    /// Show setup instructions for a provider
    Setup {
        /// Provider name (github, google, microsoft, etc.)
        provider: String,
    },
}

#[derive(Parser)]
pub struct FlattenCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,
    
    /// Output file path (defaults to stdout if not specified)
    #[arg(short, long)]
    pub output: Option<PathBuf>,
    
    /// Output format (json or yaml)
    #[arg(short, long, value_enum, default_value = "yaml")]
    pub format: FlattenFormat,
    
    /// Include schemas that are not referenced
    #[arg(long)]
    pub include_unused: bool,
    
    /// Resolve external references (http:// or file paths)
    #[arg(long)]
    pub resolve_external: bool,
    
    /// Allow insecure HTTP connections when resolving external references (not recommended)
    #[arg(long)]
    pub allow_insecure: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum FlattenFormat {
    /// YAML format
    Yaml,
    /// JSON format  
    Json,
}

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

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum SdkLanguage {
    /// TypeScript (fetch-based)
    Typescript,
    /// Python (httpx-based)
    Python,
    /// Go (net/http-based)
    Go,
    /// Rust (reqwest-based)
    Rust,
}

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

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum DiffFormat {
    /// Human-readable text format
    Text,
    /// JSON format for tooling
    Json,
    /// Markdown format for PRs
    Markdown,
}

#[derive(Parser)]
pub struct ResolveCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,
    
    /// Output file path (shows summary if not specified)
    #[arg(short, long)]
    pub output: Option<PathBuf>,
    
    /// Resolve external references (http:// or file paths)
    #[arg(long)]
    pub external: bool,
    
    /// Validate after resolving
    #[arg(long, default_value = "true")]
    pub validate: bool,
}