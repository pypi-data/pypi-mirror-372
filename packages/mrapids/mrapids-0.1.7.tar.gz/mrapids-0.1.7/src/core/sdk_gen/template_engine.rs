use anyhow::Result;
use handlebars::Handlebars;
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};

/// Template engine for generating SDKs
pub struct TemplateEngine {
    handlebars: Handlebars<'static>,
    templates_dir: PathBuf,
}

impl TemplateEngine {
    pub fn new(templates_dir: PathBuf) -> Result<Self> {
        let mut handlebars = Handlebars::new();

        // Register helpers
        handlebars.register_helper("camelCase", Box::new(camel_case_helper));
        handlebars.register_helper("pascalCase", Box::new(pascal_case_helper));
        handlebars.register_helper("snakeCase", Box::new(snake_case_helper));
        handlebars.register_helper("kebabCase", Box::new(kebab_case_helper));

        Ok(Self {
            handlebars,
            templates_dir,
        })
    }

    pub fn render_template(&mut self, template_name: &str, context: &Value) -> Result<String> {
        let template_path = self.templates_dir.join(template_name);
        let template_content = fs::read_to_string(&template_path)?;

        // Register the template
        self.handlebars
            .register_template_string(template_name, template_content)?;

        // Render
        let rendered = self.handlebars.render(template_name, context)?;
        Ok(rendered)
    }

    pub fn render_to_file(
        &mut self,
        template_name: &str,
        context: &Value,
        output_path: &Path,
    ) -> Result<()> {
        let rendered = self.render_template(template_name, context)?;

        // Create parent directories
        if let Some(parent) = output_path.parent() {
            fs::create_dir_all(parent)?;
        }

        fs::write(output_path, rendered)?;
        Ok(())
    }
}

// Helper functions for case conversion
fn camel_case_helper(
    h: &handlebars::Helper,
    _: &Handlebars,
    _: &handlebars::Context,
    _: &mut handlebars::RenderContext,
    out: &mut dyn handlebars::Output,
) -> handlebars::HelperResult {
    let value = h.param(0).and_then(|v| v.value().as_str()).ok_or_else(|| {
        handlebars::RenderErrorReason::Other(
            "camelCase helper requires a string parameter".to_string(),
        )
    })?;

    let camel_case = to_camel_case(value);
    out.write(&camel_case)?;
    Ok(())
}

fn pascal_case_helper(
    h: &handlebars::Helper,
    _: &Handlebars,
    _: &handlebars::Context,
    _: &mut handlebars::RenderContext,
    out: &mut dyn handlebars::Output,
) -> handlebars::HelperResult {
    let value = h.param(0).and_then(|v| v.value().as_str()).ok_or_else(|| {
        handlebars::RenderErrorReason::Other(
            "pascalCase helper requires a string parameter".to_string(),
        )
    })?;

    let pascal_case = to_pascal_case(value);
    out.write(&pascal_case)?;
    Ok(())
}

fn snake_case_helper(
    h: &handlebars::Helper,
    _: &Handlebars,
    _: &handlebars::Context,
    _: &mut handlebars::RenderContext,
    out: &mut dyn handlebars::Output,
) -> handlebars::HelperResult {
    let value = h.param(0).and_then(|v| v.value().as_str()).ok_or_else(|| {
        handlebars::RenderErrorReason::Other(
            "snakeCase helper requires a string parameter".to_string(),
        )
    })?;

    let snake_case = to_snake_case(value);
    out.write(&snake_case)?;
    Ok(())
}

fn kebab_case_helper(
    h: &handlebars::Helper,
    _: &Handlebars,
    _: &handlebars::Context,
    _: &mut handlebars::RenderContext,
    out: &mut dyn handlebars::Output,
) -> handlebars::HelperResult {
    let value = h.param(0).and_then(|v| v.value().as_str()).ok_or_else(|| {
        handlebars::RenderErrorReason::Other(
            "kebabCase helper requires a string parameter".to_string(),
        )
    })?;

    let kebab_case = to_kebab_case(value);
    out.write(&kebab_case)?;
    Ok(())
}

// Case conversion utilities
fn to_camel_case(s: &str) -> String {
    let pascal = to_pascal_case(s);
    if pascal.is_empty() {
        return pascal;
    }

    let mut chars = pascal.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_lowercase().collect::<String>() + chars.as_str(),
    }
}

fn to_pascal_case(s: &str) -> String {
    s.split(|c: char| !c.is_alphanumeric())
        .filter(|s| !s.is_empty())
        .map(|word| {
            let mut chars = word.chars();
            match chars.next() {
                None => String::new(),
                Some(first) => {
                    first.to_uppercase().collect::<String>() + &chars.as_str().to_lowercase()
                }
            }
        })
        .collect()
}

fn to_snake_case(s: &str) -> String {
    let mut result = String::new();
    let mut prev_was_upper = false;

    for (i, c) in s.chars().enumerate() {
        if c.is_uppercase() {
            if i > 0 && !prev_was_upper {
                result.push('_');
            }
            result.push(c.to_lowercase().next().unwrap());
            prev_was_upper = true;
        } else if c.is_alphanumeric() {
            result.push(c);
            prev_was_upper = false;
        } else if !result.is_empty() && !result.ends_with('_') {
            result.push('_');
            prev_was_upper = false;
        }
    }

    result.trim_end_matches('_').to_string()
}

fn to_kebab_case(s: &str) -> String {
    to_snake_case(s).replace('_', "-")
}
