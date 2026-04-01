# Reconvened Panel: Compressing the Blog Post

Date: 2026-03-31

## Brief

Tim has ~865 words already written (290 in the hook, 155 in the skill explanation, 420 in the "How I Built It" intro with the initial prompt in a collapsible `<details>` tag). The prompt text is collapsed, so visible prose is closer to ~445 words. Target: 1200–1500 words total. Sections 3–5 need to collapse from three full sections (~1300 words planned) into one compressed section (~400–600 words).

---

## The Panel Reacts

**The Ghost:**
> I've been waiting for this call. The original outline was 2000–2500 words and honestly, Tim was right to feel the drag. The article has two things worth saying: "here's how to build a skill" and "my automation optimized the creativity out." Everything else is scaffolding. Cut the scaffolding.

**Elena (editor):**
> The good news is that sections 1 and 2 are already tight. They do their jobs. The problem was always sections 3, 4, and 5 trying to be three separate acts when they're really one montage. In film terms: you don't need to show every training session. You show the hero training, you show a calendar flipping, and you cut to the fight.

**Aisha (developer strategist):**
> The collapsible prompt is smart — it's ~250 words that readers opt into. Don't count it against your budget. That means your visible prose is ~445 words, leaving you 750–1050 words for the compressed middle and the takeaways. That's plenty.

**David (narrative writer):**
> Here's my concern with radical compression: the "went wrong" moment is the reason this article gets shared. If you compress it to two sentences, you lose the emotional beat. I'm fine killing the manual iteration and clean room sections as standalone stories. But the autoresearch-went-wrong moment needs at least a paragraph of setup and a paragraph of payoff. That's your climax. You can't montage the climax.

**The Ghost:**
> David's right, but his "at least a paragraph" better mean 4–5 sentences, not 12. The setup is one sentence: "I built an overnight automation loop inspired by Karpathy's autoresearch." The failure is one sentence: "After 42 iterations, the scores climbed to 0.96 — but the charts were lifeless." The diagnosis is one sentence: "The scoring system penalized creativity because annotations varied between runs, so the system learned to ban them entirely." The fix is one sentence: "I restructured rigid rules into flexible guidance, and the skill spontaneously started annotating insights again." That's four sentences. That's the whole story. Everything else is padding.

**Dr. Liu (data viz):**
> The before/after images do the heavy lifting here. One pair — the "optimized but soulless" chart next to the "fixed and alive" chart — is worth 200 words of explanation. Keep that pair. Cut the trios, the variation analysis grids, the mid-iteration states. One before/after for the skill demo (section 2, already there), one before/after for the perverse incentive (section 3 compressed). That's it. Four images total.

**Elena:**
> So the new structure is: Hook → What's a skill → How I built and nearly broke it → Takeaways. Four sections, not six. The middle section does triple duty: initial prompt (already written), montage sentence about iteration, and the autoresearch story. It's one section with three beats, not three sections with one beat each.

**Aisha:**
> I like it. And the clean room mention fits naturally into the autoresearch explanation — "I tested in isolated Docker containers so the skill couldn't cheat from prior outputs." That's one clause inside one sentence. The reader gets the concept without a full section.

**David:**
> One more thing: the transition from section 2 into the compressed section 3 needs to feel like acceleration, not abbreviation. The reader shouldn't feel like you skipped something. They should feel like you're moving fast because the story is picking up speed. The initial prompt → "it worked but wasn't consistent" → "I iterated manually for weeks" → "then I found Karpathy's autoresearch" — that's a montage that feels intentional, not rushed.

**The Ghost:**
> Exactly. Speed is a feature when it's deliberate. The reader doesn't want three sections of build process. They want to get to the twist.

---

## Revised Outline

### Section 1: The Hook (~290 words) — KEEP AS-IS
Already written. Lego → Queen's → matplotlib obsession → "I built a skill."

**Image:** Lollipop chart from Beautiful-Plots (already in place).

### Section 2: What's a Claude Code Skill? (~155 words) — KEEP AS-IS
Already written. Willison quote, three components, before/after demo.

**Images:** No-skill vs. with-skill violin pair (already in place), plus one before/after option pair from the existing options.

### Section 3: How I Built It — And What Went Wrong (~400–500 words) — REWRITE/COMPRESS

This is the new merged section. Three beats in one section:

**Beat 1: The initial build** (~100 words, partially written)
- Keep the intro sentence and the collapsible initial prompt (already there)
- Add 2–3 sentences: Claude analyzed charts across 4 projects, identified common patterns, assembled the skill. The first version worked but wasn't consistent.

*Draft prose suggestion:*
> Claude Code analyzed my charts across four projects, identified the recurring aesthetics — despined axes, cubehelix palettes, dimgrey annotations — and assembled a skill with nine chart patterns. The first version worked. But it wasn't consistent. Some patterns nailed the look; others drifted. So I entered the iteration loop: run the skill, look at the output, tweak the markdown pattern file, repeat. For weeks.

