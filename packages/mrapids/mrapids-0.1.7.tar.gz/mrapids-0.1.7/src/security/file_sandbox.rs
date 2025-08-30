use std::path::{Path, PathBuf};
use std::fs;

use super::SecurityError;

#[derive(Debug, Clone)]
pub struct SafePath {
    pub path: PathBuf,
}

#[derive(Debug, Clone)]
pub struct FileSandbox {
    allowed_read_dirs: Vec<PathBuf>,
    allowed_write_dirs: Vec<PathBuf>,
    project_root: PathBuf,
    allowed_extensions: Vec<String>,
}

impl FileSandbox {
    pub fn new(project_root: PathBuf) -> Result<Self, SecurityError> {
        let project_root = project_root.canonicalize()
            .map_err(|e| SecurityError::ConfigError(format!("Invalid project root: {}", e)))?;
        
        let mut allowed_read_dirs = vec![
            project_root.clone(),
            project_root.join("config"),
            project_root.join("specs"),
            project_root.join("examples"),
        ];
        
        let mut allowed_write_dirs = vec![
            project_root.join("output"),
            project_root.join("generated"),
            project_root.join(".mrapids"),
            project_root.join("tmp"),
        ];
        
        // Ensure write directories exist
        for dir in &allowed_write_dirs {
            if !dir.exists() {
                fs::create_dir_all(dir)
                    .map_err(|e| SecurityError::ConfigError(format!("Failed to create dir: {}", e)))?;
            }
        }
        
        // Canonicalize all paths
        allowed_read_dirs = allowed_read_dirs.into_iter()
            .filter_map(|p| p.canonicalize().ok())
            .collect();
        
        allowed_write_dirs = allowed_write_dirs.into_iter()
            .filter_map(|p| p.canonicalize().ok())
            .collect();
        
        let allowed_extensions = vec![
            ".yaml".to_string(),
            ".yml".to_string(),
            ".json".to_string(),
            ".toml".to_string(),
            ".txt".to_string(),
            ".md".to_string(),
        ];
        
        Ok(Self {
            allowed_read_dirs,
            allowed_write_dirs,
            project_root,
            allowed_extensions,
        })
    }
    
    pub fn validate_read_path<P: AsRef<Path>>(&self, path: P) -> Result<SafePath, SecurityError> {
        let path = path.as_ref();
        
        // Check for dangerous patterns
        self.check_dangerous_patterns(path)?;
        
        // Resolve to absolute path
        let absolute = self.resolve_safe_path(path)?;
        
        // Check if in allowed read directories
        let allowed = self.allowed_read_dirs.iter()
            .any(|allowed_dir| absolute.starts_with(allowed_dir));
        
        if !allowed {
            return Err(SecurityError::FileAccessDenied(
                format!("Read access denied: {}", path.display())
            ));
        }
        
        // Check extension
        if let Some(ext) = absolute.extension() {
            let ext_str = format!(".{}", ext.to_string_lossy());
            if !self.allowed_extensions.contains(&ext_str) {
                return Err(SecurityError::FileAccessDenied(
                    format!("File type not allowed: {}", ext_str)
                ));
            }
        }
        
        Ok(SafePath { path: absolute })
    }
    
    pub fn validate_write_path<P: AsRef<Path>>(&self, path: P) -> Result<SafePath, SecurityError> {
        let path = path.as_ref();
        
        // Check for dangerous patterns
        self.check_dangerous_patterns(path)?;
        
        // Resolve to absolute path
        let absolute = self.resolve_safe_path(path)?;
        
        // Check if in allowed write directories
        let allowed = self.allowed_write_dirs.iter()
            .any(|allowed_dir| absolute.starts_with(allowed_dir));
        
        if !allowed {
            return Err(SecurityError::FileAccessDenied(
                format!("Write access denied: {}", path.display())
            ));
        }
        
        Ok(SafePath { path: absolute })
    }
    
