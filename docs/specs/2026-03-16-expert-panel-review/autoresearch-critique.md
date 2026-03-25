# Autoresearch Scoring Critique

## Current Scoring Formula

```
composite = compliance × (0.25 × convergence + 0.45 × visual + 0.25 × refinement)
```

## Incentive Misalignment Analysis

### Problem 1: Convergence Rewards Code Uniformity

The convergence layer (25% of composite) compares 5 structural dimensions across 3 parallel clean-room runs. Dimensions include API calls, palette, DPI, grid/despine, and core structure. Score = matching dimensions / total.

**Effect:** Any data-driven adaptation that one run makes and two don't — a moved legend, scaled figsize, contextual annotation — reduces convergence. Over 42 iterations, this creates a ratchet:

1. Run A adds an insightful annotation → convergence drops
2. Autoresearch adds rule "do not annotate" → convergence recovers
3. The skill becomes less communicative with each iteration

**Evidence:** P2's "Do not add `ax.annotate()` arrows or editorial text" rule was added during autoresearch iteration to improve convergence. It directly contradicts Design Philosophy P6.

### Problem 2: Red-Flag Caps Create Perverse Incentives

The visual rubric halves an entire PNG's score if ANY red flag is present (overlapping text, clipped content, default legend, visible spines). This means:

- A chart with one overlapping annotation loses 50% of ALL 12 visual checks
- The easiest fix: remove the annotation entirely → convergence improves too
- Result: autoresearch systematically strips annotations to avoid overlap risk

**Fix:** Red flags should zero only the specific affected check, not the entire PNG score.

### Problem 3: No Reward for Adaptiveness

The scoring has no dimension for "did the chart adapt appropriately to its data?" A chart that blindly copies the template with fixed figsize, generic labels, and default legend position scores the same as one that:
- Scales figsize for 20 categories vs 5
- Moves the legend to avoid occluding data
- Adds insight annotations specific to the dataset

### Problem 4: Pruning Targets Lowest Scores

The current pruning mode (every 10 experiments) targets the lowest-scoring pattern. But the highest-scoring patterns are the ones most likely to be over-specified — they score high on convergence precisely because excessive rules eliminate all variation.

**Fix:** Target highest-scoring patterns for pruning. Removing unnecessary rules from well-scoring patterns is structurally safe and reduces over-prescription.

### Problem 5: Rule-Count Penalty Is Too Weak

The current -0.02 per rule beyond 8 is additive and applied to refinement only. A pattern with 12 rules loses only 0.08 from refinement (one of four layers). This is insufficient to counteract the convergence benefit of adding rules.

**Fix:** Use a multiplicative signature_penalty applied to the entire composite. This makes rule accumulation structurally costly.

## Proposed Scoring Changes

### New Formula
```
composite = compliance × (0.15 × convergence + 0.40 × visual + 0.20 × refinement + 0.20 × adaptiveness) × signature_penalty
```

### Key Changes
1. **Convergence: 0.25 → 0.15** — Still measured, but reduced weight stops it from driving rule accumulation
2. **Visual: 0.45 → 0.40** — Still dominant, shares space with adaptiveness
3. **Refinement: 0.25 → 0.20** — Slightly reduced
4. **Adaptiveness: NEW 0.20** — Rewards data-driven choices (figsize scaling, semantic palette, occlusion avoidance)
5. **signature_penalty** — Multiplicative: `min(1.0, 1.0 - 0.05 × max(0, signature_count - 4))`. A pattern with 5 signature items loses 5%, with 8 loses 20%. Much stronger than the old -0.02 additive penalty.

### Convergence Redefined as Outcome Consistency

Replace code-level dimension comparison with visual outcome comparison:
1. Same chart type and data encoding visible
2. Same palette family applied
3. Same despine/grid configuration visible
4. Legend present with frame styling
5. Annotations present (value labels or insight annotations)

Code differences that produce visually identical outcomes = matching. This stops penalizing legitimate code variation.

### Adaptiveness Layer (5 Binary Checks)
1. Figsize scales for data volume (not fixed regardless of data)
2. Annotations reflect data-specific insights (not just generic labels)
3. Legend positioned to avoid data occlusion
4. Palette matches data semantics (diverging for ±, sequential for ranking)
5. At least one data-driven choice beyond template copy-paste

### Red-Flag Fix
Replace "halve entire PNG score" with "reduce the specific affected check to 0". Prevents removing labels to avoid overlap risk.

### Pruning Frequency and Targeting
- Every **5** experiments (was 10)
- Target **highest-scoring** pattern (was lowest)
- Removing signature items improves signature_penalty → simplification is structurally advantaged
