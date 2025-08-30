# Binary Distribution Clarification

## ❌ What's NOT in Git Repository

**NEVER commit these to git:**
- `/target/` directory (built binaries)
- `*.exe`, `*.dll`, `*.so`, `*.dylib` files
- Any compiled artifacts
- Release packages (`*.tar.gz`, `*.zip`)

## ✅ What IS in Git Repository

**Only source code and configuration:**
```
git-repo/
├── src/              # Rust source code
├── agent/src/        # Agent source code
├── Cargo.toml        # Build configuration
├── .github/          # CI/CD workflows
├── scripts/          # Build scripts
├── docs/             # Documentation
└── tests/            # Test files
```

## 🚀 How Binaries are Distributed

### 1. **GitHub Releases** (Separate from repo)

When you create a release tag:
```bash
git tag v0.1.0
git push origin v0.1.0
```

The CI/CD pipeline:
1. **Builds** binaries in GitHub Actions cloud
2. **Uploads** them to GitHub Releases (not the repo)
3. **Creates** download links like:
   - `https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-darwin-amd64.tar.gz`

### 2. **Package Managers** (Build from source or download)

#### Cargo (builds from source):
```bash
cargo install mrapids
# Downloads source from crates.io
# Compiles on user's machine
# No pre-built binaries
```

#### NPM/pip (downloads pre-built):
```bash
npm install -g @microrapid/cli
# postinstall script downloads binary from GitHub Releases
# NOT from npm registry (too large)
```

#### Homebrew (downloads pre-built):
```bash
brew install mrapids
# Downloads binary from GitHub Releases
# Formula contains URL to release artifacts
```

## 📁 Correct .gitignore

```gitignore
# Build artifacts - NEVER commit
/target/
**/*.rs.bk
*.pdb

# Release artifacts - NEVER commit
/release/
*.tar.gz
*.zip
*.exe
*.dll
*.so
*.dylib

# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
```

## 🔄 Binary Distribution Flow

```
1. Developer pushes code (SOURCE ONLY)
   ↓
2. GitHub Actions builds binaries (IN CLOUD)
   ↓
3. Binaries uploaded to GitHub Releases (SEPARATE STORAGE)
   ↓
4. Users download from:
   - GitHub Releases page
   - Package managers (which fetch from GitHub Releases)
   - Direct URLs
```

## 📊 Storage Comparison

| Location | What's Stored | Size | Version Control |
|----------|--------------|------|-----------------|
| **Git Repo** | Source code only | ~5MB | Yes |
| **GitHub Releases** | Built binaries | ~25MB per platform | No (immutable) |
| **Package Registries** | Metadata + download URLs | <1KB | Yes |
| **User's Machine** | Final binaries | ~25MB | No |

## 🚫 Why NOT in Git?

1. **Size**: Binaries are 10-50MB each, bloats repo
2. **History**: Every version stays forever in git history
3. **Platforms**: Need different binaries per OS/arch
4. **Security**: Binaries can't be code-reviewed
5. **Performance**: Slow clones for developers

## ✅ Best Practices

### DO:
- ✅ Keep only source code in git
- ✅ Use CI/CD to build binaries
- ✅ Host binaries on GitHub Releases
- ✅ Use .gitignore to exclude binaries
- ✅ Build reproducible binaries

### DON'T:
- ❌ Commit binaries to git
- ❌ Store large files in repository  
- ❌ Include build artifacts
- ❌ Check in release packages

## 🔍 How to Verify

Check your repository:
```bash
# Should return nothing (good!)
git ls-files | grep -E '\.(exe|dll|so|dylib)$'

# Check file sizes (nothing over 1MB except maybe test data)
git ls-files | xargs du -h | sort -hr | head -20

# Ensure target is ignored
grep "^/target" .gitignore
```

## 📦 Example: GitHub Release Assets

When you create release `v0.1.0`, these files are uploaded to GitHub Releases (NOT the repo):

```
https://github.com/microrapid/api-runtime/releases/tag/v0.1.0
├── mrapids-0.1.0-darwin-amd64.tar.gz        (13MB)
├── mrapids-0.1.0-darwin-arm64.tar.gz        (13MB)
├── mrapids-0.1.0-linux-amd64.tar.gz         (15MB)
├── mrapids-0.1.0-windows-amd64.zip          (14MB)
├── mrapids-agent-0.1.0-darwin-amd64.tar.gz  (12MB)
├── ... (more platforms)
└── checksums.txt
```

These are **separate from the git repository** and downloaded on-demand!