# Autoresearch for Skill Development

Inspired by [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch) — an autonomous AI research loop that modifies code, evaluates a scalar metric, keeps improvements, discards regressions, and repeats indefinitely (~100 experiments overnight).

**The question:** Can we apply the same pattern to autonomously improve a Claude Code skill?

---

## Expert Panel

### The Panel

1. **Dr. Alex Chen** — AI Research Systems Architect (Karpathy-like perspective)
   - Built autonomous experiment pipelines at scale. Thinks in terms of tight loops, scalar metrics, and ratcheting mechanisms.

2. **Maya Torres** — Developer Tools & Skill Authoring Expert
   - Former IDE/copilot team lead. Thinks about what makes generated code reliable and how to measure "specification quality."

3. **Prof. James Whitfield** — Data Visualization & Perception Researcher
   - Published on chart readability, colorblind accessibility, and visual cognition. Thinks about what makes charts objectively "good" vs subjective taste.

4. **Priya Sharma** — Production Systems & Automation Architect
   - Built CI/CD and autonomous systems at scale. Thinks about failure modes, observability, and when to stop.

5. **David Park** — Product Strategist (Skeptic)
   - Former product lead. Questions whether autonomous improvement actually serves end users or just optimizes proxy metrics.

---

### Key Insight: The Metric Problem

The fundamental difference between autoresearch and skill improvement:

> **Alex Chen:** "Autoresearch works because val_bpb is a single, objective, monotonic scalar. Lower is always better. The agent never needs to ask 'is this good?' — the number tells it. For chart generation, you don't have that. But here's the thing: you *almost* do. Your variation-analysis already measures convergence — how many structural dimensions produce identical code across clean-room runs. That's your val_bpb."

> **Maya Torres:** "I'd push back slightly. Convergence rate measures specification quality, not output quality. A pattern could converge perfectly on ugly charts. You need two metrics: (1) does the pattern produce consistent code, and (2) does that code produce good charts. The first is objective and automatable. The second... you need the LLM to judge."

> **Prof. Whitfield:** "Actually, 'good chart' is more objective than people think. We can decompose it: Does it have proper axis labels? Is the color palette accessible? Are annotations legible? Is the data-ink ratio reasonable? Is the layout balanced? Each of these is binary or near-binary. A rubric of 15-20 such checks, scored 0/1, gives you a surprisingly good scalar."

> **David Park:** "I want to flag something everyone's missing. The goal isn't 'best possible chart pattern' — it's 'most useful skill for Tim.' If the autonomous loop over-specifies patterns, you lose flexibility. A pattern that converges 10/10 on structural dimensions but can only handle 3 types of datasets is worse than one that converges 7/10 but handles 20. Be careful what you optimize for."

---

### The Architecture

> **Alex Chen:** "Map it directly. Three files:
> - `prepare.py` → `evaluate_skill.py` + `chart-test-container.sh` (immutable evaluation infra)
> - `train.py` → `chart-patterns.md` (the single file the agent modifies)
> - `program.md` → `program.md` (human-authored research direction)
>
> The loop: read program.md → pick a pattern → modify chart-patterns.md → run 3 clean-room tests → score → keep if improved, revert if not → repeat. Fixed time budget per experiment: one Docker clean-room run is ~3 minutes. Three parallel runs = ~3 minutes wall clock. So you get ~15-20 experiments per hour."

> **Priya Sharma:** "The keep/discard mechanism needs more nuance than autoresearch. With val_bpb, there's one number. Here you'd have a composite score — say, static_compliance (0-1) × convergence_rate (0-1) × visual_quality (0-1). If any component drops, discard. If the composite improves, keep. But you need a baseline score before each experiment to compare against."

> **Maya Torres:** "I'd add a critical guardrail: the agent should only modify ONE pattern per experiment, and the experiment should only evaluate THAT pattern. This keeps the blast radius small and the keep/discard decision clean. Exactly like autoresearch only touches one file."

---

### The Composite Metric

The panel converges on a **three-layer scoring function**:

#### Layer 1: Static Compliance (objective, fast, ~2 seconds)
Run `evaluate_skill.py` on the modified pattern. Binary pass/fail on:
- `sns.set_theme()` exact match
- `sns.despine(left=True, bottom=True)` present
- `dpi=150` correct
- No deprecated APIs
- Legend styling correct
- Annotation color `dimgrey`

**Score: 0.0 (any failure) or 1.0 (all pass)**

