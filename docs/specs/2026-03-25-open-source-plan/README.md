# Plan: Open-Source the matplotlib Skill

## Context

This repo serves two audiences: (1) a distributable Claude Code skill for matplotlib/seaborn charts, and (2) a blog article evidence base with 52 gallery entries. The goal is to make it public so others can use the skill and contribute. Research across 23+ Claude Code skill repos and official documentation informed this plan.

**Decisions locked in:**
- **Approach:** Path C — monorepo with curated gallery
- **Gallery archive:** Move removed entries to a `gallery-archive` branch
- **Datasets:** Keep all 39 in repo (16 MB, well-attributed)
- **Clone size:** Archive branch + document `git clone --depth 1` for lightweight installs

---

## Research Summary

### Ecosystem (March 2026)
- **anthropics/skills** (103k stars) — official reference with document skills, template, skill-creator
- **Agent Skills open standard** (agentskills.io) — adopted by 30+ tools (Claude Code, Cursor, Gemini CLI, OpenAI Codex, VS Code Copilot, GitHub Copilot, JetBrains Junie, etc.)
- **obra/superpowers** (112k stars) — methodology-as-skills framework
- Plugin marketplace exists for distribution via `/plugin marketplace add`

### Patterns in Successful Repos

| Pattern | Example | Stars | Characteristics |
|---------|---------|-------|----------------|
| **Minimalist** | VibeSec-Skill | 728 | 3 files: LICENSE, README, SKILL.md |
| **Single-purpose + scripts** | ios-simulator-skill | 650 | SKILL.md + supporting scripts, evaluation results |
| **Plugin marketplace package** | expo/skills | 1.5k | `.claude-plugin/` dir, multiple skills |
| **Methodology framework** | obra/superpowers | 112k | Skills encode a development philosophy |
| **Domain collection** | claude-scientific-skills | 16.2k | 170+ skills grouped by domain |

### What Makes Skills Successful
1. **Easy installation** — one-command install via plugin marketplace or git clone
2. **Focused README** — leads with "what it does" and "how to install", not internals
3. **Progressive disclosure** — simple SKILL.md surface, deeper reference files on demand
4. **Cross-platform** — Agent Skills standard means one skill works everywhere
5. **Evaluation evidence** — ios-simulator-skill shows 100% pass rate vs 46% without skill

### What This Repo Has That's Unique
- **Iterative gallery** — no other skill repo documents its evolution with before/after snapshots
- **Autonomous iteration infrastructure** — `/autoresearch`, `/variation-analysis` commands
- **Design specs** — expert panel analyses, scoring rubrics, strategic direction docs
- **39 bundled datasets** with a YAML manifest and proper attribution

### Paths Evaluated

| Path | Approach | Verdict |
|------|----------|---------|
| **A** | Ship as-is with README update | Too heavy (63MB), 52 gallery entries overwhelm |
| **B** | Two repos (skill + blog archive) | Clean but two repos to maintain, cross-refs break |
| **C** | Monorepo with curated gallery | **Selected** — best balance of usability and educational value |
| **D** | Plugin-first restructure | Heaviest restructuring, loses blog framing |

---

## Implementation Steps

### Step 1: Create `gallery-archive` Branch

Before removing anything, preserve the full gallery:

```bash
git checkout -b gallery-archive
git checkout master
```

This branch preserves all 52 gallery entries. Easier to find than digging through commit history.

### Step 2: Curate Gallery to ~12 Milestone Entries

Keep entries that represent **phase transitions** (matching BLOG-NARRATIVE.md arc):

| Entry | Blog Phase | Why it stays |
|-------|-----------|--------------|
| `00-original-inspiration` | Origin | Source material from 4 projects |
| `_00-baseline-no-skill` | Baseline | What Claude produces without the skill |
| `01-original` | Baseline | First skill output — the "before" picture |
| `02-current` | Visual iteration | API modernization — first major improvement |
| `06-subplot-outlines` | Visual iteration | Design decision — panel frames |
| `08-clean-room-testing` | Infrastructure pivot | Docker clean rooms introduced |
| `09-visual-evaluation-protocol` | Infrastructure pivot | Systematic evaluation methodology |
| `26-full-suite-coverage` | Systematic cleanup | All 9 patterns passing |
| `27-p2-variation-analysis` | Variation analysis | Best-documented parallel clean room run |
| `38-autoresearch-overnight-v3` | Autonomous iteration | First autoresearch run |
| `43-expert-panel-restructure` | Autonomous iteration | Expert panel restructures scoring |
| `50-template-improvements-v2` | Current state | Latest output |

**Remove from HEAD** (40 entries): `03`, `04`, `05`, `07`, `10`–`25`, `28`–`37`, `39`–`42`, `44`–`49`

