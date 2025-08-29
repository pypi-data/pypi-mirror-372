# CI/CD Pipeline Documentation

## Overview

MicroRapids API Runtime uses a comprehensive CI/CD pipeline with GitHub Actions to ensure code quality, security, and reliable deployments across different environments.

## Branch Strategy

```mermaid
gitGraph
    commit
    branch develop
    checkout develop
    commit
    branch feature/new-feature
    checkout feature/new-feature
    commit
    commit
    checkout develop
    merge feature/new-feature
    checkout main
    merge develop
    branch release/v1.0
    checkout release/v1.0
    commit
    checkout main
    merge release/v1.0
    tag v1.0.0
    branch hotfix/critical-fix
    checkout hotfix/critical-fix
    commit
    checkout main
    merge hotfix/critical-fix
    tag v1.0.1
```

### Branch Types

| Branch | Purpose | Deploy To | Auto Deploy |
|--------|---------|-----------|-------------|
| `main` | Production-ready code | Staging | Yes |
| `develop` | Integration branch | Development | Yes |
| `feature/*` | New features | Preview (on label) | No |
| `release/*` | Release preparation | Staging | Yes |
| `hotfix/*` | Emergency fixes | Production | Manual |

## Workflows

### 1. Feature Branch CI/CD (`feature-branch.yml`)

**Triggers:**
- Push to `feature/**`, `feat/**`, `enhancement/**`
- Pull requests to `main` or `develop`

**Jobs:**
- **Quick Check**: Validates commit messages and file sizes
- **Security**: Runs secret scanning and security audit
- **Quality**: Checks formatting, linting, and documentation
- **Test Matrix**: Runs tests on multiple OS and Rust versions
- **Integration Tests**: Tests with external services
- **Coverage**: Generates code coverage reports
- **Benchmarks**: Runs performance benchmarks (if labeled)
- **Build Artifacts**: Creates deployable artifacts
- **Deploy Preview**: Deploys to preview environment (if labeled)

### 2. PR Validation (`pr-validation.yml`)

**Triggers:**
- PR opened, edited, synchronized, or reopened
- PR review submitted
- Issue comments (for commands)

**Features:**
- Validates PR title follows conventional commits
- Checks PR description completeness
- Auto-labels based on changed files
- Detects merge conflicts
- Handles slash commands (`/retest`, `/format`, `/benchmark`, etc.)
- Auto-assigns reviewers based on code ownership
- Generates PR summary

### 3. Security Checks (`security.yml`)

**Triggers:**
- Push to `main` or `production`
- Pull requests
- Weekly schedule (Mondays at 9 AM UTC)
- Manual dispatch

**Scans:**
- **Secret Detection**: TruffleHog and Gitleaks
- **Vulnerability Audit**: cargo-audit
- **License Compliance**: cargo-license
- **Supply Chain**: SBOM generation
- **Outdated Dependencies**: cargo-outdated

### 4. Deployment Pipeline (`deploy.yml`)

**Triggers:**
- Manual workflow dispatch
- Push to `main` or `develop`
- Git tags (`v*`)
- GitHub releases

**Environments:**
- **Development**: Auto-deploy from `develop` branch
- **Staging**: Auto-deploy from `main` branch
- **Production**: Deploy from tags/releases with approval

**Features:**
- Blue-green deployment for production
- Automatic rollback on failure
- Smoke tests and E2E tests
- Performance monitoring
- Notification system

### 5. Test Suite (`test-suite.yml`)

**Triggers:**
- Manual dispatch
- Nightly schedule (2 AM UTC)
- Push to feature/test branches

**Test Types:**
- **Unit Tests**: Multiple feature combinations
- **Integration Tests**: With PostgreSQL and Redis
- **Fuzz Testing**: Security-focused fuzzing
- **Property Tests**: Property-based testing
- **Mutation Tests**: Code mutation testing
- **Stress Tests**: Load and performance testing
- **Compatibility Tests**: Multiple OS and Rust versions
- **Security Tests**: Vulnerability and unsafe code checks
- **Performance Tests**: Regression testing

## Environment Configuration

### Development
```yaml
Environment: development
URL: https://dev.api.microrapids.com
Auto-deploy: Yes (from develop branch)
Approval: Not required
```

### Staging
```yaml
Environment: staging
URL: https://staging.api.microrapids.com
Auto-deploy: Yes (from main branch)
Approval: Not required
Tests: E2E, Performance
```