    pub fn safe_join<P: AsRef<Path>>(&self, untrusted: P) -> Result<PathBuf, SecurityError> {
        let untrusted = untrusted.as_ref();
        
        // Check for dangerous patterns
        self.check_dangerous_patterns(untrusted)?;
        
        // Join with project root
        let joined = self.project_root.join(untrusted);
        
        // Resolve and verify
        let canonical = self.resolve_safe_path(&joined)?;
        
        // Ensure still under project root
        if !canonical.starts_with(&self.project_root) {
            return Err(SecurityError::PathTraversal);
        }
        
        Ok(canonical)
    }
    
    fn check_dangerous_patterns<P: AsRef<Path>>(&self, path: P) -> Result<(), SecurityError> {
        let path_str = path.as_ref().to_string_lossy();
        
        // Check for dangerous patterns
        let dangerous_patterns = [
            "..",           // Parent directory
            "~",            // Home directory
            "./.",          // Hidden traversal
            "//",           // Double slash
            "\0",           // Null byte
            "%2e%2e",       // URL encoded ..
            "%252e%252e",   // Double encoded ..
            "..\\",         // Windows traversal
            "..%5c",        // Encoded backslash
        ];
        
        for pattern in &dangerous_patterns {
            if path_str.contains(pattern) {
                return Err(SecurityError::PathTraversal);
            }
        }
        
        // Check for absolute paths
        if path.as_ref().is_absolute() {
            // Only allow if it's under project root
            if !path.as_ref().starts_with(&self.project_root) {
                return Err(SecurityError::PathTraversal);
            }
        }
        
        Ok(())
    }
    
    fn resolve_safe_path<P: AsRef<Path>>(&self, path: P) -> Result<PathBuf, SecurityError> {
        let path = path.as_ref();
        
        // If relative, make it relative to project root
        let to_resolve = if path.is_relative() {
            self.project_root.join(path)
        } else {
            path.to_path_buf()
        };
        
        // Try to canonicalize
        if let Ok(canonical) = to_resolve.canonicalize() {
            Ok(canonical)
        } else {
            // If file doesn't exist yet (for writes), canonicalize parent
            if let Some(parent) = to_resolve.parent() {
                if let Ok(canonical_parent) = parent.canonicalize() {
                    if let Some(file_name) = to_resolve.file_name() {
                        Ok(canonical_parent.join(file_name))
                    } else {
                        Err(SecurityError::PathTraversal)
                    }
                } else {
                    Err(SecurityError::PathTraversal)
                }
            } else {
                Err(SecurityError::PathTraversal)
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::TempDir;
    
    fn setup_sandbox() -> (TempDir, FileSandbox) {
        let temp_dir = TempDir::new().unwrap();
        let sandbox = FileSandbox::new(temp_dir.path().to_path_buf()).unwrap();
        
        // Create test files
        fs::create_dir_all(temp_dir.path().join("config")).unwrap();
        fs::write(temp_dir.path().join("config/test.yaml"), "test: true").unwrap();
        
        (temp_dir, sandbox)
    }
    
    #[test]
    fn test_blocks_path_traversal() {
        let (_temp_dir, sandbox) = setup_sandbox();
        
        assert!(sandbox.validate_read_path("../../../etc/passwd").is_err());
        assert!(sandbox.validate_read_path("/etc/passwd").is_err());
        assert!(sandbox.validate_read_path("~/.ssh/id_rsa").is_err());
        assert!(sandbox.safe_join("../outside").is_err());
    }
    
    #[test]
    fn test_allows_safe_paths() {
        let (_temp_dir, sandbox) = setup_sandbox();
        
        assert!(sandbox.validate_read_path("config/test.yaml").is_ok());
        assert!(sandbox.safe_join("config/test.yaml").is_ok());
    }
    
    #[test]
    fn test_write_restrictions() {
        let (_temp_dir, sandbox) = setup_sandbox();
        
        // Should allow writes to output dir
        assert!(sandbox.validate_write_path("output/result.json").is_ok());
        
        // Should block writes to config dir
        assert!(sandbox.validate_write_path("config/test.yaml").is_err());
    }
    
    #[test]
    fn test_extension_filtering() {
        let (_temp_dir, sandbox) = setup_sandbox();
        
        // Create a file with disallowed extension
        fs::write(sandbox.project_root.join("test.exe"), "binary").unwrap();
        
        assert!(sandbox.validate_read_path("test.exe").is_err());
    }
}