//! Policy decision explanation generator

#![allow(dead_code)]

use super::engine::{EvaluationContext, PolicyDecision};
use super::model::*;
use crate::core::api::types::RunRequest;
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::fmt;

/// Detailed explanation of a policy decision
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicyExplanation {
    /// The final decision (allow or deny)
    pub decision: String,

    /// The rule that made the decision
    pub rule_name: String,

    /// Human-readable summary
    pub summary: String,

    /// Detailed explanation
    pub details: Vec<String>,

    /// Suggestions for resolution (if denied)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub suggestions: Option<Vec<String>>,

    /// Audit configuration that will be applied
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub audit_level: Option<String>,
}

impl fmt::Display for PolicyExplanation {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        writeln!(f, "Policy Decision: {}", self.decision)?;
        writeln!(f, "Rule: {}", self.rule_name)?;
        writeln!(f, "Summary: {}", self.summary)?;

        if !self.details.is_empty() {
            writeln!(f, "\nDetails:")?;
            for detail in &self.details {
                writeln!(f, "  - {}", detail)?;
            }
        }

        if let Some(suggestions) = &self.suggestions {
            writeln!(f, "\nSuggestions:")?;
            for suggestion in suggestions {
                writeln!(f, "  • {}", suggestion)?;
            }
        }

        if let Some(audit_level) = &self.audit_level {
            writeln!(f, "\nAudit Level: {}", audit_level)?;
        }

        Ok(())
    }
}

/// Generate a detailed explanation for a policy decision
pub fn explain_decision(
    decision: &PolicyDecision,
    request: &RunRequest,
    url: &str,
    context: &EvaluationContext,
    policy: Option<&PolicySet>,
) -> PolicyExplanation {
    match decision {
        PolicyDecision::Allow { rule, audit } => {
            explain_allow(rule, audit.as_ref(), request, url, context)
        }
        PolicyDecision::Deny {
            rule,
            reason,
            audit,
        } => explain_deny(rule, reason, audit.as_ref(), request, url, context, policy),
    }
}

fn explain_allow(
    rule: &str,
    audit: Option<&AuditConfig>,
    request: &RunRequest,
    url: &str,
    context: &EvaluationContext,
) -> PolicyExplanation {
    let mut details = vec![
        format!("Operation '{}' is allowed", request.operation_id),
        format!("Matched URL pattern: {}", url),
    ];

    if let Some(method) = &context.method {
        details.push(format!("HTTP method: {}", method));
    }

    if let Some(auth) = &request.auth_profile {
        details.push(format!("Authenticated with profile: {}", auth));
    }

    PolicyExplanation {
        decision: "ALLOW".to_string(),
        rule_name: rule.to_string(),
        summary: format!(
            "Operation '{}' is permitted by rule '{}'",
            request.operation_id, rule
        ),
        details,
        suggestions: None,
        audit_level: audit.map(|a| a.level.clone()),
    }
}

fn explain_deny(
    rule: &str,
    reason: &str,
    audit: Option<&AuditConfig>,
    request: &RunRequest,
    url: &str,
    context: &EvaluationContext,
    policy: Option<&PolicySet>,
) -> PolicyExplanation {
    let mut details = vec![
        format!("Operation '{}' is denied", request.operation_id),
        format!("URL: {}", url),
        format!("Reason: {}", reason),
    ];

    if let Some(method) = &context.method {
        details.push(format!("HTTP method: {}", method));
    }

    // Generate suggestions based on the denial reason
    let suggestions = generate_suggestions(rule, reason, request, context, policy);

    PolicyExplanation {
        decision: "DENY".to_string(),
        rule_name: rule.to_string(),
        summary: reason.to_string(),
        details,
        suggestions: Some(suggestions),
        audit_level: audit.map(|a| a.level.clone()),
    }
}

fn generate_suggestions(
    _rule: &str,
    reason: &str,
    request: &RunRequest,
    _context: &EvaluationContext,
    policy: Option<&PolicySet>,
) -> Vec<String> {
    let mut suggestions = Vec::new();

    // Authentication-related suggestions
    if reason.contains("Authentication required") {
        suggestions.push("Provide authentication using --profile flag".to_string());
        suggestions.push("Configure authentication with: mrapids auth add <profile>".to_string());
    }

    // Method-related suggestions
    if reason.contains("Method") && reason.contains("not allowed") {
        if let Some(policy) = policy {
            let allowed_methods = &policy.defaults.allow_methods;
            suggestions.push(format!(
                "This policy only allows the following methods: {}",
                allowed_methods.join(", ")
            ));
        }
        suggestions.push("Consider using a read-only operation instead".to_string());
    }

    // Operation-related suggestions
    if reason.contains("No matching allow rule") {
        suggestions.push("This operation is not explicitly allowed by any policy rule".to_string());

        // Check if it's a write operation that could be read
        if request.operation_id.starts_with("create")
            || request.operation_id.starts_with("update")
            || request.operation_id.starts_with("delete")
        {
            let read_op = request
                .operation_id
                .replace("create", "get")
                .replace("update", "get")
                .replace("delete", "get");
            suggestions.push(format!("Try the read-only operation '{}' instead", read_op));
        }
    }

    // Environment-related suggestions
    if let Some(env) = &request.env {
        if reason.contains("environment") {
            suggestions.push(format!("Current environment '{}' may not have access", env));
            suggestions.push(
                "Check with your administrator for environment-specific policies".to_string(),
            );
        }
    }

    // Default suggestion
    if suggestions.is_empty() {
        suggestions.push("Contact your administrator for access to this operation".to_string());
        suggestions.push("Review the policy documentation for allowed operations".to_string());
    }

    suggestions
}

