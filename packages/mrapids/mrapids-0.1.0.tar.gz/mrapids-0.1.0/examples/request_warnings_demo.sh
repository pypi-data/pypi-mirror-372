#!/bin/bash

echo "=== MicroRapid Request Security Warnings Demo ==="
echo ""
echo "This demo shows how MicroRapid warns about potentially dangerous request patterns"
echo ""

# SQL Injection warning
echo "1. SQL injection warning example:"
echo "   Command: mrapids run get-user --id \"1; DROP TABLE users;--\""
echo ""

# Command injection warning  
echo "2. Command injection warning example:"
echo "   Command: mrapids run execute --command \"ls; rm -rf /\""
echo ""

# XSS warning
echo "3. XSS attempt warning example:" 
echo "   Command: mrapids run create-comment --text \"<script>alert('XSS')</script>\""
echo ""

# Path traversal warning
echo "4. Path traversal warning example:"
echo "   Command: mrapids run get-file --path \"../../etc/passwd\""
echo ""

# Header injection warning
echo "5. Header injection warning example:"
echo "   Command: mrapids run api-call --header \"X-Custom: value\\r\\nX-Injected: evil\""
echo ""

# NoSQL injection warning
echo "6. NoSQL injection warning example:"
echo "   Command: mrapids run find-user --query '{\"username\": {\"$ne\": null}}'"
echo ""

echo "To suppress warnings, add --no-warnings flag:"
echo "   Command: mrapids run get-user --id \"1; DROP TABLE users;--\" --no-warnings"
echo ""
echo "Note: These warnings are informational only. The requests will still be sent."
echo "This helps developers identify potential security issues in their API testing."