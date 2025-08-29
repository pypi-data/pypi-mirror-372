#!/bin/bash

# GitHub API curl examples

TOKEN="YOUR_GITHUB_TOKEN"
BASE_URL="https://api.github.com"

echo "GitHub API Curl Examples"
echo "======================="
echo "Replace YOUR_GITHUB_TOKEN with your actual token"
echo ""

# GET examples
echo "# GET Operations"
echo "# =============="
echo ""

echo "# Get authenticated user"
echo "curl -H \"Authorization: token \$TOKEN\" \\"
echo "     -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     $BASE_URL/user"
echo ""

echo "# List repos for user"
echo "curl -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     \"$BASE_URL/users/octocat/repos?per_page=5&sort=updated\""
echo ""

echo "# Get a repository"
echo "curl -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     $BASE_URL/repos/octocat/Hello-World"
echo ""

# POST examples
echo -e "\n# POST Operations"
echo "# ==============="
echo ""

echo "# Create a gist"
echo "curl -X POST \\"
echo "     -H \"Authorization: token \$TOKEN\" \\"
echo "     -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"description\":\"Test gist\",\"public\":true,\"files\":{\"test.txt\":{\"content\":\"Hello World\"}}}' \\"
echo "     $BASE_URL/gists"
echo ""

echo "# Star a repository"
echo "curl -X PUT \\"
echo "     -H \"Authorization: token \$TOKEN\" \\"
echo "     -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     $BASE_URL/user/starred/octocat/Hello-World"
echo ""

echo "# Create an issue"
echo "curl -X POST \\"
echo "     -H \"Authorization: token \$TOKEN\" \\"
echo "     -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"title\":\"Test issue\",\"body\":\"This is a test\"}' \\"
echo "     $BASE_URL/repos/OWNER/REPO/issues"
echo ""

# DELETE examples
echo -e "\n# DELETE Operations"
echo "# ================="
echo ""

echo "# Unstar a repository"
echo "curl -X DELETE \\"
echo "     -H \"Authorization: token \$TOKEN\" \\"
echo "     -H \"Accept: application/vnd.github.v3+json\" \\"
echo "     $BASE_URL/user/starred/octocat/Hello-World"