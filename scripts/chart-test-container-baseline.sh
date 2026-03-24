#!/bin/bash
# Launch a Docker clean room to test chart output WITHOUT the matplotlib-chart skill.
#
# Runs the same prompts as chart-test-container.sh but with NO skill installed.
# Claude Code generates charts using only its built-in knowledge — no skill spec,
# no style reference, no pattern files. This produces a baseline for comparison
# against skill-enhanced output.
#
# The container has NO access to gallery entries, git history, prior
# evaluations, or the test harness (which would bypass the skill).
#
# After each prompt, the full clean room is archived into the results
# directory (minus data/, __pycache__/, .venv/, .claude-config/ by default).
# Use --full-archive to keep data/ in the archive (~15 MB extra per prompt).
#
# Prompt selection:
#   Each pattern (P1–P9) has a pool of prompts using different datasets.
#   By default, one prompt is randomly selected from each pool per run.
#   Use --fixed to always select index 0 (the original default prompt).
#
# Usage:
#   scripts/chart-test-container-baseline.sh                    # run all 9 prompts (random from pools)
#   scripts/chart-test-container-baseline.sh --quick             # run 5 prompts (random from pools)
#   scripts/chart-test-container-baseline.sh --fixed             # use original default prompts (index 0)
#   scripts/chart-test-container-baseline.sh --quick --fixed     # 5 prompts, original defaults
#   scripts/chart-test-container-baseline.sh --full-archive      # keep data/ in workspace archives
#   scripts/chart-test-container-baseline.sh --tag A "prompt"    # tag results dir for parallel runs
#   scripts/chart-test-container-baseline.sh "horizontal bar chart of collision rates by state from data/raw/public/car_crashes.csv"
#
# Results are saved to logs/clean-room-baseline/YYYY-MM-DD_HH.MM/ (or YYYY-MM-DD_HH.MM-TAG/ with --tag)

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
FIXED=false
FULL_ARCHIVE=false
TAG=""
CUSTOM_PROMPT=""
while [ $# -gt 0 ]; do
    case "$1" in
        --quick) QUICK=true; shift ;;
        --fixed) FIXED=true; shift ;;
        --full-archive) FULL_ARCHIVE=true; shift ;;
        --tag) TAG="$2"; shift 2 ;;
        *) CUSTOM_PROMPT="$1"; shift ;;
    esac
done

# --- Build results directory (after flags parsed so TAG is available) ---
if [ -n "$TAG" ]; then
    RESULTS_DIR="$REPO_DIR/logs/clean-room-baseline/${TIMESTAMP}-${TAG}"
else
    RESULTS_DIR="$REPO_DIR/logs/clean-room-baseline/$TIMESTAMP"
fi
mkdir -p "$RESULTS_DIR"

# --- Per-pattern prompt pools ---
# Each pool's index 0 is the original default prompt (used with --fixed).
# Additional entries exercise different datasets for variety across runs.
# Pool numbering matches patterns/P*.md pattern numbering.

# P1: Horizontal bar chart
P1_POOL=(
    "horizontal bar chart of total collision rates by state from data/raw/public/car_crashes.csv — show top 10 states"
    "horizontal bar chart of average mpg by country of origin from data/raw/public/mpg.csv"
    "horizontal bar chart of GDP per capita by continent from data/raw/public/gapminder.csv — use latest year, show continent averages"
    "horizontal bar chart of average diamond price by cut quality from data/raw/public/diamonds.csv"
    "horizontal bar chart of survival rate by passenger class from data/raw/public/titanic.csv"
    "horizontal bar chart of total deaths by disaster type from data/raw/public/disasters.csv — show top 8 types"
    "horizontal bar chart of planet count by discovery method from data/raw/public/planets.csv — show top 8 methods"
    "horizontal bar chart of GDP per capita for top 15 countries from data/raw/public/country_stats.csv"
)

# P2: Vertical bar chart
P2_POOL=(
    "vertical bar chart of net electricity generation by source from data/raw/public/iowa_electricity.csv — compare the latest year"
    "vertical bar chart of average horsepower by number of cylinders from data/raw/public/mpg.csv"
    "vertical bar chart of average carat by clarity grade from data/raw/public/diamonds.csv"
    "vertical bar chart of passenger count by embarkation town from data/raw/public/titanic.csv"
    "vertical bar chart of deaths in latest decade by disaster type from data/raw/public/disasters.csv"
    "vertical bar chart of average fare by pickup borough from data/raw/public/taxis.csv"
    "vertical bar chart of correlation values by loss function from data/raw/weibull/femto_correlation_results.csv"
)

