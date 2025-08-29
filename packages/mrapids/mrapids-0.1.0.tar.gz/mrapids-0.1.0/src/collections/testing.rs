//! Testing support for collections - assertions, test results, and reporting

use super::models::{CollectionRequest, RequestResult};
use colored::*;
use serde::{Deserialize, Serialize};
use serde_json::Value;

/// Results from running a collection as tests
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestResults {
    /// Collection name
    pub name: String,

    /// Total number of tests
    pub total_tests: usize,

    /// Number of passed tests
    pub passed: usize,

    /// Number of failed tests  
    pub failed: usize,

    /// Number of skipped tests
    pub skipped: usize,

    /// Whether all tests passed
    pub all_passed: bool,

    /// Individual test results
    pub test_results: Vec<TestResult>,

    /// Total execution time in milliseconds
    pub total_duration_ms: u64,
}

/// Result of a single test
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestResult {
    /// Test name (request name)
    pub name: String,

    /// Operation that was tested
    pub operation: String,

    /// Whether the test passed
    pub passed: bool,

    /// Test status (passed, failed, skipped)
    pub status: TestStatus,

    /// Execution time in milliseconds
    pub duration_ms: u64,

    /// Assertion results
    pub assertions: Vec<AssertionResult>,

    /// Error message if request failed
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

/// Test execution status
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum TestStatus {
    Passed,
    Failed,
    Skipped,
}

/// Result of a single assertion
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AssertionResult {
    /// Type of assertion
    pub assertion_type: AssertionType,

    /// Whether the assertion passed
    pub passed: bool,

    /// Expected value
    pub expected: Value,

    /// Actual value
    pub actual: Value,

    /// Human-readable message
    pub message: String,

    /// Path to the value being tested (e.g., "body.data.id")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub path: Option<String>,
}

/// Types of assertions
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum AssertionType {
    Status,
    Body,
    Header,
}

/// Evaluate expectations against a response
pub fn evaluate_expectations(
    request: &CollectionRequest,
    result: &RequestResult,
) -> Vec<AssertionResult> {
    let mut assertions = Vec::new();

    if let Some(expect) = &request.expect {
        // Status assertion
        if let Some(expected_status) = expect.status {
            assertions.push(AssertionResult {
                assertion_type: AssertionType::Status,
                passed: result.status == expected_status,
                expected: Value::Number(expected_status.into()),
                actual: Value::Number(result.status.into()),
                message: if result.status == expected_status {
                    format!("Status code is {}", expected_status)
                } else {
                    format!("Expected status {}, got {}", expected_status, result.status)
                },
                path: None,
            });
        }

        // Body assertions
        if let Some(expected_body) = &expect.body {
            if let Some(actual_body) = &result.body {
                let matches = check_body_match(expected_body, actual_body);
                assertions.push(AssertionResult {
                    assertion_type: AssertionType::Body,
                    passed: matches,
                    expected: expected_body.clone(),
                    actual: actual_body.clone(),
                    message: if matches {
                        "Response body matches expected".to_string()
                    } else {
                        "Response body does not match expected".to_string()
                    },
                    path: Some("body".to_string()),
                });
            } else {
                assertions.push(AssertionResult {
                    assertion_type: AssertionType::Body,
                    passed: false,
                    expected: expected_body.clone(),
                    actual: Value::Null,
                    message: "Response has no body".to_string(),
                    path: Some("body".to_string()),
                });
            }
        }

        // Header assertions
        if let Some(expected_headers) = &expect.headers {
            for (header_name, expected_value) in expected_headers {
                let actual_value = result
                    .headers
                    .get(header_name)
                    .map(|v| Value::String(v.clone()))
                    .unwrap_or(Value::Null);

                let matches = result
                    .headers
                    .get(header_name)
                    .map(|v| v == expected_value)
                    .unwrap_or(false);

                assertions.push(AssertionResult {
                    assertion_type: AssertionType::Header,
                    passed: matches,
                    expected: Value::String(expected_value.clone()),
                    actual: actual_value,
                    message: if matches {
                        format!("Header '{}' matches", header_name)
                    } else {
                        format!("Header '{}' mismatch", header_name)
                    },
                    path: Some(format!("headers.{}", header_name)),
                });
            }
        }
    }

    assertions
}

/// Check if actual body matches expected (partial match)
fn check_body_match(expected: &Value, actual: &Value) -> bool {
    match (expected, actual) {
        (Value::Object(exp_map), Value::Object(act_map)) => {
            // For objects, check that all expected keys exist and match
            exp_map.iter().all(|(key, exp_val)| {
                act_map
                    .get(key)
                    .map(|act_val| check_body_match(exp_val, act_val))
                    .unwrap_or(false)
            })
        }
        (Value::Array(exp_arr), Value::Array(act_arr)) => {
            // For arrays, check length and each element
            exp_arr.len() == act_arr.len()
                && exp_arr
                    .iter()
                    .zip(act_arr.iter())
                    .all(|(exp, act)| check_body_match(exp, act))
        }
        // For primitives, exact match
        _ => expected == actual,
    }
}

/// Convert test results to JUnit XML format
pub fn to_junit_xml(results: &TestResults) -> String {
    let mut xml = String::new();
    xml.push_str("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
    xml.push_str(&format!(
        "<testsuites name=\"{}\" tests=\"{}\" failures=\"{}\" time=\"{}\">\n",
        results.name,
        results.total_tests,
        results.failed,
        results.total_duration_ms as f64 / 1000.0
    ));

    xml.push_str(&format!(
        "  <testsuite name=\"{}\" tests=\"{}\" failures=\"{}\" skipped=\"{}\" time=\"{}\">\n",
        results.name,
        results.total_tests,
        results.failed,
        results.skipped,
        results.total_duration_ms as f64 / 1000.0
    ));

    for test in &results.test_results {
        let time_sec = test.duration_ms as f64 / 1000.0;

        match test.status {
            TestStatus::Passed => {
                xml.push_str(&format!(
                    "    <testcase name=\"{}\" classname=\"{}\" time=\"{}\" />\n",
                    test.name, test.operation, time_sec
                ));
            }
            TestStatus::Failed => {
                xml.push_str(&format!(
                    "    <testcase name=\"{}\" classname=\"{}\" time=\"{}\">\n",
                    test.name, test.operation, time_sec
                ));

                let failure_msg = test
                    .assertions
                    .iter()
                    .filter(|a| !a.passed)
                    .map(|a| a.message.as_str())
                    .collect::<Vec<_>>()
                    .join("; ");

                xml.push_str(&format!(
                    "      <failure message=\"{}\" type=\"assertion\">{}</failure>\n",
                    escape_xml(&failure_msg),
                    escape_xml(&failure_msg)
                ));
                xml.push_str("    </testcase>\n");
            }
            TestStatus::Skipped => {
                xml.push_str(&format!(
                    "    <testcase name=\"{}\" classname=\"{}\" time=\"{}\">\n",
                    test.name, test.operation, time_sec
                ));
                xml.push_str("      <skipped />\n");
                xml.push_str("    </testcase>\n");
            }
        }
    }

    xml.push_str("  </testsuite>\n");
    xml.push_str("</testsuites>\n");

    xml
}

/// Pretty print test results to console
pub fn print_test_results(results: &TestResults) {
    println!("\n{} Test Results: {}", "🧪".cyan(), results.name.bold());
    println!("{}", "─".repeat(50));

    for test in &results.test_results {
        let icon = match test.status {
            TestStatus::Passed => "✓".green(),
            TestStatus::Failed => "✗".red(),
            TestStatus::Skipped => "⊘".yellow(),
        };

        let status_str = match test.status {
            TestStatus::Passed => "PASSED".green(),
            TestStatus::Failed => "FAILED".red(),
            TestStatus::Skipped => "SKIPPED".yellow(),
        };

        println!(
            "{} {} {} ({}ms)",
            icon,
            test.name.bold(),
            status_str,
            test.duration_ms
        );

        // Show failed assertions
        if test.status == TestStatus::Failed {
            for assertion in &test.assertions {
                if !assertion.passed {
                    println!(
                        "    {} {} assertion: {}",
                        "└".dimmed(),
                        format!("{:?}", assertion.assertion_type).red(),
                        assertion.message.dimmed()
                    );
                    if assertion.expected != assertion.actual {
                        println!(
                            "      {} Expected: {}",
                            "├".dimmed(),
                            serde_json::to_string(&assertion.expected)
                                .unwrap_or_default()
                                .green()
                        );
                        println!(
                            "      {} Actual: {}",
                            "└".dimmed(),
                            serde_json::to_string(&assertion.actual)
                                .unwrap_or_default()
                                .red()
                        );
                    }
                }
            }
        }

        // Show error if any
        if let Some(error) = &test.error {
            println!("    {} Error: {}", "└".dimmed(), error.red());
        }
    }

    println!("\n{}", "─".repeat(50));
    println!(
        "Tests: {}, Passed: {}, Failed: {}, Skipped: {}",
        results.total_tests.to_string().bold(),
        results.passed.to_string().green(),
        results.failed.to_string().red(),
        results.skipped.to_string().yellow()
    );

    let duration_sec = results.total_duration_ms as f64 / 1000.0;
    println!("Duration: {:.2}s", duration_sec);

    if results.all_passed {
        println!("\n{} All tests passed!", "✨".green().bold());
    } else {
        println!("\n{} Some tests failed", "❌".red().bold());
    }
}

/// Escape XML special characters
fn escape_xml(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&apos;")
}
