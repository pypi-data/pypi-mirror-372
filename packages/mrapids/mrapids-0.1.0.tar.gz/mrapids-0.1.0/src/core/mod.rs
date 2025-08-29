pub mod analyze_v2;
pub mod api;
pub mod auth;
pub mod banner;
mod config;
mod diagnostics;
mod errors;
mod examples;
mod explore;
mod external_refs;
pub mod fixtures;
mod flatten;
pub mod generate;
pub mod http;
mod init;
mod list;
pub mod parser;
pub mod policy;
mod request_runner;
mod run_v2;
mod runtime;
pub mod sdk_gen;
mod setup_tests;
mod show;
mod spec;
pub mod stubs;
mod swagger;
pub mod validation;
// pub mod secure_client; // TODO: Enable when security module is accessible

use crate::cli::{
    CleanupCommand, DiffCommand, ExploreCommand, FlattenCommand, InitCommand, InitConfigCommand,
    ListCommand, RunCommand, SetupTestsCommand, ShowCommand, TestCommand, ValidateCommand,
};
use anyhow::Result;
use colored::*;

pub fn init_command(cmd: InitCommand) -> Result<()> {
    init::init_project(cmd)
}

pub fn run_command(cmd: RunCommand) -> Result<()> {
    // Use the new simplified run implementation
    run_v2::execute(cmd)
}

pub fn test_command(cmd: TestCommand) -> Result<()> {
    use crate::utils::cleanup;
    use std::env;

    // Load the spec
    let spec = spec::load_openapi_spec(&cmd.spec)?;

    let test_result = if cmd.all {
        println!("Testing all operations...");
        let operations = spec::list_operations(&spec);
        let mut all_passed = true;

        for op_id in operations {
            println!("\n▶ Testing: {}", op_id.bright_yellow());
            match runtime::test_operation(&spec, &op_id, cmd.allow_insecure) {
                Ok(_) => println!("  ✅ {}", "PASSED".green()),
                Err(e) => {
                    println!("  ❌ {}: {}", "FAILED".red(), e);
                    all_passed = false;
                }
            }
        }

        if all_passed {
            Ok(())
        } else {
            Err(anyhow::anyhow!("Some tests failed"))
        }
    } else if let Some(op) = cmd.operation {
        println!("Testing operation: {}", op.yellow());
        runtime::test_operation(&spec, &op, cmd.allow_insecure)?;
        println!("✅ Test passed!");
        Ok(())
    } else {
        println!("{}", "Please specify --all or --operation".red());
        Ok(())
    };

    // Clean up test artifacts if enabled and not keeping them
    if cmd.cleanup && !cmd.keep_artifacts {
        println!("\n🧹 Cleaning up test artifacts...");
        let current_dir = env::current_dir()?;
        cleanup::cleanup_test_artifacts(&current_dir, true)?;
        cleanup::cleanup_empty_dirs(&current_dir)?;
        println!("✨ Cleanup complete!");
    } else if cmd.keep_artifacts {
        println!("\n📦 Test artifacts preserved for debugging");
    }

    test_result
}

pub fn setup_tests_command(cmd: SetupTestsCommand) -> Result<()> {
    setup_tests::setup_tests_command(cmd)
}

pub fn list_command(cmd: ListCommand) -> Result<()> {
    list::list_command(cmd)
}

pub fn cleanup_command(cmd: CleanupCommand) -> Result<()> {
    use crate::utils::cleanup;
    use colored::*;

    println!("{} Starting cleanup...", "🧹".bright_blue());

    if cmd.dry_run {
        println!(
            "{} Running in dry-run mode (no files will be deleted)",
            "ℹ️".yellow()
        );
    }

    // Clean test artifacts
    if cmd.test_artifacts {
        println!("\n{} Cleaning test artifacts...", "🗑️".cyan());
        if !cmd.dry_run {
            cleanup::cleanup_test_artifacts(&cmd.path, cmd.preserve_specs)?;
        } else {
            println!("  Would clean: test-*, tmp-*, temp-*, generated-*");
        }
    }

    // Clean backup directories
    if cmd.backups {
        println!("\n{} Cleaning backup directories...", "🗑️".cyan());
        if !cmd.dry_run {
            cleanup::cleanup_analyze_artifacts(&cmd.path, false)?;
        } else {
            println!("  Would clean: *.backup, *.old, *.prev");
        }
    }

    // Clean empty directories
    if cmd.empty_dirs {
        println!("\n{} Cleaning empty directories...", "🗑️".cyan());
        if !cmd.dry_run {
            cleanup::cleanup_empty_dirs(&cmd.path)?;
        } else {
            println!("  Would clean: all empty directories");
        }
    }

    if !cmd.dry_run {
        println!("\n{} Cleanup complete!", "✨".green());
    } else {
        println!(
            "\n{} Dry run complete. Use without --dry-run to actually clean.",
            "✅".green()
        );
    }

    Ok(())
}

