---
title: "I Taught Claude to Make Beautiful Charts. Then It Forgot How."
date: 2026-03-28
author: Tim
description: "How I built a Claude Code skill for publication-quality matplotlib charts over 50 iterations — and what happened when I automated its improvement."
tags: [claude-code, skills, matplotlib, data-visualization, automation]
word_target: 1200-1500
---

# I Taught Claude to Make Beautiful Charts. Then It Forgot How.

Lego. I loved lego as a kid. But it always irked me when my friends would come over and build with a mish-mash of colours. Didn't they want to make their creations look good? Then, as a young professional, I cringed when colleagues would give a PowerPoint presentation to executives and not seem to notice how visually unappealing their presentation and charts were. Are some people just oblivious to aesthetics?

It should come as no surprise then, that while working on my Master's at Queen's University, I took great pride in creating beautiful data visualizations. I would spend hours tweaking the smallest detail in a chart and getting it ready for a publication or presentation. It brought me great satisfaction, and I'm still proud of those charts I developed, mostly using matplotlib. See the lolipop chart below (and also featured in a blog post of its own) for an example of the kind of thing I'm talking about.

![Top performing models by PR-AUC score — lollipop chart with min/max/avg range, cubehelix palette, annotation-rich.](../gallery/00-original-inspiration/beautiful-plots/beautiful_lollipop.png)

Fast forward to today, and I'm now using Claude Code to make data visualizations for work and personal projects. But the "default" charts that Claude Code makes with matplolib are, well, not great. With that, I determined to build an *opinionated* Claude Code skill that would build beautiful charts. Here's what I learned while building it over 50 iterations, and how the optimization process I built led to an unexpected outcome.

---

## What's a Claude Code Skill?

