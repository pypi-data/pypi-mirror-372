//! Policy parser for YAML and TOML formats

#![allow(dead_code)]

use super::model::*;
use anyhow::{Context, Result};
use std::fs;
use std::path::Path;

/// Load a policy from a file (supports YAML and TOML)
pub fn load_policy_from_file<P: AsRef<Path>>(path: P) -> Result<PolicySet> {
    let path = path.as_ref();
    let content = fs::read_to_string(path)
        .with_context(|| format!("Failed to read policy file: {}", path.display()))?;

    let extension = path.extension().and_then(|ext| ext.to_str()).unwrap_or("");

    match extension {
        "yaml" | "yml" => parse_yaml_policy(&content),
        "toml" => parse_toml_policy(&content),
        _ => {
            // Try to auto-detect format
            if content.contains("version:") || content.contains("version =") {
                if content.contains("[[") || content.contains("[defaults]") {
                    parse_toml_policy(&content)
                } else {
                    parse_yaml_policy(&content)
                }
            } else {
                anyhow::bail!("Unknown policy file format. Use .yaml, .yml, or .toml extension")
            }
        }
    }
}

/// Parse a YAML policy
pub fn parse_yaml_policy(content: &str) -> Result<PolicySet> {
    serde_yaml::from_str(content).context("Failed to parse YAML policy")
}

/// Parse a TOML policy
pub fn parse_toml_policy(content: &str) -> Result<PolicySet> {
    toml::from_str(content).context("Failed to parse TOML policy")
}

/// Validate a policy set
pub fn validate_policy(policy: &PolicySet) -> Result<()> {
    // Check version
    if policy.version.is_empty() {
        anyhow::bail!("Policy version is required");
    }

    // Check for duplicate rule names
    let mut rule_names = std::collections::HashSet::new();
    for rule in &policy.rules {
        if !rule_names.insert(&rule.name) {
            anyhow::bail!("Duplicate rule name: {}", rule.name);
        }
    }

    // Validate each rule
    for rule in &policy.rules {
        validate_rule(rule)?;
    }

    Ok(())
}

/// Validate a single rule
fn validate_rule(rule: &PolicyRule) -> Result<()> {
    // Check pattern is valid glob
    glob::Pattern::new(&rule.pattern)
        .with_context(|| format!("Invalid pattern in rule '{}': {}", rule.name, rule.pattern))?;

    // Check that at least one of allow or deny is specified
    if rule.allow.is_none() && rule.deny.is_none() {
        anyhow::bail!(
            "Rule '{}' must specify either 'allow' or 'deny' actions",
            rule.name
        );
    }

    // Validate actions
    if let Some(allow) = &rule.allow {
        validate_action(allow, &rule.name, "allow")?;
    }

    if let Some(deny) = &rule.deny {
        validate_action(deny, &rule.name, "deny")?;
    }

    Ok(())
}

/// Validate an action
fn validate_action(action: &PolicyAction, rule_name: &str, action_type: &str) -> Result<()> {
    // Check that at least one field is specified
    if action.operations.is_none()
        && action.methods.is_none()
        && action.all.is_none()
        && action.tags.is_none()
    {
        anyhow::bail!(
            "Rule '{}' {} action must specify at least one of: operations, methods, all, or tags",
            rule_name,
            action_type
        );
    }

    // Validate operation patterns
    if let Some(operations) = &action.operations {
        for op in operations {
            // Try to compile as glob pattern
            if op.contains('*') || op.contains('?') || op.contains('[') {
                glob::Pattern::new(op).with_context(|| {
                    format!("Invalid operation pattern '{}' in rule '{}'", op, rule_name)
                })?;
            }
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    const VALID_YAML_POLICY: &str = r#"
version: "1.0"
metadata:
  name: "test-policy"
  description: "Test policy for unit tests"

defaults:
  allow_methods: ["GET", "HEAD"]
  deny_external_refs: true
  require_auth: true
  audit_level: "basic"

rules:
  - name: "readonly"
    description: "Allow read-only operations"
    pattern: "*"
    allow:
      methods: ["GET"]
      operations: ["get*", "list*"]
"#;

    const VALID_TOML_POLICY: &str = r#"
version = "1.0"

[metadata]
name = "test-policy"
description = "Test policy for unit tests"

[defaults]
allow_methods = ["GET", "HEAD"]
deny_external_refs = true
require_auth = true
audit_level = "basic"

[[rules]]
name = "readonly"
description = "Allow read-only operations"
pattern = "*"

[rules.allow]
methods = ["GET"]
operations = ["get*", "list*"]
"#;

    #[test]
    fn test_parse_yaml_policy() {
        let policy = parse_yaml_policy(VALID_YAML_POLICY).unwrap();
        assert_eq!(policy.version, "1.0");
        assert_eq!(policy.rules.len(), 1);
        assert_eq!(policy.rules[0].name, "readonly");
    }

    #[test]
    fn test_parse_toml_policy() {
        let policy = parse_toml_policy(VALID_TOML_POLICY).unwrap();
        assert_eq!(policy.version, "1.0");
        assert_eq!(policy.rules.len(), 1);
        assert_eq!(policy.rules[0].name, "readonly");
    }

    #[test]
    fn test_validate_valid_policy() {
        let policy = parse_yaml_policy(VALID_YAML_POLICY).unwrap();
        assert!(validate_policy(&policy).is_ok());
    }

    #[test]
    fn test_validate_duplicate_rule_names() {
        let mut policy = parse_yaml_policy(VALID_YAML_POLICY).unwrap();
        policy.rules.push(policy.rules[0].clone());

        let result = validate_policy(&policy);
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("Duplicate rule name"));
    }

    #[test]
    fn test_validate_invalid_pattern() {
        let mut policy = parse_yaml_policy(VALID_YAML_POLICY).unwrap();
        policy.rules[0].pattern = "[invalid".to_string();

        let result = validate_policy(&policy);
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Invalid pattern"));
    }
}
