// Smart API Exploration - Help users find operations quickly
// Searches across operation names, descriptions, paths, and tags

use crate::cli::{ExploreCommand, ExploreFormat};
use crate::core::parser::{parse_spec, UnifiedOperation, UnifiedSpec};
use anyhow::Result;
use colored::*;
use std::collections::HashMap;
use std::path::{Path, PathBuf};

pub fn explore_command(cmd: ExploreCommand) -> Result<()> {
    // Determine spec file path
    let spec_path = cmd.spec.unwrap_or_else(|| {
        // Try common locations
        if Path::new("specs/api.yaml").exists() {
            PathBuf::from("specs/api.yaml")
        } else if Path::new("specs/api.yml").exists() {
            PathBuf::from("specs/api.yml")
        } else if Path::new("specs/api.json").exists() {
            PathBuf::from("specs/api.json")
        } else if Path::new("api.yaml").exists() {
            PathBuf::from("api.yaml")
        } else {
            PathBuf::from("openapi.yaml")
        }
    });

    // Explore operations
    let results = explore_operations(&spec_path, &cmd.keyword)?;

    // Display results based on format
    match cmd.format {
        ExploreFormat::Pretty => {
            display_explore_results(&results, &cmd.keyword, cmd.limit);
        }
        ExploreFormat::Simple => {
            display_simple_results(&results, &cmd.keyword);
        }
        ExploreFormat::Json => {
            display_json_results(&results)?;
        }
    }

    Ok(())
}

pub struct ExploreResult {
    pub operation: UnifiedOperation,
    pub relevance_score: f32,
    pub matched_fields: Vec<String>,
}

pub fn explore_operations(
    spec_path: &std::path::Path,
    keyword: &str,
) -> Result<Vec<ExploreResult>> {
    // Load and parse the spec
    let spec_content = std::fs::read_to_string(spec_path)?;
    let spec = parse_spec(&spec_content)?;

    // Search operations
    let results = search_operations(&spec, keyword);

    Ok(results)
}

fn search_operations(spec: &UnifiedSpec, keyword: &str) -> Vec<ExploreResult> {
    let keyword_lower = keyword.to_lowercase();
    let mut results = Vec::new();

    for operation in &spec.operations {
        let mut score = 0.0;
        let mut matched_fields = Vec::new();

        // Check operation ID (highest weight)
        if operation
            .operation_id
            .to_lowercase()
            .contains(&keyword_lower)
        {
            score += 3.0;
            matched_fields.push("operation_id".to_string());
        }

        // Check path (high weight)
        if operation.path.to_lowercase().contains(&keyword_lower) {
            score += 2.5;
            matched_fields.push("path".to_string());
        }

        // Check method
        if operation.method.to_lowercase().contains(&keyword_lower) {
            score += 1.5;
            matched_fields.push("method".to_string());
        }

        // Check summary
        if let Some(summary) = &operation.summary {
            if summary.to_lowercase().contains(&keyword_lower) {
                score += 2.0;
                matched_fields.push("summary".to_string());
            }
        }

        // Check description
        if let Some(desc) = &operation.description {
            if desc.to_lowercase().contains(&keyword_lower) {
                score += 1.0;
                matched_fields.push("description".to_string());
            }
        }

        // Check parameters
        for param in &operation.parameters {
            if param.name.to_lowercase().contains(&keyword_lower) {
                score += 0.5;
                matched_fields.push(format!("parameter:{}", param.name));
            }
        }

        // If we have any matches, add to results
        if score > 0.0 {
            results.push(ExploreResult {
                operation: operation.clone(),
                relevance_score: score,
                matched_fields,
            });
        }
    }

    // Sort by relevance score (highest first)
    results.sort_by(|a, b| b.relevance_score.partial_cmp(&a.relevance_score).unwrap());

    results
}

pub fn display_explore_results(results: &[ExploreResult], keyword: &str, limit: usize) {
    if results.is_empty() {
        println!("❌ No operations found matching '{}'", keyword.red());
        return;
    }

    println!(
        "\n🔍 Found {} operations matching '{}':\n",
        results.len().to_string().green(),
        keyword.cyan()
    );

    // Group by similarity/category if possible
    let grouped = group_by_category(results);

    for (category, ops) in grouped {
        if !category.is_empty() {
            println!("{}", format!("📁 {}", category).bright_blue().bold());
        }

        for (idx, result) in ops.iter().take(limit).enumerate() {
            display_single_result(idx + 1, result, keyword);
        }

        if ops.len() > limit {
            println!("   ... and {} more in this category", ops.len() - limit);
        }
        println!();
    }

    // Show usage hint
    println!(
        "{}",
        "💡 Use 'mrapids show <operation>' to see details".dimmed()
    );
}

