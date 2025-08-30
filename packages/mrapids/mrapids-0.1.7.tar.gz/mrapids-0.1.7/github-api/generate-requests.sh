#!/bin/bash

# Generate request configs for common GitHub operations

echo "🚀 Generating MicroRapid Request Configurations"
echo "=============================================="

# Create directories
mkdir -p requests/github
mkdir -p data/github

# Common GET operations
operations_get=(
    "users/get-authenticated"
    "users/get-by-username"
    "repos/get"
    "repos/list-for-user"
    "repos/list-for-authenticated-user"
    "gists/list-for-authenticated-user"
    "issues/list-for-repo"
    "activity/list-repos-starred-by-authenticated-user"
    "activity/list-notifications-for-authenticated-user"
)

# Common POST operations
operations_post=(
    "gists/create"
    "repos/create-for-authenticated-user"
    "issues/create"
    "repos/create-fork"
    "activity/star-repo-for-authenticated-user"
)

# Common PUT operations
operations_put=(
    "users/follow"
    "activity/set-repo-subscription"
)

# Common DELETE operations
operations_delete=(
    "gists/delete"
    "activity/unstar-repo-for-authenticated-user"
    "users/unfollow"
)

echo -e "\n📁 Generating GET operations..."
for op in "${operations_get[@]}"; do
    echo "  - $op"
    ~/.cargo/bin/mrapids analyze --operation "$op" --force >/dev/null 2>&1
done

echo -e "\n📁 Generating POST operations..."
for op in "${operations_post[@]}"; do
    echo "  - $op"
    ~/.cargo/bin/mrapids analyze --operation "$op" --force >/dev/null 2>&1
done

echo -e "\n📁 Generating PUT operations..."
for op in "${operations_put[@]}"; do
    echo "  - $op"
    ~/.cargo/bin/mrapids analyze --operation "$op" --force >/dev/null 2>&1
done

echo -e "\n📁 Generating DELETE operations..."
for op in "${operations_delete[@]}"; do
    echo "  - $op"
    ~/.cargo/bin/mrapids analyze --operation "$op" --force >/dev/null 2>&1
done

echo -e "\n✅ Generated $(ls requests/examples/*.yaml 2>/dev/null | wc -l) request configurations"
echo -e "\n📂 Files created in:"
echo "  - requests/examples/ (request configs)"
echo "  - data/examples/ (request bodies)"

echo -e "\n🎯 Next steps:"
echo "1. List generated requests: ls requests/examples/"
echo "2. Run a request: mrapids run requests/examples/<file>.yaml --header 'Authorization: token YOUR_TOKEN'"
echo "3. Edit data files in data/examples/ for POST/PUT operations"