# Multi-Platform Distribution Guide for MicroRapid

## 🎯 Distribution Strategy

### Supported Package Managers:
1. **Cargo** (crates.io) - Rust developers
2. **npm** - JavaScript/Node.js developers  
3. **pip** - Python developers
4. **Homebrew** - macOS/Linux users
5. **Scoop** - Windows users

---

## 📦 1. Cargo (crates.io)

### Setup
```toml
# Cargo.toml - Update for publishing
[package]
name = "mrapids"
version = "0.1.0"
edition = "2021"
authors = ["MicroRapid Team <team@microrapid.dev>"]
description = "Your OpenAPI, but executable - API automation and testing toolkit"
documentation = "https://docs.microrapid.dev"
homepage = "https://microrapid.dev"
repository = "https://github.com/microrapid/api-runtime"
license = "MIT"
keywords = ["openapi", "api", "testing", "cli", "automation"]
categories = ["command-line-utilities", "development-tools", "web-programming"]
readme = "README.md"
exclude = [
    "data/*",
    "tests/*",
    "examples/*",
    ".github/*",
    "docs/*"
]

[[bin]]
name = "mrapids"
path = "src/main.rs"

[workspace]
members = [".", "agent"]
```

### Build & Publish
```bash
# 1. Test locally
cargo test --all
cargo build --release

# 2. Package check
cargo package --list  # See what will be included
cargo package        # Create .crate file

# 3. Publish to crates.io
cargo login          # One-time setup
cargo publish --dry-run
cargo publish

# For workspace with agent:
cd agent && cargo publish
cd .. && cargo publish
```

### Users Install Via:
```bash
cargo install mrapids
cargo install mrapids-agent
```

---

## 📦 2. NPM (Node.js Wrapper)

### Project Structure
```
mrapids-npm/
├── package.json
├── index.js
├── postinstall.js
├── bin/
│   └── mrapids.js
└── README.md
```

### package.json
```json
{
  "name": "@microrapid/cli",
  "version": "0.1.0",
  "description": "MicroRapid CLI - Your OpenAPI, but executable",
  "keywords": ["openapi", "api", "testing", "cli"],
  "homepage": "https://microrapid.dev",
  "bugs": "https://github.com/microrapid/api-runtime/issues",
  "repository": {
    "type": "git",
    "url": "https://github.com/microrapid/api-runtime.git"
  },
  "license": "MIT",
  "author": "MicroRapid Team",
  "main": "index.js",
  "bin": {
    "mrapids": "bin/mrapids.js",
    "mrapids-agent": "bin/mrapids-agent.js"
  },
  "scripts": {
    "postinstall": "node postinstall.js"
  },
  "engines": {
    "node": ">=14.0.0"
  },
  "os": ["darwin", "linux", "win32"],
  "cpu": ["x64", "arm64"]
}
```

### postinstall.js
```javascript
#!/usr/bin/env node
const os = require('os');
const fs = require('fs');
const path = require('path');
const https = require('https');
const { exec } = require('child_process');

const VERSION = require('./package.json').version;
const BINARY_BASE_URL = 'https://github.com/microrapid/api-runtime/releases/download';

function getPlatform() {
  const platform = os.platform();
  const arch = os.arch();
  
  const mapping = {
    'darwin-x64': 'darwin-amd64',
    'darwin-arm64': 'darwin-arm64',
    'linux-x64': 'linux-amd64',
    'linux-arm64': 'linux-arm64',
    'win32-x64': 'windows-amd64.exe',
  };
  
  const key = `${platform}-${arch}`;
  if (!mapping[key]) {
    throw new Error(`Unsupported platform: ${key}`);
  }
  
  return mapping[key];
}

async function downloadBinary() {
  const platform = getPlatform();
  const binaries = ['mrapids', 'mrapids-agent'];
  
  for (const binary of binaries) {
    const url = `${BINARY_BASE_URL}/v${VERSION}/${binary}-${platform}`;
    const dest = path.join(__dirname, 'bin', binary + (platform.includes('windows') ? '.exe' : ''));
    
    console.log(`Downloading ${binary} for ${platform}...`);
    
    await download(url, dest);
    
    // Make executable on Unix
    if (!platform.includes('windows')) {
      fs.chmodSync(dest, '755');
    }
  }
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, { 
      headers: { 'User-Agent': 'mrapids-npm-installer' }
    }, (response) => {
      if (response.statusCode === 302) {
        // Handle redirect
        return download(response.headers.location, dest).then(resolve).catch(reject);
      }
      
      response.pipe(file);
      file.on('finish', () => {
        file.close();
        resolve();
      });
    }).on('error', reject);
  });
}

// Run installer
downloadBinary().catch(err => {
  console.error('Failed to download binaries:', err);
  process.exit(1);
});
```

