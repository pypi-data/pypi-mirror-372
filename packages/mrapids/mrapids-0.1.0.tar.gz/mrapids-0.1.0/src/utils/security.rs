/// Security utilities for MicroRapid CLI
/// Provides reusable security validation functions
use anyhow::{anyhow, Result};
use colored::*;
use std::net::IpAddr;
use std::path::Path;
use url::Url;

/// Validate URL for security (blocks SSRF attacks)
pub fn validate_url(url: &str) -> Result<()> {
    // Only allow HTTP and HTTPS
    if !url.starts_with("http://") && !url.starts_with("https://") {
        return Err(anyhow!("Only HTTP and HTTPS URLs are allowed."));
    }

    // Parse URL properly
    let parsed_url = Url::parse(url).map_err(|e| anyhow!("Invalid URL format: {}", e))?;

    // Get the host
    let host = parsed_url
        .host_str()
        .ok_or_else(|| anyhow!("URL must have a host"))?;

    // Check for localhost variants
    let host_lower = host.to_lowercase();
    if host_lower == "localhost"
        || host_lower == "localhost.localdomain"
        || host_lower.starts_with("localhost:")
        || host_lower.ends_with(".local")
        || host_lower.ends_with(".localhost")
    {
        return Err(anyhow!(
            "Access to localhost is not allowed. Use actual hostnames or IPs."
        ));
    }

    // If host is an IP address, validate it
    if let Ok(ip) = host.parse::<IpAddr>() {
        match ip {
            IpAddr::V4(ipv4) => {
                // Check for loopback (127.0.0.0/8)
                if ipv4.is_loopback() {
                    return Err(anyhow!("Access to loopback addresses is not allowed."));
                }

                // Check for private IP ranges (RFC 1918)
                if ipv4.is_private() {
                    return Err(anyhow!(
                        "Access to private IP ranges is not allowed for security reasons."
                    ));
                }

                // Check for link-local (169.254.0.0/16)
                if ipv4.is_link_local() {
                    return Err(anyhow!("Access to link-local addresses is not allowed."));
                }

                // Check for broadcast
                if ipv4.is_broadcast() {
                    return Err(anyhow!("Access to broadcast addresses is not allowed."));
                }

                // Check for unspecified (0.0.0.0)
                if ipv4.is_unspecified() {
                    return Err(anyhow!("Access to unspecified addresses is not allowed."));
                }

                // Check for multicast
                if ipv4.is_multicast() {
                    return Err(anyhow!("Access to multicast addresses is not allowed."));
                }

                // Explicitly check cloud metadata endpoint
                if ipv4.octets() == [169, 254, 169, 254] {
                    return Err(anyhow!(
                        "Access to cloud metadata endpoints is not allowed."
                    ));
                }
            }
            IpAddr::V6(ipv6) => {
                // Check for loopback (::1)
                if ipv6.is_loopback() {
                    return Err(anyhow!("Access to loopback addresses is not allowed."));
                }

                // Check for unspecified (::)
                if ipv6.is_unspecified() {
                    return Err(anyhow!("Access to unspecified addresses is not allowed."));
                }

                // Check for multicast
                if ipv6.is_multicast() {
                    return Err(anyhow!("Access to multicast addresses is not allowed."));
                }

                // Check for IPv4-mapped IPv6 addresses
                if let Some(ipv4) = ipv6.to_ipv4_mapped() {
                    if ipv4.is_loopback() || ipv4.is_private() || ipv4.is_link_local() {
                        return Err(anyhow!(
                            "Access to private/local addresses via IPv6 mapping is not allowed."
                        ));
                    }
                }
            }
        }
    }

    // Block known cloud metadata endpoints by hostname
    let blocked_hosts = [
        "metadata.google.internal",
        "metadata.google",
        "metadata.goog",
        "metadata.amazon",
        "metadata.azure",
        "instance-data",
        "instance.metadata",
    ];

    for blocked in &blocked_hosts {
        if host_lower.contains(blocked) {
            return Err(anyhow!(
                "Access to cloud metadata endpoints is not allowed."
            ));
        }
    }

    // Block file:// and other dangerous protocols (redundant but explicit)
    match parsed_url.scheme() {
        "http" | "https" => Ok(()),
        _ => Err(anyhow!("Only HTTP and HTTPS protocols are allowed.")),
    }
}

/// Check if URL uses HTTPS and enforce security policy
pub fn enforce_https(url: &str, allow_insecure: bool) -> Result<()> {
    // First validate the URL for other security issues
    validate_url(url)?;

    // Check if it's HTTP
    if url.starts_with("http://") && !allow_insecure {
        // Special exception for localhost during development
        let url_lower = url.to_lowercase();
        if url_lower.starts_with("http://localhost")
            || url_lower.starts_with("http://127.0.0.1")
            || url_lower.starts_with("http://0.0.0.0")
        {
            // Still blocked by validate_url above, but provide helpful message
            return Err(anyhow!(
                "HTTP is not allowed. Use HTTPS or pass --allow-insecure flag (not recommended)."
            ));
        }

        return Err(anyhow!(
            "Insecure HTTP connection blocked: {}\n\
             \n\
             {} {}\n\
             \n\
             HTTP connections are vulnerable to:\n\
             • Man-in-the-middle attacks\n\
             • Credential theft\n\
             • Data tampering\n\
             \n\
             To use HTTP anyway (NOT RECOMMENDED):\n\
             Add --allow-insecure flag to your command\n\
             \n\
             Better solution: Use HTTPS URLs",
            url,
            "⚠️".red().bold(),
            "SECURITY WARNING".red().bold()
        ));
    }

    // If HTTP is allowed, show a warning
    if url.starts_with("http://") && allow_insecure {
        eprintln!("\n{}", "━".repeat(60).red());
        eprintln!(
            "{} {} {}",
            "⚠️".red().bold(),
            "INSECURE CONNECTION WARNING".red().bold(),
            "⚠️".red().bold()
        );
        eprintln!("{}", "━".repeat(60).red());
        eprintln!("{} Using insecure HTTP connection to:", "⚠️".yellow());
        eprintln!("   {}", url.yellow());
        eprintln!();
        eprintln!(
            "{}",
            "This connection is NOT encrypted and vulnerable to:".red()
        );
        eprintln!("   • {} Man-in-the-middle attacks", "❌".red());
        eprintln!("   • {} Credential and API key theft", "❌".red());
        eprintln!("   • {} Data tampering and injection", "❌".red());
        eprintln!("   • {} Request/response interception", "❌".red());
        eprintln!();
        eprintln!(
            "{} {}",
            "👉".cyan(),
            "Recommendation: Use HTTPS instead".cyan().bold()
        );
        eprintln!("{}", "━".repeat(60).red());
        eprintln!();
    }

    Ok(())
}

