# Blog Article Outline — Expert Panel Analysis

Date: 2026-03-24

## Context

Tim built a Claude Code skill for matplotlib charts over 50 gallery iterations. He wants to write a blog article about the journey — in his own voice, from his own experience as a researcher at Queen's University who took pride in beautiful charts. He needs a concise bullet-point outline, not draft prose. The guiding principle is Pressfield's "Nobody wants to read your shit." The focus is **tutorial-first (70%)** with the "automation went wrong" story as a compelling subplot (30%). Output: both a bullet outline with section beats AND a narrative arc overlay.

---

## The Panel

**1. Elena Voss** — Senior Technical Blog Editor, former editor at CSS-Tricks and Smashing Magazine
*Primary lens: What gets shared. Has edited 200+ developer blog posts and knows the difference between "technically correct" and "actually read." Focuses on structure, pacing, and the opening hook.*

**2. David Park** — Narrative Nonfiction Writer, author of two books on technology culture
*Primary lens: Story architecture. Turns technical material into narratives with tension and resolution. Thinks in scenes, not sections.*

**3. Aisha Rahman** — Developer Content Strategist, Head of Content at a devtools startup
*Primary lens: The developer reader. Knows what developer audiences scan, skip, bookmark, and share. Data-informed about content performance.*

**4. Dr. Tamara Liu** — Data Visualization Researcher & Practitioner, teaches at RIT
*Primary lens: Why aesthetics matter. Can articulate what most developers feel but can't explain — why one chart looks "professional" and another looks like a homework assignment.*

**5. "The Ghost"** — The Pressfield Principle, Embodied
*Primary lens: Ruthless economy. Every sentence is on trial. Asks one question: "Why should a busy person keep reading this?" Cuts anything that serves the writer but not the reader.*

---

## Panel Analysis

### Opening Salvo: What Is This Article Actually About?

**The Ghost:**
> Before anyone says a word about outlines, answer me this: why should a developer who's busy shipping features stop and read 2500 words about your matplotlib charts? Not why YOU think it's interesting. Why should THEY care? If you can't answer in one sentence, you don't have an article yet.

**Aisha (developer strategist):**
> I can answer that. The article is about **how to build a Claude Code skill that actually works** — with a real example that went through 50 iterations. That's the value proposition. Developers are adopting Claude Code right now and skills are new. Most people have written zero skills. A detailed walkthrough of building one — with the mistakes, the infrastructure, the scoring — that's a genuine resource. The chart aesthetics are the *example*, not the *point*.

**Elena (editor):**
> Aisha's right, and it clarifies the structure immediately. The article isn't "I made pretty charts." It's "Here's how to build a Claude Code skill, and here's what I learned when I tried to automate improving it." The charts are evidence, not the thesis.

**David (narrative writer):**
> But the charts ARE the hook. You can't open with "How to Build a Claude Code Skill" — that's a headline, not an opening. You open with something sensory. Tim's at Queen's University, he's making charts for his PhD research, and he cares about how they look. That's relatable. Every researcher has stared at a matplotlib chart thinking "this looks like garbage." Start there. Show the charts. Then pivot: "I turned this obsession into a Claude Code skill. Here's what I learned."

**The Ghost:**
> David, that opening has exactly two sentences of runway before the reader asks "so what?" The researcher-at-Queen's story earns you 3-4 sentences max. Show one beautiful chart, show one ugly default matplotlib chart, and get to the skill within the first 200 words. The reader doesn't care about your PhD. They care about making their charts not look ugly.

---

### The Central Debate: Tutorial vs. Story

**Aisha:**
> The user said 70/30 tutorial-first. I agree. Here's what developer readers actually do with blog posts: they scan for **"can I use this?"** If the answer is yes, they read more carefully. If the answer is no, they bounce. The article needs to establish utility fast — this is about building a Claude Code skill — and then deliver on that promise with concrete steps. The story (automation going wrong) is the seasoning, not the steak.

**David:**
> I hear you, but pure tutorials are forgettable. "Step 1, Step 2, Step 3" doesn't get bookmarked or shared. What gets shared is *insight*. The insight here is: **"I built an autonomous system to improve my skill, and it optimized for the wrong thing."** That's a universal lesson — it applies to any automated feedback loop, not just chart skills. The tutorial structure carries the reader through; the story makes them remember it.

**Elena:**
> The solution is interleaving. Each tutorial section delivers something practical. But every second or third section, you drop in a discovery — something surprising Tim learned. The "automation went wrong" moment is the biggest one, but there are smaller ones too: "comments in code work better than prose rules for LLMs," "three similar clean-room runs reveal what your spec underspecifies." These mini-discoveries keep the reader engaged between the how-to sections.

