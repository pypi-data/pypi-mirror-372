#![warn(clippy::unwrap_used)]

mod cli;
mod core;
mod utils;

use anyhow::Result;
use clap::Parser;
use colored::*;
use std::env;
use std::path::PathBuf;
use std::process;

// Exit codes for consistent scripting
const EXIT_SUCCESS: i32 = 0;
const EXIT_UNKNOWN_ERROR: i32 = 1;
const EXIT_USAGE_ERROR: i32 = 2;
const EXIT_AUTH_ERROR: i32 = 3;
const EXIT_NETWORK_ERROR: i32 = 4;
const EXIT_RATE_LIMIT_ERROR: i32 = 5;
const EXIT_SERVER_ERROR: i32 = 6;
const EXIT_VALIDATION_ERROR: i32 = 7;
const EXIT_BREAKING_CHANGE: i32 = 8;

#[tokio::main]
async fn main() {
    let exit_code = match run().await {
        Ok(code) => code,
        Err(e) => {
            eprintln!("{}: {}", "Error".bright_red(), e);

            // Determine exit code based on error type
            if let Some(network_err) = e.downcast_ref::<reqwest::Error>() {
                if network_err.is_timeout() || network_err.is_connect() {
                    EXIT_NETWORK_ERROR
                } else if network_err.status() == Some(reqwest::StatusCode::TOO_MANY_REQUESTS) {
                    EXIT_RATE_LIMIT_ERROR
                } else if network_err.is_status() {
                    EXIT_SERVER_ERROR
                } else {
                    EXIT_UNKNOWN_ERROR
                }
            } else if e.to_string().to_lowercase().contains("auth")
                || e.to_string().to_lowercase().contains("authentication")
            {
                EXIT_AUTH_ERROR
            } else if e.to_string().to_lowercase().contains("validation")
                || e.to_string().to_lowercase().contains("invalid")
            {
                EXIT_VALIDATION_ERROR
            } else if e.to_string().to_lowercase().contains("breaking") {
                EXIT_BREAKING_CHANGE
            } else {
                EXIT_UNKNOWN_ERROR
            }
        }
    };

    process::exit(exit_code);
}

async fn run() -> Result<i32> {
    // Check if no arguments provided
    let args_count = env::args().count();
    if args_count == 1 {
        // Only the program name, no arguments
        core::display_banner();
        return Ok(EXIT_SUCCESS);
    }

    // Check for version flag early
    let args_vec: Vec<String> = env::args().collect();
    if args_vec.len() == 2 && (args_vec[1] == "--version" || args_vec[1] == "-V") {
        println!("{}", core::get_version_info());
        return Ok(EXIT_SUCCESS);
    }

    let args = match cli::Args::try_parse() {
        Ok(args) => args,
        Err(e) => {
            eprintln!("{}", e);
            return Ok(EXIT_USAGE_ERROR);
        }
    };

    // Apply global options
    if args.no_color {
        colored::control::set_override(false);
    }

    if args.trace {
        env::set_var("MRAPIDS_TRACE", "true");
    } else if args.verbose {
        env::set_var("MRAPIDS_VERBOSE", "true");
    }

    // Store global options in environment for commands to use
    if let Some(env_name) = &args.env {
        env::set_var("MRAPIDS_ENV", env_name);
    }
    if let Some(output) = &args.output_format {
        env::set_var("MRAPIDS_OUTPUT", output);
    }
    if args.quiet {
        env::set_var("MRAPIDS_QUIET", "true");
    }

    match args.command {
        cli::Commands::Init(cmd) => {
            core::init_command(cmd)?;
        }
        cli::Commands::Run(cmd) => {
            core::display_short_banner();
            core::run_command(cmd)?;
        }
        cli::Commands::Test(cmd) => {
            println!("{}", "🧪 Running tests...".bright_cyan());
            core::test_command(cmd)?;
        }
        cli::Commands::SetupTests(cmd) => {
            core::setup_tests_command(cmd)?;
        }
        cli::Commands::List(cmd) => {
            core::list_command(cmd)?;
        }
        cli::Commands::Show(cmd) => {
            core::show_command(cmd)?;
        }
        cli::Commands::Cleanup(cmd) => {
            core::cleanup_command(cmd)?;
        }
        cli::Commands::InitConfig(cmd) => {
            core::init_config_command(cmd)?;
        }
        cli::Commands::Explore(cmd) => {
            core::explore_command(cmd)?;
        }
        cli::Commands::Auth(cmd) => {
            handle_auth_command(cmd).await?;
        }
        cli::Commands::Flatten(cmd) => {
            core::flatten_command(cmd).await?;
        }
        cli::Commands::Validate(cmd) => {
            core::validate_command(cmd)?;
        }
        cli::Commands::Diff(cmd) => {
            core::diff_command(cmd)?;
        }
        cli::Commands::Gen(cmd) => {
            handle_gen_command(cmd).await?;
        }
        cli::Commands::Collection(cmd) => {
            handle_collection_command(cmd).await?;
        }
    }

    Ok(EXIT_SUCCESS)
}

