use super::report::ValidationReport;
use super::rules;
/// Main validator that orchestrates different validation levels
use super::types::{ValidationLevel, ValidationResult};
use super::version::{detect_spec_version, SpecVersion};
use anyhow::{Context, Result};
use serde_json::Value;
use std::path::Path;
use std::time::Instant;

/// OpenAPI specification validator
pub struct SpecValidator;

impl SpecValidator {
    /// Create a new validator
    pub fn new() -> Result<Self> {
        Ok(Self)
    }

    /// Validate a spec from file path
    pub fn validate_file(&self, path: &Path, level: ValidationLevel) -> Result<ValidationReport> {
        let content = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read spec file: {}", path.display()))?;

        self.validate_content(&content, level)
    }

    /// Validate a spec from string content
    pub fn validate_content(
        &self,
        content: &str,
        level: ValidationLevel,
    ) -> Result<ValidationReport> {
        let start = Instant::now();

        // Detect version
        let version = detect_spec_version(content)?;
        let mut report = ValidationReport::new(version.clone());

        // Parse spec as JSON value for validation
        let spec: Value = serde_json::from_str(content)
            .or_else(|_| serde_yaml::from_str(content))
            .context("Failed to parse OpenAPI specification. Please ensure the file is valid JSON or YAML and follows OpenAPI 3.x format")?;

        // Run validation based on level
        match level {
            ValidationLevel::Quick => {
                report.levels_checked.push("quick".to_string());
                let results = self.validate_quick(&spec, &version)?;
                report.merge_results(results);
            }
            ValidationLevel::Standard => {
                report.levels_checked.push("quick".to_string());
                report.levels_checked.push("standard".to_string());

                // Quick validation first
                let results = self.validate_quick(&spec, &version)?;
                report.merge_results(results);

                // Then standard validation
                let results = self.validate_standard(&spec, &version)?;
                report.merge_results(results);
            }
            ValidationLevel::Full => {
                report.levels_checked.push("quick".to_string());
                report.levels_checked.push("standard".to_string());
                report.levels_checked.push("security".to_string());
                report.levels_checked.push("lint".to_string());

                // All levels
                let results = self.validate_quick(&spec, &version)?;
                report.merge_results(results);

                let results = self.validate_standard(&spec, &version)?;
                report.merge_results(results);

                let results = self.validate_security(&spec)?;
                report.merge_results(results);

                let results = self.validate_lint(&spec)?;
                report.merge_results(results);
            }
        }

        report.duration = start.elapsed();
        Ok(report)
    }

    /// Quick validation - basic structure only
    fn validate_quick(&self, spec: &Value, _version: &SpecVersion) -> Result<ValidationResult> {
        Ok(rules::basic::validate_basic_structure(spec))
    }

    /// Standard validation - OAS compliance
    fn validate_standard(&self, spec: &Value, _version: &SpecVersion) -> Result<ValidationResult> {
        let mut results = ValidationResult::new();

        // Basic structure validation
        let basic_results = rules::basic::validate_basic_structure(spec);
        results.merge(basic_results);

        // Reference validation
        let ref_results = rules::references::validate_references(spec);
        results.merge(ref_results);

        // Operation validation (duplicates, path params)
        let op_results = rules::operations::validate_operations(spec);
        results.merge(op_results);

        // Schema validation (type constraints)
        let schema_results = rules::schemas::validate_schemas(spec);
        results.merge(schema_results);

        // Add MicroRapid requirements
        let mrapids_results = rules::basic::validate_mrapids_requirements(spec);
        results.merge(mrapids_results);

        Ok(results)
    }

    /// Security validation
    fn validate_security(&self, spec: &Value) -> Result<ValidationResult> {
        Ok(rules::basic::validate_security(spec))
    }

    /// Lint validation - best practices and style
    fn validate_lint(&self, spec: &Value) -> Result<ValidationResult> {
        let mut results = ValidationResult::new();

        // Add linting rules
        let lint_results = rules::lint::validate_best_practices(spec);
        results.merge(lint_results);

        Ok(results)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_validate_valid_oas3() {
        let spec = json!({
            "openapi": "3.0.2",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "responses": {
                            "200": {
                                "description": "Success"
                            }
                        }
                    }
                }
            }
        });

        let validator = SpecValidator::new().unwrap();
        let report = validator
            .validate_content(
                &serde_json::to_string(&spec).unwrap(),
                ValidationLevel::Quick,
            )
            .unwrap();

        assert!(report.is_valid());
    }

    #[test]
    fn test_validate_missing_info() {
        let spec = json!({
            "openapi": "3.0.2",
            "paths": {}
        });

        let validator = SpecValidator::new().unwrap();
        let report = validator
            .validate_content(
                &serde_json::to_string(&spec).unwrap(),
                ValidationLevel::Quick,
            )
            .unwrap();

        assert!(!report.is_valid());
        assert!(report.error_count() > 0);
    }

    #[test]
    fn test_validate_security_http() {
        let spec = json!({
            "openapi": "3.0.2",
            "info": {
                "title": "Test API",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "http://api.example.com"
                }
            ],
            "paths": {}
        });

        let validator = SpecValidator::new().unwrap();
        let report = validator
            .validate_content(
                &serde_json::to_string(&spec).unwrap(),
                ValidationLevel::Full,
            )
            .unwrap();

        assert!(report.has_warnings());
    }
}
