use colored::*;
use regex::Regex;
use std::sync::LazyLock;

// Common SQL injection patterns
static SQL_PATTERNS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)(union\s+select|drop\s+table|delete\s+from|insert\s+into|update\s+set|;\s*--|'\s*or\s*'|1=1|exec\s*\(|xp_cmdshell)").unwrap()
});

// Command injection patterns
static COMMAND_PATTERNS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[;&|`$\n]|\$\(|\)").unwrap());

// CRLF injection pattern
static CRLF_PATTERN: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[\r\n]").unwrap());

// NoSQL injection patterns
static NOSQL_PATTERNS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(?i)(\$where|\$ne|\$gt|\$lt|\$regex|\$exists|\.\./)").unwrap());

// XSS patterns
static XSS_PATTERNS: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)(<script|javascript:|onerror=|onload=|<iframe|<object|<embed)").unwrap()
});

// Path traversal patterns
static PATH_TRAVERSAL_PATTERNS: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"(\.\.[\\/]|\.\.%2[fF]|\.\.%5[cC])").unwrap());

#[derive(Debug, Clone)]
pub struct RequestWarning {
    pub severity: WarningSeverity,
    #[allow(dead_code)]
    pub category: WarningCategory,
    pub message: String,
    pub location: String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum WarningSeverity {
    High,
    Medium,
    Low,
}

#[derive(Debug, Clone, PartialEq)]
pub enum WarningCategory {
    SqlInjection,
    CommandInjection,
    CrlfInjection,
    NoSqlInjection,
    XssAttempt,
    PathTraversal,
    SuspiciousPattern,
}

pub struct RequestAnalyzer {
    warnings: Vec<RequestWarning>,
    no_warnings: bool,
}

impl RequestAnalyzer {
    pub fn new(no_warnings: bool) -> Self {
        Self {
            warnings: Vec::new(),
            no_warnings,
        }
    }

    pub fn analyze_headers(&mut self, headers: &[(String, String)]) {
        if self.no_warnings {
            return;
        }

        for (name, value) in headers {
            // Check for CRLF injection
            if CRLF_PATTERN.is_match(name) || CRLF_PATTERN.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::High,
                    category: WarningCategory::CrlfInjection,
                    message: format!(
                        "Header contains CRLF characters which could lead to header injection"
                    ),
                    location: format!("Header: {}", name),
                });
            }

            // Check for suspicious patterns in header values
            if SQL_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::Medium,
                    category: WarningCategory::SqlInjection,
                    message: format!("Header value contains SQL-like syntax"),
                    location: format!("Header: {}", name),
                });
            }

            if COMMAND_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::Medium,
                    category: WarningCategory::CommandInjection,
                    message: format!("Header value contains shell metacharacters"),
                    location: format!("Header: {}", name),
                });
            }
        }
    }

    pub fn analyze_url_params(&mut self, params: &[(String, String)]) {
        if self.no_warnings {
            return;
        }

        for (key, value) in params {
            // Check for SQL injection
            if SQL_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::High,
                    category: WarningCategory::SqlInjection,
                    message: format!("Parameter contains SQL injection patterns"),
                    location: format!("Parameter: {}", key),
                });
            }

            // Check for NoSQL injection
            if NOSQL_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::High,
                    category: WarningCategory::NoSqlInjection,
                    message: format!("Parameter contains NoSQL injection patterns"),
                    location: format!("Parameter: {}", key),
                });
            }

            // Check for command injection
            if COMMAND_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::Medium,
                    category: WarningCategory::CommandInjection,
                    message: format!("Parameter contains shell metacharacters"),
                    location: format!("Parameter: {}", key),
                });
            }

            // Check for XSS
            if XSS_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::Medium,
                    category: WarningCategory::XssAttempt,
                    message: format!("Parameter contains potential XSS patterns"),
                    location: format!("Parameter: {}", key),
                });
            }

            // Check for path traversal
            if PATH_TRAVERSAL_PATTERNS.is_match(value) {
                self.warnings.push(RequestWarning {
                    severity: WarningSeverity::High,
                    category: WarningCategory::PathTraversal,
                    message: format!("Parameter contains path traversal patterns"),
                    location: format!("Parameter: {}", key),
                });
            }
        }
    }

    pub fn analyze_json_body(&mut self, body: &str) {
        if self.no_warnings {
            return;
        }

        // Check for injection patterns in JSON values
        if SQL_PATTERNS.is_match(body) {
            self.warnings.push(RequestWarning {
                severity: WarningSeverity::Medium,
                category: WarningCategory::SqlInjection,
                message: format!("Request body contains SQL-like patterns"),
                location: "JSON body".to_string(),
            });
        }

        if NOSQL_PATTERNS.is_match(body) {
            self.warnings.push(RequestWarning {
                severity: WarningSeverity::Medium,
                category: WarningCategory::NoSqlInjection,
                message: format!("Request body contains NoSQL query operators"),
                location: "JSON body".to_string(),
            });
        }

        if XSS_PATTERNS.is_match(body) {
            self.warnings.push(RequestWarning {
                severity: WarningSeverity::Low,
                category: WarningCategory::XssAttempt,
                message: format!("Request body contains HTML/JavaScript patterns"),
                location: "JSON body".to_string(),
            });
        }

        // Check for excessively large numbers that could cause issues
        if body.contains("999999999999999999999999999999") {
            self.warnings.push(RequestWarning {
                severity: WarningSeverity::Low,
                category: WarningCategory::SuspiciousPattern,
                message: format!("Request body contains very large numbers"),
                location: "JSON body".to_string(),
            });
        }
    }

    #[allow(dead_code)]
    pub fn analyze_file_path(&mut self, path: &str) {
        if self.no_warnings {
            return;
        }

        if PATH_TRAVERSAL_PATTERNS.is_match(path) {
            self.warnings.push(RequestWarning {
                severity: WarningSeverity::High,
                category: WarningCategory::PathTraversal,
                message: format!("File path contains directory traversal patterns"),
                location: format!("File: {}", path),
            });
        }
    }

    #[cfg(test)]
    pub fn get_warnings(&self) -> &[RequestWarning] {
        &self.warnings
    }

    #[allow(dead_code)]
    pub fn has_warnings(&self) -> bool {
        !self.warnings.is_empty()
    }

    pub fn display_warnings(&self) {
        if self.no_warnings || self.warnings.is_empty() {
            return;
        }

        // Group warnings by severity
        let mut high_warnings = Vec::new();
        let mut medium_warnings = Vec::new();
        let mut low_warnings = Vec::new();

        for warning in &self.warnings {
            match warning.severity {
                WarningSeverity::High => high_warnings.push(warning),
                WarningSeverity::Medium => medium_warnings.push(warning),
                WarningSeverity::Low => low_warnings.push(warning),
            }
        }

        if !high_warnings.is_empty() || !medium_warnings.is_empty() || !low_warnings.is_empty() {
            eprintln!("\n{}", "━".repeat(60).yellow());
            eprintln!(
                "{} {} {}",
                "⚠️".yellow().bold(),
                "REQUEST SECURITY WARNINGS".yellow().bold(),
                "⚠️".yellow().bold()
            );
            eprintln!("{}", "━".repeat(60).yellow());

            // Display high severity warnings
            if !high_warnings.is_empty() {
                eprintln!("\n{}", "HIGH SEVERITY:".red().bold());
                for warning in high_warnings {
                    eprintln!(
                        "  {} {} - {}",
                        "●".red(),
                        warning.location.red(),
                        warning.message
                    );
                }
            }

            // Display medium severity warnings
            if !medium_warnings.is_empty() {
                eprintln!("\n{}", "MEDIUM SEVERITY:".yellow().bold());
                for warning in medium_warnings {
                    eprintln!(
                        "  {} {} - {}",
                        "●".yellow(),
                        warning.location.yellow(),
                        warning.message
                    );
                }
            }

            // Display low severity warnings
            if !low_warnings.is_empty() {
                eprintln!("\n{}", "LOW SEVERITY:".blue().bold());
                for warning in low_warnings {
                    eprintln!(
                        "  {} {} - {}",
                        "●".blue(),
                        warning.location.blue(),
                        warning.message
                    );
                }
            }

            eprintln!(
                "\n{}",
                "These warnings are informational. Your request will still be sent.".italic()
            );
            eprintln!(
                "{}",
                "Use --no-warnings to suppress these messages.".italic()
            );
            eprintln!("{}", "━".repeat(60).yellow());
            eprintln!();
        }
    }
}

// Helper function to sanitize values for safe display
#[allow(dead_code)]
pub fn sanitize_for_display(value: &str, max_length: usize) -> String {
    let sanitized = value
        .replace('\r', "\\r")
        .replace('\n', "\\n")
        .replace('\t', "\\t");

    if sanitized.len() > max_length {
        format!("{}...", &sanitized[..max_length])
    } else {
        sanitized
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sql_injection_detection() {
        let mut analyzer = RequestAnalyzer::new(false);

        analyzer.analyze_url_params(&[
            ("id".to_string(), "1; DROP TABLE users;--".to_string()),
            ("name".to_string(), "admin' OR '1'='1".to_string()),
        ]);

        // Count only SQL injection warnings (command injection may also trigger)
        let sql_warnings: Vec<_> = analyzer
            .get_warnings()
            .iter()
            .filter(|w| w.category == WarningCategory::SqlInjection)
            .collect();

        assert_eq!(sql_warnings.len(), 2);
        assert_eq!(sql_warnings[0].category, WarningCategory::SqlInjection);
    }

    #[test]
    fn test_crlf_injection_detection() {
        let mut analyzer = RequestAnalyzer::new(false);

        analyzer.analyze_headers(&[(
            "X-Custom".to_string(),
            "value\r\nX-Injected: evil".to_string(),
        )]);

        // Count only CRLF injection warnings (command injection may also trigger on \n)
        let crlf_warnings: Vec<_> = analyzer
            .get_warnings()
            .iter()
            .filter(|w| w.category == WarningCategory::CrlfInjection)
            .collect();

        assert_eq!(crlf_warnings.len(), 1);
        assert_eq!(crlf_warnings[0].category, WarningCategory::CrlfInjection);
    }

    #[test]
    fn test_nosql_injection_detection() {
        let mut analyzer = RequestAnalyzer::new(false);

        analyzer.analyze_json_body(r#"{"username": "admin", "password": {"$ne": null}}"#);

        assert_eq!(analyzer.get_warnings().len(), 1);
        assert_eq!(
            analyzer.get_warnings()[0].category,
            WarningCategory::NoSqlInjection
        );
    }

    #[test]
    fn test_no_warnings_flag() {
        let mut analyzer = RequestAnalyzer::new(true);

        analyzer.analyze_url_params(&[("id".to_string(), "1; DROP TABLE users;--".to_string())]);

        assert_eq!(analyzer.get_warnings().len(), 0);
    }
}
