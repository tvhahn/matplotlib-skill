# Autoresearch for Skills — Implementation Plan

## Context

This project's current automation (`/variation-analysis`, `/iterate-skill`, Docker clean-rooms, `evaluate_skill.py`) is powerful but **human-triggered**. Each cycle requires manual invocation and judgment. Karpathy's autoresearch shows how to close the loop: a single scalar metric + autonomous keep/discard + infinite repetition = overnight improvement.

The goal: build an `/autoresearch` command that runs the skill improvement loop autonomously, logging experiments to `results.tsv` and advancing the branch only when improvements are confirmed.

---

## Architecture Mapping

| Dimension | autoresearch (Karpathy) | autoresearch-for-skills (this project) |
|-----------|------------------------|---------------------------------------|
| **Modifiable file** | `train.py` | `chart-patterns.md` (primary), `style-reference.md` (secondary, higher bar) |
| **Immutable infra** | `prepare.py` | `evaluate_skill.py` + `chart-test-container.sh` + `SKILL.md` |
| **Human program** | `program.md` | `program.md` |
| **Metric** | `val_bpb` (scalar) | `compliance × convergence × visual_quality` (composite scalar) |
| **Experiment time** | 5 min fixed (GPU training) | ~3-5 min (3x parallel Docker clean-room) |
| **Keep/discard** | `val_bpb < previous` | `composite_score > previous` |
| **Throughput** | ~12/hour | ~12-15/hour |
| **Experiment log** | `results.tsv` | `results.tsv` |
| **Branch strategy** | `autoresearch/<tag>` | `autoresearch/<tag>` |
| **Failure handling** | Revert + log crash | Revert + log crash + circuit breaker after 10 consecutive discards |
| **Human review** | Morning review of branch | Morning review of branch + cherry-pick to gallery |

---

## New Files to Create

### 1. `program.md` — Human-authored research program
The equivalent of autoresearch's `program.md`. Defines:
- Current research priorities (which patterns need work, what kind of improvements)
- Constraints (style invariants, no destructive changes, immutable files)
- Success criteria (minimum composite score thresholds)
- Exploration strategies (try rule tightening, try code simplification, try palette changes)
- What to do when stuck

### 2. `.claude/commands/autoresearch.md` — The autonomous loop command
A new slash command `/autoresearch` that:
- Reads `program.md` for strategy
- Runs the experiment loop (see below)
- Operates on a dedicated branch (`autoresearch/<tag>`)
- Logs to `results.tsv`
- Never stops until interrupted

### 3. `results.tsv` — Experiment log (gitignored, like autoresearch)
```
commit	pattern	score	compliance	convergence	visual	status	description
a1b2c3d	P5	0.82	1.0	0.85	0.96	keep	baseline
b2c3d4e	P5	0.91	1.0	0.95	0.96	keep	add fontsize=14 rule to stem markers
c3d4e5f	P5	0.82	1.0	0.80	1.0	discard	switch to horizontal orientation
```

---

## The Composite Metric

### Layer 1: Static Compliance (objective, fast, ~2 seconds)
Run `uv run scripts/evaluate_skill.py` and parse per-pattern results. Binary pass/fail.

**Score: 0.0 (any failure) or 1.0 (all pass)**

### Layer 2: Convergence Rate (objective, slow, ~3 minutes)
Run 3 parallel clean-room tests with different prompts from the pool. Read generated `.py` files and compare across structural dimensions. Count: `dims_matching / dims_total`.

**Score: 0.0 to 1.0**

### Layer 3: Visual Quality (Claude Code multimodal, ~30 seconds per chart)
Read each generated PNG and score against a fixed rubric:
- Layout & spacing: no overlapping elements, balanced whitespace (0/1)
- Color: palette matches pattern spec, colorblind-safe (0/1)
- Typography: titles, labels, annotations properly sized and dimgrey (0/1)
- Annotations: data values annotated where pattern specifies (0/1)
- Publishability: would this be acceptable in a blog post? (0/1)
- **All 3 PNGs must pass all checks** (3/3 requirement)

**Score: 0.0 to 1.0**

### Composite
```
skill_score = static_compliance × convergence_rate × visual_quality
```

Multiplicative — any zero kills the score.

---

## The Experiment Loop