async fn handle_gen_command(cmd: cli::GenCommand) -> Result<()> {
    use cli::GenTarget;

    match cmd.target {
        GenTarget::Snippets(snippets_cmd) => {
            // Call analyze_v2 directly
            println!("{}", "📝 Generating snippets...".bright_cyan());
            let analyze_cmd = cli::AnalyzeCommand {
                spec: snippets_cmd.spec,
                operation: snippets_cmd.operation,
                output: snippets_cmd.output,
                all: true,
                skip_data: false,
                skip_validate: false,
                force: true,
                cleanup_backups: true,
            };
            core::analyze_v2::analyze_command(analyze_cmd)?;
        }
        GenTarget::Sdk(sdk_cmd) => {
            // Call SDK generation directly
            println!("{}", "🔧 Generating SDK...".bright_cyan());
            let spec_path = sdk_cmd
                .spec
                .unwrap_or_else(|| PathBuf::from("specs/api.yaml"));
            let content = std::fs::read_to_string(&spec_path)?;
            let spec = core::parser::parse_spec(&content)?;

            let lang_str = match sdk_cmd.language {
                cli::SdkLanguage::Typescript => "typescript",
                cli::SdkLanguage::Python => "python",
                cli::SdkLanguage::Go => "go",
                cli::SdkLanguage::Rust => "rust",
            };

            let output_dir = sdk_cmd
                .output
                .unwrap_or_else(|| PathBuf::from(format!("./sdk-{}", lang_str)));

            // Generate SDK based on language
            match sdk_cmd.language {
                cli::SdkLanguage::Typescript => {
                    core::sdk_gen::typescript::generate_typescript_sdk(
                        &spec,
                        &output_dir,
                        sdk_cmd.package.as_deref(),
                        sdk_cmd.docs,
                        sdk_cmd.examples,
                    )?;
                }
                cli::SdkLanguage::Python => {
                    core::sdk_gen::python::generate_python_sdk(
                        &spec,
                        &output_dir,
                        sdk_cmd.package.as_deref(),
                        sdk_cmd.docs,
                        sdk_cmd.examples,
                    )?;
                }
                cli::SdkLanguage::Go => {
                    core::sdk_gen::go::generate_go_sdk(
                        &spec,
                        &output_dir,
                        sdk_cmd.package.as_deref(),
                        sdk_cmd.docs,
                        sdk_cmd.examples,
                    )?;
                }
                cli::SdkLanguage::Rust => {
                    core::sdk_gen::rust_gen::generate_rust_sdk(
                        &spec,
                        &output_dir,
                        sdk_cmd.package.as_deref(),
                        sdk_cmd.docs,
                        sdk_cmd.examples,
                    )?;
                }
            }

            println!("✅ SDK generated successfully in: {}", output_dir.display());
        }
        GenTarget::Stubs(stubs_cmd) => {
            // Generate server stubs based on framework
            let spec_path = stubs_cmd
                .spec
                .unwrap_or_else(|| PathBuf::from("specs/api.yaml"));
            let content = std::fs::read_to_string(&spec_path)?;
            let spec = core::parser::parse_spec(&content)?;

            let output_dir = stubs_cmd
                .output
                .unwrap_or_else(|| PathBuf::from("./generated"));

            core::stubs::generate_server_stubs(
                &spec,
                &stubs_cmd.framework,
                &output_dir,
                stubs_cmd.with_tests,
                stubs_cmd.with_validation,
            )?;
        }
        GenTarget::Fixtures(fixtures_cmd) => {
            // Generate test fixtures
            let spec_path = fixtures_cmd
                .spec
                .unwrap_or_else(|| PathBuf::from("specs/api.yaml"));
            let content = std::fs::read_to_string(&spec_path)?;
            let spec = core::parser::parse_spec(&content)?;

            // Convert format string to enum
            let format = match fixtures_cmd.format {
                cli::FixtureFormat::Json => core::fixtures::FixtureFormat::Json,
                cli::FixtureFormat::Yaml => core::fixtures::FixtureFormat::Yaml,
                cli::FixtureFormat::Csv => core::fixtures::FixtureFormat::Csv,
            };

            // For now, default to valid variant
            let variant = core::fixtures::FixtureVariant::Valid;

            core::fixtures::generate_fixtures(
                &spec,
                &fixtures_cmd.output,
                fixtures_cmd.count,
                fixtures_cmd.schema,
                fixtures_cmd.seed,
                format,
                variant,
            )?;
        }
    }

    Ok(())
}

