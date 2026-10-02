# Horizontal Bar Chart

**Use for:** one value per category, ranked — percentages, counts, scores; long category names.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: nominal categories sorted so the largest is on top ---
df = df.sort_values("value", ascending=False)
order = df["category"].tolist()

# --- Colour: one Blues_d shade; a darker shade marks the item(s) the takeaway is about ---
blues = sns.color_palette("Blues_d", 6)
highlight = {order[0]}
colors = {c: (blues[5] if c in highlight else blues[2]) for c in order}

n = len(df)
fig, ax = plt.subplots(figsize=(7, 0.55 * n + 1.6), dpi=150)
sns.barplot(data=df, x="value", y="category", hue="category", order=order,
            palette=colors, legend=False, ax=ax)

pad = df["value"].max() * 0.015
for p in ax.patches:
    ax.text(p.get_width() + pad, p.get_y() + p.get_height() / 2, f"{p.get_width():.1f}%",
            ha="left", va="center", weight="semibold", size=11, color="dimgrey")

# --- Title + takeaway subtitle (computed from the data) ---
top, last = df.iloc[0], df.iloc[-1]
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey",
             weight="semibold", pad=26)
ax.annotate(f'{top["category"]} is {top["value"] / last["value"]:.1f}x {last["category"]}',
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

ax.set_xlabel("")
ax.set_ylabel("")
ax.set_xticks([])
ax.axvline(x=0, color="lightgrey", linewidth=0.8, zorder=0)
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey", labelsize=11)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Bar-end value labels with the value axis hidden (`set_xticks([])`): the labels carry the numbers.
- Blues_d family: one shade for all bars, a darker shade only for highlighted bars.

**Guidance:**
- Sort nominal categories by value, largest on top. Keep natural order (age band, rating, education level) when the categories have one.
- Highlight what the takeaway is about (the leader, an outlier, the user's own item). Highlight nothing if there is no single story; for a strong standout, `"#bdbdbd"` grey + `ACCENT_RED` on that bar is the louder alternative.
- Write the subtitle from the data: a ratio, a gap, a share ("Basic plan: 24%, under half the Premium rate"). Drop it rather than restate a printed bar value.
- Height ≈ `0.55 × n + 1.6` in; width so the longest label and value label fit. Wrap long category names with `textwrap.fill(name, 20)`.
- Format labels for the data: `%` for rates, `$` and thousands separators for money, units where the title doesn't make them obvious. Add `n=` to labels when group sizes differ a lot.
- More than ~15 categories: show the top N and say so in the title ("Top 10 States").
