#![warn(clippy::unwrap_used)]

mod cli;
mod core;
mod utils;

use anyhow::Result;
use clap::Parser;
use colored::*;
use std::env;
use std::process;

// Exit codes
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
    let result = run().await;
    
    let exit_code = match result {
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
            } else if e.to_string().contains("auth") || e.to_string().contains("authentication") {
                EXIT_AUTH_ERROR
            } else if e.to_string().contains("validation") || e.to_string().contains("invalid") {
                EXIT_VALIDATION_ERROR
            } else if e.to_string().contains("breaking") {
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
    
    let args = match cli::Args::try_parse() {
        Ok(args) => args,
        Err(e) => {
            eprintln!("{}", e);
            return Ok(EXIT_USAGE_ERROR);
        }
    };
    
    // Apply global options
    if args.global.no_color {
        colored::control::set_override(false);
    }
    
    if args.global.trace {
        env::set_var("RUST_LOG", "trace");
        env_logger::init();
    } else if args.global.verbose {
        env::set_var("RUST_LOG", "debug");
        env_logger::init();
    }
    
    match args.command {
        cli::Commands::Init(cmd) => {
            core::init_command(cmd, &args.global)?;
        }
        cli::Commands::Config(cmd) => {
            handle_config_command(cmd, &args.global)?;
        }
        cli::Commands::Cleanup(cmd) => {
            core::cleanup_command(cmd, &args.global)?;
        }
        cli::Commands::Validate(cmd) => {
            let result = core::validate_command(cmd, &args.global)?;
            if !result.is_valid {
                return Ok(EXIT_VALIDATION_ERROR);
            }
        }
        cli::Commands::Resolve(cmd) => {
            core::resolve_command(cmd, &args.global)?;
        }
        cli::Commands::Diff(cmd) => {
            let result = core::diff_command(cmd, &args.global)?;
            if result.has_breaking_changes {
                return Ok(EXIT_BREAKING_CHANGE);
            }
        }
        cli::Commands::List(cmd) => {
            core::list_command(cmd, &args.global)?;
        }
        cli::Commands::Show(cmd) => {
            core::show_command(cmd, &args.global)?;
        }
        cli::Commands::Search(cmd) => {
            core::search_command(cmd, &args.global)?;
        }
        cli::Commands::Run(cmd) => {
            if !args.global.quiet {
                core::display_short_banner();
            }
            core::run_command(cmd, &args.global)?;
        }
        cli::Commands::Test(cmd) => {
            if !args.global.quiet {
                println!("{}", "🧪 Running tests...".bright_cyan());
            }
            let result = core::test_command(cmd, &args.global)?;
            if !result.all_passed {
                return Ok(EXIT_VALIDATION_ERROR);
            }
        }
        cli::Commands::Tests(cmd) => {
            handle_tests_command(cmd, &args.global)?;
        }
        cli::Commands::Gen(cmd) => {
            handle_gen_command(cmd, &args.global)?;
        }
        cli::Commands::Auth(cmd) => {
            handle_auth_command(cmd, &args.global).await?;
        }
        cli::Commands::Help(cmd) => {
            handle_help_command(cmd)?;
        }
    }
    
    Ok(EXIT_SUCCESS)
}

fn handle_config_command(cmd: cli::ConfigCommand, global: &cli::GlobalOpts) -> Result<()> {
    use cli::ConfigAction;
    
    match cmd.action.unwrap_or(ConfigAction::List) {
        ConfigAction::Set { key, value, env } => {
            let env_name = env.or_else(|| global.env.clone()).unwrap_or_else(|| "default".to_string());
            core::config::set_value(&env_name, &key, &value)?;
            if !global.quiet {
                println!("✅ Set {} = {} in environment '{}'", key.bright_green(), value, env_name);
            }
        }
        ConfigAction::Get { key, env } => {
            let env_name = env.or_else(|| global.env.clone()).unwrap_or_else(|| "default".to_string());
            let value = core::config::get_value(&env_name, &key)?;
            if global.output == Some(cli::OutputFormat::Json) {
                println!("{}", serde_json::json!({ "key": key, "value": value, "env": env_name }));
            } else {
                println!("{}", value);
            }
        }
        ConfigAction::List => {
            let configs = core::config::list_all()?;
            core::output::display_configs(configs, global)?;
        }
        ConfigAction::Edit { env } => {
            let env_name = env.or_else(|| global.env.clone()).unwrap_or_else(|| "default".to_string());
            core::config::edit_interactive(&env_name)?;
        }
    }
    Ok(())
}

