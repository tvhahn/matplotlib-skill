# Original Prompt — matplotlib Skill Genesis

**Session:** `555a5668-e07a-4665-b639-c059ff7bf93f`
**Project:** weibull-knowledge-informed-ml
**Timestamp:** 2026-03-05T20:28:38 UTC (12:28 PM PST)

---

I spent a lot of time creating beautiful visualizations for this project (weibull knowledge informed). You can see the final outputs in the @reports/figures/ (e.g. see the @reports/figures/ims_rul_results.png , or the @reports/figures/loss_function_percentages.svg, or the @reports/figures/spectrogram_with_binned_example.png ). These were primarily created with matplotlib and seaborn.

What I want your help with is to plan the creation of a skill that is to be used for creating matplotlib charts and diagrams. I want this skill to be able to implement a similar aesthetic to what I have already done in this project, as well in some of the other projects that I will reference below. This skill is to assume the persona of a Python developer who is an expert in data visualization. They are opinionated and have strong feelings about clean and readable data visualization, like I have implemented in the examples.

What I want you to do in this planning process is to do a thorough examination of all these example repos that have data visualizations using Matplotlib and Seaborn that I have worked on. I want you to inspect them and then come up with some findings that we can replicate within this skill. What are some aesthetics that I always seem to implement? What are some common color palettes that we should be using? Again, this skill can be opinionated and assume a standard default template for the color palettes and templating and those sort of things. Perhaps you should assemble a bunch of subagents to do the discovery and then have them come back so that you can synthesize their analysis.

I am not an expert in writing skills, and I do not necessarily know how this should be done. So that, once these skills that flawed code implements, there can be reference files that are included. Look into this as well. Would this be beneficial? Look at the official claude code docs, on skills (use the /docs ) to see what best practice is.

As part of this plan, as well, I want this skill (and all it's files, as needed) to be placed in the `dotfiles` folder, here: ~/dotfiles/claude/skills/ . You can already see the `setup-react` skill in there.

The other projects, to be referenced are:
- Documents/Beautiful-Plots -- only the decision boundary chart and the lollipop chart are to be considered. The other one was done in plotly
- Documents/arxiv-code-search -- look in the `reports` folder to see the relevant diagrams
- Documents/ml-tool-wear

---

## Follow-up Message (20:51 UTC / 12:51 PM PST)

Excellent plan. Also, I'd like you to create a document in the dotfiles folder, within the ~/dotfiles/docs/ , that describes this skill. Also, for this plan, are we using the ~/dotfiles/claude/commands/python-script.md ideas for inline scripts using uv? Also, before I approve the plan, I'd like you to consider if we should have any code style preferences? I do prefer the numpy docstrings, for example. What about modularity? What are python best practices for scripts? Think about this some more and provide me with some options and then your expert recommendation.

---

## Implementation Message (20:57 UTC / 12:57 PM PST)

> Implement the following plan: # Plan: `matplotlib-chart` Skill

_(12,791-character plan pasted back into Claude Code for execution)_

## Commit Message (21:03 UTC / 1:03 PM PST)

> git commit these changes in the dotfiles folder

Result: commit `871261a` — "feat(skills): add matplotlib-chart skill for publication-quality plots"
