# Request Security Warnings

MicroRapid now includes optional security warnings for outgoing API requests. This feature helps developers identify potentially dangerous patterns in their test data without blocking legitimate testing scenarios.

## Overview

The request analyzer examines:
- Headers for CRLF injection patterns
- URL parameters for SQL/NoSQL injection patterns
- Request bodies for malicious payloads
- File paths for directory traversal attempts
- All inputs for XSS and command injection patterns

## Warning Categories

### High Severity
- **SQL Injection**: Patterns like `'; DROP TABLE`, `UNION SELECT`, etc.
- **NoSQL Injection**: MongoDB operators like `$where`, `$ne`, `$regex`
- **CRLF Injection**: Carriage return/line feed in headers
- **Path Traversal**: Patterns like `../`, `..\\`, encoded variants

### Medium Severity  
- **Command Injection**: Shell metacharacters (`;`, `|`, `&`, backticks)
- **XSS Attempts**: HTML/JavaScript patterns (`<script>`, `javascript:`)
- **SQL-like syntax**: Found in non-query contexts

### Low Severity
- **Suspicious Patterns**: Very large numbers, unusual data formats
- **HTML in JSON**: May indicate stored XSS testing

## Usage

Warnings are shown by default when suspicious patterns are detected:

```bash
# This will show a SQL injection warning
mrapids run get-user --id "1; DROP TABLE users;--"

# Output includes:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ REQUEST SECURITY WARNINGS ⚠️
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HIGH SEVERITY:
  ● Parameter: id - Parameter contains SQL injection patterns

These warnings are informational. Your request will still be sent.
Use --no-warnings to suppress these messages.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Suppressing Warnings

Add `--no-warnings` to any command to suppress security warnings:

```bash
mrapids run get-user --id "1; DROP TABLE users;--" --no-warnings
mrapids test --all --no-warnings
```

## Philosophy

MicroRapid is a developer tool that trusts its users. These warnings:
- **Don't block requests** - You can test edge cases and vulnerabilities
- **Are educational** - Help identify potential security issues
- **Are optional** - Can be suppressed when not needed
- **Don't sanitize** - Your data is sent exactly as specified

This approach maintains the tool's utility for:
- Security researchers testing vulnerabilities
- QA engineers testing error handling
- Developers debugging encoding issues
- API security testing

## Implementation Details

The warning system uses regex patterns to detect common attack vectors:
- SQL: `UNION SELECT`, `DROP TABLE`, `OR '1'='1'`, etc.
- NoSQL: `$where`, `$ne`, `$gt`, `$regex`, etc.
- XSS: `<script>`, `javascript:`, `onerror=`, etc.
- Command: `;`, `|`, `&`, `$()`, backticks
- Path: `../`, `..\\`, URL-encoded variants

Patterns are case-insensitive where appropriate and cover common variations.