fn handle_tests_command(cmd: cli::TestsCommand, global: &cli::GlobalOpts) -> Result<()> {
    use cli::TestsAction;
    
    match cmd.action {
        TestsAction::Init { spec, framework, with_ci, output } => {
            let spec_path = spec.or_else(|| global.spec.as_ref().map(|s| s.into()));
            core::tests::init_test_suite(spec_path, framework, with_ci, output, global)?;
        }
    }
    Ok(())
}

fn handle_gen_command(cmd: cli::GenCommand, global: &cli::GlobalOpts) -> Result<()> {
    use cli::GenTarget;
    
    match cmd.target {
        GenTarget::Snippets { spec, op_id, format, output } => {
            let spec_path = spec.or_else(|| global.spec.as_ref().map(|s| s.into()));
            core::gen::generate_snippets(spec_path, op_id, format, output, global)?;
        }
        GenTarget::Sdk { spec, lang, package, with_docs, template } => {
            let spec_path = spec.or_else(|| global.spec.as_ref().map(|s| s.into()));
            core::gen::generate_sdk(spec_path, lang, package, with_docs, template, global)?;
        }
        GenTarget::Stubs { spec, framework, with_tests, output } => {
            let spec_path = spec.or_else(|| global.spec.as_ref().map(|s| s.into()));
            core::gen::generate_stubs(spec_path, framework, with_tests, output, global)?;
        }
        GenTarget::Fixtures { spec, schema, count, seed, format } => {
            let spec_path = spec.or_else(|| global.spec.as_ref().map(|s| s.into()));
            core::gen::generate_fixtures(spec_path, schema, count, seed, format, global)?;
        }
    }
    Ok(())
}

async fn handle_auth_command(cmd: cli::AuthCommand, global: &cli::GlobalOpts) -> Result<()> {
    use cli::AuthAction;
    use crate::core::auth::{oauth_login, list_profiles, delete_profile, test_auth_profile};
    
    match cmd.action {
        AuthAction::Login { provider, scopes, auth_url } => {
            let profile_name = global.profile.clone().unwrap_or_else(|| provider.clone());
            
            if crate::core::auth::token_store::profile_exists(&profile_name) {
                if !global.quiet {
                    println!("⚠️  Profile '{}' already exists. Use 'mrapids auth logout {}' first to remove it.", 
                        profile_name.bright_yellow(), profile_name);
                }
                return Ok(());
            }
            
            let config = if provider.to_lowercase() == "custom" && auth_url.is_some() {
                crate::core::auth::providers::create_custom_config_from_url(
                    &profile_name,
                    auth_url.unwrap(),
                    scopes.map(|s| s.split(',').map(|s| s.to_string()).collect()).unwrap_or_default(),
                )?
            } else {
                let mut config = crate::core::auth::providers::get_provider_config(&provider)?;
                if let Some(scope_str) = scopes {
                    config.scopes = scope_str.split(',').map(|s| s.to_string()).collect();
                }
                config
            };
            
            oauth_login(config, profile_name).await?;
        }
        
        AuthAction::Logout { provider, all, force } => {
            if all {
                let profiles = list_profiles()?;
                for profile in profiles {
                    if force || global.yes {
                        delete_profile(&profile.name)?;
                    } else {
                        println!("Remove auth profile '{}'? [y/N] ", profile.name.bright_yellow());
                        // ... prompt logic
                    }
                }
            } else if let Some(profile) = provider.or_else(|| global.profile.clone()) {
                if !force && !global.yes {
                    println!("Remove auth profile '{}'? [y/N] ", profile.bright_yellow());
                    // ... prompt logic
                } else {
                    delete_profile(&profile)?;
                }
            } else {
                anyhow::bail!("Specify a profile to logout or use --all");
            }
        }
        
        AuthAction::Status { provider, test } => {
            if let Some(profile) = provider.or_else(|| global.profile.clone()) {
                if test {
                    test_auth_profile(&profile).await?;
                } else {
                    let auth_profile = crate::core::auth::token_store::load_profile(&profile)?;
                    core::output::display_auth_status(&auth_profile, global)?;
                }
            } else {
                let profiles = list_profiles()?;
                core::output::display_auth_profiles(profiles, global)?;
            }
        }
    }
    
    Ok(())
}

fn handle_help_command(cmd: cli::HelpCommand) -> Result<()> {
    if let Some(command) = cmd.command {
        // Show help for specific command
        let _ = cli::Args::try_parse_from(&["mrapids", &command, "--help"]);
    } else {
        // Show general help
        let _ = cli::Args::try_parse_from(&["mrapids", "--help"]);
    }
    Ok(())
}