### bin/mrapids.js
```javascript
#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

const binaryPath = path.join(
  __dirname,
  '../bin',
  `mrapids${os.platform() === 'win32' ? '.exe' : ''}`
);

const child = spawn(binaryPath, process.argv.slice(2), {
  stdio: 'inherit'
});

child.on('exit', (code) => {
  process.exit(code);
});
```

### Publish to NPM
```bash
# Build release binaries first
./scripts/build-all-platforms.sh

# Publish to npm
npm login
npm publish --access public
```

### Users Install Via:
```bash
npm install -g @microrapid/cli
# or
yarn global add @microrapid/cli
```

---

## 📦 3. PyPI (Python Wrapper)

### Project Structure
```
mrapids-python/
├── setup.py
├── setup.cfg
├── pyproject.toml
├── MANIFEST.in
├── README.md
├── mrapids/
│   ├── __init__.py
│   ├── __main__.py
│   └── installer.py
└── scripts/
    └── mrapids
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mrapids"
version = "0.1.0"
description = "MicroRapid CLI - Your OpenAPI, but executable"
readme = "README.md"
requires-python = ">=3.7"
license = {text = "MIT"}
authors = [
    {name = "MicroRapid Team", email = "team@microrapid.dev"}
]
keywords = ["openapi", "api", "testing", "cli", "automation"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[project.urls]
Homepage = "https://microrapid.dev"
Documentation = "https://docs.microrapid.dev"
Repository = "https://github.com/microrapid/api-runtime"
Issues = "https://github.com/microrapid/api-runtime/issues"

[project.scripts]
mrapids = "mrapids:main"
mrapids-agent = "mrapids:agent_main"
```

### setup.py
```python
import os
import platform
import subprocess
import sys
from pathlib import Path

from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION = "0.1.0"
BINARY_BASE_URL = "https://github.com/microrapid/api-runtime/releases/download"

class PostInstallCommand(install):
    """Post-installation for downloading platform-specific binaries."""
    
    def run(self):
        install.run(self)
        self.download_binaries()
    
    def download_binaries(self):
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Map Python platform to our binary names
        platform_map = {
            ('darwin', 'x86_64'): 'darwin-amd64',
            ('darwin', 'arm64'): 'darwin-arm64',
            ('linux', 'x86_64'): 'linux-amd64',
            ('linux', 'aarch64'): 'linux-arm64',
            ('windows', 'amd64'): 'windows-amd64',
        }
        
        platform_key = (system, machine)
        if platform_key not in platform_map:
            print(f"Warning: No pre-built binary for {system} {machine}")
            return
        
        binary_platform = platform_map[platform_key]
        
        # Download binaries
        for binary in ['mrapids', 'mrapids-agent']:
            url = f"{BINARY_BASE_URL}/v{VERSION}/{binary}-{binary_platform}"
            if system == 'windows':
                url += '.exe'
                binary += '.exe'
            
            dest = Path(self.install_scripts) / binary
            
            print(f"Downloading {binary} for {binary_platform}...")
            subprocess.check_call(['curl', '-L', '-o', str(dest), url])
            
            if system != 'windows':
                dest.chmod(0o755)

setup(
    name="mrapids",
    version=VERSION,
    packages=find_packages(),
    cmdclass={
        'install': PostInstallCommand,
    },
)
```

