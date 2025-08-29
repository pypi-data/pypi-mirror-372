use std::collections::HashSet;
use std::net::{IpAddr, Ipv6Addr};
use std::str::FromStr;
use url::{Host, Url};
use ipnetwork::{IpNetwork, Ipv4Network, Ipv6Network};
use tokio::net::lookup_host;

use super::SecurityError;

#[derive(Debug, Clone)]
pub struct ValidatedUrl {
    pub url: Url,
    pub resolved_ip: Option<IpAddr>,
}

#[derive(Debug, Clone)]
pub struct UrlValidator {
    pub blocked_cidrs: Vec<IpNetwork>,
    pub allowed_schemes: HashSet<String>,
    pub allowed_ports: HashSet<u16>,
    pub max_redirects: u8,
}

impl Default for UrlValidator {
    fn default() -> Self {
        let mut blocked_cidrs = vec![];
        
        // IPv4 private and special ranges
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("127.0.0.0/8").unwrap())); // Localhost
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("10.0.0.0/8").unwrap())); // Private
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("172.16.0.0/12").unwrap())); // Private
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("192.168.0.0/16").unwrap())); // Private
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("169.254.0.0/16").unwrap())); // Link-local
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("169.254.169.254/32").unwrap())); // AWS metadata
        blocked_cidrs.push(IpNetwork::V4(Ipv4Network::from_str("0.0.0.0/8").unwrap())); // Invalid
        
        // IPv6 private and special ranges
        blocked_cidrs.push(IpNetwork::V6(Ipv6Network::from_str("::1/128").unwrap())); // Localhost
        blocked_cidrs.push(IpNetwork::V6(Ipv6Network::from_str("fc00::/7").unwrap())); // Private
        blocked_cidrs.push(IpNetwork::V6(Ipv6Network::from_str("fe80::/10").unwrap())); // Link-local
        
        let mut allowed_schemes = HashSet::new();
        allowed_schemes.insert("http".to_string());
        allowed_schemes.insert("https".to_string());
        
        let mut allowed_ports = HashSet::new();
        allowed_ports.insert(80);
        allowed_ports.insert(443);
        allowed_ports.insert(8080);
        allowed_ports.insert(8443);
        allowed_ports.insert(3000); // Common dev server
        allowed_ports.insert(8000); // Common dev server
        
        Self {
            blocked_cidrs,
            allowed_schemes,
            allowed_ports,
            max_redirects: 5,
        }
    }
}

impl UrlValidator {
    pub fn validate(&self, url_str: &str) -> Result<ValidatedUrl, SecurityError> {
        // Parse URL
        let url = Url::parse(url_str)
            .map_err(|e| SecurityError::InvalidScheme(e.to_string()))?;
        
        // Check scheme
        if !self.allowed_schemes.contains(url.scheme()) {
            return Err(SecurityError::InvalidScheme(url.scheme().to_string()));
        }
        
        // Check port
        let port = url.port().unwrap_or(match url.scheme() {
            "http" => 80,
            "https" => 443,
            _ => 0,
        });
        
        if !self.allowed_ports.contains(&port) {
            return Err(SecurityError::InvalidPort(port));
        }
        
        // Check host
        let host = url.host()
            .ok_or_else(|| SecurityError::InvalidScheme("No host".to_string()))?;
        
        // Check for dangerous hostnames
        self.check_dangerous_hostnames(&host)?;
        
        // If it's an IP, validate it immediately
        if let Host::Ipv4(ip) = host {
            self.validate_ip(&IpAddr::V4(ip))?;
        } else if let Host::Ipv6(ip) = host {
            self.validate_ip(&IpAddr::V6(ip))?;
        }
        
        Ok(ValidatedUrl {
            url,
            resolved_ip: None,
        })
    }
    
    pub async fn validate_with_dns(&self, url_str: &str) -> Result<ValidatedUrl, SecurityError> {
        let mut validated = self.validate(url_str)?;
        
        // Resolve DNS if hostname
        if let Some(host_str) = validated.url.host_str() {
            match validated.url.host() {
                Some(Host::Domain(_)) => {
                    let resolved_ip = self.safe_dns_resolve(host_str, validated.url.port_or_known_default()).await?;
                    validated.resolved_ip = Some(resolved_ip);
                }
                Some(Host::Ipv4(ip)) => {
                    validated.resolved_ip = Some(IpAddr::V4(ip));
                }
                Some(Host::Ipv6(ip)) => {
                    validated.resolved_ip = Some(IpAddr::V6(ip));
                }
                None => {}
            }
        }
        
        Ok(validated)
    }
    
