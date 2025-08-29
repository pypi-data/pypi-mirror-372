//! Policy evaluation engine

#![allow(dead_code)]

use super::model::*;
use crate::core::api::types::RunRequest;
use anyhow::Result;
use glob::Pattern;
use std::collections::HashMap;

/// Policy evaluation engine
pub struct PolicyEngine {
    policy: PolicySet,
    compiled_patterns: HashMap<String, Pattern>,
}

impl PolicyEngine {
    /// Create a new policy engine with the given policy set
    pub fn new(policy: PolicySet) -> Result<Self> {
        let mut compiled_patterns = HashMap::new();

        // Pre-compile all patterns for efficiency
        for rule in &policy.rules {
            let pattern = Pattern::new(&rule.pattern)?;
            compiled_patterns.insert(rule.name.clone(), pattern);
        }

        Ok(Self {
            policy,
            compiled_patterns,
        })
    }

    /// Evaluate a request against the policy
    pub fn evaluate(
        &self,
        request: &RunRequest,
        url: &str,
        context: &EvaluationContext,
    ) -> PolicyDecision {
        // SECURITY: Check authentication requirement FIRST
        // This prevents bypassing auth requirements through rule matching
        if self.policy.defaults.require_auth && request.auth_profile.is_none() {
            // Check if any rule explicitly allows unauthenticated access
            let has_explicit_unauth_allow = self.policy.rules.iter().any(|rule| {
                if let Some(pattern) = self.compiled_patterns.get(&rule.name) {
                    if pattern.matches(url) {
                        // Check if this rule has conditions that explicitly don't require auth
                        if let Some(_conditions) = &rule.conditions {
                            // If conditions exist but don't check for auth, this rule doesn't override
                            return false;
                        }
                        // Rule matches and has no auth conditions - check if it allows this operation
                        if let Some(allow) = &rule.allow {
                            return self.matches_action(allow, request, context);
                        }
                    }
                }
                false
            });

            // If no rule explicitly allows unauthenticated access, deny
            if !has_explicit_unauth_allow {
                return PolicyDecision::Deny {
                    rule: "authentication".to_string(),
                    reason: "Authentication required - no rule allows unauthenticated access"
                        .to_string(),
                    audit: Some(AuditConfig {
                        level: self.policy.defaults.audit_level.clone(),
                        include_body: false,
                        include_response: false,
                    }),
                };
            }
        }

        // Check each rule in order
        for rule in &self.policy.rules {
            if let Some(pattern) = self.compiled_patterns.get(&rule.name) {
                if pattern.matches(url) {
                    // Check conditions
                    if let Some(conditions) = &rule.conditions {
                        if !self.check_conditions(conditions, request, context) {
                            continue;
                        }
                    }

                    // Check deny first (deny takes precedence)
                    if let Some(deny) = &rule.deny {
                        if self.matches_action(deny, request, context) {
                            return PolicyDecision::Deny {
                                rule: rule.name.clone(),
                                reason: rule.explain.clone().unwrap_or_else(|| {
                                    format!("Operation denied by rule: {}", rule.name)
                                }),
                                audit: rule.audit.clone(),
                            };
                        }
                    }

                    // Check allow - but only if auth requirements are met
                    if let Some(allow) = &rule.allow {
                        if self.matches_action(allow, request, context) {
                            // Double-check auth requirement for allow decisions
                            if self.policy.defaults.require_auth && request.auth_profile.is_none() {
                                // This shouldn't happen due to earlier check, but defense in depth
                                return PolicyDecision::Deny {
                                    rule: rule.name.clone(),
                                    reason: "Authentication required for this operation"
                                        .to_string(),
                                    audit: rule.audit.clone(),
                                };
                            }
                            return PolicyDecision::Allow {
                                rule: rule.name.clone(),
                                audit: rule.audit.clone(),
                            };
                        }
                    }
                }
            }
        }

        // No matching rule - apply defaults
        self.apply_defaults(request, context)
    }

