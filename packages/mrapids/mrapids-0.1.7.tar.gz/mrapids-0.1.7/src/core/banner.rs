use colored::*;

/// Get the Micro Rapid ASCII art banner
fn get_banner() -> String {
    let banner = r#"
      ╭──────────────────────────────────────────╮
      │   ○ ○     M I C R O   R A P I D     ○ ○  │
      │    ╲ ╱                               ╲ ╱   │
      │     ═       🤖 agent automation 🤖    ═    │
      │    ╱ ╲        your api, automated    ╱ ╲   │
      │   ○ ○                               ○ ○  │
      ╰──────────────────────────────────────────╯
      
         >> mrapids.exe --mode agent
         >> status: [READY] ████████████ 100%"#;

    banner.bright_cyan().to_string()
}

/// Display the full banner when no command is provided
pub fn display_banner() {
    println!("{}", get_banner());
    println!("{}\n", "Your OpenAPI, but executable".bright_yellow());

    println!("{}", "Quick Start:".bright_white().underline());
    println!(
        "  {} init api-spec.yaml     {}",
        "mrapids".bright_green(),
        "# Initialize from OpenAPI spec".bright_black()
    );
    println!(
        "  {} validate spec.yaml     {}",
        "mrapids".bright_green(),
        "# Validate specification".bright_black()
    );
    println!(
        "  {} gen sdk -s spec.yaml  {}",
        "mrapids".bright_green(),
        "# Generate SDK".bright_black()
    );
    println!(
        "  {} run GetUser           {}",
        "mrapids".bright_green(),
        "# Execute API operation".bright_black()
    );
    println!();
    println!("{}", "For more information:".bright_white());
    println!(
        "  {} help                  {}",
        "mrapids".bright_green(),
        "# Show all commands".bright_black()
    );
    println!(
        "  {} <command> --help      {}",
        "mrapids".bright_green(),
        "# Show command details".bright_black()
    );
    println!();
    println!("  Website: {}", "https://microrapid.io/".bright_cyan());
}

/// Display a short banner for command execution
pub fn display_short_banner() {
    println!(
        "{} {} v{}",
        "⚡".bright_yellow(),
        "Micro Rapid".bright_cyan().bold(),
        env!("CARGO_PKG_VERSION").bright_black()
    );
}

/// Get the help header for CLI help text
pub fn get_help_header() -> &'static str {
    "\n      ╭──────────────────────────────────────────╮\n      │   ○ ○     M I C R O   R A P I D     ○ ○  │\n      │    ╲ ╱                               ╲ ╱   │\n      │     ═       🤖 agent automation 🤖    ═    │\n      │    ╱ ╲        your api, automated    ╱ ╲   │\n      │   ○ ○                               ○ ○  │\n      ╰──────────────────────────────────────────╯\n      \n         >> mrapids.exe --mode agent\n         >> status: [READY] ████████████ 100%\n\nYour OpenAPI, but executable\n\nThe blazing fast API automation toolkit"
}

/// Get version information formatted nicely
pub fn get_version_info() -> String {
    format!(
        "{}\n{} {}\n{}\n{}\n",
        get_banner(),
        "Version:".bright_white(),
        env!("CARGO_PKG_VERSION").bright_green(),
        "Build: release".white(),
        format!("Homepage: {}", "https://microrapid.io/").bright_blue()
    )
}
