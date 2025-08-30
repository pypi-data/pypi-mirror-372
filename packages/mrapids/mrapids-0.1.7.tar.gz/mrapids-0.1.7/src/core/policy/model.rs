//! Policy model types for agent access control

use schemars::JsonSchema;
use serde::{Deserialize, Serialize};

/// Policy configuration set
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicySet {
    /// Policy version (e.g., "1.0")
    pub version: String,

    /// Metadata about the policy
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub metadata: Option<PolicyMetadata>,

    /// Default settings that apply globally
    pub defaults: PolicyDefaults,

    /// List of policy rules evaluated in order
    pub rules: Vec<PolicyRule>,
}

/// Policy metadata
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicyMetadata {
    pub name: String,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub author: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub created: Option<String>,

    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub modified: Option<String>,
}

/// Default policy settings
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicyDefaults {
    /// HTTP methods allowed by default
    #[serde(default = "default_allow_methods")]
    pub allow_methods: Vec<String>,

    /// Whether to deny external references by default
    #[serde(default = "default_true")]
    pub deny_external_refs: bool,

    /// Whether to require authentication by default
    #[serde(default = "default_true")]
    pub require_auth: bool,

    /// Default audit level
    #[serde(default = "default_audit_level")]
    pub audit_level: String,
}

/// Individual policy rule
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicyRule {
    /// Rule name for identification
    pub name: String,

    /// Human-readable description
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    /// Pattern to match (glob-style, e.g., "api.github.com/*")
    pub pattern: String,

    /// Conditions that must be met for rule to apply
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub conditions: Option<Vec<PolicyCondition>>,

    /// Actions to allow
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub allow: Option<PolicyAction>,

    /// Actions to deny (takes precedence over allow)
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub deny: Option<PolicyAction>,

    /// Audit configuration for this rule
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub audit: Option<AuditConfig>,

    /// Custom explanation for denials
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub explain: Option<String>,
}

/// Policy condition
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicyCondition {
    /// Required auth profile
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub auth_profile: Option<String>,

    /// Time window constraint (e.g., "business_hours", "weekdays")
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub time_window: Option<String>,

    /// Source IP constraint
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub source_ip: Option<String>,

    /// Environment constraint (e.g., "production", "staging")
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub environment: Option<String>,
}

/// Policy action specification
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct PolicyAction {
    /// Specific operations (supports wildcards, e.g., ["get*", "list*"])
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub operations: Option<Vec<String>>,

    /// HTTP methods
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub methods: Option<Vec<String>>,

    /// Allow/deny all operations
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub all: Option<bool>,

    /// Tags to match
    #[serde(default, skip_serializing_if = "Option::is_none")]
    pub tags: Option<Vec<String>>,
}

/// Audit configuration
#[derive(Debug, Clone, Serialize, Deserialize, JsonSchema)]
pub struct AuditConfig {
    /// Audit level: "none", "basic", "detailed"
    #[serde(default = "default_audit_level")]
    pub level: String,

    /// Include request body in audit
    #[serde(default)]
    pub include_body: bool,

    /// Include response in audit
    #[serde(default)]
    pub include_response: bool,
}

// Default value functions
fn default_allow_methods() -> Vec<String> {
    vec!["GET".to_string(), "HEAD".to_string(), "OPTIONS".to_string()]
}

fn default_true() -> bool {
    true
}

fn default_audit_level() -> String {
    "basic".to_string()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_policy_defaults() {
        let defaults = PolicyDefaults {
            allow_methods: default_allow_methods(),
            deny_external_refs: true,
            require_auth: true,
            audit_level: "basic".to_string(),
        };

        assert_eq!(defaults.allow_methods, vec!["GET", "HEAD", "OPTIONS"]);
        assert!(defaults.deny_external_refs);
        assert!(defaults.require_auth);
    }

    #[test]
    fn test_policy_rule_serialization() {
        let rule = PolicyRule {
            name: "test-rule".to_string(),
            description: Some("Test rule".to_string()),
            pattern: "*.example.com/*".to_string(),
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
        };

        let json = serde_json::to_string_pretty(&rule).unwrap();
        assert!(json.contains("test-rule"));
        assert!(json.contains("*.example.com/*"));
    }
}
