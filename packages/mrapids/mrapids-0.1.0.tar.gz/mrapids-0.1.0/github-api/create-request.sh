#!/bin/bash

# Interactive request builder for MicroRapid

echo "🚀 MicroRapid Request Builder"
echo "============================"

# List available operations
echo -e "\nSearching for operations..."
echo "Popular operations:"
echo "1. users/get-authenticated - Get your user info"
echo "2. repos/list-for-user - List repos for a user"
echo "3. gists/create - Create a gist"
echo "4. issues/create - Create an issue"
echo "5. repos/create-fork - Fork a repository"
echo "6. activity/star-repo-for-authenticated-user - Star a repo"

# Get operation
echo -e "\nEnter operation name (or number from above):"
read operation

# Convert number to operation
case $operation in
    1) operation="users/get-authenticated" ;;
    2) operation="repos/list-for-user" ;;
    3) operation="gists/create" ;;
    4) operation="issues/create" ;;
    5) operation="repos/create-fork" ;;
    6) operation="activity/star-repo-for-authenticated-user" ;;
esac

# Generate the base config
echo -e "\nGenerating request configuration for: $operation"
~/.cargo/bin/mrapids analyze --operation "$operation" --force

# Get the generated file name (convert / to -)
filename=$(echo "$operation" | sed 's/\//-/g')
config_file="requests/examples/${filename}.yaml"
data_file="data/examples/${filename}.json"

echo -e "\n✅ Generated files:"
echo "   Config: $config_file"
if [ -f "$data_file" ]; then
    echo "   Data: $data_file"
fi

# Ask if user wants to customize
echo -e "\nDo you want to:"
echo "1. Run it now"
echo "2. Edit the configuration"
echo "3. Create a custom version"
echo "4. Exit"
read -p "Choose (1-4): " choice

case $choice in
    1)
        echo -e "\nRunning the request..."
        if [ -f "$data_file" ]; then
            echo "(Using data from $data_file)"
        fi
        read -p "Do you need authentication? (y/n): " need_auth
        if [ "$need_auth" = "y" ]; then
            read -p "Enter your GitHub token: " token
            ~/.cargo/bin/mrapids run "$config_file" --header "Authorization: token $token"
        else
            ~/.cargo/bin/mrapids run "$config_file"
        fi
        ;;
    2)
        echo "Opening in default editor..."
        ${EDITOR:-nano} "$config_file"
        if [ -f "$data_file" ]; then
            ${EDITOR:-nano} "$data_file"
        fi
        ;;
    3)
        read -p "Enter custom name for your request: " custom_name
        custom_dir="requests/my-requests"
        mkdir -p "$custom_dir"
        cp "$config_file" "$custom_dir/${custom_name}.yaml"
        echo "✅ Created custom request: $custom_dir/${custom_name}.yaml"
        ${EDITOR:-nano} "$custom_dir/${custom_name}.yaml"
        ;;
    4)
        echo "Goodbye!"
        ;;
esac