### mrapids/__main__.py
```python
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

def get_binary_path(name):
    """Get the path to the installed binary."""
    scripts_dir = Path(sys.prefix) / 'bin'
    if sys.platform == 'win32':
        scripts_dir = Path(sys.prefix) / 'Scripts'
        name += '.exe'
    
    return scripts_dir / name

def main():
    """Run mrapids CLI."""
    binary = get_binary_path('mrapids')
    if not binary.exists():
        print(f"Error: {binary} not found. Please reinstall mrapids.")
        sys.exit(1)
    
    sys.exit(subprocess.call([str(binary)] + sys.argv[1:]))

def agent_main():
    """Run mrapids-agent."""
    binary = get_binary_path('mrapids-agent')
    if not binary.exists():
        print(f"Error: {binary} not found. Please reinstall mrapids.")
        sys.exit(1)
    
    sys.exit(subprocess.call([str(binary)] + sys.argv[1:]))

if __name__ == '__main__':
    main()
```

### Build & Publish
```bash
# Build distribution
python -m build

# Upload to PyPI
python -m twine upload --repository pypi dist/*
```

### Users Install Via:
```bash
pip install mrapids
# or
pipx install mrapids  # Recommended for CLI tools
```

---

## 📦 4. Homebrew (macOS/Linux)

### Formula Structure
```ruby
# Formula/mrapids.rb
class Mrapids < Formula
  desc "Your OpenAPI, but executable - API automation toolkit"
  homepage "https://microrapid.dev"
  version "0.1.0"
  license "MIT"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/microrapid/api-runtime/releases/download/v#{version}/mrapids-#{version}-darwin-arm64.tar.gz"
      sha256 "YOUR_SHA256_HERE"
    else
      url "https://github.com/microrapid/api-runtime/releases/download/v#{version}/mrapids-#{version}-darwin-amd64.tar.gz"
      sha256 "YOUR_SHA256_HERE"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/microrapid/api-runtime/releases/download/v#{version}/mrapids-#{version}-linux-arm64.tar.gz"
      sha256 "YOUR_SHA256_HERE"
    else
      url "https://github.com/microrapid/api-runtime/releases/download/v#{version}/mrapids-#{version}-linux-amd64.tar.gz"
      sha256 "YOUR_SHA256_HERE"
    end
  end

  def install
    bin.install "mrapids"
    bin.install "mrapids-agent"
    
    # Install completions
    generate_completions_from_executable(bin/"mrapids", "completion")
  end

  test do
    assert_match "MicroRapid", shell_output("#{bin}/mrapids --version")
    assert_match "agent", shell_output("#{bin}/mrapids-agent --version")
  end
end
```

### Homebrew Tap Setup
```bash
# Create tap repository: homebrew-microrapid
git init homebrew-microrapid
cd homebrew-microrapid

mkdir Formula
cp mrapids.rb Formula/

git add .
git commit -m "Add mrapids formula"
git remote add origin https://github.com/microrapid/homebrew-microrapid
git push -u origin main
```

### Users Install Via:
```bash
brew tap microrapid/microrapid
brew install mrapids
```

---

## 📦 5. Scoop (Windows)

### Manifest Structure
```json
{
    "version": "0.1.0",
    "description": "MicroRapid - Your OpenAPI, but executable",
    "homepage": "https://microrapid.dev",
    "license": "MIT",
    "architecture": {
        "64bit": {
            "url": "https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-0.1.0-windows-amd64.zip",
            "hash": "YOUR_SHA256_HERE"
        }
    },
    "bin": [
        "mrapids.exe",
        "mrapids-agent.exe"
    ],
    "checkver": {
        "github": "https://github.com/microrapid/api-runtime"
    },
    "autoupdate": {
        "architecture": {
            "64bit": {
                "url": "https://github.com/microrapid/api-runtime/releases/download/v$version/mrapids-$version-windows-amd64.zip"
            }
        }
    }
}
```

### Scoop Bucket Setup
```bash
# Create bucket repository: scoop-microrapid
git init scoop-microrapid
cd scoop-microrapid

mkdir bucket
echo '{"version": "0.1.0", ...}' > bucket/mrapids.json

git add .
git commit -m "Add mrapids manifest"
git remote add origin https://github.com/microrapid/scoop-microrapid
git push -u origin main
```

### Users Install Via:
```powershell
scoop bucket add microrapid https://github.com/microrapid/scoop-microrapid
scoop install mrapids
```

---

## 🔧 Build Script for All Platforms

