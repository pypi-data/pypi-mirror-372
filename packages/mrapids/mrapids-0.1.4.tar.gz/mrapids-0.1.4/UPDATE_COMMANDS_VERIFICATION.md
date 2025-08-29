# Update Commands Verification

## Current Package Names and Commands

Based on the current configuration files, here's what will work:

### ✅ **NPM - YES, will work**
```bash
npm install -g @mrapids/cli@latest
```
- Package name: `@mrapids/cli` ✅
- Registry: npmjs.org ✅
- Binary: `mrapids` ✅

### ✅ **Cargo - YES, will work** 
```bash
cargo install mrapids --force
```
- Crate name: `mrapids` ✅
- Binary name: `mrapids` ✅
- Need `--force` to overwrite existing ✅

### ✅ **pip - YES, will work**
```bash
pip install --upgrade mrapids
```
- Package name: `mrapids` ✅
- Python 3.8+ required ✅

## Important Notes

### 1. **Publishing Required First**

These commands will ONLY work after you publish to the respective registries:

```bash
# NPM - Publish to npmjs.org
npm publish --access public

# Cargo - Publish to crates.io
cargo publish

# PyPI - Publish using maturin
maturin publish
```

### 2. **Version Compatibility**

When updating from 0.1.0 to newer versions:

#### NPM:
- `@latest` tag will get the latest stable version
- Major version updates (0.x → 1.x) will be included
- Use specific version if needed: `@mrapids/cli@0.2.0`

#### Cargo:
- Must use `--force` flag to overwrite
- Alternative: `cargo install --locked mrapids` (uses Cargo.lock)

#### pip:
- `--upgrade` or `-U` flag required
- Alternative: `pip install mrapids==0.2.0` (specific version)

### 3. **First-Time Installation Commands**

For new users who don't have it installed:

```bash
# NPM (first time)
npm install -g @mrapids/cli

# Cargo (first time)
cargo install mrapids

# pip (first time)
pip install mrapids
```

### 4. **Checking Current Version**

Users can verify what they have installed:

```bash
# Check CLI version (works for all)
mrapids --version

# Package manager specific checks
npm list -g @mrapids/cli
cargo install --list | grep mrapids
pip show mrapids
```

### 5. **Uninstall Commands**

If users need to remove:

```bash
# NPM
npm uninstall -g @mrapids/cli

# Cargo
cargo uninstall mrapids

# pip
pip uninstall mrapids
```

## Recommended Update Instructions

For your documentation, use these exact commands:

```markdown
## Updating MicroRapids

Check your current version:
```bash
mrapids --version
```

Update to the latest version:

**NPM** (if installed via npm):
```bash
npm install -g @mrapids/cli@latest
```

**Cargo** (if installed via cargo):
```bash
cargo install mrapids --force
```

**pip** (if installed via pip):
```bash
pip install --upgrade mrapids
```

Not sure how you installed it? Try each command until one works.
```

## Testing Before Release

Before publishing v0.1.0, test the update flow:

1. Publish v0.1.0 to test registry
2. Install v0.1.0
3. Publish v0.1.1 to test registry
4. Run update commands
5. Verify version changed

### NPM Test Registry:
```bash
# Publish to local registry
npm publish --registry http://localhost:4873

# Install from local registry
npm install -g @mrapids/cli --registry http://localhost:4873
```

### Cargo Test:
```bash
# Use --registry flag for custom registry
cargo publish --registry=my-registry
```

## Summary

✅ **All three update commands are correct and will work!**

The commands match your package names:
- NPM: `@mrapids/cli` 
- Cargo: `mrapids`
- pip: `mrapids`

Just make sure to publish to the registries first!