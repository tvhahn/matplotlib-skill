# Plan: Real Datasets + Autonomous Skill Iteration Infrastructure

**Date:** 2026-03-08
**Status:** Draft
**Expert Panel:** [expert-panel-analysis.md](./expert-panel-analysis.md)

## Context

The matplotlib-chart skill repo currently tests all 9 chart patterns with synthetic dummy data only. However, `data/raw/` already contains real datasets from the 4 source projects that inspired the skill (documented in `docs/gallery/00-original-inspiration/`). The user wants to:
1. Curate these existing datasets + add public reference datasets for broader coverage
2. Build infrastructure for agent-driven autonomous skill iteration

The expert panel recommended: real datasets first, single-iteration command second, autonomous loop third. They capped autonomous iterations at 3 (not 5-7) and emphasized git discipline (atomic commits per iteration, branch isolation).

**DPI rule:** All development and test renders use 150 DPI. Patterns specify 300 DPI for publication output only.

---

## Phase 1: Curate Datasets in `data/raw/`

### What already exists

`data/raw/` is organized by source project, mirroring `docs/gallery/00-original-inspiration/`:

| Subfolder | Source Project | Key Files | Patterns |
|-----------|---------------|-----------|----------|
| `arxiv/` | arxiv-code-search | `labels.csv` (4,665 rows) | P1, P9 |
| `beautiful-plots/` | Beautiful-Plots | `birth_percentage.csv` (468 rows), `best_results.csv` (6 rows) | P4, P5, P6 |
| `ml-tool-wear/` | ml-tool-wear | `labels_with_tool_class.csv` (167 rows) | P9 |
| `weibull/` | weibull-knowledge-informed-ml | Multiple CSVs + 38 HDF5 files (~14MB total) | P1-P4, P7, P8 |

### What to add: public reference datasets

New `public/` subfolder for curated, permissively-licensed datasets that broaden domain coverage:

```
data/raw/
  arxiv/                  # (existing)
  beautiful-plots/        # (existing)
  ml-tool-wear/           # (existing)
  weibull/                # (existing)
  public/                 # NEW — ~292KB total
    penguins.csv          # Palmer Penguins — ecology — 344 rows — CC-0
    gapminder.csv         # Gapminder — global dev — 1,704 rows — CC0
    tips.csv              # Restaurant tips — social science — 244 rows — BSD
    global_temp.csv       # GISTEMP anomalies — climate — ~1,700 rows — PDDL
    car_crashes.csv       # US bad drivers — transport — 51 rows — CC-BY 4.0
    breast_cancer.csv     # UCI Wisconsin — medical — 569 rows — CC BY 4.0
    healthexp.csv         # Health expenditure — economics — 231 rows — CC-BY
    iowa_electricity.csv  # US EIA — energy — ~50 rows — Public domain
  datasets.yaml           # Manifest covering ALL datasets (existing + public)
  SOURCES.md              # Attribution for all datasets
```

### Combined pattern coverage
| Pattern | Source Project Data | Public Reference Data |
|---------|-------------------|----------------------|
| P1 Horizontal Bar | weibull counts, arxiv labels | gapminder, car_crashes |
| P2 Vertical Bar | weibull correlations | car_crashes, iowa_electricity |
| P3 Time Series | weibull RUL results | global_temp |
| P4 Violin+Strip | weibull early stop stats | penguins, tips |
| P5 Lollipop | beautiful-plots best_results | healthexp |
| P6 Scatter/Decision Boundary | (none — image only) | penguins, breast_cancer |
| P7 Heatmap | weibull HDF5 spectrograms | global_temp, tips |
| P8 Multi-Panel | weibull filtered results | healthexp, gapminder |
| P9 PR/ROC | arxiv labels | breast_cancer, penguins |

### Files to create/modify
- `data/raw/public/*.csv` — 8 CSV files (new)
- `data/datasets.yaml` — manifest covering existing + public datasets (new)
- `data/SOURCES.md` — attribution (new)
- `data/fetch_datasets.py` — download script for public datasets (new)
- `CLAUDE.md` — add data directory to key files section
- `.gitignore` — ensure `data/raw/` is NOT gitignored

---

## Phase 1b: Isolation Strategy — Docker Clean Room

### The Problem

When the iteration agent tests the skill, it could "cheat" by reading previous gallery entries, evaluation documents, and test outputs — essentially grading a test with the answer key open.

### Approach: Docker-in-Docker Clean Room (Complete Isolation)

Since we're in a devcontainer with Docker-outside-of-Docker configured (`/var/run/docker.sock` mounted), we reuse the **existing devcontainer image** (Node.js 22, Python 3.12, uv, Claude Code already installed) as the clean room base.

**How it works:**
1. `scripts/chart-test-container.sh` creates a temp directory with ONLY: skill files, datasets, test harness, pyproject.toml/uv.lock, and a clean CLAUDE.md
2. Spins up a container from the existing devcontainer image
3. Runs Claude Code with `--dangerously-skip-permissions` (container IS the sandbox)
4. Copies results back, destroys container

**What doesn't exist in the clean room:** `docs/gallery/`, `docs/specs/`, `scratch/figures/`, `.git/`, real `CLAUDE.md`, parent conversation context.

**Auth inheritance:** OAuth token is extracted from parent's `/home/node/.claude/.credentials.json` at launch time and passed via `CLAUDE_CODE_OAUTH_TOKEN` env var. No API key needed. Token lasts 8-12 hours (plenty for test runs). Avoids refresh token race conditions that occur when mounting the shared credentials volume.

