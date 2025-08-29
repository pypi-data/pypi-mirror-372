use crate::core::parser::UnifiedSpec;
use anyhow::Result;
use colored::*;
use std::fs;
use std::path::Path;

mod express;
mod fastapi;
mod gin;

pub fn generate_server_stubs(
    spec: &UnifiedSpec,
    framework: &str,
    output_dir: &Path,
    with_tests: bool,
    with_validation: bool,
) -> Result<()> {
    println!("🏗️ {} Server Stubs Generation", "MicroRapid".bright_cyan());
    println!("📋 Framework: {}", framework.bright_yellow());
    println!("📁 Output: {}", output_dir.display());

    // Create output directory
    fs::create_dir_all(output_dir)?;

    // Generate based on framework
    match framework {
        "express" => express::generate(spec, output_dir, with_tests, with_validation)?,
        "fastapi" => fastapi::generate(spec, output_dir, with_tests, with_validation)?,
        "gin" => gin::generate(spec, output_dir, with_tests, with_validation)?,
        _ => {
            return Err(anyhow::anyhow!(
                "Unsupported framework: {}. Supported: express, fastapi, gin",
                framework
            ));
        }
    }

    println!(
        "✅ {} server stubs generated successfully!",
        framework.bright_green()
    );
    Ok(())
}
