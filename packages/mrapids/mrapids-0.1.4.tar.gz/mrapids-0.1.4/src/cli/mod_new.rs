use clap::{Parser, Subcommand};
use std::path::PathBuf;

/// Global flags available to all commands
#[derive(Parser, Debug, Clone)]
pub struct GlobalOpts {
    /// Path to OpenAPI specification file or URL
    #[arg(long, global = true)]
    pub spec: Option<String>,
    
    /// Environment name (dev, staging, prod)
    #[arg(long, global = true)]
    pub env: Option<String>,
    
    /// Authentication profile name
    #[arg(long, global = true)]
    pub profile: Option<String>,
    
    /// Output format
    #[arg(long, global = true, value_enum)]
    pub output: Option<OutputFormat>,
    
    /// JSONPath expression to filter output
    #[arg(long, global = true)]
    pub select: Option<String>,
    
    /// Disable colored output
    #[arg(long, global = true)]
    pub no_color: bool,
    
    /// Suppress all output except errors
    #[arg(long, short, global = true)]
    pub quiet: bool,
    
    /// Enable verbose output
    #[arg(long, short, global = true)]
    pub verbose: bool,
    
    /// Enable trace output (includes HTTP requests/responses)
    #[arg(long, global = true)]
    pub trace: bool,
    
    /// Automatic yes to prompts
    #[arg(long, short, global = true)]
    pub yes: bool,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum OutputFormat {
    /// JSON output
    Json,
    /// YAML output
    Yaml,
    /// Table output
    Table,
    /// Human-readable output
    Pretty,
}

/// Exit codes for consistent scripting
pub mod exit_codes {
    pub const SUCCESS: i32 = 0;
    pub const UNKNOWN_ERROR: i32 = 1;
    pub const USAGE_ERROR: i32 = 2;
    pub const AUTH_ERROR: i32 = 3;
    pub const NETWORK_ERROR: i32 = 4;
    pub const RATE_LIMIT_ERROR: i32 = 5;
    pub const SERVER_ERROR: i32 = 6;
    pub const VALIDATION_ERROR: i32 = 7;
    pub const BREAKING_CHANGE: i32 = 8;
}

#[derive(Parser)]
#[command(name = "mrapids")]
#[command(about = "Your OpenAPI, but executable", long_about = None)]
#[command(version)]
pub struct Args {
    #[command(subcommand)]
    pub command: Commands,
    
    #[command(flatten)]
    pub global: GlobalOpts,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Initialize a new MicroRapid project from an OpenAPI spec
    Init(InitCommand),
    
    /// Manage CLI configuration (create, view, edit)
    Config(ConfigCommand),
    
    /// Remove temporary files and test artifacts
    Cleanup(CleanupCommand),
    
    /// Validate an OpenAPI spec and lint for best practices
    Validate(ValidateCommand),
    
    /// Bundle/dereference a spec by resolving all $ref values
    Resolve(ResolveCommand),
    
    /// Compare two specs and report breaking changes
    Diff(DiffCommand),
    
    /// List operations, schemas, or components
    List(ListCommand),
    
    /// Show details for an operation or component
    Show(ShowCommand),
    
    /// Find operations, schemas, or examples by keyword
    Search(SearchCommand),
    
    /// Execute an API operation from the spec
    Run(RunCommand),
    
    /// Run contract tests derived from the spec
    Test(TestCommand),
    
    /// Test suite management
    Tests(TestsCommand),
    
    /// Generate code and artifacts
    Gen(GenCommand),
    
    /// Manage OAuth authentication
    Auth(AuthCommand),
    
    /// Show help for commands and topics
    Help(HelpCommand),
}

// Projects Commands

#[derive(Parser)]
pub struct InitCommand {
    /// Project name
    #[arg(default_value = "my-api-project")]
    pub name: String,
    
    /// Initialize from URL
    #[arg(long, value_name = "URL", conflicts_with = "from_file")]
    pub from: Option<String>,
    
    /// Initialize from local file
    #[arg(long, value_name = "FILE", conflicts_with = "from")]
    pub from_file: Option<String>,
    
    /// Project template
    #[arg(long, default_value = "rest")]
    pub template: String,
    
