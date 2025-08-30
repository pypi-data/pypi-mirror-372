use crate::utils::security::{enforce_https, validate_file_path};
use anyhow::Result;
use serde_json::Value;
use std::collections::HashMap;
use std::path::{Path, PathBuf};
use tokio::fs;

/// Load external OpenAPI documents referenced in the spec
pub struct ExternalRefLoader {
    base_path: PathBuf,
    cache: HashMap<String, Value>,
    allow_insecure: bool,
}

impl ExternalRefLoader {
    pub fn new(base_path: impl Into<PathBuf>, allow_insecure: bool) -> Self {
        Self {
            base_path: base_path.into(),
            cache: HashMap::new(),
            allow_insecure,
        }
    }

    /// Load an external reference (file or HTTP)
    pub async fn load_reference(&mut self, reference: &str) -> Result<Value> {
        // Check cache first
        if let Some(cached) = self.cache.get(reference) {
            return Ok(cached.clone());
        }

        let content = if reference.starts_with("http://") || reference.starts_with("https://") {
            // HTTP reference
            self.load_http_reference(reference).await?
        } else {
            // File reference
            self.load_file_reference(reference).await?
        };

        // Parse the content
        let value: Value = if reference.ends_with(".yaml") || reference.ends_with(".yml") {
            let yaml_value: serde_yaml::Value = serde_yaml::from_str(&content)?;
            serde_json::to_value(yaml_value)?
        } else {
            serde_json::from_str(&content)?
        };

        // Cache the result
        self.cache.insert(reference.to_string(), value.clone());
        Ok(value)
    }

    /// Load a file reference relative to the base path
    async fn load_file_reference(&self, reference: &str) -> Result<String> {
        let path = if reference.starts_with("./") || reference.starts_with("../") {
            // Relative path
            self.base_path.join(reference)
        } else {
            // Absolute path
            PathBuf::from(reference)
        };

        // Validate file path for security
        validate_file_path(&path).map_err(|e| {
            anyhow::anyhow!(
                "Security validation failed for file path '{}': {}",
                path.display(),
                e
            )
        })?;

        let content = fs::read_to_string(&path).await.map_err(|e| {
            anyhow::anyhow!("Failed to read external file '{}': {}", path.display(), e)
        })?;

        Ok(content)
    }

    /// Load an HTTP reference
    async fn load_http_reference(&self, url: &str) -> Result<String> {
        // Validate URL for security and enforce HTTPS
        enforce_https(url, self.allow_insecure)
            .map_err(|e| anyhow::anyhow!("Security validation failed for URL '{}': {}", url, e))?;

        let response = reqwest::get(url)
            .await
            .map_err(|e| anyhow::anyhow!("Failed to fetch external URL '{}': {}", url, e))?;

        if !response.status().is_success() {
            return Err(anyhow::anyhow!(
                "Failed to fetch external URL '{}': HTTP {}",
                url,
                response.status()
            ));
        }

        let content = response
            .text()
            .await
            .map_err(|e| anyhow::anyhow!("Failed to read response from '{}': {}", url, e))?;

        Ok(content)
    }

    /// Scan a spec for external references and preload them
    pub async fn preload_external_refs(&mut self, spec: &Value) -> Result<()> {
        let refs = find_all_external_refs(spec);

        for reference in refs {
            if let Some(file_part) = reference.split('#').next() {
                if !file_part.is_empty() && file_part != "" {
                    if let Err(e) = self.load_reference(file_part).await {
                        eprintln!(
                            "Warning: Failed to preload external reference '{}': {}",
                            file_part, e
                        );
                    }
                }
            }
        }

        Ok(())
    }
}

/// Find all external $ref values in a JSON value
fn find_all_external_refs(value: &Value) -> Vec<String> {
    let mut refs = Vec::new();
    find_refs_recursive(value, &mut refs);
    refs
}

fn find_refs_recursive(value: &Value, refs: &mut Vec<String>) {
    match value {
        Value::Object(map) => {
            // Check if this object has a $ref
            if let Some(Value::String(ref_str)) = map.get("$ref") {
                if !ref_str.starts_with("#/") {
                    // External reference
                    refs.push(ref_str.clone());
                }
            }

            // Recurse into all values
            for (_, v) in map {
                find_refs_recursive(v, refs);
            }
        }
        Value::Array(arr) => {
            for v in arr {
                find_refs_recursive(v, refs);
            }
        }
        _ => {}
    }
}

/// Flatten all references in a spec (inline all $refs)
pub async fn flatten_spec(spec: &mut Value, base_path: &Path, allow_insecure: bool) -> Result<()> {
    let mut loader = ExternalRefLoader::new(base_path, allow_insecure);

    // First, preload all external references
    loader.preload_external_refs(spec).await?;

    // Then flatten all references
    flatten_refs_recursive(spec, &mut loader, &mut Vec::new()).await?;

    Ok(())
}

fn flatten_refs_recursive<'a>(
    value: &'a mut Value,
    loader: &'a mut ExternalRefLoader,
    stack: &'a mut Vec<String>,
) -> std::pin::Pin<Box<dyn std::future::Future<Output = Result<()>> + 'a>> {
    Box::pin(async move {
        match value {
            Value::Object(map) => {
                // Check if this object has a $ref
                if let Some(Value::String(ref_str)) = map.get("$ref").cloned() {
                    // Check for circular reference
                    if stack.contains(&ref_str) {
                        // Keep the $ref but add a warning comment
                        map.insert("x-circular-ref".to_string(), Value::Bool(true));
                        return Ok(());
                    }

                    stack.push(ref_str.clone());

                    // Resolve the reference
                    let resolved = if ref_str.starts_with("#/") {
                        // Internal reference - would need access to root spec
                        // For now, keep as-is
                        None
                    } else {
                        // External reference
                        if let Some((file_part, fragment)) = ref_str.split_once('#') {
                            if let Ok(external_doc) = loader.load_reference(file_part).await {
                                // Navigate to the fragment
                                let path_parts: Vec<&str> =
                                    fragment.trim_start_matches('/').split('/').collect();
                                let mut current = &external_doc;

                                for part in path_parts {
                                    if let Some(next) = current.get(part) {
                                        current = next;
                                    } else {
                                        eprintln!("Warning: Path '{}' not found in external document '{}'", fragment, file_part);
                                        break;
                                    }
                                }

                                Some(current.clone())
                            } else {
                                None
                            }
                        } else {
                            None
                        }
                    };

                    if let Some(mut resolved_value) = resolved {
                        // Recursively flatten the resolved value
                        flatten_refs_recursive(&mut resolved_value, loader, stack).await?;

                        // Replace the current object with the resolved value
                        *value = resolved_value;
                    }

                    stack.pop();
                } else {
                    // Recurse into all values
                    let keys: Vec<String> = map.keys().cloned().collect();
                    for key in keys {
                        if let Some(v) = map.get_mut(&key) {
                            flatten_refs_recursive(v, loader, stack).await?;
                        }
                    }
                }
            }
            Value::Array(arr) => {
                for v in arr {
                    flatten_refs_recursive(v, loader, stack).await?;
                }
            }
            _ => {}
        }

        Ok(())
    })
}