    /// Check if all conditions are met
    fn check_conditions(
        &self,
        conditions: &[PolicyCondition],
        request: &RunRequest,
        context: &EvaluationContext,
    ) -> bool {
        conditions.iter().all(|condition| {
            // Check auth profile
            if let Some(required_profile) = &condition.auth_profile {
                if let Some(auth_profile) = &request.auth_profile {
                    if auth_profile != required_profile {
                        return false;
                    }
                } else {
                    return false;
                }
            }

            // Check time window
            if let Some(time_window) = &condition.time_window {
                if !self.check_time_window(time_window, context) {
                    return false;
                }
            }

            // Check source IP
            if let Some(required_ip) = &condition.source_ip {
                if let Some(source_ip) = &context.source_ip {
                    if !self.matches_ip_pattern(source_ip, required_ip) {
                        return false;
                    }
                } else {
                    return false;
                }
            }

            // Check environment
            if let Some(required_env) = &condition.environment {
                if let Some(env) = &request.env {
                    if env != required_env {
                        return false;
                    }
                } else {
                    return false;
                }
            }

            true
        })
    }

    /// Check if action matches the request
    fn matches_action(
        &self,
        action: &PolicyAction,
        request: &RunRequest,
        context: &EvaluationContext,
    ) -> bool {
        // Check "all" flag
        if let Some(true) = action.all {
            return true;
        }

        // Check operations
        if let Some(operations) = &action.operations {
            let matches = operations.iter().any(|op_pattern| {
                if let Ok(pattern) = Pattern::new(op_pattern) {
                    pattern.matches(&request.operation_id)
                } else {
                    op_pattern == &request.operation_id
                }
            });

            if !matches {
                return false;
            }
        }

        // Check methods
        if let Some(methods) = &action.methods {
            if let Some(method) = &context.method {
                if !methods.iter().any(|m| m.eq_ignore_ascii_case(method)) {
                    return false;
                }
            }
        }

        // Check tags
        if let Some(required_tags) = &action.tags {
            if let Some(operation_tags) = &context.tags {
                let has_required_tag = required_tags
                    .iter()
                    .any(|required| operation_tags.contains(required));

                if !has_required_tag {
                    return false;
                }
            } else if !required_tags.is_empty() {
                return false;
            }
        }

        true
    }

    /// Apply default policy when no rules match
    fn apply_defaults(&self, request: &RunRequest, context: &EvaluationContext) -> PolicyDecision {
        // Check if authentication is required
        if self.policy.defaults.require_auth && request.auth_profile.is_none() {
            return PolicyDecision::Deny {
                rule: "default".to_string(),
                reason: "Authentication required by default policy".to_string(),
                audit: Some(AuditConfig {
                    level: self.policy.defaults.audit_level.clone(),
                    include_body: false,
                    include_response: false,
                }),
            };
        }

        // Check if method is allowed by default
        if let Some(method) = &context.method {
            if !self
                .policy
                .defaults
                .allow_methods
                .iter()
                .any(|m| m.eq_ignore_ascii_case(method))
            {
                return PolicyDecision::Deny {
                    rule: "default".to_string(),
                    reason: format!("Method {} not allowed by default policy", method),
                    audit: Some(AuditConfig {
                        level: self.policy.defaults.audit_level.clone(),
                        include_body: false,
                        include_response: false,
                    }),
                };
            }
        }

        // Default deny for safety
        PolicyDecision::Deny {
            rule: "default".to_string(),
            reason: "No matching allow rule found".to_string(),
            audit: Some(AuditConfig {
                level: self.policy.defaults.audit_level.clone(),
                include_body: false,
                include_response: false,
            }),
        }
    }

    /// Check time window constraint
    fn check_time_window(&self, time_window: &str, _context: &EvaluationContext) -> bool {
        match time_window {
            "business_hours" => {
                // TODO: Implement business hours check
                true
            }
            "weekdays" => {
                // TODO: Implement weekdays check
                true
            }
            _ => false,
        }
    }

