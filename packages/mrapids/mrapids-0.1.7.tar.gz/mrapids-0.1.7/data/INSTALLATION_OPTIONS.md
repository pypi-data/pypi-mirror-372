# MicroRapid Installation Options

## 🎯 Choose What You Need

MicroRapid offers flexible installation options. Install only what you need:

| What You Need | Install Command | Size | Use Case |
|--------------|-----------------|------|----------|
| **CLI Only** | `cargo install mrapids` | ~13MB | API testing, automation, CI/CD |
| **Agent Only** | `cargo install mrapids-agent` | ~12MB | AI agents, MCP server |
| **Both** | `cargo install mrapids mrapids-agent` | ~25MB | Complete toolkit |

---

## 📦 Quick Install by Package Manager

### Homebrew (macOS/Linux)
```bash
# CLI only
brew install mrapids-cli

# Agent only  
brew install mrapids-agent

# Both
brew install mrapids
```

### NPM (Cross-platform)
```bash
# CLI only
npm install -g @microrapid/cli

# Agent only
npm install -g @microrapid/agent  

# Both
npm install -g @microrapid/suite
```

### pip (Python)
```bash
# CLI only
pip install mrapids

# Agent only
pip install mrapids-agent

# Both
pip install mrapids[full]
```

### Scoop (Windows)
```powershell
# CLI only
scoop install mrapids-cli

# Agent only
scoop install mrapids-agent

# Both  
scoop install mrapids
```

---

## 🤔 Which One Do I Need?

### Install CLI Only (`mrapids`) if you:
- 🧪 Test APIs manually or in CI/CD
- 🤖 Automate API workflows
- 📊 Generate API test reports
- 🔧 Debug API endpoints
- 📝 Create API collections
- 🚀 Generate SDK code

**Example users**: Backend developers, QA engineers, DevOps

### Install Agent Only (`mrapids-agent`) if you:
- 🤖 Build AI/LLM applications
- 🔌 Need MCP server for Claude/GPT
- 🛡️ Want policy-based API access
- 📊 Require audit logging for AI
- 🔐 Need secure credential management
- ⚡ Run automated AI workflows

**Example users**: AI developers, ML engineers, ChatGPT/Claude users

### Install Both if you:
- 🎯 Want the complete platform
- 🔄 Switch between manual and AI testing
- 🏢 Building team solutions
- 📈 Need full observability
- 🎨 Develop and deploy APIs

**Example users**: Full-stack teams, API platform engineers

---

## 💾 Download Sizes

| Package | Compressed | Installed |
|---------|------------|-----------|
| CLI only | ~5MB | ~13MB |
| Agent only | ~4MB | ~12MB |
| Suite (both) | ~9MB | ~25MB |

---

## 🚀 Direct Downloads

Don't want to use a package manager? Download directly:

### Latest Release: v0.1.0

#### CLI Only
- [mrapids-0.1.0-darwin-amd64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-0.1.0-darwin-amd64.tar.gz) (macOS Intel)
- [mrapids-0.1.0-darwin-arm64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-0.1.0-darwin-arm64.tar.gz) (macOS Apple Silicon)
- [mrapids-0.1.0-linux-amd64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-0.1.0-linux-amd64.tar.gz) (Linux x64)
- [mrapids-0.1.0-windows-amd64.zip](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-0.1.0-windows-amd64.zip) (Windows x64)

#### Agent Only
- [mrapids-agent-0.1.0-darwin-amd64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-agent-0.1.0-darwin-amd64.tar.gz) (macOS Intel)
- [mrapids-agent-0.1.0-darwin-arm64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-agent-0.1.0-darwin-arm64.tar.gz) (macOS Apple Silicon)
- [mrapids-agent-0.1.0-linux-amd64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-agent-0.1.0-linux-amd64.tar.gz) (Linux x64)
- [mrapids-agent-0.1.0-windows-amd64.zip](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-agent-0.1.0-windows-amd64.zip) (Windows x64)

#### Complete Suite
- [mrapids-suite-0.1.0-darwin-amd64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-suite-0.1.0-darwin-amd64.tar.gz) (macOS Intel)
- [mrapids-suite-0.1.0-darwin-arm64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-suite-0.1.0-darwin-arm64.tar.gz) (macOS Apple Silicon)
- [mrapids-suite-0.1.0-linux-amd64.tar.gz](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-suite-0.1.0-linux-amd64.tar.gz) (Linux x64)
- [mrapids-suite-0.1.0-windows-amd64.zip](https://github.com/microrapid/api-runtime/releases/download/v0.1.0/mrapids-suite-0.1.0-windows-amd64.zip) (Windows x64)

---

## 📝 Manual Installation

### macOS/Linux
```bash
# Download your choice
curl -L https://github.com/microrapid/api-runtime/releases/download/v0.1.0/PACKAGE.tar.gz -o mrapids.tar.gz

# Extract
tar xzf mrapids.tar.gz

# Install
sudo mv mrapids* /usr/local/bin/

# Verify
mrapids --version
```

### Windows
```powershell
# Download your choice
Invoke-WebRequest -Uri "https://github.com/microrapid/api-runtime/releases/download/v0.1.0/PACKAGE.zip" -OutFile "mrapids.zip"

# Extract
Expand-Archive -Path "mrapids.zip" -DestinationPath "."

# Add to PATH or move to desired location
# Then verify
mrapids --version
```

---

## 🔄 Switching Between Options

Already installed one and want to add the other?

### Add Agent to existing CLI install:
```bash
# If you have CLI, add Agent
cargo install mrapids-agent
# or
brew install mrapids-agent
# or  
npm install -g @microrapid/agent
```

### Add CLI to existing Agent install:
```bash
# If you have Agent, add CLI
cargo install mrapids
# or
brew install mrapids-cli
# or
npm install -g @microrapid/cli
```

---

## ❓ FAQ

**Q: Can I install both separately and have them work together?**  
A: Yes! They're independent binaries that can be installed separately.

**Q: Will installing the suite take more space than installing separately?**  
A: No, the suite just installs both binaries. Same total size.

**Q: Can I uninstall one without affecting the other?**  
A: Yes, they're completely independent.

**Q: Do they share any configuration?**  
A: No, `mrapids` uses `.mrapids.yaml` and `mrapids-agent` uses `.mrapids/` directory.

**Q: Which is more popular?**  
A: CLI (`mrapids`) for general developers, Agent (`mrapids-agent`) for AI developers.

---

## 🎯 Recommendation

- **Start with CLI only** if you're new to MicroRapid
- **Add Agent later** when you need AI capabilities
- **Install both** if you're building a team platform

Remember: You can always add the other component later!