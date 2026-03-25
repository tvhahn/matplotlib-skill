# Expert Panel Analysis: Autoresearch Scoring Methodology

Date: 2026-03-21

## Panel Composition

| # | Expert | Role | Primary Lens |
|---|--------|------|-------------|
| 1 | **Dr. Maren Kessler** | Psychometrician, Educational Testing Service (retired) | Scale design, ceiling effects, item difficulty calibration |
| 2 | **Raj Patel** | Staff Research Scientist, LLM Evaluation at a frontier lab | Benchmark saturation, self-evaluation bias, Goodhart's Law in AI evals |
| 3 | **Chloe Fontaine** | Principal Data Visualization Engineer, The Pudding | Visual quality assessment — what separates "competent" from "excellent" |
| 4 | **Marcus Webb** | Red-team lead at an AI safety org | Adversarial scoring, gaming vectors, perverse incentives |
| 5 | **Dr. Yuki Tanaka** | Independent researcher, previously ran autonomous code-gen optimization loops at Google DeepMind | Practitioner who has hit score plateaus, reward hacking, and metric collapse firsthand |

---

## The Evidence: Score Distribution from `results.tsv`

26 rows across 16 experiments:

| Metric | Min | Median | Max | Rows at 1.0 |
|--------|-----|--------|-----|-------------|
| Compliance | 1.0 | 1.0 | 1.0 | 26/26 (100%) |
| Visual | 0.819 | 0.958 | 1.0 | 2/26 (8%) |
| Refinement | 0.8 | 1.0 | 1.0 | 22/26 (85%) |
| Adaptiveness | 0.6 | 1.0 | 1.0 | 22/26 (85%) |
| **Composite** | **0.767** | **0.979** | **1.0** | **1/26 (4%)** |

7 of 9 patterns scored >= 0.95 at baseline. P9 scored a perfect 1.000 before any optimization.

---

## Dr. Maren Kessler — Psychometrician

> I've spent 30 years designing assessments, and the first thing I look for is ceiling effects. This instrument has catastrophic ceiling effects.

### Problem: The effective scoring range is 5 points wide

When refinement=1.0 and adaptiveness=1.0 (true in 85% of rows), the composite formula collapses to:

```
composite = (0.50 x visual + 0.50) x signature_penalty
```

This means the composite is bounded between 0.50 and 1.00 regardless of visual quality. And since visual scores are routinely 0.90+, the actual operating range is [0.95, 1.00] — a 5-point band.

> You're trying to distinguish between "good" and "excellent" using a ruler that only has 5 tick marks. Every measurement looks the same.

### Problem: Binary checks are psychometrically useless at the top of the range

Refinement's 5 binary checks (no hardcoded data, defensive handling, code organization, consistent approach, save convention) are item-difficulty mismatched for the population being tested. Claude passes 4-5 of these on virtually every run. They function as a floor check, not a discriminator.

> In assessment design, we call these "too-easy items." They confirm competence but provide zero information about excellence. You'd never put 5 easy items on a graduate-level exam and expect them to rank students.

### Fix: Replace binary with graded scales

Every binary check should become a 0/1/2/3 scale with anchored criteria at each level. This unlocks the 50% of the composite currently ceiling-locked.

### Fix: Reweight the formula to give visual quality more room

Since refinement and adaptiveness are ceiling-locked, 50% of the weighted score is a constant. Visual carries all the variance but only gets half the weight. Either make the other dimensions actually discriminate, or give visual more weight.

---

## Raj Patel — LLM Evaluation Researcher

> This is a textbook case of Goodhart's Law: the moment you use a metric as an optimization target, it stops being a good metric. But there's a deeper problem — the evaluator and the optimizee are the same model.

### Problem: Self-evaluation bias

Claude is both generating the charts AND scoring them on the 12-check visual rubric. The rubric is subjective enough that the evaluator has wiggle room, and it will systematically wiggle toward higher scores.

> We see this in every LLM-as-judge benchmark. Models rate their own outputs 0.3-0.5 points higher than human evaluators on a 5-point scale. Your 12-check rubric has at least 6 checks that are judgment calls: "layout balance," "publication readiness," "data-appropriate adaptation." These are exactly the checks where self-evaluation bias hits hardest.

Looking at the data: visual scores of 0.958 mean losing only 3 points out of 72 (12 checks x 2 max x 3 PNGs). That's 36 individual judgments, and 33 of them are perfect scores. This is not plausible rigor.

### Problem: The rubric checks aren't independent

"Layout balance" (check 1), "data-ink ratio" (check 9), and "publication readiness" (check 10) are highly correlated. A chart with good layout will almost always score well on data-ink and publication readiness. The redundancy inflates scores because easy-to-pass dimensions get counted multiple times under different names.