**Dr. Liu (data viz):**
> Can I add something? The charts themselves need to DO something in the article. Don't just sprinkle PNGs as decoration. Each image should make the reader go "oh, I see the difference." Show a before/after pair: here's what matplotlib gives you by default, here's what the skill produces. Show a convergence failure: here are three charts from three clean rooms, and look how different they are. Show the fix: here are three charts after tightening the spec. **Images as evidence**, not illustration.

**The Ghost:**
> Tamara just said the most important thing anyone's said. Every image earns its place or it's cut. I'd say this article needs exactly 4-6 images. Not 12. Not 8. Four to six. Each one is doing a specific job.

---

### What To Cut (The Ghost's Hit List)

**The Ghost:**
> Let me save Tim some pain. Here's what does NOT go in this article:
>
> 1. **The 50 gallery entries.** The reader doesn't care about your documentation process. Pick 4-6 moments. That's it.
> 2. **The scoring formula.** Nobody outside your project cares that `composite = compliance × (0.50 × visual + 0.25 × refinement + 0.25 × adaptiveness) × signature_penalty`. Mention that you built a scoring system. Don't explain the math.
> 3. **The full expert panel analysis.** This is backstory for you, not content for the reader. One sentence: "I ran a structured review and found the problem."
> 4. **The v1/v2 scoring distinction.** The reader doesn't know there was a v1. Just describe the final system.
> 5. **Pattern-by-pattern breakdowns.** "I have 9 patterns: horizontal bar, vertical bar, time series..." — fine. One sentence. Don't describe each one.
> 6. **The Design Philosophy list.** Ten principles is a sidebar or a link, not article content. Pick the 2 that matter most ("show the data" and "annotate the insight") and weave them in naturally.

**Elena:**
> Harsh but correct. I'd add: **don't explain what Claude Code is.** Your audience already knows. One sentence with a link, max. If someone doesn't know what Claude Code is, this article isn't for them.

**Aisha:**
> Agree on all cuts. The article should feel like you're showing a friend what you built over coffee — not presenting at a conference. Conference talks need completeness. Blog posts need momentum.

---

### The Outline

**Elena:**
> Here's my structural recommendation. Six sections, 2000-2500 words total when written out. Each section has a clear job.

**David:**
> I'll annotate with the narrative beats.

**Dr. Liu:**
> I'll flag where images earn their place.

---

#### Section 1: The Hook — "I'm Picky About Charts" (~250 words)

- Tim's identity: researcher at Queen's University who cared about chart aesthetics
- The universal pain: default matplotlib looks like a homework assignment
- Show ONE chart from Tim's research — something beautiful that makes the reader think "I want my charts to look like that"
- The pivot: "I turned my chart obsession into a Claude Code skill. Here's what I learned building it over 50 iterations."

**David:** *This is the "I'm like you" moment. The reader identifies with the aesthetic frustration. Keep it tight — this isn't backstory, it's a handshake.*

**Dr. Liu:** *IMAGE 1: One gorgeous chart from Tim's original research. Not a comparison yet — just something that makes the reader lean in.*

**The Ghost:** *250 words max. The reader decides whether to keep reading in the first 100. Don't waste them on your CV. "I'm a researcher. I care about charts. I built a thing. Here's what I learned." Done.*

---

#### Section 2: What's a Claude Code Skill? (~300 words)

- One-paragraph explanation: a skill is a markdown file that teaches Claude Code how to do a specific task — in this case, generate charts matching your personal aesthetic
- What goes IN a skill: style spec, chart pattern templates, a verification workflow
- What the skill produces: show the output (one-line prompt → publication-quality chart)
- The skill's scope: 9 chart patterns covering the most common types (bar, line, violin, heatmap, etc.)

**Aisha:** *This is the "can I use this?" section. The reader needs to understand what a skill IS and see that it works. One input/output example is worth 500 words of explanation.*

**Dr. Liu:** *IMAGE 2: Before/after — default matplotlib output vs. skill output for the same data. Side by side. This is the money shot.*

**Elena:** *Link to the skill repo or Claude Code docs here. Don't explain how to install Claude Code — just link.*

**The Ghost:** *No architecture diagrams. No file tree. The reader will explore the repo if they're interested. Your job is to make them interested.*

---

#### Section 3: How I Built It — The Iteration Loop (~400 words)

- Started with a baseline: captured what the skill produced on day 1
- Manual iteration: run the skill, look at the output, fix what's wrong, repeat
- The small stuff matters: despine consistency, annotation colors, legend frames, tick marks — things you don't notice until they're wrong
- Why baselines matter: you can't see improvement without a "before" picture
- The moment it stopped scaling: "I was spending 20 minutes per chart eyeballing details. I had 9 patterns. That's 3 hours per round."

