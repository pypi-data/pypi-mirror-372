use clap::{Parser, Subcommand};
use std::path::PathBuf;

#[derive(Parser)]
#[command(name = "mrapids")]
#[command(about = "Your OpenAPI, but executable", long_about = None)]
#[command(version)]
#[command(before_help = crate::core::banner::get_help_header())]
#[command(after_help = get_help_footer())]
#[command(override_help = get_grouped_help())]
pub struct Args {
    #[command(subcommand)]
    pub command: Commands,

    /// Global: Environment name (dev, staging, prod)
    #[arg(long, global = true, value_name = "ENV")]
    pub env: Option<String>,

    /// Global: Output format (json, yaml, table, pretty)
    #[arg(long = "output-format", global = true, value_name = "FORMAT")]
    pub output_format: Option<String>,

    /// Global: Suppress all output except errors
    #[arg(long, short = 'q', global = true)]
    pub quiet: bool,

    /// Global: Enable verbose output
    #[arg(long, short = 'v', global = true)]
    pub verbose: bool,

    /// Global: Enable trace output (includes HTTP requests/responses)
    #[arg(long, global = true)]
    pub trace: bool,

    /// Global: Disable colored output
    #[arg(long, global = true)]
    pub no_color: bool,
}

#[derive(Subcommand)]
pub enum Commands {
    // === GETTING STARTED ===
    /// Initialize a new MicroRapid project from OpenAPI/GraphQL specs
    #[command(display_order = 1)]
    Init(InitCommand),

    /// Discover what operations are available in your API
    #[command(alias = "search", alias = "discover", display_order = 2)]
    Explore(ExploreCommand),

    /// Show detailed information about specific operations
    #[command(display_order = 3)]
    Show(ShowCommand),

    /// Ensure your OpenAPI specification is correct
    #[command(display_order = 4)]
    Validate(ValidateCommand),

    // === EXECUTION & TESTING ===
    /// Execute API operations directly from specifications
    #[command(display_order = 5)]
    Run(RunCommand),

    /// Run automated tests against your API
    #[command(display_order = 6)]
    Test(TestCommand),

    /// List available operations, requests, or resources
    #[command(display_order = 7)]
    List(ListCommand),

    // === CODE GENERATION ===
    /// Generate SDKs, examples, test fixtures, and code
    #[command(alias = "generate", display_order = 8)]
    Gen(GenCommand),

    /// Resolve all $ref references in your specification
    #[command(display_order = 9)]
    Flatten(FlattenCommand),

    // === AUTOMATION & WORKFLOWS ===
    /// Manage and run complex API request collections
    #[command(display_order = 10)]
    Collection(CollectionCommand),

    /// Set up complete test environment automatically
    #[command(alias = "tests-init", display_order = 11)]
    SetupTests(SetupTestsCommand),

    // === CONFIGURATION ===
    /// Manage OAuth and API authentication
    #[command(display_order = 12)]
    Auth(AuthCommand),

    /// Initialize environment configurations
    #[command(alias = "config", display_order = 13)]
    InitConfig(InitConfigCommand),

    // === UTILITIES ===
    /// Compare specifications for breaking changes
    #[command(display_order = 14)]
    Diff(DiffCommand),

    /// Clean up test artifacts and temporary files
    #[command(display_order = 15)]
    Cleanup(CleanupCommand),
}

#[derive(Parser)]
pub struct ValidateCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: PathBuf,

    /// Strict mode - treat warnings as errors
    #[arg(long)]
    pub strict: bool,

    /// Enable linting for best practices and style issues
    #[arg(long)]
    pub lint: bool,

    /// Custom linting rules file
    #[arg(long, requires = "lint")]
    pub rules: Option<PathBuf>,

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
#[command(
    args_override_self = true,
    after_help = "EXAMPLES:
    # Execute an API operation
    mrapids run users/get-by-username --param username=octocat
    
    # POST request with data
    mrapids run repos/create --data '{\"name\": \"my-repo\"}'
    
    # Use authentication profile
    mrapids run users/get-authenticated --profile github
    
    # Search with special characters (NO encoding needed - mrapids handles it)
    mrapids run search/repos --param q=\"language:javascript stars:>1000\" --param sort=stars
    
    # Save response to file
    mrapids run users/list --save users.json
    
    # Show as curl command
    mrapids run repos/get --param owner=octocat --param repo=hello-world --as-curl

IMPORTANT TIPS:
    • Parameters are automatically URL-encoded - pass them as plain text
    • Use quotes for values with spaces: --param q=\"user:octocat type:pr\"
    • Data can be read from file: --data @request.json or --file request.json"
)]
pub struct RunCommand {
    /// Operation ID (e.g., users/get, repos/create) or path to request config file
    pub operation: String,