**Beat 2: The automation leap** (~100 words)
- One sentence about manual iteration hitting a wall
- Karpathy's autoresearch as the inspiration — brief explanation
- Clean rooms as one clause ("tested in isolated Docker containers so the skill couldn't see prior outputs")
- The overnight run: scores climbed from 0.82 to 0.96

*Draft prose suggestion:*
> But nine patterns times multiple datasets times eyeballing each output — the manual loop didn't scale. Around this time, I came across Andrej Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) — an autonomous loop that modifies code, evaluates a metric, keeps improvements, and discards regressions. The mapping was obvious: my pattern files were the "code," a composite quality score was the metric, and isolated Docker containers (where the skill couldn't see prior outputs or my gallery of "right answers") were the test environment. I built a slash command, kicked it off overnight, and woke up to scores climbing from 0.82 to 0.96. Technically perfect charts.

**Beat 3: The perverse incentive** (~150–200 words)
- "Something felt wrong" — the charts were lifeless
- The diagnosis: scoring rewarded uniformity, so creativity got penalized
- The smoking gun: a rule saying "Do not add ax.annotate()"
- The fix: rules → signature + guidance
- The one-liner: "Your optimization metric becomes your product's personality"

*Draft prose suggestion:*
> And something felt wrong. The charts were technically correct but lifeless. The scoring system rewarded consistency across parallel runs — if three isolated containers produced identical output, convergence was perfect. But insight annotations like "Renewables reached 75% of fossil fuel output by 2017" varied between runs. So the system learned to ban annotations entirely. I found the smoking gun in Pattern P2: a rule the automation had written saying "Do not add ax.annotate()." It had literally prohibited the thing that makes a chart say something.
>
> The fix was structural: I replaced rigid "Rules" with a small "Signature" (2–4 identity items) and flexible "Guidance." In its very next run, P2 spontaneously added an insight annotation. One prohibition removed, biggest visual improvement of the entire project.
>
> The lesson that stuck: your optimization metric becomes your product's personality. If you measure uniformity, you get uniform. If you measure quality and adaptiveness, you get charts that actually communicate.

**Image:** One before/after pair — the "optimized but says nothing" P2 chart next to the "fixed and alive" P2 chart. Use OPTION A from the existing Section 5 image options (taxi fares — same data, strongest contrast).

### Section 4: What I'd Tell You If You're Building a Skill (~250–300 words) — WRITE NEW

Keep the six takeaways from the original outline. These are the bookmarkable part.

1. **Start with taste.** Know what you want before you automate.
2. **Capture baselines.** You can't see improvement without a "before."
3. **Test in isolation.** If your skill only works with examples, it's a crutch.
4. **Measure what matters.** Your scoring metric becomes your skill's personality.
5. **Rules are expensive.** Each constraint removes a degree of freedom.
6. **Know when to stop.** 50 iterations was too many. Good enough at 20.

No closing paragraph. The last bullet is the ending.

**Image (optional):** One showcase chart at the end — or none. The Ghost says none.

---

## Word Budget

| Section | Visible words | Notes |
|---------|--------------|-------|
| 1. Hook | ~290 | Written |
| 2. Skill explanation | ~155 | Written |
| 3. Build + broke (merged) | ~400–500 | New prose + existing prompt in collapsed `<details>` |
| 4. Takeaways | ~250–300 | New prose |
| **Total** | **~1095–1245** | Plus ~250 in collapsed prompt = ~1345–1495 |

**The Ghost:**
> Look at that. Right in the 1200–1500 window. And notice what we cut: the standalone manual iteration section, the standalone clean room section, the standalone automation section, all the variation analysis imagery, the dataset expansion story. None of it was bad. It just wasn't necessary.

---

## Where the Panel Converges

1. **Four sections, not six.** Merge 3/4/5 into one section with three beats.
2. **The "went wrong" moment stays.** It's compressed but not cut — it's still the reason to share the article.
3. **Clean rooms get one clause, not one section.** The concept is powerful; the implementation details aren't needed.
4. **Four images max.** Hook lollipop, skill before/after, perverse incentive before/after. Maybe one showcase at the end.
5. **The collapsible prompt is free.** Don't count it against the word budget — it's opt-in reading.

## Where the Panel Diverges

- **David** wants the "something felt wrong" moment to breathe — a full paragraph of unease before the diagnosis. **The Ghost** says four sentences is enough; the before/after image does the emotional work.
- **Dr. Liu** wants a third image (the clean room trio showing three charts from isolation) to visually establish what "testing in isolation" means. **The Ghost** and **Elena** say the concept is clear from the text and adding the image slows the pace.
- **Aisha** thinks the Karpathy link alone is sufficient context. **David** thinks one sentence explaining *what* autoresearch is (for readers who don't know Karpathy) earns its space.
