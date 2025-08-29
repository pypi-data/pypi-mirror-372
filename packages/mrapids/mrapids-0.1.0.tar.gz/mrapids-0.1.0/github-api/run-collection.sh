#!/bin/bash
# Run a collection of API tests

TOKEN="ghp_YOUR_TOKEN"
BASE_DIR="requests/collections/user-workflow"

echo "🚀 Running GitHub API Collection"
echo "================================"

# Step 1: Get authenticated user
echo -e "\n1️⃣ Getting authenticated user..."
~/.cargo/bin/mrapids run $BASE_DIR/1-get-auth-user.yaml \
  --header "Authorization: token $TOKEN" \
  --save responses/user.json

# Step 2: List repositories
echo -e "\n2️⃣ Listing user repositories..."
~/.cargo/bin/mrapids run $BASE_DIR/2-list-user-repos.yaml \
  --header "Authorization: token $TOKEN" \
  --save responses/repos.json

# Step 3: You can parse the response and use it in next request
# For example, get the first repo name
if [ -f responses/repos.json ]; then
  FIRST_REPO=$(jq -r '.[0].name // empty' responses/repos.json)
  OWNER=$(jq -r '.[0].owner.login // empty' responses/repos.json)
  
  if [ ! -z "$FIRST_REPO" ]; then
    echo -e "\n3️⃣ Creating issue in $OWNER/$FIRST_REPO..."
    ~/.cargo/bin/mrapids run issues/create \
      --param owner="$OWNER" \
      --param repo="$FIRST_REPO" \
      --header "Authorization: token $TOKEN" \
      --data '{
        "title": "Test issue from collection",
        "body": "This issue was created by running a collection of API requests"
      }'
  fi
fi

echo -e "\n✅ Collection completed!"