### Step 3: Reorganize Docs

Move blog-specific files into `docs/blog/`:

```
docs/
├── gallery/           # Curated ~12 milestone entries + TEMPLATE.md
├── blog/              # Blog narrative and outline
│   ├── BLOG-NARRATIVE.md    (moved from docs/)
│   └── outline/              (moved from docs/specs/2026-03-24-blog-outline/)
├── specs/             # Keep as-is (educational process artifacts)
├── guides/            # Keep as-is
├── idea-garden/       # Keep as-is
└── bugs/              # Keep as-is
```

### Step 4: Add `.claude-plugin/` for Marketplace Distribution

Create `.claude-plugin/manifest.json`:

```json
{
  "name": "matplotlib",
  "version": "1.0.0",
  "description": "Publication-quality matplotlib/seaborn charts with opinionated aesthetics",
  "skills": ["skills/matplotlib"],
  "repository": "https://github.com/tvhhn/matplotlib-skill",
  "license": "MIT",
  "author": "Tim VH"
}
```

Note: Verify manifest schema against current plugin marketplace spec before implementation.

### Step 5: Update SKILL.md Frontmatter

Add `license` field to align with Agent Skills open standard:

```yaml
---
name: matplotlib
description: "Generate publication-quality matplotlib/seaborn charts..."
argument-hint: "[description of chart to create]"
allowed-tools: Bash, Write, Read, Glob, Grep
license: MIT
---
```

### Step 6: Rewrite README for Public Consumption

Consumer-first structure:

```markdown
# matplotlib — Claude Code Skill

Publication-quality matplotlib/seaborn charts with an opinionated aesthetic.

[3 example output PNGs — pick best from gallery entry 50]

## Install

### Plugin Marketplace (recommended)
/plugin marketplace add tvhhn/matplotlib-skill

### Manual
git clone <repo> && ln -s $(pwd)/.claude/skills/matplotlib ~/.claude/skills/matplotlib

### Lightweight Clone (skill only, ~3 MB)
git clone --depth 1 <repo>

### Cross-Platform (Agent Skills Standard)
Works with Claude Code, Cursor, Gemini CLI, and any tool supporting the Agent Skills standard.

## What It Does
9 chart patterns, each with an opinionated template:
[Pattern table with thumbnails — P1 through P9]

## Datasets
Ships with 39 datasets for testing and demos. See data/datasets.yaml.

## How This Skill Was Built
docs/gallery/ documents iterative development across 50 iterations.
See docs/blog/ for the narrative arc.

## Development & Contributing
[Test commands, how to add patterns, advanced commands]

## License
MIT
```

### Step 7: Update CLAUDE.md

- Gallery workflow: reflect curated gallery
- Blog narrative reference: `docs/blog/BLOG-NARRATIVE.md` (new path)
- Remove reference to `scratch/`
- Add note about `gallery-archive` branch

### Step 8: Add LICENSE File

MIT license at repo root.

### Step 9: Add CONTRIBUTING.md

Brief guide: adding patterns, running tests, submitting gallery entries.

---

## Files Summary

| File | Action |
|------|--------|
| `README.md` | Complete rewrite (Step 6) |
| `CLAUDE.md` | Update paths and gallery workflow (Step 7) |
| `.claude-plugin/manifest.json` | New (Step 4) |
| `.claude/skills/matplotlib/SKILL.md` | Add `license` to frontmatter (Step 5) |
| `docs/blog/BLOG-NARRATIVE.md` | Move from `docs/` (Step 3) |
| `docs/blog/outline/` | Move from `docs/specs/2026-03-24-blog-outline/` (Step 3) |
| `docs/gallery/` | Remove ~40 entries (Step 2) |
| `LICENSE` | New — MIT (Step 8) |
| `CONTRIBUTING.md` | New (Step 9) |

## Execution Order

1. **Branch:** Create `gallery-archive` branch from current HEAD
2. **Back to master:** Remove 40 gallery entries
3. **Reorganize:** Move blog docs to `docs/blog/`
4. **Add files:** `.claude-plugin/`, `LICENSE`, `CONTRIBUTING.md`
5. **Update files:** SKILL.md frontmatter, CLAUDE.md paths, README rewrite
6. **Verify:** Run tests, check cross-references, confirm repo size

## Verification

1. `scripts/chart-test-container.sh --quick` — skill still works
2. All internal cross-references in CLAUDE.md and README resolve
3. `git log gallery-archive -- docs/gallery/` — confirm full history accessible
4. Repo size is ~25 MB (check with `git count-objects -vH`)
5. Read curated gallery entries 00 → 50 in sequence — confirms coherent story
6. `.claude-plugin/manifest.json` is valid JSON with correct paths
