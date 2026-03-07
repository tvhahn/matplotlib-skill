# 04 -- Verification Checklist

## What Changed
- Phase 5 step 3 rewritten from prose to a concrete 7-item numbered checklist
- Checklist covers: spine count, grid lines, legend framing, annotation color, subplot labels, default style leakage, text readability

## Why
The original Phase 5 verification was vague prose ("Verify the chart matches the style rules"). A numbered checklist is actionable -- the LLM can check each item systematically and report pass/fail, rather than making a subjective judgment about whether the chart "looks right."

## Prompt Used
No code changes in this iteration -- the checklist was added to SKILL.md Phase 5 (committed with the DPI optimization in iteration 02).

## Observations
- The checklist caught that the old Phase 5 still referenced `frameon=False` instead of `frameon=True` -- fixed in the same edit
- Having explicit expected values (e.g., "Count visible spines -- expected: 0") makes verification deterministic
- The checklist is ordered by visual impact: spines first (most obvious defect), text readability last (hardest to judge)

## Before vs After
- **Before:** See `../03-consistency-audit/`
- **After:** See PNGs in this folder (identical output -- this was a process change, not a visual change)

## Files Modified
- `SKILL.md`: Phase 5 step 3 rewritten as numbered checklist (committed in iteration 02)

## Lessons Learned
- "Verify it looks right" is not a useful instruction for an LLM -- it needs specific, checkable criteria
- Ordering checklist items by visual impact helps catch the biggest problems first
- A verification checklist is itself a form of documentation -- it tells future readers what "correct" means