fn display_single_result(num: usize, result: &ExploreResult, keyword: &str) {
    let op = &result.operation;

    // Highlight the keyword in the output
    let highlighted_id = highlight_keyword(&op.operation_id, keyword);
    let highlighted_path = highlight_keyword(&op.path, keyword);

    println!(
        "  {} {} {}",
        format!("{}.", num).dimmed(),
        format!("{} {}", op.method.bright_green(), highlighted_path).bold(),
        format!("[{}]", highlighted_id).bright_cyan()
    );

    // Show summary if it contains the keyword
    if let Some(summary) = &op.summary {
        if summary.to_lowercase().contains(&keyword.to_lowercase()) {
            let highlighted_summary = highlight_keyword(summary, keyword);
            println!("     {}", highlighted_summary.dimmed());
        } else {
            // Show truncated summary
            let truncated = if summary.len() > 60 {
                format!("{}...", &summary[..60])
            } else {
                summary.clone()
            };
            println!("     {}", truncated.dimmed());
        }
    }

    // Show what matched
    println!(
        "     {} {}",
        "Matched:".bright_black(),
        result.matched_fields.join(", ").bright_black()
    );
}

fn highlight_keyword(text: &str, keyword: &str) -> String {
    // Case-insensitive highlighting
    let lower_text = text.to_lowercase();
    let lower_keyword = keyword.to_lowercase();

    if let Some(pos) = lower_text.find(&lower_keyword) {
        let (before, rest) = text.split_at(pos);
        let (matched, after) = rest.split_at(keyword.len());
        format!("{}{}{}", before, matched.bright_yellow().bold(), after)
    } else {
        text.to_string()
    }
}

fn group_by_category(results: &[ExploreResult]) -> Vec<(String, Vec<&ExploreResult>)> {
    let mut groups: HashMap<String, Vec<&ExploreResult>> = HashMap::new();

    for result in results {
        let category = extract_category(&result.operation);
        groups.entry(category).or_insert_with(Vec::new).push(result);
    }

    // Sort groups by total relevance
    let mut sorted_groups: Vec<_> = groups.into_iter().collect();
    sorted_groups.sort_by(|a, b| {
        let a_score: f32 = a.1.iter().map(|r| r.relevance_score).sum();
        let b_score: f32 = b.1.iter().map(|r| r.relevance_score).sum();
        b_score.partial_cmp(&a_score).unwrap()
    });

    sorted_groups
}

fn extract_category(operation: &UnifiedOperation) -> String {
    // Extract category from path or operation ID
    // Examples: /users/{id} -> Users, /products/{id}/reviews -> Products

    let path_parts: Vec<&str> = operation
        .path
        .split('/')
        .filter(|s| !s.is_empty())
        .collect();

    if let Some(first_part) = path_parts.first() {
        // Skip if it's a parameter
        if !first_part.starts_with('{') {
            return capitalize_first(first_part);
        }
    }

    // Try to extract from operation ID
    // getPetById -> Pet, createUser -> User
    let op_id_lower = operation.operation_id.to_lowercase();

    let categories = [
        "user", "pet", "order", "product", "payment", "customer", "account",
    ];
    for cat in &categories {
        if op_id_lower.contains(cat) {
            return capitalize_first(cat);
        }
    }

    "General".to_string()
}

fn capitalize_first(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().chain(chars).collect(),
    }
}

fn display_simple_results(results: &[ExploreResult], keyword: &str) {
    if results.is_empty() {
        println!("No operations found matching '{}'", keyword);
        return;
    }

    for result in results {
        let op = &result.operation;
        println!("{} {} [{}]", op.method, op.path, op.operation_id);
    }
}

fn display_json_results(results: &[ExploreResult]) -> Result<()> {
    let json_results: Vec<_> = results
        .iter()
        .map(|r| {
            serde_json::json!({
                "operation_id": r.operation.operation_id,
                "method": r.operation.method,
                "path": r.operation.path,
                "summary": r.operation.summary,
                "relevance_score": r.relevance_score,
                "matched_fields": r.matched_fields,
            })
        })
        .collect();

    println!("{}", serde_json::to_string_pretty(&json_results)?);
    Ok(())
}
