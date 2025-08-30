# Modular Installation Guide - Install What You Need

## 🎯 Installation Options

Users can install:
1. **`mrapids`** only - CLI tool for API testing/automation
2. **`mrapids-agent`** only - MCP server for AI agents
3. **Both** - Complete toolkit

---

## 📦 1. Cargo (Separate Crates)

### Setup: Split into Two Crates

```toml
# mrapids-cli/Cargo.toml
[package]
name = "mrapids"
version = "0.1.0"
description = "MicroRapid CLI - API testing and automation"

[[bin]]
name = "mrapids"

# mrapids-agent/Cargo.toml
[package]
name = "mrapids-agent"
version = "0.1.0"
description = "MicroRapid Agent - MCP server for AI agents"

[[bin]]
name = "mrapids-agent"

# Optional: Meta crate for both
# mrapids-suite/Cargo.toml
[package]
name = "mrapids-suite"
version = "0.1.0"

[dependencies]
mrapids = "0.1.0"
mrapids-agent = "0.1.0"
```

### User Installation:
```bash
# Install CLI only
cargo install mrapids

# Install Agent only
cargo install mrapids-agent

# Install both
cargo install mrapids mrapids-agent
# OR
cargo install mrapids-suite
```

---

## 📦 2. NPM (Separate Packages)

### Package Structure:
```
npm/
├── @microrapid/cli/          # CLI only
│   ├── package.json
│   └── postinstall.js
├── @microrapid/agent/        # Agent only
│   ├── package.json
│   └── postinstall.js
└── @microrapid/suite/        # Both (meta-package)
    └── package.json
```

### @microrapid/cli/package.json
```json
{
  "name": "@microrapid/cli",
  "version": "0.1.0",
  "description": "MicroRapid CLI - API testing and automation",
  "bin": {
    "mrapids": "bin/mrapids.js"
  },
  "scripts": {
    "postinstall": "node postinstall.js"
  }
}
```

### @microrapid/agent/package.json
```json
{
  "name": "@microrapid/agent",
  "version": "0.1.0",
  "description": "MicroRapid Agent - MCP server for AI agents",
  "bin": {
    "mrapids-agent": "bin/mrapids-agent.js"
  },
  "scripts": {
    "postinstall": "node postinstall.js"
  }
}
```

### @microrapid/suite/package.json (Meta-package)
```json
{
  "name": "@microrapid/suite",
  "version": "0.1.0",
  "description": "MicroRapid Suite - Complete toolkit",
  "dependencies": {
    "@microrapid/cli": "^0.1.0",
    "@microrapid/agent": "^0.1.0"
  }
}
```

### Enhanced postinstall.js (with single binary download)
```javascript
// @microrapid/cli/postinstall.js
const BINARY_NAME = 'mrapids';  // Only download this binary

async function downloadBinary() {
  const platform = getPlatform();
  const url = `${BINARY_BASE_URL}/v${VERSION}/${BINARY_NAME}-${platform}`;
  const dest = path.join(__dirname, 'bin', BINARY_NAME + (platform.includes('windows') ? '.exe' : ''));
  
  console.log(`Downloading ${BINARY_NAME} for ${platform}...`);
  await download(url, dest);
  
  if (!platform.includes('windows')) {
    fs.chmodSync(dest, '755');
  }
}
```

### User Installation:
```bash
# Install CLI only
npm install -g @microrapid/cli

# Install Agent only  
npm install -g @microrapid/agent

# Install both
npm install -g @microrapid/suite
# OR
npm install -g @microrapid/cli @microrapid/agent
```

---

## 📦 3. PyPI (Separate Packages)

### Package Structure:
```
python/
├── mrapids/              # CLI only
│   ├── setup.py
│   └── mrapids/
├── mrapids-agent/        # Agent only
│   ├── setup.py
│   └── mrapids_agent/
└── mrapids-suite/        # Both (meta-package)
    └── setup.py
```

### mrapids/setup.py
```python
from setuptools import setup

setup(
    name="mrapids",
    version="0.1.0",
    description="MicroRapid CLI - API testing and automation",
    entry_points={
        'console_scripts': [
            'mrapids=mrapids:main',
        ],
    },
    install_requires=[],
    extras_require={
        'agent': ['mrapids-agent'],  # Optional agent
        'full': ['mrapids-agent'],    # Full suite
    }
)
```

### mrapids-agent/setup.py
```python
setup(
    name="mrapids-agent",
    version="0.1.0",
    description="MicroRapid Agent - MCP server for AI agents",
    entry_points={
        'console_scripts': [
            'mrapids-agent=mrapids_agent:main',
        ],
    }
)
```

### User Installation:
```bash
# Install CLI only
pip install mrapids

# Install Agent only
pip install mrapids-agent

# Install both
pip install mrapids[full]
# OR
pip install mrapids mrapids-agent
```

---

## 📦 4. Homebrew (Formula Options)

