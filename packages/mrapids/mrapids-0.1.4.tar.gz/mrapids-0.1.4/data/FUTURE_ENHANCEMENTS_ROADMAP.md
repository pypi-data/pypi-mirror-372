# Future Enhancements Roadmap

## 🎯 Priority 1: Cross-Platform Security

### 1.1 Windows Permissions Support
**Goal**: Achieve equivalent security on Windows platforms

```rust
// Proposed implementation in src/commands/init.rs
#[cfg(windows)]
use std::os::windows::fs::OpenOptionsExt;
use windows::Win32::Storage::FileSystem::{
    FILE_ATTRIBUTE_HIDDEN,
    FILE_SHARE_NONE,
};
use windows::Win32::Security::{
    SetFileSecurity,
    DACL_SECURITY_INFORMATION,
};

#[cfg(windows)]
fn set_windows_permissions(path: &Path) -> Result<()> {
    use std::process::Command;
    
    // Option 1: Use icacls command
    Command::new("icacls")
        .args(&[
            path.to_str().unwrap(),
            "/inheritance:r",  // Remove inheritance
            "/grant:r",
            &format!("{}:F", std::env::var("USERNAME")?), // Full control for owner only
        ])
        .output()?;
    
    // Option 2: Use Windows API directly
    // This would require windows-rs crate
    Ok(())
}

// Enhanced cross-platform function
fn set_secure_permissions(path: &Path, is_directory: bool) -> Result<()> {
    #[cfg(unix)]
    {
        let mode = if is_directory { 0o700 } else { 0o600 };
        fs::set_permissions(path, fs::Permissions::from_mode(mode))?;
    }
    
    #[cfg(windows)]
    {
        set_windows_permissions(path)?;
    }
    
    Ok(())
}
```

**Implementation Tasks**:
- [ ] Add windows-rs or winapi crate dependency
- [ ] Implement ACL manipulation for owner-only access
- [ ] Test on Windows 10/11 and Windows Server
- [ ] Add CI/CD tests for Windows platform

---

## 🎯 Priority 2: Backup Management

### 2.1 Backup Retention Policies
**Goal**: Prevent unlimited backup accumulation

```toml
# Proposed config in mcp-server.toml
[backup]
enabled = true
retention_count = 10        # Keep last 10 backups
retention_days = 30         # Delete backups older than 30 days
compression = true          # Compress old backups
strategy = "rolling"        # rolling, daily, numbered
```

```rust
// Proposed backup manager
pub struct BackupManager {
    config: BackupConfig,
    backup_dir: PathBuf,
}

impl BackupManager {
    pub fn backup_file(&self, path: &Path) -> Result<PathBuf> {
        let backup_path = self.create_backup(path)?;
        self.enforce_retention_policy()?;
        Ok(backup_path)
    }
    
    fn enforce_retention_policy(&self) -> Result<()> {
        let mut backups = self.list_backups()?;
        backups.sort_by_key(|b| b.created_at);
        
        // Remove by count
        while backups.len() > self.config.retention_count {
            let oldest = backups.remove(0);
            fs::remove_file(&oldest.path)?;
        }
        
        // Remove by age
        let cutoff = Utc::now() - Duration::days(self.config.retention_days);
        for backup in backups {
            if backup.created_at < cutoff {
                fs::remove_file(&backup.path)?;
            }
        }
        
        Ok(())
    }
}
```

**CLI Interface**:
```bash
# New backup management commands
mrapids-agent backup list                      # List all backups
mrapids-agent backup restore <timestamp>       # Restore from backup
mrapids-agent backup clean                     # Manual cleanup
mrapids-agent backup config --retention-days 7 # Configure retention
```

---

## 🎯 Priority 3: Configuration Migration

### 3.1 Config Version Management
**Goal**: Smooth upgrades between mrapids-agent versions

```rust
// Proposed migration system
#[derive(Debug, Serialize, Deserialize)]
struct ConfigMetadata {
    version: String,
    created_at: DateTime<Utc>,
    last_modified: DateTime<Utc>,
    agent_version: String,
}

pub trait ConfigMigration {
    fn from_version(&self) -> &str;
    fn to_version(&self) -> &str;
    fn migrate(&self, config: toml::Value) -> Result<toml::Value>;
}

// Example migration from v1 to v2
struct MigrationV1ToV2;

impl ConfigMigration for MigrationV1ToV2 {
    fn from_version(&self) -> &str { "1.0" }
    fn to_version(&self) -> &str { "2.0" }
    
    fn migrate(&self, mut config: toml::Value) -> Result<toml::Value> {
        // Example: Rename old field to new structure
        if let Some(table) = config.as_table_mut() {
            // Move flat rate_limit to nested structure
            if let Some(rate_limit) = table.remove("rate_limit") {
                let mut rate_limits = toml::Table::new();
                rate_limits.insert("requests_per_minute".to_string(), rate_limit);
                table.insert("rate_limits".to_string(), toml::Value::Table(rate_limits));
            }
        }
        Ok(config)
    }
}
```

