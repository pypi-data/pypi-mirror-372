# Direct Execution on Self-Hosted Runner

Since GitHub billing is blocking workflow dispatch, run directly on the runner:

## SSH into your AWS EC2 Runner

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

## Option 1: Use the GitHub Actions Runner directly

```bash
# Navigate to runner directory
cd ~/actions-runner

# Check runner status
./config.sh --check

# The runner work directory
cd _work/api-runtime/api-runtime

# If not exists, create it
mkdir -p _work/api-runtime/api-runtime
cd _work/api-runtime/api-runtime

# Clone or pull latest
git clone https://github.com/microrapids/api-runtime.git . || git pull origin main

# Navigate to the actual project
cd api-runtime

# Run the build
cargo build --release --all-features
cargo test --all-features
```

## Option 2: Use act (Local GitHub Actions)

```bash
# Install act
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Navigate to repository
cd ~/api-runtime

# Run the deployment pipeline locally
act push --job build -W .github/workflows/deploy.yml

# Or run specific jobs
act -j determine-environment push
act -j build push
```

## Option 3: Manual Pipeline Execution

```bash
# Run our quick pipeline script
cd ~/api-runtime
wget https://raw.githubusercontent.com/microrapids/api-runtime/main/quick_ssh_pipeline.sh
chmod +x quick_ssh_pipeline.sh
./quick_ssh_pipeline.sh
```

## Option 4: Create Local Workflow Runner

```bash
# Create a local runner script
cat > ~/run_workflow.sh << 'EOF'
#!/bin/bash

# This simulates what GitHub Actions would do

echo "🚀 Running Deployment Pipeline Locally"
echo "======================================"

# Set environment variables like GitHub Actions
export GITHUB_WORKFLOW="Deployment Pipeline"
export GITHUB_RUN_NUMBER="1"
export GITHUB_SHA=$(git rev-parse HEAD)
export GITHUB_REF="refs/heads/main"
export GITHUB_REPOSITORY="microrapids/api-runtime"
export RUNNER_OS="Linux"
export RUNNER_ARCH="X64"

# Navigate to repo
cd ~/api-runtime/api-runtime || cd ~/actions-runner/_work/api-runtime/api-runtime/api-runtime

# Pull latest
git pull origin main

# Determine environment (from deploy.yml logic)
if [[ "$GITHUB_REF" == "refs/heads/main" ]]; then
    export ENVIRONMENT="staging"
else
    export ENVIRONMENT="development"
fi

echo "Environment: $ENVIRONMENT"
echo "Version: $GITHUB_SHA"

# Build and Test
echo ""
echo "📦 Building and Testing..."
cargo test --all-features --release
cargo build --release --all-features

# Create artifact
VERSION=${GITHUB_SHA:0:7}
mkdir -p ~/deployment
cp target/release/mrapids ~/deployment/
echo "{
  \"version\": \"$VERSION\",
  \"commit\": \"$GITHUB_SHA\",
  \"built_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
  \"environment\": \"$ENVIRONMENT\"
}" > ~/deployment/version.json

tar -czf ~/mrapids-${VERSION}-linux-x86_64.tar.gz -C ~/deployment .

echo ""
echo "✅ Pipeline Complete!"
echo "Artifact: ~/mrapids-${VERSION}-linux-x86_64.tar.gz"
EOF

chmod +x ~/run_workflow.sh

# Run it
~/run_workflow.sh
```

## Monitor Runner Activity

In another terminal, monitor the runner:

```bash
# Check if runner is processing jobs
ps aux | grep Runner.Listener

# Check runner logs
journalctl -u actions.runner.* -f

# Or check the runner directly
cd ~/actions-runner
tail -f _diag/*.log
```

## Testing the Runner Connection

```bash
# On the runner machine
cd ~/actions-runner

# Test configuration
./config.sh --check

# Run interactively to see what's happening
./run.sh

# You should see:
# √ Connected to GitHub
# Current runner version: 'x.xxx.x'
# Listening for Jobs
```

## If Runner is Not Picking Up Jobs

1. **Re-configure the runner:**
```bash
cd ~/actions-runner
./config.sh remove --token YOUR_REMOVE_TOKEN
./config.sh --url https://github.com/microrapids/api-runtime --token YOUR_NEW_TOKEN
```

2. **Check runner service:**
```bash
sudo systemctl status actions.runner.microrapids-api-runtime.ip-172-31-45-95
sudo systemctl restart actions.runner.microrapids-api-runtime.ip-172-31-45-95
```

3. **Check network connectivity:**
```bash
curl -I https://github.com
curl -I https://api.github.com
```

## Note

The billing issue is preventing GitHub from dispatching jobs to ANY runner (including self-hosted). Until this is resolved:
1. Run pipelines manually via SSH
2. Fix the billing issue at https://github.com/settings/billing
3. Or convert to a GitHub Organization with self-hosted runner support