### scripts/build-all-platforms.sh
```bash
#!/bin/bash
set -e

VERSION=$(grep version Cargo.toml | head -1 | cut -d'"' -f2)
TARGETS=(
    "x86_64-apple-darwin:darwin-amd64"
    "aarch64-apple-darwin:darwin-arm64"
    "x86_64-unknown-linux-gnu:linux-amd64"
    "aarch64-unknown-linux-gnu:linux-arm64"
    "x86_64-pc-windows-gnu:windows-amd64"
)

echo "Building MicroRapid v${VERSION} for all platforms..."

# Create release directory
mkdir -p release/v${VERSION}

for target_info in "${TARGETS[@]}"; do
    IFS=':' read -r rust_target file_suffix <<< "$target_info"
    
    echo "Building for ${rust_target}..."
    
    # Install target if needed
    rustup target add ${rust_target} || true
    
    # Build
    cargo build --release --target ${rust_target}
    
    # Package binaries
    if [[ $rust_target == *"windows"* ]]; then
        cp target/${rust_target}/release/mrapids.exe release/v${VERSION}/mrapids-${file_suffix}.exe
        cp target/${rust_target}/release/mrapids-agent.exe release/v${VERSION}/mrapids-agent-${file_suffix}.exe
        
        # Create zip for Windows
        cd release/v${VERSION}
        zip mrapids-${VERSION}-${file_suffix}.zip mrapids-${file_suffix}.exe mrapids-agent-${file_suffix}.exe
        cd ../..
    else
        cp target/${rust_target}/release/mrapids release/v${VERSION}/mrapids-${file_suffix}
        cp target/${rust_target}/release/mrapids-agent release/v${VERSION}/mrapids-agent-${file_suffix}
        
        # Create tar.gz for Unix
        cd release/v${VERSION}
        tar czf mrapids-${VERSION}-${file_suffix}.tar.gz mrapids-${file_suffix} mrapids-agent-${file_suffix}
        cd ../..
    fi
done

# Generate checksums
cd release/v${VERSION}
shasum -a 256 *.tar.gz *.zip > checksums.txt
cd ../..

echo "✅ Build complete! Artifacts in release/v${VERSION}/"
```

---

## 📋 Release Checklist

### 1. **Version Bump**
```bash
# Update version in:
- Cargo.toml (both workspace members)
- agent/Cargo.toml
- package.json (npm)
- setup.py (Python)
- Homebrew formula
- Scoop manifest
```

### 2. **Build All Platforms**
```bash
./scripts/build-all-platforms.sh
```

### 3. **Create GitHub Release**
```bash
gh release create v0.1.0 \
  --title "MicroRapid v0.1.0" \
  --notes "See CHANGELOG.md" \
  release/v0.1.0/*
```

### 4. **Publish to Registries**
```bash
# Cargo
cargo publish

# NPM
cd mrapids-npm && npm publish

# PyPI
cd mrapids-python && python -m twine upload dist/*

# Update Homebrew
cd homebrew-microrapid && ./update-formula.sh

# Update Scoop
cd scoop-microrapid && ./update-manifest.sh
```

---

## 📊 Distribution Matrix

| Platform | Package Manager | Binary Format | Auto-Update |
|----------|----------------|---------------|-------------|
| macOS    | Homebrew       | tar.gz        | ✅          |
| macOS    | Cargo          | Source        | ❌          |
| Linux    | Homebrew       | tar.gz        | ✅          |
| Linux    | Cargo          | Source        | ❌          |
| Windows  | Scoop          | zip           | ✅          |
| Windows  | Cargo          | Source        | ❌          |
| Any      | npm            | Binary        | ❌          |
| Any      | pip            | Binary        | ❌          |

---

## 🎯 Best Practices

1. **Version Consistency**: Use semantic versioning across all platforms
2. **Binary Naming**: Keep consistent naming scheme
3. **Checksums**: Always provide SHA256 checksums
4. **Documentation**: Include platform-specific install instructions
5. **Testing**: Test installation on each platform before release
6. **Automation**: Use GitHub Actions for multi-platform builds

This distribution strategy ensures MicroRapid is accessible to developers regardless of their preferred toolchain!