# P3: Time series (pre-computed: year, value, rolling)
P3_POOL=(
    "time series bar chart with rolling mean from data/raw/precomputed/p3/global_temp.csv — columns are year, value, rolling"
    "time series bar chart with rolling mean from data/raw/precomputed/p3/flights.csv — columns are year, value, rolling"
    "time series bar chart with rolling mean from data/raw/precomputed/p3/birth_percentage.csv — columns are year, value, rolling"
    "time series bar chart with rolling mean from data/raw/precomputed/p3/dowjones.csv — columns are year, value, rolling"
    "time series bar chart with rolling mean from data/raw/precomputed/p3/co2_concentration.csv — columns are year, value, rolling"
    "time series bar chart with rolling mean from data/raw/precomputed/p3/stocks.csv — columns are year, value, rolling"
    "time series bar chart with rolling mean from data/raw/precomputed/p3/planets.csv — columns are year, value, rolling"
)

# P4: Violin + Strip plot
P4_POOL=(
    "violin plot of penguin body mass by species from data/raw/public/penguins.csv"
    "violin plot of mpg distribution by number of cylinders from data/raw/public/mpg.csv"
    "violin plot of diamond price distribution by cut quality from data/raw/public/diamonds.csv"
    "violin plot of passenger age distribution by survival status from data/raw/public/titanic.csv"
    "violin plot of eruption duration by kind from data/raw/public/geyser.csv"
    "violin plot of tool wear VB values by tool class from data/raw/ml-tool-wear/labels_with_tool_class.csv"
    "violin plot of fare distribution by payment type from data/raw/public/taxis.csv"
    "violin plot of chick weight by diet group from data/raw/public/chickweight.csv"
    "violin plot of temperature distribution by weather type from data/raw/public/seattle_weather.csv — use temp_max column"
)

# P5: Lollipop/dumbbell chart (pre-computed: name, min, max, avg)
P5_POOL=(
    "lollipop chart of health spending range by country from data/raw/precomputed/p5/healthexp.csv — columns are name, min, max, avg"
    "lollipop chart of mpg range by origin from data/raw/precomputed/p5/mpg.csv — columns are name, min, max, avg"
    "lollipop chart of diamond price range by color grade from data/raw/precomputed/p5/diamonds.csv — columns are name, min, max, avg"
    "lollipop chart of classifier AUC range from data/raw/precomputed/p5/best_results.csv — columns are name, min, max, avg"
    "lollipop chart of happiness score range by region from data/raw/precomputed/p5/world_happiness.csv — columns are name, min, max, avg"
    "lollipop chart of life expectancy range by continent from data/raw/precomputed/p5/country_stats.csv — columns are name, min, max, avg"
    "lollipop chart of model score range across NLP tasks from data/raw/precomputed/p5/glue.csv — columns are name, min, max, avg"
)

# P6: Decision boundary (pre-computed NPZ with mesh grid + predictions)
P6_POOL=(
    "decision boundary plot from data/raw/precomputed/p6/iris.npz — load with np.load, arrays: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names"
    "decision boundary plot from data/raw/precomputed/p6/wine.npz — load with np.load, arrays: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names"
    "decision boundary plot from data/raw/precomputed/p6/breast_cancer.npz — load with np.load, arrays: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names"
    "decision boundary plot from data/raw/precomputed/p6/geyser.npz — load with np.load, arrays: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names"
    "decision boundary plot from data/raw/precomputed/p6/penguins.npz — load with np.load, arrays: mesh_x0, mesh_x1, yy_hat, yy_prob, X, y, class_names"
)

# P7: Heatmap (pre-computed correlation matrix / pivot table CSV)
P7_POOL=(
    "correlation heatmap from data/raw/precomputed/p7/penguins.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "correlation heatmap from data/raw/precomputed/p7/mpg.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "correlation heatmap from data/raw/precomputed/p7/diamonds.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "correlation heatmap from data/raw/precomputed/p7/wine.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "heatmap from data/raw/precomputed/p7/birth_percentage.csv — pre-computed pivot table, load with pd.read_csv(index_col=0)"
    "correlation heatmap from data/raw/precomputed/p7/tips.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "heatmap from data/raw/precomputed/p7/flights.csv — pre-computed pivot table, load with pd.read_csv(index_col=0)"
    "correlation heatmap from data/raw/precomputed/p7/diabetes.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "correlation heatmap from data/raw/precomputed/p7/mtcars.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
    "correlation heatmap from data/raw/precomputed/p7/taxis.csv — pre-computed correlation matrix, load with pd.read_csv(index_col=0), annotate cells"
)