**David:** *This is the "ascending action" — things are working but getting harder. The reader should feel the manual grind. Don't romanticize it.*

**Aisha:** *Practical takeaway: "If you build a skill, capture your baseline FIRST." This is advice the reader can use immediately.*

**The Ghost:** *Resist the temptation to list every change you made. Pick 2-3 vivid examples (one that's visual, one that's about consistency, one that surprised you). Let those stand for the whole phase.*

---

#### Section 4: Automating Quality — Docker Clean Rooms & Scoring (~500 words)

- The infrastructure pivot: to test a skill properly, the agent can't have access to previous outputs or your gallery of "right answers"
- Docker clean rooms: spin up an isolated container with ONLY the skill files and a dataset, give it a one-line prompt, see what comes out
- Why isolation matters: it's the difference between "can the skill reproduce my style?" and "can I hand-wave my way to something close?"
- Dataset diversity: 40+ datasets across 16 domains — the skill needs to work for penguins AND stock prices AND brain scans
- Building a scoring rubric: compliance checks (did it follow the style rules?), visual quality (does it look good?), adaptiveness (did it adjust to the data?)
- Running it overnight: the `/autoresearch` command proposes changes, tests them, keeps improvements, reverts regressions

**David:** *This is the "building the machine" section. The reader should feel the ambition: "I'm going to automate the improvement of my own skill." That's inherently compelling.*

**Aisha:** *This section has the highest density of reusable ideas. Clean-room testing, dataset diversity, scoring rubrics — a reader building ANY skill can use these. Emphasize the patterns, not the implementation details.*

**Dr. Liu:** *IMAGE 3: Three charts from the same prompt but different datasets — showing that the skill adapts to different data while maintaining the same aesthetic. This demonstrates what "quality" means concretely.*

**Elena:** *This is where the article earns its "tutorial" promise. Be specific enough that someone could replicate the approach, but abstract enough that they see how to adapt it to their own skill (not just charts).*

**The Ghost:** *Don't explain Docker. Don't explain what a rubric is. Your reader is a developer. Trust them. The insight is "isolate the skill from its own history" — that's the sentence that matters.*

---

#### Section 5: When Automation Went Wrong (~400 words)

