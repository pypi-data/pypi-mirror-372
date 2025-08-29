# Explore Command - Quick Reference

## 🔍 What It Does

Instantly search API operations by keyword - like Google for your API spec.

## 🚀 Quick Start

```bash
# Basic search
mrapids explore payment

# Multi-word search  
mrapids explore "reset password"

# Show descriptions
mrapids explore user --detailed
```

## 📊 Search Scope

The command searches across:
- ✅ Operation IDs (`CreatePayment`, `GetUser`)
- ✅ Paths (`/payments`, `/users/{id}`)
- ✅ Summaries (short descriptions)
- ✅ Tags (categories)
- ✅ Descriptions (detailed text)

## 🎯 Common Searches

| Find | Command |
|------|---------|
| All user endpoints | `mrapids explore user` |
| Payment operations | `mrapids explore payment` |
| Authentication | `mrapids explore auth` |
| List operations | `mrapids explore list` |
| Create operations | `mrapids explore create` |
| Webhooks | `mrapids explore webhook` |
| All operations | `mrapids explore ""` |

## ⚡ Options

| Option | Purpose | Example |
|--------|---------|---------|
| `--limit` | Show more results | `explore user --limit 20` |
| `--detailed` | Include descriptions | `explore payment --detailed` |
| `--spec` | Use specific file | `explore auth --spec v2/api.yaml` |
| `--format` | Change output | `explore user --format json` |

## 📤 Output Formats

### Pretty (Default)
```
🔍 Exploring operations matching: payment

📌 Exact Matches (2)
  • CreatePayment - POST /payments
  • GetPaymentStatus - GET /payments/{id}/status
```

### Simple
```
CreatePayment POST /payments
GetPaymentStatus GET /payments/{id}/status
```

### JSON
```json
{
  "keyword": "payment",
  "results": [...]
}
```

## 🔧 Power User Tips

### Find and Run
```bash
# Search for operation
mrapids explore "create user" --format simple

# Run it
mrapids run CreateUser --data '{"name": "John"}'
```

### List All POST Operations
```bash
mrapids explore "" --format json | \
  jq '.results[] | select(.method == "POST")'
```

### Search Multiple Keywords
```bash
# Find payment OR subscription
mrapids explore payment
mrapids explore subscription
```

### Generate Documentation
```bash
# All endpoints to file
mrapids explore "" --format json > endpoints.json

# Markdown list
mrapids explore "" --format simple | \
  awk '{print "- `" $1 "` - " $2 " " $3}' > endpoints.md
```

## 💡 Search Strategies

1. **Can't remember exact name?**
   ```bash
   # Try concept
   mrapids explore authentication
   mrapids explore auth
   mrapids explore login
   ```

2. **Building a feature?**
   ```bash
   # Find all related endpoints
   mrapids explore order
   mrapids explore payment
   mrapids explore shipping
   ```

3. **Learning the API?**
   ```bash
   # See everything with descriptions
   mrapids explore "" --detailed --limit 50
   ```

4. **Finding patterns?**
   ```bash
   # All list operations
   mrapids explore list
   
   # All delete operations  
   mrapids explore delete
   ```

## 🎮 Workflow Examples

### Development Flow
```bash
# 1. Find endpoint
mrapids explore "user profile"

# 2. Check details
mrapids show GetUserProfile

# 3. Test it
mrapids run GetUserProfile --id 123
```

### Integration Flow
```bash
# 1. Discover capabilities
mrapids explore payment --detailed

# 2. Find webhooks
mrapids explore "payment webhook"

# 3. Generate SDK
mrapids gen sdk --operations CreatePayment,GetPaymentStatus
```

## ⚡ Performance

- Instant results (<100ms)
- Works offline
- No API keys needed
- Handles large specs (1000+ operations)

## 🚦 Exit Codes

- `0` - Success (even if no results)
- `1` - Error (spec not found, invalid format)

## 📚 Related Commands

After finding operations:
- `mrapids show <operation>` - See full details
- `mrapids run <operation>` - Execute it
- `mrapids gen snippets -o <operation>` - Generate code