# P8: Multi-panel
P8_POOL=(
    "3x2 grid of life expectancy trends for 6 countries from data/raw/public/gapminder.csv — one subplot per country"
    "3x2 grid of passenger trends from data/raw/public/flights.csv — one subplot per year (pick 6 years)"
    "3x2 grid of health spending trends from data/raw/public/healthexp.csv — one subplot per country (pick 6)"
    "multi-panel of stock price trends from data/raw/public/stocks.csv — one subplot per stock symbol"
    "multi-panel of fMRI signal over time from data/raw/public/fmri.csv — one subplot per brain region and event"
    "multi-panel of chick weight over time from data/raw/public/chickweight.csv — one subplot per diet"
    "3x2 grid of happiness score by factor from data/raw/public/world_happiness.csv — one subplot per region (pick 6)"
)

# P9: PR/ROC curves (pre-computed NPZ with fold curves + averages)
P9_POOL=(
    "PR and ROC curves from data/raw/precomputed/p9/breast_cancer.npz — load with np.load, arrays: precision_array, recall_array, tpr_array, fpr_array, precision_avg, recall_avg, tpr_avg, fpr_avg, baseline"
    "PR and ROC curves from data/raw/precomputed/p9/penguins.npz — load with np.load, arrays: precision_array, recall_array, tpr_array, fpr_array, precision_avg, recall_avg, tpr_avg, fpr_avg, baseline"
    "PR and ROC curves from data/raw/precomputed/p9/titanic.npz — load with np.load, arrays: precision_array, recall_array, tpr_array, fpr_array, precision_avg, recall_avg, tpr_avg, fpr_avg, baseline"
    "PR and ROC curves from data/raw/precomputed/p9/geyser.npz — load with np.load, arrays: precision_array, recall_array, tpr_array, fpr_array, precision_avg, recall_avg, tpr_avg, fpr_avg, baseline"
    "PR and ROC curves from data/raw/precomputed/p9/wine.npz — load with np.load, arrays: precision_array, recall_array, tpr_array, fpr_array, precision_avg, recall_avg, tpr_avg, fpr_avg, baseline"
)

# --- Prompt selection ---
pick_prompt() {
    local -n pool=$1
    if [ "$FIXED" = true ] || [ "${#pool[@]}" -eq 1 ]; then
        echo "${pool[0]}"
    else
        printf '%s\n' "${pool[@]}" | shuf -n 1
    fi
}

ALL_POOLS=(P1_POOL P2_POOL P3_POOL P4_POOL P5_POOL P6_POOL P7_POOL P8_POOL P9_POOL)
# --quick: P1, P2, P5, P6, P7 (indices into ALL_POOLS)
QUICK_INDICES=(0 1 4 5 6)

# Select prompts
if [ -n "$CUSTOM_PROMPT" ]; then
    PROMPTS=("$CUSTOM_PROMPT")
elif [ "$QUICK" = true ]; then
    PROMPTS=()
    for idx in "${QUICK_INDICES[@]}"; do
        PROMPTS+=("$(pick_prompt "${ALL_POOLS[$idx]}")")
    done
else
    PROMPTS=()
    for pool_name in "${ALL_POOLS[@]}"; do
        PROMPTS+=("$(pick_prompt "$pool_name")")
    done
fi

# Log selected prompts
echo ""
echo "Selected prompts:"
for i in "${!PROMPTS[@]}"; do
    echo "  $((i + 1)). ${PROMPTS[$i]}"
done
echo ""

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
    local CLEAN_ROOM_NAME=".clean-room-baseline-run-${TAG:+${TAG}-}${run_id}"
    local TMPDIR="$REPO_DIR/$CLEAN_ROOM_NAME"
    local HOST_TMPDIR="$HOST_REPO_DIR/$CLEAN_ROOM_NAME"

    rm -rf "$TMPDIR"
    mkdir -p "$TMPDIR"
    cp -r "$REPO_DIR/data" "$TMPDIR/data"
    # Neutral pyproject.toml — deps only, no skill-related naming
    cat > "$TMPDIR/pyproject.toml" << 'PYEOF'
[project]
name = "chart-workspace"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pandas>=2.0.0",
    "numpy>=1.26.0",
    "matplotlib>=3.8.0",
    "seaborn>=0.13.0",
]
PYEOF

    # Minimal CLAUDE.md — no skill, no coaching, just data location
    cat > "$TMPDIR/CLAUDE.md" << 'CLEANEOF'
# Chart Generation

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
        bash -c "claude --dangerously-skip-permissions -p '${prompt//\'/\'\\\'\'}' --max-turns 40" \
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
ln -sfn "$(basename "$RESULTS_DIR")" "$REPO_DIR/logs/clean-room-baseline/latest"

# Disk usage summary
echo ""
RUN_SIZE=$(du -sh "$RESULTS_DIR" 2>/dev/null | cut -f1)
TOTAL_SIZE=$(du -sh "$REPO_DIR/logs/clean-room-baseline" 2>/dev/null | cut -f1)
echo "This run: $RUN_SIZE | Total logs/clean-room-baseline/: $TOTAL_SIZE"

exit "$FAILURES"
