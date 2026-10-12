# Chart Review (independent critic)

The chart's author does not review their own PNG: a model that wrote the code sees
what it meant to draw, not what is there. Step 6 hands the PNG to a fresh reviewer
that has never seen the code.

## How to run it

Spawn one subagent with the Agent tool (general-purpose) and wait for its reply — do
not run it in the background. Fill in the brackets of the prompt below. Give it the
file paths only; never paste or attach the script. If the Agent tool is unavailable,
do the review yourself by following the same prompt, and describe the PNG *before*
you reread your code.

```text
You are reviewing a chart for a demanding data-visualisation editor. You have not
seen the code and must not look for it: judge only the image.

Request: [the user's request, verbatim]
Intended takeaway: [the one thing the reader should see, from step 1]
Chart: [absolute path(s) of the PNG(s) to review]
Reference: [absolute path(s) of the pattern's exemplar PNG(s)] — what stays fixed:
[the pattern's Signature bullets]. Everything else in the reference (data,
annotations, layout details) is one good answer, not a template to copy.

Read the chart PNG(s) and the reference PNG(s) with the Read tool. Then:

1. Describe the chart literally, before judging: title, subtitle, axis labels and
   ranges, every text item and where it sits, mark types, colours, legend entries.
2. Diff that description against the request and the intended takeaway. Is the
   takeaway visible within five seconds? Do the printed numbers agree with each
   other (subtitle vs labels)? Is anything the request asked for missing?
3. Check integrity: bars/areas start at zero; scales and units stated; nothing
   silently dropped; reference lines (baseline, diagonal, target) present.
4. Check legibility: overlaps, clipped or crowded text, labels sitting on data
   without a white halo, text too small or too faint, legend covering data.
5. Check encoding: series that differ by colour alone (no label, marker or line
   style); more than 3 annotations per panel; a legend that duplicates direct
   labels; decorative colour that encodes nothing.
6. Compare with the reference: is the pattern's Signature present? Do not ask for
   changes whose only purpose is to look more like the reference.

Reply with at most 6 issues, most important first, then a verdict:

ISSUE [BLOCKER|MAJOR|MINOR] <where in the chart> — <what is wrong> — <specific fix>
...
VERDICT: SHIP | FIX
```

## Acting on the review

- Fix every BLOCKER and MAJOR; fix a MINOR when the fix is one line.
- Re-run the script and `check_figure.py` after fixing, then Read the PNG yourself.
- At most two review rounds. If the second review still has a BLOCKER, report it to
  the user rather than looping.
- Disagree with the reviewer when the user's request or the data justifies the
  choice (e.g. the user asked for a legend); say so in the final report.
