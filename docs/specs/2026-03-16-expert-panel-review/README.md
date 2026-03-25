# Expert Panel Review: Liberating the Matplotlib Skill

## Context

After 42+ gallery iterations of autoresearch optimization, the skill's 9 pattern files have become over-prescriptive. Rules added to improve convergence (3 clean-room runs producing identical code) have constrained the contextual design decisions that made the original inspiration charts beautiful.

## Panel Composition

Five expert perspectives evaluated the current skill state:

1. **Data Visualization Researcher** — evaluates against Tufte/Cleveland/Wilke principles
2. **Senior Matplotlib Developer** — assesses API usage, code quality, and maintainability
3. **Accessibility Specialist** — checks colorblind safety, readability, and WCAG compliance
4. **Information Design Practitioner** — judges communicative effectiveness and audience fit
5. **ML/AI Agent Specialist** — analyzes the autoresearch incentive structure and its effects on quality

## Key Findings

### 1. Over-Constrained Rules Contradict Design Philosophy

The skill's own Design Philosophy (P6: "Annotate the insight, not just the axis") directly contradicts rules added during autoresearch optimization. Example: P2 explicitly prohibits `ax.annotate()` arrows and editorial text — the exact tools needed to annotate insights.

**Root cause:** Autoresearch rewards code uniformity across 3 parallel runs. When one run adds an insightful annotation and two don't, convergence drops, creating pressure to prohibit the annotation.

### 2. Mechanical Rules Repeated Across All Patterns

Every pattern file independently restates: dpi=150, bbox_inches="tight", CSV reading, dropna, PDF+PNG dual save. These are invariants of the skill's identity, not pattern-specific rules. Repeating them:
- Inflates rule counts (triggering the rule-count penalty)
- Crowds out pattern-specific guidance
- Creates maintenance burden when values change (as happened with DPI 300→150)

### 3. Signature vs. Guidance Distinction Missing

Patterns mix immutable identity elements (e.g., "white violins with black dots" for P4) with flexible defaults (e.g., exact `bbox_to_anchor` positions) in the same "Rules (identity)" section. This forces Claude to treat everything as equally rigid.

### 4. Autoresearch Scoring Rewards Uniformity Over Quality

The convergence layer (25% of composite) measures whether 3 runs produce the same code. This directly penalizes:
- Data-driven figsize scaling
- Context-appropriate annotations
- Legend repositioning to avoid occlusion

## Prioritized Recommendations

1. **Extract invariants** — Create a shorthand in style-reference.md for rules common to all patterns. Remove from individual pattern files.

2. **Restructure pattern sections** — Replace "Rules (identity)" with:
   - **Signature** (2-4 items): What makes this pattern THIS pattern. Immutable.
   - **Guidance**: Advisory defaults with "consider X when Y" language.

3. **Delete anti-annotation rule** in P2 — It directly contradicts Design Philosophy P6.

4. **Revise autoresearch scoring** — Reduce convergence weight, add adaptiveness dimension, redefine convergence as outcome consistency (not code uniformity).

5. **Add Creative Brief to Phase 1** — Force Claude to think about which Design Philosophy principles apply BEFORE generating code.

## Files Affected

See `rules-audit.md` for per-pattern rule classification and `autoresearch-critique.md` for scoring analysis.