### Production
```yaml
Environment: production
URL: https://api.microrapids.com
Auto-deploy: No
Approval: Required
Tests: Smoke, Health checks
Deployment: Blue-green with automatic rollback
```

## PR Commands

Available slash commands in pull requests:

| Command | Description | Permission |
|---------|-------------|------------|
| `/retest` | Re-run CI tests | Write |
| `/format` | Run auto-formatter | Write |
| `/benchmark` | Run performance benchmarks | Write |
| `/approve` | Approve the PR | Write |
| `/deploy preview` | Deploy to preview environment | Write |
| `/help` | Show available commands | Any |

## Docker Support

### Building Images

```bash
# Build development image
docker build -t mrapids:dev .

# Build with specific version
docker build --build-arg VERSION=1.0.0 --build-arg COMMIT=$(git rev-parse HEAD) -t mrapids:1.0.0 .
```

### Running with Docker Compose

```bash
# Start all services
docker-compose up -d

# Start with development profile
docker-compose --profile dev up -d

# View logs
docker-compose logs -f mrapids

# Stop services
docker-compose down
```

## Local Development

### Prerequisites

1. Install Rust toolchain:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

2. Install security tools:
```bash
./scripts/security-setup.sh
```

3. Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### Running Tests Locally

```bash
# Run all tests
cargo test --all-features

# Run specific test suite
cargo test --lib
cargo test --doc
cargo test --tests

# Run with coverage
cargo tarpaulin --all-features --out html

# Run benchmarks
cargo bench

# Run security audit
cargo audit
cargo deny check
```

## Deployment Process

### Feature Branch → Development

1. Create feature branch from `develop`
2. Make changes and push
3. CI runs automatically
4. Create PR to `develop`
5. PR validation runs
6. After approval and merge, auto-deploys to development

### Development → Staging

1. Create PR from `develop` to `main`
2. Run comprehensive tests
3. After approval and merge, auto-deploys to staging
4. Run E2E and performance tests

### Staging → Production

1. Create release branch from `main`
2. Update version and changelog
3. Create and push tag
4. Create GitHub release
5. Manual approval required
6. Blue-green deployment with monitoring
7. Automatic rollback if health checks fail

## Monitoring and Observability

### Metrics (Prometheus)
- Available at: http://localhost:9090 (local)
- Collects application and system metrics
- 15-second scrape interval

### Visualization (Grafana)
- Available at: http://localhost:3000 (local)
- Default credentials: admin/admin
- Pre-configured dashboards for API metrics

### Tracing (Jaeger)
- UI available at: http://localhost:16686 (local)
- Distributed tracing for request flows
- Performance bottleneck identification

## Security

### Automated Security Checks

- **Every PR**: Secret scanning, vulnerability audit
- **Weekly**: Full security suite including OWASP checks
- **Pre-commit**: Local security validation
- **Dependencies**: Automated updates via Dependabot

### Security Tools

| Tool | Purpose | When |
|------|---------|------|
| Gitleaks | Secret detection | Pre-commit, CI |
| TruffleHog | Secret scanning | CI |
| cargo-audit | Vulnerability check | Pre-commit, CI |
| cargo-deny | License/security policy | CI |
| OWASP | Dependency check | Weekly |

## Troubleshooting

### Common Issues

1. **CI Failing on Format**
   ```bash
   cargo fmt --all
   ```

2. **Security Audit Failures**
   ```bash
   cargo update
   cargo audit fix
   ```

3. **Large File Rejection**
   - Files over 1MB are rejected
   - Use Git LFS for large files

4. **PR Title Validation**
   - Must follow: `type(scope): description`
   - Valid types: feat, fix, docs, style, refactor, perf, test, chore

### Getting Help

- Check CI logs in GitHub Actions tab
- Review `docs/CI-CD.md` (this file)
- Use `/help` command in PRs
- Open an issue for CI/CD problems

## Best Practices

1. **Keep PRs Small**: Easier to review and test
2. **Write Tests**: Maintain >80% code coverage
3. **Update Documentation**: Keep docs in sync with code
4. **Use Conventional Commits**: Helps with automation
5. **Security First**: Never commit secrets or credentials
6. **Monitor Performance**: Check benchmark results
7. **Clean Git History**: Squash commits when merging

## Contact

For CI/CD issues or improvements:
- Create an issue with `ci/cd` label
- Contact: devops@microrapids.com

---

Last Updated: August 2025
Version: 1.0