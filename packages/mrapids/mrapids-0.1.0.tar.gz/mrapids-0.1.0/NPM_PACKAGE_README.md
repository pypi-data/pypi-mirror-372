# @mrapids/cli

Command-line interface for MicroRapids API Runtime - test and integrate APIs instantly.

## Installation

```bash
npm install -g @mrapids/cli
```

## Usage

```bash
# Initialize a new project
mrapids init my-api

# List available operations
mrapids list operations api.yaml

# Execute an API operation
mrapids run getUser --param id=123

# Generate SDK
mrapids generate sdk --language typescript

# Test API endpoints
mrapids test --all
```

## Features

- 🚀 Direct API execution from OpenAPI specs
- 🔍 Smart API discovery
- 🧪 Built-in testing capabilities
- 📦 SDK generation for multiple languages
- 🔒 Secure authentication handling
- 📊 Response validation

## Documentation

Full documentation available at [https://microrapid.io/docs](https://microrapid.io/docs)

## Support

- GitHub Issues: [https://github.com/microrapids/api-runtime/issues](https://github.com/microrapids/api-runtime/issues)
- Discord: [https://discord.gg/microrapids](https://discord.gg/microrapids)
- Email: support@microrapid.io

## License

MIT