### Enhanced Formula with Options:
```ruby
class Mrapids < Formula
  desc "MicroRapid - API automation toolkit"
  homepage "https://microrapid.dev"
  version "0.1.0"
  
  # Define components
  option "without-cli", "Skip installing mrapids CLI"
  option "without-agent", "Skip installing mrapids-agent"
  option "with-cli-only", "Install only mrapids CLI"
  option "with-agent-only", "Install only mrapids-agent"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/microrapid/api-runtime/releases/download/v#{version}/mrapids-#{version}-darwin-arm64.tar.gz"
    else
      url "https://github.com/microrapid/api-runtime/releases/download/v#{version}/mrapids-#{version}-darwin-amd64.tar.gz"
    end
  end

  def install
    if build.with?("cli-only")
      bin.install "mrapids"
    elsif build.with?("agent-only")
      bin.install "mrapids-agent"
    else
      bin.install "mrapids" unless build.without?("cli")
      bin.install "mrapids-agent" unless build.without?("agent")
    end
  end

  def caveats
    installed = []
    installed << "mrapids" if (bin/"mrapids").exist?
    installed << "mrapids-agent" if (bin/"mrapids-agent").exist?
    
    <<~EOS
      Installed: #{installed.join(", ")}
      
      To install missing components later:
        brew reinstall mrapids
    EOS
  end
end
```

### Alternative: Separate Formulas
```ruby
# Formula/mrapids-cli.rb
class MrapidsCli < Formula
  desc "MicroRapid CLI - API testing and automation"
  # ... download only mrapids binary
end

# Formula/mrapids-agent.rb  
class MrapidsAgent < Formula
  desc "MicroRapid Agent - MCP server"
  # ... download only mrapids-agent binary
end

# Formula/mrapids-suite.rb
class MrapidsSuite < Formula
  desc "MicroRapid Suite - Complete toolkit"
  depends_on "mrapids-cli"
  depends_on "mrapids-agent"
end
```

### User Installation:
```bash
# Install CLI only
brew install mrapids --with-cli-only
# OR with separate formulas:
brew install mrapids-cli

# Install Agent only
brew install mrapids --with-agent-only
# OR with separate formulas:
brew install mrapids-agent

# Install both (default)
brew install mrapids
# OR with separate formulas:
brew install mrapids-suite
```

---

## 📦 5. Scoop (Separate Manifests)

### Manifest Structure:
```
bucket/
├── mrapids-cli.json      # CLI only
├── mrapids-agent.json    # Agent only
└── mrapids.json          # Both (depends on others)
```

### mrapids-cli.json
```json
{
    "version": "0.1.0",
    "description": "MicroRapid CLI - API testing and automation",
    "architecture": {
        "64bit": {
            "url": "https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-cli-0.1.0-windows-amd64.zip",
            "hash": "SHA256_HERE",
            "extract_dir": "mrapids-cli"
        }
    },
    "bin": "mrapids.exe"
}
```

### mrapids-agent.json
```json
{
    "version": "0.1.0",
    "description": "MicroRapid Agent - MCP server",
    "architecture": {
        "64bit": {
            "url": "https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-agent-0.1.0-windows-amd64.zip",
            "hash": "SHA256_HERE"
        }
    },
    "bin": "mrapids-agent.exe"
}
```

### mrapids.json (Meta-package)
```json
{
    "version": "0.1.0",
    "description": "MicroRapid Suite - Complete toolkit",
    "depends": [
        "mrapids-cli",
        "mrapids-agent"
    ],
    "notes": "This is a meta-package that installs both mrapids-cli and mrapids-agent"
}
```

### User Installation:
```powershell
# Install CLI only
scoop install mrapids-cli

# Install Agent only
scoop install mrapids-agent

# Install both
scoop install mrapids
```

---

## 🏗️ Build System Changes

### Release Script for Individual Binaries:
```bash
#!/bin/bash
# scripts/build-modular-release.sh

VERSION=${1:-0.1.0}

# Build everything
cargo build --release
cd agent && cargo build --release && cd ..

# Package individual binaries
for binary in mrapids mrapids-agent; do
    for platform in "${PLATFORMS[@]}"; do
        # Create individual archives
        if [[ "$platform" == *"windows"* ]]; then
            zip ${binary}-${VERSION}-${platform}.zip ${binary}.exe
        else
            tar czf ${binary}-${VERSION}-${platform}.tar.gz ${binary}
        fi
    done
done

# Also create combined archives for convenience
tar czf mrapids-suite-${VERSION}-${platform}.tar.gz mrapids mrapids-agent
```

---

## 📊 Installation Matrix

| Package Manager | CLI Only | Agent Only | Both | Method |
|----------------|----------|------------|------|---------|
| Cargo | `cargo install mrapids` | `cargo install mrapids-agent` | Install both | Separate crates |
| NPM | `npm i -g @microrapid/cli` | `npm i -g @microrapid/agent` | `npm i -g @microrapid/suite` | Separate packages |
| pip | `pip install mrapids` | `pip install mrapids-agent` | `pip install mrapids[full]` | Separate packages |
| Homebrew | `brew install mrapids-cli` | `brew install mrapids-agent` | `brew install mrapids` | Options or separate |
| Scoop | `scoop install mrapids-cli` | `scoop install mrapids-agent` | `scoop install mrapids` | Separate manifests |

---

## 🎯 Benefits

1. **Reduced Download Size**: Users only download what they need
2. **Faster Installation**: Smaller packages install quicker
3. **Flexibility**: Mix and match based on use case
4. **Clear Separation**: CLI vs Agent purposes are distinct
5. **Easy Updates**: Update only what you use

## 📋 Use Cases

### CLI Only Users:
- Developers testing APIs
- CI/CD pipelines
- API automation scripts
- Don't need AI agent features

### Agent Only Users:
- AI/LLM developers
- Running MCP servers
- Agent-based automation
- Don't need CLI testing tools

### Full Suite Users:
- Complete API development workflow
- Both human and AI agent access
- Full feature set

This modular approach gives users complete control over what they install!