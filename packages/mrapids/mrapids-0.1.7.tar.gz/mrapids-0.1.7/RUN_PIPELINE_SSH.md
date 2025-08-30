# Running CI/CD Pipeline via SSH on AWS Runner

## Prerequisites
- SSH access to your AWS EC2 instance
- GitHub runner already installed and configured

## Step 1: SSH into your AWS EC2 Instance

```bash
# Replace with your actual EC2 instance details
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Or if you're using ec2-user
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

## Step 2: Navigate to Runner Work Directory

```bash
# The runner typically clones repos here
cd /home/ubuntu/actions-runner/_work/api-runtime/api-runtime

# Or check where your runner is installed
cd ~/actions-runner/_work/api-runtime/api-runtime

# If directory doesn't exist, clone the repo manually
git clone https://github.com/microrapids/api-runtime.git
cd api-runtime
```

## Step 3: Pull Latest Code

```bash
# Make sure you have the latest code
git pull origin main
```

## Step 4: Run Build and Test Pipeline Manually

```bash
# Navigate to api-runtime directory if not already there
cd api-runtime

# 1. Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# 2. Run formatting check
cargo fmt -- --check

# 3. Run clippy linter
cargo clippy -- -W clippy::all

# 4. Run tests
cargo test --all-features --release

# 5. Build release binary
cargo build --release --all-features

# 6. Create deployment artifact
VERSION=$(git rev-parse --short HEAD)
mkdir -p deployment
cp target/release/mrapids deployment/
cp README.md deployment/
cp SECURITY.md deployment/ 2>/dev/null || true

# Create version file
echo "{
  \"version\": \"${VERSION}\",
  \"commit\": \"$(git rev-parse HEAD)\",
  \"built_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
  \"built_by\": \"manual-ssh\"
}" > deployment/version.json

# Package it
tar -czf mrapids-${VERSION}-linux-x86_64.tar.gz -C deployment .
echo "✅ Build artifact created: mrapids-${VERSION}-linux-x86_64.tar.gz"
```

## Step 5: Build and Push Docker Image (Optional)

```bash
# Only if Docker is installed and you want to build images
docker --version

# Build Docker image
docker build -t mrapids:latest .

# Tag for GitHub Container Registry
docker tag mrapids:latest ghcr.io/microrapids/api-runtime:latest

# Login to GitHub Container Registry (needs PAT token)
echo $GITHUB_TOKEN | docker login ghcr.io -u microrapids --password-stdin

# Push image
docker push ghcr.io/microrapids/api-runtime:latest
```

## Step 6: Run Publishing Tasks (For Releases)

### NPM Package (WASM)
```bash
# Install wasm-pack
curl https://rustwasm.github.io/wasm-pack/installer/init.sh -sSf | sh

# Add wasm target
rustup target add wasm32-unknown-unknown

# Build WASM package
wasm-pack build --target nodejs --out-dir pkg --scope mrapids

# Update package.json
cd pkg
npm pkg set name="@mrapids/cli"
npm pkg set version="0.1.0"

# Publish to NPM (needs npm login)
npm login
npm publish --access public
cd ..
```

### Python Package
```bash
# Install Python and maturin
python3 -m pip install maturin

# Build Python wheels
maturin build --release --out dist

# Upload to PyPI (needs PyPI credentials)
# pip install twine
# twine upload dist/*
```

### Rust Crate
```bash
# Update Cargo.toml version if needed
# Then publish to crates.io (needs cargo login)
cargo login
cargo publish
```

## Step 7: Run Full Pipeline Script

Create a script to run everything:

```bash
cat > run_pipeline.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting CI/CD Pipeline on Self-Hosted Runner"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Navigate to api-runtime directory
cd api-runtime

# Step 1: Git Pull
print_info "Pulling latest changes..."
git pull origin main || print_error "Git pull failed"

# Step 2: Format Check
print_info "Checking code formatting..."
if cargo fmt -- --check; then
    print_status "Code formatting check passed"
else
    print_error "Code formatting check failed"
    cargo fmt
    print_info "Code has been formatted. Please commit the changes."
fi

# Step 3: Clippy
print_info "Running clippy linter..."
if cargo clippy -- -W clippy::all; then
    print_status "Clippy check passed"
else
    print_error "Clippy found issues"
fi

# Step 4: Run Tests
print_info "Running tests..."
if cargo test --all-features --release; then
    print_status "All tests passed"
else
    print_error "Some tests failed"
fi

# Step 5: Build Release
print_info "Building release binary..."
if cargo build --release --all-features; then
    print_status "Build successful"
    
    # Create artifact
    VERSION=$(git rev-parse --short HEAD)
    mkdir -p ../artifacts
    cp target/release/mrapids ../artifacts/mrapids-${VERSION}
    print_status "Binary saved to artifacts/mrapids-${VERSION}"
else
    print_error "Build failed"
    exit 1
fi

echo ""
echo "================================================"
echo -e "${GREEN}✅ Pipeline Complete!${NC}"
echo "================================================"

# Show summary
echo ""
echo "Summary:"
echo "--------"
ls -lh target/release/mrapids
echo ""
echo "Version: $(./target/release/mrapids --version || echo 'N/A')"
echo "Commit: $(git rev-parse HEAD)"
echo "Branch: $(git branch --show-current)"
echo "Time: $(date)"
EOF

chmod +x run_pipeline.sh
```

## Step 8: Run the Pipeline

```bash
./run_pipeline.sh
```

## Step 9: Monitor Runner Logs (Optional)

In another SSH session, you can monitor the GitHub Actions runner logs:

```bash
# Navigate to runner directory
cd ~/actions-runner

# Check runner status
./config.sh --check

# View runner service logs
journalctl -u actions.runner.microrapids-api-runtime.ip-172-31-45-95 -f

# Or if running interactively
./run.sh
```

## Automation with Cron (Optional)

Set up a cron job to run the pipeline periodically:

```bash
# Edit crontab
crontab -e

# Add this line to run every hour
0 * * * * cd /home/ubuntu/api-runtime && git pull && ./run_pipeline.sh >> /var/log/pipeline.log 2>&1

# Or run on push using a webhook listener
```

## Troubleshooting

### If Rust is not installed:
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

### If repository is not cloned:
```bash
cd ~
git clone https://github.com/microrapids/api-runtime.git
cd api-runtime
```

### If permissions are denied:
```bash
sudo chown -R $(whoami):$(whoami) ~/api-runtime
```

### Check installed tools:
```bash
echo "Checking installed tools..."
command -v cargo && cargo --version || echo "Cargo not installed"
command -v docker && docker --version || echo "Docker not installed"
command -v node && node --version || echo "Node not installed"
command -v python3 && python3 --version || echo "Python3 not installed"
```

## Direct GitHub Actions Runner Execution

If you want to trigger the actual GitHub Actions workflow locally:

```bash
# Install act (GitHub Actions local runner)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run workflows locally
act push -W .github/workflows/deploy.yml

# Or specific job
act -j build push
```

## Notes

- This manual process bypasses GitHub's billing restrictions
- You're essentially doing what the GitHub Actions runner would do
- Make sure all environment variables and secrets are set if needed
- Consider setting up proper logging and monitoring
- For production deployments, ensure proper security measures are in place