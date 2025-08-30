use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::time::Duration;

use super::SecurityError;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SecurityConfig {
    pub network: NetworkConfig,
    pub files: FileConfig,
    pub limits: LimitConfig,
    pub tls: TlsConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct NetworkConfig {
    #[serde(default = "default_allowed_schemes")]
    pub allowed_schemes: Vec<String>,
    
    #[serde(default = "default_allowed_ports")]
    pub allowed_ports: Vec<u16>,
    
    #[serde(default = "default_max_redirects")]
    pub max_redirects: u8,
    
    #[serde(default = "default_blocked_cidrs")]
    pub blocked_cidrs: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileConfig {
    #[serde(default = "default_allowed_read_dirs")]
    pub allowed_read_dirs: Vec<PathBuf>,
    
    #[serde(default = "default_allowed_write_dirs")]
    pub allowed_write_dirs: Vec<PathBuf>,
    
    #[serde(default = "default_allowed_extensions")]
    pub allowed_extensions: Vec<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct LimitConfig {
    #[serde(default = "default_max_response_size")]
    pub max_response_size: usize,
    
    #[serde(default = "default_request_timeout")]
    pub request_timeout: u64, // milliseconds
    
    #[serde(default = "default_max_request_size")]
    pub max_request_size: usize,
    
    #[serde(default = "default_max_header_size")]
    pub max_header_size: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TlsConfig {
    #[serde(default = "default_tls_verify")]
    pub verify: bool,
    
    #[serde(default = "default_min_tls_version")]
    pub min_version: String,
}

impl Default for SecurityConfig {
    fn default() -> Self {
        Self {
            network: NetworkConfig {
                allowed_schemes: default_allowed_schemes(),
                allowed_ports: default_allowed_ports(),
                max_redirects: default_max_redirects(),
                blocked_cidrs: default_blocked_cidrs(),
            },
            files: FileConfig {
                allowed_read_dirs: default_allowed_read_dirs(),
                allowed_write_dirs: default_allowed_write_dirs(),
                allowed_extensions: default_allowed_extensions(),
            },
            limits: LimitConfig {
                max_response_size: default_max_response_size(),
                request_timeout: default_request_timeout(),
                max_request_size: default_max_request_size(),
                max_header_size: default_max_header_size(),
            },
            tls: TlsConfig {
                verify: default_tls_verify(),
                min_version: default_min_tls_version(),
            },
        }
    }
}

impl SecurityConfig {
    pub fn load() -> Result<Self, SecurityError> {
        // Try to load from .mrapids/security.toml
        let config_path = PathBuf::from(".mrapids/security.toml");
        
        if config_path.exists() {
            let content = std::fs::read_to_string(&config_path)
                .map_err(|e| SecurityError::ConfigError(format!("Failed to read config: {}", e)))?;
            
            let config: SecurityConfig = toml::from_str(&content)
                .map_err(|e| SecurityError::ConfigError(format!("Invalid config: {}", e)))?;
            
            // Validate the loaded config
            config.validate()?;
            
            Ok(config)
        } else {
            // Use defaults
            Ok(Self::default())
        }
    }
    
    pub fn validate(&self) -> Result<(), SecurityError> {
        // Validate network config
        if self.network.allowed_schemes.is_empty() {
            return Err(SecurityError::ConfigError("No allowed schemes".to_string()));
        }
        
        if self.network.allowed_ports.is_empty() {
            return Err(SecurityError::ConfigError("No allowed ports".to_string()));
        }
        
        if self.network.max_redirects > 10 {
            return Err(SecurityError::ConfigError("Too many redirects allowed".to_string()));
        }
        
        // Validate limits
        if self.limits.max_response_size > 100 * 1024 * 1024 { // 100MB
            return Err(SecurityError::ConfigError("Response size limit too high".to_string()));
        }
        
        if self.limits.request_timeout < 1000 { // 1 second minimum
            return Err(SecurityError::ConfigError("Request timeout too low".to_string()));
        }
        
        Ok(())
    }
    
    pub fn save_defaults(path: &PathBuf) -> Result<(), SecurityError> {
        let config = Self::default();
        let toml = toml::to_string_pretty(&config)
            .map_err(|e| SecurityError::ConfigError(format!("Failed to serialize: {}", e)))?;
        
        // Create directory if needed
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)
                .map_err(|e| SecurityError::ConfigError(format!("Failed to create dir: {}", e)))?;
        }
        
        std::fs::write(path, toml)
            .map_err(|e| SecurityError::ConfigError(format!("Failed to write config: {}", e)))?;
        
        Ok(())
    }
    
    pub fn to_request_timeout(&self) -> Duration {
        Duration::from_millis(self.limits.request_timeout)
    }
}

// Default value functions
fn default_allowed_schemes() -> Vec<String> {
    vec!["https".to_string(), "http".to_string()]
}

fn default_allowed_ports() -> Vec<u16> {
    vec![80, 443, 8080, 8443, 3000, 8000]
}

fn default_max_redirects() -> u8 {
    5
}

fn default_blocked_cidrs() -> Vec<String> {
    vec![
        "127.0.0.0/8".to_string(),
        "10.0.0.0/8".to_string(),
        "172.16.0.0/12".to_string(),
        "192.168.0.0/16".to_string(),
        "169.254.0.0/16".to_string(),
        "::1/128".to_string(),
        "fc00::/7".to_string(),
    ]
}

fn default_allowed_read_dirs() -> Vec<PathBuf> {
    vec![
        PathBuf::from("."),
        PathBuf::from("./config"),
        PathBuf::from("./specs"),
        PathBuf::from("./examples"),
    ]
}

fn default_allowed_write_dirs() -> Vec<PathBuf> {
    vec![
        PathBuf::from("./output"),
        PathBuf::from("./generated"),
        PathBuf::from("./.mrapids"),
        PathBuf::from("./tmp"),
    ]
}

fn default_allowed_extensions() -> Vec<String> {
    vec![
        ".yaml".to_string(),
        ".yml".to_string(),
        ".json".to_string(),
        ".toml".to_string(),
        ".txt".to_string(),
        ".md".to_string(),
    ]
}

fn default_max_response_size() -> usize {
    10 * 1024 * 1024 // 10MB
}

fn default_request_timeout() -> u64 {
    30000 // 30 seconds
}

fn default_max_request_size() -> usize {
    1024 * 1024 // 1MB
}

fn default_max_header_size() -> usize {
    8 * 1024 // 8KB
}

fn default_tls_verify() -> bool {
    true
}

fn default_min_tls_version() -> String {
    "1.2".to_string()
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_default_config_is_valid() {
        let config = SecurityConfig::default();
        assert!(config.validate().is_ok());
    }
    
    #[test]
    fn test_rejects_invalid_config() {
        let mut config = SecurityConfig::default();
        config.network.allowed_schemes.clear();
        assert!(config.validate().is_err());
        
        let mut config = SecurityConfig::default();
        config.limits.max_response_size = 200 * 1024 * 1024; // 200MB
        assert!(config.validate().is_err());
    }
}