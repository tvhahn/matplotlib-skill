---
description: Run variation analysis across multiple chart patterns sequentially with per-pattern subagent isolation.
argument-hint: [P1,P3,P5] [--rounds N]
disable-model-invocation: false
allowed-tools: Agent, Bash(git *), Bash(ls *), Read, Edit, Write
---

# Variation Analysis — All Patterns

Run variation analysis across multiple chart patterns. Each pattern is handled
by a dedicated **Agent subagent** that runs the full workflow (rounds, fixes,
gallery entry, commit) in its own context. The orchestrator never reads .py
files or PNGs — it only sees each subagent's returned summary.

This solves the context window problem: each subagent only accumulates context
for ONE pattern's worth of clean-room runs.

## Guardrails

- **Max 5 rounds per pattern** (passed to each subagent)
- **No destructive changes** — add/modify only, never delete patterns
- **Style invariants** — `sns.set_theme()` and `sns.despine()` calls are immutable
- **Atomic commits** — each pattern gets its own commit, easy to revert individually
- **Docker failures** — if Docker fails for a pattern, the subagent reports failure and the orchestrator skips to next

## Arguments

Parse `$ARGUMENTS` for:
- **Pattern list** (optional): comma-separated like `P1,P3,P5` or `P1,P4`. Default: all 9 (P1–P9)
- `--rounds N` (optional, default 3, max 5): Number of rounds per pattern

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Workflow

### Step 1: Setup

1. Parse arguments: pattern list (default all 9), `--rounds N` (default 3, max 5)

2. Read these files to provide context to subagents:
   - `.claude/skills/matplotlib/patterns/` — current pattern files
   - `.claude/skills/matplotlib/style-reference.md` — palette/layout conventions
   - `scripts/chart-test-container.sh` — to extract prompt pools per pattern

3. Determine the next gallery number from `gallery-archive/`:
   ```bash
   ls -1d gallery-archive/[0-9]* 2>/dev/null | tail -1
   ```

4. Initialize results table:
   ```
   | Pattern | Rounds | Result | Gallery | Details |
   |---------|--------|--------|---------|---------|
   ```

### Step 2: Process Each Pattern

For each pattern in the list, sequentially:

#### 2a. Extract context for this pattern

- Read the specific pattern file from `patterns/` (e.g., `patterns/P2-vertical-bar.md`)
- Extract the pattern's prompt pool array from `chart-test-container.sh`
  (e.g., for P2, extract the `P2_POOL=(...)` array)

#### 2b. Build and spawn subagent

Spawn an Agent (general-purpose) with a prompt containing:

1. **Role:** "You are running variation analysis on pattern PN."

2. **Workflow steps** (condensed from `/variation-analysis`):
   - For each round R = 1..N:
     - Select 3 different prompts from the pool at offset `(R-1)*3` (mod pool size)
     - Tags: Round 1=A,B,C; Round 2=D,E,F; Round 3=G,H,I; Round 4=J,K,L; Round 5=M,N,O
     - Run 3 parallel clean rooms: `scripts/chart-test-container.sh --tag <tag> "<prompt>" &`
     - Read .py files and PNGs from results
     - Evaluate each chart against quality dimensions:
       identity preservation, visual quality, data-appropriateness, informativeness, pattern-specific checks
     - If all meet quality bar: stop rounds early. If issues found: fix the pattern file in `patterns/`, continue.
   - Create gallery entry `gallery-archive/NN-pX-variation-analysis/`:
     - Copy representative PNGs (round1-A.png, round1-B.png, etc.)
     - Write README.md with: What Changed, Why, Prompts Used (table of tag→prompt),
       Method, Quality assessments per round, Files Modified, Lessons Learned
   - Update CLAUDE.md gallery table
   - Commit: `📊 feat(skill): tighten PX via parallel clean-room variation analysis`

3. **Current pattern code** (copy-pasted from the pattern file)

4. **Prompt pool** (copy-pasted from chart-test-container.sh)

5. **Style conventions summary** (key rules from style-reference.md)

6. **Gallery number** to use for this pattern

7. **Rounds limit** from `--rounds`

8. **Return format:** "Return a one-line summary: `PX: [passed/issues found] in N rounds (M fixes). Gallery NN. [details]`"

#### 2c. Record result

When the subagent returns, record its summary in the results table.

#### 2d. Refresh context

Re-read the pattern files in `patterns/` to get any modifications the subagent made
(so the next subagent has accurate context).

#### 2e. Advance gallery number

Check `gallery-archive/` again to determine the correct next gallery number
(the subagent may or may not have created an entry).

### Step 3: Print Final Summary

Print the complete results table:

```
## Variation Analysis Results

| Pattern | Rounds | Result | Gallery | Details |
|---------|--------|--------|---------|---------|
| P1      | 1      | Passed (no changes) | 34 | All charts met quality bar |
| P4      | 3      | Passed (5 fixes) | 35 | figsize, legend loc, spacing improved |
| P7      | 3      | Issues remain (1) | 36 | annotation density needs user input |
```

## Error Handling

- **Docker not running:** First subagent will fail fast. Report and halt — no point spawning more.
- **Subagent failure:** Record "FAILED" in results table, continue to next pattern.
- **All patterns pass:** Report success — no changes needed.
- **Partial completion:** Results table shows progress. Completed patterns have atomic commits;
  un-attempted patterns can be run later with a smaller pattern list.

## Example Usage

```bash
# Run all 9 patterns with default 3 rounds each
/variation-analysis-all

# Run specific patterns
/variation-analysis-all P1,P4

# Run all patterns with 2 rounds each (faster)
/variation-analysis-all --rounds 2

# Run specific patterns with extended analysis
/variation-analysis-all P2,P5,P8 --rounds 5
```
