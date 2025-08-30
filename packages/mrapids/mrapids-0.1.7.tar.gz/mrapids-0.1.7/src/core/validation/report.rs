/// Validation report that aggregates results from multiple validators
use super::types::{ValidationError, ValidationResult};
use super::version::SpecVersion;
use colored::*;
use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Complete validation report
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ValidationReport {
    /// Detected spec version
    pub spec_version: SpecVersion,

    /// Validation results
    #[serde(flatten)]
    pub results: ValidationResult,

    /// Time taken to validate
    pub duration: Duration,

    /// Validation levels that were run
    pub levels_checked: Vec<String>,
}

impl ValidationReport {
    pub fn new(spec_version: SpecVersion) -> Self {
        Self {
            spec_version,
            results: ValidationResult::new(),
            duration: Duration::from_secs(0),
            levels_checked: Vec::new(),
        }
    }

    /// Check if the spec is valid (no errors)
    pub fn is_valid(&self) -> bool {
        self.results.is_valid()
    }

    /// Check if there are any warnings
    pub fn has_warnings(&self) -> bool {
        self.results.has_warnings()
    }

    /// Get error count
    pub fn error_count(&self) -> usize {
        self.results.error_count()
    }

    /// Get warning count
    pub fn warning_count(&self) -> usize {
        self.results.warning_count()
    }

    /// Get all errors
    pub fn errors(&self) -> &[ValidationError] {
        &self.results.errors
    }

    /// Get all warnings
    pub fn warnings(&self) -> &[ValidationError] {
        &self.results.warnings
    }

    /// Merge another validation result into this report
    pub fn merge_results(&mut self, results: ValidationResult) {
        self.results.merge(results);
    }

    /// Display the report with colors
    pub fn display(&self) {
        println!("🔍 {} Validation Report", "OpenAPI".bright_cyan());
        println!(
            "📋 Version: {}",
            self.spec_version.to_string().bright_blue()
        );
        println!("⏱️  Duration: {}ms", self.duration.as_millis());
        println!("📊 Levels checked: {}", self.levels_checked.join(", "));
        println!();

        if self.is_valid() && !self.has_warnings() {
            println!("{} Specification is valid!", "✅".green());
            return;
        }

        // Display errors
        if !self.results.errors.is_empty() {
            println!("{} {} found:", "❌".red(), "Errors".red());
            for error in &self.results.errors {
                println!("  {} {}", "•".red(), error.message);
                if let Some(path) = &error.path {
                    println!("    {} {}", "at".dimmed(), path.dimmed());
                }
                if let Some(line) = error.line {
                    println!(
                        "    {} line {}, column {}",
                        "at".dimmed(),
                        line.to_string().dimmed(),
                        error.column.unwrap_or(0).to_string().dimmed()
                    );
                }
            }
            println!();
        }

        // Display warnings
        if !self.results.warnings.is_empty() {
            println!("{} {} found:", "⚠️".yellow(), "Warnings".yellow());
            for warning in &self.results.warnings {
                println!("  {} {}", "•".yellow(), warning.message);
                if let Some(path) = &warning.path {
                    println!("    {} {}", "at".dimmed(), path.dimmed());
                }
            }
            println!();
        }

        // Display info
        if !self.results.info.is_empty() {
            println!("{} {} found:", "ℹ️".blue(), "Information".blue());
            for info in &self.results.info {
                println!("  {} {}", "•".blue(), info.message);
                if let Some(path) = &info.path {
                    println!("    {} {}", "at".dimmed(), path.dimmed());
                }
            }
            println!();
        }

        // Summary
        let error_text = if self.error_count() == 1 {
            "error"
        } else {
            "errors"
        };
        let warning_text = if self.warning_count() == 1 {
            "warning"
        } else {
            "warnings"
        };

        println!(
            "📈 Summary: {} {}, {} {}",
            self.error_count().to_string().red(),
            error_text,
            self.warning_count().to_string().yellow(),
            warning_text
        );
    }
}
