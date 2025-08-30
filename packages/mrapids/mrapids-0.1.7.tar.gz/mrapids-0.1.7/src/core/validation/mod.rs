pub mod report;
pub mod rules;
/// OpenAPI specification validation module
/// Provides multi-level validation for OAS 2.0, 3.0.x, and 3.1.x specs
pub mod types;
pub mod validator;
pub mod version;

pub use types::ValidationLevel;
pub use validator::SpecValidator;