    // === DATA INPUT ===
    /// Request body as JSON string or @file.json
    #[arg(short, long, conflicts_with = "file", help_heading = "Data Input")]
    pub data: Option<String>,

    /// Read request body from file
    #[arg(short, long, conflicts_with = "data", help_heading = "Data Input")]
    pub file: Option<PathBuf>,

    // === COMMON PARAMETERS ===
    /// Resource ID (auto-mapped to path/query parameters)
    #[arg(long, help_heading = "Common Parameters")]
    pub id: Option<String>,

    /// Resource name
    #[arg(long, help_heading = "Common Parameters")]
    pub name: Option<String>,

    /// Filter by status
    #[arg(long, help_heading = "Common Parameters")]
    pub status: Option<String>,

    /// Limit number of results
    #[arg(long, help_heading = "Common Parameters")]
    pub limit: Option<u32>,

    /// Offset for pagination
    #[arg(long, help_heading = "Common Parameters")]
    pub offset: Option<u32>,

    /// Sort order
    #[arg(long, help_heading = "Common Parameters")]
    pub sort: Option<String>,

    // === REQUEST PARAMETERS ===
    /// Set any parameter: --param key=value (can be used multiple times)
    #[arg(
        long = "param",
        value_name = "KEY=VALUE",
        help_heading = "Request Parameters"
    )]
    pub params: Vec<String>,

    /// Force query parameters: --query key=value (can be used multiple times)
    #[arg(
        long = "query",
        value_name = "KEY=VALUE",
        help_heading = "Request Parameters"
    )]
    pub query_params: Vec<String>,

    /// Add HTTP headers: --header "Key: Value" (can be used multiple times)
    #[arg(
        short = 'H',
        long = "header",
        value_name = "KEY: VALUE",
        help_heading = "Request Parameters"
    )]
    pub headers: Vec<String>,

    // === AUTHENTICATION ===
    /// Bearer token or Basic auth (e.g., "Bearer token123" or "Basic base64")
    #[arg(long, conflicts_with = "auth_profile", help_heading = "Authentication")]
    pub auth: Option<String>,

    /// API key for X-API-Key header
    #[arg(long, conflicts_with = "auth_profile", help_heading = "Authentication")]
    pub api_key: Option<String>,

    /// Use saved OAuth/auth profile
    #[arg(long = "profile", value_name = "PROFILE", conflicts_with_all = &["auth", "api_key"], help_heading = "Authentication")]
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

    // === OUTPUT & DEBUGGING ===
    /// Use only required fields in requests
    #[arg(long, help_heading = "Testing & Debugging")]
    pub required_only: bool,

    /// Show detailed request/response info
    #[arg(short, long, help_heading = "Testing & Debugging")]
    pub verbose: bool,

    /// Preview request without sending
    #[arg(long, help_heading = "Testing & Debugging")]
    pub dry_run: bool,

    /// Show equivalent curl command
    #[arg(long, help_heading = "Testing & Debugging")]
    pub as_curl: bool,

    /// Edit generated data before sending
    #[arg(long, help_heading = "Data Input")]
    pub edit: bool,

    /// Read request body from stdin
    #[arg(long, help_heading = "Data Input")]
    pub stdin: bool,

    // === REQUEST OPTIONS ===
    /// Number of retries for failed requests
    #[arg(long, default_value = "0", help_heading = "Request Options")]
    pub retry: u32,

    /// Request timeout in seconds
    #[arg(long, default_value = "30", help_heading = "Request Options")]
    pub timeout: u32,

    /// Allow insecure HTTPS connections (skip certificate validation)
    #[arg(long, help_heading = "Security")]
    pub allow_insecure: bool,

    /// Suppress warnings about sensitive data in requests
    #[arg(long, help_heading = "Security")]
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

// Still used internally by gen snippets
#[derive(Parser)]
pub struct AnalyzeCommand {
    /// Path to the OpenAPI/Swagger specification file
    pub spec: Option<PathBuf>,

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

    /// Path to OpenAPI specification file (optional)
    pub spec: Option<PathBuf>,

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

    /// Path to the API specification file
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
    #[arg(long, alias = "breaking")]
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
pub struct GenCommand {
    #[command(subcommand)]
    pub target: GenTarget,
}

#[derive(Subcommand)]
pub enum GenTarget {
    /// Generate example requests and responses (replaces 'analyze')
    Snippets(GenSnippetsCommand),

    /// Generate SDK client library (replaces 'sdk')
    Sdk(GenSdkCommand),

