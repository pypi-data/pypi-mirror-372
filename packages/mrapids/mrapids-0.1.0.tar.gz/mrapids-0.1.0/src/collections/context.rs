//! Execution context for collections (variables, saved responses, etc.)

use anyhow::{Context, Result};
use handlebars::Handlebars;
use serde_json::Value;
use std::collections::HashMap;

/// Execution context that tracks variables and saved responses
#[derive(Debug, Clone)]
pub struct ExecutionContext {
    /// User-defined variables
    pub variables: HashMap<String, Value>,

    /// Saved responses from previous requests
    pub saved_responses: HashMap<String, Value>,

    /// Environment variables (if enabled)
    pub environment: HashMap<String, String>,

    /// Handlebars template engine
    handlebars: Handlebars<'static>,
}

impl ExecutionContext {
    /// Create a new execution context
    pub fn new() -> Self {
        Self {
            variables: HashMap::new(),
            saved_responses: HashMap::new(),
            environment: HashMap::new(),
            handlebars: Handlebars::new(),
        }
    }

    /// Create context with initial variables
    pub fn with_variables(variables: HashMap<String, Value>) -> Self {
        let mut ctx = Self::new();
        ctx.variables = variables;
        ctx
    }

    /// Add or update a variable
    pub fn set_variable(&mut self, key: String, value: Value) {
        self.variables.insert(key, value);
    }

    /// Save a response for later use
    pub fn save_response(&mut self, key: String, response: Value) {
        self.saved_responses.insert(key, response);
    }

    /// Load environment variables
    pub fn load_environment(&mut self) {
        // First try to load from .env file if it exists
        if let Ok(_) = dotenv::dotenv() {
            // .env file loaded successfully
        }

        // Load environment variables with COLLECTION_ prefix
        for (key, value) in std::env::vars() {
            if key.starts_with("COLLECTION_") {
                let var_name = key.strip_prefix("COLLECTION_").unwrap();
                self.environment.insert(var_name.to_string(), value);
            }
        }
    }

    /// Load environment variables from a specific .env file
    pub fn load_env_file(&mut self, path: &std::path::Path) -> Result<()> {
        // Read the .env file directly to capture all variables
        let env_contents = std::fs::read_to_string(path)
            .with_context(|| format!("Failed to read .env file from {:?}", path))?;

        // Parse each line for KEY=VALUE pairs
        for line in env_contents.lines() {
            let line = line.trim();
            // Skip empty lines and comments
            if line.is_empty() || line.starts_with('#') {
                continue;
            }

            // Parse KEY=VALUE
            if let Some((key, value)) = line.split_once('=') {
                let key = key.trim();
                let value = value
                    .trim()
                    .trim_matches('"') // Remove surrounding quotes if any
                    .trim_matches('\'');

                self.environment.insert(key.to_string(), value.to_string());
            }
        }

        Ok(())
    }

    /// Resolve variables in a string template
    pub fn resolve_string(&self, template: &str) -> Result<String> {
        if !template.contains("{{") {
            return Ok(template.to_string());
        }

        // Build context for handlebars
        let mut context = serde_json::Map::new();

        // Add in order of precedence (lowest to highest)
        // 1. Environment variables (lowest)
        for (k, v) in &self.environment {
            context.insert(k.clone(), Value::String(v.clone()));
        }

        // 2. Regular variables (includes collection vars and CLI overrides)
        for (k, v) in &self.variables {
            context.insert(k.clone(), v.clone());
        }

        // 3. Saved responses (highest - always override)
        for (k, v) in &self.saved_responses {
            context.insert(k.clone(), v.clone());
        }

        self.handlebars
            .render_template(template, &context)
            .with_context(|| format!("Failed to resolve template: {}", template))
    }

    /// Resolve variables in a JSON value
    pub fn resolve_value(&self, value: &Value) -> Result<Value> {
        match value {
            Value::String(s) => {
                let resolved = self.resolve_string(s)?;
                // Try to parse as JSON if it looks like JSON
                if (resolved.starts_with('{') || resolved.starts_with('['))
                    && (resolved.ends_with('}') || resolved.ends_with(']'))
                {
                    if let Ok(parsed) = serde_json::from_str(&resolved) {
                        return Ok(parsed);
                    }
                }
                Ok(Value::String(resolved))
            }
            Value::Object(map) => {
                let mut resolved = serde_json::Map::new();
                for (k, v) in map {
                    resolved.insert(k.clone(), self.resolve_value(v)?);
                }
                Ok(Value::Object(resolved))
            }
            Value::Array(arr) => {
                let mut resolved = Vec::new();
                for v in arr {
                    resolved.push(self.resolve_value(v)?);
                }
                Ok(Value::Array(resolved))
            }
            _ => Ok(value.clone()),
        }
    }

    /// Resolve variables in a HashMap
    pub fn resolve_params(
        &self,
        params: &HashMap<String, Value>,
    ) -> Result<HashMap<String, Value>> {
        let mut resolved = HashMap::new();
        for (k, v) in params {
            resolved.insert(k.clone(), self.resolve_value(v)?);
        }
        Ok(resolved)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn test_simple_variable_resolution() {
        let mut ctx = ExecutionContext::new();
        ctx.set_variable("username".to_string(), json!("octocat"));

        let result = ctx.resolve_string("Hello {{username}}!").unwrap();
        assert_eq!(result, "Hello octocat!");
    }

    #[test]
    fn test_nested_variable_resolution() {
        let mut ctx = ExecutionContext::new();
        ctx.set_variable(
            "user".to_string(),
            json!({
                "name": "octocat",
                "id": 123
            }),
        );

        let result = ctx
            .resolve_string("User: {{user.name}} (ID: {{user.id}})")
            .unwrap();
        assert_eq!(result, "User: octocat (ID: 123)");
    }

    #[test]
    fn test_saved_response_resolution() {
        let mut ctx = ExecutionContext::new();
        ctx.save_response(
            "user_response".to_string(),
            json!({
                "id": 456,
                "login": "defunkt"
            }),
        );

        let result = ctx.resolve_string("{{user_response.login}}").unwrap();
        assert_eq!(result, "defunkt");
    }

    #[test]
    fn test_resolve_params() {
        let mut ctx = ExecutionContext::new();
        ctx.set_variable("org".to_string(), json!("github"));

        let params = HashMap::from([
            ("owner".to_string(), json!("{{org}}")),
            ("repo".to_string(), json!("docs")),
        ]);

        let resolved = ctx.resolve_params(&params).unwrap();
        assert_eq!(resolved["owner"], json!("github"));
        assert_eq!(resolved["repo"], json!("docs"));
    }
}
