# 📦 GitHub Packages - ALL Package Managers Guide

## Supported Package Types in GitHub Packages

GitHub Packages supports **6 major package ecosystems**:

1. 🐳 **Container/Docker** (ghcr.io)
2. 📦 **npm** (JavaScript/TypeScript)
3. 💎 **RubyGems** (Ruby)
4. ☕ **Maven/Gradle** (Java/Kotlin)
5. 🔷 **NuGet** (.NET/C#)
6. 📁 **Generic Packages** (ANY file - Python wheels, Go binaries, etc.)

## 🐍 Python Packages (PyPI Alternative)

GitHub doesn't have native PyPI support, but you can use **Generic Packages**:

### Method 1: Upload Python Wheels as Generic Packages

```bash
# Build your Python package
python setup.py bdist_wheel

# Upload to GitHub Packages
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @dist/mypackage-1.0.0-py3-none-any.whl \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/pypi/mypackage/1.0.0/mypackage-1.0.0-py3-none-any.whl"
```

### Method 2: Create Private PyPI with GitHub Pages

```yaml
# .github/workflows/python-publish.yml
name: Publish Python Package

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      
      - name: Build package
        run: |
          pip install build
          python -m build
      
      - name: Upload as Generic Package
        run: |
          for file in dist/*; do
            curl -X PUT \
              -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
              -H "Content-Type: application/octet-stream" \
              --data-binary @$file \
              "https://uploads.github.com/repos/${{ github.repository }}/packages/pypi/$(basename $file)"
          done
```

### Installing Python Packages from GitHub

```bash
# Direct from GitHub releases
pip install https://github.com/microrapids/api-runtime/releases/download/v1.0.0/package.whl

# Or from Generic Packages (with auth)
curl -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  "https://github.com/microrapids/api-runtime/packages/pypi/mypackage-1.0.0.whl" \
  -o mypackage.whl
pip install mypackage.whl
```

## 📦 NPM Packages (JavaScript/TypeScript)

### Setup package.json

```json
{
  "name": "@microrapids/api-runtime",
  "version": "1.0.0",
  "publishConfig": {
    "registry": "https://npm.pkg.github.com"
  }
}
```

### Setup .npmrc

```bash
@microrapids:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${NPM_TOKEN}
```

### Publish to GitHub Packages

```bash
# Login (one-time)
npm login --registry=https://npm.pkg.github.com --scope=@microrapids

# Publish
npm publish
```

### Install from GitHub Packages

```bash
# Setup .npmrc with token
echo "//npm.pkg.github.com/:_authToken=$GITHUB_TOKEN" >> .npmrc

# Install
npm install @microrapids/api-runtime
```

## ☕ Java/Maven Packages

### Setup pom.xml

```xml
<distributionManagement>
  <repository>
    <id>github</id>
    <name>GitHub Packages</name>
    <url>https://maven.pkg.github.com/microrapids/api-runtime</url>
  </repository>
</distributionManagement>
```

### Setup ~/.m2/settings.xml

```xml
<settings>
  <servers>
    <server>
      <id>github</id>
      <username>YOUR_USERNAME</username>
      <password>YOUR_GITHUB_TOKEN</password>
    </server>
  </servers>
</settings>
```

### Publish

```bash
mvn deploy
```

## 🔷 NuGet Packages (.NET/C#)

### Add Source

```bash
dotnet nuget add source \
  --username YOUR_USERNAME \
  --password YOUR_GITHUB_TOKEN \
  --store-password-in-clear-text \
  --name github \
  "https://nuget.pkg.github.com/microrapids/index.json"
```

### Publish

```bash
dotnet pack --configuration Release
dotnet nuget push "bin/Release/*.nupkg" --source "github"
```

## 💎 Ruby Gems

### Setup ~/.gem/credentials

```bash
---
:github: Bearer YOUR_GITHUB_TOKEN
```

### Build and Publish

```bash
gem build mypackage.gemspec
gem push --key github --host https://rubygems.pkg.github.com/microrapids mypackage-1.0.0.gem
```

## 🐹 Go Modules

Go doesn't use GitHub Packages directly, but you can:

### Method 1: Use Go Modules with GitHub

```go
// go.mod
module github.com/microrapids/api-runtime

go 1.21
```

```bash
# Users install directly from GitHub
go get github.com/microrapids/api-runtime@latest
```

### Method 2: Upload Binaries as Generic Packages

```bash
# Build
go build -o myapp

# Upload
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  --data-binary @myapp \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/golang/myapp/1.0.0/myapp-linux-amd64"
```

## 🦀 Rust/Cargo

Rust primarily uses crates.io, but you can:

### Method 1: Git Dependencies

```toml
# Cargo.toml
[dependencies]
my-crate = { git = "https://github.com/microrapids/api-runtime" }
```

### Method 2: Upload as Generic Package

```bash
# Build
cargo build --release

# Upload
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  --data-binary @target/release/myapp \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/cargo/myapp/1.0.0/myapp-linux-amd64"
```

## 📁 Generic Packages (For ANY Language)

This works for **ANY file type** - Python wheels, Go binaries, Shell scripts, ZIPs, etc.

### Upload Any File

```bash
# Upload literally ANY file
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/octet-stream" \
  --data-binary @myfile.anything \
  "https://uploads.github.com/repos/OWNER/REPO/packages/generic/PACKAGE_NAME/VERSION/FILENAME"
```

### Examples for Different Languages

```bash
# Python Wheel
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  --data-binary @dist/myapp-1.0.0-py3-none-any.whl \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/python/myapp/1.0.0/myapp-1.0.0-py3-none-any.whl"

# Go Binary
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  --data-binary @myapp \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/go/myapp/1.0.0/myapp-linux-amd64"

# PHP Package
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  --data-binary @myapp.phar \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/php/myapp/1.0.0/myapp.phar"

# Dart/Flutter Package
curl -X PUT \
  -H "Authorization: token $GITHUB_TOKEN" \
  --data-binary @myapp.tar.gz \
  "https://uploads.github.com/repos/microrapids/api-runtime/packages/dart/myapp/1.0.0/myapp.tar.gz"
```

### Download Generic Packages

```bash
# Public repo - no auth needed
curl -L \
  "https://github.com/OWNER/REPO/releases/download/VERSION/FILENAME" \
  -o FILENAME

# Private repo - needs auth
curl -L \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/octet-stream" \
  "https://api.github.com/repos/OWNER/REPO/packages/generic/PACKAGE/VERSION/FILENAME" \
  -o FILENAME
```

## 🎯 Complete Multi-Language Example