    /// Generate server stubs (replaces 'generate')
    Stubs(GenStubsCommand),

    /// Generate test fixtures and sample data
    Fixtures(GenFixturesCommand),
}

#[derive(Parser)]
pub struct GenSnippetsCommand {
    /// Path to the OpenAPI specification
    pub spec: Option<PathBuf>,

    /// Output directory for examples
    #[arg(short, long, default_value = "./examples")]
    pub output: PathBuf,

    /// Operation ID to generate examples for (all if not specified)
    #[arg(long)]
    pub operation: Option<String>,

    /// Example format
    #[arg(long, value_enum, default_value = "json")]
    pub format: SnippetFormat,

    /// Include curl examples
    #[arg(long)]
    pub curl: bool,

    /// Include HTTPie examples
    #[arg(long)]
    pub httpie: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum SnippetFormat {
    Json,
    Yaml,
    Curl,
    Httpie,
    All,
}

#[derive(Parser)]
pub struct GenSdkCommand {
    /// Path to the OpenAPI specification
    pub spec: Option<PathBuf>,

    /// Target language
    #[arg(short, long, value_enum)]
    pub language: SdkLanguage,

    /// Output directory
    #[arg(short, long)]
    pub output: Option<PathBuf>,

    /// Package name
    #[arg(long)]
    pub package: Option<String>,

    /// Include documentation
    #[arg(long, default_value = "true")]
    pub docs: bool,

    /// Include examples
    #[arg(long, default_value = "true")]
    pub examples: bool,
}

#[derive(Parser)]
pub struct GenStubsCommand {
    /// Path to the OpenAPI specification
    pub spec: Option<PathBuf>,

    /// Target framework
    #[arg(short, long)]
    pub framework: String,

    /// Output directory
    #[arg(short, long)]
    pub output: Option<PathBuf>,

    /// Include tests
    #[arg(long)]
    pub with_tests: bool,

    /// Include validation
    #[arg(long)]
    pub with_validation: bool,
}

#[derive(Parser)]
pub struct GenFixturesCommand {
    /// Path to the OpenAPI specification
    pub spec: Option<PathBuf>,

    /// Output directory
    #[arg(short, long, default_value = "./fixtures")]
    pub output: PathBuf,

    /// Number of samples per schema
    #[arg(long, default_value = "10")]
    pub count: u32,

    /// Specific schemas to generate (all if not specified)
    #[arg(long)]
    pub schema: Vec<String>,

    /// Random seed for deterministic output
    #[arg(long)]
    pub seed: Option<u64>,

    /// Output format
    #[arg(long, value_enum, default_value = "json")]
    pub format: FixtureFormat,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum FixtureFormat {
    Json,
    Yaml,
    Csv,
}

#[derive(Parser)]
pub struct CollectionCommand {
    #[command(subcommand)]
    pub command: CollectionSubcommand,
}

#[derive(Subcommand)]
pub enum CollectionSubcommand {
    /// List available collections
    List {
        /// Directory containing collections
        #[arg(long, default_value = ".mrapids/collections")]
        dir: PathBuf,
    },

    /// Show details of a collection
    Show {
        /// Collection name
        name: String,

        /// Directory containing collections
        #[arg(long, default_value = ".mrapids/collections")]
        dir: PathBuf,
    },

    /// Validate collection syntax and operations
    Validate {
        /// Collection name
        name: String,

        /// Directory containing collections
        #[arg(long, default_value = ".mrapids/collections")]
        dir: PathBuf,

        /// Path to API specification
        #[arg(long)]
        spec: Option<PathBuf>,
    },

    /// Run a collection
    Run {
        /// Collection name
        name: String,

        /// Directory containing collections
        #[arg(long, default_value = ".mrapids/collections")]
        dir: PathBuf,

        /// Output format (json, yaml, pretty)
        #[arg(long, default_value = "pretty")]
        output: String,

        /// Save all responses to directory
        #[arg(long)]
        save_all: Option<PathBuf>,

        /// Save execution summary
        #[arg(long)]
        save_summary: Option<PathBuf>,

        /// Override variables (key=value)
        #[arg(long = "var", value_parser = parse_key_val::<String, String>)]
        variables: Vec<(String, String)>,

        /// Authentication profile to use
        #[arg(long = "profile", value_name = "PROFILE")]
        auth_profile: Option<String>,

        /// Continue execution on errors
        #[arg(long)]
        continue_on_error: bool,

        /// Run specific request(s)
        #[arg(long = "request")]
        requests: Vec<String>,

        /// Skip specific request(s)
        #[arg(long = "skip")]
        skip_requests: Vec<String>,

        /// Use environment variables
        #[arg(long)]
        use_env: bool,

        /// Path to .env file
        #[arg(long)]
        env_file: Option<PathBuf>,

        /// Path to API specification
        #[arg(long)]
        spec: Option<PathBuf>,

        /// Environment name
        #[arg(long)]
        env: Option<String>,
    },