/// Generate a policy report showing what operations are allowed/denied
pub fn generate_policy_report(policy: &PolicySet) -> String {
    let mut report = String::new();

    report.push_str(&format!(
        "Policy Report: {}\n",
        policy
            .metadata
            .as_ref()
            .map(|m| m.name.as_str())
            .unwrap_or("Unnamed Policy")
    ));
    report.push_str(&format!("Version: {}\n", policy.version));
    report.push_str("\n");

    // Defaults section
    report.push_str("Default Settings:\n");
    report.push_str(&format!(
        "  • Allowed Methods: {}\n",
        policy.defaults.allow_methods.join(", ")
    ));
    report.push_str(&format!(
        "  • Require Authentication: {}\n",
        policy.defaults.require_auth
    ));
    report.push_str(&format!(
        "  • Deny External References: {}\n",
        policy.defaults.deny_external_refs
    ));
    report.push_str(&format!(
        "  • Audit Level: {}\n",
        policy.defaults.audit_level
    ));
    report.push_str("\n");

    // Rules section
    report.push_str("Policy Rules:\n");
    for (i, rule) in policy.rules.iter().enumerate() {
        report.push_str(&format!(
            "\n{}. {} (pattern: {})\n",
            i + 1,
            rule.name,
            rule.pattern
        ));

        if let Some(desc) = &rule.description {
            report.push_str(&format!("   Description: {}\n", desc));
        }

        if let Some(allow) = &rule.allow {
            report.push_str("   Allows:\n");
            if let Some(methods) = &allow.methods {
                report.push_str(&format!("     - Methods: {}\n", methods.join(", ")));
            }
            if let Some(ops) = &allow.operations {
                report.push_str(&format!("     - Operations: {}\n", ops.join(", ")));
            }
            if let Some(true) = allow.all {
                report.push_str("     - All operations\n");
            }
        }

        if let Some(deny) = &rule.deny {
            report.push_str("   Denies:\n");
            if let Some(methods) = &deny.methods {
                report.push_str(&format!("     - Methods: {}\n", methods.join(", ")));
            }
            if let Some(ops) = &deny.operations {
                report.push_str(&format!("     - Operations: {}\n", ops.join(", ")));
            }
            if let Some(true) = deny.all {
                report.push_str("     - All operations\n");
            }
        }

        if let Some(conditions) = &rule.conditions {
            report.push_str("   Conditions:\n");
            for condition in conditions {
                if let Some(auth) = &condition.auth_profile {
                    report.push_str(&format!("     - Auth Profile: {}\n", auth));
                }
                if let Some(tw) = &condition.time_window {
                    report.push_str(&format!("     - Time Window: {}\n", tw));
                }
                if let Some(ip) = &condition.source_ip {
                    report.push_str(&format!("     - Source IP: {}\n", ip));
                }
                if let Some(env) = &condition.environment {
                    report.push_str(&format!("     - Environment: {}\n", env));
                }
            }
        }
    }

    report
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_explain_allow_decision() {
        let decision = PolicyDecision::Allow {
            rule: "test-rule".to_string(),
            audit: Some(AuditConfig {
                level: "basic".to_string(),
                include_body: false,
                include_response: false,
            }),
        };

        let request = RunRequest {
            operation_id: "getUser".to_string(),
            auth_profile: Some("default".to_string()),
            ..Default::default()
        };

        let context = EvaluationContext {
            method: Some("GET".to_string()),
            ..Default::default()
        };

        let explanation = explain_decision(
            &decision,
            &request,
            "https://api.example.com/users/123",
            &context,
            None,
        );

        assert_eq!(explanation.decision, "ALLOW");
        assert_eq!(explanation.rule_name, "test-rule");
        assert!(explanation.summary.contains("permitted"));
        assert!(explanation.suggestions.is_none());
    }

    #[test]
    fn test_explain_deny_auth_required() {
        let decision = PolicyDecision::Deny {
            rule: "default".to_string(),
            reason: "Authentication required by default policy".to_string(),
            audit: None,
        };

        let request = RunRequest {
            operation_id: "getUser".to_string(),
            auth_profile: None,
            ..Default::default()
        };

        let context = EvaluationContext::default();

        let explanation = explain_decision(
            &decision,
            &request,
            "https://api.example.com/users/123",
            &context,
            None,
        );

        assert_eq!(explanation.decision, "DENY");
        assert!(explanation.suggestions.is_some());

        let suggestions = explanation.suggestions.unwrap();
        assert!(suggestions.iter().any(|s| s.contains("--profile")));
    }
}