    /// Force overwrite
    #[arg(long)]
    pub force: bool,
}

#[derive(Parser)]
pub struct ConfigCommand {
    #[command(subcommand)]
    pub action: Option<ConfigAction>,
}

#[derive(Subcommand)]
pub enum ConfigAction {
    /// Set a configuration value
    Set {
        key: String,
        value: String,
        #[arg(long)]
        env: Option<String>,
    },
    /// Get a configuration value
    Get {
        key: String,
        #[arg(long)]
        env: Option<String>,
    },
    /// List all configuration
    List,
    /// Edit configuration interactively
    Edit {
        #[arg(long)]
        env: Option<String>,
    },
}

#[derive(Parser)]
pub struct CleanupCommand {
    /// Clean cache files
    #[arg(long)]
    pub cache: bool,
    
    /// Clean log files
    #[arg(long)]
    pub logs: bool,
    
    /// Clean all (except config)
    #[arg(long)]
    pub all: bool,
    
    /// Keep configuration files
    #[arg(long)]
    pub keep_config: bool,
    
    /// Preview what will be deleted
    #[arg(long)]
    pub dry_run: bool,
}

// Specs Commands

#[derive(Parser)]
pub struct ValidateCommand {
    /// Path to OpenAPI specification
    pub spec: Option<PathBuf>,
    
    /// Strict mode - treat warnings as errors
    #[arg(long)]
    pub strict: bool,
    
    /// Enable linting rules
    #[arg(long)]
    pub lint: bool,
    
    /// Custom rules file
    #[arg(long)]
    pub rules: Option<PathBuf>,
    
    /// Output format
    #[arg(long, value_enum)]
    pub format: Option<ValidateFormat>,
    
    /// Fail on level (warning, error)
    #[arg(long)]
    pub fail_on: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum ValidateFormat {
    Text,
    Json,
}

#[derive(Parser)]
pub struct ResolveCommand {
    /// Input specification
    pub spec: Option<PathBuf>,
    
    /// Bundle into single file
    #[arg(long)]
    pub bundle: bool,
    
    /// Only resolve external references
    #[arg(long)]
    pub external_only: bool,
    
    /// Output file
    #[arg(long, short)]
    pub output: Option<PathBuf>,
    
    /// Specific path to resolve
    #[arg(long)]
    pub path: Option<String>,
    
    /// Validate after resolving
    #[arg(long)]
    pub validate: bool,
}

#[derive(Parser)]
pub struct DiffCommand {
    /// First specification (old/base)
    pub spec1: PathBuf,
    
    /// Second specification (new)
    pub spec2: PathBuf,
    
    /// Only show breaking changes
    #[arg(long)]
    pub breaking: bool,
    
    /// Output format
    #[arg(long, value_enum)]
    pub format: Option<DiffFormat>,
    
    /// Ignore description changes
    #[arg(long)]
    pub ignore_descriptions: bool,
    
    /// Fail on level
    #[arg(long)]
    pub fail_on: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum DiffFormat {
    Text,
    Json,
    Markdown,
}

// Discoverability Commands

#[derive(Parser)]
pub struct ListCommand {
    #[command(subcommand)]
    pub resource: ListResource,
}

#[derive(Subcommand)]
pub enum ListResource {
    /// List operations
    Operations {
        spec: Option<PathBuf>,
        #[arg(long)]
        filter: Vec<String>,
    },
    /// List schemas
    Schemas {
        spec: Option<PathBuf>,
        #[arg(long)]
        filter: Vec<String>,
    },
    /// List examples
    Examples {
        spec: Option<PathBuf>,
    },
    /// List saved requests
    Requests,
}

#[derive(Parser)]
pub struct ShowCommand {
    /// Name of operation or component
    pub name: String,
    
    /// Specification file
    pub spec: Option<PathBuf>,
    
    /// Type of resource (operation, schema, example)
    #[arg(long, default_value = "operation")]
    pub r#type: String,
    
    /// Include examples
    #[arg(long)]
    pub examples: bool,
    
    /// Verbose output
    #[arg(long)]
    pub verbose: bool,
}

#[derive(Parser)]
pub struct SearchCommand {
    /// Search keyword
    pub keyword: String,
    
    /// Specification file
    pub spec: Option<PathBuf>,
    
    /// Search in descriptions
    #[arg(long)]
    pub in_descriptions: bool,
    
    /// Case sensitive search
    #[arg(long)]
    pub case_sensitive: bool,
    
    /// Search in specific areas
    #[arg(long, value_delimiter = ',')]
    pub r#in: Vec<String>,
}

// Execution Commands

#[derive(Parser)]
pub struct RunCommand {
    /// Specification file
    pub spec: Option<PathBuf>,
    
    /// Operation ID
    #[arg(long, group = "operation_select")]
    pub op_id: Option<String>,
    
