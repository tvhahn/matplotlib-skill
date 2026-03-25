# Rules Audit: Per-Pattern Classification

Each rule in every pattern is classified as:
- **Signature** — defines the pattern's visual identity; must be preserved
- **Over-Constrained** — restricts legitimate creative choices; should become Guidance
- **Redundant** — restates a global invariant; should be removed (covered by Invariants Shorthand)

## P1 — Horizontal Bar (7 rules → 3 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | Use `sns.barplot()` — not `ax.barh()` | **Signature** | Keep |
| 2 | Use `palette="Blues_d"` — do not substitute | **Over-Constrained** | → Guidance: "Default Blues_d; use Greys_r + ACCENT_RED for emphasis" |
| 3 | Hide x-axis ticks with `set_xticks([])` | **Signature** | Keep (part of bar-end-labels identity) |
| 4 | Annotations use dimgrey + semibold | **Signature** | Keep |
| 5 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |
| 6 | Always read data from CSV | **Redundant** | Remove → Invariants |
| 7 | Apply dropna after loading | **Redundant** | Remove → Invariants |

## P2 — Vertical Bar (6 rules → 3 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | Use `sns.barplot(hue=x)` | **Signature** | Keep |
| 2 | Sort descending | **Signature** | Keep |
| 3 | Palette: rocket ≥5, DIVERGING ≤4 | **Signature** | Keep |
| 4 | "Do not add ax.annotate() arrows or editorial text" | **Over-Constrained** | **DELETE** — contradicts Design Philosophy P6 |
| 5 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |
| 6 | Always read CSV, dropna | **Redundant** | Remove → Invariants |

## P3 — Time Series (8 rules → 4 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | Use `ax.bar()` as primary layer | **Signature** | Keep |
| 2 | Red/blue bar coloring by reference | **Signature** | Keep |
| 3 | Rolling line uses pal[5] | **Signature** | Keep — soften "do not hardcode navy/black" to Guidance |
| 4 | 3 legend items with Patch + Line2D | **Signature** | Keep |
| 5 | Reference = 0 or mean (conditional) | **Over-Constrained** | → Guidance (logic is in template code) |
| 6 | Use pre-computed rolling when available | **Redundant** | Remove (defensive coding, not identity) |
| 7 | Filter NaN from rolling column | **Redundant** | Remove → Invariants (covered by dropna) |
| 8 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## P4 — Violin + Strip (5 rules → 3 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | Horizontal orientation default | **Signature** | Keep |
| 2 | White violins + black strip dots | **Signature** | Keep |
| 3 | `density_norm="width", inner=None, cut=0` | **Signature** | Keep |
| 4 | Bold-prefix title convention | **Redundant** | Remove (global convention, not P4-specific) |
| 5 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## P5 — Lollipop (8 rules → 4 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | Cubehelix pal[5] dark + pal[2] light | **Signature** | Keep |
| 2 | Three `ax.scatter()` calls (min/max/avg) | **Signature** | Keep |
| 3 | Annotate all three values per row | **Signature** | Keep |
| 4 | `ax.hlines()` min-to-max connectors | **Signature** | Keep |
| 5 | Exactly 2 legend items | **Over-Constrained** | → Guidance: "Default 2; add more if data warrants" |
| 6 | Set descriptive x-axis label | **Redundant** | Remove (general charting best practice) |
| 7 | Always read from CSV | **Redundant** | Remove → Invariants |
| 8 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## P6 — Decision Boundary (6 rules → 4 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | DIVERGING_COLORBLIND palette | **Signature** | Keep |
| 2 | Probability-sized dots (not contourf) | **Signature** | Keep |
| 3 | Do not import sklearn | **Over-Constrained** | → Guidance: "Default pre-computed; allow sklearn for raw data" |
| 4 | Two outside legends with add_artist | **Signature** | Keep |
| 5 | set_aspect(1) | **Signature** | Keep |
| 6 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## P7 — Heatmap (8 rules → 3 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | RdBu_r with vmin=-1, vmax=1, center=0 | **Signature** | Keep |
| 2 | annot=True, fmt=".2f" | **Signature** | Keep |
| 3 | square=True | **Signature** | Keep |
| 4 | No colorbar label | **Over-Constrained** | → Guidance |
| 5 | Data is pre-computed (load CSV) | **Redundant** | Remove → Invariants |
| 6 | Full matrix default (no triu/tril) | **Over-Constrained** | → Guidance |
| 7 | grid(False) not needed for sns.heatmap | **Redundant** | Remove (implementation note, not rule) |
| 8 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## P8 — Multi-Panel (8 rules → 4 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | GridSpec rows-first | **Signature** | Keep |
| 2 | Default line_color pal[5], shared y-axis | **Over-Constrained** | → Guidance: "Default single color for same metric; per-panel when metrics differ" |
| 3 | Subplot outlines (ax.patch) | **Signature** | Keep |
| 4 | grid(False) on every panel | **Redundant** | Remove → Invariants |
| 5 | Axis labels: left-col ylabel, bottom-row xlabel | **Signature** | Keep |
| 6 | Panel labels: counter-based bold prefix | **Signature** | Keep |
| 7 | Round-up grid sizing | **Over-Constrained** | → Guidance |
| 8 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## P9 — PR/ROC (9 rules → 4 signature)

| # | Current Rule | Classification | Action |
|---|---|---|---|
| 1 | Do not import sklearn | **Over-Constrained** | → Guidance |
| 2 | PR first (a), ROC second (b) | **Signature** | Keep |
| 3 | Three line layers (grey folds, pal[5] avg, orange baseline) | **Signature** | Keep |
| 4 | pal[5] for average line | **Signature** | Keep (part of #3) |
| 5 | Subplot outlines | **Signature** | Keep |
| 6 | Use ax.plot not axhline for baseline | **Redundant** | Remove (implementation detail) |
| 7 | Do not use fill_between | **Over-Constrained** | → Guidance |
| 8 | xlim(0,1), ylim(0,1.05) | **Signature** | Keep (full probability range) |
| 9 | Always use dpi=150, PDF+PNG, bbox_inches | **Redundant** | Remove → Invariants |

## Summary

| Pattern | Current Rules | → Signature | Removed (Redundant) | → Guidance (Over-Constrained) |
|---------|--------------|-------------|---------------------|-------------------------------|
| P1 | 7 | 3 | 3 | 1 |
| P2 | 6 | 3 | 2 | 1 (DELETED) |
| P3 | 8 | 4 | 3 | 1 |
| P4 | 5 | 3 | 2 | 0 |
| P5 | 8 | 4 | 3 | 1 |
| P6 | 6 | 4 | 1 | 1 |
| P7 | 8 | 3 | 3 | 2 |
| P8 | 8 | 4 | 2 | 2 |
| P9 | 9 | 4 | 2 | 3 |
| **Total** | **65** | **32** | **21** | **12** |
