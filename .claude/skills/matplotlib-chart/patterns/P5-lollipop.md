# Lollipop / Dumbbell Chart

**When to use:** Showing min/max/avg ranges, model comparison across k-folds.
**Palette:** Cubehelix for dots, grey for connecting lines, dimgrey for text.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data ---
df = pd.read_csv("data.csv").dropna(subset=["name", "min", "max", "avg"])
df = df.sort_values("avg", ascending=True).reset_index(drop=True)

# --- Palette (default: two-tone cubehelix) ---
pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
darkblue = pal[5]   # min/max dots
lightblue = pal[2]  # avg dots

# --- Dynamic figsize and format ---
n_items = len(df)
max_val = df["max"].max()
# Detect annotation format from data magnitude
if max_val < 10:
    fmt = ".2f"      # small decimal values (e.g., carats, percentages)
elif max_val < 100:
    fmt = ".1f"      # medium values (e.g., mpg, scores)
else:
    fmt = ",.0f"     # large integers (e.g., dollars, population)
# Scale width for annotation text; scale height for item count
fig_w = max(8, 10 + max(0, len(f"{max_val:{fmt}}") - 4) * 0.5)
fig_h = max(3.5, 1.0 + n_items * 0.9)

fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=150)

DOT_SIZE = 150

# connecting lines (draw first, behind dots)
ax.hlines(y=df["name"], xmin=df["min"], xmax=df["max"],
          color="grey", alpha=0.4, lw=4, zorder=0)

# min/max dots
ax.scatter(x=df["min"], y=df["name"], s=DOT_SIZE,
           color=darkblue, edgecolors="white", label="Min/Max", zorder=3)
ax.scatter(x=df["max"], y=df["name"], s=DOT_SIZE,
           color=darkblue, edgecolors="white", zorder=3)

# avg dots (on top)
ax.scatter(x=df["avg"], y=df["name"], s=DOT_SIZE,
           color=lightblue, edgecolors="white", label="Average", zorder=4)

# avg value annotations — REQUIRED (centered above each avg dot)
for i in range(df.shape[0]):
    ax.text(x=df["avg"].iloc[i], y=i + 0.15, s=f'{df["avg"].iloc[i]:{fmt}}',
            ha="center", va="bottom", size=10,
            color="dimgrey", weight="medium")

# min/max value annotations — REQUIRED (below each dot, smaller text)
for i in range(df.shape[0]):
    ax.text(x=df["min"].iloc[i], y=i - 0.15, s=f'{df["min"].iloc[i]:{fmt}}',
            ha="center", va="top", size=8.5,
            color="dimgrey", weight="normal")
    ax.text(x=df["max"].iloc[i], y=i - 0.15, s=f'{df["max"].iloc[i]:{fmt}}',
            ha="center", va="top", size=8.5,
            color="dimgrey", weight="normal")

ax.grid(False)
sns.despine(left=True, bottom=True)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_ylabel("")
ax.set_xlabel("Descriptive X-Axis Label (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7, color="dimgrey")

# --- Insight annotation — positioned below axes, never inside the data area ---
df["range"] = df["max"] - df["min"]
top = df.loc[df["avg"].idxmax()]
widest = df.loc[df["range"].idxmax()]
fig.text(0.98, 0.01,
         f'{top["name"]} leads — widest spread in {widest["name"]} ({widest["range"]:{fmt}})',
         ha="right", va="bottom",
         fontsize=9, color="dimgrey", style="italic")

# Legend — REQUIRED (2 entries: "Min/Max" and "Average")
ax.legend(frameon=True, facecolor="white", framealpha=0.8, edgecolor="lightgrey",
         labelcolor="dimgrey", loc="lower right", fontsize=11)
```

Apply style-reference invariants.

**Signature:**
- Cubehelix palette: `pal[5]` (dark) for min/max dots, `pal[2]` (light) for avg dots.
- Three separate `ax.scatter()` calls: one for min dots, one for max dots, one for avg dots.
- Connecting lines: `ax.hlines()` from min to max.

**Guidance:**
- Always use two-tone coloring: all min/max dots `pal[5]`, all avg dots `pal[2]`. Do NOT assign per-item colors or substitute other colors (e.g., coral, orange) — the two-tone cubehelix look is the pattern's visual identity.
- Annotate all three values per row by default: avg above, min/max below. All annotations `color="dimgrey"`.
- Default 2 legend items: "Average" and "Min/Max". Add more if the data has additional series that need identification.
- Use classical titles that describe the metric (e.g., "Health Spending Range by Country"). Insight annotations carry findings, not the title.
- Set a descriptive x-axis label — do not leave it empty.
- Scale figsize height for item count: `max(3.5, 1.0 + n_items * 0.9)` — compact for 3–4 items, tall for 7+.
- Scale `DOT_SIZE` with figure size or data density (100-200 range).
- Add unit prefixes (e.g., `$`) when values are currency or otherwise ambiguous without units.
- Adjust annotation `size` proportionally if figure is compact or labels overlap.
- Adapt annotation format to the data domain: `$` prefix for currency, `%` suffix for rates, unit suffix (e.g., "mpg", "yr") when the axis label alone doesn't suffice. Use `f'{value:.2f}'` for decimal data, `f'{value:,.0f}'` for large integers.
- Move legend to avoid occlusion if data extends into the lower-right corner.
- Omit min/max labels if the user says "clean" or "minimal".
- Always include an insight annotation (e.g., top performer, widest range, or notable gap). Position BELOW the axes using `fig.text(0.98, 0.01, ..., ha="right", va="bottom")` — never inside the axes area where it can overlap data rows.

**Customize:** Add leading lines with `ax.plot([x_end + 0.02, x_label], [i, i], lw=1, color="grey", alpha=0.4, zorder=0)`. Add classifier name text at left margin.
