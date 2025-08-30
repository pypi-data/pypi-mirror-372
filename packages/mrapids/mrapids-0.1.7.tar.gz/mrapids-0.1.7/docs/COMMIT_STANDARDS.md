# Enterprise Commit Standards & Development Guidelines

## Commit Message Convention

### Standard Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Commit Types

| Type     | Description             | Example                                         |
|----------|-------------------------|-------------------------------------------------|
| feat     | New feature             | feat(auth): add OAuth 2.0 support              |
| fix      | Bug fix                 | fix(parser): handle empty responses correctly   |
| perf     | Performance improvement | perf(runtime): optimize parallel execution      |
| refactor | Code refactoring        | refactor(client): extract retry logic          |
| docs     | Documentation           | docs(api): update OpenAPI examples             |
| test     | Testing                 | test(e2e): add GraphQL integration tests       |
| build    | Build system            | build(deps): upgrade tokio to 1.40             |
| ci       | CI/CD changes           | ci(github): add security scanning              |
| chore    | Maintenance             | chore(deps): update dependencies               |
| style    | Code style              | style(fmt): apply rustfmt changes              |
| revert   | Revert commit           | revert: feat(auth): add OAuth 2.0 support      |

### Scope Examples
```
feat(runtime): implement spec caching
fix(cli): correct argument parsing for parallel flag
perf(http): add connection pooling
docs(readme): add installation instructions
test(unit): add spec reader test cases
```

### Subject Rules
- Imperative mood: "add" not "added" or "adds"
- No capitalization: "add feature" not "Add feature"  
- No period: "add feature" not "add feature."
- Max 50 characters
- What, not why (why goes in body)

### Body Guidelines
```
feat(runtime): implement intelligent spec caching

- Add LRU cache with 100 spec limit
- Implement file watcher for auto-invalidation  
- Cache keys based on file hash + mtime
- Configurable TTL (default 5 minutes)

Performance impact:
- 10x faster subsequent runs
- Memory usage ~50MB for full cache
- Background cleanup every 60 seconds

Closes #123
```

### Footer Conventions
```
BREAKING CHANGE: rename execute() to run()

The execute() method has been renamed to run() for consistency
with CLI commands. Update all calls accordingly:

Before: runtime.execute(spec)
After: runtime.run(spec)

Fixes #456
Closes #789
See-also: #321
Co-authored-by: Jane Doe <jane@example.com>
Signed-off-by: John Smith <john@example.com>
```

## Commit Categories

### Feature Commits
```bash
# Simple feature
feat(auth): add API key authentication

# Complex feature with body
feat(runtime): add watch mode with hot reload

Implement file system watcher that monitors spec files
and automatically re-executes on changes.

- Debounce period: 100ms
- Supports glob patterns
- Excludes hidden files by default

Closes #234
```

### Bug Fix Commits
```bash
# Critical fix
fix(security): prevent path traversal in file loader

CVE-2024-1234: File loader allowed relative paths
that could access files outside project directory.

Security-Impact: High
Affected-Versions: < 1.2.3
Fixed-Version: 1.2.4

# Standard fix
fix(parser): handle null values in JSON response

Parser was failing when response contained null values
in optional fields. Now treats null as None.

Fixes #567
```

### Breaking Changes
```bash
feat(api)!: restructure plugin API

BREAKING CHANGE: Plugin trait methods now async

All plugin methods now return Future to support
async operations. Update plugins as follows:

Before:
  fn on_request(&self, req: Request) -> Result<()>
  
After:
  async fn on_request(&self, req: Request) -> Result<()>

Migration guide: docs/migration/v2-to-v3.md
```

### Performance Commits
```bash
perf(http): implement connection pooling

Add connection pooling to reuse TCP connections
across requests to the same host.

Benchmark results:
- Throughput: +40% (1200 → 1680 req/s)
- Latency p99: -25% (100ms → 75ms)
- Memory: +5MB for pool overhead

Configuration:
- Max connections per host: 10
- Idle timeout: 60s
- Connection TTL: 300s
```

## Advanced Commit Patterns

### Multi-scope Changes
```bash
refactor(runtime,cli): extract shared configuration

Move configuration logic from CLI into runtime module
to enable programmatic usage without CLI dependency.
```

### Dependency Updates
```bash
build(deps): update critical dependencies

Security updates:
- tokio 1.39.0 → 1.40.0 (RUSTSEC-2024-0001)
- openssl 0.10.63 → 0.10.64

Feature updates:
- reqwest 0.11 → 0.12 (HTTP/3 support)
- clap 4.4 → 4.5 (improved error messages)

BREAKING CHANGE: reqwest 0.12 requires rustls feature
```

### Revert Commits
```bash
revert: fix(parser): add timeout to requests

This reverts commit abc123def456.

The timeout implementation was causing false positives
in slow network conditions. Need to redesign with
configurable backoff strategy.

Re-opens #789
```

## Git Workflow Standards

### Branch Naming
```bash
# Feature branches
feature/add-graphql-support
feature/JIRA-1234-oauth-integration

# Bug fixes
fix/connection-pool-leak
fix/BUG-5678-null-pointer

# Refactoring
refactor/extract-http-client
refactor/TECH-910-modularize-runtime

# Releases
release/v1.2.0
release/2024-Q1

# Hotfixes
hotfix/v1.2.1
hotfix/critical-security-patch
```

