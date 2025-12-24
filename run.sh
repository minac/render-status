#!/bin/bash
set -e

cd "$(dirname "$0")"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "Error: uv not installed. Run: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Sync dependencies
uv sync

echo "Running Render Status CLI..."
echo "Requires RENDER_API_KEY in .env"
echo ""
uv run render-status