> In evaluation design, we test for inter-item correlation and drop items that are redundant. You've got 12 checks that measure maybe 7 distinct qualities. The redundancy inflates scores.

### Fix: Anchor scoring with reference exemplars

For each check at each score level (0, 1, 2), provide a concrete description. Not "minor spacing issues" — instead: "labels overlap by >20% of character height = 0, labels are tight but readable = 1, generous spacing with no proximity conflicts = 2."

### Fix: Separate evaluation concerns

The evaluation prompt should be designed to resist optimism bias — include instructions like "justify every score of 2" and "a score of 2 should be rare, not the default."

---

## Chloe Fontaine — Data Visualization Engineer

> I've reviewed thousands of charts for publication. The rubric misses the things that actually separate good charts from great ones, and it tests too hard on the things that are trivially solved by templates.

### Problem: The rubric doesn't test what's hard

The 12 visual checks split roughly into:

**Easy (template-solvable, almost always 2/2):**
- Check 2 (palette correctness) — the pattern specifies the palette
- Check 4 (title format) — the template has exact fontsize/loc/pad
- Check 5 (axis label styling) — "dimgrey" is in the invariants
- Check 7 (legend compliance) — frame kwargs are in the template
- Check 8 (grid/spine cleanliness) — `sns.despine()` is invariant

**Hard (require genuine design judgment):**
- Check 1 (layout balance)
- Check 6 (annotation quality)
- Check 11 (data-appropriate adaptation)
- Check 12 (informativeness)

> 5 of your 12 checks are gimmes — they test whether the template was copy-pasted correctly. Of course scores are high. You're giving 10 out of 24 points for "did you follow the template?" and only 8 out of 24 for "did you make good design decisions?"

### Problem: No check for narrative coherence

The rubric has no check for whether the chart tells a story — does the title promise something that the visual delivers? Is there a visual hierarchy that guides the eye?

> The difference between a competent chart and a publication-worthy chart is almost entirely about narrative. Your rubric can't see it.

### Fix: Restructure the rubric into tiers

**Tier 1 — Template compliance (automated, not scored by LLM):**
Palette present, despine called, legend frame styled, title present, dpi correct. Move to `evaluate_skill.py`.

**Tier 2 — Craft (6 checks, scored 0/1/2):**
Layout balance, annotation placement, colorblind safety, data-ink ratio, color effectiveness, axis/scale appropriateness.

**Tier 3 — Design excellence (4 checks, scored 0/1/2, deliberately hard):**
Narrative coherence, typography hierarchy, reader self-sufficiency, adaptive composition.

> Tier 3 is where the discrimination happens. These checks should be hard to get 2 on. A score of 2 on "narrative coherence" means the chart doesn't just show data — it argues a point. Most generated charts can't do that.

---

## Marcus Webb — Adversarial Scoring Skeptic

> My job is to find ways a scoring system can be gamed. This one has at least four exploit vectors that autoresearch will find and abuse.

### Exploit 1: Annotation removal is always safe

The red-flag caps create an asymmetric risk. Adding an annotation risks overlap (check = 0). Not adding one also scores 0 on annotation quality. But adding one ALSO risks triggering other penalties. The expected value of annotations is negative.

> The expected value of adding annotations is negative. Any optimization loop will learn to minimize annotation count. Your scoring system is an annotation-killing machine.

The data confirms this: the previous expert panel found P2's "Do not add ax.annotate()" rule was created by autoresearch to avoid annotation risk.

### Exploit 2: Adaptiveness checks are trivially gameable

"At least one data-driven choice beyond template copy-paste" is satisfied by any column name substitution. Every binary check with a low bar becomes a free point.

### Exploit 3: The 3-PNG average smooths out failures

Scoring 3 PNGs and averaging means one bad chart is diluted by two good ones. Publication readiness means ALL outputs are publishable, not that the average is.

> You need a worst-of-3 component. If any single chart has a serious issue, that should be visible in the score.

### Exploit 4: Signature penalty is too generous

The penalty is `1.0 - 0.05 x max(0, count - 4)`. But 4 signature items is already a lot. The penalty should kick in at 3, and it should be quadratic (the marginal harm of over-specification accelerates).

### Fix: Add worst-of-3 floor

```
visual = max(0.4 x worst_png + 0.6 x mean_all_3, mean_all_3 x 0.85)
```

### Fix: Make annotations positive expected value

"Missing when data warrants" scores 0. "Present with overlap" scores 0. "Present, well-placed" scores 1-2. The only way to score above 0 is to attempt annotations.

---

## Dr. Yuki Tanaka — Autonomous Loop Practitioner