    async fn safe_dns_resolve(&self, hostname: &str, port: Option<u16>) -> Result<IpAddr, SecurityError> {
        let addr = if let Some(p) = port {
            format!("{}:{}", hostname, p)
        } else {
            format!("{}:80", hostname)
        };
        
        let ips = lookup_host(&addr).await
            .map_err(|e| SecurityError::DnsError(e.to_string()))?;
        
        // Check each resolved IP
        for socket_addr in ips {
            let ip = socket_addr.ip();
            self.validate_ip(&ip)?;
            return Ok(ip); // Return first valid IP
        }
        
        Err(SecurityError::DnsError("No valid IPs resolved".to_string()))
    }
    
    fn validate_ip(&self, ip: &IpAddr) -> Result<(), SecurityError> {
        // Check against blocked CIDR ranges
        for cidr in &self.blocked_cidrs {
            if cidr.contains(*ip) {
                return Err(SecurityError::BlockedIP(*ip));
            }
        }
        
        // Additional checks for private IPs
        match ip {
            IpAddr::V4(ipv4) => {
                if ipv4.is_private() || ipv4.is_loopback() || ipv4.is_link_local() {
                    return Err(SecurityError::PrivateIP(*ip));
                }
            }
            IpAddr::V6(ipv6) => {
                if ipv6.is_loopback() || is_ipv6_private(ipv6) {
                    return Err(SecurityError::PrivateIP(*ip));
                }
            }
        }
        
        Ok(())
    }
    
    fn check_dangerous_hostnames(&self, host: &Host<&str>) -> Result<(), SecurityError> {
        let dangerous_hosts = [
            "metadata.google.internal",
            "metadata.goog",
            "metadata",
            "localhost",
            "localhost.localdomain",
        ];
        
        if let Host::Domain(domain) = host {
            let lower = domain.to_lowercase();
            for dangerous in &dangerous_hosts {
                if lower == *dangerous || lower.ends_with(&format!(".{}", dangerous)) {
                    return Err(SecurityError::MetadataEndpoint(domain.to_string()));
                }
            }
        }
        
        Ok(())
    }
}

// Helper function for IPv6 private detection
fn is_ipv6_private(ip: &Ipv6Addr) -> bool {
    // Check for ULA (Unique Local Address) fc00::/7
    let segments = ip.segments();
    (segments[0] & 0xfe00) == 0xfc00
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_blocks_localhost() {
        let validator = UrlValidator::default();
        
        assert!(validator.validate("http://localhost/api").is_err());
        assert!(validator.validate("http://127.0.0.1/api").is_err());
        assert!(validator.validate("http://[::1]/api").is_err());
    }
    
    #[test]
    fn test_blocks_private_ips() {
        let validator = UrlValidator::default();
        
        assert!(validator.validate("http://10.0.0.1/api").is_err());
        assert!(validator.validate("http://192.168.1.1/api").is_err());
        assert!(validator.validate("http://172.16.0.1/api").is_err());
    }
    
    #[test]
    fn test_blocks_metadata_endpoints() {
        let validator = UrlValidator::default();
        
        assert!(validator.validate("http://169.254.169.254/").is_err());
        assert!(validator.validate("http://metadata.google.internal/").is_err());
    }
    
    #[test]
    fn test_allows_public_urls() {
        let validator = UrlValidator::default();
        
        assert!(validator.validate("https://api.example.com/v1").is_ok());
        assert!(validator.validate("http://example.com:8080/api").is_ok());
    }
    
    #[test]
    fn test_blocks_invalid_schemes() {
        let validator = UrlValidator::default();
        
        assert!(validator.validate("file:///etc/passwd").is_err());
        assert!(validator.validate("ftp://example.com/file").is_err());
        assert!(validator.validate("javascript:alert(1)").is_err());
    }
    
    #[test]
    fn test_blocks_invalid_ports() {
        let validator = UrlValidator::default();
        
        assert!(validator.validate("http://example.com:22/").is_err());
        assert!(validator.validate("http://example.com:3306/").is_err());
        assert!(validator.validate("http://example.com:6379/").is_err());
    }
}