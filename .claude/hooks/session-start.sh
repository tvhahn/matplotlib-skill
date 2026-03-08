#!/bin/bash
set -e

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Install Python dependencies
echo "Installing dependencies..."
uv sync
uv pip install -e .

# Load .env into Claude's environment (only works in SessionStart hooks)
if [ -n "$CLAUDE_ENV_FILE" ] && [ -f ".env" ]; then
    echo "Loading environment variables..."
    grep -v '^#' .env | grep -v '^$' >> "$CLAUDE_ENV_FILE" 2>/dev/null || true
fi

echo "Setup complete!"
