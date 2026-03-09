# Expert Panel Analysis: Autonomous Skill Iteration with Real Datasets

**Date:** 2026-03-08
**Topic:** Evaluating proposals for real-world datasets and autonomous agent-driven iteration of the matplotlib-chart Claude Code skill

**Note:** The repo already contains real datasets from the 4 source projects that inspired the skill (in `data/raw/{arxiv,beautiful-plots,ml-tool-wear,weibull}/`). The proposal below evaluates adding *additional* curated public datasets alongside these, and building autonomous iteration infrastructure.

---

## The Panel

**1. Mara Chen** — Senior Data Visualization Engineer, The New York Times Graphics Desk
*Primary lens: Visual quality and editorial standards. 12 years making publication-quality charts. Believes every pixel matters and that "good enough" charts erode trust.*

**2. Jake Moretti** — Staff Engineer, AI Developer Tools at Replit
*Primary lens: Agent loop design and failure modes. Built multiple autonomous coding agents. Has strong opinions about when to let agents run free and when to pull the leash.*

**3. Dr. Priya Sharma** — Research Data Scientist, Allen Institute for AI
*Primary lens: Open data curation and reproducibility. Maintains multiple benchmark datasets. Knows licensing pitfalls intimately.*

**4. Sam Okafor** — Independent Developer & Claude Code Power User
*Primary lens: Practical skill authoring. Has built 15+ Claude Code skills for personal and team use. Maintains a blog about LLM-assisted development workflows. Knows what actually works vs. what sounds cool.*

**5. Renata Voss** — Engineering Manager, Observability Platform at Datadog
*Primary lens: Feedback loops and iteration velocity. Runs teams that ship dashboards and visualization components. Obsessed with tight evaluate-improve cycles.*

---

## Proposal 1: Real Datasets for Testing

### Mara Chen (Data Visualization)

> "Synthetic data is the single biggest reason visualization tools produce mediocre output. When your test data is `np.random.randn(100)`, you never discover that your axis labels overflow with real country names, your color palette can't handle 47 categories, or your time series code chokes on irregular intervals. Real data has *texture* — outliers, missing values, skewed distributions — and that texture is exactly what exposes weaknesses in chart patterns."

> "But you don't need *big* data. You need *characterful* data. The Palmer Penguins dataset is 344 rows and it's taught more people about data viz than datasets 1000x larger. I'd pick datasets that have genuine visual stories to tell — the US healthcare spending paradox, global temperature trends, species differentiation. When the chart actually says something, you can evaluate whether the skill is helping or hurting the story."

**Recommendation:** Prioritize datasets with known, compelling visual narratives. If you can't look at the chart and immediately say "this is telling the right story," the dataset isn't pulling its weight.

### Dr. Priya Sharma (Data Curation)

> "The licensing question is the one most people skip and then regret. CC-0 and public domain datasets are your safest bet for committing to a repo. CC-BY is fine as long as you include attribution — a `SOURCES.md` in the data folder handles that. Stay away from anything with NC (non-commercial) clauses because the moment you blog about it commercially, you're in a gray area."

> "CSV is the right call. It's human-readable, it diffs cleanly in git, and every tool on earth reads it. Parquet is better for performance but terrible for a repo where you want people to *look* at the data. JSON is noisy for tabular data. Keep everything CSV with a header row."

> "I'd add one thing: include a `datasets.yaml` or `datasets.json` manifest that maps each file to its source URL, license, columns, and which chart patterns it's meant to exercise. That way the agent — or a human — can programmatically discover what's available without reading READMEs."

**Recommendation:** CSV only, CC-0/CC-BY/public domain only, and add a machine-readable manifest alongside the data.

### Sam Okafor (Power User)

> "I've been through this exact evolution with my own skills. The jump from synthetic to real data was transformative, but here's what I learned: don't try to have one canonical dataset per pattern. Have datasets that *overlap* across patterns. Gapminder works for bar charts, time series, lollipops, AND multi-panel grids. That overlap is a feature, not a bug — it forces your patterns to be flexible enough to handle the same data in different visual forms."

> "Also, keep the test harness as the single entry point. Don't scatter data loading logic across different scripts. Have the harness read a manifest, pick the right dataset for each pattern, and generate charts. That way when you add a new dataset, you just update the manifest and re-run."

**Recommendation:** Design for dataset-pattern overlap. Update the test harness to read from a manifest and support both synthetic and real data modes.

### Renata Voss (Iteration Velocity)

