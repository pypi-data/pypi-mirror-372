//! Reporters for collection execution output

use super::executor::ApiResponse;
use super::models::{CollectionRequest, CollectionSummary, RequestResult};
use colored::*;
use indicatif::{ProgressBar, ProgressStyle};
use std::time::Instant;

/// Trait for reporting collection execution progress
pub trait Reporter {
    /// Called when collection execution starts
    fn on_start(&mut self, collection_name: &str, total_requests: usize);

    /// Called before executing a request
    fn on_request_start(&mut self, request: &CollectionRequest);

    /// Called after a request completes successfully
    fn on_request_complete(
        &mut self,
        request: &CollectionRequest,
        response: &ApiResponse,
        duration_ms: u64,
    );

    /// Called when a request fails
    fn on_request_error(&mut self, request: &CollectionRequest, error: &anyhow::Error);

    /// Called when a request is skipped
    fn on_request_skipped(&mut self, request: &CollectionRequest, reason: &str);

    /// Called when collection execution completes
    fn on_complete(&mut self, summary: &CollectionSummary);
}

/// Console reporter that prints to stdout
pub struct ConsoleReporter {
    progress_bar: Option<ProgressBar>,
    start_time: Instant,
    verbose: bool,
}

impl ConsoleReporter {
    pub fn new(verbose: bool) -> Self {
        Self {
            progress_bar: None,
            start_time: Instant::now(),
            verbose,
        }
    }
}

impl Reporter for ConsoleReporter {
    fn on_start(&mut self, collection_name: &str, total_requests: usize) {
        self.start_time = Instant::now();

        println!(
            "{} Collection: {}",
            "▶".cyan().bold(),
            collection_name.bold()
        );
        println!("  {} requests to execute\n", total_requests);

        let pb = ProgressBar::new(total_requests as u64);
        pb.set_style(
            ProgressStyle::default_bar()
                .template("{prefix:.bold.dim} {bar:40.cyan/blue} {pos}/{len} {msg}")
                .unwrap()
                .progress_chars("=>-"),
        );
        pb.set_prefix("Progress");
        self.progress_bar = Some(pb);
    }

    fn on_request_start(&mut self, request: &CollectionRequest) {
        if let Some(pb) = &self.progress_bar {
            pb.set_message(format!("Running: {}", request.name));
        }
    }

    fn on_request_complete(
        &mut self,
        request: &CollectionRequest,
        response: &ApiResponse,
        duration_ms: u64,
    ) {
        if let Some(pb) = &self.progress_bar {
            pb.inc(1);
        }

        let status_str = format!("{}", response.status_code);
        let status_colored = match response.status_code {
            200..=299 => status_str.green(),
            300..=399 => status_str.yellow(),
            400..=499 => status_str.red(),
            500..=599 => status_str.red().bold(),
            _ => status_str.normal(),
        };

        println!(
            "  {} {} {} {} ({}ms)",
            "✓".green().bold(),
            request.name.bold(),
            "→".dimmed(),
            status_colored,
            duration_ms
        );

        if self.verbose {
            if let Some(body) = &response.body {
                println!(
                    "    Response: {}",
                    serde_json::to_string_pretty(body)
                        .unwrap_or_else(|_| "Invalid JSON".to_string())
                );
            }
        }
    }

    fn on_request_error(&mut self, request: &CollectionRequest, error: &anyhow::Error) {
        if let Some(pb) = &self.progress_bar {
            pb.inc(1);
        }

        println!(
            "  {} {} {} {}",
            "✗".red().bold(),
            request.name.bold(),
            "→".dimmed(),
            error.to_string().red()
        );
    }

    fn on_request_skipped(&mut self, request: &CollectionRequest, reason: &str) {
        if let Some(pb) = &self.progress_bar {
            pb.inc(1);
        }

        println!(
            "  {} {} {} {}",
            "⊘".yellow().bold(),
            request.name.bold(),
            "→".dimmed(),
            reason.yellow()
        );
    }

    fn on_complete(&mut self, summary: &CollectionSummary) {
        if let Some(pb) = &self.progress_bar {
            pb.finish_and_clear();
        }

        let elapsed = self.start_time.elapsed();
        println!("\n{}", "─".repeat(50));

        println!("{} Summary:", "📊".cyan());
        println!("  Total:      {} requests", summary.total_requests);
        println!(
            "  Successful: {} {}",
            summary.successful,
            if summary.successful > 0 {
                "✓".green()
            } else {
                "".normal()
            }
        );

        if summary.failed > 0 {
            println!("  Failed:     {} {}", summary.failed, "✗".red());
        }

        if summary.skipped > 0 {
            println!("  Skipped:    {} {}", summary.skipped, "⊘".yellow());
        }

        println!("  Duration:   {:.2}s", elapsed.as_secs_f64());

        // Test summary if present
        if let Some(test_summary) = &summary.test_summary {
            println!("\n{} Test Results:", "🧪");
            println!(
                "  Tests: {}, Passed: {}, Failed: {}",
                test_summary.total_tests, test_summary.passed, test_summary.failed
            );

            if test_summary.all_passed {
                println!("\n  {} All tests passed!", "✨".green().bold());
            } else {
                println!("\n  {} Some tests failed", "❌".red().bold());
            }
        }
    }
}

/// JSON reporter that collects results silently
pub struct JsonReporter {
    results: Vec<RequestResult>,
    start_time: Instant,
}

impl JsonReporter {
    pub fn new() -> Self {
        Self {
            results: Vec::new(),
            start_time: Instant::now(),
        }
    }

    pub fn get_results(self) -> Vec<RequestResult> {
        self.results
    }
}

impl Reporter for JsonReporter {
    fn on_start(&mut self, _collection_name: &str, _total_requests: usize) {
        self.start_time = Instant::now();
        self.results.clear();
    }

    fn on_request_start(&mut self, _request: &CollectionRequest) {
        // Silent
    }

    fn on_request_complete(
        &mut self,
        request: &CollectionRequest,
        response: &ApiResponse,
        duration_ms: u64,
    ) {
        self.results.push(RequestResult {
            name: request.name.clone(),
            operation: request.operation.clone(),
            status: response.status_code,
            body: response.body.clone(),
            headers: response
                .headers
                .iter()
                .map(|(k, v)| (k.to_string(), v.to_str().unwrap_or("").to_string()))
                .collect(),
            duration_ms,
            error: None,
            test_result: None,
        });
    }

    fn on_request_error(&mut self, request: &CollectionRequest, error: &anyhow::Error) {
        self.results.push(RequestResult {
            name: request.name.clone(),
            operation: request.operation.clone(),
            status: 0,
            body: None,
            headers: Default::default(),
            duration_ms: 0,
            error: Some(error.to_string()),
            test_result: None,
        });
    }

    fn on_request_skipped(&mut self, request: &CollectionRequest, reason: &str) {
        self.results.push(RequestResult {
            name: request.name.clone(),
            operation: request.operation.clone(),
            status: 0,
            body: None,
            headers: Default::default(),
            duration_ms: 0,
            error: Some(format!("Skipped: {}", reason)),
            test_result: None,
        });
    }

    fn on_complete(&mut self, _summary: &CollectionSummary) {
        // Silent
    }
}
