//! Policy testing framework

#![allow(dead_code)]

use super::engine::{EvaluationContext, PolicyDecision, PolicyEngine};
use super::model::*;
use super::parser::validate_policy;
use crate::core::api::types::RunRequest;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Test scenario for policy evaluation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyTestScenario {
    /// Scenario name
    pub name: String,

    /// Description of what's being tested
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    /// The request to test
    pub request: TestRequest,

    /// The URL to test against
    pub url: String,

    /// Evaluation context
    #[serde(default)]
    pub context: TestContext,

    /// Expected outcome
    pub expected: ExpectedOutcome,
}

/// Simplified request for testing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TestRequest {
    pub operation_id: String,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub auth_profile: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub env: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub parameters: Option<HashMap<String, serde_json::Value>>,
}

/// Test context
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct TestContext {
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub method: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tags: Option<Vec<String>>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_ip: Option<String>,
}

/// Expected test outcome
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExpectedOutcome {
    /// Expected decision (allow/deny)
    pub decision: String,

    /// Expected rule name (optional)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub rule: Option<String>,

    /// Expected reason pattern (for denials)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub reason_contains: Option<String>,
}

/// Result of a test scenario
#[derive(Debug)]
pub struct TestResult {
    pub scenario_name: String,
    pub passed: bool,
    pub message: String,
    pub actual_decision: PolicyDecision,
}

/// Policy test runner
pub struct PolicyTestRunner {
    engine: PolicyEngine,
}

impl PolicyTestRunner {
    /// Create a new test runner with a policy
    pub fn new(policy: PolicySet) -> Result<Self> {
        // Validate policy first
        validate_policy(&policy)?;

        let engine = PolicyEngine::new(policy)?;
        Ok(Self { engine })
    }

    /// Run a single test scenario
    pub fn run_scenario(&self, scenario: &PolicyTestScenario) -> TestResult {
        // Convert test request to API request
        let request = RunRequest {
            operation_id: scenario.request.operation_id.clone(),
            auth_profile: scenario.request.auth_profile.clone(),
            env: scenario.request.env.clone(),
            parameters: scenario.request.parameters.clone(),
            body: None,
            spec_path: None,
        };

        // Build evaluation context
        let context = EvaluationContext {
            method: scenario.context.method.clone(),
            tags: scenario.context.tags.clone(),
            source_ip: scenario.context.source_ip.clone(),
            timestamp: chrono::Utc::now(),
        };

        // Evaluate the policy
        let decision = self.engine.evaluate(&request, &scenario.url, &context);

        // Check the result
        let (passed, message) = self.check_outcome(&decision, &scenario.expected);

        TestResult {
            scenario_name: scenario.name.clone(),
            passed,
            message,
            actual_decision: decision,
        }
    }

    /// Run multiple test scenarios
    pub fn run_scenarios(&self, scenarios: &[PolicyTestScenario]) -> Vec<TestResult> {
        scenarios
            .iter()
            .map(|scenario| self.run_scenario(scenario))
            .collect()
    }

    /// Check if the actual outcome matches expected
    fn check_outcome(
        &self,
        decision: &PolicyDecision,
        expected: &ExpectedOutcome,
    ) -> (bool, String) {
        let actual_decision = if decision.is_allowed() {
            "allow"
        } else {
            "deny"
        };

        // Check decision type
        if actual_decision != expected.decision.to_lowercase() {
            return (
                false,
                format!("Expected {} but got {}", expected.decision, actual_decision),
            );
        }

        // Check rule name if specified
        if let Some(expected_rule) = &expected.rule {
            if decision.rule_name() != expected_rule {
                return (
                    false,
                    format!(
                        "Expected rule '{}' but got '{}'",
                        expected_rule,
                        decision.rule_name()
                    ),
                );
            }
        }

        // Check reason for denials
        if let PolicyDecision::Deny { reason, .. } = decision {
            if let Some(expected_pattern) = &expected.reason_contains {
                if !reason.contains(expected_pattern) {
                    return (
                        false,
                        format!(
                            "Expected reason to contain '{}' but got '{}'",
                            expected_pattern, reason
                        ),
                    );
                }
            }
        }

        (true, "Test passed".to_string())
    }
}

