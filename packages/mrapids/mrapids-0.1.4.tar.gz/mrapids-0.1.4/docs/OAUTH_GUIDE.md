# OAuth 2.0 Authentication Guide

MicroRapid now supports OAuth 2.0 authentication, enabling you to work with modern APIs like GitHub, Google, Microsoft, and more. This guide will help you get started.

## Quick Start

### 1. Login to GitHub
```bash
# Set up your GitHub OAuth app credentials
export GITHUB_CLIENT_ID=your_client_id_here
export GITHUB_CLIENT_SECRET=your_client_secret_here

# Login
mrapids auth login github
# Browser opens → Authorize → Done!

# Use it
mrapids run list-repos --profile github
```

### 2. Login to Google
```bash
# Set up Google OAuth credentials
export GOOGLE_CLIENT_ID=your_client_id_here
export GOOGLE_CLIENT_SECRET=your_client_secret_here

# Login with custom scopes
mrapids auth login google --scopes "https://www.googleapis.com/auth/drive.readonly"

# Use it
mrapids run list-files --profile google
```

## Available Commands

### `auth login` - Authenticate with a provider
```bash
# Login to a known provider
mrapids auth login github
mrapids auth login google
mrapids auth login microsoft
mrapids auth login gitlab
mrapids auth login slack

# Login with custom profile name
mrapids auth login github --profile my-work-github

# Custom OAuth provider
mrapids auth login custom \
  --client-id YOUR_CLIENT_ID \
  --client-secret YOUR_CLIENT_SECRET \
  --auth-url https://auth.example.com/oauth/authorize \
  --token-url https://auth.example.com/oauth/token \
  --scopes "read write" \
  --profile my-api
```

### `auth list` - Show stored profiles
```bash
# Simple list
mrapids auth list

# Detailed view with timestamps
mrapids auth list --detailed
```

### `auth show` - View profile details
```bash
# Show profile info
mrapids auth show github

# Show tokens (WARNING: sensitive data)
mrapids auth show github --show-tokens
```

### `auth refresh` - Refresh expired tokens
```bash
# Manually refresh tokens
mrapids auth refresh github

# Note: Tokens are automatically refreshed when used
```

### `auth logout` - Remove authentication
```bash
# Remove a profile (with confirmation)
mrapids auth logout github

# Skip confirmation
mrapids auth logout github --force
```

### `auth test` - Verify authentication works
```bash
# Test if auth is working
mrapids auth test github
```

### `auth setup` - Show provider setup instructions
```bash
# Get setup help for any provider
mrapids auth setup github
mrapids auth setup google
```

## Provider Setup Instructions

### GitHub
1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - Application name: MicroRapid CLI (or your choice)
   - Homepage URL: http://localhost (or your website)
   - Authorization callback URL: `http://localhost:8899/callback`
4. Click "Register application"
5. Copy the Client ID and Client Secret
6. Export as environment variables:
   ```bash
   export GITHUB_CLIENT_ID=your_client_id
   export GITHUB_CLIENT_SECRET=your_client_secret
   ```

### Google
1. Go to https://console.cloud.google.com/apis/credentials
2. Create a new project or select existing
3. Click "Create Credentials" → "OAuth client ID"
4. Choose "Web application"
5. Add authorized redirect URI: `http://localhost:8899/callback`
6. Copy the Client ID and Client Secret
7. Export as environment variables:
   ```bash
   export GOOGLE_CLIENT_ID=your_client_id
   export GOOGLE_CLIENT_SECRET=your_client_secret
   ```

### Microsoft
1. Go to https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps
2. Click "New registration"
3. Fill in:
   - Name: MicroRapid CLI
   - Supported account types: Choose based on your needs
   - Redirect URI: Web → `http://localhost:8899/callback`
4. Click "Register"
5. Copy the Application (client) ID
6. Go to "Certificates & secrets" → "New client secret"
7. Export as environment variables:
   ```bash
   export MICROSOFT_CLIENT_ID=your_application_id
   export MICROSOFT_CLIENT_SECRET=your_client_secret
   ```

## Using OAuth with API Requests

### Basic Usage
```bash
# After login, use --profile with any run command
mrapids run get-user --profile github
mrapids run create-issue --profile github --data @issue.json
```

