#!/bin/bash
set -e

# Auto-detect workspace from script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
PROJECT_NAME="$(basename "$WORKSPACE")"
CONTAINER_NAME="${PROJECT_NAME}-devcontainer-1"
session_num="${1}"
TMUX_SESSION="claude${session_num:+-$session_num}"

cd "$WORKSPACE"

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Starting devcontainer for $PROJECT_NAME..."
    devcontainer up --workspace-folder "$WORKSPACE"
    sleep 2
fi

# Check if this claude session already exists
if docker exec "$CONTAINER_NAME" tmux has-session -t "$TMUX_SESSION" 2>/dev/null; then
    echo "Attaching to existing Claude Code session ($TMUX_SESSION)..."
    docker exec -it "$CONTAINER_NAME" tmux attach -t "$TMUX_SESSION"
else
    echo "Starting Claude Code session ($TMUX_SESSION)..."
    docker exec -it "$CONTAINER_NAME" tmux new-session -s "$TMUX_SESSION" \
        "claude --dangerously-skip-permissions; zsh"
fi
