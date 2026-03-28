---
description: Run baseline chart generation in clean rooms WITHOUT the matplotlib skill — produces comparison charts using only Claude's built-in knowledge.
argument-hint: [--quick] [--fixed] [--tag TAG] ["custom prompt"]
allowed-tools: Bash(scripts/*), Bash(ls *), Bash(docker *)
---

# Baseline Charts (No Skill)

Run the same 9 chart prompts used by `chart-test-container.sh`, but in clean rooms
with NO matplotlib skill installed. This produces a baseline showing what
Claude Code generates using only its built-in knowledge — no skill spec, no style
reference, no pattern files.

Results go to `logs/clean-room-baseline/` for side-by-side comparison with
skill-enhanced output in `logs/clean-room/`.

## Arguments

Parse `$ARGUMENTS` for flags to pass through to the script:
- `--quick`: Run 5 prompts instead of 9
- `--fixed`: Use original default prompts (index 0) instead of random selection
- `--tag TAG`: Tag the results directory for parallel runs
- Remaining text: Custom single prompt (overrides all pools)

${ARGUMENTS ? `**User input:** ${ARGUMENTS}` : ""}

## Workflow

### Step 1: Run Baseline

Run the baseline container script, passing through any flags from `$ARGUMENTS`:

```bash
scripts/chart-test-container-baseline.sh $ARGUMENTS
```

### Step 2: Report Results

1. List the results directory:
   ```bash
   ls -la logs/clean-room-baseline/latest/
   ```

2. For each numbered subdirectory, report:
   - The prompt used (from `prompt.txt`)
   - Whether a PNG was generated
   - The PNG file path

3. Summarize: how many of 9 prompts produced charts, how many failed.

4. Remind the user that results are in `logs/clean-room-baseline/latest/` and
   can be compared against skill-enhanced results in `logs/clean-room/latest/`.
