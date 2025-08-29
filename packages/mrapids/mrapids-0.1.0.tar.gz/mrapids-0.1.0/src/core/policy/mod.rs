//! Policy engine for agent access control
//!
//! This module provides policy-based access control for API operations,
//! ensuring agents can only perform allowed actions.

#![allow(unused_imports)]

pub mod engine;
pub mod explain;
pub mod model;
pub mod parser;
pub mod testing;

// Re-export key types
pub use engine::{EvaluationContext, PolicyDecision, PolicyEngine};
pub use explain::{explain_decision, generate_policy_report, PolicyExplanation};
pub use model::{PolicyAction, PolicyCondition, PolicyDefaults, PolicyRule, PolicySet};
pub use parser::{load_policy_from_file, parse_toml_policy, parse_yaml_policy, validate_policy};
pub use testing::{
    generate_test_report, load_test_scenarios, PolicyTestRunner, PolicyTestScenario,
};
