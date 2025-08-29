//! Data models for collections

use serde::{Deserialize, Deserializer, Serialize};
use serde_json::Value;
use std::collections::HashMap;

/// A collection of API requests
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Collection {
    /// Name of the collection
    pub name: String,

    /// Optional description
    #[serde(skip_serializing_if = "Option::is_none")]
    pub description: Option<String>,

    /// List of requests in the collection
    pub requests: Vec<CollectionRequest>,

    /// Default variables for the collection
    #[serde(default, skip_serializing_if = "HashMap::is_empty")]
    pub variables: HashMap<String, Value>,

    /// Default authentication profile
    #[serde(skip_serializing_if = "Option::is_none")]
    pub auth_profile: Option<String>,
}

/// A single request in a collection
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct CollectionRequest {
    /// Name of the request (must be unique within collection)
    pub name: String,

    /// Operation ID to execute
    pub operation: String,

    /// Optional parameters
    #[serde(skip_serializing_if = "Option::is_none")]
    pub params: Option<HashMap<String, Value>>,

    /// Optional request body
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<Value>,

    /// Save response with this key for later use
    #[serde(skip_serializing_if = "Option::is_none")]
    pub save_as: Option<String>,

    /// Expected response for testing
    #[serde(skip_serializing_if = "Option::is_none")]
    pub expect: Option<Expectation>,

    /// Request dependencies (must complete successfully before this request)
    #[serde(
        skip_serializing_if = "Option::is_none",
        default,
        deserialize_with = "deserialize_string_or_vec"
    )]
    pub depends_on: Option<Vec<String>>,

    /// Condition for execution (if expression)
    #[serde(skip_serializing_if = "Option::is_none", rename = "if")]
    pub if_condition: Option<String>,

    /// Skip condition (inverse of if)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub skip: Option<String>,

    /// Always run this request, even on collection failure
    #[serde(default)]
    pub run_always: bool,

    /// Stop entire collection if this request fails
    #[serde(default)]
    pub critical: bool,

    /// Retry configuration
    #[serde(skip_serializing_if = "Option::is_none")]
    pub retry: Option<RetryConfig>,
}

/// Retry configuration for a request
#[derive(Debug, Clone, Deserialize, Serialize, PartialEq)]
pub struct RetryConfig {
    /// Number of retry attempts
    pub attempts: u32,

    /// Delay between retries in milliseconds
    pub delay: u64,

    /// Backoff strategy (exponential or linear)
    #[serde(default)]
    pub backoff: BackoffStrategy,
}

/// Backoff strategy for retries
#[derive(Debug, Clone, Copy, Deserialize, Serialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum BackoffStrategy {
    Linear,
    Exponential,
}

impl Default for BackoffStrategy {
    fn default() -> Self {
        BackoffStrategy::Linear
    }
}

/// Expected response for test assertions
#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct Expectation {
    /// Expected HTTP status code
    #[serde(skip_serializing_if = "Option::is_none")]
    pub status: Option<u16>,

    /// Expected response body (partial match)
    #[serde(skip_serializing_if = "Option::is_none")]
    pub body: Option<Value>,

    /// Expected headers
    #[serde(skip_serializing_if = "Option::is_none")]
    pub headers: Option<HashMap<String, String>>,
}

/// Result of executing a collection request
#[derive(Debug, Clone, Serialize)]
pub struct RequestResult {
    /// Request name
    pub name: String,

    /// Operation that was executed
    pub operation: String,

    /// HTTP status code
    pub status: u16,

    /// Response body
    pub body: Option<Value>,

    /// Response headers
    pub headers: HashMap<String, String>,

    /// Execution time in milliseconds
    pub duration_ms: u64,

    /// Error message if request failed
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,

    /// Test result if expectations were defined
    #[serde(skip_serializing_if = "Option::is_none")]
    pub test_result: Option<TestResult>,
}

/// Result of test assertions
#[derive(Debug, Clone, Serialize)]
pub struct TestResult {
    /// Whether all assertions passed
    pub passed: bool,

    /// List of assertion results
    pub assertions: Vec<AssertionResult>,
}

/// Result of a single assertion
#[derive(Debug, Clone, Serialize)]
pub struct AssertionResult {
    /// Type of assertion (status, body, header)
    pub assertion_type: String,

    /// Whether the assertion passed
    pub passed: bool,

    /// Expected value
    pub expected: Value,

    /// Actual value
    pub actual: Value,

    /// Error message if assertion failed
    #[serde(skip_serializing_if = "Option::is_none")]
    pub message: Option<String>,
}

/// Summary of collection execution
#[derive(Debug, Clone, Serialize)]
pub struct CollectionSummary {
    /// Collection name
    pub name: String,

    /// Total number of requests
    pub total_requests: usize,

    /// Number of successful requests
    pub successful: usize,

    /// Number of failed requests
    pub failed: usize,

    /// Number of skipped requests
    pub skipped: usize,

    /// Total execution time in milliseconds
    pub total_duration_ms: u64,

    /// Individual request results
    pub results: Vec<RequestResult>,

    /// Test summary if running as tests
    #[serde(skip_serializing_if = "Option::is_none")]
    pub test_summary: Option<TestSummary>,
}

/// Summary of test execution
#[derive(Debug, Clone, Serialize)]
pub struct TestSummary {
    /// Total number of tests
    pub total_tests: usize,

    /// Number of passed tests
    pub passed: usize,

    /// Number of failed tests
    pub failed: usize,

    /// Whether all tests passed
    pub all_passed: bool,
}

/// Custom deserializer that accepts either a string or a vector of strings
fn deserialize_string_or_vec<'de, D>(deserializer: D) -> Result<Option<Vec<String>>, D::Error>
where
    D: Deserializer<'de>,
{
    use serde::de::{self, Visitor};
    use std::fmt;

    struct StringOrVecVisitor;

    impl<'de> Visitor<'de> for StringOrVecVisitor {
        type Value = Option<Vec<String>>;

        fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
            formatter.write_str("a string or a sequence of strings")
        }

        fn visit_none<E>(self) -> Result<Self::Value, E>
        where
            E: de::Error,
        {
            Ok(None)
        }

        fn visit_some<D>(self, deserializer: D) -> Result<Self::Value, D::Error>
        where
            D: Deserializer<'de>,
        {
            deserializer
                .deserialize_any(StringOrVecInnerVisitor)
                .map(Some)
        }

        fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
        where
            E: de::Error,
        {
            Ok(Some(vec![value.to_string()]))
        }

        fn visit_seq<A>(self, seq: A) -> Result<Self::Value, A::Error>
        where
            A: de::SeqAccess<'de>,
        {
            let vec = Deserialize::deserialize(de::value::SeqAccessDeserializer::new(seq))?;
            Ok(Some(vec))
        }
    }

    struct StringOrVecInnerVisitor;

    impl<'de> Visitor<'de> for StringOrVecInnerVisitor {
        type Value = Vec<String>;

        fn expecting(&self, formatter: &mut fmt::Formatter) -> fmt::Result {
            formatter.write_str("a string or a sequence of strings")
        }

        fn visit_str<E>(self, value: &str) -> Result<Self::Value, E>
        where
            E: de::Error,
        {
            Ok(vec![value.to_string()])
        }

        fn visit_seq<A>(self, seq: A) -> Result<Self::Value, A::Error>
        where
            A: de::SeqAccess<'de>,
        {
            Deserialize::deserialize(de::value::SeqAccessDeserializer::new(seq))
        }
    }

    deserializer.deserialize_option(StringOrVecVisitor)
}
