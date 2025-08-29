# MicroRapids API Runtime

High-performance API runtime built with Rust.

## Features

- 🚀 High-performance request processing
- 🔒 Built-in security policies
- 📊 Rate limiting and throttling
- 🌐 Multi-protocol support
- 📦 Available as Docker, NPM (WASM), and Python packages

## Quick Start

### Docker
```bash
docker pull ghcr.io/microrapids/api-runtime:latest
docker run -p 8080:8080 ghcr.io/microrapids/api-runtime:latest
```

### NPM (WebAssembly)
```bash
npm install @microrapids/api-runtime-wasm
```

### Python
```bash
pip install mrapids
```

### Rust
```toml
[dependencies]
mrapids = { git = "https://github.com/microrapids/api-runtime" }
```

## Documentation

See the [full documentation](https://github.com/microrapids/api-runtime/tree/main/docs) for detailed usage instructions.

## License

MIT