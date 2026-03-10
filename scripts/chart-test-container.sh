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
# After each prompt, the full clean room is archived into the results
# directory (minus data/, __pycache__/, .venv/, .claude-config/ by default).
# Use --full-archive to keep data/ in the archive (~15 MB extra per prompt).
#
# Usage:
#   scripts/chart-test-container.sh                    # run all 9 test prompts
#   scripts/chart-test-container.sh --quick             # run 5 prompts (bar, violin, vertical bar, heatmap, lollipop)
#   scripts/chart-test-container.sh --full-archive      # keep data/ in workspace archives
#   scripts/chart-test-container.sh --tag A "prompt"    # tag results dir for parallel runs
#   scripts/chart-test-container.sh "horizontal bar chart of collision rates by state from data/raw/public/car_crashes.csv"
#
# Results are saved to logs/clean-room/YYYY-MM-DD_HH.MM/ (or YYYY-MM-DD_HH.MM-TAG/ with --tag)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

TIMESTAMP=$(TZ=America/Los_Angeles date +"%Y-%m-%d_%H.%M")

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

# --- Parse flags ---
QUICK=false
FULL_ARCHIVE=false
TAG=""
CUSTOM_PROMPT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --quick) QUICK=true; shift ;;
        --full-archive) FULL_ARCHIVE=true; shift ;;
        --tag) TAG="$2"; shift 2 ;;
        *) CUSTOM_PROMPT="$1"; shift ;;
    esac
done

# --- Build results directory (after flags parsed so TAG is available) ---
if [ -n "$TAG" ]; then
    RESULTS_DIR="$REPO_DIR/logs/clean-room/${TIMESTAMP}-${TAG}"
else
    RESULTS_DIR="$REPO_DIR/logs/clean-room/$TIMESTAMP"
fi
mkdir -p "$RESULTS_DIR"

# --- Test prompts ---
# Each prompt is a realistic, minimal chart request — the kind a user would type.
# The skill should handle everything from here.
DEFAULT_PROMPTS=(
    "horizontal bar chart of total collision rates by state from data/raw/public/car_crashes.csv — show top 10 states"
    "violin plot of penguin body mass by species from data/raw/public/penguins.csv"
    "time series of global temperature anomalies from data/raw/public/global_temp.csv — plot annual averages with a rolling mean"
    "PR and ROC curves for breast cancer classification using data/raw/public/breast_cancer.csv — use the target column"
    "lollipop chart comparing health spending per capita across countries from data/raw/public/healthexp.csv — show min/avg/max range"
    "vertical bar chart of net electricity generation by source from data/raw/public/iowa_electricity.csv — compare the latest year"
    "correlation heatmap of penguin measurements from data/raw/public/penguins.csv — annotate cells with values"
    "3x2 grid of life expectancy trends for 6 countries from data/raw/public/gapminder.csv — one subplot per country"
    "decision boundary plot for iris species classification using petal length vs petal width from data/raw/public/iris.csv"
)

# --quick: run 5 of 9 prompts (horizontal bar, violin, vertical bar, heatmap, lollipop)
QUICK_PROMPTS=(
    "${DEFAULT_PROMPTS[0]}"
    "${DEFAULT_PROMPTS[1]}"
    "${DEFAULT_PROMPTS[5]}"
    "${DEFAULT_PROMPTS[6]}"
    "${DEFAULT_PROMPTS[4]}"
)

# Select prompts
if [ -n "$CUSTOM_PROMPT" ]; then
    PROMPTS=("$CUSTOM_PROMPT")
elif [ "$QUICK" = true ]; then
    PROMPTS=("${QUICK_PROMPTS[@]}")
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
    local CLEAN_ROOM_NAME=".clean-room-run-${TAG:+${TAG}-}${run_id}"
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

    # Copy highlights to run_dir top level
    if ls "$TMPDIR/figures/"* 1>/dev/null 2>&1; then
        cp "$TMPDIR/figures/"* "$run_dir/"
        echo "  Charts: $(ls "$TMPDIR/figures/" | wc -l) files saved to $run_dir/"
    else
        echo "  No charts generated."
    fi

    # Copy any generated scripts (recursive, excluding data/ and __pycache__/)
    find "$TMPDIR" -name "*.py" \
        -not -path "$TMPDIR/data/*" \
        -not -path "$TMPDIR/__pycache__/*" \
        -not -path "$TMPDIR/.venv/*" \
        -not -name "pyproject.toml" \
        -exec cp {} "$run_dir/" \; 2>/dev/null

    # Save the prompt
    echo "$prompt" > "$run_dir/prompt.txt"

    # Archive the full clean room into workspace/
    rm -rf "$TMPDIR/__pycache__" "$TMPDIR/.venv" "$TMPDIR/.claude-config"
    if [ "$FULL_ARCHIVE" != true ]; then
        rm -rf "$TMPDIR/data"
    fi
    mv "$TMPDIR" "$run_dir/workspace"
}

# Run tests
for i in "${!PROMPTS[@]}"; do
    run_id=$(printf "%02d" $((i + 1)))
    run_clean_room "${PROMPTS[$i]}" "$run_id"
done

# --- Check results ---
FAILURES=0
for i in "${!PROMPTS[@]}"; do
    run_id=$(printf "%02d" $((i + 1)))
    run_dir="$RESULTS_DIR/$run_id"
    png_count=$(find "$run_dir" -maxdepth 1 -name "*.png" 2>/dev/null | wc -l)
    if [ "$png_count" -eq 0 ]; then
        echo "FAIL: Prompt $run_id produced zero PNGs"
        FAILURES=$((FAILURES + 1))
    fi
done

echo ""
echo "=========================================="
if [ "$FAILURES" -gt 0 ]; then
    echo "FAILED: $FAILURES prompt(s) produced no charts."
else
    echo "All tests passed."
fi
echo "Results in: $RESULTS_DIR/"
echo "=========================================="
ls -la "$RESULTS_DIR/"

# Symlink latest run for convenience
ln -sfn "$(basename "$RESULTS_DIR")" "$REPO_DIR/logs/clean-room/latest"

# Disk usage summary
echo ""
RUN_SIZE=$(du -sh "$RESULTS_DIR" 2>/dev/null | cut -f1)
TOTAL_SIZE=$(du -sh "$REPO_DIR/logs/clean-room" 2>/dev/null | cut -f1)
echo "This run: $RUN_SIZE | Total logs/clean-room/: $TOTAL_SIZE"

exit "$FAILURES"
