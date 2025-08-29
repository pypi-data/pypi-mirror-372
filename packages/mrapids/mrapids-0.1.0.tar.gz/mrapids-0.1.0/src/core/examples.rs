use crate::core::parser::{SchemaType, UnifiedSchema};
use serde_json::{json, Value};

/// Generate realistic example values based on field names and schema
pub fn generate_smart_example(field_name: &str, schema: &UnifiedSchema) -> Value {
    // First check if schema has an example
    if let Some(example) = &schema.example {
        return example.clone();
    }

    // Smart generation based on field name
    let field_lower = field_name.to_lowercase();

    // Common field patterns
    match field_lower.as_str() {
        // Identity fields
        "email" | "email_address" => return json!("user@example.com"),
        "name" | "full_name" | "fullname" => return json!("John Doe"),
        "first_name" | "firstname" | "given_name" => return json!("John"),
        "last_name" | "lastname" | "surname" | "family_name" => return json!("Doe"),
        "username" | "user_name" => return json!("johndoe"),
        "display_name" | "displayname" => return json!("John D."),

        // Contact info
        "phone" | "phone_number" | "phonenumber" | "mobile" => return json!("+14155551234"),
        "fax" | "fax_number" => return json!("+14155551235"),

        // Address fields
        "address" | "street" | "street_address" | "address_line1" | "line1" => {
            return json!("123 Main Street")
        }
        "address_line2" | "line2" | "apartment" | "suite" => return json!("Suite 100"),
        "city" => return json!("San Francisco"),
        "state" | "province" | "region" => return json!("CA"),
        "country" | "country_code" => return json!("US"),
        "postal_code" | "postalcode" | "zip" | "zip_code" | "zipcode" => return json!("94105"),

        // Financial fields
        "amount" | "total" | "price" | "cost" => return json!(1000),
        "currency" | "currency_code" => return json!("usd"),
        "account_number" | "accountnumber" => return json!("1234567890"),
        "routing_number" | "routingnumber" => return json!("123456789"),
        "card_number" | "cardnumber" => return json!("4242424242424242"),
        "exp_month" | "expiry_month" | "expmonth" => return json!("12"),
        "exp_year" | "expiry_year" | "expyear" => return json!("2025"),
        "cvv" | "cvc" | "security_code" => return json!("123"),

        // Date/Time fields
        "date" | "start_date" | "end_date" => return json!("2024-01-01"),
        "time" | "start_time" | "end_time" => return json!("14:30:00"),
        "created" | "created_at" | "createdat" | "created_date" => {
            return json!("2024-01-01T00:00:00Z")
        }
        "updated" | "updated_at" | "updatedat" | "modified" | "modified_at" => {
            return json!("2024-01-01T00:00:00Z")
        }
        "timestamp" => return json!(1704067200),
        "year" => return json!(2024),
        "month" => return json!(12),
        "day" => return json!(31),

        // Authentication/Security
        "password" => return json!("SecurePassword123!"),
        "token" | "access_token" | "accesstoken" => {
            return json!("sk_test_4eC39HqLyjWDarjtT1zdp7dc")
        }
        "api_key" | "apikey" => return json!("sk_test_4eC39HqLyjWDarjtT1zdp7dc"),
        "secret" | "secret_key" | "client_secret" => return json!("secret_1234567890abcdef"),
        "refresh_token" | "refreshtoken" => return json!("rt_test_1234567890abcdef"),

        // IDs and References
        "id" | "user_id" | "userid" | "customer_id" | "customerid" | "account_id" | "accountid" => {
            return match &schema.format {
                Some(f) if f == "uuid" => json!("550e8400-e29b-41d4-a716-446655440000"),
                _ => json!("cus_1234567890"),
            }
        }

        // URLs and Links
        "url" | "website" | "homepage" | "link" => return json!("https://example.com"),
        "callback_url" | "redirect_url" | "webhook_url" => {
            return json!("https://example.com/callback")
        }
        "image" | "image_url" | "avatar" | "avatar_url" | "photo" | "photo_url" => {
            return json!("https://example.com/image.jpg")
        }

        // Status and Type fields
        "status" => {
            if let Some(enums) = &schema.enum_values {
                return enums.first().cloned().unwrap_or_else(|| json!("active"));
            }
            return json!("active");
        }
        "type" | "kind" | "category" => {
            if let Some(enums) = &schema.enum_values {
                return enums.first().cloned().unwrap_or_else(|| json!("default"));
            }
            return json!("default");
        }

        // Boolean fields
        "active" | "is_active" | "enabled" | "is_enabled" => return json!(true),
        "deleted" | "is_deleted" | "archived" | "is_archived" => return json!(false),
        "verified" | "is_verified" | "confirmed" | "is_confirmed" => return json!(true),
        "published" | "is_published" | "public" | "is_public" => return json!(true),

        // Descriptive fields
        "description" | "summary" | "bio" | "about" => {
            return json!("This is an example description")
        }
        "title" | "subject" | "headline" => return json!("Example Title"),
        "message" | "content" | "body" | "text" => return json!("This is example content"),
        "notes" | "comments" | "remarks" => return json!("Additional notes here"),

        // Numeric fields
        "age" => return json!(30),
        "quantity" | "qty" | "count" => return json!(1),
        "rating" | "score" => return json!(5),
        "percentage" | "percent" => return json!(100),
        "latitude" | "lat" => return json!(37.7749),
        "longitude" | "lng" | "lon" => return json!(-122.4194),

        // File/Media fields
        "filename" | "file_name" => return json!("document.pdf"),
        "mimetype" | "mime_type" | "content_type" => return json!("application/pdf"),
        "size" | "file_size" | "filesize" => return json!(1024),

        _ => {
            // Check if field ends with common suffixes
            if field_lower.ends_with("_id") || field_lower.ends_with("_ref") {
                return json!("ref_1234567890");
            }
            if field_lower.ends_with("_url") || field_lower.ends_with("_link") {
                return json!("https://example.com/resource");
            }
            if field_lower.ends_with("_date") || field_lower.ends_with("_at") {
                return json!("2024-01-01T00:00:00Z");
            }
            if field_lower.ends_with("_name") {
                return json!("Example Name");
            }
            if field_lower.ends_with("_email") {
                return json!("contact@example.com");
            }
            if field_lower.ends_with("_count") || field_lower.ends_with("_total") {
                return json!(10);
            }

            // Fall back to schema-based generation
            generate_example_from_schema_type(schema)
        }
    }
}