```
program.md (human strategy)
    ↓
┌─────────────────────────────────────────────────────┐
│ LOOP FOREVER:                                        │
│                                                      │
│  1. Read program.md for priorities & constraints      │
│  2. Read chart-patterns.md (current state)            │
│  3. Read results.tsv (experiment history)             │
│  4. Pick target: pattern with lowest composite score  │
│  5. Propose change to chart-patterns.md               │
│  6. Git commit the change                             │
│  7. Run evaluation:                                   │
│     a. Static compliance (evaluate_skill.py)          │
│     b. 3× parallel clean-room (chart-test-container)  │
│     c. Convergence analysis (compare .py files)       │
│     d. Visual quality (read PNGs, score rubric)       │
│  8. Compute composite score                           │
│  9. Log to results.tsv                                │
│ 10. If score improved: KEEP (advance branch)          │
│     If score same/worse: DISCARD (git reset HEAD~1)   │
│ 11. Repeat                                            │
└─────────────────────────────────────────────────────┘
```

### Circuit Breakers
- **10 consecutive discards on same pattern**: Move to next-lowest-scoring pattern
- **Docker failure**: Report and halt (no point continuing without clean-room infra)
- **All patterns above threshold**: Report success, continue patrolling for regressions

---

## Files Modified
- `CLAUDE.md` — Add autoresearch section documenting the new workflow
- `scripts/evaluate_skill.py` — Add per-pattern scoring mode (currently whole-file only)
- `.gitignore` — Add `results.tsv`

## Files NOT Modified (Immutable During Autonomous Runs)
- `.claude/skills/matplotlib-chart/SKILL.md`
- `scripts/evaluate_skill.py` (the harness itself)
- `scripts/chart-test-container.sh`

## Modifiable Files (by the autonomous agent)
- `.claude/skills/matplotlib-chart/chart-patterns.md` — **Primary target.** Modified freely.
- `.claude/skills/matplotlib-chart/style-reference.md` — **Secondary target.** Higher bar: requires composite score improvement ≥0.05 (vs ≥0.001 for pattern changes).

---

## Resolved Design Decisions

1. **Visual quality scoring**: Claude Code reads PNGs directly (multimodal) and scores against a structured rubric. No external API key needed — the agent doing the loop IS the judge.
2. **Scope**: `/autoresearch` coexists with `/variation-analysis`. Different tools for different jobs — variation-analysis is targeted and human-guided, autoresearch is autonomous overnight mode.
3. **Style-reference.md mutability**: Modifiable by the agent, but with a higher bar (≥0.05 composite improvement). Prevents "cheating" by loosening standards while allowing genuine improvements.

---

## Implementation Phases

### Phase 1: The Scoring Function (inline in `/autoresearch` command)
The composite metric is computed by the agent itself during each loop iteration. No separate script — the agent runs the tools, reads the outputs, and computes the score, just as the autoresearch agent reads `run.log` and extracts `val_bpb`.

### Phase 2: The Research Program (`program.md`)
Write the human-authored strategy document. Programs the agent's research direction without touching code.

### Phase 3: The Loop Command (`.claude/commands/autoresearch.md`)
Create the `/autoresearch` slash command implementing the autonomous loop. Connects scoring to git keep/discard.

### Phase 4: Calibration
Run the scoring function against existing gallery entries:
- Do "good" charts (recent gallery) score higher than "bad" charts (early gallery)?
- Does the composite metric correlate with human judgment?
- Adjust rubric weights if needed.

### Phase 5: First Autonomous Run
- Create branch `autoresearch/first-run`
- Start with 1 experiment to verify loop mechanics
- Scale to overnight run once mechanics are solid

---

## Verification

1. **Scoring function**: Score all 9 patterns with current chart-patterns.md. Expect 0.7-0.95 range given recent convergence work.
2. **Calibration**: Compare scores of gallery entry 01 (original) vs entry 37 (latest). Later should score significantly higher.
3. **Loop mechanics**: Run one full loop iteration manually — modify a pattern, score, verify keep/discard logic works.
4. **Autonomous test**: Run 5 consecutive experiments on a single pattern. Verify results.tsv is correct and git history shows clean keep/discard decisions.
5. **Overnight run**: Run on all 9 patterns overnight. Review branch in morning.