/// Load test scenarios from YAML file
pub fn load_test_scenarios(content: &str) -> Result<Vec<PolicyTestScenario>> {
    let scenarios: Vec<PolicyTestScenario> = serde_yaml::from_str(content)?;
    Ok(scenarios)
}

/// Generate a test report
pub fn generate_test_report(results: &[TestResult]) -> String {
    let mut report = String::new();

    let total = results.len();
    let passed = results.iter().filter(|r| r.passed).count();
    let failed = total - passed;

    report.push_str(&format!("Policy Test Results\n"));
    report.push_str(&format!("==================\n\n"));
    report.push_str(&format!(
        "Total: {} | Passed: {} | Failed: {}\n\n",
        total, passed, failed
    ));

    // Group by status
    if failed > 0 {
        report.push_str("FAILED TESTS:\n");
        for result in results.iter().filter(|r| !r.passed) {
            report.push_str(&format!(
                "  ❌ {} - {}\n",
                result.scenario_name, result.message
            ));
        }
        report.push_str("\n");
    }

    if passed > 0 {
        report.push_str("PASSED TESTS:\n");
        for result in results.iter().filter(|r| r.passed) {
            report.push_str(&format!("  ✅ {}\n", result.scenario_name));
        }
    }

    report
}

#[cfg(test)]
mod tests {
    use super::*;

    fn create_test_policy() -> PolicySet {
        PolicySet {
            version: "1.0".to_string(),
            metadata: None,
            defaults: PolicyDefaults {
                allow_methods: vec!["GET".to_string()],
                deny_external_refs: true,
                require_auth: true,
                audit_level: "basic".to_string(),
            },
            rules: vec![PolicyRule {
                name: "public-read".to_string(),
                description: None,
                pattern: "api.public.com/*".to_string(),
                conditions: None,
                allow: Some(PolicyAction {
                    methods: Some(vec!["GET".to_string()]),
                    operations: None,
                    all: None,
                    tags: None,
                }),
                deny: None,
                audit: None,
                explain: None,
            }],
        }
    }

    #[test]
    fn test_scenario_pass() {
        let policy = create_test_policy();
        let runner = PolicyTestRunner::new(policy).unwrap();

        let scenario = PolicyTestScenario {
            name: "Allow public GET".to_string(),
            description: None,
            request: TestRequest {
                operation_id: "getResource".to_string(),
                auth_profile: Some("default".to_string()),
                env: None,
                parameters: None,
            },
            url: "api.public.com/resource".to_string(),
            context: TestContext {
                method: Some("GET".to_string()),
                tags: None,
                source_ip: None,
            },
            expected: ExpectedOutcome {
                decision: "allow".to_string(),
                rule: Some("public-read".to_string()),
                reason_contains: None,
            },
        };

        let result = runner.run_scenario(&scenario);
        assert!(result.passed);
    }

    #[test]
    fn test_scenario_fail_wrong_method() {
        let policy = create_test_policy();
        let runner = PolicyTestRunner::new(policy).unwrap();

        let scenario = PolicyTestScenario {
            name: "Deny POST to public".to_string(),
            description: None,
            request: TestRequest {
                operation_id: "createResource".to_string(),
                auth_profile: Some("default".to_string()),
                env: None,
                parameters: None,
            },
            url: "api.public.com/resource".to_string(),
            context: TestContext {
                method: Some("POST".to_string()),
                tags: None,
                source_ip: None,
            },
            expected: ExpectedOutcome {
                decision: "deny".to_string(),
                rule: None,
                reason_contains: Some("Method POST not allowed".to_string()),
            },
        };

        let result = runner.run_scenario(&scenario);
        assert!(result.passed);
    }

    #[test]
    fn test_load_scenarios_from_yaml() {
        let yaml = r#"
- name: "Test scenario 1"
  request:
    operation_id: "getUser"
    auth_profile: "default"
  url: "https://api.example.com/users/123"
  context:
    method: "GET"
  expected:
    decision: "allow"
"#;

        let scenarios = load_test_scenarios(yaml).unwrap();
        assert_eq!(scenarios.len(), 1);
        assert_eq!(scenarios[0].name, "Test scenario 1");
    }
}