**Why this is strongest:** No git history to `git show` from. Files physically never created. Completely separate Claude Code session. Zero contamination vectors.

### Files to create
- `scripts/chart-test-container.sh` — Docker clean room launcher (self-contained, no other config needed)

---

## Phase 2: Update Test Harness for Real Data

### Changes to `scratch/test_chart_patterns.py`
- Add a `--real-data` CLI flag (argparse)
- When `--real-data` is passed, read `data/datasets.yaml` and load CSVs for each pattern (both source project and public datasets)
- Keep synthetic mode as default (backward compatible)
- Each pattern function gets a `data_source` parameter: `"synthetic"` or a DataFrame
- Output filenames distinguish mode: `01_horizontal_bar_synthetic.png` vs `01_horizontal_bar_penguins.png`
- **All development renders at 150 DPI**

### Files to modify
- `scratch/test_chart_patterns.py` — add real data mode
- Possibly `pyproject.toml` — add `pyyaml` dependency for manifest reading

---

## Phase 3: Single-Iteration Slash Command (`/iterate-skill`)

### Command flow
1. **Evaluate** — Read skill files, run test harness (both synthetic and real data at 150 DPI), examine output PNGs, run automated checks
2. **Identify** — Select 1-2 areas for improvement (prioritize: style compliance gaps, pattern inconsistencies, code quality issues, missing annotations)
3. **Propose** — Write proposed changes to an evaluation document BEFORE making them
4. **Change** — Apply targeted changes to skill files in `skills/matplotlib-chart/`
5. **Regenerate** — Run test harness again at 150 DPI, producing new charts
6. **Document** — Create gallery entry (`docs/gallery/NN-name/`) with evaluation markdown, before/after PNGs
7. **Commit** — Atomic commit with conventional format

### Automated evaluation checklist (run at steps 1 and 5)
- [ ] All patterns render without error (exit code 0, non-zero file sizes)
- [ ] Style compliance: every pattern has `sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")`
- [ ] Style compliance: every pattern has `sns.despine(left=True, bottom=True)`
- [ ] DPI consistency: all development/test renders use `dpi=150`; patterns specify `dpi=300` for publication output only
- [ ] No deprecated API calls (`sns.set()`, `plt.hold()`, etc.)
- [ ] Legend styling present where applicable (`frameon=True, facecolor="white"`)
- [ ] Annotation color is `"dimgrey"` where applicable

### Evaluation document format
```markdown
# Iteration NN — YYYY-MM-DD

## Summary
One-sentence description of focus area.

## Changes Made
| Pattern | File | Change | Confidence |
|---------|------|--------|------------|
| P3 | chart-patterns.md | Added rolling window annotation | High |

## Automated Checks (Before)
Style compliance: 8/9 | Render success: 9/9 | DPI correct: 9/9

## Automated Checks (After)
Style compliance: 9/9 | Render success: 9/9 | DPI correct: 9/9

## Charts Generated
- `scratch/figures/03_time_series_*.png` (modified)

## Agent Notes
What changed and why. What the agent is uncertain about.
```

### Files to create
- `.claude/commands/iterate-skill.md` — slash command definition (new)
- `scratch/evaluate_skill.py` — automated evaluation script (new)

---

## Phase 4: Autonomous Loop Mode

### Design
- Each iteration runs on a dedicated git branch: `iterate/NN-timestamp`
- Workflow per iteration:
  1. Branch from current state
  2. Run single-iteration flow (Phase 3) — all renders at 150 DPI
  3. Commit to iteration branch
  4. Merge to a staging branch `iterate/batch-timestamp`
- After all iterations, produce a summary document listing all changes across iterations
- Human reviews the staging branch and can cherry-pick or drop individual iterations

### Guardrails
- **Max 3 iterations** without human feedback (not 5-7 — expert panel consensus)
- **No destructive changes** — agent can add/modify patterns but cannot delete existing ones
- **Rollback** — each iteration is an atomic commit; `git revert` any single iteration
- **Drift detection** — if automated checks score *decreases* between iterations, halt and surface the issue
- **Style invariants** — the `sns.set_theme()` call and `sns.despine()` call are immutable; agent cannot modify these

### Files to create/modify
- `.claude/commands/iterate-skill.md` — add autonomous mode instructions (modify)
- Evaluation script supports batch summary generation

---

## Verification

1. **Datasets**: Run `uv run data/fetch_datasets.py` and verify all 8 CSVs exist in `data/raw/public/`
2. **Test harness (synthetic)**: `uv run scratch/test_chart_patterns.py` — all patterns render at 150 DPI, PNGs in `scratch/figures/`
3. **Test harness (real data)**: `uv run scratch/test_chart_patterns.py --real-data` — all patterns render with real datasets at 150 DPI
4. **Slash command**: Run `/iterate-skill` manually and verify it produces a gallery entry with evaluation markdown
5. **Consistency checks**:
   ```bash
   grep 'sns.set_theme' skills/matplotlib-chart/chart-patterns.md
   grep 'dpi=' skills/matplotlib-chart/chart-patterns.md
   ```

## Implementation Order

1. Create `data/` directory structure + fetch script + download datasets + commit
2. Update test harness to support `--real-data` flag
3. Build evaluation script (`scratch/evaluate_skill.py`)
4. Create `/iterate-skill` slash command (supervised mode)
5. Add autonomous loop mode to the slash command
