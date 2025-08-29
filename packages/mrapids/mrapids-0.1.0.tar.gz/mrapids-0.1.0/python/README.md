# MicroRapid Python Package

Install MicroRapid CLI tools via pip:

```bash
pip install microrapid
```

This will install both `mrapids` and `mrapids-agent` commands.

## Usage

```bash
# Initialize a new project
mrapids init

# Run an API operation
mrapids run --operation getUser --param id=123

# Start the MCP agent
mrapids-agent
```

## Supported Platforms

- macOS (x64, ARM64)
- Linux (x64)
- Windows (x64)

The appropriate binaries will be downloaded during installation.