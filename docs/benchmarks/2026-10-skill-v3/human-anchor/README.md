# Human anchor set — pending Tim

30 charts sampled from the v2 baseline and the v3 runs, stratified by model and prompt
kind, shuffled and renamed `c01`–`c30` so the version isn't visible.

**To rate:** open `charts/cNN.png`, read the request in `ratings.csv`, and fill in
`correct`, `fit`, `legible`, `insight`, `polish` (0–3 each) and `overall` (1–10), using
`scripts/judge_rubric.md`. Don't open `key.json` until you're done — it maps each chart
back to its version and run.

**Then:**

```bash
uv run scripts/judge.py anchor-compare docs/benchmarks/2026-10-skill-v3/human-anchor
```

prints each AI judge's Pearson correlation and mean absolute difference against your
ratings. VisJudge-Bench reports that frontier-model judges agree only moderately with
expert raters on chart quality, so this tells us how far to trust the absolute scores in
the v3 write-up (the blind pairwise result depends less on calibration).
