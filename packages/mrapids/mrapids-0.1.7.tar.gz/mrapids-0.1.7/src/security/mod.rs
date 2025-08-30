pub mod url_validator;
pub mod file_sandbox;
pub mod config;

pub use url_validator::{UrlValidator, ValidatedUrl};
pub use file_sandbox::{FileSandbox, SafePath};
pub use config::SecurityConfig;

#[derive(Debug, thiserror::Error)]
pub enum SecurityError {
    #[error("Invalid URL scheme: {0}")]
    InvalidScheme(String),
    
    #[error("Blocked IP address: {0}")]
    BlockedIP(std::net::IpAddr),
    
    #[error("Private IP address not allowed: {0}")]
    PrivateIP(std::net::IpAddr),
    
    #[error("Metadata endpoint detected: {0}")]
    MetadataEndpoint(String),
    
    #[error("Path traversal attempt detected")]
    PathTraversal,
    
    #[error("File access denied: {0}")]
    FileAccessDenied(String),
    
    #[error("Invalid port: {0}")]
    InvalidPort(u16),
    
    #[error("Too many redirects")]
    TooManyRedirects,
    
    #[error("DNS resolution failed: {0}")]
    DnsError(String),
    
    #[error("Invalid configuration: {0}")]
    ConfigError(String),
}