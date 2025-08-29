# 🦀 Setting Up Crates.io Token (Optional)

## Step 1: Create a Crates.io Account

1. Go to https://crates.io
2. Click "Log in with GitHub" (top right)
3. Authorize crates.io to access your GitHub account

## Step 2: Generate API Token

1. Once logged in, click your avatar (top right)
2. Select "Account Settings"
3. Go to "API Tokens" section
4. Click "New Token"
5. Give it a name like "GitHub Actions Publishing"
6. Copy the token (you'll only see it once!)

## Step 3: Add Token to GitHub Repository

1. Go to your GitHub repository: https://github.com/microrapids/api-runtime
2. Click "Settings" tab
3. In left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add:
   - Name: `CRATES_IO_TOKEN`
   - Value: (paste the token from crates.io)
6. Click "Add secret"

## Step 4: Verify in Workflow

The workflow already uses it:
```yaml
- name: Publish to crates.io
  run: cargo publish --token ${{ secrets.CRATES_IO_TOKEN }}
```

## Alternative: Don't Use Crates.io

If you don't want to set this up, you have two options:

### Option 1: Remove the crates.io job entirely
Delete the `publish-rust-crate` job from deploy.yml

### Option 2: Keep it but let it fail gracefully
The workflow already has `continue-on-error: true`, so it won't break your pipeline

### Option 3: Use GitHub as your Rust registry
Users can still install your package directly from GitHub:

```toml
# In their Cargo.toml
[dependencies]
mrapids = { git = "https://github.com/microrapids/api-runtime", tag = "v1.0.0" }
```

## 📊 Comparison: Crates.io vs GitHub

| Feature | Crates.io | GitHub Git Dependency |
|---------|-----------|----------------------|
| Setup Required | Yes (token) | No |
| Public Discovery | Yes (searchable) | No |
| Version Resolution | Semantic | Git tags/commits |
| Private Packages | No | Yes |
| Authentication | Token | SSH/HTTPS |
| Offline Cache | Yes | No |

## Recommendation

✅ **Use crates.io if:**
- You want your package to be publicly discoverable
- You want semantic versioning
- You're building a public library

❌ **Skip crates.io if:**
- Your package is private/internal
- You don't want the setup hassle
- You're fine with git dependencies