> "The `data/raw/` folder structure is fine, but think about what happens when you want to *add* a dataset six months from now. If the path conventions and manifest are clean, it's a 2-minute PR. If they're messy, it's an archaeology expedition. I'd structure it as `data/raw/{domain}/{filename}.csv` with a flat manifest at `data/datasets.yaml`. Keep it dead simple."

**Recommendation:** `data/raw/` with domain subfolders and a root manifest. Optimize for easy additions.

---

## Proposal 2: Autonomous Agent-Driven Iteration

### Jake Moretti (Agent Loop Design)

> "Okay, this is where I have the strongest opinions. Autonomous iteration loops are *powerful* but they have a failure mode I call 'gradient descent into mediocrity.' The agent optimizes for whatever heuristics you give it, and if those heuristics don't perfectly capture what makes a chart *good*, the agent will confidently march in the wrong direction. After 5-7 unattended iterations, you might come back to find it's 'improved' everything into a bland average."

> "Here's my concrete architecture recommendation: **don't let the agent modify skill files and evaluate them in the same iteration.** Separate the concerns. Iteration step 1: the agent *proposes* changes and writes them to a branch. Step 2: a *fresh* agent context evaluates the output charts against the originals. Step 3: the evaluation decides whether to accept or reject the changes. This prevents the 'I changed it so it must be better' bias."

> "For the autonomous mode, I'd cap it at 3 iterations without human input, not 5-7. Three is enough to make meaningful progress. Beyond that, the risk of compounding errors outweighs the time savings. After 3 iterations, surface a summary and let the human decide whether to continue."

**Recommendation:** Separate the proposer and evaluator into different agent contexts. Cap autonomous iterations at 3. Use git branches so every iteration is independently revertable.

### Sam Okafor (Power User)

> "I've tried building autonomous iteration loops for my Claude Code skills and here's the honest truth: **the supervised mode is 10x more valuable than the autonomous mode.** When I'm in the loop after each iteration, I catch things like 'the agent removed the annotation opacity because it couldn't verify it visually, and now the chart looks worse.' The agent's idea of improvement and mine diverge quickly."

> "That said, the *structure* of having a slash command that runs one iteration — evaluate, propose, change, regenerate, document — is incredibly valuable. I'd build that first and make it rock-solid. The autonomous loop is just calling that slash command N times with a wrapper. Don't over-engineer the autonomy; nail the single iteration."

> "For the evaluation document, here's what I'd want to see: a table showing which patterns were modified, what specific changes were made, a before/after screenshot reference, and a confidence score for each change. Something I can scan in 30 seconds to decide 'accept all / reject all / cherry-pick.'"

**Recommendation:** Build the single-iteration slash command first. Make it excellent. Autonomous mode is just a loop around it — add it later.

### Mara Chen (Data Visualization)

> "The agent evaluating chart quality is the hardest problem here. Here are heuristics that actually work for programmatic quality checks, in rough priority order:"

1. **Style compliance** — Does the generated code contain the required `sns.set_theme()` call, `sns.despine()`, correct DPI, legend styling? This is pure text matching and the easiest to automate.
2. **Render success** — Does the script run without errors and produce a non-zero-byte image file?
3. **Visual regression** — Compare output image dimensions, color histograms, and layout against a known-good baseline. You won't catch everything, but you'll catch catastrophic regressions.
4. **Code smell detection** — Does the generated code use deprecated API calls? Are there hardcoded magic numbers that should be parameterized? Does it follow the pattern structure in `chart-patterns.md`?
5. **Annotation completeness** — Are titles, axis labels, and legends present? (Can be checked by parsing the matplotlib figure object before saving.)

> "What you *cannot* automate: whether the chart tells the right story, whether the aesthetic choices are harmonious, whether the data-ink ratio is appropriate. These require human eyes. Accept that limitation and design accordingly."

**Recommendation:** Build a tiered evaluation: automated checks (style compliance, render success, visual regression) plus human review for aesthetic judgment.

### Renata Voss (Iteration Velocity)

> "The evaluation document is the linchpin of this whole system. If it's too verbose, nobody reads it. If it's too sparse, you can't make decisions. Here's the format I'd use:"

```markdown
# Iteration 07 — 2026-03-08

## Summary
One-sentence description of what this iteration focused on.

## Changes Made
| Pattern | File | Change | Confidence |
|---------|------|--------|------------|
| P3 Time Series | chart-patterns.md | Added rolling window annotation | High |
| P5 Lollipop | chart-patterns.md | Fixed dumbbell connector alignment | Medium |

## Automated Checks
- [ ] All patterns render without error
- [ ] Style compliance: 9/9 patterns pass
- [ ] No deprecated API calls
- [ ] DPI consistency: all 300

## Charts Generated
[Links to before/after PNGs in gallery folder]

## Agent Notes
What the agent thinks went well and what it's uncertain about.
```

