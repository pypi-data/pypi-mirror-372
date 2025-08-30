//! HTTP client with resource protection features

pub mod auth;
pub mod client;
pub mod rate_limiter;
pub mod response;
pub mod retry;

pub use auth::SimpleAuthProfile;
pub use client::{HttpClient, HttpClientConfig};
pub use response::HttpResponse;