### Multiple Profiles
```bash
# Work account
mrapids auth login github --profile github-work

# Personal account  
mrapids auth login github --profile github-personal

# Use different profiles
mrapids run list-repos --profile github-work
mrapids run list-repos --profile github-personal
```

### With Environment Configuration
```yaml
# In config/development.yaml
apis:
  github:
    base_url: https://api.github.com
    # OAuth profile will override any auth here
```

## Security

### Token Storage
- Tokens are encrypted using AES-256-GCM
- Encryption keys are derived from machine-specific data
- Stored in `~/.mrapids/auth/tokens/`
- Files have restricted permissions (owner-only)

### Best Practices
1. **Never commit tokens** - The token files are encrypted but still sensitive
2. **Use environment variables** for client credentials
3. **Regularly refresh tokens** - Use `mrapids auth refresh` or let auto-refresh handle it
4. **Remove unused profiles** - Use `mrapids auth logout` when done
5. **Test authentication** - Use `mrapids auth test` to verify

### Token Expiration
- Tokens are automatically refreshed when expired
- Manual refresh available via `mrapids auth refresh`
- Check token status with `mrapids auth show --show-tokens`

## Troubleshooting

### "Port 8899 already in use"
Another instance of MicroRapid might be running the callback server. Wait a moment and try again.

### "State parameter mismatch"
This is a security feature. The authorization was not completed properly. Try logging in again.

### "No refresh token available"
Some providers don't issue refresh tokens on every auth. Try:
1. Logout: `mrapids auth logout <provider>`
2. Login again with proper scopes
3. For Google, the first login should prompt for offline access

### Browser doesn't open
If your browser doesn't open automatically:
1. Look for the URL in the terminal output
2. Copy and paste it into your browser manually
3. Complete the authorization flow

### Custom provider issues
For custom OAuth providers, ensure:
1. The redirect URI is exactly `http://localhost:8899/callback`
2. The provider supports the authorization code flow
3. PKCE is optional (MicroRapid uses it for added security)

## Examples

### GitHub API Workflow
```bash
# Setup and login
export GITHUB_CLIENT_ID=xxx
export GITHUB_CLIENT_SECRET=yyy
mrapids auth login github

# List your repositories
mrapids run list-user-repos --profile github

# Create an issue
cat > issue.json << EOF
{
  "title": "Found a bug",
  "body": "Description here"
}
EOF
mrapids run create-issue --profile github \
  --path-param owner=myorg \
  --path-param repo=myrepo \
  --data @issue.json
```

### Google Drive Example
```bash
# Login with Drive scope
mrapids auth login google \
  --scopes "https://www.googleapis.com/auth/drive.readonly"

# List files
mrapids run list-files --profile google
```

### Multiple Account Management
```bash
# Personal projects
mrapids auth login github --profile personal
mrapids run list-repos --profile personal > personal-repos.json

# Work projects
mrapids auth login github --profile work  
mrapids run list-repos --profile work > work-repos.json

# See all profiles
mrapids auth list --detailed
```

## Advanced Usage

### Custom Scopes
Different APIs require different scopes. Always request the minimum needed:

```bash
# GitHub - just public info
mrapids auth login github --scopes "read:user"

# GitHub - full repo access
mrapids auth login github --scopes "repo user"

# Google - multiple scopes
mrapids auth login google --scopes "openid email profile https://www.googleapis.com/auth/drive.readonly"
```

### Programmatic Usage
The auth profiles work seamlessly with all MicroRapid features:

```bash
# In scripts
for repo in $(mrapids run list-repos --profile github | jq -r '.[].name'); do
  echo "Processing $repo"
  mrapids run get-repo --profile github --path-param repo=$repo
done

# With setup-testsing
mrapids setup-tests api.yaml --format npm
# The generated npm scripts will respect --profile
```

### CI/CD Integration
For CI/CD, consider using API tokens directly instead of OAuth:

```bash
# Option 1: Direct token (for CI/CD)
mrapids run list-repos --auth "Bearer $GITHUB_TOKEN"

# Option 2: Pre-configured profile (for local dev)
mrapids run list-repos --profile github
```

## Summary

OAuth support in MicroRapid makes it easy to:
- 🔐 Authenticate with any OAuth 2.0 provider
- 🔄 Auto-refresh expired tokens
- 👥 Manage multiple accounts/profiles
- 🔒 Store tokens securely
- 🚀 Use modern APIs without managing tokens manually

Start with `mrapids auth login <provider>` and you're ready to go!