> "Keep it scannable. A human should be able to review an iteration in under 60 seconds."

**Recommendation:** Structured evaluation document with a changes table, automated check results, and chart links. Optimized for fast human scanning.

### Jake Moretti (Agent Loop Design)

> "One more critical thing: **every iteration must be an atomic git commit on its own branch.** The autonomous loop should be: create branch -> make changes -> run tests -> commit -> evaluate -> if pass, merge to a staging branch. If the human comes back and says 'iteration 4 was bad,' they can just drop that commit. If you're making all changes on a single branch with mixed commits, rollback becomes surgery."

**Recommendation:** One branch per iteration, atomic commits, staging branch for accepted iterations.

---

## Addendum: Context Contamination and Isolation (post-panel research)

A critical concern was raised after the initial panel: the iteration agent could "cheat" by reading previous gallery entries, evaluation documents, and test outputs. This is analogous to grading a test while having the answer key open.

**Research findings** from Claude Code official documentation:

1. **Custom subagents** (`isolation: worktree`) run in separate git worktrees with their own system prompt. They do NOT inherit the parent's CLAUDE.md or conversation history. The `skills:` frontmatter injects skill content directly — no disk discovery needed.

2. **Permission deny rules** (`Read(/docs/gallery/**)`) block Claude's built-in Read/Grep/Glob tools from accessing specific paths. Evaluated deny-first, so deny always wins.

3. **PreToolUse hooks** can validate every tool call and block contaminating reads at runtime.

4. **Sparse-checkout worktrees** can physically remove contaminating files so they don't exist in the agent's filesystem at all.

5. **Docker-in-Docker** (since this runs in a devcontainer) could spin up a clean container with only skill files + datasets for maximum isolation. More complex but provides the strongest guarantee.

**Recommended layered approach:** Custom subagent with `isolation: worktree` + post-checkout file removal + permission deny rules. Docker-in-Docker reserved as a future option for overnight autonomous batch runs.

---

## Where the Panel Converges

1. **Real datasets are a clear win.** Everyone agrees this is the right next step. Keep them small (under ~300KB total), CSV format, permissive licenses, with a machine-readable manifest.

2. **Build the single-iteration command first.** Nail the evaluate -> propose -> change -> regenerate -> document cycle before adding autonomous looping. The supervised mode is the foundation.

3. **Automated evaluation has clear limits.** Style compliance and render success are automatable. Aesthetic judgment is not. Design the system knowing the agent will catch code-level issues but miss visual ones.

4. **Cap autonomous iterations at 3, not 5-7.** The panel is unified on this: compounding errors are the biggest risk. Let the human re-enter the loop after 3 iterations.

5. **Git discipline is non-negotiable.** Atomic commits per iteration, branches for isolation, easy rollback.

## Where They Diverge

- **Jake** wants separate proposer/evaluator agents to prevent self-assessment bias. **Sam** thinks that's over-engineering for a personal skill repo — a single agent with good heuristics is sufficient.
- **Mara** wants visual regression testing (image comparison). **Renata** thinks the ROI is too low for a skill that's evolving rapidly — the baselines would need constant updating.
- **Sam** is skeptical that autonomous mode will deliver value beyond "cool demo." **Renata** thinks even 2-3 autonomous iterations could save meaningful time if the heuristics are solid.

---

## Actionable Recommendations (Prioritized)

### Do First
1. **Add public reference datasets to `data/raw/public/`** — Palmer Penguins, Gapminder, Tips, Global Temperature, Car Crashes, Breast Cancer Wisconsin, Health Expenditure, Iowa Electricity. Add a `datasets.yaml` manifest covering both existing source-project data and new public datasets, plus `SOURCES.md` with attribution.
2. **Update the test harness** to support a `--real-data` flag that reads from the manifest (both source-project and public datasets) instead of generating synthetic data. Keep synthetic mode as default.

### Do Next
3. **Build the single-iteration slash command** (`/iterate-skill` or similar) that runs: evaluate current state -> identify one improvement area -> make targeted change -> regenerate charts -> produce evaluation markdown -> commit as gallery entry.
4. **Define the automated evaluation checklist** — style compliance, render success, code smell detection. Run these checks as part of every iteration.

### Do Later
5. **Add autonomous loop mode** — wrap the single-iteration command with a `--iterations N` flag, capped at 3. Each iteration creates an atomic commit on its own branch. Produce a summary document at the end.
6. **Consider visual regression** — if the skill stabilizes enough that baselines make sense, add image comparison as a stretch goal.
