//! Condition evaluation for collection requests

use anyhow::Result;
use serde_json::Value;
use std::collections::HashMap;

/// Evaluates conditions for request execution
pub struct ConditionEvaluator;

impl ConditionEvaluator {
    /// Evaluate a condition expression
    pub fn evaluate(expression: &str, context: &HashMap<String, Value>) -> Result<bool> {
        // Implement a proper expression parser with operator precedence
        // Precedence: || < && < ==,!=

        let expr = expression.trim();

        // Handle simple boolean values
        if expr == "true" {
            return Ok(true);
        }
        if expr == "false" {
            return Ok(false);
        }

        // Parse OR operations first (lowest precedence)
        if let Some(or_pos) = Self::find_operator(expr, "||") {
            let left = &expr[..or_pos];
            let right = &expr[or_pos + 2..];
            let left_result = Self::evaluate(left.trim(), context)?;
            let right_result = Self::evaluate(right.trim(), context)?;
            return Ok(left_result || right_result);
        }

        // Parse AND operations (medium precedence)
        if let Some(and_pos) = Self::find_operator(expr, "&&") {
            let left = &expr[..and_pos];
            let right = &expr[and_pos + 2..];
            let left_result = Self::evaluate(left.trim(), context)?;
            let right_result = Self::evaluate(right.trim(), context)?;
            return Ok(left_result && right_result);
        }

        // Parse equality/inequality (highest precedence)
        if let Some(eq_pos) = Self::find_operator(expr, "==") {
            let left = &expr[..eq_pos];
            let right = &expr[eq_pos + 2..];
            let left_val = Self::resolve_value(left.trim(), context)?;
            let right_val = Self::resolve_value(right.trim(), context)?;
            return Ok(left_val == right_val);
        }

        if let Some(ne_pos) = Self::find_operator(expr, "!=") {
            let left = &expr[..ne_pos];
            let right = &expr[ne_pos + 2..];
            let left_val = Self::resolve_value(left.trim(), context)?;
            let right_val = Self::resolve_value(right.trim(), context)?;
            return Ok(left_val != right_val);
        }

        // Try to resolve as a boolean value
        let value = Self::resolve_value(expr, context)?;
        match value {
            Value::Bool(b) => Ok(b),
            Value::Null => Ok(false),
            Value::Number(n) => Ok(n.as_i64().unwrap_or(0) != 0),
            Value::String(s) => Ok(!s.is_empty()),
            _ => Ok(true), // Objects and arrays are truthy
        }
    }

    /// Find the position of an operator in an expression, respecting parentheses
    fn find_operator(expr: &str, op: &str) -> Option<usize> {
        let mut depth = 0;
        let mut in_string = false;
        let mut string_char = ' ';
        let bytes = expr.as_bytes();

        for i in 0..expr.len() {
            let ch = bytes[i] as char;

            // Handle string literals
            if ch == '"' || ch == '\'' {
                if !in_string {
                    in_string = true;
                    string_char = ch;
                } else if ch == string_char {
                    in_string = false;
                }
                continue;
            }

            if in_string {
                continue;
            }

            // Handle parentheses
            if ch == '(' {
                depth += 1;
                continue;
            }
            if ch == ')' {
                depth -= 1;
                continue;
            }

            // Only look for operators at depth 0
            if depth == 0 && expr[i..].starts_with(op) {
                return Some(i);
            }
        }

        None
    }

    /// Resolve a value from the context
    fn resolve_value(path: &str, context: &HashMap<String, Value>) -> Result<Value> {
        let path = path.trim();

        // Handle string literals
        if (path.starts_with('"') && path.ends_with('"'))
            || (path.starts_with('\'') && path.ends_with('\''))
        {
            return Ok(Value::String(path[1..path.len() - 1].to_string()));
        }

        // Handle number literals
        if let Ok(n) = path.parse::<i64>() {
            return Ok(Value::Number(n.into()));
        }
        if let Ok(n) = path.parse::<f64>() {
            return Ok(Value::Number(serde_json::Number::from_f64(n).unwrap()));
        }

        // Handle boolean literals
        if path == "true" {
            return Ok(Value::Bool(true));
        }
        if path == "false" {
            return Ok(Value::Bool(false));
        }

        // Handle null
        if path == "null" {
            return Ok(Value::Null);
        }

        // Remove {{ }} if present
        let path = if path.starts_with("{{") && path.ends_with("}}") {
            path[2..path.len() - 2].trim()
        } else {
            path
        };

        // Navigate through nested paths
        let parts: Vec<&str> = path.split('.').collect();
        let mut current = context.get(parts[0]).cloned().unwrap_or(Value::Null);

        for part in &parts[1..] {
            current = match current {
                Value::Object(map) => map.get(*part).cloned().unwrap_or(Value::Null),
                _ => Value::Null,
            };
        }

        Ok(current)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_simple_equality() {
        let context = HashMap::from([
            ("status".to_string(), json!(200)),
            ("success".to_string(), json!(true)),
        ]);

        assert!(ConditionEvaluator::evaluate("status == 200", &context).unwrap());
        assert!(!ConditionEvaluator::evaluate("status == 404", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("success == true", &context).unwrap());
    }

    #[test]
    fn test_nested_values() {
        let context = HashMap::from([(
            "response".to_string(),
            json!({
                "data": {
                    "enabled": true,
                    "count": 5
                }
            }),
        )]);

        assert!(ConditionEvaluator::evaluate("response.data.enabled == true", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("response.data.count == 5", &context).unwrap());
        assert!(!ConditionEvaluator::evaluate("response.data.count == 10", &context).unwrap());
    }

    #[test]
    fn test_boolean_operations() {
        let context = HashMap::from([
            ("a".to_string(), json!(true)),
            ("b".to_string(), json!(false)),
            ("c".to_string(), json!(true)),
        ]);

        assert!(ConditionEvaluator::evaluate("a == true && c == true", &context).unwrap());
        assert!(!ConditionEvaluator::evaluate("a == true && b == true", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("a == true || b == true", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("b == false || c == true", &context).unwrap());
    }

    #[test]
    fn test_string_comparisons() {
        let context = HashMap::from([
            ("env".to_string(), json!("production")),
            ("user".to_string(), json!("admin")),
        ]);

        assert!(ConditionEvaluator::evaluate("env == \"production\"", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("env != \"development\"", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("user == 'admin'", &context).unwrap());
    }

    #[test]
    fn test_null_handling() {
        let context = HashMap::from([
            ("value".to_string(), json!(null)),
            ("missing".to_string(), json!({})),
        ]);

        assert!(!ConditionEvaluator::evaluate("value", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("value == null", &context).unwrap());
        assert!(!ConditionEvaluator::evaluate("nonexistent", &context).unwrap());
        assert!(ConditionEvaluator::evaluate("missing.field == null", &context).unwrap());
    }
}