async fn handle_auth_command(cmd: cli::AuthCommand) -> Result<()> {
    use crate::core::auth::{
        delete_profile, list_profiles, load_tokens, oauth_login, refresh_tokens, test_auth_profile,
    };
    use cli::AuthCommands;

    match cmd.command {
        AuthCommands::Login {
            provider,
            client_id,
            client_secret,
            auth_url,
            token_url,
            scopes,
            profile,
            setup_help,
        } => {
            if setup_help {
                println!(
                    "{}",
                    crate::core::auth::providers::get_provider_help(&provider)
                );
                return Ok(());
            }

            let profile_name = profile.unwrap_or_else(|| provider.clone());

            // Check if profile already exists
            if crate::core::auth::token_store::profile_exists(&profile_name) {
                println!("⚠️  Profile '{}' already exists. Use 'mrapids auth logout {}' first to remove it.", 
                    profile_name.bright_yellow(), profile_name);
                return Ok(());
            }

            let config = if provider.to_lowercase() == "custom" {
                // Custom provider requires all fields
                if client_id.is_none() || auth_url.is_none() || token_url.is_none() {
                    anyhow::bail!(
                        "Custom provider requires --client-id, --auth-url, and --token-url"
                    );
                }

                crate::core::auth::providers::create_custom_config(
                    &profile_name,
                    client_id.unwrap(),
                    client_secret,
                    auth_url.unwrap(),
                    token_url.unwrap(),
                    if scopes.is_empty() {
                        vec!["read".to_string()]
                    } else {
                        scopes
                    },
                )
            } else {
                // Known provider
                let mut config = crate::core::auth::providers::get_provider_config(&provider)?;

                // Override with provided values if any
                if let Some(id) = client_id {
                    config.client_id = id;
                }
                if let Some(secret) = client_secret {
                    config.client_secret = Some(secret);
                }
                if !scopes.is_empty() {
                    config.scopes = scopes;
                }

                // Check for default placeholders
                if config.client_id.starts_with("YOUR_") {
                    println!("⚠️  {} OAuth setup required:", provider.bright_yellow());
                    println!(
                        "{}",
                        crate::core::auth::providers::get_provider_help(&provider)
                    );
                    return Ok(());
                }

                config
            };

            oauth_login(config, profile_name).await?;
        }

        AuthCommands::List { detailed } => {
            let profiles = list_profiles()?;

            if profiles.is_empty() {
                println!(
                    "No auth profiles found. Use 'mrapids auth login <provider>' to create one."
                );
                return Ok(());
            }

            if detailed {
                use prettytable::{row, Table};
                let mut table = Table::new();
                table.add_row(row!["Profile", "Provider", "Created", "Last Used"]);

                for profile in profiles {
                    let last_used = profile
                        .last_used
                        .map(|dt| dt.format("%Y-%m-%d %H:%M").to_string())
                        .unwrap_or_else(|| "Never".to_string());

                    table.add_row(row![
                        profile.name.bright_green(),
                        profile.provider.bright_cyan(),
                        profile.created_at.format("%Y-%m-%d %H:%M"),
                        last_used
                    ]);
                }

                table.printstd();
            } else {
                println!("🔐 Auth Profiles:\n");
                for profile in profiles {
                    println!(
                        "  • {} ({})",
                        profile.name.bright_green(),
                        profile.provider.bright_cyan()
                    );
                }
                println!("\nUse 'mrapids auth list --detailed' for more information.");
            }
        }

        AuthCommands::Show {
            profile,
            show_tokens,
        } => {
            let auth_profile = crate::core::auth::token_store::load_profile(&profile)?;
            let provider_config = crate::core::auth::providers::load_provider_config(&profile)?;

            println!("🔐 Auth Profile: {}\n", profile.bright_green());
            println!("  Provider: {}", auth_profile.provider.bright_cyan());
            println!(
                "  Created: {}",
                auth_profile.created_at.format("%Y-%m-%d %H:%M")
            );
            if let Some(last_used) = auth_profile.last_used {
                println!("  Last Used: {}", last_used.format("%Y-%m-%d %H:%M"));
            }
            println!("  Scopes: {}", provider_config.scopes.join(", "));

            if show_tokens {
                println!("\n⚠️  {}:", "Token Information (SENSITIVE)".bright_red());
                let tokens = load_tokens(&profile)?;
                println!("  Token Type: {}", tokens.token_type);
                println!(
                    "  Access Token: {}...{}",
                    &tokens.access_token[..10.min(tokens.access_token.len())],
                    &tokens.access_token[tokens.access_token.len().saturating_sub(10)..]
                );
                if let Some(expires_at) = tokens.expires_at {
                    let remaining = expires_at.signed_duration_since(chrono::Utc::now());
                    if remaining.num_seconds() > 0 {
                        println!("  Expires In: {} minutes", remaining.num_minutes());
                    } else {
                        println!("  Status: {} (refresh required)", "EXPIRED".bright_red());
                    }
                }
                println!(
                    "  Has Refresh Token: {}",
                    if tokens.refresh_token.is_some() {
                        "Yes"
                    } else {
                        "No"
                    }
                );
            }
        }

        AuthCommands::Refresh { profile } => {
            refresh_tokens(&profile).await?;
        }

        AuthCommands::Logout { profile, force } => {
            if !force {
                println!(
                    "Are you sure you want to remove auth profile '{}'? [y/N] ",
                    profile.bright_yellow()
                );
                use std::io::{self, BufRead};
                let stdin = io::stdin();
                let mut lines = stdin.lock().lines();
                if let Some(Ok(line)) = lines.next() {
                    if !line.trim().eq_ignore_ascii_case("y") {
                        println!("Cancelled.");
                        return Ok(());
                    }
                }
            }

            delete_profile(&profile)?;
            println!(
                "✅ Auth profile '{}' removed successfully.",
                profile.bright_green()
            );
        }

        AuthCommands::Test { profile } => {
            test_auth_profile(&profile).await?;
        }

        AuthCommands::Setup { provider } => {
            println!(
                "{}",
                crate::core::auth::providers::get_provider_help(&provider)
            );
        }
    }

    Ok(())
}

