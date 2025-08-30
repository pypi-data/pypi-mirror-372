use crate::core::parser::{SchemaType, UnifiedSchema, UnifiedSpec};
use anyhow::Result;
use colored::*;
use rand::rngs::StdRng;
use rand::{Rng, SeedableRng};
use serde_json::{json, Value};
use std::fs;
use std::path::Path;

#[derive(Debug, Clone, Copy)]
#[allow(dead_code)]
pub enum FixtureVariant {
    Valid,
    EdgeCases,
    Invalid,
}

impl std::fmt::Display for FixtureVariant {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            FixtureVariant::Valid => write!(f, "valid"),
            FixtureVariant::EdgeCases => write!(f, "edge-cases"),
            FixtureVariant::Invalid => write!(f, "invalid"),
        }
    }
}

#[derive(Debug, Clone, Copy)]
#[allow(dead_code)]
pub enum FixtureFormat {
    Json,
    Yaml,
    Csv,
    Sql,
}

impl FixtureFormat {
    pub fn extension(&self) -> &'static str {
        match self {
            FixtureFormat::Json => "json",
            FixtureFormat::Yaml => "yaml",
            FixtureFormat::Csv => "csv",
            FixtureFormat::Sql => "sql",
        }
    }
}

pub fn generate_fixtures(
    spec: &UnifiedSpec,
    output_dir: &Path,
    count: u32,
    schemas: Vec<String>,
    seed: Option<u64>,
    format: FixtureFormat,
    variant: FixtureVariant,
) -> Result<()> {
    println!("🎲 {} Test Fixtures Generation", "MicroRapid".bright_cyan());

    // Create output directory
    fs::create_dir_all(output_dir)?;

    // Initialize random generator
    let mut rng = if let Some(seed) = seed {
        println!("🌱 Using seed: {}", seed);
        StdRng::seed_from_u64(seed)
    } else {
        StdRng::from_entropy()
    };

    // For now, generate fixtures based on operations' request bodies
    // In a full implementation, we would extract schemas from components
    let mut generated_count = 0;

    for operation in &spec.operations {
        // Skip if specific schemas requested and this doesn't match
        if !schemas.is_empty() {
            let op_name = operation.operation_id.to_lowercase();
            if !schemas.iter().any(|s| op_name.contains(&s.to_lowercase())) {
                continue;
            }
        }

        if let Some(request_body) = &operation.request_body {
            if let Some(media_type) = request_body.content.get("application/json") {
                let schema_name = operation.operation_id.clone();
                println!(
                    "📋 Generating fixtures for: {}",
                    schema_name.bright_yellow()
                );

                let fixtures = match variant {
                    FixtureVariant::Valid => {
                        generate_valid_fixtures(&media_type.schema, count, &mut rng)?
                    }
                    FixtureVariant::EdgeCases => generate_edge_case_fixtures(&media_type.schema)?,
                    FixtureVariant::Invalid => generate_invalid_fixtures(&media_type.schema)?,
                };

                // Write fixtures
                let filename = format!(
                    "{}-{}.{}",
                    to_kebab_case(&schema_name),
                    variant,
                    format.extension()
                );

                write_fixtures(&fixtures, &output_dir.join(filename), format)?;
                generated_count += 1;

                println!(
                    "  ✅ Generated {} {} fixtures",
                    fixtures.len(),
                    variant.to_string().bright_green()
                );
            }
        }
    }

    if generated_count == 0 {
        println!("⚠️  No schemas found to generate fixtures for");
        println!("💡 Tip: Fixtures are generated from request body schemas in operations");
    } else {
        println!("\n✅ Generated fixtures for {} schemas", generated_count);
    }

    Ok(())
}

fn generate_valid_fixtures(
    schema: &UnifiedSchema,
    count: u32,
    rng: &mut StdRng,
) -> Result<Vec<Value>> {
    let mut fixtures = Vec::new();

    for i in 0..count {
        let value = generate_value_from_schema(schema, rng, Some(i))?;
        fixtures.push(value);
    }

    Ok(fixtures)
}

fn generate_edge_case_fixtures(schema: &UnifiedSchema) -> Result<Vec<Value>> {
    let mut fixtures = Vec::new();
    let mut rng = StdRng::from_entropy();

    // Generate minimum values
    let min_value = generate_min_value(schema)?;
    fixtures.push(min_value);

    // Generate maximum values
    let max_value = generate_max_value(schema)?;
    fixtures.push(max_value);

    // Generate empty/minimal valid values
    let empty_value = generate_empty_value(schema)?;
    fixtures.push(empty_value);

    // Generate boundary values
    if let Some(boundary) = generate_boundary_value(schema, &mut rng)? {
        fixtures.push(boundary);
    }

    Ok(fixtures)
}