    /// Check if IP matches pattern (supports CIDR notation)
    fn matches_ip_pattern(&self, ip: &str, pattern: &str) -> bool {
        // TODO: Implement proper IP matching with CIDR support
        ip == pattern
    }
}

/// Evaluation context provides additional information for policy decisions
#[derive(Debug, Clone)]
pub struct EvaluationContext {
    /// HTTP method of the operation
    pub method: Option<String>,

    /// Tags associated with the operation
    pub tags: Option<Vec<String>>,

    /// Source IP address
    pub source_ip: Option<String>,

    /// Current timestamp
    pub timestamp: chrono::DateTime<chrono::Utc>,
}

impl Default for EvaluationContext {
    fn default() -> Self {
        Self {
            method: None,
            tags: None,
            source_ip: None,
            timestamp: chrono::Utc::now(),
        }
    }
}

/// Result of policy evaluation
#[derive(Debug, Clone)]
pub enum PolicyDecision {
    Allow {
        rule: String,
        audit: Option<AuditConfig>,
    },
    Deny {
        rule: String,
        reason: String,
        audit: Option<AuditConfig>,
    },
}

impl PolicyDecision {
    /// Check if the decision is to allow the operation
    pub fn is_allowed(&self) -> bool {
        matches!(self, PolicyDecision::Allow { .. })
    }

    /// Get the rule name that made the decision
    pub fn rule_name(&self) -> &str {
        match self {
            PolicyDecision::Allow { rule, .. } => rule,
            PolicyDecision::Deny { rule, .. } => rule,
        }
    }

    /// Get the audit configuration for this decision
    pub fn audit_config(&self) -> Option<&AuditConfig> {
        match self {
            PolicyDecision::Allow { audit, .. } => audit.as_ref(),
            PolicyDecision::Deny { audit, .. } => audit.as_ref(),
        }
    }
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
                name: "readonly".to_string(),
                description: Some("Allow read-only operations".to_string()),
                pattern: "*".to_string(),
                conditions: None,
                allow: Some(PolicyAction {
                    methods: Some(vec!["GET".to_string()]),
                    operations: Some(vec!["get*".to_string(), "list*".to_string()]),
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
    fn test_allow_readonly_operation() {
        let policy = create_test_policy();
        let engine = PolicyEngine::new(policy).unwrap();

        let request = RunRequest {
            operation_id: "getUser".to_string(),
            parameters: None,
            body: None,
            spec_path: None,
            env: None,
            auth_profile: Some("default".to_string()),
        };

        let context = EvaluationContext {
            method: Some("GET".to_string()),
            ..Default::default()
        };

        let decision = engine.evaluate(&request, "https://api.example.com/users/123", &context);
        assert!(decision.is_allowed());
        assert_eq!(decision.rule_name(), "readonly");
    }

    #[test]
    fn test_deny_write_operation() {
        let policy = create_test_policy();
        let engine = PolicyEngine::new(policy).unwrap();

        let request = RunRequest {
            operation_id: "createUser".to_string(),
            parameters: None,
            body: None,
            spec_path: None,
            env: None,
            auth_profile: Some("default".to_string()),
        };

        let context = EvaluationContext {
            method: Some("POST".to_string()),
            ..Default::default()
        };

        let decision = engine.evaluate(&request, "https://api.example.com/users", &context);
        assert!(!decision.is_allowed());
    }

    #[test]
    fn test_deny_no_auth() {
        let policy = create_test_policy();
        let engine = PolicyEngine::new(policy).unwrap();

        let request = RunRequest {
            operation_id: "getUser".to_string(),
            parameters: None,
            body: None,
            spec_path: None,
            env: None,
            auth_profile: None, // No auth
        };

        let context = EvaluationContext {
            method: Some("GET".to_string()),
            ..Default::default()
        };

        let decision = engine.evaluate(&request, "https://api.example.com/users/123", &context);
        assert!(!decision.is_allowed());

        if let PolicyDecision::Deny { reason, .. } = decision {
            assert!(reason.contains("Authentication required"));
        }
    }
}
