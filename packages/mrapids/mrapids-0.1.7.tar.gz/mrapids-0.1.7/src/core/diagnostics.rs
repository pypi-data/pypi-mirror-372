use colored::*;

/// Enhanced error with diagnostics and suggestions
pub struct DiagnosticError {
    pub error: anyhow::Error,
    pub suggestions: Vec<String>,
    pub context: Option<ErrorContext>,
}

#[derive(Debug, Clone)]
pub struct ErrorContext {
    pub file: Option<String>,
    pub line: Option<usize>,
    pub column: Option<usize>,
    pub snippet: Option<String>,
}

impl DiagnosticError {
    pub fn new(error: anyhow::Error) -> Self {
        Self {
            error,
            suggestions: Vec::new(),
            context: None,
        }
    }

    pub fn with_suggestion(mut self, suggestion: impl Into<String>) -> Self {
        self.suggestions.push(suggestion.into());
        self
    }

    pub fn with_context(mut self, context: ErrorContext) -> Self {
        self.context = Some(context);
        self
    }

    pub fn display(&self) {
        // Error header
        println!("{} {}", "❌ Error:".bright_red(), self.error);

        // Context information
        if let Some(ctx) = &self.context {
            println!();
            if let (Some(file), Some(line)) = (&ctx.file, ctx.line) {
                println!("   {} {}:{}", "at".dimmed(), file.cyan(), line);
            }

            if let Some(snippet) = &ctx.snippet {
                println!();
                println!("   {}", snippet);
                if let Some(col) = ctx.column {
                    let pointer = " ".repeat(3 + col) + "^";
                    println!("{}", pointer.bright_red());
                }
            }
        }

        // Suggestions
        if !self.suggestions.is_empty() {
            println!();
            println!(
                "{} {}",
                "💡".bright_yellow(),
                "Suggestions:".bright_yellow()
            );
            for (i, suggestion) in self.suggestions.iter().enumerate() {
                println!("   {}. {}", i + 1, suggestion);
            }
        }
    }
}

/// Common error scenarios with helpful suggestions
pub fn enhance_error(error: anyhow::Error) -> DiagnosticError {
    let error_str = error.to_string();
    let mut diagnostic = DiagnosticError::new(error);

    // Parameter reference errors
    if error_str.contains("missing field `name`") && error_str.contains("parameter") {
        diagnostic = diagnostic
            .with_suggestion("This looks like a parameter reference issue. Make sure your OpenAPI spec uses proper $ref syntax")
            .with_suggestion("Example: { \"$ref\": \"#/components/parameters/MyParam\" }")
            .with_suggestion("If using Swagger 2.0, references should point to '#/parameters/...'");
    }
    // Schema reference errors
    else if error_str.contains("Schema") && error_str.contains("not found") {
        if let Some(schema_name) = extract_quoted_text(&error_str) {
            diagnostic = diagnostic
                .with_suggestion(format!(
                    "Schema '{}' is not defined in components/schemas",
                    schema_name
                ))
                .with_suggestion("Check your spec for typos in the schema name")
                .with_suggestion("Make sure the schema is defined before it's referenced");
        }
    }
    // Circular reference errors
    else if error_str.contains("Circular reference detected") {
        diagnostic = diagnostic
            .with_suggestion("Your spec has a circular reference chain")
            .with_suggestion(
                "Consider using allOf with a base schema instead of direct circular refs",
            )
            .with_suggestion(
                "You can use 'mrapids flatten --include-unused' to see the reference chain",
            );
    }
    // External reference errors
    else if error_str.contains("External") && error_str.contains("not yet implemented") {
        diagnostic = diagnostic
            .with_suggestion("External references require the --resolve-external flag")
            .with_suggestion("Example: mrapids flatten spec.yaml --resolve-external")
            .with_suggestion("Make sure external files exist and are accessible");
    }
    // File not found errors
    else if error_str.contains("Cannot read spec file") || error_str.contains("No such file") {
        diagnostic = diagnostic
            .with_suggestion("Check that the file path is correct")
            .with_suggestion("Use 'mrapids list' to see available spec files")
            .with_suggestion("Make sure you're in the right directory");
    }
    // YAML parsing errors
    else if error_str.contains("Failed to parse") && error_str.contains("YAML") {
        diagnostic = diagnostic
            .with_suggestion("Check your YAML syntax - common issues include:")
            .with_suggestion("  • Incorrect indentation (use spaces, not tabs)")
            .with_suggestion("  • Missing quotes around special characters")
            .with_suggestion("  • Invalid YAML anchors or references")
            .with_suggestion("Try validating with: mrapids validate <your-spec.yaml>");
    }
    // Authentication errors
    else if error_str.contains("401") || error_str.contains("Unauthorized") {
        diagnostic = diagnostic
            .with_suggestion("The API requires authentication")
            .with_suggestion("Set up auth with: mrapids auth login <provider>")
            .with_suggestion("Or use environment variables for API keys")
            .with_suggestion("Check the API documentation for required auth headers");
    }
    // Network errors
    else if error_str.contains("Connection refused") || error_str.contains("Failed to connect") {
        diagnostic = diagnostic
            .with_suggestion("Cannot connect to the API server")
            .with_suggestion("Check if the server is running and accessible")
            .with_suggestion("Verify the base URL in your spec or config")
            .with_suggestion("Check for proxy or firewall issues");
    }

    diagnostic
}

/// Extract text between single quotes from an error message
fn extract_quoted_text(text: &str) -> Option<&str> {
    let start = text.find('\'')?;
    let rest = &text[start + 1..];
    let end = rest.find('\'')?;
    Some(&rest[..end])
}

/// Create a diagnostic error with YAML parsing context
pub fn yaml_parse_error(error: serde_yaml::Error, content: &str) -> DiagnosticError {
    let location = error.location();
    let mut diagnostic = DiagnosticError::new(anyhow::anyhow!("YAML parsing failed: {}", error));

    if let Some(loc) = location {
        let lines: Vec<&str> = content.lines().collect();
        let line_num = loc.line();
        let col_num = loc.column();

        // Create context
        let mut context = ErrorContext {
            file: None,
            line: Some(line_num),
            column: Some(col_num),
            snippet: None,
        };

        // Add snippet with context lines
        if line_num > 0 && line_num <= lines.len() {
            let mut snippet_lines = Vec::new();

            // Add previous line if available
            if line_num > 1 {
                snippet_lines.push(format!("{:4} | {}", line_num - 1, lines[line_num - 2]));
            }

            // Add error line
            snippet_lines.push(format!("{:4} | {}", line_num, lines[line_num - 1]));

            // Add next line if available
            if line_num < lines.len() {
                snippet_lines.push(format!("{:4} | {}", line_num + 1, lines[line_num]));
            }

            context.snippet = Some(snippet_lines.join("\n"));
        }

        diagnostic = diagnostic.with_context(context);
    }

    // Add YAML-specific suggestions
    diagnostic
        .with_suggestion("Check indentation - YAML requires consistent spaces (not tabs)")
        .with_suggestion("Ensure proper quoting of special characters (:, -, ?, etc.)")
        .with_suggestion("Verify that lists start with '-' at the correct indentation")
}

/// Create a diagnostic error for spec validation
#[allow(dead_code)]
pub fn validation_error(field: &str, issue: &str, suggestion: &str) -> DiagnosticError {
    DiagnosticError::new(anyhow::anyhow!(
        "Validation failed for field '{}': {}",
        field,
        issue
    ))
    .with_suggestion(suggestion)
}
