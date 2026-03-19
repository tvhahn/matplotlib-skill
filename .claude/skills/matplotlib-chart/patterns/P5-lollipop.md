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

# Scale height to item count
n_items = len(df)
fig, ax = plt.subplots(figsize=(10, max(5, 1.5 + n_items * 0.8)), dpi=150)

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
    ax.text(x=df["avg"].iloc[i], y=i + 0.15, s=f'{df["avg"].iloc[i]:,.0f}',
            ha="center", va="bottom", size=10,
            color="dimgrey", weight="medium")

# min/max value annotations — REQUIRED (below each dot, smaller text)
for i in range(df.shape[0]):
    ax.text(x=df["min"].iloc[i], y=i - 0.15, s=f'{df["min"].iloc[i]:,.0f}',
            ha="center", va="top", size=8.5,
            color="dimgrey", weight="normal")
    ax.text(x=df["max"].iloc[i], y=i - 0.15, s=f'{df["max"].iloc[i]:,.0f}',
            ha="center", va="top", size=8.5,
            color="dimgrey", weight="normal")

# --- Insight annotation (highlight widest range or top performer) ---
df["range"] = df["max"] - df["min"]
top = df.loc[df["avg"].idxmax()]
ax.text(0.98, 0.02, f'{top["name"]} leads with avg {top["avg"]:,.0f}',
        transform=ax.transAxes, ha="right", va="bottom",
        fontsize=9, color="dimgrey", style="italic")

ax.grid(False)
sns.despine(left=True, bottom=True)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey")
ax.set_ylabel("")
ax.set_xlabel("X-Axis Label", fontsize=12, labelpad=8, color="dimgrey")
ax.set_title("Chart Title", fontsize=14, loc="left", pad=7)

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
- Default two-tone coloring (all min/max one color, all avg another). Use per-item colors when items have semantic meaning that warrants distinct colors (e.g., pass/fail categories).
- Annotate all three values per row by default: avg above, min/max below. All annotations `color="dimgrey"`.
- Default 2 legend items: "Average" and "Min/Max". Add more if the data has additional series that need identification.
- Set a descriptive x-axis label — do not leave it empty.
- Scale figsize height for item count: `max(5, 1.5 + n_items * 0.8)` — taller for more items.
- Scale `DOT_SIZE` with figure size or data density (100-200 range).
- Add unit prefixes (e.g., `$`) when values are currency or otherwise ambiguous without units.
- Adjust annotation `size` proportionally if figure is compact or labels overlap.
- Use `f'{value:.2f}'` for decimal data, `f'{value:,.0f}'` for large integers.
- Move legend to avoid occlusion if data extends into the lower-right corner.
- Omit min/max labels if the user says "clean" or "minimal".
- Always include an insight annotation (e.g., top performer, widest range, or notable gap). Position in an open corner using `transform=ax.transAxes`.

**Customize:** Add leading lines with `ax.plot([x_end + 0.02, x_label], [i, i], lw=1, color="grey", alpha=0.4, zorder=0)`. Add classifier name text at left margin.