As [Simon Willison put it](https://simonwillison.net/2025/Oct/16/claude-skills/), skills are "conceptually extremely simple: a skill is a Markdown file telling the model how to do something, optionally accompanied by extra documents and pre-written scripts."

The matplotlib skill that I've built has three main components:
- A style spec (palettes, fonts, despine rules)
- Nine pattern templates (one per chart type)
- A verification workflow

All one has to do, then, to use the skill in Claude Code is to say something like "Make a chart using the matplotlib skill". The skill will determine the chart type based on the dataset and apply the appropriate styling and patterns that I like. I made it to look like the charts as I would like them. It's opinionated, and that's the point.

Here's an example of what a chart looks like with the "vanilla" Claude Code, versus what it looks like with the matplotlib skill. Same data, same one-line prompt, but the skill's templates and style rules make it look much more polished and publication-ready.

The defaults chart:

![Default violin plot — vertical orientation, bold black title, colored violins (blue/orange/green), visible spines, box-plot insets, sample-size labels but no insight annotation.](no-skill-p4.png)

And the improved chart with the skill:

![With skill — horizontal violins in white/grey with strip overlay showing individual points, despined, median annotations (3,700 g, 3,700 g, 5,000 g), dimgrey text throughout.](skill-p4.png)

| Without the skill | With the skill |
|:-:|:-:|
| ![No skill — visible spines, default blue/orange/green, alphabetical order, no insight](../gallery/_00-baseline-no-skill/P02-iowa_electricity_2017.png) | ![With skill — despined, rocket palette, value-descending, "Renewables reached 75% of fossil fuel output by 2017"](../gallery/43-expert-panel-restructure/p2-vertical-bar.png) |
| *Default matplotlib. Spines, default colors, no story.* | *Same data, one-line prompt. Despined, sorted, annotated.* |

---

## How I Built It — And What Went Wrong

Like most things I do in Claude Code, I started building the skill by asking Claude Code to build it for me. Here's the initial prompt I used while in my weibull-knowledge-informed-ml project ([github link here](https://github.com/tvhahn/weibull-knowledge-informed-ml)) to create the skill:

<details>
<summary>Initial prompt to Claude Code (click to expand)</summary>

> I spent a lot of time creating beautiful visualizations for this project (weibull knowledge informed). You can see the final outputs in the @reports/figures/ (e.g. see the @reports/figures/ims_rul_results.png , or the @reports/figures/loss_function_percentages.svg, or the @reports/figures/spectrogram_with_binned_example.png ). These were primarily created with matplotlib and seaborn.
>
> What I want your help with is to plan the creation of a skill that is to be used for creating matplotlib charts and diagrams. I want this skill to be able to implement a similar aesthetic to what I have already done in this project, as well in some of the other projects that I will reference below. This skill is to assume the persona of a Python developer who is an expert in data visualization. They are opinionated and have strong feelings about clean and readable data visualization, like I have implemented in the examples.
>
> What I want you to do in this planning process is to do a thorough examination of all these example repos that have data visualizations using Matplotlib and Seaborn that I have worked on. I want you to inspect them and then come up with some findings that we can replicate within this skill. What are some aesthetics that I always seem to implement? What are some common color palettes that we should be using? Again, this skill can be opinionated and assume a standard default template for the color palettes and templating and those sort of things. Perhaps you should assemble a bunch of subagents to do the discovery and then have them come back so that you can synthesize their analysis.
>
> I am not an expert in writing skills, and I do not necessarily know how this should be done. So that, once these skills that flawed code implements, there can be reference files that are included. Look into this as well. Would this be beneficial? Look at the official claude code docs, on skills (use the /docs ) to see what best practice is.
>
> As part of this plan, as well, I want this skill (and all it's files, as needed) to be placed in the `dotfiles` folder, here: ~/dotfiles/claude/skills/ . You can already see the `setup-react` skill in there.
>
> The other projects, to be referenced are:
> - Documents/Beautiful-Plots -- only the decision boundary chart and the lollipop chart are to be considered. The other one was done in plotly
> - Documents/arxiv-code-search -- look in the `reports` folder to see the relevant diagrams
> - Documents/ml-tool-wear

</details>

Claude Code analyzed my charts across four projects and identified the recurring aesthetics; things like despined axes, cubehelix palettes, dimgrey annotations, etc. It assembled the skill with nine chart patterns. 

The first version worked, but it wasn't consistent. It was able to nail certain patterns (like the horizontal bar charts), but for other chart types it drifted. I entered the iteration loop: run the skill, look at the output, tweak the markdown pattern file with Claude Code, and repeat.

But it was taking way too much time, and I'm lazy. Plus, I had been reading about leaning into the automation capabilities of Claude Code (and agents in general). My default work pattern should be having them do more, not less. I should be less involved in the loop, not more.

Around this time I read Andrej Karpathy's "autoresearch" tweet:

https://x.com/karpathy/status/2030371219518931079

Heck, why not do that for the matplotlib skill? 

It worked, kinda. I had to create a scoring system to evaluate the quality of the charts, and that's not as straightforward as in Andrej's case where he's optimizing a single metric. How do you score a chart? I ended up with a composite that measured style compliance, visual quality, and how well the chart adapted to its dataset. I kicked it off overnight, and the scores climbed. But something was off.

The charts kept refusing to add annotations. I'd look at the output and think, why isn't it annotating the insight? I was explicitly asking for it in the pattern files, but the automation kept stripping it out. 

It took me a while to trace it back to the scoring system. The system rewarded consistency across parallel runs, but insight annotations are inherently creative — they varied between runs, and variation meant a lower score. So the automation learned to just... not annotate. I dug into the pattern files and found the smoking gun: a rule the automation had written saying "Do not add `ax.annotate()`."

| "Optimized" — technically correct | Fixed — alive again |
|:-:|:-:|
| ![P2 taxi fares — value labels but NO insight annotation (banned by automation)](../gallery/41-autoresearch-overnight-v7/p2-taxis.png) | ![P2 taxi fares — same aesthetic, now with "Queens leads — $3.6 higher avg fare than Bronx"](../gallery/50-template-improvements-v2/P2-vertical-bar.png) |
| *Technically perfect. Says nothing.* | *Same skill, one rule removed. Now it tells you something.* |

The fix ended up being simple. I restructured each pattern file to have a small "Signature" (the 2-4 things that define its identity) and then flexible "Guidance" for everything else. The very next run, P2 added an insight annotation on its own. One rule removed — biggest visual improvement of the entire project.

If there's one thing I took away from this whole process: your optimization metric becomes your product's personality. Measure uniformity, you get uniform. Measure quality and adaptiveness, you get charts that actually communicate.

---

## What I'd Tell You If You're Building a Skill

1. **Start with taste.** A skill encodes your aesthetic judgment. Know what you want before you automate.
2. **Capture baselines.** You can't see improvement without a "before." I saved the skill's output at every iteration so I could see what was actually getting better and what was regressing.
3. **Test in isolation.** I ran every test in a Docker container with nothing but the skill files and a dataset — no gallery, no git history, no prior outputs. If the skill can't reproduce your aesthetic from scratch, it's not encoding your taste. It's just pattern-matching from context.
4. **Measure what matters.** Your scoring metric becomes your skill's personality. If you measure code uniformity, you get uniform code. If you measure visual quality, you get quality.
5. **Rules are expensive.** Each constraint you add removes a degree of freedom. Keep identity items to 2–4 per pattern. Everything else is guidance, not law.
6. **Know when to stop.** 50 iterations was too many. The skill was good enough at iteration 20. The last 30 taught me about automation, not about charts.
