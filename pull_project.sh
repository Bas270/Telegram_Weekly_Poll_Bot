#!/bin/bash
#
# pull_project.sh
# Clones a GitHub repository if it doesn't exist, or pulls latest changes if it does.
#
# Usage: ./pull_project.sh <github_repo_url> <destination_directory>
# Example: ./pull_project.sh https://github.com/user/repo.git /opt/telegram-bot
#
# Authentication:
# - SSH: Ensure your SSH key is added to GitHub (recommended)
# - HTTPS: Use a GitHub Personal Access Token in the URL or via git credential helper
#

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <github_repo_url> <destination_directory>" >&2
    exit 1
fi

REPO_URL="$1"
DEST_DIR="$2"

# Validate destination directory path
if [ -z "$DEST_DIR" ]; then
    echo "Error: Destination directory cannot be empty" >&2
    exit 1
fi

# Get absolute path
DEST_DIR=$(realpath -m "$DEST_DIR")

echo "Repository URL: $REPO_URL"
echo "Destination: $DEST_DIR"

# Check if directory exists and is a git repository
if [ -d "$DEST_DIR" ]; then
    if [ -d "$DEST_DIR/.git" ]; then
        echo "Directory exists and is a git repository. Pulling latest changes..."
        cd "$DEST_DIR"
        
        # Check if remote URL matches (in case repo was moved)
        CURRENT_REMOTE=$(git remote get-url origin 2>/dev/null || echo "")
        if [ "$CURRENT_REMOTE" != "$REPO_URL" ]; then
            echo "Warning: Remote URL mismatch. Current: $CURRENT_REMOTE, Expected: $REPO_URL"
            read -p "Update remote URL? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                git remote set-url origin "$REPO_URL"
            fi
        fi
        
        # Fetch and pull latest changes
        git fetch origin
        git pull origin "$(git branch --show-current)" || {
            echo "Warning: Pull failed. You may need to resolve conflicts manually." >&2
            exit 1
        }
        
        echo "Successfully pulled latest changes."
    else
        echo "Error: Directory exists but is not a git repository: $DEST_DIR" >&2
        exit 1
    fi
else
    echo "Directory does not exist. Cloning repository..."
    
    # Create parent directory if it doesn't exist
    PARENT_DIR=$(dirname "$DEST_DIR")
    if [ ! -d "$PARENT_DIR" ]; then
        echo "Creating parent directory: $PARENT_DIR"
        mkdir -p "$PARENT_DIR"
    fi
    
    # Clone the repository
    git clone "$REPO_URL" "$DEST_DIR" || {
        echo "Error: Failed to clone repository. Check:" >&2
        echo "  1. Repository URL is correct" >&2
        echo "  2. You have access to the repository" >&2
        echo "  3. SSH key is set up (for SSH URLs) or credentials are configured (for HTTPS)" >&2
        exit 1
    }
    
    echo "Successfully cloned repository to $DEST_DIR"
fi

# Show current commit info
cd "$DEST_DIR"
echo ""
echo "Repository status:"
echo "  Current branch: $(git branch --show-current)"
echo "  Latest commit: $(git log -1 --oneline)"
echo "  Commit date: $(git log -1 --format=%cd)"