pub fn init_config_command(cmd: InitConfigCommand) -> Result<()> {
    config::init_config(&cmd.env, cmd.api.as_deref(), cmd.output.as_deref())
}

pub fn show_command(cmd: ShowCommand) -> Result<()> {
    show::show_command(cmd)
}

pub fn explore_command(cmd: ExploreCommand) -> Result<()> {
    explore::explore_command(cmd)
}

pub async fn flatten_command(cmd: FlattenCommand) -> Result<()> {
    flatten::flatten_command(cmd).await
}

pub fn validate_command(cmd: ValidateCommand) -> Result<()> {
    // Use the new validation system
    use crate::core::validation::{SpecValidator, ValidationLevel};

    // Only print headers for text format
    if matches!(cmd.format, crate::cli::ValidateFormat::Text) {
        println!("🔍 {} OpenAPI Specification", "Validating".bright_cyan());
        println!("📄 Spec: {}", cmd.spec.display().to_string().cyan());
    }

    // Determine validation level from command
    let level = if cmd.lint {
        ValidationLevel::Full
    } else if cmd.strict {
        ValidationLevel::Standard
    } else {
        ValidationLevel::Quick
    };

    if matches!(cmd.format, crate::cli::ValidateFormat::Text) {
        let mode_desc = if cmd.lint {
            "(lint mode)"
        } else if cmd.strict {
            "(strict mode)"
        } else {
            ""
        };
        println!("📊 Level: {} {}", level.to_string().yellow(), mode_desc);
    }

    // Create validator
    let validator = SpecValidator::new()?;

    // Run validation
    let report = validator.validate_file(&cmd.spec, level)?;

    // Display report based on format
    match cmd.format {
        crate::cli::ValidateFormat::Text => {
            report.display();
        }
        crate::cli::ValidateFormat::Json => {
            // Output JSON format
            let json_output = serde_json::json!({
                "valid": report.is_valid(),
                "version": report.spec_version.to_string(),
                "errors": report.errors().iter().map(|e| {
                    serde_json::json!({
                        "code": e.code,
                        "message": e.message,
                        "path": e.path,
                        "severity": e.severity.to_string()
                    })
                }).collect::<Vec<_>>(),
                "warnings": report.warnings().iter().map(|w| {
                    serde_json::json!({
                        "code": w.code,
                        "message": w.message,
                        "path": w.path,
                        "severity": w.severity.to_string()
                    })
                }).collect::<Vec<_>>(),
                "duration_ms": report.duration.as_millis()
            });
            println!("{}", serde_json::to_string_pretty(&json_output)?);
        }
    }

    // Return error if validation failed (or warnings in strict mode)
    if !report.is_valid() || (cmd.strict && report.has_warnings()) {
        if matches!(cmd.format, crate::cli::ValidateFormat::Text) {
            return Err(anyhow::anyhow!(
                "Validation failed with {} errors, {} warnings",
                report.error_count(),
                report.warning_count()
            ));
        } else {
            // For JSON format, exit with code 1 but don't print error
            std::process::exit(1);
        }
    }

    Ok(())
}

pub fn diff_command(cmd: DiffCommand) -> Result<()> {
    // TODO: Implement spec diffing
    println!("🔍 {} Diff", "MicroRapid".bright_cyan());
    println!("📄 Old spec: {}", cmd.old_spec.display());
    println!("📄 New spec: {}", cmd.new_spec.display());
    if cmd.breaking_only {
        println!("⚠️  Breaking changes only");
    }
    println!("⚠️  Spec diffing is not yet implemented");
    Ok(())
}

// Re-export banner functions
pub use banner::{display_banner, display_short_banner, get_version_info};