/// Generate example based purely on schema type (fallback)
fn generate_example_from_schema_type(schema: &UnifiedSchema) -> Value {
    match schema.schema_type {
        SchemaType::String => {
            if let Some(enum_values) = &schema.enum_values {
                enum_values
                    .first()
                    .cloned()
                    .unwrap_or_else(|| json!("option1"))
            } else if let Some(format) = &schema.format {
                match format.as_str() {
                    "date" => json!("2024-01-01"),
                    "date-time" => json!("2024-01-01T00:00:00Z"),
                    "email" => json!("user@example.com"),
                    "uuid" => json!("550e8400-e29b-41d4-a716-446655440000"),
                    "uri" | "url" => json!("https://example.com"),
                    "hostname" => json!("example.com"),
                    "ipv4" => json!("192.168.1.1"),
                    "ipv6" => json!("2001:0db8:85a3:0000:0000:8a2e:0370:7334"),
                    "binary" => json!("SGVsbG8gV29ybGQ="), // Base64
                    "byte" => json!("U3dhZ2dlcg=="),       // Base64
                    _ => json!("example_string"),
                }
            } else {
                // Default string value
                json!("example_string")
            }
        }
        SchemaType::Integer => {
            if let Some(format) = &schema.format {
                match format.as_str() {
                    "int32" => json!(123),
                    "int64" => json!(1234567890),
                    _ => json!(100),
                }
            } else {
                json!(100)
            }
        }
        SchemaType::Number => {
            json!(123.45)
        }
        SchemaType::Boolean => json!(true),
        SchemaType::Array => {
            if let Some(items) = &schema.items {
                json!([generate_example_from_schema_type(items)])
            } else {
                json!([])
            }
        }
        SchemaType::Object => {
            let mut obj = serde_json::Map::new();
            if let Some(props) = &schema.properties {
                for (prop_name, prop_schema) in props {
                    // Use smart generation for nested properties
                    let value = generate_smart_example(prop_name, prop_schema);
                    obj.insert(prop_name.to_string(), value);
                }
            }
            json!(obj)
        }
        SchemaType::Unknown => json!(null),
    }
}

/// Generate example data for request body
pub fn generate_body_example(schema: &UnifiedSchema) -> Value {
    match schema.schema_type {
        SchemaType::Object => {
            let mut obj = serde_json::Map::new();
            if let Some(props) = &schema.properties {
                // Only include required fields by default
                let required_fields = schema.required.as_ref().cloned().unwrap_or_default();

                for (prop_name, prop_schema) in props {
                    if required_fields.contains(prop_name) {
                        let value = generate_smart_example(prop_name, prop_schema);
                        obj.insert(prop_name.to_string(), value);
                    }
                }

                // If no required fields, include first 3-5 optional fields as examples
                if obj.is_empty() && !props.is_empty() {
                    for (prop_name, prop_schema) in props.iter().take(5) {
                        let value = generate_smart_example(prop_name, prop_schema);
                        obj.insert(prop_name.to_string(), value);
                    }
                }
            }
            json!(obj)
        }
        _ => generate_example_from_schema_type(schema),
    }
}
