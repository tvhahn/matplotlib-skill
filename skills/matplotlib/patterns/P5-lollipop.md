# Lollipop / Dumbbell Chart

**Use for:** min/avg/max ranges per item — model scores across folds or tasks, price ranges by grade.
**Exemplars:** `exemplars/P5-a.png` (8 models) and `exemplars/P5-b.png` (6 countries, money). Fixed: dark min/max dots, light average dot, grey range bar, best on top. Varies: label density, number format, subtitle.

```python
sns.set_theme(font_scale=1.0, style="whitegrid", font="DejaVu Sans")

# --- Data: best average on top ---
df = pd.read_csv("data.csv").dropna(subset=["name", "min", "max", "avg"])
df = df.sort_values("avg", ascending=True).reset_index(drop=True)

pal = sns.cubehelix_palette(6, rot=-0.25, light=0.7)
dark, light = pal[5], pal[2]  # min/max dots, avg dots

n = len(df)
fmt = ".2f" if df["max"].max() < 10 else ".1f" if df["max"].max() < 100 else ",.0f"
fig, ax = plt.subplots(figsize=(10, 0.85 * n + 1.8), dpi=150)
DOT = 150

# Faint full-width guide per row, then the range line
ax.hlines(y=df.index, xmin=df["min"].min() * 0.98, xmax=df["max"].max() * 1.02,
          color="lightgrey", lw=1, zorder=0)
ax.hlines(y=df.index, xmin=df["min"], xmax=df["max"], color="grey", alpha=0.4, lw=4, zorder=1)
ax.scatter(df["min"], df.index, s=DOT, color=dark, edgecolors="white", zorder=3, label="Min/Max")
ax.scatter(df["max"], df.index, s=DOT, color=dark, edgecolors="white", zorder=3)
ax.scatter(df["avg"], df.index, s=DOT, color=light, edgecolors="white", zorder=4, label="Average")

for i, r in df.iterrows():
    ax.annotate(f'{r["avg"]:{fmt}}', xy=(r["avg"], i), xytext=(0, 9), textcoords="offset points",
                ha="center", va="bottom", fontsize=10, color="dimgrey", weight="medium")
    for x in (r["min"], r["max"]):
        ax.annotate(f"{x:{fmt}}", xy=(x, i), xytext=(0, -9), textcoords="offset points",
                    ha="center", va="top", fontsize=8.5, color="dimgrey")

ax.set_yticks(df.index, df["name"])
ax.set_xlabel("Score (units)", fontsize=12, labelpad=8, color="dimgrey")
ax.set_ylabel("")

# --- Title + takeaway subtitle; legend across the top ---
best, widest = df.iloc[-1], df.loc[(df["max"] - df["min"]).idxmax()]
ax.set_title("Chart Title", loc="left", fontsize=14, color="dimgrey",
             weight="semibold", pad=46)
ax.annotate(f'{best["name"]} has the highest average; {widest["name"]} varies most '
            f'({widest["max"] - widest["min"]:{fmt}} from min to max)',
            xy=(0, 1), xycoords="axes fraction", xytext=(0, 28), textcoords="offset points",
            ha="left", va="bottom", fontsize=10.5, color="dimgrey")
ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=True, facecolor="white",
          framealpha=0.8, edgecolor="lightgrey", labelcolor="dimgrey", fontsize=10)

ax.grid(False)
ax.tick_params(axis="both", which="both", length=0, labelcolor="dimgrey", labelsize=11)
sns.despine(left=True, bottom=True)
```

Apply style-reference invariants.

**Signature:**
- Two-tone cubehelix: `pal[5]` for all min/max dots, `pal[2]` for all average dots.
- Separate `ax.scatter()` layers for min, max, and average, joined by an `ax.hlines()` range line.

**Guidance:**
- Keep the two-tone scheme for every row; don't colour items individually.
- Sort by average, best on top (or by the user's key metric).
- Label averages by default. Min/max labels help with ≤ 8 rows; with more rows, or when the user wants it clean, drop them and keep the axis.
- Add a reference line where one exists (naive baseline, target, overall average) as a dashed `"#d73027"` `axvline` at `alpha=0.5`, labelled along the line.
- Subtitle states the comparison (best item, widest range, items overlapping the leader). Annotate an individual row with `ax.annotate` when the story is about one item.
- Height ≈ `0.85 × n + 1.8` in. `DOT` 100–200 depending on rows.
- Use units in the x label; `$`/`%` in value labels where they clarify.