    /// Run collection as tests
    Test {
        /// Collection name
        name: String,

        /// Directory containing collections
        #[arg(long, default_value = ".mrapids/collections")]
        dir: PathBuf,

        /// Path to API specification
        #[arg(long)]
        spec: Option<PathBuf>,

        /// Authentication profile to use
        #[arg(long = "profile", value_name = "PROFILE")]
        auth_profile: Option<String>,

        /// Output format (pretty, json, junit)
        #[arg(long, default_value = "pretty")]
        output: String,

        /// Continue on test failures
        #[arg(long)]
        continue_on_error: bool,
    },
}

/// Parse key=value pairs
fn parse_key_val<T, U>(
    s: &str,
) -> Result<(T, U), Box<dyn std::error::Error + Send + Sync + 'static>>
where
    T: std::str::FromStr,
    T::Err: std::error::Error + Send + Sync + 'static,
    U: std::str::FromStr,
    U::Err: std::error::Error + Send + Sync + 'static,
{
    let pos = s
        .find('=')
        .ok_or_else(|| format!("invalid KEY=value: no `=` found in `{}`", s))?;
    Ok((s[..pos].parse()?, s[pos + 1..].parse()?))
}

/// Get the grouped help display with section headers
fn get_grouped_help() -> &'static str {
    r#"      ╭──────────────────────────────────────────╮
      │   ○ ○     M I C R O   R A P I D     ○ ○  │
      │    ╲ ╱                               ╲ ╱   │
      │     ═       🤖 agent automation 🤖    ═    │
      │    ╱ ╲        your api, automated    ╱ ╲   │
      │   ○ ○                               ○ ○  │
      ╰──────────────────────────────────────────╯
      
         >> mrapids.exe --mode agent
         >> status: [READY] ████████████ 100%

Your OpenAPI, but executable

The blazing fast API automation toolkit

Usage: mrapids [OPTIONS] <COMMAND>

GETTING STARTED
  init          Initialize a new MicroRapid project
  explore       Discover what operations are available in your API
  show          Show detailed information about specific operations
  validate      Ensure your OpenAPI specification is correct

EXECUTION & TESTING  
  run           Execute API operations directly
  test          Run automated tests against your API
  list          List available operations, requests, or resources

CODE GENERATION
  gen           Generate SDKs, examples, test fixtures, and code
  flatten       Resolve all $ref references in your specification

AUTOMATION & WORKFLOWS
  collection    Manage and run complex API request collections
  setup-tests   Set up complete test environment automatically

CONFIGURATION
  auth          Manage OAuth and API authentication
  init-config   Initialize environment configurations
  
UTILITIES
  diff          Compare specifications for breaking changes
  cleanup       Clean up test artifacts and temporary files
  help          Print this message or the help of the given subcommand(s)

Options:
      --env <ENV>               Environment name (dev, staging, prod)
      --output-format <FORMAT>  Output format (json, yaml, table, pretty)
  -q, --quiet                   Suppress all output except errors
  -v, --verbose                 Enable verbose output
      --trace                   Enable trace output (includes HTTP requests/responses)
      --no-color                Disable colored output
  -h, --help                    Print help
  -V, --version                 Print version

EXAMPLES:
    # Start with a new project
    mrapids init my-api --from-url https://api.example.com/openapi.json
    
    # Explore available operations
    mrapids explore user
    
    # Execute an operation
    mrapids run GetUser --id 123
    
    # Generate an SDK
    mrapids gen sdk --language typescript --output ./sdk
    
    # Run a test collection
    mrapids collection run smoke-tests

For detailed help on any command:
    mrapids <command> --help

For more information, visit: https://microrapid.io/"#
}

/// Get the help footer with examples and additional information
fn get_help_footer() -> &'static str {
    r#"
EXAMPLES:
    # Start with a new project
    mrapids init my-api --from-url https://api.example.com/openapi.json
    
    # Explore available operations
    mrapids explore user
    
    # Execute an operation
    mrapids run GetUser --id 123
    
    # Generate an SDK
    mrapids gen sdk --language typescript --output ./sdk
    
    # Run a test collection
    mrapids collection run smoke-tests

For detailed help on any command:
    mrapids <command> --help

For more information, visit: https://microrapid.io/"#
}