fn generate_invalid_fixtures(_schema: &UnifiedSchema) -> Result<Vec<Value>> {
    let fixtures = vec![
        // Wrong type
        json!({
            "_comment": "Invalid: wrong types",
            "string_field": 123,
            "number_field": "not a number",
            "boolean_field": "yes",
            "array_field": "not an array"
        }),
        // Missing required fields
        json!({
            "_comment": "Invalid: missing required fields"
        }),
        // Invalid formats
        json!({
            "_comment": "Invalid: bad formats",
            "email": "not-an-email",
            "date": "not-a-date",
            "uuid": "not-a-uuid"
        }),
        // Out of range
        json!({
            "_comment": "Invalid: out of range",
            "age": -1,
            "percentage": 150,
            "rating": 6
        }),
    ];

    Ok(fixtures)
}

fn generate_value_from_schema(
    schema: &UnifiedSchema,
    rng: &mut StdRng,
    index: Option<u32>,
) -> Result<Value> {
    match schema.schema_type {
        SchemaType::String => generate_string_value(schema, rng, index),
        SchemaType::Integer => generate_integer_value(schema, rng),
        SchemaType::Number => generate_number_value(schema, rng),
        SchemaType::Boolean => Ok(json!(rng.gen_bool(0.5))),
        SchemaType::Array => generate_array_value(schema, rng, index),
        SchemaType::Object => generate_object_value(schema, rng, index),
        SchemaType::Unknown => Ok(json!(null)),
    }
}

fn generate_string_value(
    schema: &UnifiedSchema,
    rng: &mut StdRng,
    index: Option<u32>,
) -> Result<Value> {
    // Check for enum values
    if let Some(enum_values) = &schema.enum_values {
        if !enum_values.is_empty() {
            let idx = rng.gen_range(0..enum_values.len());
            return Ok(enum_values[idx].clone());
        }
    }

    // Generate based on format
    let value = match schema.format.as_deref() {
        Some("email") => format!(
            "user{}@example.com",
            index.unwrap_or(rng.gen_range(1..1000))
        ),
        Some("date-time") => "2024-01-15T10:30:00Z".to_string(),
        Some("date") => "2024-01-15".to_string(),
        Some("uuid") => format!(
            "550e8400-e29b-41d4-a716-{:012}",
            rng.gen_range(0..999999999999u64)
        ),
        Some("uri") | Some("url") => "https://example.com".to_string(),
        Some("phone") => format!(
            "+1-555-{:03}-{:04}",
            rng.gen_range(100..999),
            rng.gen_range(1000..9999)
        ),
        _ => {
            // Generate generic string
            format!("string_{}", rng.gen_range(1000..9999))
        }
    };

    Ok(json!(value))
}

fn generate_integer_value(schema: &UnifiedSchema, rng: &mut StdRng) -> Result<Value> {
    let min = schema.minimum.unwrap_or(0.0) as i64;
    let max = schema.maximum.unwrap_or(100.0) as i64;
    Ok(json!(rng.gen_range(min..=max)))
}

fn generate_number_value(schema: &UnifiedSchema, rng: &mut StdRng) -> Result<Value> {
    let min = schema.minimum.unwrap_or(0.0);
    let max = schema.maximum.unwrap_or(100.0);
    let value: f64 = rng.gen_range(min..=max);
    Ok(json!((value * 100.0).round() / 100.0)) // Round to 2 decimal places
}

fn generate_array_value(
    schema: &UnifiedSchema,
    rng: &mut StdRng,
    _index: Option<u32>,
) -> Result<Value> {
    let count = rng.gen_range(1..=5);
    let mut items = Vec::new();

    if let Some(item_schema) = &schema.items {
        for i in 0..count {
            items.push(generate_value_from_schema(item_schema, rng, Some(i))?);
        }
    }

    Ok(json!(items))
}

fn generate_object_value(
    _schema: &UnifiedSchema,
    rng: &mut StdRng,
    index: Option<u32>,
) -> Result<Value> {
    let mut object = serde_json::Map::new();

    // Generate properties based on schema
    // For now, generate some common fields
    object.insert(
        "id".to_string(),
        json!(format!("id_{}", index.unwrap_or(rng.gen_range(1..1000)))),
    );
    object.insert("created_at".to_string(), json!("2024-01-15T10:30:00Z"));

    Ok(json!(object))
}

fn generate_min_value(schema: &UnifiedSchema) -> Result<Value> {
    match schema.schema_type {
        SchemaType::String => {
            let min_length = 0;
            Ok(json!("a".repeat(min_length.max(1))))
        }
        SchemaType::Integer => Ok(json!(schema.minimum.unwrap_or(0.0) as i64)),
        SchemaType::Number => Ok(json!(schema.minimum.unwrap_or(0.0))),
        SchemaType::Boolean => Ok(json!(false)),
        SchemaType::Array => Ok(json!([])),
        SchemaType::Object => Ok(json!({})),
        SchemaType::Unknown => Ok(json!(null)),
    }
}