### PR Title Format
```
[JIRA-1234] feat(runtime): add caching support
[BUG-5678] fix(parser): handle edge cases
[TECH-910] refactor: improve error handling
[SECURITY] fix: patch CVE-2024-1234
```

## Development Standards

### Code Review Checklist
```markdown
## Review Checklist
- [ ] Commit messages follow convention
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No security vulnerabilities
- [ ] Performance impact assessed
- [ ] Breaking changes documented
- [ ] Error handling comprehensive
- [ ] Logs and metrics added
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen/commitizen
    hooks:
      - id: commitizen
        stages: [commit-msg]
        
  - repo: local
    hooks:
      - id: rust-linting
        name: Rust linting
        entry: cargo clippy -- -D warnings
        language: system
        files: \.rs$
        
      - id: rust-formatting
        name: Rust formatting
        entry: cargo fmt -- --check
        language: system
        files: \.rs$
        
      - id: test-runner
        name: Run tests
        entry: cargo test
        language: system
        pass_filenames: false
```

### Semantic Versioning
```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)

Examples:
1.0.0 → 2.0.0  (BREAKING CHANGE)
1.0.0 → 1.1.0  (feat: new feature)
1.0.0 → 1.0.1  (fix: bug fix)
```

## Enterprise Integration

### JIRA Integration
```bash
# Link to JIRA tickets
feat(API-1234): implement retry mechanism

Implements exponential backoff retry for failed requests
as specified in API-1234.

JIRA: API-1234
```

### Security Commits
```bash
fix(security): patch SQL injection vulnerability

[SECURITY ADVISORY]
Severity: CRITICAL
CVE: CVE-2024-12345
CVSS: 9.8

Sanitize user input in query builder to prevent
SQL injection attacks.

Reported-by: security@example.com
Fixed-by: security-team@company.com
```

### Compliance Commits
```bash
feat(compliance): add GDPR data retention

Implement automatic data deletion after retention
period as required by GDPR Article 17.

Compliance: GDPR-ART17
Audit-Trail: AUDIT-2024-Q1-023
Reviewed-by: legal@company.com
```

## Metrics and Tracking

### Commit Metrics
Tracking:
- Commit frequency per developer
- Average commit size (lines changed)
- Time between commit and review
- Commit message quality score
- Fix commit ratio (bugs per feature)

### Automated Validation
```json
{
  "rules": {
    "header-max-length": [2, "always", 72],
    "type-enum": [2, "always", [
      "feat", "fix", "docs", "style",
      "refactor", "perf", "test", "build",
      "ci", "chore", "revert"
    ]],
    "scope-case": [2, "always", "lower-case"],
    "subject-case": [2, "always", "lower-case"],
    "subject-empty": [2, "never"],
    "subject-full-stop": [2, "never", "."],
    "body-leading-blank": [2, "always"],
    "footer-leading-blank": [2, "always"]
  }
}
```

## Commit Examples by Scenario

### Feature Development
```bash
# Initial implementation
feat(runtime): add basic spec execution

# Enhancement
feat(runtime): add parallel execution support

# Configuration
feat(runtime): make timeout configurable
```

### Bug Fixing
```bash
# Investigation
test(runtime): add failing test for issue #123

# Fix
fix(runtime): correct timeout calculation

# Verification
test(runtime): verify timeout fix
```

### Refactoring
```bash
# Preparation
test(client): add tests for current behavior

# Refactor
refactor(client): extract retry logic to middleware

# Cleanup
chore(client): remove deprecated methods
```

## Validation Tools

### commitlint Configuration
```javascript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'header-max-length': [2, 'always', 72],
    'scope-enum': [2, 'always', [
      'runtime', 'cli', 'parser', 'http',
      'auth', 'cache', 'plugin', 'config'
    ]],
    'type-enum': [2, 'always', [
      'feat', 'fix', 'perf', 'refactor',
      'docs', 'test', 'build', 'ci',
      'chore', 'style', 'revert'
    ]]
  }
};
```

### Git Aliases
```bash
# ~/.gitconfig
[alias]
  # Conventional commits
  feat = "!f() { git commit -m \"feat($1): $2\"; }; f"
  fix = "!f() { git commit -m \"fix($1): $2\"; }; f"
  docs = "!f() { git commit -m \"docs($1): $2\"; }; f"
  refactor = "!f() { git commit -m \"refactor($1): $2\"; }; f"
  
  # Utilities
  last = log -1 HEAD --stat
  unstage = reset HEAD --
  visual = !gitk
  changelog = log --pretty=format:'* %s (%h)' --no-merges
```

## Quick Reference

### Common Patterns
```bash
# Feature with tests
feat(module): add new capability
test(module): add tests for new capability

# Bug fix with regression test
fix(module): resolve edge case
test(module): prevent regression of edge case

# Performance with benchmarks
perf(module): optimize algorithm
test(bench): add performance benchmarks

# Breaking change
feat(api)!: restructure public interface
BREAKING CHANGE: detailed migration instructions

# Security patch
fix(security): patch vulnerability CVE-2024-1234
```

### Commit Workflow
1. Make changes
2. Run tests: `cargo test`
3. Format code: `cargo fmt`
4. Lint code: `cargo clippy`
5. Stage changes: `git add .`
6. Commit with message: `git commit`
7. Push to branch: `git push origin feature/branch-name`

This comprehensive guide ensures consistent, traceable, and professional commit history suitable for enterprise environments with audit requirements and compliance needs.