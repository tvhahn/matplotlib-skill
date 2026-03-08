---
name: expert-panel
description: Assemble a panel of domain experts to analyze a topic from multiple perspectives. Use when you need structured multi-viewpoint analysis — sales strategy, engineering decisions, product direction, or any topic benefiting from diverse expertise.
argument-hint: "[topic or question to analyze]"
---

# Expert Panel Analysis

You are assembling a panel of 4-6 domain experts to analyze the following topic:

**$ARGUMENTS**

## Phase 1: Interview

Before generating the panel analysis, ask the user these questions (use the AskUserQuestion tool with all three questions in a single call):

1. **Expertise domains**: What expertise domains should the panel cover? For example: "enterprise sales, healthcare ops, engineering" — or "you pick based on the topic."
2. **Specific perspectives**: Any specific perspectives or roles you want represented? For example: "include a skeptic," "include someone from the buyer's side," or "no preference."
3. **Desired output**: What kind of output do you want: actionable recommendations, gap analysis, pros/cons debate, or open-ended discussion?

Wait for the user's answers before proceeding to Phase 2.

## Phase 2: Panel Generation

Once you have the user's preferences, generate the expert panel analysis following these guidelines:

### Panel composition
- Create 4-6 named experts with realistic titles, professional backgrounds, and a "primary lens" that defines how they see the world
- Each expert should feel like a real person with opinions and biases — not a generic "Expert in X"
- Avoid overlapping perspectives — each panelist should bring something the others can't

### Analysis style
- Each expert contributes from their unique vantage point
- Include direct quotes in each expert's voice using blockquote format (`>`)
- Surface disagreements naturally — don't force consensus where it doesn't exist
- Let the topic dictate the structure — don't impose rigid sections that don't fit

### Synthesis
- End with what the panel converges on and where they diverge
- If there are clear next steps or recommendations, surface them — but only if the topic warrants it

### What NOT to do
- Don't enforce mandatory sections like "Implementation Roadmap" or "Verification Plan"
- Don't make every expert agree — real panels have friction
- Don't use generic consultant-speak — each voice should be distinct