- After 42+ automated iterations, scores were great (0.82 → 0.96)
- But something felt off: the charts were getting... boring. Technically correct but lifeless.
- The diagnosis: the scoring system rewarded consistency across parallel runs — if 3 clean rooms produced identical code, convergence was perfect
- The perverse incentive: creativity got penalized. If one run added an insightful annotation ("Renewables reached 75% of fossil fuel output by 2017") but another didn't, the convergence score dropped. So the system learned to prohibit annotations entirely.
- The smoking gun: Pattern P2 had a rule saying "Do not add ax.annotate()" — literally banning the thing that makes charts communicative
- The fix: restructured "Rules" into "Signature" (2-4 things that define the pattern's identity) and "Guidance" (flexible defaults). Replaced convergence-as-uniformity with an adaptiveness dimension that REWARDS data-driven choices.
- The result: P2 spontaneously added insight annotations in its very next run. The removal of one prohibition produced the biggest visual improvement of the entire project.

**David:** *This is the climax. The machine the hero built turned against its own purpose. Keep the emotion in — "something felt off" is the right register. The reader should feel the unease, then the satisfaction of the diagnosis.*

**Aisha:** *The transferable insight: "Your optimization metric becomes your product's personality. Choose it carefully." That's a takeaway that applies to any automated feedback loop — ML training, A/B testing, content recommendation, performance optimization.*

**Dr. Liu:** *IMAGE 4: The before/after of the annotation ban. Show P2 WITHOUT annotations (the "optimized" version) next to P2 WITH the spontaneous annotation after the fix. This is the visual proof of the perverse incentive.*

**The Ghost:** *This section is the reason someone shares the article. "I built an automation system and it optimized the creativity out of my charts" — that's a sentence that makes a developer stop scrolling. Earn it. Don't bury it in technical detail.*

**Elena:** *One thing to watch: don't over-explain the scoring math. "The system measured consistency by comparing code across parallel runs" is enough. The reader doesn't need the formula.*

---

#### Section 6: What I'd Tell You If You're Building a Skill (~300 words)

- **Start with taste.** A skill encodes your aesthetic judgment. Know what you want before you automate.
- **Capture baselines.** You can't see improvement without a "before."
- **Test in isolation.** If your skill only works when the agent has access to examples, it's not a skill — it's a crutch.
- **Measure what matters.** Your scoring metric becomes your skill's personality. If you measure code uniformity, you get uniform code. If you measure visual quality, you get quality.
- **Rules are expensive.** Each constraint you add removes a degree of freedom. Keep identity items to 2-4 per pattern. Everything else is guidance, not law.
- **Know when to stop.** 50 iterations was too many. The skill was good enough at iteration 20. The last 30 iterations taught me about automation, not about charts.

**David:** *End with honesty. "I over-iterated" is disarming and generous — it saves the reader from making the same mistake.*

**Aisha:** *These takeaways are the "bookmark trigger." Developers bookmark articles with numbered lists of hard-won lessons. Make each one concrete and actionable.*

**The Ghost:** *This is the landing. Don't add a conclusion paragraph after this. The last bullet IS the conclusion. End on "know when to stop." That's your mic drop.*

---

## Narrative Arc Overlay

**David's story map:**

```
Reader's Journey:

HOOK        "I'm picky about charts"        → IDENTIFICATION
            (I feel that too)                  Reader thinks: "me too"

PROMISE     "Here's a Claude Code skill"     → CURIOSITY
            (and it works)                     Reader thinks: "I want that"

RISING      "I iterated manually, then       → INVESTMENT
ACTION       automated it"                     Reader thinks: "I could do this"

CLIMAX      "The automation optimized the     → SURPRISE
             creativity out of my charts"      Reader thinks: "oh no / oh wow"

RESOLUTION  "I fixed the metric and           → SATISFACTION
             everything got better"            Reader thinks: "that makes sense"

LANDING     "Here's what I'd tell you"        → ACTIONABLE
                                               Reader thinks: "I'm going to try this"
```

**Emotional temperature:**

| Section | Reader Feeling | Tim's Job |
|---------|---------------|-----------|
| 1. Hook | Recognition ("I hate ugly charts too") | Be relatable, show taste |
| 2. What's a skill | Curiosity ("I could build one of these") | Demonstrate value quickly |
| 3. Manual iteration | Respect ("this takes care") | Show craft, establish credibility |
| 4. Infrastructure | Ambition ("this is clever") | Share reusable patterns |
| 5. Went wrong | Surprise + recognition ("I've seen this in my own work") | Be honest about failure |
| 6. Takeaways | Empowerment ("I know what to do") | Be generous with lessons |

---

## Image Guide

| # | What | Source | Job |
|---|------|--------|-----|
| 1 | One beautiful chart from Tim's research | Gallery 00 (original inspiration) | Hook — "I want my charts to look like that" |
| 2 | Before/after: default matplotlib vs. skill output | Gallery 01 vs Gallery 08 | Proof — the skill works |
| 3 | Three charts from different datasets, same aesthetic | Gallery 08 (clean room outputs) | Demonstrate adaptiveness |
| 4 | P2 without annotations vs. P2 with spontaneous annotation | Gallery 42 vs Gallery 43 | The perverse incentive, visualized |
| 5 | (Optional) Three clean-room outputs showing convergence | Gallery 27-35 (variation analysis) | What "testing in isolation" looks like |

**The Ghost:** *Four images minimum, six maximum. Every image without a caption that starts with "Notice how..." is wasted space.*

---

## Where the Panel Converges

1. **Tutorial-first is correct** — the practical value (how to build a skill) is what earns the reader's time
2. **The story is the spice, not the steak** — the "automation went wrong" moment makes the article memorable, but it's section 5 of 6, not the spine
3. **Four to six images, each doing a specific job** — evidence, not decoration
4. **2000-2500 words** — not 3500. Pressfield's ghost wins this one.
5. **End with takeaways, not a conclusion** — the last bullet point is the ending
6. **Don't explain Claude Code, Docker, or matplotlib** — trust the reader

## Where the Panel Diverges

- **David** wants more emotional register in the "went wrong" section — lingering on the unease before the diagnosis. **Elena** says keep it brisk; developers don't want to marinate in feelings.
- **Dr. Liu** wants a 5th image showing the scoring dashboard. **The Ghost** says absolutely not — "nobody cares about your rubric's numbers."
- **Aisha** thinks the title should be practical ("How I Built a Claude Code Skill for Charts in 50 Iterations"). **David** thinks it should be provocative ("My Automation System Optimized the Creativity Out of My Charts"). **Elena** suggests both — provocative title, practical subtitle.

## Title Options (for Tim to choose)

1. **"My Automation Optimized the Creativity Out of My Charts"** — provocative, shareable, but buries the tutorial angle
2. **"Building a Claude Code Skill: 50 Iterations of matplotlib Charts"** — practical, searchable, but forgettable
3. **"I Taught Claude to Make Beautiful Charts. Then It Forgot How."** — narrative hook, implies a story, makes you want to read
4. **"How I Built (and Nearly Broke) a Claude Code Skill for Charts"** — balanced, has tension, signals both tutorial and story