fn generate_max_value(schema: &UnifiedSchema) -> Result<Value> {
    match schema.schema_type {
        SchemaType::String => {
            let max_length = 50;
            Ok(json!("Z".repeat(max_length)))
        }
        SchemaType::Integer => Ok(json!(schema.maximum.unwrap_or(i64::MAX as f64) as i64)),
        SchemaType::Number => Ok(json!(schema.maximum.unwrap_or(f64::MAX))),
        SchemaType::Boolean => Ok(json!(true)),
        SchemaType::Array => {
            // Generate array with max items
            let max_items = 10;
            let items: Vec<Value> = (0..max_items).map(|i| json!(i)).collect();
            Ok(json!(items))
        }
        SchemaType::Object => {
            // Generate object with many properties
            let mut obj = serde_json::Map::new();
            for i in 0..10 {
                obj.insert(format!("prop_{}", i), json!(i));
            }
            Ok(json!(obj))
        }
        SchemaType::Unknown => Ok(json!(null)),
    }
}

fn generate_empty_value(schema: &UnifiedSchema) -> Result<Value> {
    match schema.schema_type {
        SchemaType::String => Ok(json!("")),
        SchemaType::Array => Ok(json!([])),
        SchemaType::Object => Ok(json!({})),
        _ => generate_min_value(schema),
    }
}

fn generate_boundary_value(schema: &UnifiedSchema, rng: &mut StdRng) -> Result<Option<Value>> {
    match schema.schema_type {
        SchemaType::String => {
            // Special characters
            Ok(Some(json!("Test!@#$%^&*()_+-=[]{}|;':\",./<>?")))
        }
        SchemaType::Integer | SchemaType::Number => {
            // Just below and above limits
            if let (Some(min), Some(max)) = (schema.minimum, schema.maximum) {
                let boundary = if rng.gen_bool(0.5) {
                    min + 0.0001
                } else {
                    max - 0.0001
                };
                Ok(Some(json!(boundary)))
            } else {
                Ok(None)
            }
        }
        _ => Ok(None),
    }
}

fn write_fixtures(fixtures: &[Value], path: &Path, format: FixtureFormat) -> Result<()> {
    match format {
        FixtureFormat::Json => {
            let content = serde_json::to_string_pretty(&fixtures)?;
            fs::write(path, content)?;
        }
        FixtureFormat::Yaml => {
            let content = serde_yaml::to_string(&fixtures)?;
            fs::write(path, content)?;
        }
        FixtureFormat::Csv => {
            // Simple CSV implementation
            if fixtures.is_empty() {
                fs::write(path, "")?;
                return Ok(());
            }

            // Extract headers from first item
            if let Some(first) = fixtures.first() {
                if let Some(obj) = first.as_object() {
                    let headers: Vec<&str> = obj.keys().map(|s| s.as_str()).collect();
                    let mut csv_content = headers.join(",") + "\n";

                    // Write rows
                    for fixture in fixtures {
                        if let Some(obj) = fixture.as_object() {
                            let values: Vec<String> = headers
                                .iter()
                                .map(|h| {
                                    obj.get(*h)
                                        .map(|v| match v {
                                            Value::String(s) => format!("\"{}\"", s),
                                            _ => v.to_string(),
                                        })
                                        .unwrap_or_default()
                                })
                                .collect();
                            csv_content.push_str(&values.join(","));
                            csv_content.push_str("\n");
                        }
                    }

                    fs::write(path, csv_content)?;
                }
            }
        }
        FixtureFormat::Sql => {
            // Simple SQL insert generation
            let table_name = path
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("table")
                .split('-')
                .next()
                .unwrap_or("table");

            let mut sql_content = format!("-- Generated fixtures for {}\n", table_name);
            sql_content += &format!("INSERT INTO {} VALUES\n", table_name);

            let values: Vec<String> = fixtures
                .iter()
                .map(|f| {
                    if let Some(obj) = f.as_object() {
                        let vals: Vec<String> = obj
                            .values()
                            .map(|v| match v {
                                Value::String(s) => format!("'{}'", s.replace("'", "''")),
                                Value::Null => "NULL".to_string(),
                                _ => v.to_string(),
                            })
                            .collect();
                        format!("({})", vals.join(", "))
                    } else {
                        "()".to_string()
                    }
                })
                .collect();

            sql_content.push_str(&values.join(",\n"));
            sql_content.push_str(";\n");
            fs::write(path, sql_content)?;
        }
    }

    Ok(())
}

fn to_kebab_case(s: &str) -> String {
    let mut result = String::new();
    let mut prev_is_lower = false;

    for ch in s.chars() {
        if ch.is_uppercase() && prev_is_lower {
            result.push('-');
        }
        result.push(ch.to_lowercase().next().unwrap());
        prev_is_lower = ch.is_lowercase();
    }

    result
}