/// Validate file path for reads (prevents directory traversal)
pub fn validate_file_path(path: &Path) -> Result<()> {
    let path_str = path.to_string_lossy();

    // Block path traversal
    if path_str.contains("..") {
        return Err(anyhow!("Path traversal is not allowed"));
    }

    // Block access to sensitive system files
    let blocked_paths = [
        "/etc/passwd",
        "/etc/shadow",
        "/etc/sudoers",
        "/.ssh/",
        "/root/",
        "/proc/",
        "/sys/",
        "/.aws/",
        "/.kube/",
        "/.docker/",
        "/.git/credentials",
        "/.netrc",
        "/.npmrc",
    ];

    for blocked in &blocked_paths {
        if path_str.contains(blocked) {
            return Err(anyhow!("Access to {} is not allowed", blocked));
        }
    }

    // Block Windows sensitive paths
    if cfg!(windows) {
        let blocked_windows = [
            "C:\\Windows\\System32",
            "C:\\Windows\\System",
            "C:\\Program Files",
        ];
        for blocked in &blocked_windows {
            if path_str.contains(blocked) {
                return Err(anyhow!("Access to {} is not allowed", blocked));
            }
        }
    }

    Ok(())
}

/// Validate output path for writes (additional restrictions)
pub fn validate_output_path(path: &Path) -> Result<()> {
    // First do all read validations
    validate_file_path(path)?;

    let path_str = path.to_string_lossy();

    // Block writing to system directories
    let blocked_write_paths = [
        "/usr/",
        "/bin/",
        "/sbin/",
        "/lib/",
        "/lib64/",
        "/etc/",
        "/boot/",
        "/dev/",
        "/opt/",
        "/var/lib/",
        "/var/run/",
    ];

    for blocked in &blocked_write_paths {
        if path_str.starts_with(blocked) {
            return Err(anyhow!("Cannot write to system directory: {}", blocked));
        }
    }

    // Block Windows system directories
    if cfg!(windows) {
        let blocked_windows = [
            "C:\\Windows",
            "C:\\Program Files",
            "C:\\ProgramData",
            "C:\\System",
        ];
        for blocked in &blocked_windows {
            if path_str.starts_with(blocked) {
                return Err(anyhow!("Cannot write to system directory: {}", blocked));
            }
        }
    }

    Ok(())
}

/// Validate directory for deletion operations
pub fn validate_delete_path(path: &Path) -> Result<()> {
    validate_output_path(path)?;

    let path_str = path.to_string_lossy();

    // Extra restrictions for deletions
    let critical_paths = ["/", "/home", "/Users", "~", ".", ".."];

    for critical in &critical_paths {
        if path_str == *critical || path_str.ends_with(critical) {
            return Err(anyhow!("Cannot delete critical directory: {}", critical));
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_url_validation() {
        // Should block
        assert!(validate_url("http://localhost/api").is_err());
        assert!(validate_url("http://127.0.0.1/api").is_err());
        assert!(validate_url("http://192.168.1.1/api").is_err());
        assert!(validate_url("http://10.0.0.1/api").is_err());
        assert!(validate_url("http://172.16.0.1/api").is_err());
        assert!(validate_url("http://169.254.169.254/metadata").is_err());
        assert!(validate_url("file:///etc/passwd").is_err());

        // Should allow
        assert!(validate_url("https://api.example.com").is_ok());
        assert!(validate_url("http://8.8.8.8/api").is_ok());
    }

    #[test]
    fn test_file_path_validation() {
        // Should block
        assert!(validate_file_path(Path::new("/etc/passwd")).is_err());
        assert!(validate_file_path(Path::new("../../../etc/passwd")).is_err());
        assert!(validate_file_path(Path::new("/home/user/.ssh/id_rsa")).is_err());

        // Should allow
        assert!(validate_file_path(Path::new("/home/user/project/api.yaml")).is_ok());
        assert!(validate_file_path(Path::new("./specs/api.yaml")).is_ok());
    }

    #[test]
    fn test_output_path_validation() {
        // Should block
        assert!(validate_output_path(Path::new("/etc/test.yaml")).is_err());
        assert!(validate_output_path(Path::new("/usr/bin/test")).is_err());

        // Should allow
        assert!(validate_output_path(Path::new("/tmp/test.yaml")).is_ok());
        assert!(validate_output_path(Path::new("./output/sdk/")).is_ok());
    }
}
