# Expert Panel Analysis: Design Philosophy for the matplotlib-chart Skill

**Date:** 2026-03-09
**Topic:** Whether a set of guiding principles (analogous to Python's "Zen of Python") would improve the chart-generation skill's decision-making in novel situations

**Research context:** Three research agents surveyed 30+ sources across Tufte, Cleveland & McGill, Cairo, Few, Wilke, Knaflic, Muth, Schwabish, Rougier et al., WCAG, and the matplotlib/seaborn ecosystem. Key finding: **no existing "Zen of Visualization" exists in the literature**, but strong cross-cutting principles emerge from multiple sources.

---

## The Panel

**1. Dr. Maren Engel** — Information Visualization Researcher, UC San Diego
*Primary lens: Perceptual science and evidence-based design.*
20 years studying how humans decode charts. Co-author on papers extending Cleveland & McGill. Believes every design choice should trace back to a perceptual finding.

**2. Kwame Asante** — Staff ML Engineer, AI Tooling Startup
*Primary lens: How LLMs consume and operationalize instructions.*
Built internal "skill" and "persona" systems for code-generating agents. Obsesses over what makes instructions *actionable* for an AI vs. decorative filler.

**3. Elise Navarro** — Data Visualization Editor, The Economist
*Primary lens: Editorial chart craft at scale.*
Manages a team that ships 50+ charts/week under a strict house style. Knows firsthand what happens when principles are too abstract vs. too prescriptive.

**4. Dr. Jonas Frey** — Author, "Clarity First: A Practitioner's Guide to Scientific Figures"
*Primary lens: Publication-quality charts for researchers.*
Teaches workshops on matplotlib for academics. Has seen thousands of bad figures and distilled his feedback into repeatable patterns.

**5. Rina Chowdhury** — Senior Accessibility Engineer, Datawrapper
*Primary lens: Inclusive design and colorblind accessibility.*
Leads accessibility compliance for a major chart tool. Pushes back when "aesthetics" conflicts with "everyone can read this."

---

## Question 1: Would golden rules actually help an AI agent, or are they redundant?

**Kwame** leads on this one — it's his bread and butter.

> The existing skill has excellent *tactical* rules: "use `sns.despine(left=True, bottom=True)`", "use `dpi=150`". These are unambiguous and the agent follows them reliably. But tactical rules don't help when the agent encounters a *novel situation* — a chart type not covered by the 9 patterns, an unusual dataset shape, or an ambiguous user request. That's where principles earn their keep. They act as a **decision-making tiebreaker** when concrete rules run out.

**Dr. Engel** agrees, with a nuance:

> The Zen of Python works because Python developers face dozens of micro-decisions per hour where the language permits multiple approaches. Chart generation is similar — for any given dataset, there are many *valid* chart designs. Principles like "maximize data-ink ratio" or "position encodes more accurately than color" give the agent a *ranking function* over design alternatives. Without them, the agent defaults to whatever pattern is closest, even when a different approach would serve the data better.

**Elise** adds the editorial angle:

> At The Economist, our style guide is 80 pages of tactical rules. But we *also* have five principles on a single card that every new designer memorizes. The rules tell you *what* to do; the principles tell you *why*, which matters when rules conflict. For example: "labels should be horizontal" conflicts with "don't truncate axis labels." The principle "readability trumps convention" resolves the conflict. An AI agent needs the same escape valve.

**Verdict: Yes, golden rules add value** — not as replacements for the tactical rules, but as a decision-making layer above them for novel situations and rule conflicts.

---

## Question 2: What should the principles be?

**Dr. Frey** frames the constraint:

> Tim's skill already embodies a specific aesthetic — this isn't a general-purpose visualization textbook. The principles should codify *Tim's philosophy*, not try to be universal. That means: Tufte-leaning minimalism, but tempered with practitioner pragmatism. The skill already removes spines, uses dimgrey annotations, favors whitegrid — the principles should explain the *worldview* behind those choices.

**Dr. Engel** proposes a structure:

> I'd organize around three tiers: (1) **What to show** — principles about data fidelity and chart selection, (2) **How to show it** — principles about visual encoding, ink, and clutter, (3) **Who sees it** — principles about accessibility and readability. This maps to the perceptual pipeline: data → encoding → perception.

**Rina** pushes on accessibility:

> Most "Zen" lists treat accessibility as an afterthought. In Tim's skill, colorblind safety is already baked into the palette choices — that's great. But the principles should elevate it to a *first-class concern*, not just a checkbox. Something like "if it doesn't work in greyscale, it doesn't work" or "encode meaning twice — never rely on color alone."

**Kwame** brings it back to the agent:

> For an LLM, principles need to be **short, concrete, and opinionated**. "Beautiful is better than ugly" works for Python because developers intuit what "beautiful code" means. But "beautiful chart" is too vague — the agent will over-decorate. Better: "Every element earns its ink." That's short, memorable, and *actionable* — the agent can literally check each element and ask "does this earn its presence?"

The panel converges on these candidate principles, refined through discussion:

1. **Above all else, show the data.** (Tufte — the prime directive)
2. **Every element earns its ink.** (Data-ink ratio, reframed as a test)
3. **Prefer position over color, color over size.** (Cleveland & McGill hierarchy, compressed)
4. **Grey is a color. White space is a feature.** (Muth + Schwabish — the minimalist foundation)
5. **Despine, degrid, then add back only what the reader needs.** (Tim's workflow, made explicit)
6. **Annotate the insight, not just the axis.** (Cairo + Knaflic — charts should *say something*)
7. **Encode meaning twice — never rely on color alone.** (Wilke/WCAG — accessibility as principle)
8. **Consistency across panels; variety across charts.** (Multi-panel coherence vs. chart-type adaptation)
9. **The reader should never do arithmetic.** (Cleveland — if they need to compare, plot the comparison)
10. **When in doubt, remove.** (Darkhorse "remove to improve" + Tufte "erase non-data-ink")

**Dr. Frey** on what was deliberately left out:

> I'd resist including "choose the right chart type" — that's a skill the whole workflow already addresses. Same with "label your axes" — that's a tactical rule, not a principle. And I'd avoid anything about "tell a story" — Tim's charts are for research papers, not dashboards. The principles should match the use case.

---

## Question 3: Where should they live?

**Kwame** is emphatic:

> **SKILL.md, at the top, before the workflow phases.** SKILL.md is always loaded — it's the agent's first context. Principles buried in style-reference.md will be read *after* the agent has already started planning. You want the principles to prime the agent's decision-making *before* it touches any code. Think of it as the preamble to the constitution — it frames everything that follows.

**Elise** agrees:

> At The Economist, the principles card is on the wall, not in the appendix. Same logic. Put them where they're seen first, every time.

**Dr. Engel** adds:

> Keep them in a clearly delimited section — a fenced block or a numbered list with a header like "Design Philosophy" or "Guiding Principles." Don't interleave them with the tactical rules. The agent should be able to distinguish "this is a principle (flexible, guides judgment)" from "this is a rule (rigid, always apply)."

**Rina:**

> One thing — don't call it "Zen of Visualization." That implies universal truth. Call it something personal, like "Design Philosophy" or "Chart Principles." It's Tim's aesthetic, not a standard.

**Verdict: Top of SKILL.md**, in a dedicated "Design Philosophy" section between Persona and Phase 1. Short, numbered, clearly separated from the tactical rules.

---

## Question 4: Prescriptive or philosophical?

**Kwame:**

> For an AI agent, the sweet spot is **philosophical but testable**. "Every element earns its ink" is philosophical (it's a worldview), but the agent can operationalize it (look at each element, ask "is this needed?"). Avoid pure philosophy like "beauty matters" — the agent can't act on that. Avoid pure prescription like "always use dimgrey" — that's already in the tactical rules.

**Dr. Frey:**

> The Zen of Python nails this. "Flat is better than nested" is a *preference statement* — it says "prefer X over Y" without saying "never use Y." That's exactly right for visualization principles. "Prefer position over color" doesn't mean never use color — it means reach for position encoding first.

**Verdict: Philosophical preferences, stated as testable heuristics.** "Prefer X over Y" and "every X should Y" formulations. Not "always" or "never."

---

## Question 5: How many?

**Elise:**

> The Economist's principles card has five. Our designers can recite them from memory. I've never seen anyone memorize 19 things. For an AI agent, memory isn't the constraint — context window is. But *signal dilution* is real. Ten principles where each one matters is better than 19 where half are filler.

**Kwame:**

> For an LLM, the sweet spot is **7-12**. Fewer than 7 and you haven't covered enough edge cases. More than 12 and the agent starts treating them as a checklist to satisfy rather than a philosophy to internalize. The Zen of Python has 19 but several are jokes ("Although that way may not be obvious at first unless you're Dutch"). Strip the humor, you're at about 13 substantive principles.

**Dr. Engel:**

> Miller's 7±2 applies to human chunking, not LLMs. But concision forces *prioritization*, which is the real value. If you can't fit it in 10, you haven't figured out what matters most.

**Verdict: Aim for ~10.** Enough to cover the key tensions, few enough that each one carries weight.

---

## Panel Convergence

The panel unanimously recommends:

1. **Yes, add principles** — they serve as a decision-making layer above tactical rules, especially for novel situations
2. **~10 principles**, philosophical but testable, stated as preferences not absolutes
3. **Place in SKILL.md**, at the top, in a "Design Philosophy" section before the workflow
4. **Name it "Design Philosophy"**, not "Zen of..." — it's Tim's aesthetic, not a universal standard
5. **Draft list of 10 principles** as proposed above, refined to match Tim's existing style choices

### The Final 10 Principles

```
 1. Above all else, show the data. (Tufte — the prime directive)
 2. Every element earns its ink. (Data-ink ratio, reframed as a test)
 3. Prefer position over color, color over size. (Cleveland & McGill hierarchy, compressed)
 4. Grey is a color. White space is a feature. (Muth + Schwabish — the minimalist foundation)
 5. Despine, degrid, then add back only what the reader needs. (Tim's workflow, made explicit)
 6. Annotate the insight, not just the axis. (Cairo + Knaflic — charts should say something)
 7. Encode meaning twice — never rely on color alone. (Wilke/WCAG — accessibility as principle)
 8. Consistency across panels; variety across charts. (Multi-panel coherence vs. chart-type adaptation)
 9. The reader should never do arithmetic. (Cleveland — if they need to compare, plot the comparison)
10. When in doubt, remove. (Darkhorse "remove to improve" + Tufte "erase non-data-ink")
```