#### Layer 2: Convergence Rate (objective, slow, ~3 minutes)
Run 3 parallel clean-room tests with different prompts from the pool. Compare generated `.py` files across structural dimensions (API calls, palette, figsize, annotation style, legend config, title format, tick style, grid config, DPI/save, pattern-specific).

**Score: dimensions_converged / total_dimensions (0.0 to 1.0)**

#### Layer 3: Visual Quality (LLM-judged, ~30 seconds per chart)
Claude Code reads each generated PNG (multimodal) and scores against a structured rubric:
- Layout & spacing (0/1): Is the chart well-proportioned with no overlapping elements?
- Color & accessibility (0/1): Is the palette applied correctly and colorblind-safe?
- Typography (0/1): Are titles, labels, annotations properly sized and colored?
- Annotations (0/1): Are data values annotated where expected?
- Overall publishability (0/1): Would this chart be acceptable in a blog post or report?
- **All 3 PNGs must pass all checks** (3/3 requirement)

**Score: checks_passed / total_checks (0.0 to 1.0)**

#### Composite Score
```
skill_score = static_compliance × convergence_rate × visual_quality
```

Multiplicative so any zero kills the score (a pattern that doesn't comply with style rules is always 0, regardless of convergence or visual quality).

> **Prof. Whitfield:** "The visual quality rubric should be calibrated against your gallery. Take your best 5 charts (the ones you'd put in the blog), score them with the rubric, and verify they score ≥0.8. Then take your worst 5 (early gallery entries you replaced), verify they score ≤0.5. If the rubric can't distinguish good from bad in your own data, it's useless."

> **David Park:** "I'd also track a 'flexibility score' — how many unique prompts from the pool produce valid charts. A pattern that only works with 3/10 prompts is fragile, even if those 3 converge perfectly."

---

### The Autonomous Loop

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
│     d. Visual quality (LLM judges PNGs)               │
│  8. Compute composite score                           │
│  9. Log to results.tsv                                │
│ 10. If score improved: KEEP (advance branch)          │
│     If score same/worse: DISCARD (git reset HEAD~1)   │
│ 11. Repeat                                            │
└─────────────────────────────────────────────────────┘
```

> **Alex Chen:** "The key design choice from autoresearch: NEVER STOP. Once started, the agent runs until manually interrupted. If it runs out of ideas, it re-reads program.md, reviews experiment history, tries combining previous near-misses, tries more radical changes. ~15 experiments/hour means ~100+ overnight."

> **Priya Sharma:** "Add a circuit breaker: if 10 consecutive experiments are discarded, pause and write a summary to `results.tsv` explaining what was tried and why nothing worked. This prevents burning compute on a plateau. But don't stop — move to the next-lowest-scoring pattern."

---

### Where the Panel Diverges

**On visual quality automation:**
> **Prof. Whitfield:** "LLM-as-judge for visual quality is good enough for autonomous iteration. You're not trying to replace human taste — you're trying to catch regressions. If a change makes charts worse, the LLM will catch it 90% of the time."

> **David Park:** "90% isn't enough for autonomous operation. That 10% miss rate means ~10 bad changes get kept per 100 experiments overnight. The user wakes up to a mess. I'd require a higher bar — maybe 3/3 clean-room PNGs must all pass the visual rubric, not just average."

**On scope of modifications:**
> **Alex Chen:** "Let the agent modify style-reference.md too, not just chart-patterns.md. Some improvements require changing the shared conventions."

> **Maya Torres:** "Absolutely not. Style-reference.md is like prepare.py — it's the fixed evaluation standard. If the agent can change both the pattern AND the reference, it can 'cheat' by loosening the standard. Keep it immutable during autonomous runs."

**On gallery documentation:**
> **Priya Sharma:** "Drop the gallery requirement for autonomous runs. The git history IS the documentation. Gallery entries are for human-curated narrative, not machine output. Let the autonomous loop just log to results.tsv. The human reviews the branch later and cherry-picks interesting experiments into gallery entries."

> **David Park:** "Agreed. The gallery is part of the blog story. Autonomous experiments are raw material, not finished narrative."

---

### The Agent IS the Judge

In Karpathy's autoresearch, `evaluate_bpb()` is a deterministic Python function — run the model, compute the number. Here, Layer 3 (visual quality) requires Claude Code itself to read PNGs and score them. This means:
- The judge and the modifier are the same agent (potential bias)
- Mitigation: The rubric is structured and binary (pass/fail per dimension), not subjective
- Mitigation: Layers 1 and 2 are fully objective and serve as a floor
- Mitigation: All 3 clean-room PNGs must pass every rubric check (David Park's "3/3 requirement")
