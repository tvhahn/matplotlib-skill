# Vertical Bar Chart

**Use for:** one value per category with few, short category names, or categories with a natural order (years, sizes, ratings).
**Exemplars:** `exemplars/P2-a.png` (ordinal cylinders kept in natural order, one colour) and `exemplars/P2-b.png` (3 nominal islands sorted by value). Fixed: bar-end labels, no value axis. Varies: order (natural vs by value), palette size, subtitle wording.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: aggregate in pandas; natural order if one exists, else sort by value ---
df = raw.dropna(subset=["category", "value"]).groupby("category", as_index=False)["value"].mean()
natural_order = pd.api.types.is_numeric_dtype(df["category"])
df = df.sort_values("category" if natural_order else "value", ascending=natural_order)
order = df["category"].tolist()
n = len(df)

# --- Palette: ≤4 bars DIVERGING_COLORBLIND; ≥5 rocket with the near-white end trimmed ---
pal = ["#d73027", "#fc8d59", "#fee090", "#4575b4"][:n] if n <= 4 else sns.color_palette("rocket", n + 2)[:n]
if natural_order and n >= 5:
    pal = [sns.color_palette("rocket", 6)[2]] * n  # one colour: x position already encodes order

fmt = ".2f" if df["value"].max() < 10 else ".1f" if df["value"].max() < 100 else ",.0f"
fig, ax = plt.subplots(figsize=(max(6, 4 + n * 0.9), 6), dpi=150)
sns.barplot(data=df, x="category", y="value", hue="category", order=order,
            palette=pal, legend=False, ax=ax)
for container in ax.containers:
    ax.bar_label(container, fmt=f"{{:{fmt}}}", padding=3, weight="semibold",
                 size=12, color="dimgrey")

# --- Title + takeaway subtitle (computed from the data) ---
hi, lo = df.loc[df["value"].idxmax()], df.loc[df["value"].idxmin()]
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey",
             weight="semibold", pad=26)
label = lambda c: f"{c:g}" if pd.api.types.is_number(c) else str(c)  # 8.0 → "8"
ax.annotate(f'{label(hi["category"])} averages {hi["value"] / lo["value"]:.1f}x '
            f'{label(lo["category"])}',
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 8), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")

ax.set_xlabel("Category label", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("")
ax.set_yticks([])
ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey", labelsize=12)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Bar-end value labels with the value axis hidden: the labels carry the numbers.
- Palette family: `DIVERGING_COLORBLIND` for ≤ 4 bars, `rocket` for ≥ 5.

**Guidance:**
- Order: natural order for ordinal or numeric categories (shoe sizes, months, star ratings 1–5); descending by value for nominal ones. Always pass `order=` — seaborn otherwise sorts alphabetically.
- When x position already encodes order, a rocket gradient adds nothing: use a single rocket shade, and optionally a darker one for the bar the takeaway is about.
- Label the x-axis with what the categories are ("Star rating"); put units in the title or value labels, since the value axis is hidden.
- Give the categories their noun in the subtitle ("8-cylinder cars average 2.0x the 4-cylinder"), not bare codes.
- Show `n=` under tick labels (`f"{cat}\nn={count}"`) when some groups are tiny — readers should know a bar rests on 3 observations.
- Long or many labels (> 8 bars): rotate 30–45° with `ha="right"`, or switch to P1.
- Subtitle states a computed comparison (ratio, gap, trend across the order). Annotate a single bar with `ax.annotate` instead when the story is about one item.
