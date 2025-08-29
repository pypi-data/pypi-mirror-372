# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

## Reporting a Vulnerability

We take the security of MicroRapids API Runtime seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please do NOT:
- Create a public GitHub issue for security vulnerabilities
- Disclose the vulnerability publicly before it has been addressed

### Please DO:
- Email your findings to security@microrapids.com (or create a private security advisory on GitHub)
- Provide sufficient information to reproduce the problem
- Include the version of the software you are using
- Include any special configuration required to reproduce the issue

### What to expect:
- **Initial Response**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will assess the vulnerability and determine its severity within 5 business days
- **Fix Timeline**: For critical vulnerabilities, we aim to release a patch within 7 days
- **Communication**: We will keep you informed about the progress of addressing the vulnerability
- **Credit**: With your permission, we will acknowledge your contribution in the security advisory

## Security Update Process

1. Security patches are released as soon as possible after verification
2. We will publish a security advisory on GitHub
3. Update notifications will be sent through our standard channels

## Security Best Practices

When using MicroRapids API Runtime, we recommend:

### 1. Keep Dependencies Updated
- Regularly run `cargo update` to get the latest dependency patches
- Use `cargo audit` to check for known vulnerabilities
- Enable Dependabot alerts on your repository

### 2. API Security
- **Always use HTTPS** in production (use `--allow-insecure` flag only for local development)
- **Implement proper authentication** for all API endpoints
- **Use rate limiting** to prevent abuse
- **Validate all inputs** to prevent injection attacks

### 3. Policy Configuration
- Enable authentication by default in your policy files
- Use the principle of least privilege when defining access rules
- Regularly audit your policy rules
- Test policies using the built-in policy testing framework

### 4. Secure Storage
- Never commit sensitive data (API keys, passwords) to version control
- Use environment variables for configuration
- Encrypt sensitive data at rest
- Use secure credential storage solutions

### 5. Network Security
- The tool blocks SSRF attacks by default:
  - Private IP ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
  - Loopback addresses (127.0.0.0/8, ::1)
  - Link-local addresses (169.254.0.0/16)
  - Cloud metadata endpoints
- Never bypass these protections in production

### 6. Audit and Monitoring
- Enable audit logging for sensitive operations
- Monitor for suspicious patterns in request logs
- Set up alerts for repeated authentication failures
- Review security warnings from the request analyzer

## Known Security Features

MicroRapids API Runtime includes several built-in security features:

1. **SSRF Protection**: Automatic blocking of requests to private networks and metadata endpoints
2. **Injection Detection**: Real-time detection of SQL, NoSQL, Command, and XSS injection attempts
3. **Rate Limiting**: Configurable per-host and global rate limiting
4. **Policy Engine**: Fine-grained access control with authentication enforcement
5. **HTTPS Enforcement**: Warnings and optional blocking of insecure HTTP connections
6. **Path Traversal Protection**: Blocking of directory traversal attempts
7. **CRLF Injection Protection**: Detection and prevention of header injection attacks

## Security Checklist

Before deploying to production:

- [ ] All dependencies are up to date (`cargo audit` shows no vulnerabilities)
- [ ] HTTPS is enforced for all external API calls
- [ ] Authentication is required for sensitive operations
- [ ] Rate limiting is configured appropriately
- [ ] Input validation is enabled
- [ ] Audit logging is configured
- [ ] Secrets are stored securely (not in code or config files)
- [ ] Security policies are tested and documented
- [ ] Error messages don't leak sensitive information
- [ ] File permissions are properly restricted

## Vulnerability Disclosure Policy

We follow responsible disclosure practices:

1. Vulnerabilities are disclosed after a fix is available
2. We provide a 30-day window for users to update before public disclosure
3. Critical vulnerabilities may be disclosed sooner with mitigation steps
4. CVE identifiers will be requested for significant vulnerabilities

## Contact

For security concerns, please contact:
- Email: security@microrapids.com
- GitHub Security Advisories: [Create private advisory](https://github.com/microrapids/api-runtime/security/advisories/new)

## Acknowledgments

We thank the following researchers for responsibly disclosing security issues:
- *Your name could be here*

---

Last Updated: August 2025
Version: 1.0