# Quick Start: Creating Your First Package

## Current Status
✅ **Code**: In GitHub  
✅ **CI/CD**: Configured  
❌ **Packages**: Not created yet  
❌ **Deployments**: Not set up yet  

## Why You Don't See Packages

You don't see packages because **we haven't built and pushed any yet!** Here's what needs to happen:

```mermaid
graph LR
    A[Your Code<br/>✅ Done] --> B[Build Docker Image<br/>❌ Not Done]
    B --> C[Push to Registry<br/>❌ Not Done]
    C --> D[Package Visible<br/>❌ Waiting]
```

## Option 1: Quick Manual Test (Recommended First)

Run this script to create your first Docker package:

```bash
# This will build and push your first Docker image
./scripts/build-and-push-docker.sh
```

What this does:
1. Builds a Docker image from your code
2. Logs into GitHub Container Registry
3. Pushes the image to ghcr.io
4. Makes it available at: `ghcr.io/microrapids/api-runtime:latest`

**Required**: GitHub Personal Access Token
- Go to: https://github.com/settings/tokens/new
- Create token with `write:packages` scope
- Use when script prompts for token

## Option 2: Use CI/CD (Automated)

Trigger the workflow manually:

```bash
# Login to GitHub CLI first
gh auth login

# Run the publish workflow (dry run)
gh workflow run publish.yml -f target=docker -f dry_run=true

# Check the status
gh run list --workflow=publish.yml

# View the logs
gh run view
```

## Option 3: Create a Release (Full Automation)

```bash
# Create a tag
git tag v0.1.0
git push origin v0.1.0

# Create a release on GitHub
gh release create v0.1.0 --title "First Release" --notes "Initial release"

# This triggers all publishing workflows automatically!
```

## After Publishing - Where to Find Your Packages

### 1. GitHub Packages Page
```
https://github.com/microrapids/api-runtime/packages
```
You'll see your Docker containers here after pushing.

### 2. Direct Docker Pull
```bash
# After publishing, anyone can pull your image
docker pull ghcr.io/microrapids/api-runtime:latest
```

### 3. In GitHub UI
- Go to your repo
- Look for "Packages" in the right sidebar
- Click to see all published packages

## Understanding the Flow

### What Happens When You Push Code
```
git push → GitHub → CI Builds → Artifact Created → Stored Temporarily
                                        ↓
                                  (NOT visible as package)
```

### What Happens When You Publish
```
Create Release → CI Builds → Docker Image → Push to ghcr.io → Package Visible!
                                                     ↓
                              (NOW visible at github.com/.../packages)
```

## Common Confusion Points

**Q: I pushed my code, why no packages?**  
A: Pushing code only triggers builds. Packages are created when you explicitly publish (release or manual push).

**Q: Where are the artifacts from my feature branch?**  
A: In GitHub Actions → Your workflow run → Artifacts section (temporary, 90 days)

**Q: How do I make packages appear?**  
A: Run `./scripts/build-and-push-docker.sh` or create a release

**Q: What's the difference between artifacts and packages?**  
- **Artifacts**: Temporary build outputs in GitHub Actions
- **Packages**: Permanent published images/libraries in registries

## Try It Now!

1. **Quickest Way** (2 minutes):
   ```bash
   ./scripts/build-and-push-docker.sh
   ```
   Then check: https://github.com/microrapids/api-runtime/packages

2. **Automated Way** (5 minutes):
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   gh release create v0.1.0
   ```

After either method, you'll finally see packages in your repository!

## Troubleshooting

### "Permission denied" when pushing Docker image
- Make sure your PAT token has `write:packages` scope
- Token creation: https://github.com/settings/tokens/new

### "Package not found" after pushing
- It may take 1-2 minutes to appear
- Check: https://github.com/orgs/microrapids/packages
- Make sure the push succeeded (check script output)

### "Cannot pull image"
- If package is private, you need to login first:
  ```bash
  echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
  ```

---

**Next Step**: Run `./scripts/build-and-push-docker.sh` to create your first package!