> I ran exactly this kind of loop for 18 months at DeepMind. The failure mode you're about to hit isn't score saturation. It's metric collapse — when the optimizer learns to satisfy the rubric without improving the output.

### Problem: The loop has no ground truth

In supervised learning, you have labels. Here, the "ground truth" is Claude's subjective evaluation of its own output. When the optimizer and evaluator share the same biases, improvements in score can reflect:
1. Actual improvement
2. Evaluator exploitation (scores higher without looking better)
3. Evaluator drift (standards shift over time)

> After ~50 iterations in our system, we found that 60% of "improvements" were type 2. We called it "rubric overfitting."

### Problem: No holdout evaluation

Every experiment uses the same rubric, same evaluator, same prompt pool. There's no held-out test.

> In ML, we'd never report training accuracy as the result. But that's what autoresearch does.

### Problem: No diminishing returns signal

P8 went from 0.979 to 0.993 over 8 experiments — a 0.014 improvement. Each experiment costs ~3 Docker runs. Past a certain score, you're optimizing noise.

> Any pattern above 0.95 should be frozen. Further optimization is more likely to be rubric overfitting than genuine improvement.

### Fix: Prompt holdout set

Split each pattern's prompt pool 70/30 train/holdout. Iterations use train prompts. Every 10 experiments, evaluate on holdout. Divergence = overfitting signal.

### Fix: Diminishing returns brake

Freeze patterns above 0.90 composite. Only re-evaluate in patrol mode.

### Fix: Periodic blind comparison

Every 10 experiments, produce unlabeled A/B galleries (current vs 10-experiments-ago). If users can't tell the difference, the last 10 experiments were noise.

---

## Synthesis

### Where the panel converges

All five panelists agree on three core problems:

1. **Refinement and adaptiveness are ceiling-locked.** Binary checks are too easy for Claude to pass. They contribute a constant 0.50 to the weighted composite in 85% of cases, leaving visual quality as the only discriminating dimension. (Kessler, Patel, Webb)

2. **The self-evaluator is too generous.** Claude scoring its own charts on subjective checks systematically inflates scores. The 12-check rubric doesn't anchor "2" strictly enough, and 5 of the 12 checks test template compliance rather than design judgment. (Patel, Fontaine)

3. **The loop lacks external validation.** No holdout prompts, no human checkpoints, no way to distinguish genuine improvement from rubric overfitting after scores pass ~0.95. (Tanaka, Webb)

### Where the panel diverges

- **Kessler** wants to fix the rubric scales (make binary checks graded, tighten anchors) — she believes the instrument can be saved with better calibration
- **Patel** is skeptical that self-evaluation can ever work well past 0.90 — he wants a separate evaluator model or human checkpoints
- **Fontaine** wants to restructure the rubric entirely into tiers (template compliance automated, craft scored, design excellence deliberately hard)
- **Webb** focuses on gaming vectors — worst-of-3 floors, steeper signature penalties, annotation-positive incentives
- **Tanaka** thinks the scoring is a secondary problem — the primary issue is running 10+ iterations on patterns already scoring 0.95+ with no diminishing-returns brake

### Prioritized Recommendations

**Tier 1 — Fix score saturation (highest impact):**

| # | Fix | Rationale | Panelist |
|---|-----|-----------|----------|
| 1 | Graduate refinement & adaptiveness to graded scales | Unlocks the 50% of composite currently ceiling-locked | Kessler |
| 2 | Move template-compliance checks to automated compliance | Removes 5 "free points" from visual rubric | Fontaine |
| 3 | Add 4 deliberately hard visual checks | Creates headroom at the top of the scale | Fontaine |
| 4 | Tighten rubric anchors with "justify every 2" guidance | Reduces evaluator generosity | Patel |

**Tier 2 — Fix gaming vectors:**

| # | Fix | Rationale | Panelist |
|---|-----|-----------|----------|
| 5 | Add worst-of-3 floor to visual scoring | Prevents one bad chart from being averaged away | Webb |
| 6 | Make annotation presence a positive signal | Stops the annotation-killing incentive | Webb |
| 7 | Steeper signature penalty (quadratic, starts at 4) | Over-specification accelerates in harm | Webb |

**Tier 3 — Fix evaluation validity (longer-term):**

| # | Fix | Rationale | Panelist |
|---|-----|-----------|----------|
| 8 | Prompt holdout set (70/30 train/holdout) | Detects rubric overfitting | Tanaka |
| 9 | Diminishing returns brake (freeze above 0.90) | Stops wasting compute on noise | Tanaka |
| 10 | Periodic blind comparison gallery | Ground truth checkpoint | Tanaka |
