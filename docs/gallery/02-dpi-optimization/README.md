# 02 -- DPI Optimization

## What Changed
- Phase 2: Added "Verification DPI" -- during iterative development, renders use 150 DPI
- Phase 5: Verification render always saves a 150 DPI PNG for LLM inspection; final save uses 300 DPI for publication
- style-reference.md: Updated "Saving Convention" to document verification vs final render

## Why
Rendering at 300 DPI during the iterative LLM verification loop is wasteful. The LLM only needs enough resolution to check visual correctness (spines, colors, layout). 150 DPI is sufficient for verification and renders faster. The final output still uses 300 DPI for publication quality.

## Prompt Used
See `../../scratch/test_chart_patterns.py` (no code changes to patterns -- this was a process/workflow change)

## Observations
- No visual difference in the gallery PNGs since the test script still uses 300 DPI for final output
- The improvement is in the development workflow: fewer wasted cycles during the fix-and-rerun loop
- This change makes the skill more practical for real use -- especially on large multi-panel figures where 300 DPI rendering is noticeably slow

## Before vs After
- **Before:** See `../01-current/`
- **After:** See PNGs in this folder (identical output -- the change is in the process, not the final render)

## Files Modified
- `SKILL.md`: Phase 2 adds verification DPI concept; Phase 5 rewritten with verification render step and numbered checklist
- `style-reference.md`: Saving Convention now documents three tiers (verification, publication, exploratory)

## Lessons Learned
- Skill files define process as well as output -- optimizing the verification loop is as valuable as optimizing the aesthetic
- Separating "verification quality" from "publication quality" is a pattern that applies to many generative workflows