async fn handle_collection_command(cmd: cli::CollectionCommand) -> Result<()> {
    use cli::CollectionSubcommand;
    use mrapids::collections::{
        find_collection, list_collections, parse_collection, validate_collection,
        CollectionExecutor, ConsoleReporter, ExecutionOptions,
    };
    use mrapids::core::parser::parse_spec;
    use serde_json::json;
    use std::collections::HashMap;

    match cmd.command {
        CollectionSubcommand::List { dir } => {
            let collections = list_collections(&dir)?;

            if collections.is_empty() {
                println!("No collections found in {:?}", dir);
                println!("\n💡 Create a collection YAML file in this directory to get started.");
            } else {
                println!("📚 Available collections:\n");
                for path in collections {
                    if let Some(name) = path.file_stem() {
                        println!("  • {}", name.to_string_lossy().bright_cyan());
                    }
                }
                println!("\nRun 'mrapids collection show <name>' for details");
            }
        }

        CollectionSubcommand::Show { name, dir } => {
            let path = find_collection(&dir, &name)?;
            let collection = parse_collection(&path)?;

            println!("📋 Collection: {}", collection.name.bright_cyan().bold());
            if let Some(desc) = &collection.description {
                println!("   {}", desc.dimmed());
            }
            println!("\n🔗 Requests ({}):", collection.requests.len());

            for (i, request) in collection.requests.iter().enumerate() {
                println!(
                    "   {}. {} → {}",
                    i + 1,
                    request.name.bright_green(),
                    request.operation.dimmed()
                );
            }

            if !collection.variables.is_empty() {
                println!("\n📝 Variables:");
                for (key, value) in &collection.variables {
                    println!(
                        "   {} = {}",
                        key.bright_yellow(),
                        serde_json::to_string(value).unwrap_or_else(|_| "?".to_string())
                    );
                }
            }

            if let Some(auth) = &collection.auth_profile {
                println!("\n🔐 Auth Profile: {}", auth.bright_magenta());
            }
        }

        CollectionSubcommand::Validate {
            name,
            dir,
            spec: spec_path,
        } => {
            let path = find_collection(&dir, &name)?;
            let collection = parse_collection(&path)?;

            // Load spec if provided
            let spec = if let Some(spec_path) = spec_path {
                let content = std::fs::read_to_string(&spec_path)?;
                Some(parse_spec(&content)?)
            } else {
                None
            };

            let result = validate_collection(&collection, spec.as_ref());

            if result.is_valid() {
                println!("✅ Collection '{}' is valid!", name.bright_green());
            } else {
                println!("❌ Collection '{}' has errors:", name.bright_red());
                for error in &result.errors {
                    println!("   • {}", error.red());
                }
            }

            if !result.warnings.is_empty() {
                println!("\n⚠️  Warnings:");
                for warning in &result.warnings {
                    println!("   • {}", warning.yellow());
                }
            }
        }

        CollectionSubcommand::Run {
            name,
            dir,
            output,
            save_all,
            save_summary,
            variables,
            auth_profile,
            continue_on_error,
            requests,
            skip_requests,
            use_env,
            env_file,
            spec: spec_path,
            env: _,
        } => {
            let path = find_collection(&dir, &name)?;
            let collection = parse_collection(&path)?;

            // Load spec
            let spec_path = spec_path.unwrap_or_else(|| PathBuf::from("specs/api.yaml"));
            let spec_content = std::fs::read_to_string(&spec_path)?;
            let spec = parse_spec(&spec_content)?;

            // Build execution options
            let mut variable_map = HashMap::new();
            for (key, value) in variables {
                variable_map.insert(key, json!(value));
            }

            let options = ExecutionOptions {
                continue_on_error,
                skip_requests,
                only_requests: if requests.is_empty() {
                    None
                } else {
                    Some(requests)
                },
                auth_profile,
                variable_overrides: variable_map,
                use_env,
                env_file,
                save_all,
                save_summary,
            };

            // TODO: Load auth profile
            let auth = None;

            // Create executor and reporter
            let executor = CollectionExecutor::new(spec, auth);
            let mut reporter = ConsoleReporter::new(output != "json");

            // Execute collection
            let summary = executor
                .execute(&collection, options, &mut reporter)
                .await?;

            // Output JSON if requested
            if output == "json" {
                println!("{}", serde_json::to_string_pretty(&summary)?);
            }

            // Exit with error if any requests failed
            if summary.failed > 0 && !continue_on_error {
                std::process::exit(1);
            }
        }

        CollectionSubcommand::Test {
            name,
            dir,
            spec: spec_path,
            auth_profile,
            output,
            continue_on_error,
        } => {
            let path = find_collection(&dir, &name)?;
            let collection = parse_collection(&path)?;

            // Load spec
            let spec_path = spec_path.unwrap_or_else(|| PathBuf::from("specs/api.yaml"));
            let spec_content = std::fs::read_to_string(&spec_path)?;
            let spec = parse_spec(&spec_content)?;

            // Build execution options
            let options = ExecutionOptions {
                continue_on_error,
                skip_requests: vec![],
                only_requests: None,
                auth_profile,
                variable_overrides: HashMap::new(),
                use_env: false,
                env_file: None,
                save_all: None,
                save_summary: None,
            };

            // TODO: Load auth profile
            let auth = None;

            // Create executor
            let executor = CollectionExecutor::new(spec, auth);

            // Run as tests
            let test_results = executor.execute_as_tests(&collection, options).await?;

            // Output results based on format
            match output.as_str() {
                "json" => {
                    println!("{}", serde_json::to_string_pretty(&test_results)?);
                }
                "junit" => {
                    let junit_xml = mrapids::collections::testing::to_junit_xml(&test_results);
                    println!("{}", junit_xml);
                }
                _ => {
                    // Pretty print test results
                    mrapids::collections::testing::print_test_results(&test_results);
                }
            }

            // Exit with error if tests failed
            if !test_results.all_passed {
                std::process::exit(1);
            }
        }
    }

    Ok(())
}
