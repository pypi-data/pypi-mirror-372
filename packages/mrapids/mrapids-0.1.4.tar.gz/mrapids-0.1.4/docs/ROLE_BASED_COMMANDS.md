# MicroRapid Commands by Role

## 👩‍💻 For Backend Developers

### "I need to..."

#### Test my new endpoint quickly
```bash
mrapids run api.yaml --operation myNewEndpoint --dry-run
mrapids run api.yaml --operation myNewEndpoint --param id=test123
```

#### Generate example data for my endpoint
```bash
mrapids analyze api.yaml
cat examples/requests/myNewEndpoint.json
```

#### See what parameters my endpoint needs
```bash
mrapids show myNewEndpoint --spec api.yaml
```

#### Generate TypeScript types from my spec
```bash
mrapids generate models api.yaml --language typescript
```

#### Check if I broke anything
```bash
mrapids diff api-main.yaml api-feature.yaml --breaking-only
```

## 🔧 For DevOps Engineers

### "I need to..."

#### Set up API testing in CI/CD
```bash
# In your CI pipeline:
mrapids validate api.yaml --strict || exit 1
mrapids test api.yaml --all --env $ENV || exit 1
mrapids diff api-prod.yaml api.yaml --breaking-only || exit 1
```

#### Configure multiple environments
```bash
mrapids init-config --env dev --base-url https://api.dev.company.com
mrapids init-config --env staging --base-url https://api.staging.company.com
mrapids init-config --env prod --base-url https://api.company.com
```

#### Monitor API health
```bash
# Cron job every 5 minutes:
mrapids test api.yaml --operation healthCheck --env prod || alert-team
```

#### Automate SDK deployment
```bash
mrapids sdk api.yaml --language typescript --package-name @company/api-client
npm publish ./sdk-typescript/
```

#### Debug production issues
```bash
mrapids run api.yaml --operation failingEndpoint --env prod --curl-output
mrapids run api.yaml --operation failingEndpoint --env prod --verbose
```

## 🧪 For QA Engineers

### "I need to..."

#### Create a test suite from scratch
```bash
mrapids setup-tests api.yaml --framework pytest
mrapids analyze api.yaml --output test-data/
```

#### Test all endpoints
```bash
mrapids test api.yaml --all --validate-response --report junit.xml
```

#### Test with different data sets
```bash
# Create test data files, then:
for file in test-data/*.json; do
  mrapids test api.yaml --operation createUser --data $file
done
```

#### Performance test an endpoint
```bash
mrapids test api.yaml --operation search \
  --iterations 1000 \
  --concurrent 50 \
  --duration 5m \
  --report perf-report.json
```

#### Validate API contract
```bash
# Test that responses match schema:
mrapids test api.yaml --all --validate-response --strict
```

#### Find what changed between releases
```bash
mrapids diff api-v1.0.yaml api-v2.0.yaml > changes.md
mrapids diff api-v1.0.yaml api-v2.0.yaml --breaking-only > breaking-changes.md
```

## 🎨 For Frontend Developers

### "I need to..."

#### Get the API client/SDK
```bash
mrapids sdk api.yaml --language typescript --output ./src/api-client
```

#### See available endpoints
```bash
mrapids list operations api.yaml --format table
```

#### Try an endpoint with real data
```bash
mrapids run api.yaml --operation getUser --param userId=123 --format json | jq .
```

#### Get example responses
```bash
mrapids analyze api.yaml
cat examples/responses/getUser.json
```

#### Mock API responses for development
```bash
mrapids analyze api.yaml --output ./mock-data
# Use mock-data/ files with your mock server
```

## 🔐 For Security Engineers

### "I need to..."

#### Validate API security
```bash
mrapids validate api.yaml --rules security-rules.yaml
```

#### Test authentication flows
```bash
mrapids auth test production-oauth
mrapids auth test api-key-auth
```

#### Audit API operations
```bash
# Find all admin operations:
mrapids list operations api.yaml --pattern "*/admin/*"

# Find operations without auth:
mrapids list operations api.yaml --format json | \
  jq '.operations[] | select(.security == null)'
```

#### Test with different auth profiles
```bash
mrapids test api.yaml --operation deleteUser --profile readonly-user
mrapids test api.yaml --operation deleteUser --profile admin-user
```

## 📊 For Product Managers

### "I need to..."

#### See what our API offers
```bash
mrapids list operations api.yaml --format table > api-inventory.txt
```

#### Check API compatibility
```bash
mrapids diff api-current.yaml api-proposed.yaml --format human
```

#### Generate API documentation
```bash
mrapids analyze api.yaml --with-docs
mrapids generate docs api.yaml --format markdown
```

## 💡 Universal Quick Tips

### Set up your environment once:
```bash
echo 'export MRAPIDS_SPEC=./api.yaml' >> ~/.bashrc
echo 'export MRAPIDS_ENV=dev' >> ~/.bashrc
echo 'alias mr=mrapids' >> ~/.bashrc
```

### Then just:
```bash
mr list operations
mr run --operation getUser
mr test --all
```

### For any role, remember:
- `--dry-run` to preview without executing
- `--help` on any command for details
- `--format json` for scriptable output
- `--verbose` when debugging

---

**The key insight**: Your OpenAPI spec is executable. Stop writing separate tests!