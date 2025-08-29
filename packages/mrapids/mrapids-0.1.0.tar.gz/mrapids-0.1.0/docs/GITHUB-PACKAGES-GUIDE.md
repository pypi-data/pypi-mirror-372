# 🚀 GitHub Packages - The Complete Guide

## What is GitHub Packages?

GitHub Packages is a **FREE** package hosting service built into GitHub that can store:
- 🐳 Docker/Container images
- 📦 npm packages (JavaScript)
- 💎 RubyGems (Ruby)
- 📦 Maven/Gradle (Java)
- 📦 NuGet (.NET)
- 🦀 Cargo packages (Rust) - via cargo-registry

**Best Part**: It's integrated with your repo - packages live next to your code!

## 🎯 Why GitHub Packages is Awesome

| Feature | GitHub Packages | Docker Hub | crates.io |
|---------|----------------|------------|-----------|
| **Free Storage** | 500MB (free) / Unlimited (paid) | 1 image (free) | Unlimited |
| **Private Packages** | ✅ Yes | Paid only | ❌ No |
| **Integration** | Built into GitHub | External | External |
| **Authentication** | GitHub token | Separate account | Separate account |
| **CI/CD** | Native with Actions | Needs setup | Needs setup |
| **Visibility Control** | Per-package | Per-repo | Always public |

## 🏃 Quick Start: Publish Your First Package NOW

### Step 1: Create a Personal Access Token (PAT)

1. Go to: https://github.com/settings/tokens/new
2. Name: "Package Publishing"
3. Select scopes:
   - ✅ `write:packages` - Upload packages
   - ✅ `read:packages` - Download packages  
   - ✅ `delete:packages` - Delete packages
   - ✅ `repo` - If using private repos
4. Click "Generate token"
5. **COPY THE TOKEN NOW** (you won't see it again!)

### Step 2: Save Your Token

```bash
# For Docker
echo YOUR_TOKEN | docker login ghcr.io -u YOUR_USERNAME --password-stdin

# For environment variable
echo "export GITHUB_TOKEN=YOUR_TOKEN" >> ~/.bashrc
source ~/.bashrc
```

### Step 3: Publish Different Package Types

## 📦 1. Docker/Container Images (Most Popular)

### Manual Publishing
```bash
# Build your image
docker build -t ghcr.io/microrapids/api-runtime:latest .

# Push to GitHub Packages
docker push ghcr.io/microrapids/api-runtime:latest

# Your package is now at:
# https://github.com/microrapids/api-runtime/pkgs/container/api-runtime
```

### Automated with GitHub Actions
Create `.github/workflows/docker-publish.yml`:

```yaml
name: Publish Docker Image

on:
  push:
    branches: [main]
  release:
    types: [published]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - uses: actions/checkout@v4
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
```

## 🦀 2. Rust Packages (Using cargo-registry)

GitHub Packages can host a private Cargo registry!

### Setup Private Cargo Registry

1. Create `.cargo/config.toml`:
```toml
[registries.github]
index = "https://github.com/microrapids/cargo-registry"
token = "YOUR_GITHUB_TOKEN"

[registry]
default = "github"
```

2. Publish to GitHub registry:
```bash
cargo publish --registry github
```

## 📦 3. NPM Packages (If you have JS tools)

### Setup `.npmrc`:
```
@microrapids:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=YOUR_GITHUB_TOKEN
```

### Publish:
```bash
npm publish
```

## 🎁 4. Generic Packages (Any file type!)

You can upload ANY file as a package:

```bash
# Upload any file
curl -X PUT \
  -H "Authorization: token YOUR_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @myfile.tar.gz \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/generic/my-package/1.0.0/myfile.tar.gz"
```

## 🔧 Complete Working Example

Let me create a complete workflow that publishes MULTIPLE package types: