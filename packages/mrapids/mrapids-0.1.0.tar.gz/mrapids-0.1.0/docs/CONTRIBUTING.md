# Contributing to API-Runtime

Thank you for your interest in contributing to API-Runtime! This document provides guidelines and standards for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

### Prerequisites
- Rust 1.70+ (install via [rustup](https://rustup.rs/))
- Git
- A code editor with Rust support (VS Code with rust-analyzer recommended)

### Setup
```bash
# Clone the repository
git clone https://github.com/deepwissen/api-runtime.git
cd api-runtime

# Install development tools
cargo install cargo-watch cargo-audit cargo-deny

# Install pre-commit hooks
pip install pre-commit commitizen
pre-commit install
pre-commit install --hook-type commit-msg

# Configure git commit template
git config commit.template .gitmessage

# Build the project
cargo build

# Run tests
cargo test

# Run lints
cargo clippy -- -D warnings

# Format code
cargo fmt
```

## Development Standards

### Architecture
Please read [ARCHITECTURE.md](./ARCHITECTURE.md) for development principles. Key points:
- Follow the 3-3-3 rule (layers, parameters, nesting)
- Make it boring and obvious
- Test behavior, not implementation
- Start ugly, refactor later

### Code Style
We use automated formatting and linting:
```bash
# Format your code
cargo fmt

# Check lints
cargo clippy

# Check dependencies
cargo deny check
```

### Testing
Every contribution must include tests:
- Unit tests for business logic
- Integration tests for module interactions
- E2E tests for user-facing features

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_feature() {
        // Your test here
    }
}
```

## Contribution Process

### 1. Find or Create an Issue
- Check existing issues for something you'd like to work on
- Create a new issue if you've found a bug or have a feature request
- Comment on the issue to indicate you're working on it

### 2. Fork and Branch
```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/api-runtime.git
cd api-runtime
git remote add upstream https://github.com/deepwissen/api-runtime.git

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 3. Make Your Changes
- Follow the principles in [ARCHITECTURE.md](./ARCHITECTURE.md)
- Write boring, obvious code
- Add tests for user-visible behavior
- Update documentation if needed

### 4. Commit Your Changes
We follow strict commit message conventions for better traceability and automation. See [Commit Standards](./docs/COMMIT_STANDARDS.md) for detailed guidelines.

```bash
# Configure git to use our commit template
git config commit.template .gitmessage

# Format: type(scope): description
git commit -m "feat(parser): add GraphQL schema parsing"
git commit -m "fix(http): handle timeout errors properly"
git commit -m "docs(readme): update installation instructions"
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `perf`: Performance improvement  
- `refactor`: Code refactoring
- `docs`: Documentation
- `test`: Testing
- `build`: Build system
- `ci`: CI/CD changes
- `chore`: Maintenance
- `style`: Code style
- `revert`: Revert commit

For breaking changes, add `!` after type: `feat(api)!: restructure plugin interface`

### 5. Test Your Changes
```bash
# Run all tests
cargo test

# Run lints
cargo clippy -- -D warnings

# Format code
cargo fmt

# Check for security issues
cargo audit

# Check dependencies
cargo deny check
```

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what was changed and why
- Reference to related issue(s)
- Screenshots if applicable

## Pull Request Guidelines

### PR Checklist
- [ ] Code follows [ARCHITECTURE.md](./ARCHITECTURE.md) principles
- [ ] All tests pass (`cargo test`)
- [ ] Code is formatted (`cargo fmt`)
- [ ] No clippy warnings (`cargo clippy`)
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention
- [ ] PR description explains the change

### Review Process
1. Automated checks must pass
2. At least one maintainer review required
3. Address review feedback
4. Maintainer merges when approved

## Areas for Contribution

### High Priority
- **Parser Implementations**: OpenAPI, GraphQL, cURL parsers
- **Authentication Methods**: OAuth, JWT, custom auth
- **Platform Support**: Windows, macOS, Linux specific features
- **Documentation**: Examples, tutorials, guides

### Good First Issues
Look for issues labeled `good-first-issue` for beginner-friendly tasks.

### Feature Requests
Check issues labeled `enhancement` for feature ideas.

## Development Tips

### Running in Watch Mode
```bash
# Auto-run tests on file changes
cargo watch -x test

# Auto-run specific test
cargo watch -x "test test_name"

# Auto-compile on changes
cargo watch -x build
```

### Debugging
```rust
// Use debug prints during development
dbg!(&variable);

// Use tracing for structured logging
tracing::debug!("Processing request: {:?}", request);
```

### Performance Testing
```bash
# Run benchmarks
cargo bench

# Profile with flamegraph
cargo flamegraph
```

## Documentation

### Code Documentation
```rust
/// Brief description of the function.
///
/// # Arguments
/// * `param` - Description of parameter
///
/// # Returns
/// Description of return value
///
/// # Errors
/// Description of possible errors
///
/// # Examples
/// ```
/// let result = function(param);
/// ```
pub fn function(param: Type) -> Result<ReturnType> {
    // Implementation
}
```

### Architecture Documentation
Update architecture docs when making structural changes:
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Core principles and structure

## Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

### Release Checklist
1. Update version in `Cargo.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Create git tag
5. Push to GitHub
6. Create GitHub release
7. Publish to crates.io

## Getting Help

### Resources
- [Documentation](./docs/)
- [GitHub Issues](https://github.com/deepwissen/api-runtime/issues)
- [Discord Community](https://discord.gg/api-runtime)

### Questions?
- Check existing issues and discussions
- Ask in Discord for quick questions
- Create an issue for bugs or features

## Recognition

Contributors are recognized in:
- [CONTRIBUTORS.md](./CONTRIBUTORS.md)
- GitHub contributors page
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

---

Thank you for contributing to API-Runtime! Your efforts help make API testing better for everyone.