    /// Operation path
    #[arg(long, requires = "method", group = "operation_select")]
    pub path: Option<String>,
    
    /// HTTP method
    #[arg(long, requires = "path")]
    pub method: Option<String>,
    
    /// Parameters as key=value
    #[arg(long = "param", value_name = "KEY=VALUE")]
    pub params: Vec<String>,
    
    /// Request body file
    #[arg(long)]
    pub body: Option<PathBuf>,
    
    /// Preview without executing
    #[arg(long)]
    pub dry_run: bool,
    
    /// Show as curl command
    #[arg(long)]
    pub curl_output: bool,
}

#[derive(Parser)]
pub struct TestCommand {
    /// Specification file
    pub spec: Option<PathBuf>,
    
    /// Operation ID to test
    #[arg(long)]
    pub op_id: Option<String>,
    
    /// Test all operations
    #[arg(long)]
    pub all: bool,
    
    /// Test from file
    #[arg(long)]
    pub from: Option<PathBuf>,
    
    /// Validate responses
    #[arg(long)]
    pub validate: bool,
    
    /// Load test iterations
    #[arg(long)]
    pub load: Option<u32>,
    
    /// Concurrent requests
    #[arg(long)]
    pub concurrent: Option<u32>,
    
    /// Test report output
    #[arg(long)]
    pub report: Option<PathBuf>,
    
    /// Output format
    #[arg(long)]
    pub format: Option<TestFormat>,
    
    /// Fail on level
    #[arg(long)]
    pub fail_on: Option<String>,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum TestFormat {
    Text,
    Json,
    Junit,
}

#[derive(Parser)]
pub struct TestsCommand {
    #[command(subcommand)]
    pub action: TestsAction,
}

#[derive(Subcommand)]
pub enum TestsAction {
    /// Scaffold a test suite from the spec
    Init {
        spec: Option<PathBuf>,
        #[arg(long)]
        framework: Option<String>,
        #[arg(long)]
        with_ci: Option<String>,
        #[arg(long, short)]
        output: Option<PathBuf>,
    },
}

// Generation Commands

#[derive(Parser)]
pub struct GenCommand {
    #[command(subcommand)]
    pub target: GenTarget,
}

#[derive(Subcommand)]
pub enum GenTarget {
    /// Generate example requests and payloads
    Snippets {
        spec: Option<PathBuf>,
        #[arg(long)]
        op_id: Option<String>,
        #[arg(long, value_enum)]
        format: Option<SnippetFormat>,
        #[arg(long, short)]
        output: Option<PathBuf>,
    },
    /// Generate an SDK in the selected language
    Sdk {
        spec: Option<PathBuf>,
        #[arg(long, value_delimiter = ',')]
        lang: Vec<String>,
        #[arg(long)]
        package: Option<String>,
        #[arg(long)]
        with_docs: bool,
        #[arg(long)]
        template: Option<PathBuf>,
    },
    /// Generate server stubs
    Stubs {
        spec: Option<PathBuf>,
        #[arg(long)]
        framework: String,
        #[arg(long)]
        with_tests: bool,
        #[arg(long, short)]
        output: Option<PathBuf>,
    },
    /// Generate sample requests/responses as files
    Fixtures {
        spec: Option<PathBuf>,
        #[arg(long)]
        schema: Vec<String>,
        #[arg(long)]
        count: Option<u32>,
        #[arg(long)]
        seed: Option<u64>,
        #[arg(long, value_enum)]
        format: Option<FixtureFormat>,
    },
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum SnippetFormat {
    Curl,
    Httpie,
    Fetch,
    Axios,
    Requests,
}

#[derive(Clone, Debug, PartialEq, Eq, clap::ValueEnum)]
pub enum FixtureFormat {
    Json,
    Yaml,
}

// Auth Commands

#[derive(Parser)]
pub struct AuthCommand {
    #[command(subcommand)]
    pub action: AuthAction,
}

#[derive(Subcommand)]
pub enum AuthAction {
    /// OAuth login flow
    Login {
        provider: String,
        #[arg(long)]
        scopes: Option<String>,
        #[arg(long)]
        auth_url: Option<String>,
    },
    /// Remove credentials
    Logout {
        provider: Option<String>,
        #[arg(long)]
        all: bool,
        #[arg(long)]
        force: bool,
    },
    /// Show auth status
    Status {
        provider: Option<String>,
        #[arg(long)]
        test: bool,
    },
}

#[derive(Parser)]
pub struct HelpCommand {
    /// Command to show help for
    pub command: Option<String>,
}