# Build Artifacts and Distribution Explanation

## What Gets Built

When you run `cargo build --release`, you get these artifacts:

### 1. **Main Executables** (What users install)
```
target/release/
├── mrapids         (13.6 MB) - Main CLI tool
└── mrapids-agent   (11.7 MB) - MCP server daemon
```

### 2. **Library Files** (For developers)
```
target/release/
├── libmrapids.rlib       (16.2 MB) - Rust library
└── libmrapids_agent.rlib (718 KB)  - Agent library
```

## What's Included in the Installable

### ✅ **INCLUDED** in Distribution:

#### Binary Executables Only:
```
/usr/local/bin/
├── mrapids         # Main CLI executable
└── mrapids-agent   # MCP server executable
```

#### Embedded Resources:
- **Example specs**: Compiled into the binary (from `include_str!`)
- **Default configs**: Embedded as string literals
- **Error messages**: Part of the compiled code
- **Help text**: Built into the binary

### ❌ **NOT INCLUDED** in Distribution:

1. **`/data/` folder** - Documentation and analysis files
2. **`/docs/` folder** - Development documentation  
3. **`/tests/` folder** - Test scripts
4. **`/examples/` folder** - Example files (unless embedded)
5. **Source code** (`/src/`, `/agent/src/`)
6. **Cargo files** (`Cargo.toml`, `Cargo.lock`)
7. **Git files** (`.git/`, `.gitignore`)
8. **Development files** (`*.md`, `Makefile`)

## Installation Methods

### 1. **Binary Release** (Smallest)
```bash
# What users download:
mrapids-v0.1.0-darwin-amd64.tar.gz (15 MB)
├── mrapids
├── mrapids-agent
└── README.md

# After extraction:
sudo cp mrapids /usr/local/bin/
sudo cp mrapids-agent /usr/local/bin/
```

### 2. **Homebrew** (macOS)
```bash
brew install mrapids
# Installs only the binaries to /usr/local/bin/
```

### 3. **Cargo Install** (From crates.io)
```bash
cargo install mrapids
# Builds from source, installs only binaries
```

### 4. **Package Managers** (Linux)
```bash
# .deb package contains:
/usr/bin/mrapids
/usr/bin/mrapids-agent
/usr/share/doc/mrapids/README.md
/usr/share/man/man1/mrapids.1.gz
```

## Runtime File Creation

When users run `mrapids-agent init`, it creates:
```
.mrapids/                    # Created at runtime
├── mcp-server.toml         # Generated from embedded template
├── policy.yaml             # Generated from embedded template
├── api.yaml                # Generated from embedded template
└── auth/
    └── example.toml        # Generated from embedded template
```

## Size Breakdown

### Binary Sizes (Release Build):
- **mrapids**: ~13.6 MB
  - Includes: HTTP client, OpenAPI parser, JSON/YAML parsers
  - Statically linked Rust runtime
  
- **mrapids-agent**: ~11.7 MB
  - Includes: JSON-RPC server, policy engine, auth system
  - Statically linked dependencies

### Why Are They Large?
1. **Static Linking**: All dependencies compiled in
2. **No Runtime Required**: Users don't need Rust installed
3. **Feature-Rich**: Includes full HTTP client, crypto, parsers
4. **Cross-Platform**: Same binary works everywhere

## Distribution Best Practices

### What We Ship:
```yaml
Essential:
  - mrapids binary
  - mrapids-agent binary
  - Basic README
  - LICENSE file

Optional (in docs package):
  - Man pages
  - Shell completions
  - Examples (as separate download)
```

### What We Don't Ship:
```yaml
Development Only:
  - /data/* - Analysis and test results
  - /docs/* - Developer documentation
  - /tests/* - Test suites
  - Source code
  - Build files
```

## Summary

**For end users**, the installable is just:
- 2 executable files (~25 MB total)
- Everything else is generated at runtime or downloaded separately
- The `/data/` folder and other development files are **never** distributed

This keeps the distribution small, secure, and focused on what users actually need to run the tools.