**CLI Commands**:
```bash
# Check if migration needed
mrapids-agent migrate check

# Preview migration changes
mrapids-agent migrate preview

# Perform migration with automatic backup
mrapids-agent migrate apply

# Rollback to previous version
mrapids-agent migrate rollback
```

---

## 🎯 Priority 4: Enhanced RBAC Implementation

### 4.1 Database-Backed RBAC
**Goal**: Move beyond file-based role management

```sql
-- SQLite schema for embedded RBAC
CREATE TABLE roles (
    id TEXT PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    parent_role_id TEXT REFERENCES roles(id),
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id TEXT PRIMARY KEY,
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    conditions JSON,
    UNIQUE(resource, action)
);

CREATE TABLE role_permissions (
    role_id TEXT REFERENCES roles(id),
    permission_id TEXT REFERENCES permissions(id),
    granted BOOLEAN DEFAULT TRUE,
    metadata JSON,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE agent_sessions (
    session_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    roles JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    metadata JSON
);
```

---

## 🎯 Priority 5: Advanced Security Features

### 5.1 Hardware Security Module (HSM) Support
```rust
// Support for hardware-backed key storage
pub trait SecretStore {
    fn get_secret(&self, name: &str) -> Result<SecureString>;
    fn set_secret(&self, name: &str, value: &SecureString) -> Result<()>;
}

pub struct HsmSecretStore {
    hsm: pkcs11::Context,
}

pub struct TpmSecretStore {
    tpm: tpm2::Context,
}
```

### 5.2 Audit Log Encryption
```rust
// Encrypted audit logs with key rotation
pub struct EncryptedAuditLogger {
    current_key: EncryptionKey,
    key_rotation_period: Duration,
    cipher: AesGcm<Aes256>,
}
```

---

## 🎯 Priority 6: Developer Experience

### 6.1 Interactive Init Wizard
```rust
// TUI-based configuration wizard
use ratatui::{Frame, Terminal};

pub struct InitWizard {
    steps: Vec<WizardStep>,
    current_step: usize,
}

impl InitWizard {
    pub fn run(&mut self) -> Result<InitConfig> {
        // Interactive prompts with validation
        // Real-time connection testing
        // Example selection with preview
    }
}
```

### 6.2 Config Validation & Linting
```bash
# Validate configuration with detailed feedback
mrapids-agent lint
  ✅ Server configuration valid
  ⚠️  Warning: Rate limit might be too low for production
  ℹ️  Suggestion: Enable audit log compression to save space
  ✅ Policy rules: 12 rules, no conflicts
  ✅ Auth profiles: 3 profiles, all valid
```

---

## 🔄 Implementation Timeline

### Phase 1 (Q1 2024)
- [ ] Windows permissions support
- [ ] Basic backup retention
- [ ] Config version tracking

### Phase 2 (Q2 2024)
- [ ] Full backup management CLI
- [ ] Config migration framework
- [ ] SQLite-based RBAC

### Phase 3 (Q3 2024)
- [ ] HSM/TPM support
- [ ] Encrypted audit logs
- [ ] Interactive wizard

### Phase 4 (Q4 2024)
- [ ] Advanced linting
- [ ] Performance optimizations
- [ ] Cloud secret store integration

---

## 🧪 Testing Strategy

### Unit Tests
```rust
#[cfg(test)]
mod tests {
    #[test]
    #[cfg(windows)]
    fn test_windows_permissions() {
        // Test ACL manipulation
    }
    
    #[test]
    fn test_backup_retention() {
        // Test cleanup logic
    }
    
    #[test]
    fn test_config_migration() {
        // Test version upgrades
    }
}
```

### Integration Tests
```bash
# Cross-platform CI/CD matrix
os: [ubuntu-latest, windows-latest, macos-latest]
rust: [stable, beta]
```

---

## 📊 Success Metrics

1. **Security**: 0 permission-related vulnerabilities
2. **Reliability**: 99.9% successful config migrations
3. **Performance**: <100ms init time
4. **Usability**: 90% users complete init without documentation
5. **Compatibility**: Support for 3 latest OS versions

---

## 🤝 Community Contributions

We welcome contributions! Priority areas:
1. Windows security implementation
2. Additional example templates
3. Config migration scripts
4. Documentation improvements
5. Integration examples

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.