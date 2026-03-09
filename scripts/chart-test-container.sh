#!/bin/bash
# Launch a Docker clean room to test the matplotlib-chart skill.
#
# Gives Claude Code the skill spec + datasets and a simple chart request.
# Claude Code discovers the skill and generates the chart from scratch —
# no test harness, no pre-written chart code. This tests whether the skill
# itself produces quality output from unfamiliar data.
#
# The container has NO access to gallery entries, git history, prior
# evaluations, or the test harness (which would bypass the skill).
#
# Usage:
#   scripts/chart-test-container.sh                    # run all test prompts
#   scripts/chart-test-container.sh "horizontal bar chart of collision rates by state from data/raw/public/car_crashes.csv"
#
# Results are saved to scratch/clean-room-results/

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RESULTS_DIR="$REPO_DIR/scratch/clean-room-results"
mkdir -p "$RESULTS_DIR"

# --- Resolve devcontainer image + host path (for DooD) ---
CONTAINER_ID=$(docker ps -qf "name=matplotlib-chart-skill" 2>/dev/null | head -1)
if [ -n "$CONTAINER_ID" ]; then
    IMAGE=$(docker inspect --format='{{.Config.Image}}' "$CONTAINER_ID" 2>/dev/null || echo "")
    HOST_REPO_DIR=$(docker inspect "$CONTAINER_ID" \
        --format='{{range .Mounts}}{{if eq .Destination "/workspace"}}{{.Source}}{{end}}{{end}}' 2>/dev/null || echo "")
fi
IMAGE="${IMAGE:-node:22}"
HOST_REPO_DIR="${HOST_REPO_DIR:-$REPO_DIR}"
echo "Image: $IMAGE"
echo "Host path: $HOST_REPO_DIR"

# --- Extract OAuth token ---
CREDS_FILE="${HOME}/.claude/.credentials.json"
OAUTH_TOKEN=$(python3 -c "
import json
with open('$CREDS_FILE') as f:
    creds = json.load(f)
print(creds.get('claudeAiOauth', {}).get('accessToken', ''))
" 2>/dev/null || echo "")

if [ -z "$OAUTH_TOKEN" ]; then
    echo "ERROR: Could not extract OAuth token from $CREDS_FILE"
    exit 1
fi

# --- Test prompts ---
# Each prompt is a realistic, minimal chart request — the kind a user would type.
# The skill should handle everything from here.
DEFAULT_PROMPTS=(
    "horizontal bar chart of total collision rates by state from data/raw/public/car_crashes.csv — show top 10 states"
    "violin plot of penguin body mass by species from data/raw/public/penguins.csv"
    "time series of global temperature anomalies from data/raw/public/global_temp.csv — plot annual averages with a rolling mean"
    "PR and ROC curves for breast cancer classification using data/raw/public/breast_cancer.csv — use the target column"
    "lollipop chart comparing health spending per capita across countries from data/raw/public/healthexp.csv — show min/avg/max range"
)

# Use provided prompt or all defaults
if [ $# -gt 0 ]; then
    PROMPTS=("$1")
else
    PROMPTS=("${DEFAULT_PROMPTS[@]}")
fi

# --- Run each prompt in a fresh clean room ---
run_clean_room() {
    local prompt="$1"
    local run_id="$2"
    local run_dir="$RESULTS_DIR/$run_id"
    mkdir -p "$run_dir"

    echo ""
    echo "=========================================="
    echo "Test $run_id: $prompt"
    echo "=========================================="

    # Build clean room inside workspace (host-visible for DooD)
    local CLEAN_ROOM_NAME=".clean-room-run-$run_id"
    local TMPDIR="$REPO_DIR/$CLEAN_ROOM_NAME"
    local HOST_TMPDIR="$HOST_REPO_DIR/$CLEAN_ROOM_NAME"

    rm -rf "$TMPDIR"
    mkdir -p "$TMPDIR/.claude/skills"
    cp -r "$REPO_DIR/.claude/skills/matplotlib-chart" "$TMPDIR/.claude/skills/"
    cp -r "$REPO_DIR/data" "$TMPDIR/data"
    cp "$REPO_DIR/pyproject.toml" "$TMPDIR/"
    [ -f "$REPO_DIR/uv.lock" ] && cp "$REPO_DIR/uv.lock" "$TMPDIR/"

    # Minimal CLAUDE.md — just enough context, no coaching
    cat > "$TMPDIR/CLAUDE.md" << 'CLEANEOF'
# matplotlib-chart-skill

Datasets are in `data/raw/`. Save charts to `./figures/`.
CLEANEOF

    # Onboarding stub
    mkdir -p "$TMPDIR/.claude-config"
    echo '{"hasCompletedOnboarding":true,"installMethod":"native"}' > "$TMPDIR/.claude-config/.claude.json"

    # Run Claude Code with the prompt
    docker run --rm \
        -v "$HOST_TMPDIR:/workspace" \
        -v "$HOST_TMPDIR/.claude-config:/home/node/.claude" \
        -e CLAUDE_CODE_OAUTH_TOKEN="$OAUTH_TOKEN" \
        -w /workspace \
        "$IMAGE" \
        bash -c "claude --dangerously-skip-permissions -p '${prompt//\'/\'\\\'\'}' --max-turns 15" \
        > "$run_dir/claude_output.txt" 2>&1

    # Copy results
    if ls "$TMPDIR/figures/"* 1>/dev/null 2>&1; then
        cp "$TMPDIR/figures/"* "$run_dir/"
        echo "  Charts: $(ls "$TMPDIR/figures/" | wc -l) files saved to $run_dir/"
    else
        echo "  No charts generated."
    fi

    # Copy any generated scripts
    find "$TMPDIR" -maxdepth 1 -name "*.py" ! -name "pyproject.toml" -exec cp {} "$run_dir/" \; 2>/dev/null

    # Save the prompt
    echo "$prompt" > "$run_dir/prompt.txt"

    # Cleanup
    rm -rf "$TMPDIR"
}

# Run tests
for i in "${!PROMPTS[@]}"; do
    run_id=$(printf "%02d" $((i + 1)))
    run_clean_room "${PROMPTS[$i]}" "$run_id"
done

echo ""
echo "=========================================="
echo "All tests complete. Results in: $RESULTS_DIR/"
echo "=========================================="
ls -la "$RESULTS_DIR/"
